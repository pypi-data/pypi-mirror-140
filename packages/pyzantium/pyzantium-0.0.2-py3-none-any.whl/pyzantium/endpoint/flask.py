from . import Endpoint
from flask import Flask


class FlaskEndpoint(Endpoint):
    """
    HTTP Endpoint using Flask

    This endpoint implements an HTTP server using flask freamwork
    """

    def __init__(
        self,
        name: str,
        address: str,
        port: int,
    ) -> None:
        super().__init__()

        self.app = Flask(name, None, None)
        self.address = address
        self.port = port
