from __future__ import annotations

from uuid import UUID, uuid4

import pytest


@pytest.fixture
def random_uuid() -> UUID:
    return uuid4()
