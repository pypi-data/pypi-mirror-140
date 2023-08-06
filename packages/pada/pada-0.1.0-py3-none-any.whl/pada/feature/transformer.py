# -*- coding: utf-8 -*-
from typing import (
    Callable, Collection, List, NamedTuple, Optional, Sequence, Tuple, Type,
    Union, cast,)
from collections import Counter
from copy import deepcopy
import traceback

import pandas as pd
import numpy as np
from funcy import identity, select_values
from sklearn.preprocessing import FunctionTransformer
from sklearn.base import BaseEstimator
from sklearn_pandas.pipeline import TransformerPipeline

from pada.libs import BaseTransformer, IdentityTransformer, SubsetTransformer
from pada.utils import DeepcopyMixin, asarray2d, quiet, indent
from pada.utils.state import OneOrMore, TransformerLike
from pada.check.checks import check_transformer
from pada.check.exception import UnsuccessfulInputConversionError
from pada.utils.log import logger, TRACE


RobustTransformer = Union[TransformerPipeline, 'DelegatingRobustTransformer']


def make_robust_transformer(
    transformer: OneOrMore[TransformerLike]
) -> RobustTransformer:
    """Convert to robust transformer or pipeline

    Convert to either a single DelegatingRobustTransformer or a
    TransformerPipeline where each transformer in the pipeline is a
    DelegatingRobustTransformer.
    """
    if isinstance(transformer, list):
        transformers = list(map(make_robust_transformer, transformer))
        return make_transformer_pipeline(transformers)
    else:
        transformer = desugar_transformer(transformer)
        check_transformer(transformer)
        return DelegatingRobustTransformer(transformer)


def make_transformer_pipeline(
    steps: Sequence[BaseTransformer],
) -> TransformerPipeline:
    """Construct a TransformerPipeline from the given estimators.

    Source: sklearn_pandas.cont_method
    """
    return TransformerPipeline(_name_estimators(steps))


def _name_estimators(
    estimators: Sequence[BaseEstimator]
) -> List[Tuple[str, BaseEstimator]]:
    """Generate names for estimators.

    Adapted from sklearn.pipeline._name_estimators to use the name of the
    underlying transformer within a DelegatingRobustTransformer.
    """

    def get_name(estimator):
        if isinstance(estimator, DelegatingRobustTransformer):
            return get_name(estimator._transformer)

        return type(estimator).__name__.lower()

    names = list(map(get_name, estimators))
    counter = dict(Counter(names))
    counter = select_values(lambda x: x > 1, counter)

    for i in reversed(range(len(estimators))):
        name = names[i]
        if name in counter:
            names[i] += "-%d" % counter[name]
            counter[name] -= 1

    return list(zip(names, estimators))


class ConversionApproach(NamedTuple):
    name: str
    convert: Callable
    caught: Collection[Type[Exception]]

    isokay: Optional[Callable[[Exception], bool]] = lambda exc: False
    """Opportunity to catch other exceptions that match a condition"""


def catch_bare_exception_sanitize_array(e):
    """See pandas-dev/pandas#35744"""
    return isinstance(e, Exception) and 'Data must be 1-dimensional' in str(e)


