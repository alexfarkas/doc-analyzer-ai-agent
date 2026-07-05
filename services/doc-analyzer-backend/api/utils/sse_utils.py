import asyncio
import json
import logging
from typing import Callable, Awaitable, Any

logger = logging.getLogger(__name__)


async def stream_with_queue(
    task_runner: Callable[[], Awaitable[Any]],
    event_queue: asyncio.Queue,
):
    task = asyncio.create_task(task_runner())
    try:
        while True:
            event = await event_queue.get()
            yield sse_event(event['event'], event['data'])
            if event["event"] in ["complete", "error"]:
                break
    except Exception as e:
        logger.error(f"Documents analysis stream error: {e}", exc_info=True)
        yield sse_error(str(e))
    finally:
        await task


def sse_event(event_type: str, data: dict) -> str:
    return (
        f"event: {event_type}\n"
        f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
    )


def sse_error(message: str) -> str:
    return f"event: error\ndata: {json.dumps({'message': message}, ensure_ascii=False)}\n\n"


SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}