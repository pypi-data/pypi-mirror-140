from abc import ABC, abstractmethod
from typing import Mapping

from .base_handler import BaseHandler


class PingHandler(ABC, BaseHandler):
    @abstractmethod
    async def ping(self) -> Mapping[str, bool]:
        raise NotImplementedError
