from typing import get_origin, get_args, NewType, Any, Type, _GenericAlias, Union  # type: ignore


# A RuntimeType is a type that Python knows at runtime
# (not a type hint, such as List[int], which is known as list at runtime)
# It is an alias for Type[Any], aka type[Any]
RuntimeType = Type[Any]

# A generic alias is a type hint that represents a generic type,
#    such as List[int], Dict[str, int], int | None, etc.
GenericAlias = _GenericAlias

# A type alias for types that include runtime types and generic types
TypeLike = Union[RuntimeType, _GenericAlias, NewType]


def fully_qualified_runtime_typename(type_: RuntimeType) -> str:
    """Returns the fully qualified name of a runtime type.
    A runtime type is a type that Python knows at runtime (i.e., not a type hint, such as List[int],
    which is known as list at runtime).
    For example:
        fiatlight.fiat_kits.fiat_image.lut_functions.LutParams
    """
    if not isinstance(type_, type) and not hasattr(type_, "__origin__"):
        raise TypeError(f"Expected a type, got {type_!r}")

    # Handle generic types (e.g., list[int], dict[str, int])
    origin = get_origin(type_)
    if origin is not None:
        args = ", ".join(fully_qualified_runtime_typename(arg) for arg in get_args(type_))
        return f"{origin.__module__}.{origin.__qualname__}[{args}]"

    # Handle non-generic types
    return f"{type_.__module__}.{type_.__qualname__}"


def base_runtime_typename(type_: RuntimeType) -> str:
    """Returns the name of a type without the module.
    For example:
        LutParams
    """
    if not isinstance(type_, type) and not hasattr(type_, "__origin__"):
        raise TypeError(f"base_typename: expected a type, got {type_!r}")

    # Handle generic types
    origin = get_origin(type_)
    if origin is not None:
        args = ", ".join(base_runtime_typename(arg) for arg in get_args(type_))
        return f"{origin.__name__}[{args}]"

    # Handle non-generic types
    r = type_.__name__
    if r.startswith("builtins."):
        r = r[len("builtins.") :]
    return r


def fully_qualified_generic_typename(type_: GenericAlias) -> str:  # type: ignore
    """Returns the fully qualified name of a generic type.
    For example:
        builtins.list[int]
    """
    origin = get_origin(type_)
    if origin is None:
        raise TypeError(f"Expected a generic type, got {type_!r}")

    args = ", ".join(fully_qualified_typename(arg) for arg in get_args(type_))
    return f"{origin.__module__}.{origin.__qualname__}[{args}]"  # type: ignore


def base_generic_typename(type_: GenericAlias) -> str:  # type: ignore
    """Returns the name of a generic type without the module.
    For example:
        list[int]
    """
    origin = get_origin(type_)
    if origin is None:
        raise TypeError(f"Expected a generic type, got {type_!r}")

    args = ", ".join(base_typename(arg) for arg in get_args(type_))
    return f"{origin.__name__}[{args}]"


def fully_qualified_newtype_typename(new_type: type[Any]) -> str:
    """Returns the fully qualified name of a NewType
    This is a custom format, e.g.:
        fiatlight.fiat_types.typename_utils.MyNewType --|> NewType(builtins.int)
    """
    if not isinstance(new_type, NewType):  # noqa
        raise TypeError(f"Expected a NewType, got {new_type!r}")
    str_type = str(new_type)
    return f"{str_type}"


def base_newtype_typename(new_type: type[Any]) -> str:
    """Returns the base name of a NewType
    This is a custom format, e.g.:
        MyNewType --|> NewType(int)
    """
    if not isinstance(new_type, NewType):  # noqa
        raise TypeError(f"Expected a NewType, got {new_type!r}")
    supertype = new_type.__supertype__  # noqa
    str_newtype_full = str(new_type)
    str_newtype_base = str_newtype_full.split(".")[-1]
    return f"{str_newtype_base}"


def fully_qualified_typename(type_: TypeLike) -> str:
    """Returns the fully qualified name of a type, generic type, or NewType."""
    if isinstance(type_, NewType):  # noqa
        return fully_qualified_newtype_typename(type_)  # type: ignore
    elif isinstance(type_, type):
        return fully_qualified_runtime_typename(type_)
    else:
        try:
            return fully_qualified_generic_typename(type_)
        except TypeError:
            # Can happen for AnnotatedType (and may be others)
            return str(type_)


def base_typename(type_: TypeLike) -> str:
    """Returns the base name of a type, generic type, or NewType."""
    if isinstance(type_, NewType):  # noqa
        return base_newtype_typename(type_)  # type: ignore
    elif isinstance(type_, type):
        return base_runtime_typename(type_)
    else:
        try:
            return base_generic_typename(type_)
        except TypeError:
            # Can happen for AnnotatedType (and may be others)
            return str(type_)


def base_and_qualified_typename(type_: TypeLike) -> str:
    """Return either the basename or basename(qualified) of a type."""
    basename = base_typename(type_)
    full_typename = fully_qualified_typename(type_)
    if basename == full_typename:
        return basename
    else:
        return f"{basename} ({full_typename})"


__all__ = [
    "base_typename",
    "fully_qualified_typename",
    "base_and_qualified_typename",
]
