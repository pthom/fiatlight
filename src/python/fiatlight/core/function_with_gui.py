from fiatlight.core import UnspecifiedValue, ErrorValue, Unspecified, Error, JsonDict, DataType
from fiatlight.core.any_data_with_gui import AnyDataWithGui
from typing import Any, List, final, Callable, Optional, Generic
from dataclasses import dataclass
from enum import Enum


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

    def to_json(self) -> JsonDict:
        data_json = self.data_with_gui.to_json()
        data_dict = {"name": self.name, "data": data_json}
        return data_dict

    def fill_from_json(self, json_data: JsonDict) -> None:
        if json_data["name"] != self.name:
            raise ValueError(f"Expected name {self.name}, got {json_data['name']}")
        if "data" in json_data:
            self.data_with_gui.fill_from_json(json_data["data"])

    def get_value_or_default(self) -> DataType | Unspecified | Error:
        param_value = self.data_with_gui.value
        if isinstance(param_value, Error):
            return ErrorValue
        elif isinstance(param_value, Unspecified):
            return self.default_value
        else:
            return self.data_with_gui.value


@dataclass
class OutputWithGui(Generic[DataType]):
    data_with_gui: AnyDataWithGui[DataType]


class FunctionWithGui:
    """Instantiate this class with your functions, to make them available in a graph
    You need to provide:
    - the name of the function
    - the implementation of the function (f_impl)
    - the inputs and outputs of the function, as a list of ParamWithGui
    """

    # set this with the actual function implementation at construction time
    f_impl: Callable[..., Any] | None = None

    # the name of the function
    name: str

    # input_gui and output_gui should be filled during construction
    inputs_with_gui: List[ParamWithGui[Any]]
    outputs_with_gui: List[OutputWithGui[Any]]

    # if the last call raised an exception, the message is stored here
    last_exception_message: Optional[str] = None
    last_exception_traceback: Optional[str] = None

    def __init__(self) -> None:
        self.inputs_with_gui = []
        self.outputs_with_gui = []

    def all_inputs_ids(self) -> List[str]:
        return [param.name for param in self.inputs_with_gui]

    def input_of_name(self, name: str) -> AnyDataWithGui[Any]:
        for param in self.inputs_with_gui:
            if param.name == name:
                return param.data_with_gui
        assert False, f"input {name} not found"

    def doc(self) -> Optional[str]:
        if self.f_impl is None:
            return None
        return self.f_impl.__doc__

    @final
    def invoke(self) -> None:
        assert self.f_impl is not None

        self.last_exception_message = None
        self.last_exception_traceback = None

        positional_only_values = []
        for param in self.inputs_with_gui:
            if param.param_kind == ParamKind.PositionalOnly:
                positional_only_values.append(param.get_value_or_default())

        keyword_values = {}
        for param in self.inputs_with_gui:
            if param.param_kind != ParamKind.PositionalOnly:
                keyword_values[param.name] = param.get_value_or_default()

        # if any of the inputs is an error or unspecified, we do not call the function
        all_params = positional_only_values + list(keyword_values.values())
        if any(value is ErrorValue or value is UnspecifiedValue for value in all_params):
            for output_with_gui in self.outputs_with_gui:
                output_with_gui.data_with_gui.value = UnspecifiedValue
            return

        try:
            fn_output = self.f_impl(*positional_only_values, **keyword_values)
            if not isinstance(fn_output, tuple):
                assert len(self.outputs_with_gui) == 1
                self.outputs_with_gui[0].data_with_gui.value = fn_output
            else:
                assert len(fn_output) == len(self.outputs_with_gui)
                for i, output_with_gui in enumerate(self.outputs_with_gui):
                    output_with_gui.data_with_gui.value = fn_output[i]
        except Exception as e:
            self.last_exception_message = str(e)
            import traceback
            import sys

            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback_details = traceback.format_exception(exc_type, exc_value, exc_traceback)
            self.last_exception_traceback = "".join(traceback_details)
            for output_with_gui in self.outputs_with_gui:
                output_with_gui.data_with_gui.value = ErrorValue

    def to_json(self) -> JsonDict:
        inputs_dicts = [param.to_json() for param in self.inputs_with_gui]
        function_dict = {"inputs": inputs_dicts}
        return function_dict

    def fill_from_json(self, json_data: JsonDict) -> None:
        inputs_json = json_data["inputs"]
        if len(inputs_json) != len(self.inputs_with_gui):
            raise ValueError(f"Expected {len(self.inputs_with_gui)} inputs, got {len(inputs_json)}")
        for param_json in inputs_json:
            param_name = param_json["name"]
            for input_param in self.inputs_with_gui:
                if input_param.name == param_name:
                    input_param.fill_from_json(param_json)
                    break

    def set_output_gui(self, data_with_gui: AnyDataWithGui[Any], output_idx: int = 0) -> None:
        if output_idx >= len(self.outputs_with_gui):
            raise ValueError(f"output_idx {output_idx} out of range")
        self.outputs_with_gui[output_idx].data_with_gui = data_with_gui

    def set_input_gui(self, input_name: str, data_with_gui: AnyDataWithGui[Any]) -> None:
        for param in self.inputs_with_gui:
            if param.name == input_name:
                param.data_with_gui = data_with_gui
                return
        raise ValueError(f"input_name {input_name} not found")

    def get_input_gui(self, input_name: str) -> AnyDataWithGui[Any]:
        for param in self.inputs_with_gui:
            if param.name == input_name:
                return param.data_with_gui
        raise ValueError(f"input_name {input_name} not found")

    def get_output_gui(self, output_idx: int = 0) -> AnyDataWithGui[Any]:
        if output_idx >= len(self.outputs_with_gui):
            raise ValueError(f"output_idx {output_idx} out of range")
        return self.outputs_with_gui[output_idx].data_with_gui
