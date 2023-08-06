from abc import ABC, abstractmethod
from typing import Any

from croniter import croniter

from .base_handler import ServiceHandler


class CronHandler(ABC, ServiceHandler):
    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        cron_spec = cls.cron_spec()
        if not croniter.is_valid(cron_spec):
            raise ValueError(f"Cron spec {cron_spec} is invalid")

    @classmethod
    @abstractmethod
    def cron_spec(cls) -> str:
        raise NotImplementedError

    @abstractmethod
    async def handle(self) -> None:
        raise NotImplementedError
