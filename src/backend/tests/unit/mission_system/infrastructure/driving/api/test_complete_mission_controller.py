from __future__ import annotations

from uuid import uuid4
from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.pkg.mission_system.domain.exceptions.mission_already_completed import (
    MissionAlreadyCompletedError,
)
from core.pkg.mission_system.domain.ports.driving.mission_use_cases import MissionUseCases
from core.pkg.mission_system.infrastructure.driving.api.complete_mission_controller import (
    CompleteMissionController,
)
from core.pkg.shared.domain.entities.mission_completion import MissionCompletion
from core.pkg.shared.domain.exceptions.entity_not_found import EntityNotFoundError


@pytest.fixture
def use_case() -> Mock:
    return Mock(spec=MissionUseCases)


@pytest.fixture
def client(use_case: Mock) -> TestClient:
    app = FastAPI()
    CompleteMissionController(
        app=app,
        use_case_factory=lambda: use_case,
        base_path="/api",
    ).register_routes()
    return TestClient(app=app)


def test_given_valid_request_when_complete_mission_then_returns_201_with_completion(
    client: TestClient,
    use_case: Mock,
) -> None:
    user_id = uuid4()
    mission_id = uuid4()
    completion = MissionCompletion(user_id=user_id, mission_id=mission_id)
    use_case.complete_mission.return_value = completion

    response = client.post(
        url=f"/api/missions/{mission_id}/complete",
        json={"user_id": str(user_id)},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["user_id"] == str(user_id)
    assert body["mission_id"] == str(mission_id)


def test_given_unknown_entity_when_complete_mission_then_returns_404(
    client: TestClient,
    use_case: Mock,
) -> None:
    mission_id = uuid4()
    use_case.complete_mission.side_effect = EntityNotFoundError(
        entity_type="Mission",
        entity_id=mission_id,
    )

    response = client.post(
        url=f"/api/missions/{mission_id}/complete",
        json={"user_id": str(uuid4())},
    )

    assert response.status_code == 404


def test_given_already_completed_when_complete_mission_then_returns_409(
    client: TestClient,
    use_case: Mock,
) -> None:
    user_id = uuid4()
    mission_id = uuid4()
    use_case.complete_mission.side_effect = MissionAlreadyCompletedError(
        user_id=user_id,
        mission_id=mission_id,
    )

    response = client.post(
        url=f"/api/missions/{mission_id}/complete",
        json={"user_id": str(user_id)},
    )

    assert response.status_code == 409


def test_given_unexpected_error_when_complete_mission_then_returns_500(
    client: TestClient,
    use_case: Mock,
) -> None:
    use_case.complete_mission.side_effect = RuntimeError("boom")

    response = client.post(
        url=f"/api/missions/{uuid4()}/complete",
        json={"user_id": str(uuid4())},
    )

    assert response.status_code == 500
