from . import Chain


class ForkProxy:
    """
    A helper class to ease forking an existing chain

    This class manages an existing chain to create another chain
    in order tho create a fork.
    """

    def __init__(self, base: Chain) -> None:
        self._base = base

    @property
    def base(self) -> Chain:
        return self._base
