import dataclasses
from dataclasses import dataclass
from types import NoneType

import pydantic

from fiatlight.fiat_types import UnspecifiedValue, DataType, CustomAttributesDict
from fiatlight.fiat_types.base_types import JsonDict
from fiatlight.fiat_togui import primitives_gui
from fiatlight.fiat_core.any_data_with_gui import AnyDataWithGui, AnyDataWithGui_UnregisteredType
from fiatlight.fiat_core.param_with_gui import ParamKind, ParamWithGui
from fiatlight.fiat_core.function_with_gui import FunctionWithGui
from fiatlight.fiat_core.output_with_gui import OutputWithGui
from fiatlight.fiat_togui.composite_gui import OptionalWithGui, EnumWithGui, ListWithGui
from fiatlight.fiat_togui.function_signature import get_function_signature
from fiatlight.fiat_types.fiat_number_types import FloatInterval, IntInterval
from fiatlight.fiat_utils import docstring_first_line
from .dataclass_gui import DataclassLikeType
from enum import Enum

import inspect
import logging
from typing import TypeAlias, Callable, Any, Tuple, List, Type, Generic

GuiFactory = Callable[[], AnyDataWithGui[DataType]]
FunctionWithGuiFactory = Callable[[], FunctionWithGui]

_ErrorMessage = str


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


def fully_qualified_typename(type_: Type[Any]) -> str:
    """Returns the fully qualified name of a type.
    For example:
        fiatlight.fiat_kits.fiat_image.lut_functions.LutParams
    """
    assert isinstance(type_, type)
    full_typename = f"{type_.__module__}.{type_.__qualname__}"
    if full_typename.startswith("builtins."):
        full_typename = full_typename[len("builtins.") :]
    return full_typename


def fully_qualified_complex_typename(type_: DataType) -> str:
    """Returns the fully qualified name of a complex type (tuple, list, NewType, etc.)"""
    assert not isinstance(type_, type)
    return str(type_)


def fully_qualified_typename_or_str(type_: DataType) -> str:
    """Returns the fully qualified name of a type,
    or the string representation of a complex type (tuple, list, NewType, etc.)"""
    if isinstance(type_, type):
        return fully_qualified_typename(type_)
    else:
        return fully_qualified_complex_typename(type_)


def fully_qualified_annotation(annotation: Any) -> str:
    """Returns the fully qualified name of an annotation, when possible"""
    annotation_str = str(annotation)
    uses_inner_type = "[" in annotation_str
    if hasattr(annotation, "__module__") and hasattr(annotation, "__qualname__") and not uses_inner_type:
        r = f"{annotation.__module__}.{annotation.__qualname__}"
        if r.startswith("builtins."):
            r = r[len("builtins.") :]
        return r
    else:
        return str(annotation)


def _extract_union_list(type_class_name: str) -> List[str]:
    """Extract the list of types in a Union type."""
    if type_class_name.startswith("typing.Union[") and type_class_name.endswith("]"):
        inner_type_str = type_class_name[len("typing.Union[") : -1]
        # inner_type_strs = _parse_typeclasses_list(inner_type_str)
        inner_type_strs = inner_type_str.split(", ")
        return inner_type_strs
    return []


def _extract_optional_typeclass(type_class_name: str) -> Tuple[bool, str]:
    """Extract the inner type of an Optional type."""
    if type_class_name.startswith("typing.Optional[") and type_class_name.endswith("]"):
        return True, type_class_name[16:-1]
    if type_class_name.endswith(" | None"):
        return True, type_class_name[:-7]

    # If the type is a union of multiple types, and one of them is NoneType, we can convert it to Optional
    union_list = _extract_union_list(type_class_name)
    if len(union_list) >= 2 and "NoneType" in union_list:
        union_list.remove("NoneType")
        union_str = ", ".join(union_list)
        new_union_type = f"typing.Union[{union_str}]"
        return True, new_union_type

    return False, type_class_name


