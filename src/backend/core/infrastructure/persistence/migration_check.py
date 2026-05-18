from __future__ import annotations

from pathlib import Path

import structlog
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import Engine

_BACKEND_DIR = Path(__file__).resolve().parents[3]
_ALEMBIC_INI = _BACKEND_DIR / "alembic.ini"
_ALEMBIC_SCRIPT_LOCATION = _BACKEND_DIR / "alembic"

logger = structlog.get_logger(__name__)


class SchemaOutOfDateError(RuntimeError):
    def __init__(self, current: str, expected: str) -> None:
        self.current = current
        self.expected = expected
        super().__init__(
            f"Database schema is at revision '{current}', "
            f"but the code expects '{expected}'. "
            f"Run 'alembic upgrade head' from src/backend/ before starting the API."
        )


def assert_schema_up_to_date(engine: Engine) -> None:
    alembic_cfg = Config(file_=str(_ALEMBIC_INI))
    alembic_cfg.set_main_option(name="script_location", value=str(_ALEMBIC_SCRIPT_LOCATION))
    script = ScriptDirectory.from_config(config=alembic_cfg)
    expected = script.get_current_head() or ""

    with engine.connect() as connection:
        ctx = MigrationContext.configure(connection=connection)
        current = ctx.get_current_revision() or ""

    if current != expected:
        logger.error("schema_out_of_date", current=current, expected=expected)
        raise SchemaOutOfDateError(current=current, expected=expected)
    logger.info("schema_up_to_date", revision=current)
