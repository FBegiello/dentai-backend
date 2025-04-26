from pydantic import BaseModel

from app.schemas.response_schema import Tooth


class BaseAgentQueryRequest(BaseModel):
    message: str


class BaseAgentQueryResponse(BaseModel):
    response_text: str
    response_bytes: bytes
    action: list[Tooth] | None
