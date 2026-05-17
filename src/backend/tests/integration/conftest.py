from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
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


_BACKEND_DIR = Path(__file__).resolve().parents[2]
_ALEMBIC_INI = _BACKEND_DIR / "alembic.ini"
_ALEMBIC_SCRIPT_LOCATION = _BACKEND_DIR / "alembic"


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

    alembic_cfg = Config(file_=str(_ALEMBIC_INI))
    alembic_cfg.set_main_option(name="script_location", value=str(_ALEMBIC_SCRIPT_LOCATION))
    alembic_cfg.set_main_option(name="sqlalchemy.url", value=settings.url)
    command.upgrade(config=alembic_cfg, revision="head")

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
