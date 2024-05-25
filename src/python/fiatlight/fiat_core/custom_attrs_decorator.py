"""with_custom_attrs: a decorator to add custom attributes to a function,
that will be applied to the GUI of its parameters
"""

from __future__ import annotations


from fiatlight.fiat_types.function_types import Function


def with_custom_attrs(**kwargs) -> Function:  # type: ignore
    def decorator(func: Function) -> Function:
        for key, value in kwargs.items():
            setattr(func, key, value)
        return func

    return decorator


def test_fiatlight_custom_attrs() -> None:
    @with_custom_attrs(x__range=(0, 10), y__range=(0, 20))
    def f(x: int, y: int) -> int:
        return x + y

    assert f.x__range == (0, 10)
    assert f.y__range == (0, 20)
