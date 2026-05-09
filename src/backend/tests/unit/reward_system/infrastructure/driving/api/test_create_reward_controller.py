from __future__ import annotations

from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.pkg.reward_system.domain.entities.reward import Reward
from core.pkg.reward_system.domain.ports.driving.reward_use_cases import RewardUseCases
from core.pkg.reward_system.infrastructure.driving.api.create_reward_controller import (
    CreateRewardController,
)


@pytest.fixture
def use_case() -> Mock:
    return Mock(spec=RewardUseCases)


@pytest.fixture
def client(use_case: Mock) -> TestClient:
    app = FastAPI()
    CreateRewardController(app=app, use_case=use_case, base_path="/api").register_routes()
    return TestClient(app=app)


def test_given_valid_payload_when_post_rewards_then_returns_201_with_response(
    client: TestClient,
    use_case: Mock,
) -> None:
    reward = Reward(name="N", description="D", cost=10, reward_type="cosmetic")
    use_case.create_reward.return_value = reward

    response = client.post(
        url="/api/rewards",
        json={"name": "N", "description": "D", "cost": 10, "reward_type": "cosmetic"},
    )

    assert response.status_code == 201
    assert response.json()["id"] == str(reward.id)


def test_given_invalid_payload_when_post_rewards_then_returns_422(client: TestClient) -> None:
    response = client.post(url="/api/rewards", json={"name": "only"})

    assert response.status_code == 422
