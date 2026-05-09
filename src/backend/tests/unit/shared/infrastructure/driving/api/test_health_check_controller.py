from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.pkg.shared.infrastructure.driving.api.health_check_controller import (
    HealthCheckController,
)


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    HealthCheckController(app=app, base_path="/api").register_routes()
    return TestClient(app=app)


def test_given_app_when_get_health_then_returns_200(client: TestClient) -> None:
    response = client.get(url="/api/health")

    assert response.status_code == 200


def test_given_app_when_get_health_then_returns_expected_payload(client: TestClient) -> None:
    response = client.get(url="/api/health")

    assert response.json() == {"status": "ok"}
