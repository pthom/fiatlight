from fiatlight.fiat_types import CustomAttributesDict, JsonDict
from fiatlight.fiat_core.any_data_with_gui import AnyDataWithGui
from fiatlight.fiat_core.possible_custom_attributes import PossibleCustomAttributes
from fiatlight.fiat_kits.fiat_dataframe.dataframe_presenter import _DATAFRAME_POSSIBLE_CUSTOM_ATTRIBUTES
import pandas as pd

from fiatlight.fiat_kits.fiat_dataframe.dataframe_presenter import DataFramePresenter


class DataFrameWithGui(AnyDataWithGui[pd.DataFrame]):
    dataframe_presenter: DataFramePresenter

    def __init__(self) -> None:
        super().__init__(pd.DataFrame)
        self.dataframe_presenter = DataFramePresenter()

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
        # Here, we present the DataFrame as a table.
        # There are two different presentations depending on whether we are inside a pop-up or inside a node.
        # --------------------------------------------------------------------------------------------
        """
        pass

    def present_str(self, value: pd.DataFrame) -> str:
        return self.dataframe_presenter.present_str(value)

    def present_custom(self, value: pd.DataFrame) -> None:
        self.dataframe_presenter.present_custom(value)

    @staticmethod
    def _EditCallbacksSection() -> None:
        """
        # --------------------------------------------------------------------------------------------
        #        Edit callbacks
        # --------------------------------------------------------------------------------------------
        """
        pass

    def edit(self, value: pd.DataFrame) -> tuple[bool, pd.DataFrame]:
        # We will probably not be able to edit data frames.
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
    def default_value_provider() -> pd.DataFrame:
        # Here, we provide an example data frame to the user,
        # using the Titanic dataset from the Data Science Dojo repository.
        # (widely used in data science tutorials)
        url = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
        try:
            df = pd.read_csv(url)
        except Exception as e:
            print(f"Error loading sample dataset: {e}")
            df = pd.DataFrame()  # Return an empty DataFrame in case of failure
        return df

    @staticmethod
    def _OnChangeSection() -> None:
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
        self.dataframe_presenter.on_custom_attrs_changed(custom_attrs)

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

    @staticmethod
    def _ClipboardSection() -> None:
        """
        # --------------------------------------------------------------------------------------------
        #        Clipboard
        # --------------------------------------------------------------------------------------------
        """
        pass

    def clipboard_copy_str(self, value: pd.DataFrame) -> str:
        # Is there an easy way to export a clipboard-friendly version of the data frame?
        return value.to_string()


def register_gui() -> None:
    from fiatlight.fiat_togui.to_gui import register_type

    register_type(pd.DataFrame, DataFrameWithGui)


# Register the GUI at startup
register_gui()
