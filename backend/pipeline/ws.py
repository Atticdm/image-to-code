from __future__ import annotations

import json
from typing import Any, Dict

from fastapi import WebSocket

from config import WS_MAX_PAYLOAD_BYTES
from pipeline.types import MessageType
from ws.constants import APP_ERROR_WEB_SOCKET_CODE  # type: ignore


class WebSocketCommunicator:
    """Handles WebSocket communication with consistent error handling."""

    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.is_closed = False

    async def accept(self) -> None:
        await self.websocket.accept()
        print("Incoming websocket connection...")

    async def send_message(
        self,
        type: MessageType,
        value: str,
        variantIndex: int,
    ) -> None:
        if type == "error":
            print(f"Error (variant {variantIndex + 1}): {value}")
        elif type == "status":
            print(f"Status (variant {variantIndex + 1}): {value}")
        elif type == "variantComplete":
            print(f"Variant {variantIndex + 1} complete")
        elif type == "variantError":
            print(f"Variant {variantIndex + 1} error: {value}")

        await self.websocket.send_json(
            {"type": type, "value": value, "variantIndex": variantIndex}
        )

    async def throw_error(self, message: str) -> None:
        print(message)
        if not self.is_closed:
            await self.websocket.send_json({"type": "error", "value": message})
            await self.websocket.close(APP_ERROR_WEB_SOCKET_CODE)
            self.is_closed = True

    async def receive_params(self) -> Dict[str, Any]:
        raw = await self.websocket.receive_text()
        if len(raw.encode("utf-8")) > WS_MAX_PAYLOAD_BYTES:
            await self.throw_error(
                f"Request payload too large (>{WS_MAX_PAYLOAD_BYTES} bytes). "
                "Try using a smaller image or fewer history items."
            )
            raise ValueError("WS payload too large")

        try:
            params = json.loads(raw)
        except Exception:
            await self.throw_error("Invalid JSON payload")
            raise

        if not isinstance(params, dict):
            await self.throw_error("Invalid request payload: expected an object")
            raise ValueError("WS payload must be an object")

        print("Received params")
        return params

    async def close(self) -> None:
        if not self.is_closed:
            await self.websocket.close()
            self.is_closed = True
