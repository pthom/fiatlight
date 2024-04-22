from dataclasses import dataclass

from fiatlight.fiat_types import UnspecifiedValue, DataType, GlobalsDict, LocalsDict
from fiatlight.fiat_core import primitives_gui
from fiatlight.fiat_core.any_data_with_gui import AnyDataWithGui
from fiatlight.fiat_core.param_with_gui import ParamKind, ParamWithGui
from fiatlight.fiat_core.function_with_gui import FunctionWithGui
from fiatlight.fiat_core.output_with_gui import OutputWithGui
from fiatlight.fiat_core.composite_gui import OptionalWithGui, EnumWithGui, ListWithGui
from fiatlight.fiat_core.function_signature import get_function_signature
from fiatlight.fiat_types.fiat_number_types import FloatInterval, IntInterval
from enum import Enum

import inspect
import logging
from typing import TypeAlias, Callable, Any, Tuple, List


GuiFactory = Callable[[], AnyDataWithGui[DataType]]
FunctionWithGuiFactory = Callable[[], FunctionWithGui]


_COMPLAINTS_MISSING_GUI_FACTORY = []


def _extract_optional_typeclass(type_class_name: str) -> Tuple[bool, str]:
    if type_class_name.startswith("typing.Optional[") and type_class_name.endswith("]"):
        return True, type_class_name[16:-1]
    if type_class_name.endswith(" | None"):
        return True, type_class_name[:-7]
    return False, type_class_name


def _extract_enum_typeclass(
    type_class_name: str, globals_dict: GlobalsDict, locals_dict: LocalsDict
) -> Tuple[bool, str]:
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
        type_class = eval(type_class_name, globals_dict, locals_dict)
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
    type_class_name: str, *, globals_dict: GlobalsDict, locals_dict: LocalsDict
) -> AnyDataWithGui[Any]:
    # logging.warning(f"any_typeclass_to_gui: {type_class_name}")
    if type_class_name.startswith("<class '") and type_class_name.endswith("'>"):
        type_class_name = type_class_name[8:-2]

    if gui_factories().can_handle_typename(type_class_name):
        return gui_factories().factor(type_class_name)

    is_optional, type_class_name = _extract_optional_typeclass(type_class_name)
    is_enum, type_class_name = _extract_enum_typeclass(type_class_name, globals_dict, locals_dict)
    is_list, type_class_name = _extract_list_typeclass(type_class_name)

    if is_enum:
        try:
            if gui_factories().can_handle_typename(type_class_name):
                return gui_factories().factor(type_class_name)
            elif globals_dict is not None and locals_dict is not None:
                enum_class = eval(type_class_name, globals_dict, locals_dict)
            else:
                # If you get an error here (NameError: name 'MyEnum' is not defined),
                # you need to pass the globals and locals
                enum_class = eval(type_class_name)
            r = EnumWithGui(enum_class)
            return r
        except NameError:
            logging.warning(f"Enum {type_class_name}: enum not found in globals and locals")
            return AnyDataWithGui.make_for_any()

    if is_optional:
        inner_gui = _any_type_class_name_to_gui(type_class_name, globals_dict=globals_dict, locals_dict=locals_dict)
        return OptionalWithGui(inner_gui)
    elif is_list:
        inner_gui = _any_type_class_name_to_gui(type_class_name, globals_dict=globals_dict, locals_dict=locals_dict)
        return ListWithGui(inner_gui)

    # if we reach this point, we have no GUI implementation for the type
    if type_class_name not in _COMPLAINTS_MISSING_GUI_FACTORY:
        logging.warning(f"Type {type_class_name} not registered in gui_factories()")
        _COMPLAINTS_MISSING_GUI_FACTORY.append(type_class_name)
    return AnyDataWithGui.make_for_any()


def _any_typeclass_to_gui_split_if_tuple(
    type_class_name: str, *, globals_dict: GlobalsDict, locals_dict: LocalsDict
) -> List[AnyDataWithGui[Any]]:
    r = []
    is_tuple, inner_type_classes = _extract_tuple_typeclasses(type_class_name)
    if is_tuple:
        for inner_type_class in inner_type_classes:
            r.append(_any_type_class_name_to_gui(inner_type_class, globals_dict=globals_dict, locals_dict=locals_dict))
    else:
        r.append(_any_type_class_name_to_gui(type_class_name, globals_dict=globals_dict, locals_dict=locals_dict))
    return r


