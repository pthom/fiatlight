import numpy as np
from numpy.typing import NDArray
import time


LATENCY = 0.000005


def set_latency(latency: float) -> None:
    global LATENCY
    LATENCY = latency


def get_latency() -> float:
    return LATENCY


class NumbersList:
    values: NDArray[np.int_]

    def __init__(self, values: NDArray[np.int_]) -> None:
        self.values = values

    def __getitem__(self, index: int) -> int:
        if LATENCY > 0:
            time.sleep(LATENCY)  # Introduce delay
        return self.values[index]  # type: ignore

    def __setitem__(self, key: int, value: int) -> None:
        if LATENCY > 0:
            time.sleep(LATENCY)  # Introduce delay
        self.values[key] = value

    def __len__(self) -> int:
        return len(self.values)

    def slice(self, start: int, end: int) -> "NumbersList":
        return NumbersList(self.values[start:end])

    def __str__(self) -> str:
        return str(self.values)

    def copy(self) -> "NumbersList":
        return NumbersList(self.values.copy())

    def __copy__(self) -> "NumbersList":
        return self.copy()
