from typing import Any
from uuid import UUID

from .types import Platform


class UserInfo:
    __slots__ = ("_user_id", "_platform")

    def __init__(
        self,
        user_id: UUID,
        platform: Platform,
        **kwargs: Any,
    ) -> None:
        self._user_id = user_id
        self._platform = platform

    @property
    def user_id(self) -> UUID:
        return self._user_id

    @property
    def platform(self) -> Platform:
        return self._platform
