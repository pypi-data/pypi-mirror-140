from datetime import datetime
from typing import Any, Mapping
from uuid import UUID

from jambot_client.clients.base_client import BaseClient


class BridgeClient(BaseClient):
    async def send_event(
        self,
        event_type: str,
        payload: Mapping[str, Any],
        bot_id: UUID,
        user_id: UUID,
        platform: str,
    ) -> None:
        await self._post(
            path="api/v1/events",
            json={
                "event": {
                    "event_type": event_type,
                    "payload": payload,
                    "event_ts": int(datetime.utcnow().timestamp()),
                },
                "bot": {
                    "bot_id": bot_id,
                },
                "user": {
                    "user_id": user_id,
                    "platform": platform,
                },
            },
        )
