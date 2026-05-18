from __future__ import annotations

from collections.abc import Iterator

import structlog
from sqlalchemy.orm import Session, sessionmaker

logger = structlog.get_logger(__name__)


class SessionProvider:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._factory = session_factory

    def get(self) -> Iterator[Session]:
        session = self._factory()
        try:
            yield session
            session.commit()
        except Exception as exc:
            logger.error(
                "session_rollback",
                exc_type=type(exc).__name__,
                message=str(exc),
            )
            session.rollback()
            raise
        finally:
            session.close()
