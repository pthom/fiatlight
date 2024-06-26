from . import primitives_gui
from .dataclass_like_gui import DataclassLikeType
from fiatlight.fiat_types.base_types import DataType, FiatAttributes
from fiatlight.fiat_types import typename_utils
from fiatlight.fiat_types.fiat_number_types import FloatInterval, IntInterval
from fiatlight.fiat_core.any_data_with_gui import AnyDataWithGui
from fiatlight.fiat_utils import docstring_first_line

from typing import Any, Callable, Generic, List, Tuple, Type, TypeAlias
from enum import Enum
from dataclasses import dataclass
from types import NoneType
import dataclasses
import pydantic

Typename: TypeAlias = str
FnTypenameMatcher = Callable[[Typename], bool]
GuiFactory = Callable[[], AnyDataWithGui[DataType]]

_ErrorMessage = str


def _make_union_matcher(typenames_prefix: str) -> FnTypenameMatcher:
    """Create a matcher for union of types whose name start with the given prefix."""

    # e.g. for typenames_prefix="fiatlight.fiat_kits.fiat_image.image_types.Image" the matcher will match types like
    #     "UNION_UNION-(fiatlight.fiat_kits.fiat_image.image_types.ImageU8_1, fiatlight.fiat_kits.fiat_image.image_types.ImageU8_2, ...)
    def union_matcher(typename: str) -> bool:
        if not typename.startswith("UNION_UNION-(") or not typename.endswith(")"):
            return False
        nb_open_paren = typename.count("(")
        nb_close_paren = typename.count(")")
        if nb_open_paren != 1 or nb_close_paren != 1:
            return False
        # Extract the inner type
        inner_type = typename[len("UNION_UNION-(") : -1]
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
    datatype: Type[Any] | None
    datatype_explanation: str | None = None

    def sort_key_by_parent_module_then_name(self) -> tuple[str, str]:
        # a sort key (unused at the moment)
        def extract_module_and_name(typename_: str) -> Tuple[str, str]:
            parts = typename_.rsplit(".", 1)
            if len(parts) == 1:
                return "", parts[0]
            return parts[0], parts[1]

        typename = str(self.datatype)
        parent_module, type_name = extract_module_and_name(typename)
        return parent_module, type_name

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

        datatype_str = "Unknown" if self.datatype == NoneType else typename_utils.base_typename(self.datatype)
        try:
            if isinstance(self.datatype, type):
                if issubclass(self.datatype, Enum):
                    datatype_str = "(Enum) " + datatype_str
                if issubclass(self.datatype, pydantic.BaseModel):
                    datatype_str = "(BaseModel) " + datatype_str
                if dataclasses.is_dataclass(self.datatype):
                    datatype_str = "(dataclass) " + datatype_str
        except TypeError:
            pass

        datatype_explanation = self.get_datatype_explanation()

        gui_typename = typename_utils.base_typename(type(factored_gui))
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
        matches_data_typename_query = _lower_case_match(typename_utils.fully_qualified_typename(self.datatype), query)
        matches_gui_typename_query = _lower_case_match(factored_gui_typename, query)
        matches_explanation_query = _lower_case_match(self.datatype_explanation, query)

        any_match = matches_data_typename_query or matches_gui_typename_query or matches_explanation_query
        return any_match


