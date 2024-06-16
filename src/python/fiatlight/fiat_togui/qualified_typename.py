from fiatlight.fiat_types.base_types import DataType
from typing import Type, Any


def fully_qualified_typename(type_: Type[Any]) -> str:
    """Returns the fully qualified name of a type.
    For example:
        fiatlight.fiat_kits.fiat_image.lut_functions.LutParams
    """
    if not isinstance(type_, type):
        raise RuntimeError(f"fiatlight.to_gui.fully_qualified_typename({type_}): this is not a type!")
    full_typename = f"{type_.__module__}.{type_.__qualname__}"
    if full_typename.startswith("builtins."):
        full_typename = full_typename[len("builtins.") :]
    return full_typename


def fully_qualified_typename_or_str(type_: DataType) -> str:
    """Returns the fully qualified name of a type,
    or the string representation of a complex type (tuple, list, NewType, etc.)"""
    if isinstance(type_, type):
        return fully_qualified_typename(type_)
    else:
        return str(type_)
