from fiatlight.fiat_types import FiatAttributes, JsonDict
from fiatlight.fiat_core.any_data_with_gui import AnyDataWithGui
from fiatlight.fiat_core.possible_fiat_attributes import PossibleFiatAttributes
from fiatlight.fiat_kits.fiat_dataframe.dataframe_presenter import _DATAFRAME_POSSIBLE_FIAT_ATTRIBUTES
import pandas as pd

from fiatlight.fiat_kits.fiat_dataframe.dataframe_presenter import DataFramePresenter


class DataFrameWithGui(AnyDataWithGui[pd.DataFrame]):
    """A class to present a pandas DataFrame in the GUI, with pagination and other features. Open in a pop-up for more features"""

    dataframe_presenter: DataFramePresenter

    def __init__(self) -> None:
        super().__init__(pd.DataFrame)
        self.dataframe_presenter = DataFramePresenter()

        # present callbacks
        self.callbacks.present_str = self.present_str
        self.callbacks.present = self.present
        self.callbacks.present_collapsible = True
        # edit callbacks: there is no edit, actually!
        self.callbacks.edit = self.edit
        self.callbacks.edit_collapsible = False
        # default value provider: None
        self.callbacks.default_value_provider = self.default_value_provider
        # on_change callback
        self.callbacks.on_change = self.on_change
        self.callbacks.on_heartbeat = self.on_heartbeat
        # custom attributes
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

    @staticmethod
    def default_value_provider() -> pd.DataFrame:
        return pd.DataFrame()

    class _PresentCallbacksSection:  # Dummy class to create a section in the IDE # noqa
        """
        # --------------------------------------------------------------------------------------------
        #        Present callbacks
        # Here, we present the DataFrame as a table.
        # There are two different presentations depending on whether we are inside a pop-up or inside a node.
        # --------------------------------------------------------------------------------------------
        """

        pass

    def present_str(self, value: pd.DataFrame) -> str:
        return self.dataframe_presenter.present_str(value)

    def present(self, value: pd.DataFrame) -> None:
        self.dataframe_presenter.present(value)

    class _EditCallbacksSection:
        """
        # --------------------------------------------------------------------------------------------
        #        Edit callbacks
        # --------------------------------------------------------------------------------------------
        """

        pass

    def edit(self, value: pd.DataFrame) -> tuple[bool, pd.DataFrame]:
        # We will probably not be able to edit data frames.
        return False, value

    class _OnChangeSection:
        """
        # --------------------------------------------------------------------------------------------
        #        On Change
        # --------------------------------------------------------------------------------------------
        """

        pass

    def on_change(self, value: pd.DataFrame) -> None:
        self.dataframe_presenter.on_change(value)

    def on_heartbeat(self) -> bool:
        # Probably nothing to do here.
        return False

    class _FiatAttributesSection:
        """
        # --------------------------------------------------------------------------------------------
        #        Fiat Attributes
        # --------------------------------------------------------------------------------------------
        """

        pass

    @staticmethod
    def possible_fiat_attributes() -> PossibleFiatAttributes | None:
        # This is a method which we inherit from AnyDataWithGui.
        return _DATAFRAME_POSSIBLE_FIAT_ATTRIBUTES

    def on_fiat_attributes_changes(self, fiat_attrs: FiatAttributes) -> None:
        self.dataframe_presenter.on_fiat_attributes_changes(fiat_attrs)

    class _SerializationAndDeserializationSection:
        """
        # --------------------------------------------------------------------------------------------
        #        Serialization and deserialization
        # --------------------------------------------------------------------------------------------
        """

        pass

    def save_gui_options_to_json(self) -> JsonDict:
        # Here we should save the GUI presentation options to a JSON dict
        # (columns width, etc.)
        # This will ask the presenter to save DataFramePresenterParams
        return self.dataframe_presenter.save_gui_options_to_json()

    def load_gui_options_from_json(self, json_dict: JsonDict) -> None:
        # Here we should load the GUI presentation options from a JSON dict
        # (columns width, etc.)
        # This will ask the presenter to load DataFramePresenterParams
        self.dataframe_presenter.load_gui_options_from_json(json_dict)

    def _save_to_dict(self, value: pd.DataFrame) -> JsonDict:
        # Here we could save the data frame to a JSON dict,
        # But this is probably a bad idea, so we will probably dump this method or return an empty dict
        return {}

    def _load_from_dict(self, json_dict: JsonDict) -> pd.DataFrame:
        # Here we could load the data frame from a JSON dict,
        # But this is probably a bad idea, so we will probably dump this method or return an empty data frame
        return pd.DataFrame()

    class _ClipboardSection:
        """
        # --------------------------------------------------------------------------------------------
        #        Clipboard
        # --------------------------------------------------------------------------------------------
        """

        pass

    def clipboard_copy_str(self, value: pd.DataFrame) -> str:
        # Is there an easy way to export a clipboard-friendly version of the data frame?
        return self.dataframe_presenter.clipboard_copy_str(value)


def register_gui() -> None:
    from fiatlight.fiat_togui.gui_registry import register_type

    register_type(pd.DataFrame, DataFrameWithGui)


# Register the GUI at startup
register_gui()
