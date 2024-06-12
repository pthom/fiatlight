import copy
from dataclasses import dataclass

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
from fiatlight.fiat_widgets import fiat_osd
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


@dataclass
class GuiHeaderLineParams(Generic[DataType]):
    label: str = ""
    label_color: ImVec4 | None = None
    label_tooltip: str | None = None
    show_clipboard_button: bool = True
    prefix_gui: Callable[[], None] | None = None
    suffix_gui: Callable[[], None] | None = None
    default_value_if_unspecified: DataType | Unspecified = UnspecifiedValue
    #
    popup_allow: bool = False
    popup_title: str = ""


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
    _can_set_unspecified_or_default: bool = False

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
        tooltip = "Collapse" if self._expanded else "Expand"
        if imgui.button(icon):
            self._expanded = not self._expanded
        fiat_osd.set_widget_tooltip(tooltip)

    def _show_copy_to_clipboard_button(self) -> None:
        if not self.callbacks.clipboard_copy_possible:
            return
        if self.value is UnspecifiedValue or self.value is ErrorValue:
            return
        with fontawesome_6_ctx():
            if imgui.button(icons_fontawesome_6.ICON_FA_COPY):
                clipboard_str = self.datatype_value_to_clipboard_str()
                imgui.set_clipboard_text(clipboard_str)
            fiat_osd.set_widget_tooltip("Copy value to clipboard")

    def can_collapse_present(self) -> bool:
        if isinstance(self.value, (Unspecified, Error)):
            return False
        return self.callbacks.present_collapsible

    def can_collapse_edit(self) -> bool:
        if isinstance(self.value, (Unspecified, Error)):
            return False
        return self.callbacks.edit_collapsible

    def can_edit_on_header_line(self) -> bool:
        return self.callbacks.edit is not None and not self.callbacks.edit_collapsible

    def can_present_on_header_line(self) -> bool:
        return self.callbacks.present is not None and not self.callbacks.present_collapsible

    def _can_edit_on_next_lines_if_expanded(self) -> bool:
        is_datatype_or_invalid = not isinstance(self.value, (Unspecified, Error))
        return self.callbacks.edit is not None and self.callbacks.edit_collapsible and is_datatype_or_invalid

    def _can_present_on_next_lines_if_expanded(self) -> bool:
        is_datatype_or_invalid = not isinstance(self.value, (Unspecified, Error))
        return self.callbacks.present is not None and self.callbacks.present_collapsible and is_datatype_or_invalid

    def _is_editing_on_next_lines(self) -> bool:
        return self._expanded and self._can_edit_on_next_lines_if_expanded()

    def _is_presenting_on_next_lines(self) -> bool:
        return self._expanded and self._can_present_on_next_lines_if_expanded()

    def _gui_present_header_line(self, params: GuiHeaderLineParams[DataType]) -> None:
        """Present the value as a string in one line, or as a widget if it fits on one line"""

        # can_present_in_node = not self.callbacks.present_popup_required
        can_present_in_popup = params.popup_allow and (
            self.callbacks.present_popup_required or self.callbacks.present_popup_possible
        )

        with imgui_ctx.begin_horizontal("present_header_line"):
            #
            # Left side:
            #   * prefix_gui  (might contain a node input pin when used in a function node)
            #   * label
            #   * expand button (if collapsible)
            #   * if not expanded: value or error or gui_edit (if fits one line)
            #   * invalid value info
            if params.prefix_gui is not None:
                params.prefix_gui()
            # Label
            label_color = (
                imgui.get_style().color_(imgui.Col_.text.value) if params.label_color is None else params.label_color
            )
            imgui.text_colored(label_color, params.label)
            if params.label_tooltip is not None:
                fiat_osd.set_widget_tooltip(params.label_tooltip)
            # Expand button
            if self.can_collapse_present():
                self._show_collapse_button()

            # Value as string or widget
            if not self._is_presenting_on_next_lines():
                if isinstance(self.value, Unspecified):
                    if isinstance(params.default_value_if_unspecified, Unspecified):
                        imgui.text_colored(
                            get_fiat_config().style.color_as_vec4(FiatColorType.ValueUnspecified), "Unspecified"
                        )
                    else:
                        imgui.text_colored(
                            get_fiat_config().style.color_as_vec4(FiatColorType.ParameterValueUsingDefault),
                            "Default value: ",
                        )
                        as_str = self.datatype_value_to_str(params.default_value_if_unspecified)
                        text_maybe_truncated(as_str, max_width_chars=40, max_lines=1)
                elif isinstance(self.value, Error):
                    imgui.text_colored(get_fiat_config().style.color_as_vec4(FiatColorType.ValueWithError), "Error")
                else:  # if isinstance(self.value, (InvalidValue, DataType))
                    value = self.get_actual_or_invalid_value()
                    can_present_on_header_line = self.can_present_on_header_line()
                    if can_present_on_header_line:
                        assert self.callbacks.present is not None  # make mypy happy
                        with imgui_ctx.begin_vertical(
                            "callback_present"
                        ):  # Some widgets expect a standard vertical layout
                            self.callbacks.present(value)
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

            #
            # Right Side:
            #   * open in popup button
            #   * clipboard button
            #   * suffix_gui (might contain a node output pin when used in a function node)
            imgui.spring()  # Align the rest to the right
            # popup button
            if can_present_in_popup:
                btn_label = "##present_in_popup"  # This will be our popup id (with the imgui id context)
                popup_label = params.popup_title + "##" + str(id(self))

                def gui_present_in_popup() -> None:
                    self._gui_present_next_lines(in_popup=True)

                fiat_osd.show_void_detached_window_button(btn_label, popup_label, gui_present_in_popup)
            # clipboard button
            if params.show_clipboard_button:
                self._show_copy_to_clipboard_button()
            # suffix_gui
            if params.suffix_gui is not None:
                params.suffix_gui()

    def _gui_edit_header_line(self, params: GuiHeaderLineParams[DataType]) -> bool:
        # can_edit_in_node = not self.callbacks.edit_popup_required
        can_edit_in_popup = params.popup_allow and (
            self.callbacks.edit_popup_required or self.callbacks.edit_popup_possible
        )

        changed = False

        with imgui_ctx.begin_horizontal("edit_header_line"):
            #
            # Left side: label, expand button, value or error or gui_edit (if fits one line), invalid value info
            #   * prefix_gui  (might contain a node input pin when used in a function node)
            #   * label
            #   * expand button (if collapsible)
            #   * if not expanded: value or error or gui_edit (if fits one line)
            #   * invalid value info
            if params.prefix_gui is not None:
                params.prefix_gui()
            # Label
            label_color = (
                imgui.get_style().color_(imgui.Col_.text.value) if params.label_color is None else params.label_color
            )
            imgui.text_colored(label_color, params.label)
            if params.label_tooltip is not None:
                fiat_osd.set_widget_tooltip(params.label_tooltip)
            # Expand button
            if self.can_collapse_edit():
                self._show_collapse_button()

            # Value as string or widget
            if not self._is_editing_on_next_lines():
                if isinstance(self.value, Unspecified):
                    if isinstance(params.default_value_if_unspecified, Unspecified):
                        imgui.text_colored(
                            get_fiat_config().style.color_as_vec4(FiatColorType.ValueUnspecified), "Unspecified"
                        )
                    else:
                        imgui.text_colored(
                            get_fiat_config().style.color_as_vec4(FiatColorType.ParameterValueUsingDefault),
                            "Default value: ",
                        )
                        as_str = self.datatype_value_to_str(params.default_value_if_unspecified)
                        text_maybe_truncated(as_str, max_width_chars=40, max_lines=1)
                elif isinstance(self.value, Error):
                    imgui.text_colored(get_fiat_config().style.color_as_vec4(FiatColorType.ValueWithError), "Error")
                else:  # if isinstance(self.value, (InvalidValue, DataType))
                    value = self.get_actual_or_invalid_value()
                    can_edit_on_header_line = self.can_edit_on_header_line()
                    if can_edit_on_header_line:
                        assert self.callbacks.edit is not None  # make mypy happy
                        with imgui_ctx.begin_vertical(
                            "callback_edit"
                        ):  # Some widgets expect a standard vertical layout
                            changed, new_value = self.callbacks.edit(value)
                        if changed:
                            self.value = new_value  # this will call the setter and trigger the validation
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

            #
            # Right Side:
            #   * open in popup button
            #   * Clipboard
            #   * Reset to unspecified or to default value
            imgui.spring()  # Align the rest to the right
            # popup button
            if can_edit_in_popup:
                btn_label = (
                    "##edit_in_popup" + "##" + str(id(self))
                )  # This will be our popup id (with the imgui id context)
                popup_label = params.popup_title + "##" + str(id(self))

                def gui_edit_in_popup() -> bool:
                    if isinstance(self.value, Unspecified):
                        # If unspecified, set to default value before editing in popup
                        if self.callbacks.default_value_provider is not None:
                            logging.warning(
                                "Value unspecified: setting to default_value_provider() before editing in popup"
                            )
                            self.value = self.callbacks.default_value_provider()
                    # Edit in popup
                    changed = self._gui_edit_next_lines(in_popup=True)

                    return changed

                fiat_osd.show_bool_detached_window_button(btn_label, popup_label, gui_edit_in_popup)

                # If the user edits the input value in a detached window
                if fiat_osd.get_detached_window_bool_return(btn_label):
                    changed = True

            # clipboard button
            if params.show_clipboard_button:
                self._show_copy_to_clipboard_button()
            # Reset to unspecified or to default value
            if self._can_set_unspecified_or_default:
                if self._show_set_unspecified_or_default_button():
                    changed = True
            # suffix_gui
            if params.suffix_gui is not None:
                params.suffix_gui()

        return changed

    def _show_set_unspecified_or_default_button(self) -> bool:
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
            fiat_osd.set_widget_tooltip("Reset to unspecified")
        if can_set_default_value:
            if imgui.button(icons_fontawesome_6.ICON_FA_SQUARE_PLUS):
                assert self.callbacks.default_value_provider is not None
                self.value = self.callbacks.default_value_provider()
                changed = True
            fiat_osd.set_widget_tooltip("Set to default value")
        if warn_no_default_provider:
            imgui.text_colored(
                get_fiat_config().style.color_as_vec4(FiatColorType.InvalidValue),
                icons_fontawesome_6.ICON_FA_TRIANGLE_EXCLAMATION,
            )
            fiat_osd.set_widget_tooltip("No default value provider")

        return changed

    def _gui_edit_next_lines(self, in_popup: bool) -> bool:
        # Line 2 and beyond: edit (if one line present is impossible)
        changed = False
        can_edit = self._is_editing_on_next_lines() if not in_popup else self._can_edit_on_next_lines_if_expanded()
        if can_edit:
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

    def _gui_present_next_lines(self, in_popup: bool) -> None:
        # Line 2 and beyond: present (if one line present is impossible)
        can_present = (
            self._is_presenting_on_next_lines() if not in_popup else self._can_present_on_next_lines_if_expanded()
        )
        if can_present:
            assert self.callbacks.present is not None
            with imgui_ctx.begin_horizontal("left_margin_present"):
                margin_size = hello_imgui.em_size(1.5)
                imgui.dummy(ImVec2(margin_size, 0))
                value = self.get_actual_or_invalid_value()
                with imgui_ctx.begin_vertical("callback_present"):
                    self.callbacks.present(value)

    def gui_present_customizable(self, params: GuiHeaderLineParams[DataType]) -> None:
        """Present the value using either the present callback or the default str conversion
        May present on one line (if possible) or on multiple lines with an expand button
        """
        with imgui_ctx.push_obj_id(self):
            with fontawesome_6_ctx():
                self._gui_present_header_line(params)
                self._gui_present_next_lines(in_popup=False)

    def gui_present(self, label: str) -> None:
        params = GuiHeaderLineParams[DataType](label=label)
        self.gui_present_customizable(params)

    def gui_edit_customizable(self, params: GuiHeaderLineParams[DataType]) -> bool:
        """Call the edit callback. Returns True if the value has changed
        May edit on one line (if possible) or on multiple lines with an expand button
        """
        changed = False  # noqa
        with imgui_ctx.push_obj_id(self):
            with fontawesome_6_ctx():
                if self._gui_edit_header_line(params):
                    changed = True
                if self._gui_edit_next_lines(in_popup=False):
                    changed = True

        return changed

    def gui_edit(self, label: str) -> bool:
        params = GuiHeaderLineParams[DataType](label=label)
        return self.gui_edit_customizable(params)

    def _Callbacks_Section(self) -> None:  # Dummy function to create a section in the IDE # noqa
        """
        # ------------------------------------------------------------------------------------------------------------------
        #            Callbacks sections
        # ------------------------------------------------------------------------------------------------------------------
        """

    def set_edit_callback(self, edit_callback: DataEditFunction[DataType]) -> None:
        """Helper function to set the edit callback from a free function"""
        self.callbacks.edit = edit_callback

    def set_present_callback(
        self, present_callback: DataPresentFunction[DataType], present_popup_required: bool | None = None
    ) -> None:
        """Helper function to set the present custom callback from a free function"""
        self.callbacks.present = present_callback
        if present_popup_required is not None:
            self.callbacks.present_popup_required = present_popup_required

    def add_validate_value_callback(self, cb: Callable[[DataType], DataValidationResult]) -> None:
        self.callbacks.validate_value.append(cb)

    def _Serialization_Section(self) -> None:
        """
        # ------------------------------------------------------------------------------------------------------------------
        #            Serialization and deserialization
        # ------------------------------------------------------------------------------------------------------------------
        """

    @final
    def call_save_to_dict(self, value: DataType | Unspecified | Error | InvalidValue[DataType]) -> JsonDict:
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
    def call_load_from_dict(self, json_data: JsonDict) -> DataType | Unspecified | Error:
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

    @final
    def call_save_gui_options_to_json(self) -> JsonDict:
        callbacks_options = self.callbacks.save_gui_options_to_json() if self.callbacks.save_gui_options_to_json else {}
        return {"cb_options": callbacks_options, "expanded": self._expanded}

    @final
    def call_load_gui_options_from_json(self, json_data: JsonDict) -> None:
        if self.callbacks.load_gui_options_from_json is not None:
            self.callbacks.load_gui_options_from_json(json_data["cb_options"])
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

    def can_present(self) -> bool:
        """Returns True if the present callback can be called
        i.e. if the value is not Unspecified or Error, and the present callback is set
        """
        if isinstance(self.value, (Error, Unspecified)):
            return False
        return self.callbacks.present is not None

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
