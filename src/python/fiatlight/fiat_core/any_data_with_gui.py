import pydantic

from fiatlight.fiat_types.base_types import (
    JsonDict,
    DataType,
)
from fiatlight.fiat_types.error_types import Error, ErrorValue, Unspecified, UnspecifiedValue, InvalidValue
from fiatlight.fiat_types.function_types import DataPresentFunction, DataEditFunction  # noqa
from .any_data_gui_callbacks import AnyDataGuiCallbacks
from .possible_custom_attributes import PossibleCustomAttributes
from imgui_bundle import imgui
from typing import Generic, Any, Type, final
import logging


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
    def value(self, new_value: DataType | Unspecified | Error) -> None:
        """Set the value of the data. This triggers the on_change callback (if set)"""
        self._value = new_value
        if isinstance(new_value, (Unspecified, Error)):
            return

        # Run validators and return if the value is invalid
        if len(self.callbacks.validate_value) > 0:
            error_messages = []
            for validate_value in self.callbacks.validate_value:
                validation_result = validate_value(new_value)
                if not validation_result.is_valid:
                    error_messages.append(validation_result.error_message)
            if len(error_messages) > 0:
                all_error_messages = " - ".join(error_messages)
                self._value = InvalidValue(error_message=all_error_messages, invalid_value=new_value)
                return

        # Call on_change callback if everything is fine
        if self.callbacks.on_change is not None:
            self.callbacks.on_change(new_value)

    def get_actual_value(self) -> DataType:
        """Returns the actual value of the data, or raises an exception if the value is Unspecified or Error.
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

    @property
    def custom_attrs(self) -> dict[str, Any]:
        return self._custom_attrs

    def merge_custom_attrs(self, custom_attrs: dict[str, Any]) -> None:
        """Merge custom attributes with the existing ones"""
        if len(custom_attrs) == 0:
            return
        possible_custom_attrs = self.possible_custom_attributes()
        if possible_custom_attrs is None:
            raise ValueError(
                f'''
            Cannot set custom attributes for {self._type} in class {self.__class__}
                Please override the possible_custom_attributes() method in the class {self.__class__}
                with the following signature:

                    @staticmethod
                    def possible_custom_attributes() -> PossibleCustomAttributes | None:
                        """Return the possible custom attributes for this type, if available.

                        It is strongly advised to return a class variable, or a global variable
                        to avoid creating a new instance each time this method is called.
                        """
                        return None
            '''
            )

        possible_custom_attrs.raise_exception_if_bad_custom_attrs(custom_attrs)
        self.custom_attrs.update(custom_attrs)
        if self.callbacks.on_custom_attrs_changed is not None:
            self.callbacks.on_custom_attrs_changed(self.custom_attrs)

    def _Callbacks_Section(self) -> None:  # Dummy function to create a section in the IDE # noqa
        """
        # ------------------------------------------------------------------------------------------------------------------
        #            Callbacks sections
        # ------------------------------------------------------------------------------------------------------------------
        """

    def call_edit(self) -> bool:
        """Call the edit callback. Returns True if the value has changed
        If the value is Unspecified or Error, it will return False and display a message in the GUI
        (this method should not be called in this case)
        """
        if isinstance(self.value, (Unspecified, Error)):
            imgui.text("Cannot edit Unspecified or Error")
            return False
        if self.callbacks.edit is not None:
            if isinstance(self.value, InvalidValue):
                changed, new_value = self.callbacks.edit(self.value.invalid_value)
                if changed:
                    self.value = new_value  # this will call the setter and trigger the validation
                return changed
            changed, new_value = self.callbacks.edit(self.value)
            if changed:
                self.value = new_value  # this will call the setter and trigger the validation
            return changed
        else:
            return False

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
            actual_value = self.get_actual_value()
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
