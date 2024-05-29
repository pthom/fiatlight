"""with_custom_attrs: a decorator to add custom attributes to a function,
that will be applied to the GUI of its parameters
"""

from __future__ import annotations


from typing import Any, Callable, TypeVar
from functools import wraps

FunctionType = TypeVar("FunctionType", bound=Callable[..., Any])


def with_custom_attrs(**kwargs: Any) -> Callable[[FunctionType], FunctionType]:
    def decorator(func: FunctionType) -> FunctionType:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        for key, value in kwargs.items():
            setattr(wrapper, key, value)
        return wrapper  # type: ignore

    return decorator


def test_fiatlight_custom_attrs() -> None:
    @with_custom_attrs(x__range=(0, 10), y__range=(0, 20))
    def f(x: int, y: int) -> int:
        return x + y

    assert hasattr(f, "x__range")
    assert f.x__range == (0, 10)
    assert hasattr(f, "y__range")
    assert f.y__range == (0, 20)
