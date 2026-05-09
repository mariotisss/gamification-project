from __future__ import annotations

from uuid import uuid4
from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.pkg.reward_system.domain.entities.reward import Reward
from core.pkg.reward_system.domain.ports.driving.reward_use_cases import RewardUseCases
from core.pkg.reward_system.infrastructure.driving.api.get_reward_controller import (
    GetRewardController,
)
from core.pkg.shared.domain.exceptions.entity_not_found import EntityNotFoundError


@pytest.fixture
def use_case() -> Mock:
    return Mock(spec=RewardUseCases)


@pytest.fixture
def client(use_case: Mock) -> TestClient:
    app = FastAPI()
    GetRewardController(app=app, use_case=use_case, base_path="/api").register_routes()
    return TestClient(app=app)


def test_given_existing_reward_when_get_reward_then_returns_200_with_payload(
    client: TestClient,
    use_case: Mock,
) -> None:
    reward = Reward(name="N", description="D", cost=10, reward_type="cosmetic")
    use_case.get_reward.return_value = reward

    response = client.get(url=f"/api/rewards/{reward.id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(reward.id)


def test_given_missing_reward_when_get_reward_then_returns_404(
    client: TestClient,
    use_case: Mock,
) -> None:
    reward_id = uuid4()
    use_case.get_reward.side_effect = EntityNotFoundError(
        entity_type="Reward",
        entity_id=reward_id,
    )

    response = client.get(url=f"/api/rewards/{reward_id}")

    assert response.status_code == 404
