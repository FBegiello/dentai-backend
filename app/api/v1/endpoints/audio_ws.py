from fastapi import WebSocket
from fastapi import APIRouter

from agents.voice import (
    AudioInput,
    SingleAgentVoiceWorkflow,
    VoicePipeline,
)

from app.api.deps import DentalAgentManagerDep

router = APIRouter()


@router.websocket("/audio")
async def audio_websocket_endpoint(
    websocket: WebSocket,
    dental_agent: DentalAgentManagerDep,
):
    pipeline = VoicePipeline(workflow=SingleAgentVoiceWorkflow(dental_agent))
    await websocket.accept()
    try:
        while True:
            # Receive audio chunk
            data = await websocket.receive_bytes()
            # Log the size of the received chunk
            print(f"Received audio chunk of size: {len(data)} bytes")
            audio_input = AudioInput(buffer=data)
            result = await pipeline.run(audio_input)

            async for event in result.stream():
                if event.type == "voice_stream_event_audio":
                    websocket.send_bytes(event.data)
                else:
                    await websocket.send_text(f"Received chunk of {len(data)} bytes")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()
