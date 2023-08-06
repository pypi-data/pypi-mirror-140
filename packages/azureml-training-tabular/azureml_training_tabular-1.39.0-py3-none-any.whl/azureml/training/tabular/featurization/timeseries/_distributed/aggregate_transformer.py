# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict, List

import pandas as pd

from ...._diagnostics.azureml_error import AzureMLError
from ...._diagnostics.error_definitions import TimeseriesGrainAbsentNoDataContext
from ...._diagnostics.reference_codes import ReferenceCodes
from ..._azureml_transformer import AzureMLTransformer
from .._grain_based_stateful_transformer import _GrainBasedStatefulTransformer
from . import _distributed_timeseries_util


class PerGrainAggregateTransformer(AzureMLTransformer):
    """A transformer to map per grain transformers within a featurization pipeline."""

    def __init__(self, groupby_cols: List[str], mapping: Dict[str, _GrainBasedStatefulTransformer]):
        self._groupby_cols = groupby_cols
        self._mapping = mapping

    def fit(self, X, y=None):
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        dfs = []
        for group, X_group in X.groupby(self._groupby_cols):
            group_pairs = {}
            if not isinstance(group, tuple):
                group = [group]
            for k, v in zip(self._groupby_cols, group):
                group_pairs[k] = v
            desired_tr = _distributed_timeseries_util.convert_grain_dict_to_str(group_pairs)
            tr = self._mapping.get(desired_tr)
            if tr is None:
                raise AzureMLError.create(
                    TimeseriesGrainAbsentNoDataContext,
                    grain=group,
                    reference_code=ReferenceCodes._DIST_FORECASTING_MISSING_GRAIN,
                )
            dfs.append(tr.transform(X_group))
        return pd.concat(dfs)

    def get_params(self, deep=True):
        params = super().get_params(deep)
        params["groupby_cols"] = self._groupby_cols
        params["mapping"] = self._mapping
        return params


AutoMLAggregateTransformer = PerGrainAggregateTransformer
