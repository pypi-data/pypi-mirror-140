from abc import ABC, abstractmethod
from enum import Enum, unique
from functools import partial
from http import HTTPStatus
from typing import Any, Callable, Coroutine, Dict, Optional

import fast_json
from multidict import CIMultiDict, CIMultiDictProxy, MultiDictProxy
from yarl import URL

from jambot_plugin.deps import consumer

from .base_handler import ServiceHandler


@unique
class HTTPMethod(str, Enum):
    METH_GET = "GET"
    METH_POST = "POST"
    METH_PUT = "PUT"
    METH_DELETE = "DELETE"


class HTTPRequest:
    __slots__ = (
        "_method",
        "_url",
        "_match_info",
        "_query",
        "_text",
        "_headers",
    )

    def __init__(
        self,
        method: HTTPMethod,
        url: URL,
        match_info: Dict[str, str],
        query: MultiDictProxy[str],
        text: str,
        headers: CIMultiDictProxy[str],
    ) -> None:
        self._method = method
        self._url = url
        self._match_info = match_info
        self._query = query
        self._text = text
        self._headers = headers

    @property
    def method(self) -> HTTPMethod:
        return self._method

    @property
    def url(self) -> URL:
        return self._url

    @property
    def match_info(self) -> Dict[str, str]:
        return self._match_info

    @property
    def query(self) -> MultiDictProxy[str]:
        return self._query

    @property
    def text(self) -> str:
        return self._text

    @property
    def headers(self) -> CIMultiDictProxy[str]:
        return self._headers

    def json(self) -> Any:
        return fast_json.loads(self._text)


class HTTPResponse:
    __slots__ = ("_body", "_status", "_text", "_headers", "_content_type")

    def __init__(
        self,
        status: int = HTTPStatus.OK,
        body: Optional[Any] = None,
        text: Optional[str] = None,
        headers: Optional[CIMultiDict[str]] = None,
        content_type: Optional[str] = None,
    ) -> None:
        if text and body:
            raise ValueError(
                "only one of data, text, or body should be specified",
            )
        self._status = status
        self._body = body
        self._text = text
        self._headers = headers
        self._content_type = content_type

    @property
    def status(self) -> int:
        return self._status

    @property
    def body(self) -> Optional[Any]:
        return self._body

    @property
    def text(self) -> Optional[str]:
        return self._text

    @property
    def headers(self) -> Optional[CIMultiDict[str]]:
        return self._headers

    @property
    def content_type(self) -> Optional[str]:
        return self._content_type


def json_response(
    data: Any,
    *,
    status: int = 200,
    headers: Optional[CIMultiDict[str]] = None,
    content_type: str = "application/json",
) -> HTTPResponse:
    return HTTPResponse(
        status=status,
        text=fast_json.dumps(data),
        headers=headers,
        content_type=content_type,
    )


HandlerFunc = Callable[[HTTPRequest], Coroutine[Any, Any, HTTPResponse]]

_THandler = Callable[..., Coroutine[Any, Any, HTTPResponse]]
_TMiddleware = Callable[..., Coroutine[Any, Any, HTTPResponse]]


def middleware(
    middleware_func: _TMiddleware,
) -> Callable[[_THandler], _THandler]:
    def middleware_wrapper(handler: _THandler) -> _THandler:
        async def handler_wrapper(
            self: "HTTPHandler",
            request: HTTPRequest,
        ) -> HTTPResponse:
            partial_handler = partial(handler, self)
            return await consumer(middleware_func)(request, partial_handler)

        return handler_wrapper

    return middleware_wrapper


class HTTPHandler(ABC, ServiceHandler):
    @classmethod
    @abstractmethod
    def method(cls) -> HTTPMethod:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def route(cls) -> str:
        raise NotImplementedError

    @abstractmethod
    async def handle(self, request: HTTPRequest) -> HTTPResponse:
        raise NotImplementedError