def _extract_enum_typeclass(type_class_name: str) -> Tuple[bool, str]:
    """Extract the name of an enum type. Probably not useful anymore, since enum are registered manually."""
    # An enum type will be displayed as
    #     <enum 'EnumName'>
    # or
    #     <enum 'EnumName' of 'module_name'>
    if type_class_name.startswith("<enum '") and type_class_name.endswith("'>"):
        # extract the enum name between ''
        first_quote = type_class_name.index("'")
        second_quote = type_class_name.index("'", first_quote + 1)
        return True, type_class_name[first_quote + 1 : second_quote]
    else:
        return False, type_class_name


def _extract_list_typeclass(type_class_name: str) -> Tuple[bool, str]:
    """Extract the inner type of a List type."""
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
    """Extract the inner types of a Tuple type."""
    possible_tuple_names = ["typing.Tuple[", "Tuple[", "tuple["]
    for tuple_name in possible_tuple_names:
        if type_class_name.startswith(tuple_name) and type_class_name.endswith("]"):
            inner_type_str = type_class_name[len(tuple_name) : -1]
            inner_type_strs = _parse_typeclasses_list(inner_type_str)
            return True, inner_type_strs
    return False, []


def _any_typename_to_gui(typename: str, custom_attributes: CustomAttributesDict) -> AnyDataWithGui[Any]:
    """Central function to convert a type name to a GUI representation.
    It handles simple types, enum, optional, list, tuple, etc.
    """

    # Note: typename can be a string like "int", "float", "str", "typing.List[int]", "typing.Optional[int]", etc.
    # i.e. it can be a type name, or a composite type name (which is not really a type for Python runtime)
    global _TO_GUI_CONTEXT
    _TO_GUI_CONTEXT.enqueue_typename(typename)

    # logging.warning(f"any_typeclass_to_gui: {typename}")
    if gui_factories().can_handle_typename(typename):
        return gui_factories().factor(typename, custom_attributes)

    # Remove the "<class '" and "'>", and retry
    # (this is suspicious, but we sometimes receive type names like "<class 'int'>")
    if typename.startswith("<class '") and typename.endswith("'>"):
        type_class_name = typename[8:-2]
        if gui_factories().can_handle_typename(type_class_name):
            return gui_factories().factor(type_class_name, custom_attributes)

    is_optional, optional_inner_type_class_name = _extract_optional_typeclass(typename)
    is_enum, enum_type_class_name = _extract_enum_typeclass(typename)
    is_list, list_inner_type_class_name = _extract_list_typeclass(typename)

    if is_enum:
        if gui_factories().can_handle_typename(enum_type_class_name):
            return gui_factories().factor(enum_type_class_name, custom_attributes)
        else:
            logging.warning(f"Enum {typename}: enum not found in globals and locals")
            return AnyDataWithGui_UnregisteredType(enum_type_class_name)

    if is_optional:
        inner_gui = _any_typename_to_gui(optional_inner_type_class_name, custom_attributes=custom_attributes)
        return OptionalWithGui(inner_gui)
    elif is_list:
        inner_gui = _any_typename_to_gui(list_inner_type_class_name, custom_attributes=custom_attributes)
        return ListWithGui(inner_gui)

    # if we reach this point, we have no GUI implementation for the type
    _TO_GUI_CONTEXT.add_missing_gui_factory(typename)
    return AnyDataWithGui_UnregisteredType(typename)


def any_type_to_gui(type_: Type[Any], custom_attributes: CustomAttributesDict) -> AnyDataWithGui[Any]:
    """Converts a type to a GUI representation."""
    typename = fully_qualified_typename(type_)
    return _any_typename_to_gui(typename, custom_attributes)


