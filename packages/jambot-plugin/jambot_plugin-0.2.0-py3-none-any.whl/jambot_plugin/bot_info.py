from typing import Any
from uuid import UUID

from .types import BotConfig


class BotInfo:
    __slots__ = ("_bot_id", "_config")

    def __init__(self, bot_id: UUID, config: BotConfig, **kwargs: Any) -> None:
        self._bot_id = bot_id
        self._config = config

    @property
    def bot_id(self) -> UUID:
        return self._bot_id

    @property
    def config(self) -> BotConfig:
        return self._config
