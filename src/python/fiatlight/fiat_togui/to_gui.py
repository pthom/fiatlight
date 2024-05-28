import dataclasses
from dataclasses import dataclass

import pydantic

from fiatlight.fiat_types import UnspecifiedValue, DataType, CustomAttributesDict
from fiatlight.fiat_types.base_types import ScopeStorage, JsonDict
from fiatlight.fiat_togui import primitives_gui
from fiatlight.fiat_core.any_data_with_gui import AnyDataWithGui
from fiatlight.fiat_core.param_with_gui import ParamKind, ParamWithGui
from fiatlight.fiat_core.function_with_gui import FunctionWithGui
from fiatlight.fiat_core.output_with_gui import OutputWithGui
from fiatlight.fiat_togui.composite_gui import OptionalWithGui, EnumWithGui, ListWithGui
from fiatlight.fiat_togui.function_signature import get_function_signature
from fiatlight.fiat_types.fiat_number_types import FloatInterval, IntInterval
from .dataclass_gui import DataclassLikeType
from enum import Enum

import inspect
import logging
from typing import TypeAlias, Callable, Any, Tuple, List, Type


GuiFactory = Callable[[], AnyDataWithGui[DataType]]
FunctionWithGuiFactory = Callable[[], FunctionWithGui]


class _ToGuiContext(pydantic.BaseModel):
    last_typenames_handled: list[str] = pydantic.Field(default_factory=list)
    last_functions_handled: list[str] = pydantic.Field(default_factory=list)
    missing_gui_factories: list[str] = pydantic.Field(default_factory=list)

    def enqueue_typename(self, typename: str) -> None:
        if len(self.last_typenames_handled) > 0 and self.last_typenames_handled[-1] == typename:
            return
        self.last_typenames_handled.append(typename)

    def enqueue_function(self, function_name: str) -> None:
        if len(self.last_functions_handled) > 0 and self.last_functions_handled[-1] == function_name:
            return
        self.last_functions_handled.append(function_name)

    def add_missing_gui_factory(self, typename: str) -> None:
        if typename in self.missing_gui_factories:
            return
        logging.warning(f"Type {typename} not registered in gui_factories()")
        self.missing_gui_factories.append(typename)

    def info(self) -> str:
        # Return the 3 last typenames and functions handled
        from fiatlight.fiat_doc import code_utils

        last_typenames_handled = "\n".join(self.last_typenames_handled[-3:])
        last_typenames_handled = "\n" + code_utils.indent_code(last_typenames_handled, 4)
        last_functions_handled = "\n".join(self.last_functions_handled[-3:])
        last_functions_handled = "\n" + code_utils.indent_code(last_functions_handled, 4)
        all_missing_gui_factories = "\n".join(self.missing_gui_factories)
        all_missing_gui_factories = "\n" + code_utils.indent_code(all_missing_gui_factories, 4)

        intro = (
            "It seems you experience an error during the transformation of a type or function into a GUI. "
            "To help you, here is some context about the GUI creation:\n"
        )
        outro = "(most recent functions and typenames are at the bottom)"

        msg = intro

        if len(self.missing_gui_factories) > 0:
            msg += "Missing GUI factories:" + all_missing_gui_factories + "\n"

        msg += "Last typenames transformed to GUI:" + last_typenames_handled + "\n"
        msg += "Last functions transformed to GUI:" + last_functions_handled + "\n"
        msg += outro

        return msg


_TO_GUI_CONTEXT = _ToGuiContext()


def to_gui_context_info() -> str:
    return _TO_GUI_CONTEXT.info()


def _wip_extract_union_list(type_class_name: str) -> List[str]:
    if type_class_name.startswith("typing.Union[") and type_class_name.endswith("]"):
        inner_type_str = type_class_name[len("typing.Union[") : -1]
        # inner_type_strs = _parse_typeclasses_list(inner_type_str)
        inner_type_strs = inner_type_str.split(", ")
        return inner_type_strs
    return []


