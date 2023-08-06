"""Testing utilities.
"""
from __future__ import annotations

from datetime import datetime
from functools import partial
from typing import Any, Callable, Iterable, Mapping, Optional
from unittest.mock import MagicMock

import pandas as pd
from flask import Flask
from hemlock.user import List, SeedFunctionType, Type, User
from hemlock.utils.random import make_hash
from rq import Queue
from rq.job import Job
from rq.registry import FinishedJobRegistry


def init_test_app(app: Flask, pr_run: float = 1) -> None:
    """Initialize a test application with Ax configuration.

    This function updates the app configuration and adds a mock ``ax_queue`` attribute.

    Args:
        app (Flask): Application.
        pr_run (float, optional): Probability that an enqueued job is run when the
            :meth:`hemlock_ax.Assigner.refresh` method is called. Defaults to 1.

    Examples:

        .. code-block::

            >>> from hemlock import create_test_app
            >>> from hemlock_ax import init_test_app
            >>> app = create_test_app()
            >>> init_test_app(app)
            >>> app.ax_queue
            <MagicMock spec='MockQueue' id='139747642845024'>
    """
    from .app import AX_QUEUE_NAME, get_redis_url

    app.config.update(TESTING=True, PR_AX_JOB_RUN=pr_run, REDIS_URL=get_redis_url())
    app.ax_queue = make_mock(MockQueue, AX_QUEUE_NAME, connection=MockConnection())  # type: ignore


def run_test(
    n_users: int = 1,
    seed_func: SeedFunctionType = None,
    user_kwargs: Mapping[str, Any] = None,
    test_kwargs: Mapping[str, Any] = None,
) -> list[pd.DataFrame]:
    """Run a diagnostic test.

    Args:
        n_users (int, optional): Number of users to run. Defaults to 1.
        seed_func (SeedFunctionType, optional): Function that returns the user's first
            branch. Defaults to None.
        user_kwargs (Mapping[str, Any], optional): Passed to
            ``hemlock.User.make_test_user``. Defaults to None.
        test_kwargs (Mapping[str, Any], optional): Passed to ``hemlock.User.test``.
            Defaults to None.

    Returns:
        list[pd.DataFrame]: Dataframe of descriptive statistics for each adaptive
            assigner.

    Examples:

        .. code-block::

            >>> import random
            >>> from hemlock import Page, create_test_app
            >>> from hemlock_ax import Assigner, init_test_app, run_test
            >>> assigner = Assigner({"factor0": (0, 1, 2)})
            >>> def seed():
            >>>     assignment = assigner.assign_user()
            >>>     return Page(data=[("target", assignment["factor0"] + 1e-5 * random.random())])
            >>> app = create_test_app()
            >>> init_test_app(app)
            >>> result = run_test(9, seed)
            >>> result[0].tail(3)
               n_assigned_users  assignment  pr_best    weight  cum_assigned
            3                 9         0.0    0.001  0.002453             2
            4                 9         1.0    0.283  0.498242             3
            5                 9         2.0    0.716  0.499305             4
    """
    from .assign import assigners

    def capture_data(i, assigner):
        cum_assigned = assigner.get_cum_assigned()["count"]
        n_assigned_users = cum_assigned.sum()
        for assignment, pr_best, weight in zip(
            assigner.possible_assignments, assigner.pr_best, assigner.weights
        ):
            if len(assignment) == 1:
                assignment = assignment[0]
            assigner_records[i].append(
                {
                    "n_assigned_users": n_assigned_users,
                    "assignment": assignment,
                    "pr_best": pr_best,
                    "weight": weight,
                    "cum_assigned": cum_assigned[assignment],
                }
            )

    user_kwargs = dict(user_kwargs or {})
    user_kwargs["seed_func"] = seed_func
    test_kwargs = dict(test_kwargs or {})
    test_kwargs.setdefault("verbosity", 0)

    assigner_records: list[list[dict[str, Any]]] = [[] for _ in assigners]
    for _ in range(n_users):
        User.make_test_user(**user_kwargs).test(**test_kwargs)
        for i, assigner in enumerate(assigners):
            if assigner.weights:
                capture_data(i, assigner)

    return [pd.DataFrame(records) for records in assigner_records]


def make_mock(cls: Type, *args: Any, **kwargs: Any) -> MagicMock:
    """Create a ``MagicMock`` object.

    Args:
        cls (type): Class to mock.
        *args (Any): Passed to ``cls`` constructor.
        **kwargs (Any): Passed to ``cls`` constructor.

    Returns:
        MagicMock: Mock object.
    """
    mock = MagicMock(spec=cls)
    for attr_name in dir(cls):
        if not attr_name.startswith("__"):
            attr = getattr(cls, attr_name)
            if callable(attr):
                getattr(mock, attr_name).side_effect = partial(attr, mock)
            else:
                setattr(mock, attr_name, attr)

    cls.__init__(mock, *args, **kwargs)  # type: ignore
    return mock


