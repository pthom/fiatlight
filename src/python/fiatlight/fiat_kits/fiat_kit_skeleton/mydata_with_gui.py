from fiatlight.fiat_core.possible_custom_attributes import PossibleCustomAttributes
from fiatlight.fiat_types import CustomAttributesDict, JsonDict
from fiatlight.fiat_core.any_data_with_gui import AnyDataWithGui
from imgui_bundle import imgui
from fiatlight.fiat_kits.fiat_kit_skeleton.mydata import Mydata

from fiatlight.fiat_kits.fiat_kit_skeleton.mydata_presenter import MydataPresenter


class DataFramePossibleCustomAttributes(PossibleCustomAttributes):
    # Here we will add all the possible custom attributes for presentation and other options.
    def __init__(self) -> None:
        super().__init__("DataFrameWithGui")


_DATAFRAME_POSSIBLE_CUSTOM_ATTRIBUTES = DataFramePossibleCustomAttributes()


class MydataWithGui(AnyDataWithGui[Mydata]):
    my_presenter: MydataPresenter

    def __init__(self) -> None:
        super().__init__(Mydata)
        self.my_presenter = MydataPresenter()

        # present callbacks
        self.callbacks.present_str = self.present_str
        self.callbacks.present_custom = self.present_custom
        self.callbacks.present_custom_popup_required = False
        self.callbacks.present_custom_popup_possible = True
        # edit callbacks
        self.callbacks.edit = self.edit
        self.callbacks.edit_popup_required = False
        self.callbacks.edit_popup_possible = False
        # default value provider
        self.callbacks.default_value_provider = self.default_value_provider
        # on_change callback
        self.callbacks.on_change = self.on_change
        self.callbacks.on_heartbeat = self.on_heartbeat
        # custom attributes
        self.callbacks.on_custom_attrs_changed = self.on_custom_attrs_changed
        # serialization and deserialization of presentation options
        self.callbacks.save_gui_options_to_json = self.save_gui_options_to_json
        self.callbacks.load_gui_options_from_json = self.load_gui_options_from_json
        # serialization and deserialization of the data itself
        self.callbacks.save_to_dict = self._save_to_dict
        self.callbacks.load_from_dict = self._load_from_dict
        # clipboard
        self.callbacks.clipboard_copy_str = self.clipboard_copy_str
        self.callbacks.clipboard_copy_possible = True

    @staticmethod
    def _PresentCallbacksSection() -> None:  # Dummy function to create a section in the IDE # noqa
        """
        # --------------------------------------------------------------------------------------------
        #        Present callbacks
        # Here, we present the Data
        # There can be two different presentations depending on whether we are inside a pop-up or inside a node.
        # --------------------------------------------------------------------------------------------
        """
        pass

    def present_str(self, value: Mydata) -> str:
        return f"Mydata: {value}"

    def present_custom(self, value: Mydata) -> None:
        imgui.text("present_custom")
        # We should probably use a distinct class such as DataFramePresenter here

    @staticmethod
    def _EditCallbacksSection() -> None:
        """
        # --------------------------------------------------------------------------------------------
        #        Edit callbacks
        # --------------------------------------------------------------------------------------------
        """
        pass

    def edit(self, value: Mydata) -> tuple[bool, Mydata]:
        # Here, we edit the data.
        # There can be two different presentations, depending on whether we are inside a pop-up or inside a node.
        return False, value

    @staticmethod
    def _DefaultValueProviderSection() -> None:
        """
        # --------------------------------------------------------------------------------------------
        #        Default value provider
        # --------------------------------------------------------------------------------------------
        """
        pass

    @staticmethod
    def default_value_provider() -> Mydata:
        # Here we provide a default value for the data.
        return Mydata(x=0)

    @staticmethod
    def _OnChangeSection() -> None:
        """
        # --------------------------------------------------------------------------------------------
        #        On Change
        # --------------------------------------------------------------------------------------------
        """
        pass

    def on_change(self, value: Mydata) -> None:
        # Here we should transmit the new data frame to the presenter
        # (if we use a separate presenter)
        pass

    def on_heartbeat(self) -> bool:
        # Probably nothing to do here.
        return False

    @staticmethod
    def _CustomAttributesSection() -> None:
        """
        # --------------------------------------------------------------------------------------------
        #        Custom Attributes
        # --------------------------------------------------------------------------------------------
        """
        pass

    @staticmethod
    def possible_custom_attributes() -> PossibleCustomAttributes | None:
        # This is a method which we inherit from AnyDataWithGui.
        return _DATAFRAME_POSSIBLE_CUSTOM_ATTRIBUTES

    def on_custom_attrs_changed(self, custom_attrs: CustomAttributesDict) -> None:
        # Here we should update the presenter with the new custom attributes
        pass

    @staticmethod
    def _SerializationAndDeserializationSection() -> None:
        """
        # --------------------------------------------------------------------------------------------
        #        Serialization and deserialization
        # --------------------------------------------------------------------------------------------
        """
        pass

    def save_gui_options_to_json(self) -> JsonDict:
        # Here we should save the GUI presentation options to a JSON dict
        # (columns width, etc.)
        # This will ask the presenter to save its params
        return {}

    def load_gui_options_from_json(self, json_dict: JsonDict) -> None:
        # Here we should load the GUI presentation options from a JSON dict
        # (columns width, etc.)
        # This will ask the presenter to load its params
        pass

    def _save_to_dict(self, value: Mydata) -> JsonDict:
        # Here we could save the data frame to a JSON dict,
        # But this is probably a bad idea, so we will probably dump this method or return an empty dict
        return {}

    def _load_from_dict(self, json_dict: JsonDict) -> Mydata:
        # Here we could load the data frame from a JSON dict,
        # But this is probably a bad idea, so we will probably dump this method or return an empty data frame
        raise NotImplementedError()

    @staticmethod
    def _ClipboardSection() -> None:
        """
        # --------------------------------------------------------------------------------------------
        #        Clipboard
        # --------------------------------------------------------------------------------------------
        """
        pass

    def clipboard_copy_str(self, value: Mydata) -> str:
        return "Mydata: clipboard_copy_str() not implemented yet"