def _to_data_with_gui(
    value: DataType,
    *,
    globals_dict: GlobalsDict,
    locals_dict: LocalsDict,
) -> AnyDataWithGui[DataType]:
    type_class_name = str(type(value))
    r = _any_type_class_name_to_gui(type_class_name, globals_dict=globals_dict, locals_dict=locals_dict)
    r.value = value
    return r


def _to_param_with_gui(
    name: str,
    param: inspect.Parameter,
    *,
    globals_dict: GlobalsDict,
    locals_dict: LocalsDict,
) -> ParamWithGui[Any]:
    annotation = param.annotation

    data_with_gui: AnyDataWithGui[Any]
    if annotation is None or annotation is inspect.Parameter.empty:
        data_with_gui = AnyDataWithGui.make_for_any()
    else:
        data_with_gui = _any_type_class_name_to_gui(str(annotation), globals_dict=globals_dict, locals_dict=locals_dict)

    param_kind = ParamKind.PositionalOrKeyword
    if param.kind is inspect.Parameter.POSITIONAL_ONLY:
        param_kind = ParamKind.PositionalOnly
    elif param.kind is inspect.Parameter.KEYWORD_ONLY:
        param_kind = ParamKind.KeywordOnly

    default_value = param.default if param.default is not inspect.Parameter.empty else UnspecifiedValue
    return ParamWithGui(name, data_with_gui, param_kind, default_value)


def _capture_caller_globals_locals() -> tuple[GlobalsDict, LocalsDict]:
    """Advanced: when a function is added, capture the locals and globals of the caller.

    This is required to be able to "eval" the types in the function signature
    (if they were defined locally at the caller scope)

    Since this method is private, we need to go up the call stack twice to get the caller's locals and globals
    :return:
    """
    import inspect

    current_frame = inspect.currentframe()
    if current_frame is None:
        raise ValueError("No current frame")

    # We need to go up the call stack twice to get the caller's locals and globals

    frame_back_1 = current_frame.f_back
    if frame_back_1 is None:
        raise ValueError("No frame back")

    frame_back_2 = frame_back_1.f_back
    if frame_back_2 is None:
        raise ValueError("No frame back")

    # Make sure we don't modify the user namespace
    globals_dict = frame_back_2.f_globals.copy()
    locals_dict = frame_back_2.f_locals.copy()

    return globals_dict, locals_dict


def to_function_with_gui(f: Callable[..., Any], signature_string: str | None = None) -> FunctionWithGui:
    """Create a FunctionWithGui from a function.

    :param f: the function for which we want to create a FunctionWithGui
    :param signature_string: (advanced) a string representing the signature of the function
                             used when the function signature cannot be retrieved automatically
    :return: a FunctionWithGui instance that wraps the function.

    Note: This function will capture the locals and globals of the caller to be able to evaluate the types.
          Make sure to call this function *from the module where the function and its input/output types are defined*
    """
    globals_dict, locals_dict = _capture_caller_globals_locals()
    r = to_function_with_gui_globals_local_captured(
        f, globals_dict=globals_dict, locals_dict=locals_dict, signature_string=signature_string
    )
    return r


def to_function_with_gui_factory(f: Callable[..., Any], signature_string: str | None = None) -> FunctionWithGuiFactory:
    def factory() -> FunctionWithGui:
        return to_function_with_gui(f, signature_string=signature_string)

    return factory


