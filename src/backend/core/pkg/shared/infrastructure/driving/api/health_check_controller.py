import structlog
from fastapi import FastAPI
from fastapi.responses import JSONResponse

logger = structlog.get_logger(__name__)


class HealthCheckController:

    def __init__(self, app: FastAPI, base_path: str) -> None:
        self.app = app
        self.base_path = base_path

    def register_routes(self) -> None:

        @self.app.get(path=f"{self.base_path}/health")
        def handle_health_check() -> JSONResponse:
            logger.info("incoming_health_check_request")
            response = JSONResponse(status_code=200, content={"status": "ok"})
            logger.info("outgoing_health_check_response", status_code=200)
            return response
