from __future__ import annotations

from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.pkg.user_system.domain.entities.user import User
from core.pkg.user_system.domain.ports.driving.user_use_cases import UserUseCases
from core.pkg.user_system.infrastructure.driving.api.create_user_controller import (
    CreateUserController,
)


@pytest.fixture
def use_case() -> Mock:
    return Mock(spec=UserUseCases)


@pytest.fixture
def client(use_case: Mock) -> TestClient:
    app = FastAPI()
    CreateUserController(app=app, use_case_factory=lambda: use_case, base_path="/api").register_routes()
    return TestClient(app=app)


def test_given_valid_payload_when_post_users_then_returns_201_with_response(
    client: TestClient,
    use_case: Mock,
) -> None:
    user = User(username="alice", email="a@example.com")
    use_case.create_user.return_value = user

    response = client.post(
        url="/api/users",
        json={"username": "alice", "email": "a@example.com"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == str(user.id)
    assert body["username"] == "alice"


def test_given_invalid_payload_when_post_users_then_returns_422(client: TestClient) -> None:
    response = client.post(url="/api/users", json={"username": "missing email"})

    assert response.status_code == 422
