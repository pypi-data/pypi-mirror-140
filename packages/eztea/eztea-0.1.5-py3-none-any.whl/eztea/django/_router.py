from collections import ChainMap
from typing import Callable, Dict, List

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.urls import URLPattern
from django.urls import path as url_path
from django.views import View
from validr import Invalid

import eztea.json as ezjson
from eztea.web._mimetype import MIME_TYPE_JSON, MIME_TYPE_MULTIPART
from eztea.web._router import BaseRouter, RouterHandlerDefine
from eztea.web.error import (
    BaseWebError,
    RequestParamsInvalid,
    ResponderReturnsInvalid,
)


class RouterHandler:
    def __init__(self, define: RouterHandlerDefine) -> None:
        self._define = define

    def _extract_params(self, request: HttpRequest, kwargs: dict) -> dict:
        data_s = [kwargs]
        if request.content_type == MIME_TYPE_JSON:
            data_s.append(ezjson.loads(request.body))
        elif request.content_type == MIME_TYPE_MULTIPART:
            data_s.append(self._extract_multipart(request))
        else:
            data_s.append(request.POST)
        data_s.append(request.GET)
        request_data = ChainMap(*data_s)
        try:
            params = self._define.validate_params(request_data)
        except Invalid as ex:
            raise RequestParamsInvalid(ex) from ex
        return params

    def _is_json_str(self, value: str):
        value = value.strip()
        for start, end in ("{}", "[]", '""'):
            if value.startswith(start) and value.endswith(end):
                return True
        return False

    def _try_decode_json(self, value: str):
        if self._is_json_str(value):
            try:
                value = ezjson.loads(value)
            except ezjson.JSONDecodeError:
                pass  # ignore
        return value

    def _extract_multipart(self, request: HttpRequest):
        params = {}
        for name, file_info in request.FILES.items():
            data = file_info.read()
            params[name] = dict(
                filename=file_info.name,  # TODO: secure filename
                content_type=file_info.content_type,
                data=data,
            )
        # FIX: django not decode multipart content by content-type, and
        # not able to access the multipart content-type, so try decode json
        # and fallback to plain text if failed.
        for name, value in request.POST.items():
            params[name] = self._try_decode_json(value)
        return params

    def _error_response(self, ex: BaseWebError):
        response = JsonResponse(
            {
                "error": ex.error,
                "message": ex.message,
                "detail": ex.detail,
            },
            safe=False,
            status=ex.status,
        )
        header_items = getattr(ex.headers, "items", None)
        if callable(header_items):
            headers = header_items()
        else:
            headers = ex.headers or []
        for name, value in headers:
            response[name] = value
        return response

    def on_request(self, request: HttpRequest, **kwargs) -> HttpRequest:
        try:
            if self._define.validate_params is not None:
                params = self._extract_params(request, kwargs)
            else:
                params = kwargs
            returns = self._define.func(request, **params)
            if self._define.validate_returns is not None:
                try:
                    returns = self._define.validate_returns(returns)
                except Invalid as ex:
                    raise ResponderReturnsInvalid(str(ex)) from ex
            if returns is not None:
                if not isinstance(returns, HttpResponse):
                    returns = JsonResponse(returns, safe=False)
            else:
                returns = HttpResponse(status=204)
            return returns
        except BaseWebError as ex:
            return self._error_response(ex)


def _make_view(
    handler_define_s: Dict[str, RouterHandlerDefine],
) -> Callable[..., HttpResponse]:
    class RouterView(View):
        pass

    for method, define in handler_define_s.items():
        handler = RouterHandler(define)
        setattr(RouterView, f"{method.lower()}", handler.on_request)
    return RouterView.as_view()


class Router(BaseRouter):
    def to_url_s(self) -> List[URLPattern]:
        url_s = []
        for path, handler_define_s in self._define_s.items():
            view = _make_view(handler_define_s)
            url_s.append(url_path(path.lstrip("/"), view))
        return url_s
