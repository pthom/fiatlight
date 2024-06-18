from typing import Type, Any
from fiatlight.fiat_types.base_types import DataType


def base_typename(type_: Type[Any]) -> str:
    """Returns the name of a type without the module.
    For example:
        LutParams
    """
    if not isinstance(type_, type):
        raise TypeError(f"base_typename: expected a type, got {type_!r}")
    return type_.__name__


def fully_qualified_typename(type_: Type[Any]) -> str:
    """Returns the fully qualified name of a type.
    For example:
        fiatlight.fiat_kits.fiat_image.lut_functions.LutParams
    """
    if not isinstance(type_, type):
        raise TypeError(f"base_typename: expected a type, got {type_!r}")
    return f"{type_.__module__}.{type_.__qualname__}"


def base_and_qualified_typename(type_: Type[Any]) -> str:
    """Return either the basename or basename(qualified) of a type."""
    basename = base_typename(type_)
    full_typename = fully_qualified_typename(type_)
    if basename == full_typename:
        return basename
    else:
        return f"{basename} ({full_typename})"


def fully_qualified_typename_or_str(type_: DataType) -> str:
    """Returns the fully qualified name of a type,
    or the string representation of a complex type (tuple, list, NewType, etc.)"""
    if isinstance(type_, type):
        return fully_qualified_typename(type_)
    else:
        return str(type_)


def test_typename() -> None:
    from fiatlight.fiat_togui.tests.sample_enum import SampleEnum

    assert fully_qualified_typename(int) == "builtins.int"
    assert base_typename(int) == "int"
    assert base_and_qualified_typename(int) == "int (builtins.int)"

    assert fully_qualified_typename(list) == "builtins.list"
    assert base_typename(list) == "list"
    assert base_and_qualified_typename(list) == "list (builtins.list)"

    assert fully_qualified_typename(SampleEnum) == "fiatlight.fiat_togui.tests.sample_enum.SampleEnum"

    # with pytest.raises(RuntimeError):
    #     fully_qualified_typename(int | None)
    #
    # fully_qualified_typename(Optional[int])
    # fully_qualified_typename(list[int])


def f(type_: type[Any]) -> None:
    print(fully_qualified_typename(type_))


# f(int)
# f(list)
# f(tuple[int, str])


# fully_qualified_typename(int | None)  # mypy catches this as illegal
# fully_qualified_typename(Optional[int])  # mypy catches this as illegal
# fully_qualified_typename(list[int])  # mypy accepts this, but the test isinstance(type_, type) fails
