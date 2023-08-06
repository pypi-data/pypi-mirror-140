"""Application and worker initialization.
"""
from __future__ import annotations

import os

import redis  # type: ignore
from flask import Flask
from rq import Connection, Queue

if os.path.exists("/app/.heroku"):
    from rq.worker import HerokuWorker as Worker  # pragma: no cover
else:
    from rq.worker import Worker

AX_QUEUE_NAME = "ax"


def get_redis_url() -> str:
    """Get the Redis URL.

    Works with ``REDIS_URL`` and ``REDISTOGO_URL`` environment variables.

    Returns:
        str: Redis server URL.
    """
    return os.getenv("REDIS_URL", os.getenv("REDISTOGO_URL", "redis://"))


def init_app(app: Flask) -> None:
    """Initialize application with Ax configurations.

    This function updates the app configuration and adds an ``ax_queue`` attribute.

    Args:
        app (Flask): Application.

    Examples:

        .. doctest::

            >>> from hemlock import create_app
            >>> from hemlock_ax import init_app
            >>> app = create_app()
            >>> init_app(app)
            >>> app.ax_queue
            Queue('ax')
    """
    app.config.update(REDIS_URL=get_redis_url())
    app.ax_queue = Queue(AX_QUEUE_NAME, connection=redis.from_url(app.config["REDIS_URL"]))  # type: ignore


def run_worker():  # pragma: no cover
    """Start a worker listening on the hemlock-ax queue.

    Examples:

        .. code-block::

            >>> from hemlock_ax import run_worker
            >>> run_worker()
            INFO:rq.worker:Worker rq:worker:6e59173f13b34258818ffd29c021958c: started, version 1.9.0
            INFO:rq.worker:Subscribing to channel rq:pubsub:6e59173f13b34258818ffd29c021958c
            INFO:rq.worker:*** Listening on ax...
            INFO:rq.worker:Cleaning registries for queue: ax

    Notes:

        If your app is deployed on Heroku, this will automatically use
        ``rq.worker.HerokuWorker``.

        If you need to run an alternative worker process, have your worker listen on
        ``hemlock_ax.app.AX_QUEUE_NAME``.
    """
    with Connection(redis.from_url(get_redis_url())):
        Worker([AX_QUEUE_NAME]).work()
