from fiatlight.fiat_types.function_types import DataType
from fiatlight.fiat_core.any_data_with_gui import AnyDataWithGui
from fiatlight.fiat_types.error_types import Error, ErrorValue, Unspecified
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

    def save_to_json(self) -> JsonDict:
        data_json = self.data_with_gui.save_to_json()
        data_dict = {"name": self.name, "data": data_json}
        return data_dict

    def load_from_json(self, json_data: JsonDict) -> None:
        if json_data["name"] != self.name:
            raise ValueError(f"Expected name {self.name}, got {json_data['name']}")
        if "data" in json_data:
            self.data_with_gui.load_from_json(json_data["data"])

    def get_value_or_default(self) -> DataType | Unspecified | Error:
        param_value = self.data_with_gui.value
        if isinstance(param_value, Error):
            return ErrorValue
        elif isinstance(param_value, Unspecified):
            return self.default_value
        else:
            return self.data_with_gui.value
