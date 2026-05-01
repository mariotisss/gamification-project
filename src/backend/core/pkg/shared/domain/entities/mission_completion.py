from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass
class MissionCompletion:
    user_id: UUID
    mission_id: UUID
    id: UUID = field(default_factory=uuid4)
    completed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
