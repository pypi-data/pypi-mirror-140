from abc import ABC
from argparse import Namespace
from types import MappingProxyType
from typing import (
    Any, Callable, Dict, Generic, Mapping, Optional, Sequence, Type, TypeVar,
    final, get_args,
)

from configargparse import ArgumentParser

from jambot_plugin.handlers import (
    CronHandler, EventHandler, HTTPHandler, PingHandler,
)

from .template import JinjaTemplate
from .types import PluginConfig, PluginDependency, ResponseEvent


_TPluginConfig = TypeVar("_TPluginConfig", bound=PluginConfig)
_CCronHandler = Type[CronHandler]
_CEventHandler = Type[EventHandler[_TPluginConfig, Any, Any]]
_CHTTPHandler = Type[HTTPHandler]
_CPingHandler = Type[PingHandler]


@final
class Plugin(ABC, Generic[_TPluginConfig]):
    def __init__(
        self,
        arg_parser: ArgumentParser,
        init_dependencies: Callable[[Namespace], None],
        event_handlers: Sequence[_CEventHandler[_TPluginConfig]] = (),
        cron_handlers: Sequence[_CCronHandler] = (),
        http_handlers: Sequence[_CHTTPHandler] = (),
        ping_handler: Optional[_CPingHandler] = None,
        plugin_dependencies: Sequence[PluginDependency] = (),
        **kwargs: Any,
    ) -> None:
        self.arg_parser = arg_parser
        self.init_dependencies = init_dependencies
        self.event_handlers = tuple(event_handlers)
        self.cron_handlers = tuple(cron_handlers)
        self.http_handlers = tuple(http_handlers)
        self.ping_handler = ping_handler
        self.plugin_dependencies = tuple(plugin_dependencies)

    def load_templates(self) -> Mapping[Type[ResponseEvent], JinjaTemplate]:
        package_name, *_ = self.config_type.__module__.split(".")
        templates: Dict[Type[ResponseEvent], JinjaTemplate] = {}
        for handler in self.event_handlers:
            for event_type in handler.response_event_types():
                event_package_name, *_ = event_type.__module__.split(".")
                if (
                    event_type in templates
                    or package_name != event_package_name
                ):
                    continue
                templates[event_type] = JinjaTemplate(event_type)
        return MappingProxyType(templates)

    @property
    def config_type(self) -> Type[_TPluginConfig]:
        config_type, *_ = get_args(
            self.__orig_class__,  # type: ignore
        )
        return config_type
