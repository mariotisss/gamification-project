from __future__ import annotations

from uuid import uuid4
from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.pkg.shared.domain.exceptions.entity_not_found import EntityNotFoundError
from core.pkg.user_system.domain.entities.user import User
from core.pkg.user_system.domain.ports.driving.user_use_cases import UserUseCases
from core.pkg.user_system.infrastructure.driving.api.get_user_controller import (
    GetUserController,
)


@pytest.fixture
def use_case() -> Mock:
    return Mock(spec=UserUseCases)


@pytest.fixture
def client(use_case: Mock) -> TestClient:
    app = FastAPI()
    GetUserController(app=app, use_case_factory=lambda: use_case, base_path="/api").register_routes()
    return TestClient(app=app)


def test_given_existing_user_when_get_user_then_returns_200_with_payload(
    client: TestClient,
    use_case: Mock,
) -> None:
    user = User(username="alice", email="a@example.com")
    use_case.get_user.return_value = user

    response = client.get(url=f"/api/users/{user.id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(user.id)


def test_given_missing_user_when_get_user_then_returns_404(
    client: TestClient,
    use_case: Mock,
) -> None:
    user_id = uuid4()
    use_case.get_user.side_effect = EntityNotFoundError(
        entity_type="User",
        entity_id=user_id,
    )

    response = client.get(url=f"/api/users/{user_id}")

    assert response.status_code == 404
