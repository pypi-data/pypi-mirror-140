"""Models.
"""
from __future__ import annotations

from typing import Any, Callable, List, Protocol, Tuple, Union

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import multivariate_normal


class DataFrame(Protocol):
    columns: list[Any]
    values: np.ndarray


class Distribution(Protocol):
    def rvs(self, size: int, *args: Any, **kwargs: Any) -> np.ndarray:
        ...  # pragma: no cover


ModelReturnType = Union[DataFrame, Tuple[List[Tuple], Union[np.ndarray, Distribution]]]


def linear_regression(
    df: pd.DataFrame, exog_names: list[str], endog_name: str = "target"
) -> ModelReturnType:
    """Estimate the distribution using linear regression.

    Args:
        df (pd.DataFrame): Data used to fit the model.
        exog_names (list[str]): Names of exogenous (assignment) variables.
        endog_name (str, optional): Name of the endogenous variable. Defaults to
            "target".

    Returns:
        ModelReturnType: list of possible assignments, distribution of effects.
    """
    df = df.dropna(subset=exog_names + [endog_name])
    assignments = df[exog_names].apply(lambda row: tuple(row), axis=1)
    model = sm.OLS(df[endog_name], pd.get_dummies(assignments))
    results = model.fit().get_robustcov_results("cluster", groups=df.id)
    return model.exog_names, multivariate_normal(
        results.params, results.cov_params(), allow_singular=True
    )


models: dict[
    str,
    Callable[..., ModelReturnType],
] = {"linear_regression": linear_regression}
