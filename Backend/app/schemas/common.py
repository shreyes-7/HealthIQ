"""Shared response envelope.

Per PROJECT_CONTEXT.md Section 60/110: every successful response carries
status/message/data/timestamp/version, and error responses follow the
same structure. Routes (Milestone 5+) return these, never a bare
resource, so client-side handling stays uniform whether the request
succeeded or failed.
"""

from datetime import datetime, timezone
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SuccessResponse(BaseModel, Generic[DataT]):
    status: Literal["success"] = "success"
    message: str
    data: DataT
    timestamp: datetime = Field(default_factory=_utc_now)
    api_version: str = "v1"
    metadata: dict | None = None


class ErrorDetail(BaseModel):
    field: str | None = None
    message: str


class ErrorResponse(BaseModel):
    status: Literal["error"] = "error"
    message: str
    errors: list[ErrorDetail] = []
    timestamp: datetime = Field(default_factory=_utc_now)
    api_version: str = "v1"