def any_composed_type_to_gui(type_: DataType, custom_attributes: CustomAttributesDict) -> AnyDataWithGui[Any]:
    """Converts a complex type to a GUI representation.
    By composed we mean a type composed of multiple types like:
        - Optional[int]
        - int | None
        - List[int]
        - Tuple[int, float]
        - Union[int, float]
        - int | float
        etc.
    """
    if isinstance(type_, type):
        raise ValueError("Use any_type_to_gui for simple types")
    composed_typename = fully_qualified_complex_typename(type_)
    r = _any_typename_to_gui(composed_typename, custom_attributes)
    return r


def any_typing_new_type_to_gui(type_: DataType, custom_attributes: CustomAttributesDict) -> AnyDataWithGui[Any]:
    """Converts a type created with typing.NewType to a GUI representation."""
    if isinstance(type_, type):
        raise ValueError("Use any_type_to_gui for simple types")
    composed_typename = fully_qualified_complex_typename(type_)
    r = _any_typename_to_gui(composed_typename, custom_attributes)
    return r


def _add_validate_value_callback(
    custom_attributes: CustomAttributesDict, inout_data_with_gui: AnyDataWithGui[Any]
) -> None:
    """Add a validate_value callback to the inout_data_with_gui, if it is defined in the custom attributes."""
    if "validate_value" in custom_attributes:
        validate_value = custom_attributes["validate_value"]
        if not callable(validate_value):
            raise ValueError("validate_value is not a callable for parameter output")
        inout_data_with_gui.callbacks.validate_value.append(validate_value)


def _fn_outputs_with_gui(type_class_name: str, fn_custom_attributes: CustomAttributesDict) -> List[AnyDataWithGui[Any]]:
    """Convert the return type of a function to a (list of) GUI representation."""
    r = []
    is_tuple, inner_type_classes = _extract_tuple_typeclasses(type_class_name)
    if is_tuple:
        for idx_output, inner_type_class in enumerate(inner_type_classes):
            output_custom_attrs = get_output_custom_attributes(fn_custom_attributes, idx_output)
            output_gui = _any_typename_to_gui(inner_type_class, custom_attributes=output_custom_attrs)
            _add_validate_value_callback(output_custom_attrs, output_gui)
            r.append(output_gui)
    else:
        output_custom_attrs = get_output_custom_attributes(fn_custom_attributes)
        output_gui = _any_typename_to_gui(type_class_name, custom_attributes=output_custom_attrs)
        _add_validate_value_callback(output_custom_attrs, output_gui)
        r.append(output_gui)
    return r


def to_data_with_gui(
    value: DataType,
    custom_attributes: CustomAttributesDict,
) -> AnyDataWithGui[DataType]:
    """Convert a value to a GUI representation."""
    type_class_name = fully_qualified_typename_or_str(type(value))
    r = _any_typename_to_gui(type_class_name, custom_attributes)
    r.value = value
    return r


def _to_param_with_gui(
    name: str, param: inspect.Parameter, custom_attributes: CustomAttributesDict
) -> ParamWithGui[Any]:
    """Convert a function parameter to a GUI representation."""
    annotation = param.annotation

    data_with_gui: AnyDataWithGui[Any]
    if annotation is None or annotation is inspect.Parameter.empty:
        data_with_gui = AnyDataWithGui_UnregisteredType(fully_qualified_annotation(annotation))
    else:
        param_typename = fully_qualified_annotation(annotation)
        data_with_gui = _any_typename_to_gui(param_typename, custom_attributes)

    # add validate_value callback
    _add_validate_value_callback(custom_attributes, data_with_gui)

    param_kind = ParamKind.PositionalOrKeyword
    if param.kind is inspect.Parameter.POSITIONAL_ONLY:
        param_kind = ParamKind.PositionalOnly
    elif param.kind is inspect.Parameter.KEYWORD_ONLY:
        param_kind = ParamKind.KeywordOnly

    default_value = param.default if param.default is not inspect.Parameter.empty else UnspecifiedValue
    r = ParamWithGui(name, data_with_gui, param_kind, default_value)

    return r


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
    """Get the optional custom attributes for the parameter.
    Those parameters are defined in the function attributes, and may be passed:

    * either by manually adding attributes some time after the function definition:
        def f(x: float):
            return x

       f.x__range = (0, 1)
       f.x__type = "slider"

    * or by using the with_custom_attrs decorator:
       @fl.with_custom_attrs(x__range=(0, 1), x__type="slider")
       def f(x: float):
           return x
    """
    r = {}
    for k, v in fn_attributes.items():
        if k.startswith(param_name + "__"):
            r[k[len(param_name) + 2 :]] = v
    return r


