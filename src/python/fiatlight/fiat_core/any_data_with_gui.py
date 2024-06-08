import copy

import pydantic

from fiatlight.fiat_types.base_types import (
    JsonDict,
    DataType,
)
from fiatlight.fiat_types.error_types import Error, ErrorValue, Unspecified, UnspecifiedValue, InvalidValue
from fiatlight.fiat_types.function_types import DataPresentFunction, DataEditFunction, DataValidationResult  # noqa
from .any_data_gui_callbacks import AnyDataGuiCallbacks
from .possible_custom_attributes import PossibleCustomAttributes
from imgui_bundle import imgui, imgui_ctx, ImVec4, hello_imgui, ImVec2
from fiatlight.fiat_config import get_fiat_config, FiatColorType
from fiatlight.fiat_widgets.fontawesome6_ctx_utils import icons_fontawesome_6, fontawesome_6_ctx
from fiatlight.fiat_widgets.fiat_osd import set_widget_tooltip
from fiatlight.fiat_widgets.misc_widgets import text_maybe_truncated
from typing import Generic, Any, Type, final, Callable
import logging


class AnyDataWithGuiGenericPossibleCustomAttributes(PossibleCustomAttributes):
    def __init__(self) -> None:
        super().__init__("AnyDataWithGui Generic attributes")
        self.add_explained_section("Generic attributes")
        self.add_explained_attribute(
            name="validate_value",
            type_=object,
            explanation="Function to validate a parameter value (should return DataValidationResult.ok() .error()",
            default_value=None,
        )


_ANYDATAWITHGUI_GENERIC_POSSIBLE_CUSTOM_ATTRIBUTES = AnyDataWithGuiGenericPossibleCustomAttributes()


