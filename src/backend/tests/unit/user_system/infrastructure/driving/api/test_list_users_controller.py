from __future__ import annotations

from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.pkg.user_system.domain.entities.user import User
from core.pkg.user_system.domain.ports.driving.user_use_cases import UserUseCases
from core.pkg.user_system.infrastructure.driving.api.list_users_controller import (
    ListUsersController,
)


@pytest.fixture
def use_case() -> Mock:
    return Mock(spec=UserUseCases)


@pytest.fixture
def client(use_case: Mock) -> TestClient:
    app = FastAPI()
    ListUsersController(app=app, use_case=use_case, base_path="/api").register_routes()
    return TestClient(app=app)


def test_given_no_users_when_list_users_then_returns_empty_list(
    client: TestClient,
    use_case: Mock,
) -> None:
    use_case.list_users.return_value = []

    response = client.get(url="/api/users")

    assert response.status_code == 200
    assert response.json() == []


def test_given_users_when_list_users_then_returns_serialized_list(
    client: TestClient,
    use_case: Mock,
) -> None:
    users = [
        User(username="a", email="a@example.com"),
        User(username="b", email="b@example.com"),
    ]
    use_case.list_users.return_value = users

    response = client.get(url="/api/users")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert {item["username"] for item in body} == {"a", "b"}
