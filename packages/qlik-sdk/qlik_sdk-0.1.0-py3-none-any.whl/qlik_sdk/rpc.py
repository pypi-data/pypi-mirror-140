import typing
from threading import Lock, Thread, Condition

import websocket
import json
from functools import reduce


class RpcClient:
    """
    RpcClient represents an WS RPC client, tailored to the
    QIX Associative Engine's RPC API specifically.

    It is safe to use the client.send from multiple threads.
    """

    def __init__(
        self,
        url: str,
        header: typing.List[str] = None,
        request_interceptors=None,
        response_interceptors=None,
    ):
        self._socket = None
        self._id = -1
        self._connected = False
        self._received = None

        if header is None:
            header = []
        if response_interceptors is None:
            response_interceptors = []
        self._response_interceptors = response_interceptors
        if request_interceptors is None:
            request_interceptors = []
        self._request_interceptors = request_interceptors
        self.lock = Lock()
        if not url:
            raise Exception("Empty url")
        self.connect(url, header)

    def _watch_recv(self):
        """
        _watch_recv watches for socket responses.
        Adds the response to _received.
        """

        while True:
            if not self._connected:
                return
            res = self._socket.recv()
            with self._received_added:
                if res:
                    res = json.loads(res)
                    # add response to _received and notify waiting
                    self._received[res["id"]] = res
                    self._received_added.notify_all()

    def connect(self, url: str, header: typing.List[str] = None):
        """
        connect establishes a connection to provided url
        using the specified headers.

        If the client is already connected an exception will
        be raised.
        """
        if header is None:
            header = []

        if self._connected:
            raise Exception("Client already connected")
        socket = websocket.WebSocket()
        socket.connect(url, header=header, suppress_origin=True)
        socket.recv()

        self._socket = socket
        self._received = {}
        self._connected = True
        self._id = -1
        self._received_added = Condition()

        self._watch_recv_thread = Thread(target=self._watch_recv)
        self._watch_recv_thread.start()

    def is_connected(self):
        """
        return connected state
        """

        return self._connected

    def close(self):
        """
        close closes the socket (if it's open).
        """

        if self._connected:
            self._socket.send_close()
            self._connected = False
        if self._watch_recv_thread.is_alive():
            self._watch_recv_thread.join()

    def __enter__(self):
        """
        __enter__ is called when client is used in a 'with' statement.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        __exit__ is called when the 'with' scope is exited. This will call
        the client's close method.
        """

        self.close()

    def send(self, method: str, handle: int, *params):
        """
        send is a thread-safe method that sends a websocket-message with the
        specified method, handle and parameters.
        The resulting response is returned.

        If the client isn't connected an exception is raised.
        """

        if not self._connected:
            raise Exception("Client not connected")

        self.lock.acquire()
        self._id += 1
        id_ = self._id
        self.lock.release()

        encoded_params = []
        for param in params:
            encoded_params.append(param)

        data = {
            "jsonrpc": "2.0",
            "id": self._id,
            "method": method,
            "handle": handle,
            "params": encoded_params,
        }
        data = reduce(lambda d, f: f(d), self._request_interceptors, data)
        json_data = json.dumps(data)
        self._socket.send(json_data)
        res = self._wait_response(id_)
        res = reduce(lambda r, f: f(r), self._response_interceptors, res)
        return_value = None
        if "result" in res:
            return_value = res["result"]
        elif "error" in res:
            raise Exception(res["error"]["message"])
        else:
            return_value = res
        return return_value

    def _wait_response(self, id_):
        """
        _wait_response waits (blocking) for a message with the specified id.
        Internal method that should only be called from send
        """

        with self._received_added:
            while id_ not in self._received:
                self._received_added.wait()
            res = self._received[id_]
            del self._received[id_]
            return res