def to_function_with_gui_globals_local_captured(
    f: Callable[..., Any],
    *,
    globals_dict: GlobalsDict,
    locals_dict: LocalsDict,
    signature_string: str | None = None,
) -> FunctionWithGui:
    """Create a FunctionWithGui from a function.

    :param f: the function for which we want to create a FunctionWithGui
    :param globals_dict: the globals dictionary of the module where the function is defined
    :param locals_dict: the locals dictionary of the module where the function is defined
    :param signature_string: (advanced) a string representing the signature of the function
    :return: a FunctionWithGui instance that wraps the function.
    """

    function_with_gui = FunctionWithGui()
    function_with_gui.name = f.__name__
    function_with_gui._f_impl = f

    if hasattr(f, "invoke_automatically"):
        function_with_gui.invoke_automatically = f.invoke_automatically
    if hasattr(f, "invoke_automatically_can_set"):
        function_with_gui.invoke_automatically_can_set = f.invoke_automatically_can_set
    if hasattr(f, "invoke_async"):
        function_with_gui.invoke_async = f.invoke_async

    try:
        sig = get_function_signature(f, signature_string=signature_string)
    except ValueError as e:
        raise ValueError(f"Failed to get the signature of the function {f.__name__}") from e

    params = sig.parameters
    for name, param in params.items():
        function_with_gui._inputs_with_gui.append(
            _to_param_with_gui(name, param, globals_dict=globals_dict, locals_dict=locals_dict)
        )

    return_annotation = sig.return_annotation
    if return_annotation is inspect.Parameter.empty:
        output_with_gui = AnyDataWithGui.make_for_any()
        function_with_gui._outputs_with_gui.append(OutputWithGui(output_with_gui))
    else:
        return_annotation_str = str(return_annotation)
        outputs_with_guis = _any_typeclass_to_gui_split_if_tuple(
            return_annotation_str, globals_dict=globals_dict, locals_dict=locals_dict
        )
        for output_with_gui in outputs_with_guis:
            function_with_gui._outputs_with_gui.append(OutputWithGui(output_with_gui))

    return function_with_gui


# ----------------------------------------------------------------------------------------------------------------------
#       all to gui
# ----------------------------------------------------------------------------------------------------------------------
Typename: TypeAlias = str
FnTypenameMatcher = Callable[[Typename], bool]


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
        for factory in self._factories:
            if factory.fn_matcher(typename):
                return factory.gui_factory
        raise ValueError(f"No factory found for typename {typename}")

    def register_factory(self, typename: Typename, factory: GuiFactory[Any]) -> None:
        def matcher_function(tested_typename: Typename) -> bool:
            return typename == tested_typename

        self._factories.append(self._GuiFactoryWithMatcher(matcher_function, factory))

    def register_matcher_factory(self, matcher: FnTypenameMatcher, factory: GuiFactory[Any]) -> None:
        self._factories.append(self._GuiFactoryWithMatcher(matcher, factory))

    def register_enum(self, enum_class: type[Enum]) -> None:
        enum_class_name = str(enum_class)

        def enum_gui_factory() -> EnumWithGui:
            return EnumWithGui(enum_class)

        self.register_factory(enum_class_name, enum_gui_factory)

    def _get_calling_module_name(self) -> str:
        frame = inspect.currentframe()
        if frame is None:
            raise ValueError("No current frame")
        f_back = frame.f_back
        if f_back is None:
            raise ValueError("No frame back")
        f_back_2 = f_back.f_back
        if f_back_2 is None:
            raise ValueError("No frame back")

        calling_module: str = f_back_2.f_globals["__name__"]
        return calling_module

    def register_bound_float(
        self, interval: FloatInterval, typename: Typename, use_calling_module_name: bool = True
    ) -> None:
        def factory() -> primitives_gui.FloatWithGui:
            r = primitives_gui.FloatWithGui()
            r.params.v_min = interval[0]
            r.params.v_max = interval[1]
            return r

        if use_calling_module_name:
            typename = self._get_calling_module_name() + "." + typename
        self.register_factory(typename, factory)

    def register_bound_int(
        self, interval: IntInterval, typename: Typename, use_calling_module_name: bool = True
    ) -> None:
        def factory() -> primitives_gui.IntWithGui:
            r = primitives_gui.IntWithGui()
            r.params.v_min = interval[0]
            r.params.v_max = interval[1]
            return r

        if use_calling_module_name:
            typename = self._get_calling_module_name() + "." + typename
        self.register_factory(typename, factory)

    def factor(self, typename: Typename) -> AnyDataWithGui[Any]:
        return self.get_factory(typename)()


_GUI_FACTORIES = GuiFactories()


def gui_factories() -> GuiFactories:
    return _GUI_FACTORIES


# ----------------------------------------------------------------------------------------------------------------------
#       register primitive types
# ----------------------------------------------------------------------------------------------------------------------
def _register_base_types() -> None:
    from fiatlight.fiat_types import fiat_number_types
    from fiatlight.fiat_core import primitives_gui

    fiat_number_types._register_bound_numbers()
    primitives_gui._register_all_primitive_types()


_register_base_types()