def get_output_custom_attributes(fn_attributes: JsonDict, idx_output: int = 0) -> JsonDict:
    """Get the optional custom attributes for the return value.
    For example:
        @with_custom_attrs(return__range=(0, 1))
        def f() -> float:
            return 1.0
    """
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
    signature_string: str | None,
    custom_attributes: CustomAttributesDict,
) -> None:
    """Central function that is called by FunctionWithGui.__init__ to add the inputs and outputs to the function.

    It analyzes the signature of the function, and adds the inputs and outputs to the function_with_gui.
    """

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
        function_with_gui._inputs_with_gui.append(_to_param_with_gui(name, param, param_custom_attrs))

    return_annotation = sig.return_annotation
    if return_annotation is inspect.Parameter.empty:
        output_with_gui = AnyDataWithGui_UnregisteredType("inspect.Parameter.empty")
        output_with_gui.merge_custom_attrs(get_output_custom_attributes(custom_attributes))
        function_with_gui._outputs_with_gui.append(OutputWithGui(output_with_gui))
    else:
        return_annotation_str = fully_qualified_annotation(return_annotation)
        if return_annotation_str != "None":
            outputs_with_guis = _fn_outputs_with_gui(return_annotation_str, custom_attributes)
            for i, numbered_output_with_gui in enumerate(outputs_with_guis):
                function_with_gui._outputs_with_gui.append(OutputWithGui(numbered_output_with_gui))


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


def _lower_case_match(s: str | None, query: str | None) -> bool:
    if query is None:
        return True
    if s is None:
        return False
    return query.lower() in s.lower()


@dataclass
class _GuiFactoryWithMatcher(Generic[DataType]):
    """_GuiFactoryWithMatcher represents the items that are stored by the Gui registry
    It is conceptually a dataclass, but possesses methods that are used
    to display the registry content as a nice table.
    """

    fn_matcher: FnTypenameMatcher
    gui_factory: GuiFactory[Any]
    datatype: Type[DataType]  # might be NoneType for special cases like unions, and typename_prefix
    datatype_explanation: str | None = None

    def sort_key_by_parent_module_then_name(self) -> tuple[str, str]:
        # a sort key (unused at the moment)
        def extract_module_and_name(typename: str) -> Tuple[str, str]:
            parts = typename.rsplit(".", 1)
            if len(parts) == 1:
                return "", parts[0]
            return parts[0], parts[1]

        typename = str(self.datatype)
        parent_module, type_name = extract_module_and_name(typename)
        return (parent_module, type_name)

    def get_datatype_explanation(self) -> str:
        r = self.datatype_explanation
        if r is None:
            if self.datatype in (str, int, float, bool):
                r = ""
            else:
                r = docstring_first_line(self.datatype) or ""
                # Special case for NewType: we want invite the user to add a __doc__ to the NewType
                if r.startswith("NewType creates simple"):  # extract from NewType docstring
                    r = 'NewType(...). Add a docstring to the new type: MyType.__doc__ = "..."'
        return r

    @staticmethod
    def tabulate_info_headers() -> list[str]:
        return [
            "Data Type",
            "Gui Type",
        ]

    def info_cells(self) -> list[str | None]:
        factored_gui = self.gui_factory()

        datatype_str = "None" if self.datatype == NoneType else fully_qualified_typename_or_str(self.datatype)
        try:
            if issubclass(self.datatype, Enum):
                datatype_str = "(Enum) " + datatype_str
            if issubclass(self.datatype, pydantic.BaseModel):
                datatype_str = "(BaseModel) " + datatype_str
            if dataclasses.is_dataclass(self.datatype):
                datatype_str = "(dataclass) " + datatype_str
        except TypeError:
            pass

        datatype_explanation = self.get_datatype_explanation()

        gui_typename = fully_qualified_typename(type(factored_gui))
        gui_explanation = factored_gui.docstring_first_line() or ""

        cell1 = datatype_str
        if len(datatype_explanation) > 0:
            cell1 += "\n  " + datatype_explanation

        cell2 = gui_typename
        if len(gui_explanation) > 0:
            cell2 += "\n  " + gui_explanation

        from fiatlight.fiat_utils.str_utils import text_wrap_preserve_eol

        cell1 = text_wrap_preserve_eol(cell1, 50)
        cell2 = text_wrap_preserve_eol(cell2, 70)

        return [cell1, cell2]

    def matches_query(self, query: str) -> bool:
        factored_gui_typename = type(self.gui_factory()).__name__
        matches_data_typename_query = _lower_case_match(fully_qualified_typename_or_str(self.datatype), query)
        matches_gui_typename_query = _lower_case_match(factored_gui_typename, query)
        matches_explanation_query = _lower_case_match(self.datatype_explanation, query)

        any_match = matches_data_typename_query or matches_gui_typename_query or matches_explanation_query
        return any_match