class DelegatingRobustTransformer(DeepcopyMixin, BaseTransformer):
    """Robust transformer that delegates to underlying transformer

    This transformer is robust against different typed and shaped input data.
    It tries a variety of input data conversion approaches and passes the
    result to the underlying transformer, using the first approach that works.

    Args:
        transformer: a transformer object with fit and transform methods

    Raises:
        UnsuccessfulInputConversionError: If none of the conversion approaches
            work.

    """

    DEFAULT_CAUGHT = (ValueError, TypeError)

    CONVERSION_APPROACHES = [
        ConversionApproach('identity', identity, DEFAULT_CAUGHT),
        ConversionApproach(
            'series', pd.Series, DEFAULT_CAUGHT,
            isokay=catch_bare_exception_sanitize_array),  # FIXME
        ConversionApproach('dataframe', pd.DataFrame, DEFAULT_CAUGHT),
        ConversionApproach('array', np.asarray, DEFAULT_CAUGHT),
        ConversionApproach('asarray2d', asarray2d, ()),
    ]

    def __init__(self, transformer: BaseTransformer):
        self._transformer = transformer
        self._stored_conversion_approach = None

    def get_params(self, deep=False):
        transformer = self.__getattribute__('_transformer')
        if deep:
            transformer = deepcopy(transformer)
        return {
            'transformer': transformer
        }

    def __getattr__(self, attr):
        if '_transformer' in self.__dict__:
            return getattr(self._transformer, attr)
        else:
            raise AttributeError

    def __getstate__(self):
        return self.__dict__.copy()

    def __setstate__(self, state):
        self.__dict__.update(state)

    def __repr__(self):
        name = type(self).__name__
        return f'{name}({self._transformer!r})'

    def __str__(self):
        return str(self._transformer)

    @property
    def _tname(self) -> str:
        return type(self._transformer).__name__

    def fit(self, X, y=None, **kwargs):
        # don't return the result of transformer.fit because it is the
        # underlying transformer, not this robust transformer
        self._call_robust(self._transformer.fit, X, y, kwargs)

        # instead, return this robust transformer
        return self

    def transform(self, X, y=None, **kwargs):
        return self._call_robust(self._transformer.transform, X, y, kwargs)

    @staticmethod
    def _call_with_convert(method, convert, X, y, kwargs):
        if y is not None:
            return method(convert(X), y=convert(y), **kwargs)
        else:
            return method(convert(X), **kwargs)

    @quiet
    def _call_robust(self, method, X, y, kwargs):
        if self._stored_conversion_approach is not None:
            approach = self._stored_conversion_approach
            self._log_attempt_using_stored_approach(approach)
            convert = approach.convert
            try:
                result = self._call_with_convert(method, convert, X, y, kwargs)
                self._log_success_using_stored_approach(approach)
                return result
            except Exception as e:
                self._log_failure_using_stored_approach(approach, e)
                raise
        else:
            for approach in DelegatingRobustTransformer.CONVERSION_APPROACHES:
                try:
                    self._log_attempt(approach)
                    result = self._call_with_convert(
                        method, approach.convert, X, y, kwargs)
                    self._log_success(approach)
                    self._stored_conversion_approach = approach
                    return result
                except approach.caught as e:
                    self._log_catch(approach, e)
                    continue
                except Exception as e:
                    if approach.isokay(e):
                        self._log_catch(approach, e)
                        continue
                    else:
                        self._log_error(approach, e)
                        raise

            self._log_failure_no_more_approaches()
            raise UnsuccessfulInputConversionError

    def _log_attempt_using_stored_approach(self, approach):
        logger.log(
            TRACE,
            f'{self._tname}: '
            f'Attempting to convert using stored, '
            f'previously-successful approach {approach.name!r}')

    def _log_failure_using_stored_approach(self, approach, e):
        pretty_tb = self._get_pretty_tb()
        exc_name = type(e).__name__
        logger.debug(
            f'{self._tname}: '
            f'Conversion unexpectedly failed using stored, '
            f'previously-successful approach {approach.name!r} '
            f'because of error {exc_name!r}\n\n{pretty_tb}')

    def _log_success_using_stored_approach(self, approach):
        logger.log(
            TRACE,
            f'{self._tname}: '
            f'Conversion with stored, previously-successful approach '
            f'{approach.name!r} succeeded!')

    def _log_attempt(self, approach):
        logger.log(
            TRACE,
            f'{self._tname}: '
            f'Attempting to convert using approach {approach.name!r}...')

    def _get_pretty_tb(self):
        tb = traceback.format_exc()
        pretty_tb = indent(tb, n=8)
        return pretty_tb

    def _log_catch(self, approach, e):
        pretty_tb = self._get_pretty_tb()
        exc_name = type(e).__name__
        logger.debug(
            f'{self._tname}: '
            f'Conversion approach {approach.name!r} didn\'t work so we\'ll '
            f'try another approach, '
            f'caught exception {exc_name!r}\n\n{pretty_tb}')

    def _log_error(self, approach, e):
        pretty_tb = self._get_pretty_tb()
        exc_name = type(e).__name__
        logger.debug(
            f'{self._tname}: '
            f'Conversion failed during {approach.name!r} because of '
            f'an unrecoverable error {exc_name!r}\n\n{pretty_tb}')

    def _log_success(self, approach):
        logger.log(
            TRACE,
            f'{self._tname}: '
            f'Conversion approach {approach.name!r} succeeded!')

    def _log_failure_no_more_approaches(self):
        logger.debug('Conversion failed, and we\'re not sure why...')


def desugar_transformer(
    transformer: TransformerLike,
) -> BaseTransformer:
    """Replace transformer syntactic sugar with actual transformer

    The following syntactic sugar is supported:
    - `None` is replaced with an IdentityTransformer
    - a callable (function or lambda) is replaced with a FunctionTransformer
        that wraps that callable
    - a tuple (input, transformer) is replaced with a SubsetTransformer
    """
    if transformer is None:
        return IdentityTransformer()
    elif callable(transformer) and not isinstance(transformer, type):
        return FunctionTransformer(transformer)
    elif isinstance(transformer, tuple):
        return SubsetTransformer(*transformer)
    else:
        transformer = cast(BaseTransformer, transformer)
        return transformer