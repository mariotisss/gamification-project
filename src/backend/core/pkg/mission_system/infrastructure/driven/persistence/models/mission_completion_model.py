from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from core.infrastructure.persistence.base import Base


class MissionCompletionModel(Base):
    __tablename__ = "mission_completions"
    __table_args__ = (
        UniqueConstraint("user_id", "mission_id", name="uq_mission_completion_user_mission"),
    )

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey(column="users.id", ondelete="CASCADE"),
        nullable=False,
    )
    mission_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey(column="missions.id", ondelete="CASCADE"),
        nullable=False,
    )
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