class GuiFactories:
    """GuiFactories is the registry of all the factories that can convert a type to a GUI representation."""

    _factories: List[_GuiFactoryWithMatcher[Any]]

    def _InitSection(self) -> None:  # dummy method to create a section in the IDE  # noqa
        """
        # ==================================================================================================================
        #                        Construction
        # ==================================================================================================================
        """

    def __init__(self) -> None:
        self._factories = []

    def _InfoSection(self) -> None:  # dummy method to create a section in the IDE  # noqa
        """
        # ==================================================================================================================
        #                        Info about the registry
        # ==================================================================================================================
        """

    def info_factories(self, query: str | None = None) -> str:
        """Returns a nice table listing detailed info about the factories in the registry."""
        if query is None:
            factories = self._factories
        else:
            factories = [f for f in self._factories if f.matches_query(query)]
        if len(factories) == 0:
            return "No factories found"

        # factories = sorted(factories, key=_GuiFactoryWithMatcher.sort_by_parent_module_then_name)

        import tabulate

        headers = _GuiFactoryWithMatcher.tabulate_info_headers()
        cells = [f.info_cells() for f in factories]
        r = tabulate.tabulate(
            cells,
            headers=headers,
            tablefmt="grid",
        )
        return r

    def _cli_search_gui_type(self, typename_gui_or_data: str) -> AnyDataWithGui[Any] | _ErrorMessage:
        matching_guis: List[AnyDataWithGui[Any]] = []

        def add_gui_type(gui_type: AnyDataWithGui[Any]) -> None:
            # check if already present
            for existing_gui_type in matching_guis:
                if type(existing_gui_type) is type(gui_type):
                    return
            matching_guis.append(gui_type)

        # Search for a GUI type
        for factory in self._factories:
            factored_gui = factory.gui_factory()
            if type(factored_gui).__name__ == typename_gui_or_data:
                add_gui_type(factored_gui)

        # Search for a data type
        for factory in self._factories:
            datatype_qualified_name = fully_qualified_typename_or_str(factory.datatype)
            if datatype_qualified_name == typename_gui_or_data:
                add_gui_type(factory.gui_factory())
            else:
                if "." in datatype_qualified_name:
                    datatype_name = datatype_qualified_name.split(".")[-1]
                    if datatype_name == typename_gui_or_data:
                        add_gui_type(factory.gui_factory())

        if len(matching_guis) == 0:
            r = f"This typename ({typename_gui_or_data}) is not handled\n"
            r += "===============================\n"
            r += "List of all GUI types:\n"
            for factory in self._factories:
                factored_gui = factory.gui_factory()
                typename = type(factored_gui).__name__
                r += f"    {typename}\n"
            return r
        elif len(matching_guis) > 1:
            r = "Multiple GUI types found for this typename:\n"
            for gui_type in matching_guis:
                r += f"    {type(gui_type).__name__}\n"
            r += "Please refine your search\n"
            return r
        else:
            return matching_guis[0]

    # def run_gui_demo(self, gui_or_data_typename: str) -> None:
    #     """Returns the info about a GUI type."""
    #
    #     factored_gui = self._cli_search_gui_type(gui_or_data_typename)
    #     if isinstance(factored_gui, _ErrorMessage):
    #         return factored_gui
    #
    #     from fiatlight.fiat_togui.make_gui_demo_code import make_gui_demo_code
    #
    #     code = make_gui_demo_code(factored_gui)
    #     print(code)
    #     exec(code)

    def get_gui_info(self, gui_or_data_typename: str) -> str:
        """Returns the info about a GUI type."""
        from fiatlight.fiat_doc import code_utils

        factored_gui = self._cli_search_gui_type(gui_or_data_typename)
        if isinstance(factored_gui, _ErrorMessage):
            return factored_gui

        doc = factored_gui.__doc__

        r = f"GUI type: {gui_or_data_typename}\n"
        r += "=" * len(r) + "\n"
        if doc is not None:
            r += code_utils.indent_code(doc, 2)
            r += "\n"

        (
            possible_custom_attributes,
            generic_custom_attributes,
        ) = factored_gui.possible_custom_attributes_with_generic()
        if possible_custom_attributes is not None:
            doc_attr = possible_custom_attributes.documentation()
            r += "\n"
            r += code_utils.indent_code(doc_attr, 2)
            r += "\n"

        generic_attr_doc = generic_custom_attributes.documentation()
        r += "\n"
        r += code_utils.indent_code(generic_attr_doc, 2)
        r += "\n"

        from fiatlight.fiat_togui.make_gui_demo_code import make_gui_demo_code

        r += "\n"
        r += "Code to test this GUI type:\n"
        r += "----------------------------\n"
        r += "```python\n"
        r += make_gui_demo_code(factored_gui)
        r += "```\n"
        return r

    def _RegisterFactoriesSection(self) -> None:  # dummy method to create a section in the IDE  # noqa
        """
        # ==================================================================================================================
        #                       Registering factories
        # ==================================================================================================================
        """

    def get_factory(self, typename: Typename) -> GuiFactory[Any]:
        """Returns the factory that can convert a type to a GUI representation."""
        # We reverse the list to give priority to the last registered factories
        for factory in reversed(self._factories):
            if factory.fn_matcher(typename):
                return factory.gui_factory
        raise ValueError(f"No factory found for typename {typename}")

    def register_typing_new_type(self, type_: Any, factory: GuiFactory[Any]) -> None:
        """Registers a factory for a type created with typing.NewType."""
        full_typename = fully_qualified_complex_typename(type_)

        def matcher_function(tested_typename: Typename) -> bool:
            return full_typename == tested_typename

        new_type_doc = type_.__doc__
        if new_type_doc.startswith("NewType creates simple"):
            raise ValueError(
                f"""
            Please add a docstring to the NewType {full_typename}
            Example:
                {full_typename}.__doc__ = "MyType is a synonym for ... (NewType)"
            """
            )
        self.register_matcher_factory(matcher_function, factory, type_, new_type_doc)

    def register_real_type(
        self, type_: Type[Any], factory: GuiFactory[Any], datatype_explanation: str | None = None
    ) -> None:
        """Registers a factory for a type."""
        assert isinstance(type_, type)
        full_typename = fully_qualified_typename(type_)

        def matcher_function(tested_typename: Typename) -> bool:
            return full_typename == tested_typename

        self.register_matcher_factory(matcher_function, factory, type_, datatype_explanation)

    def register_type(
        self, type_: Type[Any], factory: GuiFactory[Any], datatype_explanation: str | None = None
    ) -> None:
        """Registers a factory for a type (real type or NewType)."""
        if isinstance(type_, type):
            full_typename = fully_qualified_typename(type_)
        else:
            full_typename = fully_qualified_complex_typename(type_)

        def matcher_function(tested_typename: Typename) -> bool:
            return full_typename == tested_typename

        self.register_matcher_factory(matcher_function, factory, type_, datatype_explanation)

    def register_factory_name_start_with(self, typename_prefix: Typename, factory: GuiFactory[Any]) -> None:
        """Registers a factory for all types whose name starts with the given prefix."""

        def matcher_function(tested_typename: Typename) -> bool:
            return tested_typename.startswith(typename_prefix)

        self._factories.append(
            _GuiFactoryWithMatcher(
                matcher_function, factory, NoneType, "All types whose name starts with " + typename_prefix
            )
        )

    def register_factory_union(self, typename_prefix: Typename, factory: GuiFactory[Any]) -> None:
        """Registers a factory for a union of types whose name starts with the given prefix."""
        union_matcher = _make_union_matcher(typename_prefix)
        self.register_matcher_factory(
            union_matcher, factory, NoneType, "Union of types whose name starts with " + typename_prefix
        )

    def register_matcher_factory(
        self,
        matcher: FnTypenameMatcher,
        factory: GuiFactory[Any],
        datatype: Type[Any],
        datatype_explanation: str | None = None,
    ) -> None:
        """Registers a factory for a type, with a custom matcher function."""
        self._factories.append(_GuiFactoryWithMatcher(matcher, factory, datatype, datatype_explanation))

    def register_enum(self, enum_class: type[Enum]) -> None:
        """Registers an enum with an autogenerated GUI implementation."""

        def enum_gui_factory() -> EnumWithGui:
            return EnumWithGui(enum_class)

        self.register_real_type(enum_class, enum_gui_factory)

    def register_bound_float(self, type_: Type[Any], interval: FloatInterval) -> None:
        """Registers a float type inside an interval (will use FloatWithGui)"""

        def factory() -> primitives_gui.FloatWithGui:
            r = primitives_gui.FloatWithGui()
            r.params.edit_type = primitives_gui.FloatEditType.slider
            r.params.v_min = interval[0]
            r.params.v_max = interval[1]
            return r

        self.register_typing_new_type(type_, factory)

    def register_bound_int(self, type_: Type[Any], interval: IntInterval) -> None:
        """Registers an int type inside an interval (will use IntWithGui)"""

        def factory() -> primitives_gui.IntWithGui:
            r = primitives_gui.IntWithGui()
            r.params.edit_type = primitives_gui.IntEditType.slider
            r.params.v_min = interval[0]
            r.params.v_max = interval[1]
            return r

        self.register_typing_new_type(type_, factory)

    def _FactoringSection(self) -> None:  # dummy method to create a section in the IDE  # noqa
        """
        # ==================================================================================================================
        #                       Factoring
        # ==================================================================================================================
        """

    def factor(self, typename: Typename, custom_attributes: CustomAttributesDict) -> AnyDataWithGui[Any]:
        """Converts a type name to a GUI representation."""
        r = self.get_factory(typename)()
        r.merge_custom_attrs(custom_attributes)
        return r

    def can_handle_typename(self, typename: Typename) -> bool:
        """Returns True if the registry can handle the given type name."""
        for matcher in self._factories:
            if matcher.fn_matcher(typename):
                return True
        return False


