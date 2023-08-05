from datetime import datetime


class Block:
    def __init__(self) -> None:
        self._hash = bytes()
        self._prev_hash = bytes()
        self._nonce = None
        self._timestamp = None
        self._data = None
