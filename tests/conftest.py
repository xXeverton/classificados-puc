"""Shared fixtures for database-backed tests."""

from collections.abc import Iterator

import pytest
from sqlalchemy.engine import Engine

from server.infra.db.database import (
    create_database_engine,
    initialize_database,
)


@pytest.fixture
def database_engine() -> Iterator[Engine]:
    engine = create_database_engine("sqlite:///:memory:")
    initialize_database(engine)
    yield engine
    engine.dispose()
