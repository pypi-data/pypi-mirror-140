from abc import ABC, abstractmethod
from typing import Optional


class Endpoint(ABC):
    """
    Abstract base class for communication channels to other nodes (endpoints)

    This class is the window to out world. Both other nodes and peers will
    communicate with this class to submit requiests and other works to
    blockchain.
    """

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def submission() -> bool:
        """
        Status of submission of data from peers

        :return: status
        """
        ...


from .flask import FlaskEndpoint
