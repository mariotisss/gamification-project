from __future__ import annotations

from collections.abc import Iterator

import pytest
from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker
from testcontainers.postgres import PostgresContainer

from core.infrastructure.persistence.base import Base
from core.infrastructure.persistence.database import build_engine, build_session_factory
from core.infrastructure.persistence.settings import DatabaseSettings

import core.pkg.user_system.infrastructure.driven.persistence.models.user_model  # noqa: F401
import core.pkg.mission_system.infrastructure.driven.persistence.models.mission_model  # noqa: F401
import core.pkg.mission_system.infrastructure.driven.persistence.models.mission_completion_model  # noqa: F401
import core.pkg.reward_system.infrastructure.driven.persistence.models.reward_model  # noqa: F401


@pytest.fixture(scope="session")
def postgres_container() -> Iterator[PostgresContainer]:
    with PostgresContainer(image="postgres:16") as container:
        yield container


@pytest.fixture(scope="session")
def engine(postgres_container: PostgresContainer) -> Iterator[Engine]:
    settings = DatabaseSettings(
        host=postgres_container.get_container_host_ip(),
        port=int(postgres_container.get_exposed_port(port=5432)),
        user=postgres_container.username,
        password=postgres_container.password,
        name=postgres_container.dbname,
    )
    engine = build_engine(settings=settings)
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture
def session(engine: Engine) -> Iterator[Session]:
    factory: sessionmaker[Session] = build_session_factory(engine=engine)
    session = factory()
    try:
        yield session
    finally:
        session.rollback()
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(statement=table.delete())
        session.commit()
        session.close()
