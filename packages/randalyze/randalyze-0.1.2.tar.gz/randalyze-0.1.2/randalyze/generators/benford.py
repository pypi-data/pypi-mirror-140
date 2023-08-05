from random import Random
from typing import Any, Tuple


class BenfordRandom(Random):
    """
    Random number generator whose output follows a Benford distribution.

    https://docs.python.org/3.8/library/random.html
    """

    def __init__(self, seed=None, adjustments=5):
        """

        :param adjustments: The number of "adjustments" to make to every random number.
        """
        super().__init__(x=seed)
        self.adjustments = adjustments

    def random(self) -> float:
        result = 1

        for i in range(self.adjustments):
            result *= super().random()

        return result

    def seed(self, a: Any = ..., version: int = ...) -> None:
        super().seed(a, version)

    def getstate(self) -> Tuple[Any, ...]:
        return super().getstate()

    def setstate(self, state: Tuple[Any, ...]) -> None:
        super().setstate(state)
