from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, unique
from typing import Any, Dict, Literal, Mapping, Optional, Type, Union

import inflection
from pydantic import BaseModel, Field, validator


class ImmutableModel(BaseModel):
    class Config:
        allow_mutation = False


class PluginDependency(ImmutableModel):
    plugin_name: str = Field()
    required: bool = Field(default=False)

    @validator("plugin_name")
    def plugin_name_underscoring(cls, value: str) -> str:
        return inflection.underscore(value)


class PluginConfig(ImmutableModel):
    ...


@unique
class PlatformType(str, Enum):
    Telegram = "telegram"
    Unknown = "unknown"


class Platform:
    def __init__(self, platform: str) -> None:
        self._value = platform
        try:
            self._type = PlatformType(platform)
        except ValueError:
            self._type = PlatformType.Unknown

    @property
    def type(self) -> PlatformType:
        return self._type

    @property
    def value(self) -> str:
        return self._value


@unique
class Language(str, Enum):
    English = "en"
    Russian = "ru"


class BotConfig(ImmutableModel):
    language: Language = Field(default=Language.Russian)


class SerializedEvent(ImmutableModel):
    event_name: str
    payload: Mapping[str, Any]


class BaseEvent(ABC, ImmutableModel):
    @abstractmethod
    def serialize(self) -> SerializedEvent:
        raise NotImplementedError


class CallbackEvent(BaseEvent):
    event_name: str = Field()
    payload: Mapping[str, Any] = Field()

    def serialize(self) -> SerializedEvent:
        return SerializedEvent(
            event_name=self.event_name,
            payload=self.payload,
        )


class Event(BaseEvent):
    __events__: Dict[str, Type[Event]] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        event_name = cls.event_name()
        if event_name in cls.__events__:
            raise TypeError(
                f"An event with the name {event_name} has already been "
                "initialized before",
            )
        cls.__events__[event_name] = cls

    @classmethod
    def event_name(cls) -> str:
        plugin_name, *_ = cls.__module__.split(".")
        event_name = inflection.underscore(cls.__name__)
        return f"{plugin_name}.{event_name}"

    def serialize(self) -> SerializedEvent:
        return SerializedEvent(
            event_name=self.event_name(),
            payload=self.dict(),
        )

    @classmethod
    def deserialize(
        cls,
        event_name: str,
        payload: Mapping[str, Any],
    ) -> Event:
        if event_type := cls.__events__.get(event_name):
            return event_type(**payload)
        raise TypeError(f"Unknown event name {event_name}")

    def create_action(self, text: str) -> EventAction:
        return EventAction(
            text=text,
            event_name=self.event_name(),
            payload=self.dict(),
        )


class MessageEvent(Event):
    text: Optional[str] = Field()


class ResponseEvent(Event):
    @classmethod
    @abstractmethod
    def title(cls) -> str:
        raise NotImplementedError

    @classmethod
    def description(cls) -> Optional[str]:
        return None


class Action(ImmutableModel):
    text: str = Field()
    action_type: str = Field()


class EventAction(Action):
    action_type: Literal["event"] = Field(default="event")
    event_name: str = Field()
    payload: Mapping[str, Any] = Field(default_factory=dict)


AnyAction = Union[EventAction]
