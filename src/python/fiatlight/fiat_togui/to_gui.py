from inspect import isclass
from fiatlight.fiat_types import DataType, FiatAttributes
from fiatlight.fiat_types import typename_utils
from fiatlight.fiat_core.any_data_with_gui import AnyDataWithGui, AnyDataWithGui_UnregisteredType
from .optional_with_gui import OptionalWithGui
from .enum_with_gui import EnumWithGui
from .list_with_gui import ListWithGui
from .gui_registry import gui_factories, _GUI_FACTORIES
from .handle_annotated_types import try_convert_type_annotations_to_fiat_attributes
from .to_gui_context import TO_GUI_CONTEXT
import types
from types import NoneType
from enum import Enum

from typing import Any, List, Type
import typing


def call_factor(type_: Type[Any], fiat_attributes: FiatAttributes) -> AnyDataWithGui[Any]:
    """Central function to convert a type name to a GUI representation."""
    typename = typename_utils.fully_qualified_typename(type_)
    if gui_factories().can_handle_typename(typename):
        return gui_factories()._factor(typename, fiat_attributes)

    # if we reach this point, we have no GUI implementation for the type
    TO_GUI_CONTEXT.add_missing_gui_factory(typename)
    return AnyDataWithGui_UnregisteredType(typename, type_)


def _any_annotated_type_to_gui_impl(
    type_: typing.Annotated[Type[Any], Any], fiat_attributes: FiatAttributes
) -> AnyDataWithGui[Any]:
    base_type, *annotations = typing.get_args(type_)
    assert isinstance(annotations, list)
    gui_type = call_factor(base_type, fiat_attributes)
    try_convert_type_annotations_to_fiat_attributes(base_type, annotations, gui_type)
    return gui_type


def _any_optional_type_to_gui_impl(
    inner_type: Type[Any] | typing.Union[Type[Any], Any],
    fiat_attributes: FiatAttributes,
    is_artificial_union: bool = False,
) -> AnyDataWithGui[Any]:
    inner_gui = _any_type_to_gui_impl(inner_type, fiat_attributes, is_artificial_union=is_artificial_union)
    optional_gui = OptionalWithGui(inner_gui)
    AnyDataWithGui.propagate_label_and_tooltip(inner_gui, optional_gui)
    return optional_gui


def _extract_optionals_from_union(union_args: tuple[type[Any], ...]) -> tuple[type[Any], ...] | None:
    nb_none = 0
    for type_ in union_args:
        if type_ is NoneType:
            nb_none += 1

    if nb_none != 1:
        return None

    non_none_types = tuple(type_ for type_ in union_args if type_ is not NoneType)
    return non_none_types


def _any_union_type_to_gui_impl(
    union_args: tuple[type[Any], ...], fiat_attributes: FiatAttributes
) -> AnyDataWithGui[Any]:
    if len(union_args) == 0:
        raise RuntimeError(f"_any_union_type_to_gui_impl{union_args} could not extract union args")
    if len(union_args) == 1:
        raise RuntimeError(f"_any_union_type_to_gui_impl{union_args}: found only one type")

    inner_optional_types = _extract_optionals_from_union(union_args)
    if inner_optional_types is not None:
        if len(inner_optional_types) == 1:
            return _any_optional_type_to_gui_impl(inner_optional_types[0], fiat_attributes)
        else:
            return _any_optional_type_to_gui_impl(inner_optional_types, fiat_attributes, is_artificial_union=True)

    union_typename = "UNION_UNION-" + str(union_args)
    if _GUI_FACTORIES.can_handle_typename(union_typename):
        return _GUI_FACTORIES._factor(union_typename, fiat_attributes)

    TO_GUI_CONTEXT.add_missing_gui_factory(union_typename)
    return AnyDataWithGui_UnregisteredType("unimplemented", type(Any))


def _any_new_type_to_gui_impl(type_: Type[Any], fiat_attributes: FiatAttributes) -> AnyDataWithGui[Any]:
    """Handle NewType types."""
    assert hasattr(type_, "__supertype__")
    _supertype = type_.__supertype__  # noqa
    return call_factor(type_, fiat_attributes)


