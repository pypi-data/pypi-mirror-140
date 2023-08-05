from nis import match
from . import Storage
from typing import Union
from pathlib import Path
from os import mkdir


class DiskStorage(Storage):
    """
    Disk storage for storing blocks of a blockchain on disk

    This class is the default implementation of storage system for blockchain.
    Blocks are stored by their hash similar to git's object storage:

        #. In root directory of storage, there will be a directory named `blocks`.

        #. In `blocks` directory will be some directories with 2 letters name.
           name is infered from two beggining letters of block's hash.

        #. A file named `index` is stored in root directory of storage that is
           a simple text file with hashes of blocks sorted by time in it (most 
           recent last) to accelerate access to blocks
    """

    def __init__(
        self,
        path: Union[str, Path],
        create: bool = False,
        error_if_exists: bool = False,
    ) -> None:
        """
        Initialize or open existing blockchain disk storage

        :param path: str or pathlib.Path that specifies path on disk to use.
        """
        super().__init__("Disk")

        self._path = path if type(path) == Path else Path(path)

        if error_if_exists and self._path.exists():
            raise FileExistsError(path)

        if create:
            mkdir(self._path)

        self._index_file = open(self._path + "/index", "r")
    
    def __getitem__(self, hash: bytes):
        return super().__getitem__(hash)
