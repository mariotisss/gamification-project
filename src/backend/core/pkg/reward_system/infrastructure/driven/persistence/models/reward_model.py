from __future__ import annotations

from uuid import UUID

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from core.infrastructure.persistence.base import Base


class RewardModel(Base):
    __tablename__ = "rewards"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(length=255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    cost: Mapped[int] = mapped_column(nullable=False)
    reward_type: Mapped[str] = mapped_column(String(length=64), nullable=False)
