from fiatlight.fiat_config import get_fiat_config
from fiatlight.fiat_types import UnspecifiedValue, ErrorValue, JsonDict, GuiType
from fiatlight.fiat_core.any_data_with_gui import AnyDataWithGui
from fiatlight.fiat_types.function_types import BoolFunction
from fiatlight.fiat_core.param_with_gui import ParamWithGui, ParamKind
from fiatlight.fiat_core.output_with_gui import OutputWithGui
from fiatlight.fiat_core.primitives_gui import IntWithGui, FloatWithGui, BoolWithGui, StrWithGui

from typing import Any, List, final, Callable, Optional, Type, TypeAlias
import logging


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

    # the name of the function
    name: str = ""

    #
    # Behavioral Flags
    #

    # invoke_async: if true, the function shall be called asynchronously
    invoke_async: bool = False

    # invoke_manually: if true, the function will be called only if the user clicks on the "invoke" button
    # (if inputs were changed, a "Refresh needed" label will be displayed)
    invoke_manually: bool = False

    # invoke_always_dirty: if true, the function output will always be considered out of date, and
    #   - if invoke_manually is true, the "Refresh needed" label will be displayed
    #   - if invoke_manually is false, the function will be called at each frame
    # Note: a "live" function is thus a function with invoke_manually=False and invoke_always_dirty=True
    invoke_always_dirty: bool = False

    # internal_state_gui: optional Gui for the internal state of the function
    # (this function may display a GUI to show the internal state of the function,
    #  and return True if the state has changed, and the function needs to be called)
    internal_state_gui: BoolFunction | None = None

    # on_heartbeat: optional function that will be called at each frame
    # (and return True if the function needs to be called to update the output)
    on_heartbeat: BoolFunction | None = None

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
    def __init__(self, fn: Callable[..., Any] | None) -> None:
        from fiatlight.fiat_core.to_gui import (
            _add_input_outputs_to_function_with_gui_globals_locals_captured,
            _capture_caller_globals_locals,
        )

        self._inputs_with_gui = []
        self._outputs_with_gui = []
        self._f_impl = fn

        if fn is not None:
            globals_dict, locals_dict = _capture_caller_globals_locals()
            _add_input_outputs_to_function_with_gui_globals_locals_captured(
                self, globals_dict=globals_dict, locals_dict=locals_dict
            )

    @staticmethod
    def create_empty() -> "FunctionWithGui":
        r = FunctionWithGui(None)
        return r

    # def add_param(
    #     self,
    #     name: str,
    #     data_with_gui: AnyDataWithGui[Any],
    #     default_value: Any | Unspecified = UnspecifiedValue,
    #     param_kind: ParamKind = ParamKind.PositionalOrKeyword,
    # ) -> None:
    #     """For manual construction of the function, add a parameter to the function"""
    #     self._inputs_with_gui.append(ParamWithGui(name, data_with_gui, param_kind, default_value))
    #
    # def add_output(self, data_with_gui: AnyDataWithGui[Any] | None = None) -> None:
    #     """For manual construction of the function, add an output to the function"""
    #     if data_with_gui is None:
    #         data_with_gui = AnyDataWithGui()
    #     self._outputs_with_gui.append(OutputWithGui(data_with_gui))

    def set_invoke_live(self) -> None:
        """Set flags to make this a live function (called automatically at each frame)"""
        self.invoke_manually = False
        self.invoke_always_dirty = True

    def set_invoke_manually(self) -> None:
        """Set flags to make this a function that needs to be called manually"""
        self.invoke_manually = True

    def set_invoke_manually_io(self) -> None:
        """Set flags to make this a IO function that needs to be called manually
        and that is always considered dirty, because it depends on an external device
        or state (and likely has no input)"""
        self.invoke_manually = True
        self.invoke_always_dirty = True

    def is_invoke_manually_io(self) -> bool:
        """Return True if the function is an IO function that needs to be called manually"""
        return self.invoke_manually and self.invoke_always_dirty

    def set_invoke_async(self) -> None:
        """Set flags to make this a function that is called asynchronously"""
        self.invoke_async = True

    def is_live(self) -> bool:
        """Return True if the function is live"""
        return not self.invoke_manually and self.invoke_always_dirty

    # --------------------------------------------------------------------------------------------
    #        Utilities
    # --------------------------------------------------------------------------------------------
    def is_dirty(self) -> bool:
        return self._dirty

    def set_dirty(self) -> None:
        self._dirty = True

    def get_last_exception_message(self) -> str | None:
        return self._last_exception_message

    def shall_display_refresh_needed_label(self) -> bool:
        return self.invoke_manually and self._dirty and not self.is_invoke_manually_io()

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

    def input_as_float(self, name: str) -> FloatWithGui:
        return self.input_as(name, FloatWithGui)

    def input_as_int(self, name: str) -> IntWithGui:
        return self.input_as(name, IntWithGui)

    def input_as_bool(self, name: str) -> BoolWithGui:
        return self.input_as(name, BoolWithGui)

    def input_as_str(self, name: str) -> StrWithGui:
        return self.input_as(name, StrWithGui)

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
                assert len(self._outputs_with_gui) <= 1
                if len(self._outputs_with_gui) == 1:
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

    def on_exit(self) -> None:
        for output_with_gui in self._outputs_with_gui:
            if output_with_gui.data_with_gui.callbacks.on_exit is not None:
                output_with_gui.data_with_gui.callbacks.on_exit()
        for input_with_gui in self._inputs_with_gui:
            if input_with_gui.data_with_gui.callbacks.on_exit is not None:
                input_with_gui.data_with_gui.callbacks.on_exit()

    # --------------------------------------------------------------------------------------------
    #        Save and load to json
    # Here, we only save the options that the user entered manually in the GUI:
    #   - the options of the inputs
    #   - the options of the outputs
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
