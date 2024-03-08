from fiatlight.core import UnspecifiedValue, ErrorValue, Unspecified, Error, JsonDict, DataType
from fiatlight.core.any_data_gui_handlers import AnyDataGuiHandlers
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
        self.name = json_data["name"]
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
        for i, param_json in enumerate(inputs_json):
            self.inputs_with_gui[i].fill_from_json(param_json)

    def set_output_gui_handler(self, handler: AnyDataGuiHandlers[Any], output_idx: int = 0) -> None:
        if output_idx >= len(self.outputs_with_gui):
            raise ValueError(f"output_idx {output_idx} out of range")
        self.outputs_with_gui[output_idx].data_with_gui.handlers = handler

    def set_input_gui_handler(self, input_name: str, handler: AnyDataGuiHandlers[Any]) -> None:
        for param in self.inputs_with_gui:
            if param.name == input_name:
                param.data_with_gui.handlers = handler
                return
        raise ValueError(f"input_name {input_name} not found")


def sandbox() -> None:
    from fiatlight.core.to_gui import any_function_to_function_with_gui
    from fiatlight.core.to_gui import ALL_GUI_HANDLERS_FACTORIES

    class Foo:
        a: int

        def __init__(self, a: int = 0):
            self.a = a

    def make_foo_with_gui(_: Any | None = None) -> AnyDataGuiHandlers[Foo]:
        r = AnyDataGuiHandlers[Foo]()
        r.gui_edit_impl = lambda x: (False, x)
        r.gui_present_impl = lambda x: None
        # r.to_dict_impl = lambda x: {"a": x.a}
        # r.from_dict_impl = lambda d: Foo(a=d["a"])
        return r

    ALL_GUI_HANDLERS_FACTORIES["Foo"] = make_foo_with_gui

    def add(foo: Foo) -> int:
        return foo.a

    add_gui = any_function_to_function_with_gui(add)
    add_gui.inputs_with_gui[0].data_with_gui.value = Foo()
    # s = add_gui.to_json()
    # print(s)


if __name__ == "__main__":
    sandbox()