def _extract_optional_typeclass(type_class_name: str) -> Tuple[bool, str]:
    if type_class_name.startswith("typing.Optional[") and type_class_name.endswith("]"):
        return True, type_class_name[16:-1]
    if type_class_name.endswith(" | None"):
        return True, type_class_name[:-7]

    # If the type is a union of multiple types, and one of them is NoneType, we can convert it to Optional
    union_list = _wip_extract_union_list(type_class_name)
    if len(union_list) >= 2 and "NoneType" in union_list:
        union_list.remove("NoneType")
        union_str = ", ".join(union_list)
        new_union_type = f"typing.Union[{union_str}]"
        return True, new_union_type

    return False, type_class_name


def _extract_enum_typeclass(type_class_name: str, scope_storage: ScopeStorage) -> Tuple[bool, str]:
    # An enum type will be displayed as
    #     <enum 'EnumName'>
    # or
    #     <enum 'EnumName' of 'module_name'>
    if type_class_name.startswith("<enum '") and type_class_name.endswith("'>"):
        # extract the enum name between ''
        first_quote = type_class_name.index("'")
        second_quote = type_class_name.index("'", first_quote + 1)
        return True, type_class_name[first_quote + 1 : second_quote]
    try:
        type_class = eval(type_class_name, scope_storage.globals_, scope_storage.locals_)
        if issubclass(type_class, Enum):
            return True, type_class_name
    except (NameError, AttributeError, SyntaxError, TypeError):
        # We might end up here if the type is not an enum at all and thus we do not warn
        pass
        # logging.debug(f"_extract_enum_typeclass: failed to evaluate {type_class_name}")
    return False, type_class_name


def _extract_list_typeclass(type_class_name: str) -> Tuple[bool, str]:
    if type_class_name.startswith("typing.List[") and type_class_name.endswith("]"):
        return True, type_class_name[12:-1]
    elif type_class_name.startswith("List[") and type_class_name.endswith("]"):
        return True, type_class_name[5:-1]
    elif type_class_name.startswith("list[") and type_class_name.endswith("]"):
        return True, type_class_name[5:-1]
    return False, type_class_name


def _parse_typeclasses_list(type_class_name: str) -> List[str]:
    """
    Parse a string representing a list of type classes.
    :param type_class_name:
    :return: a list of type classes

    Is able to parse the following formats:
        int, float, str               -> ['int', 'float', 'str']
        int, numpy.ndarray[typing.Any, numpy.dtype[numpy.uint8]]    -> ['int', 'numpy.ndarray[typing.Any, numpy.dtype[numpy.uint8]]']
    """
    type_classes = []
    current_type_class = ""
    current_brackets = 0
    for c in type_class_name:
        if c == "," and current_brackets == 0:
            type_classes.append(current_type_class.strip())
            current_type_class = ""
        else:
            current_type_class += c
            if c == "[":
                current_brackets += 1
            elif c == "]":
                current_brackets -= 1
    type_classes.append(current_type_class.strip())
    return type_classes


def _extract_tuple_typeclasses(type_class_name: str) -> Tuple[bool, List[str]]:
    possible_tuple_names = ["typing.Tuple[", "Tuple[", "tuple["]
    for tuple_name in possible_tuple_names:
        if type_class_name.startswith(tuple_name) and type_class_name.endswith("]"):
            inner_type_str = type_class_name[len(tuple_name) : -1]
            inner_type_strs = _parse_typeclasses_list(inner_type_str)
            return True, inner_type_strs
    return False, []


