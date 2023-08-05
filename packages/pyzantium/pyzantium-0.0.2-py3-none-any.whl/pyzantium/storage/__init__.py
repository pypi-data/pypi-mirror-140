from abc import ABC, abstractmethod


class Storage(ABC):
    """
    Abstract base class for storage mechanisms

    All storage mechanisms must implement this base class.
    This class provides an abstraction to separate storage from higher level
    blockchain machinary.
    """

    def __init__(self, name: str) -> None:
        super().__init__()

    @abstractmethod
    def __getitem__(self, hash: bytes):
        ...

    @abstractmethod
    def __contains__(self, hash: bytes) -> bool:
        ...

    @abstractmethod
    def __iter__(self):
        ...

    @abstractmethod
    def __next__(self):
        ...

    @abstractmethod
    def __len__(self) -> int:
        ...

from .disk import DiskStorage