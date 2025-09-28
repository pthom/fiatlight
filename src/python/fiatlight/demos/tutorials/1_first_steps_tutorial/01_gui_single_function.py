import fiatlight as fl


def add(a: int, b: int) -> int:
    """A *very* simple function, which adds two **integers**"""
    return a + b


fl.run(add)
