from __future__ import annotations

from uuid import uuid4
from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.pkg.mission_system.domain.entities.mission import Mission
from core.pkg.mission_system.domain.ports.driving.mission_use_cases import MissionUseCases
from core.pkg.mission_system.infrastructure.driving.api.get_mission_controller import (
    GetMissionController,
)
from core.pkg.shared.domain.exceptions.entity_not_found import EntityNotFoundError


@pytest.fixture
def use_case() -> Mock:
    return Mock(spec=MissionUseCases)


@pytest.fixture
def client(use_case: Mock) -> TestClient:
    app = FastAPI()
    GetMissionController(app=app, use_case_factory=lambda: use_case, base_path="/api").register_routes()
    return TestClient(app=app)


def test_given_existing_mission_when_get_mission_then_returns_200_with_payload(
    client: TestClient,
    use_case: Mock,
) -> None:
    mission = Mission(title="T", description="D", xp_reward=10, coin_reward=5)
    use_case.get_mission.return_value = mission

    response = client.get(url=f"/api/missions/{mission.id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(mission.id)


def test_given_missing_mission_when_get_mission_then_returns_404(
    client: TestClient,
    use_case: Mock,
) -> None:
    mission_id = uuid4()
    use_case.get_mission.side_effect = EntityNotFoundError(
        entity_type="Mission",
        entity_id=mission_id,
    )

    response = client.get(url=f"/api/missions/{mission_id}")

    assert response.status_code == 404


def test_given_invalid_uuid_when_get_mission_then_returns_422(client: TestClient) -> None:
    response = client.get(url="/api/missions/not-a-uuid")

    assert response.status_code == 422