class AnyDataWithGui(Generic[DataType]):
    """AnyDataWithGui: a GUI associated to a type.

    AnyDataWithGui[DataType]
    ========================

    This class manages data of any type with associated GUI callbacks, allowing for custom rendering, editing,
    serialization, and event handling within the Fiatlight framework.

    Members:
    --------
    # The type of the data, e.g. int, str, typing.List[int], typing.Tuple[int, str], typing.Optional[int], etc.
    _type: Type[DataType]

    # The value of the data - can be a DataType, Unspecified, or Error
    # It is accessed through the value property, which triggers the on_change callback (if set)
    _value: DataType | Unspecified | Error = UnspecifiedValue

    # Callbacks for the GUI
    # This is the heart of FiatLight: the GUI is defined by the callbacks.
    # Think of them as __dunder__ methods for the GUI.
    callbacks: AnyDataGuiCallbacks[DataType]

    # If True, the value can be None. This is useful when the data is optional.
    # Otherwise, any None value will be considered as an Error.
    # Note: when using Optional[any registered type], this flag is automatically set to True.
    can_be_none: bool = False

    Property:
    ---------
    # Custom attributes that can be set by the user, to give hints to the GUI.
    # For example, with this function declaration,
    #         def f(x: int, y: int) -> int:
    #             return x + y
    #        f.x__range = (0, 10)
    # custom_attrs["range"] will be (0, 10) for the parameter x.
    @property
    custom_attrs -> dict[str, Any]

    """

    # ------------------------------------------------------------------------------------------------------------------
    #            Members
    # ------------------------------------------------------------------------------------------------------------------
    # The type of the data, e.g. int, str, List[int], Tuple[int, str], Optional[int], etc.
    _type: Type[DataType]

    # The value of the data - can be a DataType, Unspecified, or Error
    # It is accessed through the value property, which triggers the on_change callback (if set)
    _value: DataType | Unspecified | Error | InvalidValue[DataType] = UnspecifiedValue

    # Callbacks for the GUI
    # This is the heart of FiatLight: the GUI is defined by the callbacks.
    # Think of them as __dunder__ methods for the GUI.
    callbacks: AnyDataGuiCallbacks[DataType]

    # If True, the value can be None. This is useful when the data is optional.
    # Otherwise, any None value will be considered as an Error.
    # Note: when using Optional[any registered type], this flag is automatically set to True.
    can_be_none: bool = False

    # Custom attributes that can be set by the user, to give hints to the GUI.
    # For example, with this function declaration,
    #         def f(x: int, y: int) -> int:
    #             return x + y
    #        f.x__range = (0, 10)
    # custom_attrs["range"] will be (0, 10) for the parameter x.
    _custom_attrs: dict[str, Any]

    # Is the present or edit view expanded. This is serialized and deserialized in the GUI options.
    _expanded: bool = True

    # If True, a GUI to set the value as Unspecified is provided
    # This is useful in Function Nodes.
    # Unspecified stands for a function parameter that has not been set by the user
    _can_set_unspecified: bool = False

    @staticmethod
    def _Init_Section() -> None:  # Dummy function to create a section in the IDE # noqa
        """
        # ------------------------------------------------------------------------------------------------------------------
        #            Initialization
        # ------------------------------------------------------------------------------------------------------------------
        """
        pass

    def __init__(self, data_type: Type[DataType]) -> None:
        """Initialize the AnyDataWithGui with a type, an unspecified value, and no callbacks."""
        self._type = data_type
        self.callbacks = AnyDataGuiCallbacks()
        self._custom_attrs = {}

    @staticmethod
    def _Value_Section() -> None:  # Dummy function to create a section in the IDE # noqa
        """
        # ------------------------------------------------------------------------------------------------------------------
        #            Value getter and setter + get_actual_value (which returns a DataType or raises an exception)
        # ------------------------------------------------------------------------------------------------------------------
        """
        pass

    @property
    def value(self) -> DataType | Unspecified | Error | InvalidValue[DataType]:
        """The value of the data, accessed through the value property.
        Warning: it might be an instance of `Unspecified` (user did not enter any value) or `Error` (an error was triggered)
        """
        return self._value

    @value.setter
    def value(self, new_value: DataType | Unspecified | Error | InvalidValue[DataType]) -> None:
        """Set the value of the data. This triggers the on_change callback (if set)"""
        self._value = new_value
        if isinstance(new_value, (Unspecified, Error, InvalidValue)):
            return

        # If value is of type DataType, run validators
        # (this may change self.value to an InvalidValue)
        if len(self.callbacks.validate_value) > 0:
            error_messages = []
            for validate_value in self.callbacks.validate_value:
                validation_result = validate_value(new_value)
                if not validation_result.is_valid:
                    error_messages.append(validation_result.error_message)
            if len(error_messages) > 0:
                all_error_messages = " - ".join(error_messages)
                self._value = InvalidValue(error_message=all_error_messages, invalid_value=new_value)

        # Call on_change callback if everything is fine
        if not isinstance(self.value, InvalidValue) and self.callbacks.on_change is not None:
            self.callbacks.on_change(new_value)

    def get_actual_value(self) -> DataType:
        """Returns the actual value of the data, or raises an exception if the value is Unspecified or Error or InvalidValue
        When we are inside a callback, we can be sure that the value is of the correct type, so we can call this method
        instead of accessing the value directly and checking for Unspecified or Error.
        """
        if isinstance(self.value, Unspecified):
            raise ValueError("Cannot get value of Unspecified")
        elif isinstance(self.value, Error):
            raise ValueError("Cannot get value of Error")
        elif isinstance(self.value, InvalidValue):
            raise ValueError(f"Invalid value: {self.value} ({self.value.error_message})")
        else:
            return self.value

    def get_actual_or_invalid_value(self) -> DataType:
        """Returns the actual value of the data, or raises an exception if the value is Unspecified or Error"""
        if isinstance(self.value, Unspecified):
            raise ValueError("Cannot get value of Unspecified")
        elif isinstance(self.value, Error):
            raise ValueError("Cannot get value of Error")
        elif isinstance(self.value, InvalidValue):
            return self.value.invalid_value
        else:
            return self.value

    @staticmethod
    def _CustomAttributes_Section() -> None:  # Dummy function to create a section in the IDE # noqa
        """
        # ------------------------------------------------------------------------------------------------------------------
        #            Custom Attributes
        # ------------------------------------------------------------------------------------------------------------------
        """
        pass

    @staticmethod
    def possible_custom_attributes() -> PossibleCustomAttributes | None:
        """Return the possible custom attributes for this type, if available.
        Should be overridden in subclasses, when custom attributes are available.

        It is strongly advised to return a class variable, or a global variable
        to avoid creating a new instance each time this method is called.
        """
        return None

    @final
    def possible_custom_attributes_with_generic(
        self,
    ) -> tuple[PossibleCustomAttributes | None, PossibleCustomAttributes]:
        descendant_attrs = self.possible_custom_attributes()
        return descendant_attrs, _ANYDATAWITHGUI_GENERIC_POSSIBLE_CUSTOM_ATTRIBUTES

    @property
    def custom_attrs(self) -> dict[str, Any]:
        return self._custom_attrs

    def merge_custom_attrs(self, custom_attrs: dict[str, Any]) -> None:
        """Merge custom attributes with the existing ones"""
        if len(custom_attrs) == 0:
            return
        possible_custom_attrs, _generic_custom_attrs = self.possible_custom_attributes_with_generic()

        # Create a version that holds all custom attributes
        all_custom_attrs = copy.deepcopy(_generic_custom_attrs)
        if possible_custom_attrs is not None:
            all_custom_attrs.merge_attributes(copy.copy(possible_custom_attrs))

        all_custom_attrs.raise_exception_if_bad_custom_attrs(custom_attrs)
        # except FiatToGuiException as e:
        #     msg_error = f'''
        #         Cannot set custom attributes for {self._type} in class {self.__class__}
        #             Please override the possible_custom_attributes() method in the class {self.__class__}
        #             with the following signature:
        #
        #                 @staticmethod
        #                 def possible_custom_attributes() -> PossibleCustomAttributes | None:
        #                     """Return the possible custom attributes for this type, if available.
        #
        #                     It is advised to return a global variable, to avoid creating
        #                     a new instance each time this method is called.
        #                     """
        #                     ...
        #         '''
        #     raise FiatToGuiException(msg_error) from e

        self.custom_attrs.update(custom_attrs)
        if self.callbacks.on_custom_attrs_changed is not None:
            self.callbacks.on_custom_attrs_changed(self.custom_attrs)

    def _Gui_Section(self) -> None:  # Dummy function to create a section in the IDE # noqa
        """
        # ------------------------------------------------------------------------------------------------------------------
        #            Gui sections
        #      (Can also be used outside a function Node)
        # ------------------------------------------------------------------------------------------------------------------
        """

    def _show_collapse_button(self) -> None:
        icon = icons_fontawesome_6.ICON_FA_CARET_DOWN if self._expanded else icons_fontawesome_6.ICON_FA_CARET_RIGHT
        if imgui.button(icon):
            self._expanded = not self._expanded

    def _show_copy_to_clipboard_button(self) -> None:
        if not self.callbacks.clipboard_copy_possible:
            return
        if self.value is UnspecifiedValue or self.value is ErrorValue:
            return
        with fontawesome_6_ctx():
            if imgui.button(icons_fontawesome_6.ICON_FA_COPY):
                clipboard_str = self.datatype_value_to_clipboard_str()
                imgui.set_clipboard_text(clipboard_str)
            set_widget_tooltip("Copy value to clipboard")

    def can_collapse_present(self) -> bool:
        if isinstance(self.value, (Unspecified, Error)):
            return False
        return self.callbacks.present_custom_collapsible

    def can_collapse_edit(self) -> bool:
        if isinstance(self.value, (Unspecified, Error)):
            return False
        return self.callbacks.edit_collapsible

    def can_edit_on_header_line(self) -> bool:
        return self.callbacks.edit is not None and not self.callbacks.edit_collapsible

    def can_present_custom_on_header_line(self) -> bool:
        return self.callbacks.present_custom is not None and not self.callbacks.present_custom_collapsible

    def can_edit_on_next_lines(self) -> bool:
        is_datatype_or_invalid = not isinstance(self.value, (Unspecified, Error))
        return (
            self.callbacks.edit is not None
            and self.callbacks.edit_collapsible
            and self._expanded
            and is_datatype_or_invalid
        )

    def can_present_on_next_lines(self) -> bool:
        is_datatype_or_invalid = not isinstance(self.value, (Unspecified, Error))
        return (
            self.callbacks.present_custom is not None
            and self.callbacks.present_custom_collapsible
            and self._expanded
            and is_datatype_or_invalid
        )

    def _gui_present_header_line(
        self,
        label: str,
        label_color: ImVec4,
        value_tooltip: str | None = None,
    ) -> None:
        """Present the value as a string in one line, or as a widget if it fits on one line"""
        with imgui_ctx.begin_horizontal("present_header_line"):
            #
            # Left side: label, expand button, value or error or gui_edit (if fits one line), invalid value info
            #
            # Label
            imgui.text_colored(label_color, label)
            # Expand button
            if self.can_collapse_present():
                self._show_collapse_button()

            # Value as string or widget
            if isinstance(self.value, Unspecified):
                imgui.text_colored(get_fiat_config().style.color_as_vec4(FiatColorType.ValueUnspecified), "Unspecified")
            elif isinstance(self.value, Error):
                imgui.text_colored(get_fiat_config().style.color_as_vec4(FiatColorType.ValueWithError), "Error")
            else:  # if isinstance(self.value, (InvalidValue, DataType))
                value = self.get_actual_or_invalid_value()
                can_present_custom_on_header_line = self.can_present_custom_on_header_line()
                if can_present_custom_on_header_line:
                    assert self.callbacks.present_custom is not None  # make mypy happy
                    with imgui_ctx.begin_vertical(
                        "callback_present_custom"
                    ):  # Some widgets expect a standard vertical layout
                        self.callbacks.present_custom(value)
                else:
                    as_str = self.datatype_value_to_str(value)
                    text_maybe_truncated(as_str, max_width_chars=40, max_lines=1)

            # invalid value info
            if isinstance(self.value, InvalidValue):
                text_maybe_truncated(
                    icons_fontawesome_6.ICON_FA_TRIANGLE_EXCLAMATION + " " + self.value.error_message,
                    color=get_fiat_config().style.color_as_vec4(FiatColorType.InvalidValue),
                    max_lines=1,
                    max_width_chars=40,
                )

            # Tooltip
            if value_tooltip is not None:
                set_widget_tooltip(value_tooltip)

            #
            # Right Side: clipboard button
            #
            imgui.spring()  # Align the rest to the right
            self._show_copy_to_clipboard_button()

    def _gui_edit_header_line(self, label: str, label_color: ImVec4, value_tooltip: str | None = None) -> bool:
        changed = False

        with imgui_ctx.begin_horizontal("edit_header_line"):
            #
            # Left side: label, expand button, value or error or gui_edit (if fits one line), invalid value info
            #
            # Label
            imgui.text_colored(label_color, label)
            # Expand button
            if self.can_collapse_edit():
                self._show_collapse_button()

            # Value as string or widget
            if isinstance(self.value, Unspecified):
                imgui.text_colored(get_fiat_config().style.color_as_vec4(FiatColorType.ValueUnspecified), "Unspecified")
            elif isinstance(self.value, Error):
                imgui.text_colored(get_fiat_config().style.color_as_vec4(FiatColorType.ValueWithError), "Error")
            else:  # if isinstance(self.value, (InvalidValue, DataType))
                value = self.get_actual_or_invalid_value()
                can_edit_on_header_line = self.can_edit_on_header_line()
                if can_edit_on_header_line:
                    assert self.callbacks.edit is not None  # make mypy happy
                    with imgui_ctx.begin_vertical("callback_edit"):  # Some widgets expect a standard vertical layout
                        changed, new_value = self.callbacks.edit(value)
                    if changed:
                        self.value = new_value  # this will call the setter and trigger the validation
                else:
                    as_str = self.datatype_value_to_str(value)
                    text_maybe_truncated(as_str, max_width_chars=40, max_lines=1)

                # After drawing on one line, display the tooltip
                if value_tooltip is not None:
                    set_widget_tooltip(value_tooltip)

            # invalid value info
            if isinstance(self.value, InvalidValue):
                text_maybe_truncated(
                    icons_fontawesome_6.ICON_FA_TRIANGLE_EXCLAMATION + " " + self.value.error_message,
                    color=get_fiat_config().style.color_as_vec4(FiatColorType.InvalidValue),
                    max_lines=1,
                    max_width_chars=40,
                )

            #
            # Right Side: Clipboard, Reset to unspecified or to default value
            #
            imgui.spring()  # Align the rest to the right
            self._show_copy_to_clipboard_button()
            if self._show_set_unset_button():
                changed = True

        return changed

    def _show_set_unset_button(self) -> bool:
        can_set_default_value = False
        warn_no_default_provider = False
        can_set_unspecified = False
        if isinstance(self.value, Unspecified):
            # if unspecified, provide "+" to set to default provider value
            if self.callbacks.default_value_provider is not None:
                can_set_default_value = True
            else:
                warn_no_default_provider = True
        if not isinstance(self.value, (Error, Unspecified)):
            can_set_unspecified = True

        changed = False
        if can_set_unspecified:
            if imgui.button(icons_fontawesome_6.ICON_FA_SQUARE_MINUS):
                self.value = UnspecifiedValue
                changed = True
            set_widget_tooltip("Reset to unspecified")
        if can_set_default_value:
            if imgui.button(icons_fontawesome_6.ICON_FA_SQUARE_PLUS):
                assert self.callbacks.default_value_provider is not None
                self.value = self.callbacks.default_value_provider()
            set_widget_tooltip("Set to default value")
        if warn_no_default_provider:
            imgui.text_colored(
                get_fiat_config().style.color_as_vec4(FiatColorType.InvalidValue),
                icons_fontawesome_6.ICON_FA_TRIANGLE_EXCLAMATION,
            )
            set_widget_tooltip("No default value provider")

        return changed

    def _gui_edit_next_lines(self) -> bool:
        # Line 2 and beyond: edit (if one line present is impossible)
        changed = False
        if self.can_edit_on_next_lines():
            assert self.callbacks.edit is not None
            with imgui_ctx.begin_horizontal("left_margin_edit"):
                margin_size = hello_imgui.em_size(1.5)
                imgui.dummy(ImVec2(margin_size, 0))
                value = self.get_actual_or_invalid_value()
                with imgui_ctx.begin_vertical("callback_edit"):
                    changed, new_value = self.callbacks.edit(value)
                    if changed:
                        self.value = new_value  # this will call the setter and trigger the validation
        return changed

    def _gui_present_custom_next_lines(self) -> None:
        # Line 2 and beyond: present (if one line present is impossible)
        if self.can_present_on_next_lines():
            assert self.callbacks.present_custom is not None
            with imgui_ctx.begin_horizontal("left_margin_present"):
                margin_size = hello_imgui.em_size(1.5)
                imgui.dummy(ImVec2(margin_size, 0))
                value = self.get_actual_or_invalid_value()
                with imgui_ctx.begin_vertical("callback_present"):
                    self.callbacks.present_custom(value)

    def gui_present_custom(
        self,
        label: str,
        label_color: ImVec4 | None = None,
    ) -> None:
        """Present the value using either the present_custom callback or the default str conversion
        May present on one line (if possible) or on multiple lines with an expand button
        """
        if label_color is None:
            label_color = imgui.get_style().color_(imgui.Col_.text.value)
        with imgui_ctx.push_obj_id(self):
            with fontawesome_6_ctx():
                self._gui_present_header_line(label, label_color)
                self._gui_present_custom_next_lines()

    def gui_edit(
        self,
        label: str,
        label_color: ImVec4 | None = None,
    ) -> bool:
        """Call the edit callback. Returns True if the value has changed
        May edit on one line (if possible) or on multiple lines with an expand button
        """
        if label_color is None:
            label_color = imgui.get_style().color_(imgui.Col_.text.value)
        changed = False  # noqa
        with imgui_ctx.push_obj_id(self):
            with fontawesome_6_ctx():
                if self._gui_edit_header_line(label, label_color):
                    changed = True
                if self._gui_edit_next_lines():
                    changed = True

        return changed

    def _Callbacks_Section(self) -> None:  # Dummy function to create a section in the IDE # noqa
        """
        # ------------------------------------------------------------------------------------------------------------------
        #            Callbacks sections
        # ------------------------------------------------------------------------------------------------------------------
        """

    def set_edit_callback(self, edit_callback: DataEditFunction[DataType]) -> None:
        """Helper function to set the edit callback from a free function"""
        self.callbacks.edit = edit_callback

    def set_present_custom_callback(
        self, present_callback: DataPresentFunction[DataType], present_custom_popup_required: bool | None = None
    ) -> None:
        """Helper function to set the present custom callback from a free function"""
        self.callbacks.present_custom = present_callback
        if present_custom_popup_required is not None:
            self.callbacks.present_custom_popup_required = present_custom_popup_required

    def add_validate_value_callback(self, cb: Callable[[DataType], DataValidationResult]) -> None:
        self.callbacks.validate_value.append(cb)

    def _Serialization_Section(self) -> None:
        """
        # ------------------------------------------------------------------------------------------------------------------
        #            Serialization and deserialization
        # ------------------------------------------------------------------------------------------------------------------
        """

    @final
    def save_to_dict(self, value: DataType | Unspecified | Error | InvalidValue[DataType]) -> JsonDict:
        """Serialize the value to a dictionary

        Will call the save_to_dict callback if set, otherwise will use the default serialization, when available.
        A default serialization is available for primitive types, tuples, and Pydantic models.

        (This is how fiatlight saves the data to a JSON file)

        Do not override these methods in descendant classes!
        """
        if isinstance(value, (Unspecified, InvalidValue)):
            # We do not save Unspecified or InvalidValue,
            # and we do not differentiate between them in the saved JSON
            return {"type": "Unspecified"}
        elif isinstance(value, Error):
            return {"type": "Error"}
        elif self.callbacks.save_to_dict is not None:
            return self.callbacks.save_to_dict(value)
        elif isinstance(value, (str, int, float, bool)):
            return {"type": "Primitive", "value": value}
        elif isinstance(value, tuple):
            return {"type": "Tuple", "value": value}
        elif isinstance(value, pydantic.BaseModel):
            return {"type": "Pydantic", "value": value.model_dump(mode="json")}
        else:
            logging.warning(f"Cannot serialize {value}")
            return {"type": "Error"}

    @final
    def load_from_dict(self, json_data: JsonDict) -> DataType | Unspecified | Error:
        """Deserialize the value from a dictionary
        Do not override these methods in descendant classes!
        """
        if "type" not in json_data and self.callbacks.load_from_dict is None:
            raise ValueError(f"Cannot deserialize {json_data}: missing 'type' key")

        if "type" in json_data and json_data["type"] == "Unspecified":
            return UnspecifiedValue
        elif "type" in json_data and json_data["type"] == "Error":
            return ErrorValue
        elif self.callbacks.load_from_dict is not None:
            return self.callbacks.load_from_dict(json_data)
        elif json_data["type"] == "Primitive":
            r = json_data["value"]
            assert isinstance(r, (str, int, float, bool))
            return r  # type: ignore
        elif json_data["type"] == "Tuple":
            as_list = json_data["value"]
            return tuple(as_list)  # type: ignore
        elif json_data["type"] == "Pydantic":
            assert self._type is not None
            assert issubclass(self._type, pydantic.BaseModel)
            r = self._type.model_validate(json_data["value"])
            assert isinstance(r, self._type)
            return r  # type: ignore
        else:
            raise ValueError(f"Cannot deserialize {json_data}")

    def save_gui_options_to_json(self) -> JsonDict:
        return {"expanded": self._expanded}

    def load_gui_options_from_json(self, json_data: JsonDict) -> None:
        self._expanded = json_data.get("expanded", True)

    def _Utilities_Section(self) -> None:
        """
        # ------------------------------------------------------------------------------------------------------------------
        #            Utilities
        # ------------------------------------------------------------------------------------------------------------------
        """

    def datatype_value_to_str(self, value: DataType) -> str:
        """Convert the value to a string
        Uses either the present_str callback, or the default str conversion
        """
        default_str: str
        if self.callbacks.present_str is not None:
            default_str = self.callbacks.present_str(value)
        else:
            try:
                default_str = str(value)
            except (TypeError, OverflowError):
                default_str = "???"
        return default_str

    def datatype_value_to_clipboard_str(self) -> str:
        """Convert the value to a string for the clipboard
        Uses either the clipboard_copy_str callback, or the default str conversion
        """
        if isinstance(self.value, Unspecified):
            return "Unspecified"
        elif isinstance(self.value, Error):
            return "Error"
        else:
            actual_value = self.get_actual_or_invalid_value()
            if self.callbacks.clipboard_copy_str is not None:
                return self.callbacks.clipboard_copy_str(actual_value)
            else:
                return self.datatype_value_to_str(actual_value)

    def can_present_custom(self) -> bool:
        """Returns True if the present_custom callback can be called
        i.e. if the value is not Unspecified or Error, and the present_custom callback is set
        """
        if isinstance(self.value, (Error, Unspecified)):
            return False
        return self.callbacks.present_custom is not None

    def docstring_first_line(self) -> str | None:
        """Return the first line of the docstring, if available"""
        from fiatlight.fiat_utils.docstring_utils import docstring_first_line

        doc = docstring_first_line(self)
        if doc is None:
            return None
        # We are only interested in the docstring of subclasses.
        if doc.startswith("AnyDataWithGui:"):
            return None
        return doc


class AnyDataWithGui_UnregisteredType(AnyDataWithGui[Any]):
    """AnyDataWithGui_UnregisteredType: a GUI associated to a type that is not registered in the Fiatlight framework.

    Use sparingly, as such a data type cannot do much, and is not very useful.
    """

    unregistered_typename: str

    def __init__(self, typename: str) -> None:
        super().__init__(type(Any))
        self.unregistered_typename = typename


def toggle_expanded_state_on_guis(guis: list[AnyDataWithGui[Any]]) -> None:
    has_one_expanded = False
    for gui in guis:
        if gui._expanded:
            has_one_expanded = True
    new_expanded_state = not has_one_expanded
    for gui in guis:
        gui._expanded = new_expanded_state
