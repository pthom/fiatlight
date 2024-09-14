"""with_fiat_attributes: a decorator to add custom attributes to a function,
that will be applied to the GUI of its parameters
"""

from __future__ import annotations


from typing import Any, Callable, TypeVar
from functools import wraps

FunctionType = TypeVar("FunctionType", bound=Callable[..., Any])
AttrType = TypeVar("AttrType", bound=Any)


def with_fiat_attributes(**kwargs: Any) -> Callable[[FunctionType], FunctionType]:
    def decorator(func: FunctionType) -> FunctionType:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        for key, value in kwargs.items():
            setattr(wrapper, key, value)
        return wrapper  # type: ignore

    return decorator


def add_fiat_attributes(func: FunctionType, **kwargs: Any) -> FunctionType:
    for key, value in kwargs.items():
        setattr(func, key, value)
    return func


def get_fiat_attribute(func: FunctionType, attr_name: str, default_value: AttrType) -> AttrType:
    if hasattr(func, attr_name):
        return getattr(func, attr_name)  # type: ignore
    else:
        return default_value


def set_fiat_attribute(func: FunctionType, attr_name: str, value: AttrType) -> None:
    setattr(func, attr_name, value)


def test_fiatlight_attrs() -> None:
    @with_fiat_attributes(x__range=(0, 10), y__range=(0, 20))
    def f(x: int, y: int) -> int:
        return x + y

    assert hasattr(f, "x__range")
    assert f.x__range == (0, 10)
    assert hasattr(f, "y__range")
    assert f.y__range == (0, 20)
