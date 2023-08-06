from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import (
    Any, Callable, Generic, List, Optional, Set, Tuple, Type, TypeVar, Union,
    final, get_args, get_origin,
)

from jambot_plugin.bot_info import BotInfo
from jambot_plugin.types import (
    AnyAction, BaseEvent, Event, PlatformType, PluginConfig, ResponseEvent,
)
from jambot_plugin.user_info import UserInfo

from .base_handler import BaseHandler


_TRequestEvent = TypeVar("_TRequestEvent", bound=Event)
_TResponseEvent = TypeVar("_TResponseEvent", bound=Optional[ResponseEvent])


@final
class Request(Generic[_TRequestEvent]):
    __slots__ = ("_event", "_bot", "_user", "_event_ts")

    def __init__(
        self,
        event: _TRequestEvent,
        bot: BotInfo,
        user: UserInfo,
        event_ts: datetime,
        **kwargs: Any,
    ) -> None:
        self._event = event
        self._bot = bot
        self._user = user
        self._event_ts = event_ts

    @property
    def event(self) -> _TRequestEvent:
        return self._event

    @property
    def bot(self) -> BotInfo:
        return self._bot

    @property
    def user(self) -> UserInfo:
        return self._user

    @property
    def event_ts(self) -> datetime:
        return self._event_ts


@final
class Response(Generic[_TResponseEvent]):
    __slots__ = ("_response_event", "_system_events", "_inline", "_actions")

    def __init__(
        self,
        response_event: _TResponseEvent,
        system_events: Optional[List[BaseEvent]] = None,
        inline: bool = True,
        actions: Optional[List[Tuple[AnyAction, ...]]] = None,
    ):
        self._response_event = response_event
        self._system_events = system_events or []
        self._inline = inline
        self._actions = actions or []

    @property
    def response_event(self) -> _TResponseEvent:
        return self._response_event

    @property
    def system_events(self) -> List[BaseEvent]:
        return self._system_events

    @property
    def inline(self) -> bool:
        return self._inline

    @property
    def actions(self) -> List[Tuple[AnyAction, ...]]:
        return self._actions

    def add_row_actions(self, *actions: AnyAction) -> None:
        self._actions.append(actions)


_TPluginConfig = TypeVar("_TPluginConfig", bound=PluginConfig)


def _extract_response_event_types(
    type_: Any,
) -> Tuple[Type[ResponseEvent], ...]:
    if isinstance(type_, type):
        if issubclass(type_, ResponseEvent) and (type_ is not ResponseEvent):
            return (type_,)
        elif issubclass(type_, type(None)):
            return ()
    origin_type = get_origin(type_)
    if origin_type is Union:
        types: List[Type[ResponseEvent]] = []
        for t in get_args(type_):
            types.extend(_extract_response_event_types(t))
        return tuple(types)
    raise TypeError(
        f"Wrong type for user response event: {type_}. "
        f"Derivative types ResponseEvent or None were expected.",
    )


class EventHandler(
    ABC,
    BaseHandler,
    Generic[_TPluginConfig, _TRequestEvent, _TResponseEvent],
):
    __allowed_platforms__: Tuple[PlatformType, ...] = ()
    __disallowed_platforms__: Tuple[PlatformType, ...] = ()

    __request_event_type__: Type[_TRequestEvent]
    __response_event_types__: Tuple[Type[_TResponseEvent], ...]

    __used_request_event_types__: Set[Type[_TRequestEvent]] = set()

    def __init__(
        self,
        request: Request[_TRequestEvent],
        config: _TPluginConfig,
    ) -> None:
        self._request = request
        self._config = config

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        _, request_event_type, response_event_types = get_args(
            cls.__orig_bases__[0],  # type: ignore
        )
        if request_event_type in cls.__used_request_event_types__:
            raise TypeError(
                f"Duplicate event {request_event_type} in event handlers",
            )
        cls.__used_request_event_types__.add(request_event_type)
        cls.__request_event_type__ = request_event_type
        cls.__response_event_types__ = _extract_response_event_types(
            type_=response_event_types,
        )

    @property
    def request(self) -> Request[_TRequestEvent]:
        return self._request

    @property
    def config(self) -> _TPluginConfig:
        return self._config

    @classmethod
    def allowed_platforms(cls) -> Tuple[PlatformType, ...]:
        return cls.__allowed_platforms__

    @classmethod
    def disallowed_platforms(cls) -> Tuple[PlatformType, ...]:
        return cls.__disallowed_platforms__

    @classmethod
    def request_event_type(cls) -> Type[_TRequestEvent]:
        return cls.__request_event_type__

    @classmethod
    def response_event_types(cls) -> Tuple[Type[_TResponseEvent], ...]:
        return cls.__response_event_types__

    @abstractmethod
    async def handle(self) -> Response[_TResponseEvent]:
        raise NotImplementedError


def _inverse_platforms_list(
    platforms: Tuple[PlatformType, ...],
) -> Tuple[PlatformType, ...]:
    return tuple(
        platform for platform in list(PlatformType) if platform not in platforms
    )


_THandlerImpl = TypeVar("_THandlerImpl", bound=EventHandler[Any, Any, Any])


def allow_platforms(
    *platforms: PlatformType,
) -> Callable[[Type[_THandlerImpl]], Type[_THandlerImpl]]:
    def decorator(class_: Type[_THandlerImpl]) -> Type[_THandlerImpl]:
        if class_.__disallowed_platforms__:
            raise ValueError(
                "One of the allow_platforms or disallow_platforms "
                "properties must be empty",
            )
        if PlatformType.Unknown in platforms:
            return disallow_platforms(*_inverse_platforms_list(platforms))(
                class_,
            )
        class_.__allowed_platforms__ = platforms
        return class_

    return decorator


def disallow_platforms(
    *platforms: PlatformType,
) -> Callable[[Type[_THandlerImpl]], Type[_THandlerImpl]]:
    def decorator(class_: Type[_THandlerImpl]) -> Type[_THandlerImpl]:
        if class_.__allowed_platforms__:
            raise ValueError(
                "One of the allow_platforms or disallow_platforms "
                "properties must be empty",
            )
        if PlatformType.Unknown in platforms:
            return allow_platforms(*_inverse_platforms_list(platforms))(class_)
        class_.__disallowed_platforms__ = platforms
        return class_

    return decorator
