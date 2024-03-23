from typing import Sequence, Tuple, TypeVar, Callable, TypeAlias


VoidFunction: TypeAlias = Callable[[], None]


T = TypeVar("T")


def overlapping_pairs(sequence: Sequence[T]) -> Sequence[Tuple[T, T]]:
    return [(sequence[i], sequence[i + 1]) for i in range(len(sequence) - 1)]


def sequence_void_functions(f1: VoidFunction | None, f2: VoidFunction | None) -> VoidFunction:
    def void_function() -> None:
        if f1 is not None:
            f1()
        if f2 is not None:
            f2()

    return void_function
