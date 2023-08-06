import httpx

from eztea.web._helper import join_url_path
from eztea.web._testing import BaseCallResult, BaseWebTestClient

__all__ = (
    "CallResult",
    "WebTestClient",
)


class CallResult(BaseCallResult[httpx.Response]):
    def __init__(self, response: httpx.Response):
        self._response = response

    @property
    def raw(self) -> httpx.Response:
        return self._response

    @property
    def status_code(self) -> int:
        return self._response.status_code

    @property
    def data(self) -> dict:
        return self._response.json()

    @property
    def text(self) -> str:
        return self._response.text


class WebTestClient(BaseWebTestClient[httpx.Response]):
    def __init__(self, app, *, headers=None, prefix: str = ""):
        self.__app = app
        self.__headers = headers
        self.__prefix = prefix
        self.__client = self.__create_client()

    def __create_client(self):
        transport = httpx.WSGITransport(
            app=self.__app,
            raise_app_exceptions=False,
        )
        return httpx.Client(
            transport=transport,
            base_url="http://testserver.localhost",
            headers=self.__headers,
        )

    def __enter__(self):
        self.__client.__enter__()
        return self

    def __exit__(self, *args, **kwargs):
        self.__client.__exit__(*args, **kwargs)

    @property
    def raw(self) -> httpx.Client:
        return self.__client

    def request(
        self,
        method: str = "GET",
        path: str = "/",
        *args,
        **kwargs,
    ) -> httpx.Response:
        """
        Simulate a request to a WSGI application.
        """
        path = join_url_path(self.__prefix, path)
        return self.__client.request(method, path, *args, **kwargs)

    def call(self, api: str, **kwargs) -> CallResult:
        response = self.post(f"/{api}", json=kwargs)
        return CallResult(response)
