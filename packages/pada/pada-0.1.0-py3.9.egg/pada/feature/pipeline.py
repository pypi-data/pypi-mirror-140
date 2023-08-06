# -*- coding: utf-8 -*-
from typing import Callable, List, NamedTuple, Tuple

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn_pandas import DataFrameMapper
from sklearn_pandas import __version__ as sklearn_pandas_version
from stacklog import stacklog

# n.b. cannot import Feature here bc of circular import
import pada.feature.features
import pada.feature.transformer
from pada.libs import BaseTransformer
from pada.libs.misc import NullTransformer
from pada.utils.log import logger
from pada.utils.state import OneOrMore


class FeatureEngineeringPipeline(DataFrameMapper):
    """Feature engineering pipeline

    Args:
        features: feature or list of features
    """

    def __init__(self, features: OneOrMore['pada.feature.feature.BaseFeature']):
        if not features:
            _features = [
                pada.feature.feature.BaseFeature(input=[],
                                       transformer=NullTransformer())
            ]
        elif not isinstance(features, list):
            _features = [features, ]
        else:
            _features = list(features)

        self._pada_features = _features

        super().__init__(
            [t.as_input_transformer_tuple() for t in _features],
            input_df=True,
        )

    @property
    def pada_features(self) -> List['pada.feature.features.BaseFeature']:
        return self._pada_features

    def get_names(self, columns, transformer, x, alias=None, prefix='',
                  suffix=''):
        """Return verbose names for the transformed columns.

        This extends the behavior of DataFrameMapper to allow ``alias`` to
        rename all of the output columns, rather than just providing a common
        base. It also allows ``columns`` to be a callable that supports
        selection by callable of the data frame.
        """
        num_cols = x.shape[1] if len(x.shape) > 1 else 1
        if isinstance(alias, list) and len(alias) == num_cols:
            return alias

        # set some default, but it would be better to store the column names
        # when we see them and then index out using the callable
        if callable(columns):
            columns = f'selected_input_{hash(columns)}'

        return super().get_names(columns, transformer, x, alias=alias)

    if sklearn_pandas_version.startswith('1'):
        def __setstate__(self, state):
            # FIXME see SubsetTransformer.__setstate__
            BaseEstimator.__setstate__(self, state)
            DataFrameMapper.__setstate__(self, state)


class EngineerFeaturesResult(NamedTuple):
    X_df: pd.DataFrame
    features: List['pada.feature.feature.BaseFeature']
    pipeline: FeatureEngineeringPipeline
    X: np.ndarray
    y_df: pd.DataFrame
    encoder: BaseTransformer
    y: np.ndarray


def make_engineer_features(
    pipeline: FeatureEngineeringPipeline,
    encoder: BaseTransformer,
    load_data: Callable[..., Tuple[pd.DataFrame, pd.DataFrame]],
) -> Callable[[pd.DataFrame, pd.DataFrame], EngineerFeaturesResult]:
    features = pipeline.pada_features

    @stacklog(logger.info, 'Building features and target')
    def engineer_features(
        X_df: pd.DataFrame = None, y_df: pd.DataFrame = None
    ) -> EngineerFeaturesResult:
        """Build features and target

        Args:
            X_df: raw variables
            y_df: raw target

        Returns:
            build result
        """
        if X_df is None or y_df is None:
            _X_df, _y_df = load_data()
        if X_df is None:
            X_df = _X_df
        if y_df is None:
            y_df = _y_df

        pipeline = FeatureEngineeringPipeline(features)
        X = pipeline.fit_transform(X_df, y=y_df)
        y = encoder.fit_transform(y_df)

        return EngineerFeaturesResult(
            X_df=X_df, features=features, pipeline=pipeline, X=X,
            y_df=y_df, encoder=encoder, y=y)

    return engineer_features