class MockConnection:
    """Tracks mock queues and jobs.

    Attributes:
        queues (list[MockQueue]): Mock queues.
        jobs (list[MockJob]): Mock jobs.

    Notes:
        This connection tracks all jobs, both enqueued and finished.
    """

    def __init__(self):
        self.queues: list[MockQueue] = []
        self.jobs: list[MockJob] = []  # tracks all jobs associated with this connection


class MockQueue(Queue):
    """Mocks a ``rq.Queue`` object.

    Args:
        name (str): Queue name.
        connection (MockConnection): Mock connection.

    Attributes:
        name (str): Queue name.
        connection (MockConnection): Mock connection.
        jobs (list[MockJob]): Enqueued jobs.
        finished_job_registry (MockFinishedJobRegistry): Mock finished job registry.
    """

    def __init__(
        self, name: str, connection: MockConnection, *args: Any, **kwargs: Any
    ):
        self.name = name
        self.connection = connection
        connection.queues.append(self)
        self.jobs: list[MockJob] = []
        self.finished_job_registry = make_mock(MockFinishedJobRegistry)

    def enqueue(
        self,
        func: Callable,
        args: Iterable = None,
        kwargs: Mapping = None,
        **params: Any,
    ) -> MagicMock:
        """Enqueue a job.

        Args:
            func (Callable): Function.
            args (Iterable, optional): Passed to ``func``. Defaults to None.
            kwargs (Mapping, optional): Passed to ``func``. Defaults to None.

        Returns:
            MagicMock: Mock job.
        """
        job = make_mock(
            MockJob, func, self.connection, args=args, kwargs=kwargs, **params
        )
        self.jobs.append(job)
        return job


class MockJob(Job):
    """Mocks an ``rq.job.Job`` object.

    Args:
        func (Callable): Function
        connection (MockConnection): Mock connection.
        args (Iterable, optional): Passed to ``func``. Defaults to None.
        kwargs (Mapping, optional): Passed to ``func``. Defaults to None.
        job_id (str, optional): Job ID. Defaults to None.

    Attributes:
        func (Callable): Function
        connection (MockConnection): Mock connection.
        args (Iterable): Passed to ``func``.
        kwargs (Mapping): Passed to ``func``.
        id (str): Job ID.
        result (Any): Result of ``func(*args, **kwargs)``.
        started_at (datetime): Start time.
    """

    def __init__(
        self,
        func: Callable,
        connection: MockConnection,
        args: Iterable = None,
        kwargs: Mapping = None,
        job_id: str = None,
        **params: Any,
    ):
        self.func = func
        self.args = args or ()
        self.kwargs = kwargs or {}
        self.connection = connection
        connection.jobs.append(self)
        self.id = job_id or make_hash(30)
        self.result: Any = None
        self.started_at: Optional[datetime] = None

    @classmethod
    def fetch(
        cls, job_id: str, connection: MockConnection, *args: Any, **kwargs: Any
    ) -> MagicMock:
        """Fetch a job by ID.

        Args:
            job_id (str): Job ID.
            connection (MockConnection): Connection from which to fetch the job.

        Raises:
            ValueError: If ``job_id`` is not in the connection's jobs.

        Returns:
            MagicMock: Mock job.
        """
        for job in connection.jobs:
            if job.id == job_id:
                return job

        raise ValueError(f"Could not find job with id {job_id}")

    def delete(self) -> None:
        """Delete a job."""
        self.connection.jobs.remove(self)

        for queue in self.connection.queues:
            if self in queue.jobs:
                queue.jobs.remove(self)
                return

            if self.id in queue.finished_job_registry.get_job_ids():
                queue.finished_job_registry.remove(self)
                return

    def perform(self) -> None:
        """Perform the job (i.e., run ``func(*args, **kwargs)``)."""
        for queue in self.connection.queues:
            if self in queue.jobs:
                queue.jobs.remove(self)
                queue.finished_job_registry.add(self)
                break

        self.started_at = datetime.utcnow()
        self.result = self.func(*self.args, **self.kwargs)


class MockFinishedJobRegistry(FinishedJobRegistry):
    """Mocks a ``rq.registry.FinishedJobRegistry`` object."""

    def __init__(self, *args: Any, **kwargs: Any):
        self._job_ids: List[str] = []  # tracks finished job IDs for a specific queue

    def get_job_ids(self) -> List[str]:
        """Get finished job IDs.

        Returns:
            list[str]: Finished job IDs.
        """
        return self._job_ids

    def add(self, job: MagicMock) -> None:
        """Add a job.

        Args:
            job (MagicMock): Job to add.
        """
        self._job_ids.append(job.id)

    def remove(self, job: MagicMock) -> None:
        """Remove a job.

        Args:
            job (MagicMock): Job to remove.
        """
        self._job_ids.remove(job.id)
