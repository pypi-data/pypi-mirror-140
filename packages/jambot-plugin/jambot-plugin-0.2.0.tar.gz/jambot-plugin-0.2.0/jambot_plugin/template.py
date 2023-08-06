from pathlib import Path
from typing import Tuple, Type, final

from jinja2 import Environment, PackageLoader, TemplateNotFound

from .types import ResponseEvent


ALLOWED_TEMPLATE_FILE_EXTENSIONS: Tuple[str, ...] = ("j2", "jinja2")


def _inject_event_mock(event_name: str) -> str:
    raise NotImplementedError


@final
class JinjaTemplate:
    def __init__(self, event_type: Type[ResponseEvent]) -> None:
        self._path = self._get_template_path(event_type)
        with self._path.open("r") as file:
            self._template_body = file.read().strip()

    @property
    def path(self) -> Path:
        return self._path

    @property
    def template_body(self) -> str:
        return self._template_body

    def _get_template_path(self, event_type: Type[ResponseEvent]) -> Path:
        package_name, *_ = event_type.__module__.split(".")
        env = self._make_jinja2_env(package_name)
        _, event_name = event_type.event_name().split(".")
        for ext in ALLOWED_TEMPLATE_FILE_EXTENSIONS:
            try:
                template = env.get_template(f"{event_name}.{ext}")
                if template.filename:
                    return Path(template.filename)
            except TemplateNotFound:
                pass
        raise TemplateNotFound(name=event_name)

    @staticmethod
    def _make_jinja2_env(package_name: str) -> Environment:
        env = Environment(loader=PackageLoader(package_name, "templates"))
        env.globals.update(inject_event=_inject_event_mock)
        return env