class GuiFactories:
    """GuiFactories is the registry of all the factories that can convert a type to a GUI representation."""

    _factories: List[_GuiFactoryWithMatcher[Any]]

    # if _GUI_FACTORIES.can_handle_union_type(union_args):
    # return _GUI_FACTORIES.factor_union_type(union_args, fiat_attributes)

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

        def add_gui_type(gui_type_: AnyDataWithGui[Any]) -> None:
            # check if already present
            for existing_gui_type in matching_guis:
                if type(existing_gui_type) is type(gui_type_):
                    return
            matching_guis.append(gui_type_)

        # Search for a matching GUI type or datatype
        for factory in self._factories:
            factored_gui = factory.gui_factory()
            # print(f"testing {type(factored_gui).__name__} {factored_gui.datatype_basename()}")
            if type(factored_gui).__name__.lower() == typename_gui_or_data.lower():
                add_gui_type(factored_gui)
            elif factored_gui.datatype_basename().lower() == typename_gui_or_data.lower():
                add_gui_type(factored_gui)

        if len(matching_guis) == 1:
            return matching_guis[0]

        error_message = ""
        if len(matching_guis) == 0:
            error_message = f"This typename ({typename_gui_or_data}) is not handled\n"
        elif len(matching_guis) > 1:
            error_message = "Multiple GUI types found for this typename:\n"
            error_message += "Please refine your search\n"

        error_message += "Available GUI types:\n"
        error_message += "=====================\n"
        for gui_type in self._factories:
            factored_gui = gui_type.gui_factory()
            error_message += (
                f"    {factored_gui.datatype_basename()} => {typename_utils.base_typename(type(factored_gui))}\n"
            )
        return error_message

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
            possible_fiat_attributes,
            generic_fiat_attributes,
        ) = factored_gui.possible_fiat_attributes_with_generic()
        if possible_fiat_attributes is not None:
            doc_attr = possible_fiat_attributes.documentation()
            r += "\n"
            r += code_utils.indent_code(doc_attr, 2)
            r += "\n"

        generic_attr_doc = generic_fiat_attributes.documentation()
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
        full_typename = typename_utils.fully_qualified_typename(type_)
        base_typename = typename_utils.base_typename(type_)

        def matcher_function(tested_typename: Typename) -> bool:
            return full_typename == tested_typename

        new_type_doc = type_.__doc__
        if new_type_doc.startswith("NewType creates simple"):
            raise ValueError(
                f"""
            Please add a docstring to the NewType {base_typename}
            Example:
                {base_typename}.__doc__ = "MyType is a synonym for ... (NewType)"
            """
            )
        self.register_matcher_factory(matcher_function, factory, type_, new_type_doc)

    def register_type(self, type_: Type[Any], factory: GuiFactory[Any]) -> None:
        """Registers a factory for a type (real type or NewType)."""
        full_typename = typename_utils.fully_qualified_typename(type_)

        def matcher_function(tested_typename: Typename) -> bool:
            return full_typename == tested_typename

        self.register_matcher_factory(matcher_function, factory, type_)

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

    def _factor(self, typename: Typename, fiat_attributes: FiatAttributes) -> AnyDataWithGui[Any]:
        """Converts a type name to a GUI representation."""
        r = self.get_factory(typename)()
        r.merge_fiat_attributes(fiat_attributes)
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
    """Register a type with its GUI implementation.

    This is the main entry point to associate a type with its GUI representation inside Fiatlight.

    * type_:   can be any type, including NewType, Enum, dataclass, pydantic BaseModel, etc.

    * factory: most of the time simply pass class that inherits from AnyDataWithGui.
      In more complex cases, you can pass a function that returns an instance of AnyDataWithGui.

    """
    gui_factories().register_type(type_, factory)


def register_typing_new_type(type_: Any, factory: GuiFactory[Any]) -> None:
    """Register a type created with typing.NewType with its GUI implementation,
    while making sure it is properly documented.
    """
    gui_factories().register_typing_new_type(type_, factory)


def register_dataclass(dataclass_type: Type[DataclassLikeType], **kwargs) -> None:  # type: ignore
    """Register a dataclass with its autogenerated GUI implementation.
    Note: you can also use the dataclass_with_gui_registration decorator."""
    from fiatlight.fiat_togui.dataclass_gui import DataclassGui

    def factory() -> AnyDataWithGui[Any]:
        r = DataclassGui(dataclass_type, kwargs)
        return r

    gui_factories().register_type(dataclass_type, factory)


# Decorators for registered dataclasses and pydantic models
def dataclass_with_gui_registration(**kwargs) -> Callable[[Type[DataType]], Type[DataType]]:  # type: ignore
    """Decorator to register a dataclass with its autogenerated GUI implementation.
    Use this as a replacement for dataclass decorator.
    Example:
         @fl.dataclass_with_gui_registration(age__range=(0, 120))
         class Person:
             name: str
             age: int
    """

    def actual_decorator(cls: Type[DataType]) -> Type[DataType]:
        cls = dataclasses.dataclass(cls)  # First, create the dataclass
        register_dataclass(cls, **kwargs)
        return cls

    return actual_decorator


def register_base_model(base_model_type: Type[DataclassLikeType], **fiat_attrs) -> None:  # type: ignore
    """Register a pydantic BaseModel with its autogenerated GUI implementation.
    Note: you can also use the base_model_with_gui_registration decorator."""
    from fiatlight.fiat_togui.basemodel_gui import BaseModelGui

    assert issubclass(base_model_type, pydantic.BaseModel)

    def factory() -> AnyDataWithGui[Any]:
        attrs_as_dict = FiatAttributes(fiat_attrs)
        r = BaseModelGui(base_model_type, attrs_as_dict)
        return r

    gui_factories().register_type(base_model_type, factory)


def base_model_with_gui_registration(**kwargs) -> Callable[[Type[pydantic.BaseModel]], Type[pydantic.BaseModel]]:  # type: ignore
    """Decorator to register a pydantic BaseModel with its autogenerated GUI implementation."""

    def actual_decorator(cls: Type[pydantic.BaseModel]) -> Type[pydantic.BaseModel]:
        register_base_model(cls, **kwargs)
        return cls

    return actual_decorator


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
