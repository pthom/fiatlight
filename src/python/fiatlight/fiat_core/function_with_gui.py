import logging

from fiatlight.fiat_config import get_fiat_config
from fiatlight.fiat_types import UnspecifiedValue, ErrorValue, Unspecified, Error, JsonDict, DataType, GuiType
from fiatlight.fiat_core.any_data_with_gui import AnyDataWithGui
from typing import Any, List, final, Callable, Optional, Generic, Type, TypeAlias
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


@dataclass
class OutputWithGui(Generic[DataType]):
    data_with_gui: AnyDataWithGui[DataType]


class FunctionWithGui:
    """Instantiate this class with your functions, to make them available in a graph
    You need to provide:
    - the name of the function
    - the implementation of the function (_f_impl)
    - the inputs and outputs of the function, as a list of ParamWithGui
    """

    # --------------------------------------------------------------------------------------------
    #        Members
    # --------------------------------------------------------------------------------------------

    #
    # Public members
    #

    # if this is True, the function will be called automatically when any of the inputs change
    invoke_automatically: bool = True
    # if this is True, the user can set the invoke_automatically flag
    invoke_automatically_can_set: bool = False
    # the name of the function
    name: str

    #
    # Private members
    #

    # if True, this indicates that the inputs have changed since the last call, and the function needs to be called
    _dirty: bool = True

    # This is the implementation of the function, i.e. the function that will be called
    _f_impl: Callable[..., Any] | None = None

    # _inputs_with_gui and _outputs_with_gui should be filled soon after construction
    _inputs_with_gui: List[ParamWithGui[Any]]
    _outputs_with_gui: List[OutputWithGui[Any]]

    # if the last call raised an exception, the message is stored here
    _last_exception_message: Optional[str] = None
    _last_exception_traceback: Optional[str] = None

    # --------------------------------------------------------------------------------------------
    #        Construction
    #  input_with_gui and output_with_gui should be filled soon after construction
    # --------------------------------------------------------------------------------------------
    def __init__(self) -> None:
        self._inputs_with_gui = []
        self._outputs_with_gui = []

    # --------------------------------------------------------------------------------------------
    #        Inputs, aka parameters
    # --------------------------------------------------------------------------------------------
    def nb_inputs(self) -> int:
        return len(self._inputs_with_gui)

    def all_inputs_names(self) -> List[str]:
        return [param.name for param in self._inputs_with_gui]

    def input(self, name: str) -> AnyDataWithGui[Any]:
        """Return the input with the given name as a AnyDataWithGui[Any]
        The inner type of the returned value is Any in this case.
        You may have to cast it to the correct type, if you rely on type hints.

        Use input_as() if you want to get the input with the correct type.
        """
        for param in self._inputs_with_gui:
            if param.name == name:
                return param.data_with_gui
        assert False, f"input {name} not found"

    def input_as(self, name: str, gui_type: Type[GuiType]) -> GuiType:
        """Return the input with the given name as a GuiType

        GuiType can be any descendant of AnyDataWithGui, like
            fiatlight.fiat_core.IntWithGui, fiatlight.fiat_core.FloatWithGui, etc.

        Raises a ValueError if the input is not found, and a TypeError if the input is not of the correct type.
        """
        for param in self._inputs_with_gui:
            if param.name == name:
                r = param.data_with_gui
                if not isinstance(r, gui_type):
                    raise TypeError(f"Expected type {gui_type.__name__}, got {type(r).__name__} instead.")
                return r
        raise ValueError(f"Parameter {name} not found")

    def input_of_idx(self, idx: int) -> ParamWithGui[Any]:
        return self._inputs_with_gui[idx]

    def input_of_idx_as(self, idx: int, gui_type: Type[GuiType]) -> GuiType:
        r = self._inputs_with_gui[idx].data_with_gui
        if not isinstance(r, gui_type):
            raise TypeError(f"Expected type {gui_type.__name__}, got {type(r).__name__} instead.")
        return r

    def param(self, name: str) -> ParamWithGui[Any]:
        for param in self._inputs_with_gui:
            if param.name == name:
                return param
        raise ValueError(f"Parameter {name} not found")

    # --------------------------------------------------------------------------------------------
    #        Outputs
    # --------------------------------------------------------------------------------------------
    def nb_outputs(self) -> int:
        return len(self._outputs_with_gui)

    def output(self, output_idx: int = 0) -> AnyDataWithGui[Any]:
        """Return the output with the given index as a AnyDataWithGui[Any]
        The inner type of the returned value is Any in this case.
        You may have to cast it to the correct type, if you rely on type hints.

        Use output_as() if you want to get the output with the correct type.
        """
        if output_idx >= len(self._outputs_with_gui):
            raise ValueError(f"output_idx {output_idx} out of range")
        return self._outputs_with_gui[output_idx].data_with_gui

    def output_as(self, output_idx: int, gui_type: Type[GuiType]) -> GuiType:
        """Return the output with the given index as a GuiType

        GuiType can be any descendant of AnyDataWithGui, like
            fiatlight.fiat_core.IntWithGui, fiatlight.fiat_core.FloatWithGui, etc.

        Raises a ValueError if the output is not found, and a TypeError if the output is not of the correct type.
        """
        r = self._outputs_with_gui[output_idx].data_with_gui
        if not isinstance(r, gui_type):
            raise TypeError(f"Expected type {gui_type.__name__}, got {type(r).__name__} instead.")
        return r

    # --------------------------------------------------------------------------------------------
    #        Invoke the function
    # This is the heart of fiatlight: it calls the function with the current inputs
    # and stores the result in the outputs, stores the exception if any, etc.
    # --------------------------------------------------------------------------------------------
    @final
    def invoke(self) -> None:
        assert self._f_impl is not None

        if not self._dirty:
            return

        self._last_exception_message = None
        self._last_exception_traceback = None

        positional_only_values = []
        for param in self._inputs_with_gui:
            if param.param_kind == ParamKind.PositionalOnly:
                positional_only_values.append(param.get_value_or_default())

        keyword_values = {}
        for param in self._inputs_with_gui:
            if param.param_kind != ParamKind.PositionalOnly:
                keyword_values[param.name] = param.get_value_or_default()

        # if any of the inputs is an error or unspecified, we do not call the function
        all_params = positional_only_values + list(keyword_values.values())
        if any(value is ErrorValue or value is UnspecifiedValue for value in all_params):
            for output_with_gui in self._outputs_with_gui:
                output_with_gui.data_with_gui.value = UnspecifiedValue
            self._dirty = False
            return

        try:
            fn_output = self._f_impl(*positional_only_values, **keyword_values)
            if not isinstance(fn_output, tuple):
                assert len(self._outputs_with_gui) == 1
                self._outputs_with_gui[0].data_with_gui.value = fn_output
            else:
                assert len(fn_output) == len(self._outputs_with_gui)
                for i, output_with_gui in enumerate(self._outputs_with_gui):
                    output_with_gui.data_with_gui.value = fn_output[i]
        except Exception as e:
            if not get_fiat_config().exception_config.catch_function_exceptions:
                raise e
            else:
                self._last_exception_message = str(e)
                import traceback
                import sys

                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback_details = traceback.format_exception(exc_type, exc_value, exc_traceback)
                self._last_exception_traceback = "".join(traceback_details)
                for output_with_gui in self._outputs_with_gui:
                    output_with_gui.data_with_gui.value = ErrorValue

        self._dirty = False

    def is_dirty(self) -> bool:
        return self._dirty

    def get_last_exception_message(self) -> str | None:
        return self._last_exception_message

    # --------------------------------------------------------------------------------------------
    #        Save and load to json
    # Here, we only save the options that the user entered manually in the GUI:
    #   - the options of the inputs
    #   - the options of the outputs
    #   - the options of this FunctionWithGui (invoke_automatically, etc.)
    # --------------------------------------------------------------------------------------------
    def save_gui_options_to_json(self) -> JsonDict:
        input_options = {}
        for input_with_gui in self._inputs_with_gui:
            if input_with_gui.data_with_gui.callbacks.save_gui_options_to_json is not None:
                input_options[input_with_gui.name] = input_with_gui.data_with_gui.callbacks.save_gui_options_to_json()

        output_options = {}
        for i, output_with_gui in enumerate(self._outputs_with_gui):
            if output_with_gui.data_with_gui.callbacks.save_gui_options_to_json is not None:
                output_options[i] = output_with_gui.data_with_gui.callbacks.save_gui_options_to_json()

        r = {
            "inputs": input_options,
            "outputs": output_options,
        }
        if self.invoke_automatically_can_set:
            r["invoke_automatically"] = self.invoke_automatically
        return r

    def load_gui_options_from_json(self, json_data: JsonDict) -> None:
        input_options = json_data.get("inputs", {})
        for input_name, input_option in input_options.items():
            for input_with_gui in self._inputs_with_gui:
                callback_load = input_with_gui.data_with_gui.callbacks.load_gui_options_from_json
                if input_with_gui.name == input_name and callback_load is not None:
                    callback_load(input_option)
                    break

        output_options = json_data.get("outputs", {})
        for output_idx, output_option in output_options.items():
            output_idx = int(output_idx)
            if output_idx >= len(self._outputs_with_gui):
                logging.warn(f"Output index {output_idx} out of range")
                continue
            output_with_gui = self._outputs_with_gui[output_idx]
            callback_load = output_with_gui.data_with_gui.callbacks.load_gui_options_from_json
            if callback_load is not None:
                callback_load(output_option)

        if self.invoke_automatically_can_set:
            self.invoke_automatically = json_data.get("invoke_automatically", True)

    # --------------------------------------------------------------------------------------------
    #       Function documentation & source code
    # --------------------------------------------------------------------------------------------
    def has_doc(self) -> bool:
        return self.get_function_doc() is not None

    def get_function_doc(self) -> str | None:
        if self._f_impl is None:
            return None
        if hasattr(self._f_impl, "__doc__"):
            return self._f_impl.__doc__
        return None

    def get_function_doc_as_markdown(self) -> str | None:
        raise NotImplementedError("This method is not implemented yet")
        # Here be dragons...
        #
        # * PEP 257:
        #     is quite short and specifies that docstring should look like this:
        #     """Return an int (short one-liner info)
        #
        #     Optional additional description or example
        #     (More details in several lines)
        #
        #     Args:
        #     ...
        #     """
        #
        # Google style guide (https://google.github.io/styleguide/pyguide.html):
        #     specifies that docstring should look like this:
        #
        #    """Connects to the next available port.
        #
        #        Args:
        #          minimum: A port value greater or equal to 1024.
        #
        #       Returns:
        #         The new minimum port.
        #     """
        #
        # Sphinx (https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html)
        #    specifies that docstring should look like this:
        #
        #    """[Summary]
        #
        #       :param [ParamName]: [ParamDescription], defaults to [DefaultParamVal]
        #       :type [ParamName]: [ParamType](, optional)
        #       ...
        #       :raises [ErrorType]: [ErrorDescription]
        #       ...
        #       :return: [ReturnDescription]
        #       :rtype: [ReturnType]
        # """

        doc = self.get_function_doc()
        if doc is None:
            return None

        # remove leading and trailing whitespace
        doc = doc.strip()

        has_multiple_lines = "\n" in doc
        if not has_multiple_lines:
            return doc

        lines = doc.split("\n")
        first_line = lines[0]

        remaining_lines = lines[1:]
        remaining_lines = [line.strip() for line in remaining_lines]
        remaining_text = "\n".join(remaining_lines)

        # Search for first occurrence of "Args:" or "Returns:" or "Raises:" or ":params:"
        # and split the docstring at that point into
        #     detailed description
        #     parameters_description
        params_markers = ["Args:", "Returns:", "Raises:", ":param"]
        detailed_description = ""
        parameters_description = ""
        could_split = False
        for marker in params_markers:
            if marker in remaining_text:
                pos = remaining_text.index(marker)
                detailed_description = remaining_text[:pos]
                parameters_description = remaining_text[pos:]
                could_split = True
                break
        if not could_split:
            parameters_description = remaining_text

        # create markdown docstring
        markdown_doc = ""
        markdown_doc += f"## {first_line}\n\n"
        markdown_doc += f"{detailed_description}\n\n"
        markdown_doc += "### Parameters\n\n"
        markdown_doc += "```"
        markdown_doc += f"{parameters_description}\n\n"
        markdown_doc += "```"

        return markdown_doc

    def get_function_source_code(self) -> str | None:
        if self._f_impl is None:
            return None
        import inspect

        try:
            r = inspect.getsource(self._f_impl)
            return r
        except (OSError, TypeError):
            return None


FunctionWithGuiFactoryFromName: TypeAlias = Callable[[str], FunctionWithGui]
