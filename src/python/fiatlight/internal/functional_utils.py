from typing import Sequence, Tuple, TypeVar


T = TypeVar("T")


def overlapping_pairs(sequence: Sequence[T]) -> Sequence[Tuple[T, T]]:
    return [(sequence[i], sequence[i + 1]) for i in range(len(sequence) - 1)]
