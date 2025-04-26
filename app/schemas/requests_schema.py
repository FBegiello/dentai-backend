from pydantic import BaseModel


class BaseAgentQueryRequest(BaseModel):
    message: str


class BaseAgentQueryResponse(BaseModel):
    response: str
