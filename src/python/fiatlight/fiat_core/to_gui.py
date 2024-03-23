from fiatlight.fiat_types import UnspecifiedValue, DataType, GlobalsDict, LocalsDict
from fiatlight.fiat_core import primitives_gui
from fiatlight.fiat_core.any_data_with_gui import AnyDataWithGui
from fiatlight.fiat_core.function_with_gui import FunctionWithGui, ParamKind, ParamWithGui, OutputWithGui
from fiatlight.fiat_core.composite_gui import OptionalWithGui, EnumWithGui, ListWithGui
from fiatlight.fiat_core.function_signature import get_function_signature
from enum import Enum

import inspect
import logging
from typing import TypeAlias, Callable, Any, Dict, Tuple, List


GuiFactory = Callable[[], AnyDataWithGui[DataType]]


_COMPLAINTS_MISSING_GUI_FACTORY = []


def _extract_optional_typeclass(type_class_name: str) -> Tuple[bool, str]:
    if type_class_name.startswith("typing.Optional[") and type_class_name.endswith("]"):
        return True, type_class_name[16:-1]
    if type_class_name.endswith(" | None"):
        return True, type_class_name[:-7]
    return False, type_class_name


def _extract_enum_typeclass(
    type_class_name: str, globals_dict: GlobalsDict | None, locals_dict: LocalsDict | None
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
    except (NameError, AttributeError, SyntaxError):
        logging.debug(f"_extract_enum_typeclass: failed to evaluate {type_class_name}")
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


def any_typeclass_to_gui(
    type_class_name: str, *, globals_dict: GlobalsDict | None = None, locals_dict: LocalsDict | None = None
) -> AnyDataWithGui[Any]:
    if type_class_name.startswith("<class '") and type_class_name.endswith("'>"):
        type_class_name = type_class_name[8:-2]

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
            return AnyDataWithGui.make_default()

    if is_optional:
        inner_gui = any_typeclass_to_gui(type_class_name, globals_dict=globals_dict, locals_dict=locals_dict)
        return OptionalWithGui(inner_gui)
    elif is_list:
        inner_gui = any_typeclass_to_gui(type_class_name, globals_dict=globals_dict, locals_dict=locals_dict)
        return ListWithGui(inner_gui)

    if gui_factories().can_handle_typename(type_class_name):
        return gui_factories().factor(type_class_name)

    # if we reach this point, we have no GUI implementation for the type
    if type_class_name not in _COMPLAINTS_MISSING_GUI_FACTORY:
        logging.warning(f"Type {type_class_name} not present in ALL_GUI_FACTORIES")
        _COMPLAINTS_MISSING_GUI_FACTORY.append(type_class_name)
    return AnyDataWithGui.make_default()


def any_typeclass_to_gui_split_if_tuple(
    type_class_name: str, *, globals_dict: GlobalsDict | None = None, locals_dict: LocalsDict | None = None
) -> List[AnyDataWithGui[Any]]:
    r = []
    is_tuple, inner_type_classes = _extract_tuple_typeclasses(type_class_name)
    if is_tuple:
        for inner_type_class in inner_type_classes:
            r.append(any_typeclass_to_gui(inner_type_class, globals_dict=globals_dict, locals_dict=locals_dict))
    else:
        r.append(any_typeclass_to_gui(type_class_name, globals_dict=globals_dict, locals_dict=locals_dict))
    return r


def to_data_with_gui(value: DataType) -> AnyDataWithGui[DataType]:
    type_class_name = str(type(value))
    r = any_typeclass_to_gui(type_class_name)
    r.value = value
    return r


def to_param_with_gui(
    name: str,
    param: inspect.Parameter,
    *,
    globals_dict: GlobalsDict | None = None,
    locals_dict: LocalsDict | None = None,
) -> ParamWithGui[Any]:
    annotation = param.annotation

    data_with_gui: AnyDataWithGui[Any]
    if annotation is None or annotation is inspect.Parameter.empty:
        data_with_gui = AnyDataWithGui.make_default()
    else:
        data_with_gui = any_typeclass_to_gui(str(annotation), globals_dict=globals_dict, locals_dict=locals_dict)

    param_kind = ParamKind.PositionalOrKeyword
    if param.kind is inspect.Parameter.POSITIONAL_ONLY:
        param_kind = ParamKind.PositionalOnly
    elif param.kind is inspect.Parameter.KEYWORD_ONLY:
        param_kind = ParamKind.KeywordOnly

    default_value = param.default if param.default is not inspect.Parameter.empty else UnspecifiedValue
    return ParamWithGui(name, data_with_gui, param_kind, default_value)


def to_function_with_gui(
    f: Callable[..., Any],
    *,
    globals_dict: GlobalsDict | None = None,
    locals_dict: LocalsDict | None = None,
    signature_string: str | None = None,
) -> FunctionWithGui:
    """Create a FunctionWithGui from a function.

    :param f: the function for which we want to create a FunctionWithGui
    :param globals_dict: the globals dictionary of the module where the function is defined
    :param locals_dict: the locals dictionary of the module where the function is defined
    :param signature_string: a string representing the signature of the function
    :return: a FunctionWithGui instance that wraps the function.
    """
    function_with_gui = FunctionWithGui()
    function_with_gui.name = f.__name__
    function_with_gui.f_impl = f

    try:
        sig = get_function_signature(f, signature_string=signature_string)
    except ValueError as e:
        raise ValueError(f"Failed to get the signature of the function {f.__name__}") from e

    params = sig.parameters
    for name, param in params.items():
        function_with_gui.inputs_with_gui.append(
            to_param_with_gui(name, param, globals_dict=globals_dict, locals_dict=locals_dict)
        )

    return_annotation = sig.return_annotation
    if return_annotation is inspect.Parameter.empty:
        output_with_gui = AnyDataWithGui.make_default()
        function_with_gui.outputs_with_gui.append(OutputWithGui(output_with_gui))
    else:
        return_annotation_str = str(return_annotation)
        outputs_with_guis = any_typeclass_to_gui_split_if_tuple(return_annotation_str)
        for output_with_gui in outputs_with_guis:
            function_with_gui.outputs_with_gui.append(OutputWithGui(output_with_gui))

    return function_with_gui


# ----------------------------------------------------------------------------------------------------------------------
#       all to gui
# ----------------------------------------------------------------------------------------------------------------------
Typename: TypeAlias = str


class GuiFactories:
    _factories: Dict[Typename, GuiFactory[Any]]

    def __init__(self) -> None:
        self._factories = {
            "int": primitives_gui.IntWithGui,
            "float": primitives_gui.FloatWithGui,
            "str": primitives_gui.StrWithGui,
            "bool": primitives_gui.BoolWithGui,
            "FilePath": primitives_gui.FilePathWithGui,
            "TextPath": primitives_gui.TextPathWithGui,
            "fiatlight.fiat_types.str_types.ImagePath": primitives_gui.ImagePathWithGui,
        }

    def can_handle_typename(self, typename: Typename) -> bool:
        return typename in self._factories

    def get_factory(self, typename: Typename) -> GuiFactory[Any]:
        if typename not in self._factories:
            raise ValueError(f"Unknown typename {typename}")
        return self._factories[typename]

    def add_factory(self, typename: Typename, factory: GuiFactory[Any]) -> None:
        self._factories[typename] = factory

    def factor(self, typename: Typename) -> AnyDataWithGui[Any]:
        return self.get_factory(typename)()


_GUI_FACTORIES = GuiFactories()


def gui_factories() -> GuiFactories:
    return _GUI_FACTORIES
