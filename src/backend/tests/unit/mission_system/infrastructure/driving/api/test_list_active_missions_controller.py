from __future__ import annotations

from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.pkg.mission_system.domain.entities.mission import Mission
from core.pkg.mission_system.domain.ports.driving.mission_use_cases import MissionUseCases
from core.pkg.mission_system.infrastructure.driving.api.list_active_missions_controller import (
    ListActiveMissionsController,
)


@pytest.fixture
def use_case() -> Mock:
    return Mock(spec=MissionUseCases)


@pytest.fixture
def client(use_case: Mock) -> TestClient:
    app = FastAPI()
    ListActiveMissionsController(
        app=app,
        use_case_factory=lambda: use_case,
        base_path="/api",
    ).register_routes()
    return TestClient(app=app)


def test_given_no_missions_when_list_active_missions_then_returns_empty_list(
    client: TestClient,
    use_case: Mock,
) -> None:
    use_case.list_active_missions.return_value = []

    response = client.get(url="/api/missions")

    assert response.status_code == 200
    assert response.json() == []


def test_given_active_missions_when_list_active_missions_then_returns_serialized_list(
    client: TestClient,
    use_case: Mock,
) -> None:
    missions = [
        Mission(title="A", description="a", xp_reward=1, coin_reward=1),
        Mission(title="B", description="b", xp_reward=2, coin_reward=2),
    ]
    use_case.list_active_missions.return_value = missions

    response = client.get(url="/api/missions")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert {item["title"] for item in body} == {"A", "B"}