def _any_type_class_name_to_gui(
    type_class_name: str, scope_storage: ScopeStorage, custom_attributes: CustomAttributesDict
) -> AnyDataWithGui[Any]:
    global _TO_GUI_CONTEXT
    _TO_GUI_CONTEXT.enqueue_typename(type_class_name)

    # logging.warning(f"any_typeclass_to_gui: {type_class_name}")
    if gui_factories().can_handle_typename(type_class_name):
        return gui_factories().factor(type_class_name, custom_attributes)

    # Remove the "<class '" and "'>", and retry
    # (this is suspicious)
    if type_class_name.startswith("<class '") and type_class_name.endswith("'>"):
        type_class_name = type_class_name[8:-2]
        if gui_factories().can_handle_typename(type_class_name):
            return gui_factories().factor(type_class_name, custom_attributes)

    is_optional, optional_inner_type_class_name = _extract_optional_typeclass(type_class_name)
    is_enum, enum_type_class_name = _extract_enum_typeclass(type_class_name, scope_storage)
    is_list, list_inner_type_class_name = _extract_list_typeclass(type_class_name)

    if is_enum:
        try:
            if gui_factories().can_handle_typename(enum_type_class_name):
                return gui_factories().factor(enum_type_class_name, custom_attributes)
            else:
                # If you get an error here (NameError: name 'MyEnum' is not defined),
                # you need to pass the globals and locals
                enum_class = eval(enum_type_class_name, scope_storage.globals_, scope_storage.locals_)
            r = EnumWithGui(enum_class)
            return r
        except NameError:
            logging.warning(f"Enum {type_class_name}: enum not found in globals and locals")
            return AnyDataWithGui.make_for_any()

    if is_optional:
        inner_gui = _any_type_class_name_to_gui(
            optional_inner_type_class_name, scope_storage=scope_storage, custom_attributes=custom_attributes
        )
        return OptionalWithGui(inner_gui)
    elif is_list:
        inner_gui = _any_type_class_name_to_gui(
            list_inner_type_class_name, scope_storage=scope_storage, custom_attributes=custom_attributes
        )
        return ListWithGui(inner_gui)

    # if we reach this point, we have no GUI implementation for the type
    _TO_GUI_CONTEXT.add_missing_gui_factory(type_class_name)
    return AnyDataWithGui.make_for_any()


def _fn_outputs_with_gui(
    type_class_name: str, scope_storage: ScopeStorage, fn_custom_attributes: CustomAttributesDict
) -> List[AnyDataWithGui[Any]]:
    r = []
    is_tuple, inner_type_classes = _extract_tuple_typeclasses(type_class_name)
    if is_tuple:
        for idx_output, inner_type_class in enumerate(inner_type_classes):
            output_custom_attrs = get_output_custom_attributes(fn_custom_attributes, idx_output)
            r.append(
                _any_type_class_name_to_gui(
                    inner_type_class, scope_storage=scope_storage, custom_attributes=output_custom_attrs
                )
            )
    else:
        output_custom_attrs = get_output_custom_attributes(fn_custom_attributes)
        r.append(
            _any_type_class_name_to_gui(
                type_class_name, scope_storage=scope_storage, custom_attributes=output_custom_attrs
            )
        )
    return r


def to_type_with_gui(
    type_: DataType, scope_storage: ScopeStorage, custom_attributes: CustomAttributesDict
) -> AnyDataWithGui[DataType]:
    typename = str(type_)
    r = _any_type_class_name_to_gui(typename, scope_storage, custom_attributes)
    return r


def to_data_with_gui(
    value: DataType,
    scope_storage: ScopeStorage,
    custom_attributes: CustomAttributesDict,
) -> AnyDataWithGui[DataType]:
    type_class_name = str(type(value))
    r = _any_type_class_name_to_gui(type_class_name, scope_storage, custom_attributes)
    r.value = value
    return r


def _to_param_with_gui(
    name: str, param: inspect.Parameter, scope_storage: ScopeStorage, custom_attributes: CustomAttributesDict
) -> ParamWithGui[Any]:
    annotation = param.annotation

    data_with_gui: AnyDataWithGui[Any]
    if annotation is None or annotation is inspect.Parameter.empty:
        data_with_gui = AnyDataWithGui.make_for_any()
    else:
        data_with_gui = _any_type_class_name_to_gui(str(annotation), scope_storage, custom_attributes)

    param_kind = ParamKind.PositionalOrKeyword
    if param.kind is inspect.Parameter.POSITIONAL_ONLY:
        param_kind = ParamKind.PositionalOnly
    elif param.kind is inspect.Parameter.KEYWORD_ONLY:
        param_kind = ParamKind.KeywordOnly

    default_value = param.default if param.default is not inspect.Parameter.empty else UnspecifiedValue
    r = ParamWithGui(name, data_with_gui, param_kind, default_value)

    return r


