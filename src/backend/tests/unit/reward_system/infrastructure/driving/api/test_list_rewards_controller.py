from __future__ import annotations

from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.pkg.reward_system.domain.entities.reward import Reward
from core.pkg.reward_system.domain.ports.driving.reward_use_cases import RewardUseCases
from core.pkg.reward_system.infrastructure.driving.api.list_rewards_controller import (
    ListRewardsController,
)


@pytest.fixture
def use_case() -> Mock:
    return Mock(spec=RewardUseCases)


@pytest.fixture
def client(use_case: Mock) -> TestClient:
    app = FastAPI()
    ListRewardsController(app=app, use_case=use_case, base_path="/api").register_routes()
    return TestClient(app=app)


def test_given_no_rewards_when_list_rewards_then_returns_empty_list(
    client: TestClient,
    use_case: Mock,
) -> None:
    use_case.list_rewards.return_value = []

    response = client.get(url="/api/rewards")

    assert response.status_code == 200
    assert response.json() == []


def test_given_rewards_when_list_rewards_then_returns_serialized_list(
    client: TestClient,
    use_case: Mock,
) -> None:
    rewards = [
        Reward(name="A", description="a", cost=1, reward_type="cosmetic"),
        Reward(name="B", description="b", cost=2, reward_type="cosmetic"),
    ]
    use_case.list_rewards.return_value = rewards

    response = client.get(url="/api/rewards")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert {item["name"] for item in body} == {"A", "B"}
