from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio
import json
from ..services.fan_control import FanControlService

router = APIRouter()


async def event_generator(fan_control: FanControlService):
    """Generador de eventos Server-Sent Events"""
    while True:
        try:
            # Obtener datos actuales
            last_record = fan_control.history.get_last_record()
            if last_record:
                yield f"data: {json.dumps(last_record)}\n\n"

            # Esperar 1 segundo
            await asyncio.sleep(1)
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"SSE Error: {e}")
            await asyncio.sleep(5)


@router.get("/stream")
async def stream_data(fan_control: FanControlService = Depends()):
    """Endpoint para streaming Server-Sent Events"""
    return StreamingResponse(
        event_generator(fan_control),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )