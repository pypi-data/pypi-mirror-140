"""Adaptively assign users to conditions.
"""
from __future__ import annotations

import random
import traceback
import warnings
from random import choices
from typing import Any, Callable, Mapping, Optional, Union

import numpy as np
import pandas as pd
from flask import current_app
from flask_login import current_user
from hemlock import User, create_app
from hemlock.utils.random import Assigner as AssignerBase, make_hash
from rq.job import Job

from .acquisition import functions as acquisition_functions, thompson
from .models import ModelReturnType, models
from .testing import MockJob

EARLY_WARNING_MESSAGE = (
    "\nThis warning is normal early in the study when there are not"
    " enough data to fit the model. If you continue to see this"
    " warning, there is likely a more serious error.\n"
)

ModelType = Union[str, Callable[..., ModelReturnType]]
AcquisitionType = Union[str, Callable[[np.ndarray], np.ndarray]]

assigners: list[Assigner] = []


def get_data(assigner: Assigner) -> pd.DataFrame:
    """Gets data for the model.

    This function drops users that haven't been assigned to a condition or don't have a
    target value.

    Args:
        assigner (Assigner): Assigner which is getting the data.

    Returns:
        pd.DataFrame: User data.
    """
    df = User.get_all_data()
    columns = assigner.factor_names + [assigner.model_kwargs.get("endog_name", "target")]
    if set(columns).issubset(df.columns):
        return df.dropna(subset=columns)
    return pd.DataFrame()


