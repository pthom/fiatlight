import functools


def add(a: int, b: int) -> int:
    return a + b


add4 = functools.partial(add, 4)
