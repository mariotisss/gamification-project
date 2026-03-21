from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass
class User:
    username: str
    email: str
    id: UUID = field(default_factory=uuid4)
    xp: int = 0
    level: int = 1
    dev_coins: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # ── Business helpers ────────────────────────────────────────────

    def add_xp(self, amount: int) -> None:
        if amount < 0:
            raise ValueError("XP amount must be non-negative")
        self.xp += amount
        self.level = self._calculate_level()

    def add_dev_coins(self, amount: int) -> None:
        if amount < 0:
            raise ValueError("DevCoin amount must be non-negative")
        self.dev_coins += amount

    def deduct_dev_coins(self, amount: int) -> None:
        if amount < 0:
            raise ValueError("DevCoin amount must be non-negative")
        if amount > self.dev_coins:
            raise ValueError("Insufficient DevCoins")
        self.dev_coins -= amount

    def _calculate_level(self) -> int:
        return math.floor(self.xp / 100) + 1
