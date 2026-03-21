from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Reward:
    name: str
    description: str
    cost: int
    reward_type: str
    id: UUID = field(default_factory=uuid4)