_GUI_FACTORIES = GuiFactories()


def gui_factories() -> GuiFactories:
    """Returns the global registry of factories that can convert a type to a GUI representation."""
    return _GUI_FACTORIES


def register_type(type_: Type[Any], factory: GuiFactory[Any]) -> None:
    """Register a type with its GUI implementation."""
    gui_factories().register_type(type_, factory)


def register_real_type(type_: Type[Any], factory: GuiFactory[Any]) -> None:
    """Register a real type with its GUI implementation."""
    gui_factories().register_real_type(type_, factory)


def register_typing_new_type(type_: Any, factory: GuiFactory[Any]) -> None:
    """Register a type created with typing.NewType with its GUI implementation."""
    gui_factories().register_typing_new_type(type_, factory)


def register_enum(enum_class: type[Enum]) -> None:
    """Register an enum with its GUI implementation.
    Note: you can also use the enum_with_registration decorator."""
    gui_factories().register_enum(enum_class)


def enum_with_gui_registration(cls: Type[Enum]) -> Type[Enum]:
    """Decorator to register an enum with its GUI implementation."""
    register_enum(cls)
    return cls


def register_dataclass(dataclass_type: Type[DataclassLikeType], **kwargs) -> None:  # type: ignore
    """Register a dataclass with its autogenerated GUI implementation.
    Note: you can also use the dataclass_with_gui_registration decorator."""
    from fiatlight.fiat_togui.dataclass_gui import DataclassGui

    def factory() -> AnyDataWithGui[Any]:
        r = DataclassGui(dataclass_type, kwargs)
        return r

    gui_factories().register_real_type(dataclass_type, factory)