def _any_enum_type_to_gui_impl(type_: Type[Enum], fiat_attributes: FiatAttributes) -> AnyDataWithGui[Any]:
    """Handle Enum types."""
    assert issubclass(type_, Enum)
    return EnumWithGui(type_)


def _any_list_type_to_gui_impl(type_: Type[List[Any]], fiat_attributes: FiatAttributes) -> AnyDataWithGui[Any]:
    """Handle list types."""
    element_type = typing.get_args(type_)[0]
    inner_gui = _any_type_to_gui_impl(element_type, fiat_attributes)
    list_gui = ListWithGui(inner_gui)
    AnyDataWithGui.propagate_label_and_tooltip(inner_gui, list_gui)
    return list_gui


def _any_tuple_type_to_gui_impl(
    element_types: tuple[type, ...], fiat_attributes: FiatAttributes
) -> AnyDataWithGui[Any]:
    """Handle tuple types."""
    from fiatlight.fiat_togui.tuple_with_gui import TupleWithGui

    empty_fiat_attrs = FiatAttributes({})
    element_guis_tuple = tuple(_any_type_to_gui_impl(element_type, empty_fiat_attrs) for element_type in element_types)
    tuple_gui = TupleWithGui(element_guis_tuple, fiat_attributes)
    return tuple_gui


def _any_type_to_gui_impl(
    type_: Type[Any] | typing.Annotated[Type[Any], Any] | typing.Union[Type[Any], Any],
    fiat_attributes: FiatAttributes,
    is_artificial_union: bool = False,
) -> AnyDataWithGui[Any]:
    """Converts a type to a GUI representation."""
    typename = typename_utils.fully_qualified_typename(type_)
    TO_GUI_CONTEXT.enqueue_typename(typename)

    if typing.get_origin(type_) is typing.Annotated:
        return _any_annotated_type_to_gui_impl(type_, fiat_attributes)

    elif typing.get_origin(type_) is typing.Union or isinstance(type_, types.UnionType):
        union_args = typing.get_args(type_)
        assert isinstance(union_args, tuple)
        return _any_union_type_to_gui_impl(union_args, fiat_attributes)
    if is_artificial_union:
        assert isinstance(type_, tuple)
        return _any_union_type_to_gui_impl(type_, fiat_attributes)

    elif typing.get_origin(type_) is list:
        return _any_list_type_to_gui_impl(type_, fiat_attributes)

    elif typing.get_origin(type_) is tuple:
        element_types = typing.get_args(type_)
        return _any_tuple_type_to_gui_impl(element_types, fiat_attributes)

    elif hasattr(type_, "__supertype__"):  # Check if it's a NewType
        return _any_new_type_to_gui_impl(type_, fiat_attributes)

    elif isclass(type_) and issubclass(type_, Enum):  #
        return _any_enum_type_to_gui_impl(type_, fiat_attributes)

    else:
        return call_factor(type_, fiat_attributes)


def any_type_to_gui(type_: Type[Any] | typing.Annotated[Type[Any], Any], **fiat_attributes: Any) -> AnyDataWithGui[Any]:
    """Converts a type to a GUI representation."""
    attr_as_dict = FiatAttributes(fiat_attributes)
    return _any_type_to_gui_impl(type_, attr_as_dict)


def _to_data_with_gui_impl(
    value: DataType,
    fiat_attributes: FiatAttributes,
) -> AnyDataWithGui[DataType]:
    """Convert a value to a GUI representation."""
    r = _any_type_to_gui_impl(type(value), fiat_attributes)
    r.value = value
    return r


def to_data_with_gui(value: DataType, **fiat_attributes: Any) -> AnyDataWithGui[DataType]:
    """Convert a value to a GUI representation."""
    attr_as_dict = FiatAttributes(fiat_attributes)
    return _to_data_with_gui_impl(value, attr_as_dict)
