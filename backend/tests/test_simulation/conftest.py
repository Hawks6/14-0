"""
conftest.py for test_simulation package.

Simulation tests are pure Python unit tests with no database dependency.
This conftest overrides the session-level `setup_test_db` fixture so that
Alembic migration failures (e.g., DB not available, schema already exists)
do not block these tests from running.
"""

import pytest


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """
    Override root conftest's setup_test_db for simulation tests.
    Simulation tests are pure unit tests and require no database.
    """
    yield