# Decorators for registered dataclasses and pydantic models
def dataclass_with_gui_registration(**kwargs) -> Callable[[Type[DataType]], Type[DataType]]:  # type: ignore
    """Decorator to register a dataclass with its autogenerated GUI implementation."""

    def actual_decorator(cls: Type[DataType]) -> Type[DataType]:
        cls = dataclasses.dataclass(cls)  # First, create the dataclass
        register_dataclass(cls, **kwargs)
        return cls

    return actual_decorator


def register_base_model(base_model_type: Type[DataclassLikeType], **kwargs) -> None:  # type: ignore
    """Register a pydantic BaseModel with its autogenerated GUI implementation.
    Note: you can also use the base_model_with_gui_registration decorator."""
    from fiatlight.fiat_togui.dataclass_gui import BaseModelGui

    assert issubclass(base_model_type, pydantic.BaseModel)

    def factory() -> AnyDataWithGui[Any]:
        r = BaseModelGui(base_model_type, kwargs)
        return r

    gui_factories().register_real_type(base_model_type, factory)


def base_model_with_gui_registration(**kwargs) -> Callable[[Type[pydantic.BaseModel]], Type[pydantic.BaseModel]]:  # type: ignore
    """Decorator to register a pydantic BaseModel with its autogenerated GUI implementation."""

    def actual_decorator(cls: Type[pydantic.BaseModel]) -> Type[pydantic.BaseModel]:
        register_base_model(cls, **kwargs)
        return cls

    return actual_decorator


def register_bound_float(type_: Type[Any], interval: FloatInterval) -> None:
    """Registers a float type inside an interval (will use FloatWithGui)"""
    gui_factories().register_bound_float(type_, interval)


def register_bound_int(type_: Type[Any], interval: IntInterval) -> None:
    """Registers an int type inside an interval (will use IntWithGui)"""
    gui_factories().register_bound_int(type_, interval)


# ----------------------------------------------------------------------------------------------------------------------
#       register primitive types
# ----------------------------------------------------------------------------------------------------------------------
def _register_base_types() -> None:
    """Registers the base types (int, float, str, etc.) with their GUI implementations.
    This is called by default when importing this module.
    """
    from fiatlight.fiat_types import fiat_number_types
    from fiatlight.fiat_togui import primitives_gui

    fiat_number_types._register_bound_numbers()
    primitives_gui._register_all_primitive_types()


_register_base_types()
