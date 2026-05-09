from __future__ import annotations

from uuid import uuid4
from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.pkg.reward_system.domain.entities.reward import Reward
from core.pkg.reward_system.domain.exceptions.insufficient_coins import InsufficientCoinsError
from core.pkg.reward_system.domain.ports.driving.reward_use_cases import RewardUseCases
from core.pkg.reward_system.infrastructure.driving.api.purchase_reward_controller import (
    PurchaseRewardController,
)
from core.pkg.shared.domain.exceptions.entity_not_found import EntityNotFoundError


@pytest.fixture
def use_case() -> Mock:
    return Mock(spec=RewardUseCases)


@pytest.fixture
def client(use_case: Mock) -> TestClient:
    app = FastAPI()
    PurchaseRewardController(
        app=app,
        use_case=use_case,
        base_path="/api",
    ).register_routes()
    return TestClient(app=app)


def test_given_valid_purchase_when_post_purchase_then_returns_200_with_reward(
    client: TestClient,
    use_case: Mock,
) -> None:
    reward = Reward(name="N", description="D", cost=10, reward_type="cosmetic")
    use_case.purchase_reward.return_value = reward

    response = client.post(
        url=f"/api/rewards/{reward.id}/purchase",
        json={"user_id": str(uuid4())},
    )

    assert response.status_code == 200
    assert response.json()["id"] == str(reward.id)


def test_given_unknown_entity_when_post_purchase_then_returns_404(
    client: TestClient,
    use_case: Mock,
) -> None:
    reward_id = uuid4()
    use_case.purchase_reward.side_effect = EntityNotFoundError(
        entity_type="Reward",
        entity_id=reward_id,
    )

    response = client.post(
        url=f"/api/rewards/{reward_id}/purchase",
        json={"user_id": str(uuid4())},
    )

    assert response.status_code == 404


def test_given_insufficient_coins_when_post_purchase_then_returns_402(
    client: TestClient,
    use_case: Mock,
) -> None:
    user_id = uuid4()
    reward_id = uuid4()
    use_case.purchase_reward.side_effect = InsufficientCoinsError(
        user_id=user_id,
        required=100,
        available=20,
    )

    response = client.post(
        url=f"/api/rewards/{reward_id}/purchase",
        json={"user_id": str(user_id)},
    )

    assert response.status_code == 402
