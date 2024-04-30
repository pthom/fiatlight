from fiatlight.fiat_types.base_types import DataType
from fiatlight.fiat_core.any_data_with_gui import AnyDataWithGui

from typing import Generic
from dataclasses import dataclass


@dataclass
class OutputWithGui(Generic[DataType]):
    data_with_gui: AnyDataWithGui[DataType]
