from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy.orm import Session, sessionmaker


class SessionProvider:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._factory = session_factory

    def get(self) -> Iterator[Session]:
        session = self._factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
