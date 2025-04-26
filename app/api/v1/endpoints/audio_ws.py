from fastapi import WebSocket
from fastapi import APIRouter

router = APIRouter()


@router.websocket("/ws/audio")
async def audio_websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Receive audio chunk
            data = await websocket.receive_bytes()
            # Log the size of the received chunk
            print(f"Received audio chunk of size: {len(data)} bytes")

            # Send acknowledgment back to client
            await websocket.send_text(f"Received chunk of {len(data)} bytes")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()
