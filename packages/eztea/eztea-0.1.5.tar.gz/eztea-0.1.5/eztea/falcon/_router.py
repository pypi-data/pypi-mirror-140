from collections import ChainMap
from typing import Any, Dict, List

import falcon
from falcon.media.multipart import MultipartForm
from validr import Invalid

from eztea import json
from eztea.web._mimetype import (
    MIME_TYPE_JSON,
    MIME_TYPE_MULTIPART,
    MIME_TYPE_URLENCODED,
)
from eztea.web._router import BaseRouter, RouterHandlerDefine
from eztea.web.error import RequestParamsInvalid, ResponderReturnsInvalid

from .request import Request, parse_content_type


class RouterHandler:
    def __init__(
        self,
        define: RouterHandlerDefine,
    ) -> None:
        self._define = define

    def _extract_params(self, request: Request, kwargs: dict) -> dict:
        data_s = [kwargs]
        media = request.get_media(default_when_empty=None)
        if media is not None:
            if request.mimetype == MIME_TYPE_MULTIPART:
                data_s.append(self._extract_multipart(media))
            else:
                data_s.append(media)
        if request.params is not None:
            data_s.append(request.params)
        request_data = ChainMap(*data_s)
        try:
            params = self._define.validate_params(request_data)
        except Invalid as ex:
            raise RequestParamsInvalid(ex) from ex
        return params

    def _extract_multipart(self, form: MultipartForm):
        params = {}
        for part in form:
            is_file = bool(part.filename)
            if is_file:
                params[part.name] = dict(
                    filename=part.secure_filename,
                    content_type=part.content_type,
                    data=part.get_data(),
                )
            else:
                mimetype, _ = parse_content_type(part.content_type)
                if mimetype in (MIME_TYPE_URLENCODED, MIME_TYPE_JSON):
                    params[part.name] = part.get_media()
                else:
                    params[part.name] = part.get_text()
        return params

    def on_request(
        self,
        request: Request,
        response: falcon.Response,
        **kwargs,
    ):
        if self._define.validate_params is not None:
            params = self._extract_params(request, kwargs)
        else:
            # fallback to falcon usage with path match params
            params = kwargs
        ctx = ResponderContext(
            request=request, response=response, params=params
        )
        returns = self._define.func(ctx, **params)
        if self._define.validate_returns is not None:
            try:
                returns = self._define.validate_returns(returns)
            except Invalid as ex:
                raise ResponderReturnsInvalid(str(ex)) from ex
        if returns is not None:
            response.text = json.dumps(returns)
            response.status = falcon.HTTP_200
            response.content_type = falcon.MEDIA_JSON


class ResponderContext:
    def __init__(
        self,
        request: Request,
        response: falcon.Response,
        params: Dict[str, Any] = None,
    ) -> None:
        self.request = request
        self.response = response
        self.params = params


class RouterResource:
    def __init__(
        self, path: str, handler_define_s: Dict[str, RouterHandlerDefine]
    ) -> None:
        self.path = path
        for method, handler_define in handler_define_s.items():
            handler = RouterHandler(handler_define)
            setattr(self, f"on_{method.lower()}", handler.on_request)


class Router(BaseRouter):
    def to_resource_s(self) -> List[RouterResource]:
        resource_s = []
        for path, handler_define_s in self._define_s.items():
            resource_s.append(RouterResource(path, handler_define_s))
        return resource_s
