from __future__ import annotations

from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.pkg.mission_system.domain.entities.mission import Mission
from core.pkg.mission_system.domain.ports.driving.mission_use_cases import MissionUseCases
from core.pkg.mission_system.infrastructure.driving.api.create_mission_controller import (
    CreateMissionController,
)


@pytest.fixture
def use_case() -> Mock:
    return Mock(spec=MissionUseCases)


@pytest.fixture
def client(use_case: Mock) -> TestClient:
    app = FastAPI()
    CreateMissionController(app=app, use_case_factory=lambda: use_case, base_path="/api").register_routes()
    return TestClient(app=app)


def test_given_valid_payload_when_post_missions_then_returns_201_and_mission_response(
    client: TestClient,
    use_case: Mock,
) -> None:
    mission = Mission(title="T", description="D", xp_reward=10, coin_reward=5)
    use_case.create_mission.return_value = mission

    response = client.post(
        url="/api/missions",
        json={"title": "T", "description": "D", "xp_reward": 10, "coin_reward": 5},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == str(mission.id)
    assert body["title"] == "T"
    assert body["is_active"] is True


def test_given_invalid_payload_when_post_missions_then_returns_422(client: TestClient) -> None:
    response = client.post(url="/api/missions", json={"title": "missing fields"})

    assert response.status_code == 422


def test_given_use_case_raises_when_post_missions_then_returns_500(
    client: TestClient,
    use_case: Mock,
) -> None:
    use_case.create_mission.side_effect = RuntimeError("boom")

    response = client.post(
        url="/api/missions",
        json={"title": "T", "description": "D", "xp_reward": 10, "coin_reward": 5},
    )

    assert response.status_code == 500
