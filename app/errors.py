from fastapi import HTTPException
from typing import Any, Dict

def validation_error(details: Dict[str, str], error: str = "Validation Failed") -> HTTPException:
    return HTTPException(status_code=422, detail={"error": error, "details": details})

def not_found_error(message: str = "Not Found") -> HTTPException:
    return HTTPException(status_code=404, detail={"error": "Not Found", "details": {"message": message}})

def to_error_payload(detail: Any):
    # Normalize HTTPException.detail into required shape when possible
    if isinstance(detail, dict) and "error" in detail and "details" in detail:
        return detail
    return {"error": "Error", "details": {"message": str(detail)}}
