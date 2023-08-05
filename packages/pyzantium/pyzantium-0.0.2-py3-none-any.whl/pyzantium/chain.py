from ctypes import Union
import hashlib
from .storage import Storage
from typing import Union


class Chain:
    def __init__(self, *, hash: str, storage: Storage) -> None:
        self._hash = hashlib[hash] if type(hash) == str else hash
        self._storage = storage
        self._last_hash = storage[-1]

    @property
    def storage(self):
        return self._storage

    @property
    def hash(self):
        return self._hash

    @property
    def last_block_hash(self):
        return self._last_hash
