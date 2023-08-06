import socket
import json
from typing import Callable
import logging


class InfoService:
    def __init__(self, port: int = 7777):
        self._logger = logging.getLogger("InfoService")

        self._broad_cast_receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._broad_cast_receiver.bind(("", port))

        self._callbacks: list[Callable[[dict], None]] = []

    def register_info_callback(self, callback: Callable[[dict], None]):
        self._callbacks.append(callback)

    def try_read(self, block_until_response: bool = True):
        response = None
        while response is None:
            try:
                data, server = self._broad_cast_receiver.recvfrom(8192)
                response = json.loads(data.decode("utf-8"))
            except Exception as e:
                self._logger.error(e)

            # if we have data or we aren't blocking until we get a response
            if data is not None or not block_until_response:
                break

        if response is not None:
            for c in self._callbacks:
                c(response)


def on_info_receive(data: dict):
    print(json.dumps(data))


if __name__ == "__main__":
    info_service: InfoService = InfoService()
    info_service.register_info_callback(on_info_receive)
    while True:
        info_service.try_read()
