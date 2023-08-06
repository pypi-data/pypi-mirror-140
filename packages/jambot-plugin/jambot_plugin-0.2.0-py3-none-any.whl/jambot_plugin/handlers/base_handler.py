from __future__ import annotations

from typing import Any, Generator, TypeVar

from jambot_client import JambotClient

from jambot_plugin.deps import inject


_THandlerImpl = TypeVar("_THandlerImpl")


class BaseHandler:
    def __await__(self: _THandlerImpl) -> Generator[None, Any, _THandlerImpl]:
        if hasattr(self.__class__, "__annotations__"):
            yield from inject(self, *self.__class__.__annotations__).__await__()
        return self


class ServiceHandler(BaseHandler):
    def __init__(self, jambot_client: JambotClient) -> None:
        self._jambot_client = jambot_client

    @property
    def jambot_client(self) -> JambotClient:
        return self._jambot_client
