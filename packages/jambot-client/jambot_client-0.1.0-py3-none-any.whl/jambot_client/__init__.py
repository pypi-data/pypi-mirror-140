from .clients import BridgeClient


class JambotClient:
    def __init__(self, bridge: BridgeClient):
        self._bridge = bridge

    @property
    def bridge(self) -> BridgeClient:
        return self._bridge


__all__ = ("JambotClient",)