class Assigner(AssignerBase):
    """Adaptive assigner.

    Inherits from ``hemlock.utils.random.Assigner``.

    Args:
        conditions (Mapping): Mapping of factor names to possible assignment values.
        get_data (Callable[[Assigner], pd.DataFrame], optional): Function that gets data
            used to fit the model. Defaults to get_data.
        model (ModelType, optional): Estimates the value of each possible assignment.
            Defaults to "linear_regression".
        model_kwargs (Mapping, optional): Keyword arguments passed to ``model``.
            Defaults to None.
        acquisition (AcquisitionType, optional): Determines the weights to put on each
            possible assignment. Defaults to "exploration".
        min_users_per_condition (int, optional): Minimum number of users that need to be
            in each condition before adaptive assigner kicks in. Defaults to 0.
        allow_singular (bool, optional): Allows estimated effects to have a singular
            covariance matrix. Defaults to False.

    Attributes:
        get_data (Callable[[Assigner], pd.DataFrame]): Function that gets data used to
            fit the model.
        model (ModelType): Estimates the value of each possible assignment.
        model_kwargs (dict): Keyword arguments passed to ``model``.
        acquisition (AcquisitionType): Determines the weights to put on each possible
            assignment.
        min_users_per_condition (int): Minimum number of users that need to be in each
            condition before adaptive assigner kicks in.
        allow_singular (bool): Allows estimated effects to have a singular covariance
            matrix.
        weights (list[float]): Weights attached to each possible assignment.
        pr_best (list[float]): Probability that each possible assignment is best.

    Notes:

        The ``get_data``, ``model``, and ``acquisition`` functions should not be in
        main module, or you will get a serialization error.
    """

    _hash_length = 30
    enqueued_status = "enqueued"
    finished_status = "finished"

    def __init__(
        self,
        conditions: Mapping,
        get_data: Callable[[Assigner], pd.DataFrame] = get_data,
        model: ModelType = "linear_regression",
        model_kwargs: Mapping = None,
        acquisition: AcquisitionType = "exploration",
        min_users_per_condition: int = 0,
        allow_singular: bool = False,
    ):
        super().__init__(conditions)
        self.get_data = get_data
        self.model = model
        self.model_kwargs = dict(model_kwargs or {})
        if isinstance(model, str):
            self.model_kwargs["exog_names"] = self.factor_names
        self.acquisition = acquisition
        self.min_users_per_condition = min_users_per_condition
        self.allow_singular = allow_singular
        self.weights: list[float] = []
        self.pr_best: list[float] = []
        assigners.append(self)

    def _get_job_id_prefix(self) -> str:
        """Get the job ID prefix associated with this assigner.

        Will be of the form ``"ax-assigner-xxx"``.

        Returns:
            str: Prefix.
        """
        index = str(assigners.index(self)).zfill(len(assigners) % 10)
        return f"ax-assigner-{index}"

    def assign_user(self, user: User = None, df: pd.DataFrame = None) -> dict[Any, Any]:
        """Assign the user to a condition.

        Args:
            user (User, optional): User to assign. If None, this method assigns the
                current user. Defaults to None.
            df (pd.DataFrame, optional): Passed to :meth:`Assigner.get_cum_assigned`.

        Returns:
            dict[Any, Any]: Mapping of factor names to assignment values.
        """
        self.refresh(enqueue_new_job=True)
        if self.weights:
            if user is None:
                user = current_user
            values = choices(self.possible_assignments, self.weights, k=1)[0]
            assignment = {key: value for key, value in zip(self.factor_names, values)}
            user.meta_data.update(assignment)
            return assignment

        warnings.warn(
            "Assignment weights not yet set by the adaptive assigner."
            " Falling back on random assignment.",
            RuntimeWarning,
        )
        # randomly select a condition with the fewest users
        if not len(df := self.get_data(self)):
            df = pd.DataFrame([user.get_meta_data() for user in User.query.all()])
        return super().assign_user(user, df)

    def get_cum_assigned(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """Get the cumulative number of users assigned to each condition.

        Args:
            df (pd.DataFrame, optional): Dataframe used to count users. If None, uses
                the dataframe returned by ``self.get_data``. Defaults to None.

        Returns:
            pd.DataFrame: Count of users by condition.
        """
        return super().get_cum_assigned(self.get_data(self) if df is None else df)

    def get_jobs(self, status: str = "enqueued") -> list[Job]:
        """Get the assigner's background jobs.

        Args:
            status (str, optional): Get jobs with this status. Defaults to "enqueued".

        Returns:
            list[Job]: Jobs associated with this assigner.
        """
        assert status in (self.enqueued_status, self.finished_status)
        prefix = self._get_job_id_prefix()

        if status == self.enqueued_status:
            return [
                job for job in current_app.ax_queue.jobs if job.id.startswith(prefix)  # type: ignore
            ]

        jobs = []
        job_cls = MockJob if current_app.config["TESTING"] else Job
        for job_id in current_app.ax_queue.finished_job_registry.get_job_ids():  # type: ignore
            if job_id.startswith(prefix):
                jobs.append(
                    job_cls.fetch(job_id, connection=current_app.ax_queue.connection)  # type: ignore
                )
        return jobs

    def refresh(self, enqueue_new_job: bool = False) -> None:
        """Refresh the assigner's attributes.

        Gets the results of the latest finished job.

        Args:
            enqueue_new_job (bool, optional): Enqueue a new background job if the queue
                is empty. Defaults to False.
        """
        # get result from the most recently started finished job
        # and delete all finished jobs except the most recently started
        if finished_jobs := self.get_jobs(self.finished_status):
            finished_jobs.sort(key=lambda job: job.started_at)
            if (result := finished_jobs.pop().result) is not None:
                self.possible_assignments, self.weights, self.pr_best = result
            for job in finished_jobs:
                job.delete()

        # enqueue a new job if this assigner has no enqueued jobs
        if enqueue_new_job and len(self.get_jobs(self.enqueued_status)) == 0:
            current_app.ax_queue.enqueue(  # type: ignore
                self._update_assignment_weights,
                args=(current_app.config,),
                job_id=f"{self._get_job_id_prefix()}-{make_hash(self._hash_length)}",
                result_ttl=-1,
            )

        if (
            current_app.config["TESTING"]
            and current_app.ax_queue.jobs  # type: ignore
            and random.random() < current_app.config["PR_AX_JOB_RUN"]
        ):
            current_app.ax_queue.jobs[-1].perform()  # type: ignore

    def _update_assignment_weights(
        self, config: dict
    ) -> Optional[tuple[list[tuple], list[float], list[float]]]:
        """Update assignment weights.

        Args:
            config (dict): Application configuration.

        Returns:
            Optional[tuple[list[tuple], list[float], list[float]]]: Possible assignment
                values (conditions), assignment weights, probability that each condition
                is best.
        """

        def fit_model():
            if (self.get_cum_assigned()["count"] < self.min_users_per_condition).any():
                # there are not enough users in each condition
                return None
                
            try:
                return model(self.get_data(self), **self.model_kwargs)
            except Exception:
                traceback.print_exc()
                warnings.warn(
                    "MODEL FAILED TO FIT" + EARLY_WARNING_MESSAGE,
                    RuntimeWarning,
                )
                return None

        # get the model and acquisition function
        model = models[self.model] if isinstance(self.model, str) else self.model
        acquisition = (
            acquisition_functions[self.acquisition]
            if isinstance(self.acquisition, str)
            else self.acquisition
        )

        # fit the model and get the result
        if config["TESTING"]:
            result = fit_model()
        else:  # pragma: no cover
            with create_app(config).app_context():
                result = fit_model()
        if result is None:
            return None

        # get possible assignment values and sample distribution from results
        if isinstance(result, tuple):
            possible_assignments, distribution = result
            if hasattr(distribution, "rvs"):
                # distribution has rvs is a method that takes a size parameter and returns a np.ndarray
                distribution = distribution.rvs(size=1000)  # type: ignore
        else:
            # result is like a pandas dataframe
            possible_assignments = result.columns
            distribution = result.values
        possible_assignments = [
            (value if isinstance(value, tuple) else (value,))
            for value in possible_assignments
        ]
        distribution = np.atleast_2d(distribution)

        # check that the model has returned the correct set of possible assignments
        if extra_assignments := set(possible_assignments) - set(
            self.possible_assignments
        ):
            raise ValueError(
                f"The model returned invalid possible assignments \n{extra_assignments}"
            )
        if missing_assignments := set(self.possible_assignments) - set(
            possible_assignments
        ):
            warnings.warn(
                "The model did not return all expected assignment values."
                + EARLY_WARNING_MESSAGE
                + f"Missing values: {missing_assignments}",
                RuntimeWarning,
            )
            return None

        # if singular matrices are not allowed, assign participants only to conditions
        # with an estimated std of 0
        weights = (distribution.std(axis=0) == 0).astype(float)
        if not self.allow_singular and weights.any():
            warnings.warn(
                "The estimated covariance matrix is singular." + EARLY_WARNING_MESSAGE,
                RuntimeWarning,
            )
        else:
            # compute assignment weights
            weights = acquisition(distribution)  # type: ignore
        if (weights_sum := weights.sum()) == 0:
            weights = np.full(len(weights), 1 / len(weights))
        else:
            weights /= weights_sum

        return list(possible_assignments), list(weights), list(thompson(distribution))
