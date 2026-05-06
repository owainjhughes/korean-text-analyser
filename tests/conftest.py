"""Shared pytest fixtures and markers.

DB-backed tests are gated behind the `requires_postgres` marker. They are
skipped unless `RUN_DB_TESTS=1` is set in the environment, which CI sets
after the postgres service is healthy.
"""
import asyncio
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "requires_postgres: marks tests that need a live Postgres "
        "(skipped unless RUN_DB_TESTS=1)",
    )


def pytest_collection_modifyitems(config, items):
    if os.environ.get("RUN_DB_TESTS") == "1":
        return
    skip_pg = pytest.mark.skip(reason="requires postgres; set RUN_DB_TESTS=1 to run")
    for item in items:
        if "requires_postgres" in item.keywords:
            item.add_marker(skip_pg)


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


@pytest.fixture
def clean_db():
    """Truncate users (and dependents via CASCADE) before each DB-backed test."""
    from app.db import AsyncSessionLocal

    async def _truncate():
        async with AsyncSessionLocal() as session:
            await session.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE"))
            await session.commit()

    asyncio.run(_truncate())
    yield
