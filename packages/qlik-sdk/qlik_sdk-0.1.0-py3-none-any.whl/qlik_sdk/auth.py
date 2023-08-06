from dataclasses import dataclass
import typing
import requests
from urllib.parse import urlparse

from .config import Config
from .rest import RestClient, ApiKeyAuth, Middleware
from .rpc import RpcClient


@dataclass
class Auth:
    """
    Auth can be used to make rest and rpc calls
    """

    config: Config
    rest: typing.Callable[
        [str, str, typing.Dict, typing.Dict, typing.Dict], requests.Response
    ]

    def __init__(self, config: Config, middlewares: typing.List[Middleware] = None):
        if middlewares is None:
            middlewares = []
        config.validate()
        self.config = config
        auth = ApiKeyAuth(api_key=self.config.api_key)
        rc = RestClient(base_url=self.config.host, auth=auth, middlewares=middlewares)
        self.rest = rc.rest

    def rpc(
        self,
        app_id: str,
        request_interceptors=None,
        response_interceptors=None,
    ) -> RpcClient:
        """
        rpc returns an RpcClient that can be used to
        connect to the engine for a specific app
        """
        hostname = urlparse(self.config.host).hostname
        ws_url = "wss://" + hostname.strip("/") + "/app/" + app_id
        header = ["Authorization: Bearer %s" % self.config.api_key]
        if request_interceptors is None:
            request_interceptors = []
        if response_interceptors is None:
            response_interceptors = []
        return RpcClient(
            ws_url,
            header,
            request_interceptors=request_interceptors,
            response_interceptors=response_interceptors,
        )
