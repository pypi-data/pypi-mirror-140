from abc import abstractmethod
from http import HTTPStatus
from typing import Generic, Optional, TypeVar

import eztea.json as ezjson
from eztea.web._helper import shorten

ResponseType = TypeVar("ResponseType")


class BaseCallResult(Generic[ResponseType]):
    def __repr__(self):
        if self.is_success:
            s = HTTPStatus(self.status_code)
            msg = f"{s.value} {s.phrase}"
        else:
            msg = f"{self.error}: {shorten(self.message, 80)}"
        return f"<{type(self).__name__} {msg}>"

    @property
    @abstractmethod
    def status_code(self) -> int:
        """response status code"""

    @property
    @abstractmethod
    def data(self) -> dict:
        """response data"""

    @property
    @abstractmethod
    def text(self) -> str:
        """response text"""

    @property
    @abstractmethod
    def raw(self) -> ResponseType:
        """raw response"""

    @property
    def is_success(self):
        return 200 <= self.status_code <= 299

    @property
    def error(self) -> Optional[str]:
        if self.is_success:
            return None
        try:
            return self.data["error"]
        except (ezjson.JSONDecodeError, KeyError, TypeError):
            return str(self.status_code)

    @property
    def message(self) -> Optional[str]:
        if self.is_success:
            return None
        try:
            return self.data["message"]
        except (ezjson.JSONDecodeError, KeyError, TypeError):
            return self.text


class BaseWebTestClient(Generic[ResponseType]):
    @abstractmethod
    def request(self, method="GET", path="/", *args, **kwargs) -> ResponseType:
        """
        Simulate a request to a WSGI application.
        """

    @property
    @abstractmethod
    def raw(self):
        """raw client"""

    @abstractmethod
    def call(self, api: str, **kwargs) -> BaseCallResult:
        """call api"""

    def get(self, path="/", *args, **kwargs) -> ResponseType:
        """
        Simulate a GET request to a WSGI application.
        """
        return self.request("GET", path, *args, **kwargs)

    def head(self, path="/", *args, **kwargs) -> ResponseType:
        """
        Simulate a HEAD request to a WSGI application.
        """
        return self.request("HEAD", path, *args, **kwargs)

    def post(self, path="/", *args, **kwargs) -> ResponseType:
        """
        Simulate a POST request to a WSGI application.
        """
        return self.request("POST", path, *args, **kwargs)

    def put(self, path="/", *args, **kwargs) -> ResponseType:
        """
        Simulate a PUT request to a WSGI application.
        """
        return self.request("PUT", path, *args, **kwargs)

    def options(self, path="/", *args, **kwargs) -> ResponseType:
        """
        Simulate an OPTIONS request to a WSGI application.
        """
        return self.request("OPTIONS", path, *args, **kwargs)

    def patch(self, path="/", *args, **kwargs) -> ResponseType:
        """
        Simulate a PATCH request to a WSGI application.
        """
        return self.request("PATCH", path, *args, **kwargs)

    def delete(self, path="/", *args, **kwargs) -> ResponseType:
        """
        Simulate a DELETE request to a WSGI application.
        """
        return self.request("DELETE", path, *args, **kwargs)