def _capture_scope(nb_steps_back: int = 0) -> ScopeStorage:
    """Advanced: when a function is added, capture the locals and globals of the caller.

    This is required to be able to "eval" the types in the function signature
    (if they were defined locally at the caller scope)

    Since this method is private, we need to go up the call stack twice to get the caller's locals and globals
    :return:
    """
    import inspect
    import copy

    nb_steps_back += 1  # 1 for this function

    stack = inspect.stack()
    assert len(stack) >= nb_steps_back
    caller_frame = stack[nb_steps_back]
    globals_ = copy.copy(caller_frame.frame.f_globals)
    locals_ = copy.copy(caller_frame.frame.f_locals)
    return ScopeStorage(globals_, locals_)


def capture_current_scope() -> ScopeStorage:
    return _capture_scope(0 + 1)  # 0 for the caller, 1 for this function


def _capture_scope_back_1() -> ScopeStorage:
    return _capture_scope(1 + 1)  # 1 for the caller, 1 for this function (capture_scope_back_2


def _get_calling_module_name() -> str:
    """Get the name of the module where the function is called from.
    This is useful to register the types in the correct module.
    This function is private to this module
    """
    stack = inspect.stack()
    assert len(stack) >= 3
    # stack[0] is the current frame (here)
    # stack[1] is the caller frame (a function in this module)
    # stack[2] is the original caller frame (the module where the function is called from)
    caller_frame = stack[2]

    # 'frame' is a Frame object, and from it, you can access the module object
    module = inspect.getmodule(caller_frame[0])
    if module:
        return module.__name__
    else:
        raise ValueError("No module found")


def _get_input_param_custom_attributes(fn_attributes: JsonDict, param_name: str) -> JsonDict:
    # Get the optional custom attributes for the parameter. For example:
    #     def f(x: float):
    #         return x
    #
    #    f.x__range = (0, 1)
    #    f.x__type = "slider"
    #
    # Or
    #    @fl.with_custom_attrs(x__range=(0, 1), x__type="slider")
    #    def f(x: float):
    #        return x
    #
    r = {}
    for k, v in fn_attributes.items():
        if k.startswith(param_name + "__"):
            r[k[len(param_name) + 2 :]] = v
    return r


def get_output_custom_attributes(fn_attributes: JsonDict, idx_output: int = 0) -> JsonDict:
    # Get the optional custom attributes for the return value. For example:
    #     @with_custom_attrs(return__range=(0, 1))
    #     def f() -> float:
    #         return 1.0
    r = {}

    if idx_output == 0:
        prefix = "return__"
    else:
        prefix = f"return_{idx_output}__"
    prefix_len = len(prefix)

    for k, v in fn_attributes.items():
        if k.startswith(prefix):
            r[k[prefix_len:]] = v
    return r


def _add_input_outputs_to_function_with_gui_globals_locals_captured(
    function_with_gui: FunctionWithGui,
    scope_storage: ScopeStorage,
    signature_string: str | None,
    custom_attributes: CustomAttributesDict,
) -> None:
    _TO_GUI_CONTEXT.enqueue_function(function_with_gui.name)
    f = function_with_gui._f_impl  # noqa
    assert f is not None
    try:
        sig = get_function_signature(f, signature_string=signature_string)
    except ValueError as e:
        raise ValueError(f"Failed to get the signature of the function {f.__name__}") from e

    params = sig.parameters
    for name, param in params.items():
        param_custom_attrs = _get_input_param_custom_attributes(custom_attributes, name)
        function_with_gui._inputs_with_gui.append(_to_param_with_gui(name, param, scope_storage, param_custom_attrs))

    return_annotation = sig.return_annotation
    if return_annotation is inspect.Parameter.empty:
        output_with_gui = AnyDataWithGui.make_for_any()
        output_with_gui.merge_custom_attrs(get_output_custom_attributes(custom_attributes))
        function_with_gui._outputs_with_gui.append(OutputWithGui(output_with_gui))
    else:
        return_annotation_str = str(return_annotation)
        if return_annotation_str != "None":
            outputs_with_guis = _fn_outputs_with_gui(return_annotation_str, scope_storage, custom_attributes)
            for i, output_with_gui in enumerate(outputs_with_guis):
                function_with_gui._outputs_with_gui.append(OutputWithGui(output_with_gui))


