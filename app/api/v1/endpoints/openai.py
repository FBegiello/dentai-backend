from fastapi import APIRouter, HTTPException
import httpx

from starlette.requests import Request
from app.api.deps import DentalAgentManagerDep

from app.schemas.requests_schema import (
    BaseAgentQueryRequest,
    BaseAgentQueryResponse,
    BaseAgentTranscriptResponse,
)

router = APIRouter()


@router.post("/text_query")
async def run_text_query(
    request: Request,
    agent_request: BaseAgentQueryRequest,
    dental_agent: DentalAgentManagerDep,
):
    # try:
    dental_agent.add_to_transcript(message=agent_request.message, role="Dentist")
    response = await dental_agent.query_agent_text_mode(query=agent_request.message)
    dental_agent.add_to_transcript(message=response, role="Assistant")

    bytes = dental_agent.generate_audio_response(message=response)

    return BaseAgentQueryResponse(
        response_text=response,
        response_bytes=bytes,
        action=dental_agent.flush_buffer(),
    )


# except httpx.HTTPError as e:
#     raise HTTPException(status_code=500, detail=f"HTTP error occurred: {str(e)}")
# except Exception as e:
#     raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/generate_note")
async def generate_visit_note(
    request: Request,
    dental_agent: DentalAgentManagerDep,
):
    try:
        transcript = dental_agent.generate_transcript()
        return BaseAgentTranscriptResponse(transcript=transcript)

    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"HTTP error occurred: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
