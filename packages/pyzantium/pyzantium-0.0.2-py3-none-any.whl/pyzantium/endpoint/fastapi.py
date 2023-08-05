from . import Endpoint


class FlaskEndpoint(Endpoint):
    """
    HTTP Endpoint using FastApi

    This endpoint implements an HTTP server using FastApi
    """

    def __init__(
        self,
        name: str,
        address: str,
        port: int,
    ) -> None:
        super().__init__()

        self.address = address
        self.port = port
