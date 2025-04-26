from fastapi import APIRouter

from app.api.v1.endpoints import openai, audio_ws

api_router = APIRouter()

api_router.include_router(openai.router, prefix="/openai", tags=["openai"])
api_router.include_router(audio_ws.router, prefix="/ws", tags=["audio"])
