import requests
from dataclasses import dataclass, field
import typing


@dataclass
class Middleware:
    """
    Base class for creating request and response middleware to modify request and response
    """

    def handle_request(self, req: requests.Request):
        pass

    def handle_response(self, res: requests.Response):
        pass


@dataclass
class ApiKeyAuth(Middleware):
    """
    ApiKeyAuth is request middleware for authorizing using an api key
    """

    api_key: str

    def handle_request(self, req: requests.Request):
        req.headers["authorization"] = "Bearer " + self.api_key


class NoUrlException(Exception):
    """
    NoUrlException represents a missing URL
    """

    pass


class ConnectionException(Exception):
    """
    ConnectionException represents a failure in the request
    The request raised an exception
    ConnectionException is not a 4xx response
    """

    pass


class AuthenticationException(Exception):
    """
    AuthenticationException represents a failure to authenticate
    """

    pass


def _get_dict(o: any):
    """
    get_dict attempts to convert objects to dict, nested
    """
    try:
        d = o.__dict__
        for k in d:
            d[k] = _get_dict(d[k])
        return d
    except (Exception):
        return o


@dataclass
class RestClient:
    """
    RestClient represents a rest client for making api calls
    """

    base_url: str
    auth: Middleware = None
    middlewares: typing.List[Middleware] = field(default_factory=list)

    def rest(
        self,
        path: str,
        method="get",
        data=None,
        params: dict = None,
        headers: dict = None,
    ) -> requests.Response:
        """
        rest sends a request
        """
        if not self.base_url:
            raise NoUrlException("Caller has no 'base_url'")
        if not path.startswith("/api/v1/"):
            path = "/api/v1/" + path.strip("/")

        # If the data can be converted to a dict then send
        # it as json, otherwise send it as data.
        json_data = None
        if data:
            json_data = _get_dict(data)
            if json_data:
                data = None
        if params:
            params = _get_dict(params)

        # Create request.
        req = requests.Request(
            method,
            self.base_url + path,
            data=data,
            json=json_data,
            headers=headers,
            params=params,
        )

        # Use authentication middleware if provided.
        if self.auth:
            self.auth.handle_request(req)

        for mw in self.middlewares:
            mw.handle_request(req)

        with requests.Session() as session:
            prepared = req.prepare()
            try:
                res = session.send(prepared)
            except Exception as exc:
                raise ConnectionException("Connection Error: " + self.base_url) from exc
            for mw in self.middlewares:
                mw.handle_response(res)

            try:
                res.raise_for_status()
            except Exception as e:
                res.close()
                if res.status_code == 401:
                    raise AuthenticationException("Failed to authenticate")
                raise e

            return res
