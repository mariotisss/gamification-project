from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from core.infrastructure.persistence.base import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    username: Mapped[str] = mapped_column(String(length=64), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(length=255), unique=True, nullable=False)
    xp: Mapped[int] = mapped_column(nullable=False, default=0)
    level: Mapped[int] = mapped_column(nullable=False, default=1)
    dev_coins: Mapped[int] = mapped_column(nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version_id: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    __mapper_args__ = {"version_id_col": version_id}
