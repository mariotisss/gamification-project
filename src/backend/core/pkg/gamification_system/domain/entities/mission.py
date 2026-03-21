from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Mission:
    title: str
    description: str
    xp_reward: int
    coin_reward: int
    id: UUID = field(default_factory=uuid4)
    is_active: bool = True