# ----------------------------------------------------------------------------------------------------------------------
#       all to gui
# ----------------------------------------------------------------------------------------------------------------------
Typename: TypeAlias = str
FnTypenameMatcher = Callable[[Typename], bool]


def _make_union_matcher(typenames_prefix: str) -> FnTypenameMatcher:
    """Create a matcher for union of types whose name start with the given prefix."""

    # e.g. for typenames_prefix="fiatlight.fiat_kits.fiat_image.image_types.Image" the matcher will match types like
    #     typing.Union[fiatlight.fiat_kits.fiat_image.image_types.ImageU8_1, fiatlight.fiat_kits.fiat_image.image_types.ImageU8_2, ...]
    def union_matcher(typename: str) -> bool:
        if not typename.startswith("typing.Union[") or not typename.endswith("]"):
            return False
        nb_open_brackets = typename.count("[")
        nb_close_brackets = typename.count("]")
        if nb_open_brackets != 1 or nb_close_brackets != 1:
            return False
        # Extract the inner type
        inner_type = typename[len("typing.Union[") : -1]
        inner_types = inner_type.split(", ")
        are_all_inner_types_image_types = all([t.startswith(typenames_prefix) for t in inner_types])
        return are_all_inner_types_image_types

    return union_matcher


class GuiFactories:
    @dataclass
    class _GuiFactoryWithMatcher:
        fn_matcher: FnTypenameMatcher
        gui_factory: GuiFactory[Any]

    _factories: List[_GuiFactoryWithMatcher]

    def __init__(self) -> None:
        self._factories = []

    def can_handle_typename(self, typename: Typename) -> bool:
        for matcher in self._factories:
            if matcher.fn_matcher(typename):
                return True
        return False

    def get_factory(self, typename: Typename) -> GuiFactory[Any]:
        # We reverse the list to give priority to the last registered factories
        for factory in reversed(self._factories):
            if factory.fn_matcher(typename):
                return factory.gui_factory
        raise ValueError(f"No factory found for typename {typename}")

    def register_type(self, type_: Type[Any], factory: GuiFactory[Any]) -> None:
        full_typename = str(type_)
        full_typename_no_class = ""
        if full_typename.startswith("<class '") and full_typename.endswith("'>"):
            full_typename_no_class = full_typename[8:-2]

        def matcher_function(tested_typename: Typename) -> bool:
            return full_typename == tested_typename or full_typename_no_class == tested_typename

        debug = False
        if debug:
            msg = f"register_type: {full_typename}"
            if len(full_typename_no_class) > 0:
                msg += f" (no class: {full_typename_no_class})"
            logging.debug(msg)
        self.register_matcher_factory(matcher_function, factory)

    def register_factory_name_start_with(self, typename_prefix: Typename, factory: GuiFactory[Any]) -> None:
        def matcher_function(tested_typename: Typename) -> bool:
            return tested_typename.startswith(typename_prefix)

        self._factories.append(self._GuiFactoryWithMatcher(matcher_function, factory))

    def register_factory_union(self, typename_prefix: Typename, factory: GuiFactory[Any]) -> None:
        self.register_matcher_factory(_make_union_matcher(typename_prefix), factory)

    def register_matcher_factory(self, matcher: FnTypenameMatcher, factory: GuiFactory[Any]) -> None:
        self._factories.append(self._GuiFactoryWithMatcher(matcher, factory))

    def register_enum(self, enum_class: type[Enum]) -> None:
        def enum_gui_factory() -> EnumWithGui:
            return EnumWithGui(enum_class)

        self.register_type(enum_class, enum_gui_factory)

    def register_bound_float(self, type_: Type[Any], interval: FloatInterval) -> None:
        def factory() -> primitives_gui.FloatWithGui:
            r = primitives_gui.FloatWithGui()
            r.params.edit_type = primitives_gui.FloatEditType.slider
            r.params.v_min = interval[0]
            r.params.v_max = interval[1]
            return r

        self.register_type(type_, factory)

    def register_bound_int(self, type_: Type[Any], interval: IntInterval) -> None:
        def factory() -> primitives_gui.IntWithGui:
            r = primitives_gui.IntWithGui()
            r.params.edit_type = primitives_gui.IntEditType.slider
            r.params.v_min = interval[0]
            r.params.v_max = interval[1]
            return r

        self.register_type(type_, factory)

    def factor(self, typename: Typename, custom_attributes: CustomAttributesDict) -> AnyDataWithGui[Any]:
        r = self.get_factory(typename)()
        r.merge_custom_attrs(custom_attributes)
        return r


