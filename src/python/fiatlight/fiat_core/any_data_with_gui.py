import copy
from dataclasses import dataclass
from enum import Enum

import pydantic

from fiatlight.fiat_types.base_types import (
    JsonDict,
    DataType,
)
from fiatlight.fiat_types.error_types import Error, ErrorValue, Unspecified, UnspecifiedValue, Invalid
from fiatlight.fiat_types.function_types import DataPresentFunction, DataEditFunction
from fiatlight.fiat_types.base_types import FiatAttributes
from fiatlight.fiat_types import typename_utils
from .any_data_gui_callbacks import AnyDataGuiCallbacks
from .possible_fiat_attributes import PossibleFiatAttributes
from imgui_bundle import imgui, imgui_ctx, ImVec4, hello_imgui, ImVec2
from fiatlight.fiat_config import get_fiat_config, FiatColorType
from fiatlight.fiat_widgets.fontawesome6_ctx_utils import icons_fontawesome_6, fontawesome_6_ctx
from fiatlight.fiat_widgets import fiat_osd
from fiatlight.fiat_widgets.text_truncated import text_maybe_truncated
from typing import Generic, Any, Type, final, Callable
import logging


class AnyDataWithGuiGenericPossibleFiatAttributes(PossibleFiatAttributes):
    def __init__(self) -> None:
        super().__init__("AnyDataWithGui Generic attributes")
        self.add_explained_section("Generic attributes")
        self.add_explained_attribute(
            name="validator",
            type_=object,
            explanation="Function to validate a parameter value: should raise a ValueError if invalid, or return the value (possibly modified)",
            default_value=None,
        )
        self.add_explained_attribute(
            name="label",
            type_=str,
            explanation="A label for the parameter. If empty, the function parameter name is used",
            default_value="",
        )
        self.add_explained_attribute(
            name="tooltip",
            type_=str,
            explanation="An optional tooltip to be displayed",
            default_value="",
        )
        self.add_explained_attribute(
            name="label_color",
            type_=ImVec4,
            explanation="The color of the label (will use the default text color if not provided)",
            default_value=ImVec4(0, 0, 0, 1),
        )
        self.add_explained_attribute(
            name="edit_collapsible",
            type_=bool,
            explanation="If True, the edit GUI may be collapsible",
            default_value=True,
        )
        self.add_explained_attribute(
            name="present_collapsible",
            type_=bool,
            explanation="If True, the present GUI may be collapsible",
            default_value=True,
        )
        self.add_explained_attribute(
            name="present_detachable",
            type_=bool,
            explanation="If True, the present GUI may be shown in a separate window",
            default_value=False,
        )
        self.add_explained_attribute(
            name="edit_detachable",
            type_=bool,
            explanation="If True, the edit GUI may be shown in a separate window",
            default_value=False,
        )


_ANYDATAWITHGUI_GENERIC_POSSIBLE_FIAT_ATTRIBUTES = AnyDataWithGuiGenericPossibleFiatAttributes()


def _draw_label_with_max_width(
    label: str, color: ImVec4, label_tooltip: str | None, status_tooltip: str | None = None
) -> None:
    tooltip: str

    if label_tooltip is not None and status_tooltip is not None:
        tooltip = label_tooltip + "\n----------------------------------\n" + status_tooltip
    elif label_tooltip is not None:
        tooltip = label_tooltip
    elif status_tooltip is not None:
        tooltip = status_tooltip
    else:
        tooltip = ""

    cur_pos = imgui.get_cursor_screen_pos()
    if "##" in label:
        label = label.split("##")[0]
    shortened_label = label
    max_width_pixels = hello_imgui.em_size(get_fiat_config().style.str_truncation.param_label_max_width_em)
    while True:
        size = imgui.calc_text_size(shortened_label)
        if size.x < max_width_pixels:
            break
        shortened_label = shortened_label[:-1]
        if len(shortened_label) == 0:
            break

    if shortened_label != label:
        imgui.text_colored(color, shortened_label + "...")
        tooltip = label + "\n" + tooltip
    else:
        imgui.text_colored(color, label)

    if len(tooltip) > 0:
        fiat_osd.set_widget_tooltip(tooltip)

    new_cursor_pos = ImVec2(cur_pos.x + max_width_pixels, cur_pos.y)
    imgui.set_cursor_screen_pos(new_cursor_pos)


