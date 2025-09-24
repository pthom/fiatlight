from fiatlight.fiat_types import FiatAttributes, JsonDict
from fiatlight.fiat_core.any_data_with_gui import AnyDataWithGui
from imgui_bundle import imgui
from fiatlight.fiat_kits.fiat_kit_skeleton.mydata import Mydata

from fiatlight.fiat_kits.fiat_kit_skeleton.mydata_presenter import MydataPresenter, MydataPossibleFiatAttributes


class MydataWithGui(AnyDataWithGui[Mydata]):
    my_presenter: MydataPresenter

    def __init__(self) -> None:
        super().__init__(Mydata)
        self.my_presenter = MydataPresenter()

        # present callbacks
        self.callbacks.present_str = self.present_str
        self.callbacks.present = self.present
        # edit callbacks
        self.callbacks.edit = self.edit
        # default value provider
        self.callbacks.default_value_provider = self.default_value_provider
        # on_change callback
        self.callbacks.on_change = self.on_change
        self.callbacks.on_heartbeat = self.on_heartbeat
        # fiat attributes
        self.callbacks.on_fiat_attributes_changed = self.on_fiat_attributes_changes
        # serialization and deserialization of presentation options
        self.callbacks.save_gui_options_to_json = self.save_gui_options_to_json
        self.callbacks.load_gui_options_from_json = self.load_gui_options_from_json
        # serialization and deserialization of the data itself
        self.callbacks.save_to_dict = self._save_to_dict
        self.callbacks.load_from_dict = self._load_from_dict
        # clipboard
        self.callbacks.clipboard_copy_str = self.clipboard_copy_str
        self.callbacks.clipboard_copy_possible = True

    class _PresentCallbacksSection:  # Dummy class to create a section in the IDE # noqa
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

    def present(self, value: Mydata) -> None:
        imgui.text("present")
        # We should probably use a distinct class such as DataFramePresenter here

    class _EditCallbacksSection:  # Dummy class to create a section in the IDE # noqa
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

    class _DefaultValueProviderSection:  # Dummy class to create a section in the IDE # noqa
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

    class _OnChangeSection:  # Dummy class to create a section in the IDE # noqa
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

    class _FiatAttributesSection:  # Dummy class to create a section in the IDE # noqa
        """
        # --------------------------------------------------------------------------------------------
        #        Fiat Attributes
        # --------------------------------------------------------------------------------------------
        """

        pass

    @staticmethod
    def possible_fiat_attributes() -> MydataPossibleFiatAttributes | None:
        return MydataPresenter.possible_fiat_attributes()

    def on_fiat_attributes_changes(self, fiat_attrs: FiatAttributes) -> None:
        # Here we should update the presenter with the new fiat attributes
        pass

    class _SerializationAndDeserializationSection:  # Dummy class to create a section in the IDE # noqa
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

    class _ClipboardSection:  # Dummy class to create a section in the IDE # noqa
        """
        # --------------------------------------------------------------------------------------------
        #        Clipboard
        # --------------------------------------------------------------------------------------------
        """

        pass

    def clipboard_copy_str(self, value: Mydata) -> str:
        return "Mydata: clipboard_copy_str() not implemented yet"


def register_gui() -> None:
    from fiatlight.fiat_togui.gui_registry import register_type

    register_type(Mydata, MydataWithGui)


# Register the GUI at startup
register_gui()
