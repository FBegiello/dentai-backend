from fastapi import APIRouter, HTTPException
import httpx

from starlette.requests import Request
from app.api.deps import DentalAgentManagerDep

from app.schemas.requests_schema import BaseAgentQueryRequest, BaseAgentQueryResponse

from app.schemas.prompts import AGENT_PROMPT

from app.core.config import settings

router = APIRouter()


@router.post("/session")
async def create_openai_session():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/realtime/sessions",
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-4o-realtime-preview",
                    "modalities": ["audio", "text"],
                    "tools": [],
                    "instructions": AGENT_PROMPT,
                },
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"OpenAI API error: {response.text}",
                )

            return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"HTTP error occurred: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/text_query")
async def run_text_query(
    request: Request,
    agent_request: BaseAgentQueryRequest,
    dental_agent: DentalAgentManagerDep,
):
    try:
        response = await dental_agent.query_agent_text_mode(query=agent_request.message)
        bytes = dental_agent.generate_audio_response(message=response)

        return BaseAgentQueryResponse(
            response_text=response,
            response_bytes=bytes,
            action=dental_agent.flush_buffer(),
        )

    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"HTTP error occurred: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
