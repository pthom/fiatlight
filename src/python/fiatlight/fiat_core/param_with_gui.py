from fiatlight.fiat_types.base_types import DataType
from fiatlight.fiat_core.any_data_with_gui import AnyDataWithGui
from fiatlight.fiat_types.error_types import Error, ErrorValue, Unspecified, Invalid
from fiatlight.fiat_types.base_types import JsonDict

from enum import Enum
from dataclasses import dataclass
from typing import Generic


class ParamKind(Enum):
    PositionalOnly = 0
    PositionalOrKeyword = 1
    KeywordOnly = 3


@dataclass
class ParamWithGui(Generic[DataType]):
    name: str
    data_with_gui: AnyDataWithGui[DataType]
    param_kind: ParamKind
    default_value: DataType | Unspecified

    def __post_init__(self) -> None:
        default_value = self.default_value
        if not isinstance(default_value, Unspecified):
            self.data_with_gui.callbacks.default_value_provider = lambda: default_value

    def save_self_value_to_dict(self) -> JsonDict:
        data_json = self.data_with_gui.call_save_to_dict(self.data_with_gui.value)
        data_dict = {"name": self.name, "data": data_json}
        return data_dict

    def load_self_value_from_dict(self, json_data: JsonDict) -> None:
        if json_data["name"] != self.name:
            raise ValueError(f"Expected name {self.name}, got {json_data['name']}")
        if "data" in json_data:
            self.data_with_gui.value = self.data_with_gui.call_load_from_dict(json_data["data"])

    def get_value_or_default(self) -> DataType | Unspecified | Error | Invalid[DataType]:
        param_value = self.data_with_gui.value
        if isinstance(param_value, Error):
            return ErrorValue
        elif isinstance(param_value, Unspecified):
            return self.default_value
        elif isinstance(param_value, Invalid):
            return param_value
        else:  # if isinstance(param_value, DataType):
            return param_value
