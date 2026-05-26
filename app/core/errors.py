from dataclasses import dataclass
from http import HTTPStatus
from typing import Any, Dict, Tuple

from flask import Flask, jsonify


@dataclass
class AppError(Exception):
    message: str
    status_code: int = HTTPStatus.BAD_REQUEST
    details: Dict[str, Any] | None = None


class ValidationError(AppError):
    status_code = HTTPStatus.BAD_REQUEST


class ModelNotReadyError(AppError):
    status_code = HTTPStatus.SERVICE_UNAVAILABLE


class ExternalServiceError(AppError):
    status_code = HTTPStatus.BAD_GATEWAY


class AlertDispatchError(AppError):
    status_code = HTTPStatus.BAD_GATEWAY


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(AppError)
    def handle_app_error(error: AppError) -> Tuple[Any, int]:
        payload = {
            "success": False,
            "error": {
                "message": error.message,
                "code": "app_error",
                "details": error.details or {},
            },
        }
        return jsonify(payload), error.status_code

    @app.errorhandler(404)
    def handle_not_found(_: Exception) -> Tuple[Any, int]:
        return (
            jsonify(
                {
                    "success": False,
                    "error": {"message": "Not found", "code": "not_found", "details": {}},
                }
            ),
            HTTPStatus.NOT_FOUND,
        )

    @app.errorhandler(500)
    def handle_server_error(_: Exception) -> Tuple[Any, int]:
        return (
            jsonify(
                {
                    "success": False,
                    "error": {
                        "message": "Internal server error",
                        "code": "server_error",
                        "details": {},
                    },
                }
            ),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