@dataclass
class GuiHeaderLineParams(Generic[DataType]):
    parent_name: str
    show_clipboard_button: bool = True
    prefix_gui: Callable[[], None] | None = None
    suffix_gui: Callable[[], None] | None = None
    default_value_if_unspecified: DataType | Unspecified = UnspecifiedValue
    is_expand_disabled: bool = (
        False  # expand will be disabled when a whole region is collapsed (e.g. inputs, outputs, fiat_tuning, etc.)
    )


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
    _value: DataType | Unspecified | Error | Invalid[DataType] = UnspecifiedValue

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
    # fiat_attributes["range"] will be (0, 10) for the parameter x.
    @property
    fiat_attributes -> dict[str, Any]

    """

    # ------------------------------------------------------------------------------------------------------------------
    #            Members
    # ------------------------------------------------------------------------------------------------------------------
    # The type of the data, e.g. int, str, List[int], Tuple[int, str], Optional[int], etc.
    _type: Type[DataType] | None

    # The value of the data - can be a DataType, Unspecified, or Error
    # It is accessed through the value property, which triggers the on_change callback (if set)
    _value: DataType | Unspecified | Error | Invalid[DataType] = UnspecifiedValue

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
    # _fiat_attributes["range"] will be (0, 10) for the parameter x.
    _fiat_attributes: FiatAttributes

    # Is the present or edit view expanded. This is serialized and deserialized in the GUI options.
    _expanded: bool = True

    # If True, a GUI to set the value as Unspecified is provided
    # This is useful in Function Nodes.
    # Unspecified stands for a function parameter that has not been set by the user
    _can_set_unspecified_or_default: bool = False

    # Label and tooltip (can be set via fiat attributes)
    label: str | None = None
    label_color: ImVec4 | None = None
    tooltip: str | None = None
    status_tooltip: str | None = None

    class CollapseOrExpandChildren(Enum):
        collapse = "Collapse all children"
        expand = "Expand all children"

    class PresentOrEdit(Enum):
        present = "View"
        edit = "Edit"

    class _Init_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # ------------------------------------------------------------------------------------------------------------------
        #            Initialization
        # ------------------------------------------------------------------------------------------------------------------
        """

        pass

    def __init__(self, data_type: Type[DataType] | None) -> None:
        """Initialize the AnyDataWithGui with a type, an unspecified value, and no callbacks."""
        self._type = data_type
        self.callbacks = AnyDataGuiCallbacks()
        self._fiat_attributes = FiatAttributes({})

    class _Value_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # ------------------------------------------------------------------------------------------------------------------
        #            Value getter and setter + get_actual_value (which returns a DataType or raises an exception)
        # ------------------------------------------------------------------------------------------------------------------
        """

        pass

    @property
    def value(self) -> DataType | Unspecified | Error | Invalid[DataType]:
        """The value of the data, accessed through the value property.
        Warning: it might be an instance of `Unspecified` (user did not enter any value)
                 or `Error` (an error was triggered) or `Invalid` (the value is invalid).
        """
        return self._value

    @value.setter
    def value(self, new_value: DataType | Unspecified | Error | Invalid[DataType]) -> None:
        """Set the value of the data. This triggers the on_change callback (if set)"""
        self._value = new_value
        if isinstance(new_value, (Unspecified, Error, Invalid)):
            return

        # If value is of type DataType, run validators
        # (this may change self.value to an Invalid)
        if len(self.callbacks.validators) > 0:
            error_messages = []
            for validator in self.callbacks.validators:
                is_valid = True
                error_message = ""
                try:
                    new_value_after_validation = validator(new_value)
                    if new_value_after_validation is None and new_value is not None:
                        import inspect

                        validator_info = inspect.getsourcelines(validator)
                        file_name = inspect.getfile(validator)
                        raise RuntimeError(
                            f"""
                            The validator "{validator}" for the value "{self.label}" returned None.
                            A validator should either:
                                - raise a ValueError if the value is invalid, with a nice error message.
                                  (the error message will be shown to the user)
                                - or, return the value itself (or a modified version of it, if needed).
                            This validator is defined in {file_name}
                            at line {validator_info[1]}.
                        """
                        )
                    new_value = new_value_after_validation
                except ValueError as e:
                    is_valid = False
                    error_message = str(e)
                if not is_valid:
                    if error_message not in error_messages:
                        error_messages.append(error_message)
            if len(error_messages) > 0:
                all_error_messages = " - ".join(error_messages)
                self._value = Invalid(error_message=all_error_messages, invalid_value=new_value)
            else:
                # Since the validators may have changed the value, we need to set it again
                # We do it by using the _value member, not the value property, to avoid calling the validators again
                self._value = new_value

        # Call on_change callback if everything is fine
        if not isinstance(self.value, Invalid) and self.callbacks.on_change is not None:
            self.callbacks.on_change(new_value)

    def has_valid_value(self) -> bool:
        """Return True if the value is valid, i.e. it is not Unspecified, Error, or Invalid"""
        return not isinstance(self.value, (Unspecified, Error, Invalid))

    def get_actual_value(self) -> DataType:
        """Returns the actual value of the data, or raises an exception if the value is Unspecified or Error or Invalid
        When we are inside a callback, we can be sure that the value is of the correct type, so we can call this method
        instead of accessing the value directly and checking for Unspecified or Error.
        """
        if isinstance(self.value, Unspecified):
            raise ValueError("Cannot get value of Unspecified")
        elif isinstance(self.value, Error):
            raise ValueError("Cannot get value of Error")
        elif isinstance(self.value, Invalid):
            raise ValueError(f"Invalid value: {self.value} ({self.value.error_message})")
        else:
            return self.value

    def get_actual_or_invalid_value(self) -> DataType:
        """Returns the actual value of the data, or raises an exception if the value is Unspecified or Error"""
        if isinstance(self.value, Unspecified):
            raise ValueError("Cannot get value of Unspecified")
        elif isinstance(self.value, Error):
            raise ValueError("Cannot get value of Error")
        elif isinstance(self.value, Invalid):
            return self.value.invalid_value
        else:
            return self.value

    class _FiatAttributes_Section:  # Dummy class to create a section in the IDE  # noqa
        """
        # ------------------------------------------------------------------------------------------------------------------
        #            Fiat Attributes
        # ------------------------------------------------------------------------------------------------------------------
        """

        pass

    @staticmethod
    def possible_fiat_attributes() -> PossibleFiatAttributes | None:
        """Return the possible fiat attributes for this type, if available.
        Should be overridden in subclasses, when fiat attributes are available.

        It is strongly advised to return a class variable, or a global variable
        to avoid creating a new instance each time this method is called.
        """
        return None

    @final
    def possible_fiat_attributes_with_generic(
        self,
    ) -> tuple[PossibleFiatAttributes | None, PossibleFiatAttributes]:
        descendant_attrs = self.possible_fiat_attributes()
        return descendant_attrs, _ANYDATAWITHGUI_GENERIC_POSSIBLE_FIAT_ATTRIBUTES

    @property
    def fiat_attributes(self) -> FiatAttributes:
        return self._fiat_attributes

    def merge_fiat_attributes(self, fiat_attrs: FiatAttributes) -> None:
        """Merge fiat attributes with the existing ones"""
        if len(fiat_attrs) == 0:
            return
        possible_fiat_attrs, _generic_possible_fiat_attrs = self.possible_fiat_attributes_with_generic()

        # Create a version that holds all fiat attributes
        all_possible_fiat_attrs = copy.deepcopy(_generic_possible_fiat_attrs)
        if possible_fiat_attrs is not None:
            all_possible_fiat_attrs.merge_attributes(copy.copy(possible_fiat_attrs))

        all_possible_fiat_attrs.raise_exception_if_bad_fiat_attrs(fiat_attrs)

        self.fiat_attributes.update(fiat_attrs)
        self._handle_generic_attrs()
        if self.callbacks.on_fiat_attributes_changed is not None:
            self.callbacks.on_fiat_attributes_changed(self.fiat_attributes)

    def _handle_generic_attrs(self) -> None:
        """Handle generic fiat attributes"""
        if "label" in self.fiat_attributes:
            self.label = self.fiat_attributes["label"]
        if "tooltip" in self.fiat_attributes:
            self.tooltip = self.fiat_attributes["tooltip"]
        if "validator" in self.fiat_attributes:
            validator = self.fiat_attributes["validator"]
            if not callable(validator):
                raise ValueError("validator is not a callable for parameter output")
            self.callbacks.validators.append(validator)
        if "edit_collapsible" in self.fiat_attributes:
            self.callbacks.edit_collapsible = self.fiat_attributes["edit_collapsible"]
        if "present_collapsible" in self.fiat_attributes:
            self.callbacks.present_collapsible = self.fiat_attributes["present_collapsible"]
        if "present_detachable" in self.fiat_attributes:
            self.callbacks.present_detachable = self.fiat_attributes["present_detachable"]
        if "edit_detachable" in self.fiat_attributes:
            self.callbacks.edit_detachable = self.fiat_attributes["edit_detachable"]

    @staticmethod
    def propagate_label_and_tooltip(a: "AnyDataWithGui[Any]", b: "AnyDataWithGui[Any]") -> None:
        """Propagate label and tooltip from one AnyDataWithGui to another
        Meant to be used with CompositeGui
        """
        if a.label is None:
            a.label = b.label
        if a.tooltip is None:
            a.tooltip = b.tooltip
        if b.label is None:
            b.label = a.label
        if b.tooltip is None:
            b.tooltip = a.tooltip

    class _Gui_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # ------------------------------------------------------------------------------------------------------------------
        #            Gui sections
        #      (Can also be used outside a function Node)
        # ------------------------------------------------------------------------------------------------------------------
        """

    def sub_items_can_collapse(self, _present_or_edit: PresentOrEdit) -> bool:
        """Overwrite this in derived classes if they provide multiple sub-items that can be collapsed"""
        return False

    def sub_items_collapse_or_expand(self, _collapse_or_expand: CollapseOrExpandChildren) -> None:
        """Overwrite this in derived classes if they provide multiple sub-items that can be collapsed"""
        return

    def sub_items_will_collapse_or_expand(self, _present_or_edit: PresentOrEdit) -> CollapseOrExpandChildren:
        """Overwrite this in derived classes if they provide multiple sub-items that can be collapsed"""
        return self.CollapseOrExpandChildren.collapse

    def _show_collapse_sub_items_buttons(self, present_or_edit: PresentOrEdit) -> None:
        if not get_fiat_config().any_gui_with_data_settings().show_collapse_button:
            return
        icon = icons_fontawesome_6.ICON_FA_COMPRESS
        new_expanded_state = self.sub_items_will_collapse_or_expand(present_or_edit)
        tooltip = str(new_expanded_state.value)
        if imgui.button(icon):
            self.sub_items_collapse_or_expand(new_expanded_state)
        fiat_osd.set_widget_tooltip(tooltip)

    def _show_collapse_button(self) -> None:
        if not get_fiat_config().any_gui_with_data_settings().show_collapse_button:
            return
        icon = icons_fontawesome_6.ICON_FA_CARET_DOWN if self._expanded else icons_fontawesome_6.ICON_FA_CARET_RIGHT
        tooltip = "Collapse" if self._expanded else "Expand"
        if imgui.button(icon):
            self._expanded = not self._expanded
        fiat_osd.set_widget_tooltip(tooltip)

    def _show_copy_to_clipboard_button(self) -> None:
        if not get_fiat_config().any_gui_with_data_settings().show_clipboard_button:
            return
        if not self.callbacks.clipboard_copy_possible:
            return
        if isinstance(self.value, (Error, Unspecified, Invalid)):
            return
        with fontawesome_6_ctx():
            if imgui.button(icons_fontawesome_6.ICON_FA_COPY):
                clipboard_str = self.datatype_value_to_clipboard_str(self.value)
                imgui.set_clipboard_text(clipboard_str)
            fiat_osd.set_widget_tooltip("Copy value to clipboard")

    def can_collapse_present(self, is_expand_disabled: bool) -> bool:
        if is_expand_disabled:
            return False
        if isinstance(self.value, (Unspecified, Error)):
            return False
        return self.callbacks.present_collapsible

    def can_collapse_edit(self, is_expand_disabled: bool) -> bool:
        if is_expand_disabled:
            return False
        if isinstance(self.value, (Unspecified, Error)):
            return False
        return self.callbacks.edit_collapsible

    def can_edit_on_header_line(self) -> bool:
        has_small_edit = self.callbacks.edit is not None and not self.callbacks.edit_collapsible
        return has_small_edit

    def can_present_on_header_line(self) -> bool:
        # we do not test self.callbacks.present is None because if not provided, it will be presented with str()
        has_small_present = not self.callbacks.present_collapsible
        return has_small_present

    def _can_edit_on_next_lines_if_expanded(self, is_expand_disabled: bool) -> bool:
        if is_expand_disabled:
            return False
        is_datatype_or_invalid = not isinstance(self.value, (Unspecified, Error))
        has_callback = self.callbacks.edit is not None
        # collapsible = self.callbacks.edit_collapsible
        return has_callback and is_datatype_or_invalid

    def _can_present_detachable(self) -> bool:
        if not self.callbacks.present_detachable:
            return False
        if isinstance(self.value, (Unspecified, Error, Invalid)):
            return False
        if self.callbacks.present is None:
            return False
        return True

    def _can_edit_detachable(self) -> bool:
        if not self.callbacks.edit_detachable:
            return False
        if isinstance(self.value, (Unspecified, Error, Invalid)):
            return False
        if self.callbacks.edit is None:
            return False
        return True

    def _can_present_on_next_lines_if_expanded(self, is_expand_disabled: bool) -> bool:
        if is_expand_disabled:
            return False
        # we do not test self.callbacks.present is None because if not provided, it will be presented with str()
        is_datatype_or_invalid = not isinstance(self.value, (Unspecified, Error))
        # collapsible = self.callbacks.present_collapsible
        return is_datatype_or_invalid

    def _is_editing_on_next_lines(self, is_expand_disabled: bool) -> bool:
        if is_expand_disabled:
            return False
        if not self.callbacks.edit_collapsible:
            return False
        return self._expanded and self._can_edit_on_next_lines_if_expanded(is_expand_disabled)

    def _is_presenting_on_next_lines(self, is_expand_disabled: bool) -> bool:
        if is_expand_disabled:
            return False
        if not self.callbacks.present_collapsible:
            return False
        return self._expanded and self._can_present_on_next_lines_if_expanded(is_expand_disabled)

    def _popup_window_name(self, params: GuiHeaderLineParams[DataType], present_or_edit: PresentOrEdit) -> str:
        window_name = ""
        if self.label is not None:
            window_name += f"{self.label}"
        if len(params.parent_name) > 0:
            if len(window_name) > 0:
                window_name += "    -    "
            window_name += params.parent_name
        window_name += f"   ({present_or_edit.value})"
        return window_name

    def _gui_present_header_line(self, params: GuiHeaderLineParams[DataType]) -> None:
        """Present the value as a string in one line, or as a widget if it fits on one line"""

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
            if self.label is not None:
                label_color = (
                    imgui.get_style().color_(imgui.Col_.text) if self.label_color is None else self.label_color
                )
                _draw_label_with_max_width(self.label, label_color, self.tooltip, self.status_tooltip)
            # Expand button
            if self.can_collapse_present(params.is_expand_disabled) and not params.is_expand_disabled:
                self._show_collapse_button()
                if self._expanded:
                    if self.sub_items_can_collapse(self.PresentOrEdit.present):
                        self._show_collapse_sub_items_buttons(self.PresentOrEdit.present)

            # Value as string or widget
            if not self._is_presenting_on_next_lines(params.is_expand_disabled):
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
                        text_maybe_truncated(as_str, get_fiat_config().style.str_truncation.present_header_line)
                elif isinstance(self.value, Error):
                    imgui.text_colored(get_fiat_config().style.color_as_vec4(FiatColorType.ValueWithError), "Error")
                else:  # if isinstance(self.value, (Invalid, DataType))
                    value = self.get_actual_or_invalid_value()
                    can_present_on_header_line = self.can_present_on_header_line()
                    if can_present_on_header_line:
                        if self.callbacks.present is not None:
                            with imgui_ctx.begin_vertical(
                                "callback_present"
                            ):  # Some widgets expect a standard vertical layout
                                self.callbacks.present(value)
                        else:
                            as_str = self.datatype_value_to_str(value)
                            text_maybe_truncated(as_str, get_fiat_config().style.str_truncation.present_header_line)
                    else:
                        as_str = self.datatype_value_to_str(value)
                        text_maybe_truncated(as_str, get_fiat_config().style.str_truncation.present_header_line)

            #
            # Right Side:
            #   * open in popup button
            #   * clipboard button
            #   * suffix_gui (might contain a node output pin when used in a function node)
            imgui.spring()  # Align the rest to the right
            if self._can_present_detachable():

                def gui_present_detached() -> None:
                    self._gui_present_next_lines(in_popup=True, is_expand_disabled=params.is_expand_disabled)

                detached_window_params = fiat_osd.DetachedWindowParams(
                    unique_id="##present_in_popup" + str(id(self)),
                    window_name=self._popup_window_name(params, self.PresentOrEdit.present),
                    gui_function=gui_present_detached,
                )
                fiat_osd.show_void_detached_window_button(detached_window_params)
            # clipboard button
            if params.show_clipboard_button:
                self._show_copy_to_clipboard_button()
            # suffix_gui
            if params.suffix_gui is not None:
                params.suffix_gui()

        # Optional second line: invalid value info
        if isinstance(self.value, Invalid):
            text_maybe_truncated(
                icons_fontawesome_6.ICON_FA_TRIANGLE_EXCLAMATION + " " + self.value.error_message,
                get_fiat_config().style.str_truncation.invalid_value_message,
                color=get_fiat_config().style.color_as_vec4(FiatColorType.Invalid),
            )

    def _gui_edit_header_line(self, params: GuiHeaderLineParams[DataType]) -> bool:
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
            if self.label is not None:
                label_color = (
                    imgui.get_style().color_(imgui.Col_.text) if self.label_color is None else self.label_color
                )
                _draw_label_with_max_width(self.label, label_color, self.tooltip, self.status_tooltip)
            # Expand button
            if self.can_collapse_edit(params.is_expand_disabled):
                self._show_collapse_button()
                if self._expanded:
                    if self.sub_items_can_collapse(self.PresentOrEdit.edit):
                        self._show_collapse_sub_items_buttons(self.PresentOrEdit.edit)

            # Value as string or widget
            if not self._is_editing_on_next_lines(params.is_expand_disabled):
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
                        text_maybe_truncated(as_str, get_fiat_config().style.str_truncation.present_header_line)
                elif isinstance(self.value, Error):
                    imgui.text_colored(get_fiat_config().style.color_as_vec4(FiatColorType.ValueWithError), "Error")
                else:  # if isinstance(self.value, (Invalid, DataType))
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
                        text_maybe_truncated(as_str, get_fiat_config().style.str_truncation.present_header_line)

            #
            # Right Side:
            #   * open in popup button
            #   * Clipboard
            #   * Reset to unspecified or to default value
            imgui.spring()  # Align the rest to the right
            # popup button
            if self._can_edit_detachable():

                def gui_edit_detached() -> bool:
                    if isinstance(self.value, Unspecified):
                        # If unspecified, set to default value before editing in popup
                        if self.can_construct_default_value():
                            logging.warning("Value unspecified: setting to default value before editing in popup")
                            self.value = self.construct_default_value()
                    # Edit in popup
                    changed = self._gui_edit_next_lines(in_popup=True, is_expand_disabled=params.is_expand_disabled)

                    return changed

                detached_gui_edit = fiat_osd.DetachedWindowParams(
                    unique_id="##edit_in_popup" + str(id(self)),
                    window_name=self._popup_window_name(params, self.PresentOrEdit.edit),
                    gui_function=gui_edit_detached,
                )
                fiat_osd.show_bool_detached_window_button(detached_gui_edit)

                # If the user edits the input value in a detached window
                if fiat_osd.get_detached_window_bool_return(detached_gui_edit):
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

        # Optional second line: invalid value info
        if isinstance(self.value, Invalid):
            text_maybe_truncated(
                icons_fontawesome_6.ICON_FA_TRIANGLE_EXCLAMATION + " " + self.value.error_message,
                get_fiat_config().style.str_truncation.invalid_value_message,
                color=get_fiat_config().style.color_as_vec4(FiatColorType.Invalid),
            )

        return changed

    def _show_set_unspecified_or_default_button(self) -> bool:
        can_set_default_value = False
        warn_no_default_provider = False
        can_set_unspecified = False
        if isinstance(self.value, (Unspecified, Error)):
            # if unspecified, provide "+" to set to default provider value
            if self.can_construct_default_value():
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
                assert self.can_construct_default_value()
                self.value = self.construct_default_value()
                changed = True
            fiat_osd.set_widget_tooltip("Set to default value")
        if warn_no_default_provider:
            imgui.text_colored(
                get_fiat_config().style.color_as_vec4(FiatColorType.Invalid),
                icons_fontawesome_6.ICON_FA_TRIANGLE_EXCLAMATION,
            )
            fiat_osd.set_widget_tooltip("No default value provider")

        return changed

    def _gui_edit_next_lines(self, in_popup: bool, is_expand_disabled: bool) -> bool:
        # Line 2 and beyond: edit (if one line present is impossible)
        changed = False
        can_edit = (
            self._is_editing_on_next_lines(is_expand_disabled)
            if not in_popup
            else self._can_edit_on_next_lines_if_expanded(is_expand_disabled)
        )
        if can_edit:
            assert self.callbacks.edit is not None
            with imgui_ctx.begin_horizontal("left_margin_edit"):
                margin_size = hello_imgui.em_size(get_fiat_config().style.indentation_em)
                imgui.dummy(ImVec2(margin_size, 0))
                value = self.get_actual_or_invalid_value()
                with imgui_ctx.begin_vertical("callback_edit"):
                    changed, new_value = self.callbacks.edit(value)
                    if changed:
                        self.value = new_value  # this will call the setter and trigger the validation
        return changed

    def _gui_present_next_lines(self, in_popup: bool, is_expand_disabled: bool) -> None:
        # Line 2 and beyond: present (if one line present is impossible)
        can_present = (
            self._is_presenting_on_next_lines(is_expand_disabled)
            if not in_popup
            else self._can_present_on_next_lines_if_expanded(is_expand_disabled)
        )
        if can_present:
            with imgui_ctx.begin_horizontal("left_margin_present"):
                margin_size = hello_imgui.em_size(1.5)
                imgui.dummy(ImVec2(margin_size, 0))
                value = self.get_actual_or_invalid_value()
                with imgui_ctx.begin_vertical("callback_present"):
                    if self.callbacks.present is not None:
                        self.callbacks.present(value)
                    else:
                        as_str = self.datatype_value_to_str(value)
                        text_maybe_truncated(as_str, get_fiat_config().style.str_truncation.present_next_lines)

    def gui_present_customizable(self, params: GuiHeaderLineParams[DataType]) -> None:
        """Present the value using either the present callback or the default str conversion
        May present on one line (if possible) or on multiple lines with an expand button
        """
        with imgui_ctx.push_obj_id(self):
            with fontawesome_6_ctx():
                self._gui_present_header_line(params)
                self._gui_present_next_lines(in_popup=False, is_expand_disabled=params.is_expand_disabled)

    # def gui_present(self, label: str) -> None:
    def gui_present(self) -> None:
        params = GuiHeaderLineParams[DataType](parent_name="")
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
                if self._gui_edit_next_lines(in_popup=False, is_expand_disabled=params.is_expand_disabled):
                    changed = True

        return changed

    def gui_edit(self) -> bool:
        params = GuiHeaderLineParams[DataType](parent_name="")
        return self.gui_edit_customizable(params)

    class _Callbacks_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # ------------------------------------------------------------------------------------------------------------------
        #            Callbacks sections
        # ------------------------------------------------------------------------------------------------------------------
        """

    def set_edit_callback(
        self,
        edit_callback: DataEditFunction[DataType],
        *,
        edit_collapsible: bool | None = None,
    ) -> None:
        """Helper function to set the edit callback from a free function"""
        self.callbacks.edit = edit_callback
        if edit_collapsible is not None:
            self.callbacks.edit_collapsible = edit_collapsible

    def set_present_callback(
        self,
        present_callback: DataPresentFunction[DataType],
        *,
        present_collapsible: bool | None = None,
    ) -> None:
        """Helper function to set the present custom callback from a free function"""
        self.callbacks.present = present_callback
        if present_collapsible is not None:
            self.callbacks.present_collapsible = present_collapsible

    def add_validator_callback(self, cb: Callable[[DataType], DataType]) -> None:
        self.callbacks.validators.append(cb)

    def _Serialization_Section(self) -> None:
        """
        # ------------------------------------------------------------------------------------------------------------------
        #            Serialization and deserialization
        # ------------------------------------------------------------------------------------------------------------------
        """

    @final
    def call_save_to_dict(self, value: DataType | Unspecified | Error | Invalid[DataType]) -> JsonDict:
        """Serialize the value to a dictionary

        Will call the save_to_dict callback if set, otherwise will use the default serialization, when available.
        A default serialization is available for primitive types, tuples, and Pydantic models.

        (This is how fiatlight saves the data to a JSON file)

        Do not override these methods in descendant classes!
        """
        if isinstance(value, (Unspecified, Invalid)):
            # We do not save Unspecified or Invalid,
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
            logging.warning(
                f"""
            AnyDataWithGui.call_save_to_dict():
                Cannot serialize type {typename_utils.base_typename(self._type)}
                with value =
                   {value}
            """
            )
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

    class _Utilities_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # ------------------------------------------------------------------------------------------------------------------
        #            Utilities
        # ------------------------------------------------------------------------------------------------------------------
        """

    def can_construct_default_value(self) -> bool:
        if self.callbacks.default_value_provider is not None:
            return True
        if self._type is None:
            return False
        try:
            _ = self._type()
            return True
        except TypeError:
            return False
        except ValueError:
            return False

    def construct_default_value(self) -> DataType:
        if self._type is None and self.callbacks.default_value_provider is None:
            raise ValueError("Cannot construct default value: Please call can_construct_default_value before!")
        if self.callbacks.default_value_provider is not None:
            return self.callbacks.default_value_provider()
        assert self._type is not None
        return self._type()

    def datatype_qualified_name(self) -> str:
        if self._type is None:
            return "Unknown type!"
        return typename_utils.fully_qualified_typename(self._type)

    def datatype_basename(self) -> str:
        if self._type is None:
            return "Unknown type!"
        return typename_utils.base_typename(self._type)

    def datatype_base_and_qualified_name(self) -> str:
        if self._type is None:
            return "Unknown type!"
        return typename_utils.base_and_qualified_typename(self._type)

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

    def datatype_value_to_clipboard_str(self, value: DataType) -> str:
        """Convert the value to a string for the clipboard
        Uses either the clipboard_copy_str callback, or the default str conversion
        """
        if isinstance(value, Unspecified):
            return "Unspecified"
        elif isinstance(value, Error):
            return "Error"
        elif isinstance(value, Invalid):
            return "Invalid"
        else:
            if self.callbacks.clipboard_copy_str is not None:
                return self.callbacks.clipboard_copy_str(value)
            else:
                return self.datatype_value_to_str(value)

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


class AnyDataWithGui_UnregisteredType(AnyDataWithGui[Any], Generic[DataType]):
    """AnyDataWithGui_UnregisteredType: a GUI associated to a type that is not registered in the Fiatlight framework.

    Use sparingly, as such a data type cannot do much, and is not very useful.
    """

    unregistered_typename: str

    def __init__(self, typename: str, data_type: Type[DataType] | None) -> None:
        super().__init__(data_type)
        self.unregistered_typename = typename


def toggle_expanded_state_on_guis(guis: list[AnyDataWithGui[Any]]) -> None:
    has_one_expanded = False
    for gui in guis:
        if gui._expanded:
            has_one_expanded = True
    new_expanded_state = not has_one_expanded
    for gui in guis:
        gui._expanded = new_expanded_state
