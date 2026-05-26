from __future__ import annotations

from typing import Any, Dict, Tuple

from flask import jsonify, request
from marshmallow import Schema, ValidationError as MarshmallowValidationError

from app.core.errors import ValidationError


def ok(data: Any = None, meta: Dict[str, Any] | None = None, status: int = 200):
    payload = {"success": True, "data": data, "meta": meta or {}}
    return jsonify(payload), status


def fail(
    message: str,
    *,
    status: int = 400,
    code: str = "bad_request",
    details: Dict[str, Any] | None = None,
):
    payload = {
        "success": False,
        "error": {
            "message": message,
            "code": code,
            "details": details or {},
        },
    }
    return jsonify(payload), status


def validate_json(schema: Schema, payload: Dict[str, Any] | None) -> Dict[str, Any]:
    if payload is None:
        raise ValidationError("Request body must be JSON")
    try:
        return schema.load(payload)
    except MarshmallowValidationError as exc:
        raise ValidationError("Invalid request", details=exc.messages) from exc


def validate_query(schema: Schema) -> Dict[str, Any]:
    try:
        return schema.load(request.args)
    except MarshmallowValidationError as exc:
        raise ValidationError("Invalid query parameters", details=exc.messages) from exc


def pagination_params(default_limit: int = 50, max_limit: int = 500) -> Tuple[int, int]:
    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", default=default_limit, type=int)
    page = max(page, 1)
    limit = max(1, min(limit, max_limit))
    return page, limit


def pagination_meta(page: int, limit: int, total: int) -> Dict[str, Any]:
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "pages": (total + limit - 1) // limit if limit else 1,
    }
