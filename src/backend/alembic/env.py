from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from core.infrastructure.persistence.base import Base
from core.infrastructure.persistence.settings import DatabaseSettings

import core.pkg.user_system.infrastructure.driven.persistence.models.user_model  # noqa: F401
import core.pkg.mission_system.infrastructure.driven.persistence.models.mission_model  # noqa: F401
import core.pkg.mission_system.infrastructure.driven.persistence.models.mission_completion_model  # noqa: F401
import core.pkg.reward_system.infrastructure.driven.persistence.models.reward_model  # noqa: F401


config = context.config

if config.config_file_name is not None:
    fileConfig(fname=config.config_file_name)

target_metadata = Base.metadata
config.set_main_option(name="sqlalchemy.url", value=DatabaseSettings().url)


def run_migrations_offline() -> None:
    url = config.get_main_option(name="sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        configuration=config.get_section(name=config.config_ini_section, default={}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