_GUI_FACTORIES = GuiFactories()


def gui_factories() -> GuiFactories:
    return _GUI_FACTORIES


def register_type(type_: Type[Any], factory: GuiFactory[Any]) -> None:
    gui_factories().register_type(type_, factory)


def register_enum(enum_class: type[Enum]) -> None:
    """Register an enum with its GUI implementation.
    Note: you can also use the enum_with_registration decorator."""
    gui_factories().register_enum(enum_class)


def enum_with_gui_registration(cls: Type[Enum]) -> Type[Enum]:
    register_enum(cls)
    return cls


def register_dataclass(dataclass_type: Type[DataclassLikeType], **kwargs) -> None:  # type: ignore
    """Register a dataclass with its GUI implementation.
    Note: you can also use the dataclass_with_gui_registration decorator."""
    from fiatlight.fiat_togui.dataclass_gui import DataclassGui

    def factory() -> AnyDataWithGui[Any]:
        r = DataclassGui(dataclass_type, kwargs)
        return r

    gui_factories().register_type(dataclass_type, factory)


# Decorators for registered dataclasses and pydantic models
def dataclass_with_gui_registration(**kwargs) -> Callable[[Type[DataType]], Type[DataType]]:  # type: ignore
    def actual_decorator(cls: Type[DataType]) -> Type[DataType]:
        cls = dataclasses.dataclass(cls)  # First, create the dataclass
        register_dataclass(cls, **kwargs)
        return cls

    return actual_decorator


def register_base_model(base_model_type: Type[DataclassLikeType], **kwargs) -> None:  # type: ignore
    """Register a pydantic BaseModel with its GUI implementation.
    Note: you can also use the base_model_with_gui_registration decorator."""
    from fiatlight.fiat_togui.dataclass_gui import BaseModelGui

    assert issubclass(base_model_type, pydantic.BaseModel)

    def factory() -> AnyDataWithGui[Any]:
        r = BaseModelGui(base_model_type, kwargs)
        return r

    gui_factories().register_type(base_model_type, factory)


def base_model_with_gui_registration(**kwargs) -> Callable[[Type[pydantic.BaseModel]], Type[pydantic.BaseModel]]:  # type: ignore
    def actual_decorator(cls: Type[pydantic.BaseModel]) -> Type[pydantic.BaseModel]:
        register_base_model(cls, **kwargs)
        return cls

    return actual_decorator


def register_bound_float(type_: Type[Any], interval: FloatInterval) -> None:
    gui_factories().register_bound_float(type_, interval)


def register_bound_int(type_: Type[Any], interval: IntInterval) -> None:
    gui_factories().register_bound_int(type_, interval)


# ----------------------------------------------------------------------------------------------------------------------
#       register primitive types
# ----------------------------------------------------------------------------------------------------------------------
def _register_base_types() -> None:
    from fiatlight.fiat_types import fiat_number_types
    from fiatlight.fiat_togui import primitives_gui

    fiat_number_types._register_bound_numbers()
    primitives_gui._register_all_primitive_types()


_register_base_types()
