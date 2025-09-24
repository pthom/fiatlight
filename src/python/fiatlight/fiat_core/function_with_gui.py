"""FunctionWithGui: add GUI to a function"""

from fiatlight.fiat_config import get_fiat_config
from fiatlight.fiat_core.togui_exception import FiatToGuiException
from fiatlight.fiat_types import UnspecifiedValue, ErrorValue, JsonDict, GuiType
from fiatlight.fiat_types.error_types import Unspecified, Error, Invalid
from fiatlight.fiat_core.any_data_with_gui import AnyDataWithGui, toggle_expanded_state_on_guis
from fiatlight.fiat_types.function_types import BoolFunction
from fiatlight.fiat_core.param_with_gui import ParamWithGui, ParamKind
from fiatlight.fiat_core.output_with_gui import OutputWithGui
from fiatlight.fiat_core.possible_fiat_attributes import PossibleFiatAttributes
from fiatlight.fiat_types.base_types import FiatAttributes
from typing import Any, List, final, Callable, Optional, Type, TypeAlias
from dataclasses import dataclass

import logging


class FunctionPossibleFiatAttributes(PossibleFiatAttributes):
    def __init__(self) -> None:
        super().__init__("FunctionWithGui")

        self.add_explained_section("Behavioral Flags")
        self.add_explained_attribute(
            "invoke_async",
            bool,
            "If True, the function shall be called asynchronously",
            False,
        )
        self.add_explained_attribute(
            "invoke_manually",
            bool,
            "If True, the function will be called only if the user clicks on the 'invoke' button",
            False,
        )
        self.add_explained_attribute(
            "invoke_always_dirty",
            bool,
            "If True, the function output will always be considered out of date, and "
            "  - if invoke_manually is True, the 'Refresh needed' label will be displayed"
            "  - if invoke_manually is False, the function will be called at each frame",
            False,
        )
        self.add_explained_section("Documentation")
        self.add_explained_attribute(
            "label",
            str,
            "The display name of the function (will use the function name if empty)",
            "",
        )
        self.add_explained_attribute(
            "doc_display",
            bool,
            "If True, the doc string is displayed in the GUI",
            False,
        )
        self.add_explained_attribute(
            "doc_markdown",
            bool,
            "If True, the doc string is in Markdown format",
            True,
        )
        self.add_explained_attribute(
            "doc_user", str, "The documentation string. If not provided, the function docstring will be used", ""
        )
        self.add_explained_attribute(
            "doc_show_source", bool, "If True, the source code of the function will be displayed in the GUI", False
        )


_FUNCTION_POSSIBLE_FIAT_ATTRIBUTES = FunctionPossibleFiatAttributes()


@dataclass
class FunctionWithGuiDoc:
    user_doc: str | None = None
    is_user_doc_markdown: bool = True
    source_code: str | None = None


class FunctionWithGui:
    """FunctionWithGui: add GUI to a function

    `FunctionWithGui` is one of the core classes of FiatLight: it wraps a function with a GUI that presents its
    inputs and its output(s).

    Public Members
    ==============
    # the name of the function
    name: str = ""

    #
    # Behavioral Flags
    # ----------------
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

    # Optional user documentation to be displayed in the GUI
    #     - doc_display: if True, the doc string is displayed in the GUI (default: False)
    #     - doc_is_markdown: if True, the doc string is in Markdown format (default: True)
    #     - doc_user: the documentation string. If not provided, the function docstring will be used
    #     - doc_show_source: if True, the source code of the function will be displayed in the GUI
    doc_display: bool = True
    doc_markdown: bool = True
    doc_user: str = ""
    doc_show_source: bool = False

    #
    # Internal state GUI
    # ------------------
    # internal_state_gui: optional Gui for the internal state of the function
    # (this function may display a GUI to show the internal state of the function,
    #  and return True if the state has changed, and the function needs to be called)
    internal_state_gui: BoolFunction | None = None

    #
    # Heartbeat
    # ---------
    # on_heartbeat: optional function that will be called at each frame
    # (and return True if the function needs to be called to update the output)
    on_heartbeat: BoolFunction | None = None

    #
    # Serialization
    # -------------
    # save/load_internal_gui_options_from_json (Optional)
    # Optional serialization and deserialization of the internal state GUI presentation options
    # (i.e. anything that deals with how the GUI is presented, not the data itself)
    # If provided, these functions will be used to recreate the GUI presentation options when loading a graph,
    # so that the GUI looks the same when the application is restarted.
    save_internal_gui_options_to_json: Callable[[], JsonDict] | None = None
    load_internal_gui_options_from_json: Callable[[JsonDict], None] | None = None

    """

    # --------------------------------------------------------------------------------------------
    #        Public Members
    # --------------------------------------------------------------------------------------------
    # the name of the function: this is usually inferred from the name of the function in the source code
    # It should be unique in a function graph: add a hidden "##suffix" to make it unique if needed, e.g.
    #    "my_function##123"
    function_name: str = ""
    # the display name of the function (will use the function name if empty)
    label: str = ""

    #
    # Behavioral Flags
    # ----------------
    # invoke_async: if true, the function shall be called asynchronously
    invoke_async: bool = False

    # invoke_async_stoppable: if true a GUI button will be displayed to stop the async function while it is running.
    # In this case, the function body should periodically check whether it should stop,
    # by checking the value of the flag `invoke_async_shall_stop`
    # (which is added to the function object by FiatLight)
    #
    # Example:
    #    def my_async_function():
    #         ...
    #         while some_condition:  # inner loop of the function processing
    #             if hasattr(my_async_function, "invoke_async_shall_stop") and my_async_function.invoke_async_shall_stop:
    #                 my_async_function.invoke_async_shall_stop = False  # reset the flag
    #                 break
    #        ...  # continue the function processing
    invoke_async_stoppable: bool = False

    # invoke_manually: if true, the function will be called only if the user clicks on the "invoke" button
    # (if inputs were changed, a "Refresh needed" label will be displayed)
    invoke_manually: bool = False

    # invoke_always_dirty: if true, the function output will always be considered out of date, and
    #   - if invoke_manually is true, the "Refresh needed" label will be displayed
    #   - if invoke_manually is false, the function will be called at each frame
    # Note: a "live" function is thus a function with invoke_manually=False and invoke_always_dirty=True
    invoke_always_dirty: bool = False

    # invoke_is_gui_only: if True, the function is only used for its GUI; i.e.:
    # - it will not be called as a standard function (i.e. when its inputs change).
    # - instead, it will be called at each frame, and its GUI will be displayed
    invoke_is_gui_only: bool = False

    # Optional user documentation to be displayed in the GUI
    #     - doc_display: if True, the doc string is displayed in the GUI (default: False)
    #     - doc_is_markdown: if True, the doc string is in Markdown format (default: True)
    #     - doc_user: the documentation string. If not provided, the function docstring will be used
    #     - doc_show_source: if True, the source code of the function will be displayed in the GUI
    doc_display: bool = True
    doc_markdown: bool = True
    doc_user: str = ""
    doc_show_source: bool = False

    #
    # Internal state GUI
    # ------------------
    # internal_state_gui: optional Gui for the internal state of the function
    # (this function may display a GUI to show the internal state of the function,
    #  and return True if the state has changed, and the function needs to be called)
    internal_state_gui: BoolFunction | None = None

    # Serialization
    # save/load_internal_gui_options_from_json (Optional)
    # Optional serialization and deserialization of the internal state GUI presentation options and data
    # If provided, these functions will be used to recreate the GUI presentation options or data when loading a graph,
    # so that the GUI looks the same when the application is restarted.
    save_internal_gui_options_to_json: Callable[[], JsonDict] | None = None
    load_internal_gui_options_from_json: Callable[[JsonDict], None] | None = None

    #
    # Heartbeat
    # ---------
    # on_heartbeat: optional function that will be called at each frame
    # (and return True if the function needs to be called to update the output)
    on_heartbeat: BoolFunction | None = None

    # --------------------------------------------------------------------------------------------
    #        Private Members
    # --------------------------------------------------------------------------------------------
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

    class _Construct_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # --------------------------------------------------------------------------------------------
        #        Construction
        #  input_with_gui and output_with_gui should be filled soon after construction
        # --------------------------------------------------------------------------------------------
        """

        pass

    def __init__(
        self,
        fn: Callable[..., Any] | None,
        fn_name: str | None = None,
        *,
        signature_string: str | None = None,
        fiat_attributes: FiatAttributes | None = None,
        is_dataclass_init_method: bool = False,
    ) -> None:
        """Create a FunctionWithGui object, with the given function as implementation

        The function signature is automatically parsed, and the inputs and outputs are created
        with the correct GUI types.

        :param fn: the function for which we want to create a FunctionWithGui

        Notes:
        This function will capture the locals and globals of the caller to be able to evaluate the types.
        Make sure to call this function *from the module where the function and its input/output types are defined*

        If the function has attributes like invoke_manually or invoke_async, they will be taken into account:
            - if `invoke_async` is True, the function will be called asynchronously
            - if `invoke_manually` is True, the function will be called only if the user clicks on the "invoke" button


        Advanced parameters:
        ********************
        :param signature_string: a string representing the signature of the function
                                 used when the function signature cannot be retrieved automatically
        """
        from fiatlight.fiat_togui.add_input_outputs_to_function import (
            add_input_outputs_to_function,
        )

        self._inputs_with_gui = []
        self._outputs_with_gui = []
        self._f_impl = fn
        self.function_name = fn_name or ""

        if fn is not None:
            if self.function_name == "":
                self.function_name = fn.__name__ if hasattr(fn, "__name__") else ""
            if fiat_attributes is None:
                fiat_attributes = FiatAttributes(fn.__dict__) if hasattr(fn, "__dict__") else FiatAttributes({})
            add_input_outputs_to_function(
                self,
                signature_string=signature_string,
                fiat_attributes=fiat_attributes,
            )

        if self.function_name == "":
            raise FiatToGuiException("FunctionWithGui: function name is empty")
        self.label = self.function_name  # Can be customized via fiat_attributes

        if fiat_attributes is not None:
            self.handle_fiat_attributes(fiat_attributes)

        for input_with_gui in self._inputs_with_gui:
            input_with_gui.data_with_gui._can_set_unspecified_or_default = True

        for output_with_gui in self._outputs_with_gui:
            output_with_gui.data_with_gui._expanded = True

    class _FiatAttributes_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # --------------------------------------------------------------------------------------------
        #        Fiat Attributes
        # --------------------------------------------------------------------------------------------
        """

        pass

    def handle_fiat_attributes(self, fiat_attributes: dict[str, Any]) -> None:
        """Handle fiat attributes for the function"""
        # Filter out the attributes for parameters and outputs
        # (they contain a double underscore "__" in their name)
        fn_fiat_attributes = {key: value for key, value in fiat_attributes.items() if "__" not in key}
        # We accept wrong keys, because other libraries, such as Pydantic, may add custom attributes
        # that would not be recognized by FiatLight
        _FUNCTION_POSSIBLE_FIAT_ATTRIBUTES.raise_exception_if_bad_fiat_attrs(fn_fiat_attributes)

        # Check that there are no attributes for a non-existing parameter or output
        params_fiat_attributes = [key for key in fiat_attributes if "__" in key and not key.startswith("__")]
        for fiat_attribute in params_fiat_attributes:
            assert "__" in fiat_attribute
            param_name = fiat_attribute.split("__")[0]
            if fiat_attribute.startswith("return__"):
                if len(self._outputs_with_gui) == 0:
                    raise FiatToGuiException(
                        f"""
                        FunctionWithGui({self.function_name}): custom attribute '{fiat_attribute}' invalid. The function has no output!
                        """
                    )
            else:
                if not self.has_param(param_name):
                    raise FiatToGuiException(
                        f"""
                        FunctionWithGui({self.function_name}): custom attribute '{fiat_attribute}' is associated to a parameter {param_name} that does not exist!
                        """
                    )

        # Set the fiat attributes for the function
        if "invoke_async" in fn_fiat_attributes:
            self.invoke_async = fn_fiat_attributes["invoke_async"]
        if "invoke_async_stoppable" in fn_fiat_attributes:
            self.invoke_async_stoppable = fn_fiat_attributes["invoke_async_stoppable"]
            if self.invoke_async_stoppable:
                self.invoke_async = True
        if "invoke_manually" in fn_fiat_attributes:
            self.invoke_manually = fn_fiat_attributes["invoke_manually"]
        if "invoke_always_dirty" in fn_fiat_attributes:
            self.invoke_always_dirty = fn_fiat_attributes["invoke_always_dirty"]
        if "doc_display" in fn_fiat_attributes:
            self.doc_display = fn_fiat_attributes["doc_display"]
        if "doc_markdown" in fn_fiat_attributes:
            self.doc_markdown = fn_fiat_attributes["doc_markdown"]
        if "doc_user" in fn_fiat_attributes:
            self.doc_user = fn_fiat_attributes["doc_user"]
        if "doc_show_source" in fn_fiat_attributes:
            self.doc_show_source = fn_fiat_attributes["doc_show_source"]
        if "label" in fn_fiat_attributes:
            self.label = fn_fiat_attributes["label"]

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

    class _Utilities_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # --------------------------------------------------------------------------------------------
        #        Utilities
        # --------------------------------------------------------------------------------------------
        """

        pass

    # There is intentionally no __call__ function!
    # To call the function, set its params via set_param_value, then call the invoke() function

    def call_for_tests(self, **params: Any) -> Any:
        """Call the function with the given parameters, for testing purposes"""
        self._dirty = True
        for name, value in params.items():
            self.set_param_value(name, value)
        self.invoke()
        if self.nb_outputs() == 1:
            return self.output().value
        return tuple([output.data_with_gui.value for output in self._outputs_with_gui])

    def is_dirty(self) -> bool:
        """Return True if the function needs to be called, because the inputs have changed since the last call"""
        return self._dirty

    def set_dirty(self) -> None:
        """Set the function as dirty."""
        self._dirty = True

    def get_last_exception_message(self) -> str | None:
        """Return the last exception message, if any"""
        return self._last_exception_message

    def shall_display_refresh_needed_label(self) -> bool:
        """Return True if the "Refresh needed" label should be displayed
        i.e. if the function is dirty and invoke_manually is True"""
        return self.invoke_manually and self._dirty and not self.is_invoke_manually_io()

    def __str__(self) -> str:
        return f"FunctionWithGui({self.function_name})"

    class _Inputs_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # --------------------------------------------------------------------------------------------
        #        Inputs, aka parameters
        # --------------------------------------------------------------------------------------------
        """

        pass

    def nb_inputs(self) -> int:
        """Return the number of inputs of the function"""
        return len(self._inputs_with_gui)

    def all_inputs_names(self) -> List[str]:
        """Return the names of all the inputs of the function"""
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
        """Return the input with the given index as a ParamWithGui[Any]"""
        return self._inputs_with_gui[idx]

    def input_of_idx_as(self, idx: int, gui_type: Type[GuiType]) -> GuiType:
        """Return the input with the given index as a GuiType"""
        r = self._inputs_with_gui[idx].data_with_gui
        if not isinstance(r, gui_type):
            raise TypeError(f"Expected type {gui_type.__name__}, got {type(r).__name__} instead.")
        return r

    def inputs_guis(self) -> List[AnyDataWithGui[Any]]:
        r = []
        for i in self._inputs_with_gui:
            r.append(i.data_with_gui)
        return r

    def set_input_gui(self, name: str, gui: AnyDataWithGui[Any]) -> None:
        """Set the GUI for the input with the given name"""
        for param in self._inputs_with_gui:
            if param.name == name:
                param.data_with_gui = gui
                return
        raise ValueError(f"Parameter {name} not found")

    def has_param(self, name: str) -> bool:
        """Return True if the function has a parameter with the given name"""
        return any(param.name == name for param in self._inputs_with_gui)

    def param(self, name: str) -> ParamWithGui[Any]:
        """Return the input with the given name as a ParamWithGui[Any]"""
        for param in self._inputs_with_gui:
            if param.name == name:
                return param
        raise ValueError(f"Parameter {name} not found")

    def param_gui(self, name: str) -> AnyDataWithGui[Any]:
        """Return the input with the given name as a AnyDataWithGui[Any]"""
        return self.param(name).data_with_gui

    def set_param_value(self, name: str, value: Any) -> None:
        """Set the value of the input with the given name
        This is useful to set the value of an input programmatically, for example in tests.
        """
        for param in self._inputs_with_gui:
            if param.name == name:
                param.data_with_gui.value = value
                return
        raise ValueError(f"Parameter {name} not found")

    def toggle_expand_inputs(self) -> None:
        toggle_expanded_state_on_guis(self.inputs_guis())

    def toggle_expand_outputs(self) -> None:
        toggle_expanded_state_on_guis(self.outputs_guis())

    def _nb_collapsible_inputs(self) -> int:
        """Return the number of collapsible inputs of the function"""
        n = 0
        for param in self._inputs_with_gui:
            if param.data_with_gui.callbacks.edit_collapsible:
                n += 1
        return n

    class _Outputs_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # --------------------------------------------------------------------------------------------
        #        Outputs
        # --------------------------------------------------------------------------------------------
        """

        pass

    def nb_outputs(self) -> int:
        """Return the number of outputs of the function.
        A function typically has 0 or 1 output, but it can have more if it returns a tuple.
        """
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

    def outputs_guis(self) -> List[AnyDataWithGui[Any]]:
        r = []
        for i in self._outputs_with_gui:
            r.append(i.data_with_gui)
        return r

    def _nb_collapsible_outputs(self) -> int:
        """Return the number of collapsible outputs of the function"""
        n = 0
        for output in self._outputs_with_gui:
            if output.data_with_gui.callbacks.edit_collapsible:
                n += 1
        return n

    class _Invoke_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # --------------------------------------------------------------------------------------------
        #        Invoke the function
        # This is the heart of fiatlight: it calls the function with the current inputs
        # and stores the result in the outputs, stores the exception if any, etc.
        # --------------------------------------------------------------------------------------------
        """

        pass

    @final
    def has_bad_inputs(self) -> bool:
        # if any of the inputs is an error or unspecified, we cannot call the function
        for param in self._inputs_with_gui:
            if isinstance(param.data_with_gui.value, (Error, Unspecified, Invalid)):
                return True
        return False

    @final
    def invoke(self) -> None:
        """Invoke the function with the current inputs, and store the result in the outputs.

        Will call the function if:
         - the inputs have changed since the last call
         - the function is dirty
         - none of the inputs is an error or unspecified

        If an exception is raised, the outputs will be set to ErrorValue, and the exception will be stored.

        If the function returned None and the output is not allowed to be None, a ValueError will be raised
        (this is inferred from the function signature)
        """
        if not self.invoke_is_gui_only:
            self._invoke_impl()

    def invoke_gui(self) -> None:
        if not self.invoke_is_gui_only:
            raise ValueError("This function is not a GUI-only function")
        self._invoke_impl()

    @final
    def _invoke_impl(self) -> None:
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
        if any(isinstance(value, (Error, Unspecified, Invalid)) for value in all_params):
            for output_with_gui in self._outputs_with_gui:
                output_with_gui.data_with_gui.value = UnspecifiedValue
            self._dirty = False
            return

        try:
            fn_output = self._f_impl(*positional_only_values, **keyword_values)

            if fn_output is None and not self._can_emit_none_output():
                msg = f"Function {self.function_name} returned None, which is not allowed"
                logging.warning(msg)
                # If you are trying to debug and find the root cause of your problem,
                # be informed that a user was just called a few lines before, with this call:
                #     fn_output = self._f_impl(*positional_only_values, **keyword_values)
                # This user function returned none and this was not expected.
                # In the debugger, look at self.name to know which function this was.
                raise ValueError(msg)

            if not isinstance(fn_output, tuple):
                assert len(self._outputs_with_gui) <= 1
                if len(self._outputs_with_gui) == 1:
                    self._outputs_with_gui[0].data_with_gui.value = fn_output
            else:
                assert len(fn_output) == len(self._outputs_with_gui)
                for i, output_with_gui in enumerate(self._outputs_with_gui):
                    output_with_gui.data_with_gui.value = fn_output[i]
        except Exception as e:
            if not get_fiat_config().run_config.catch_function_exceptions:
                raise e
            else:
                self._last_exception_message = str(e)
                import traceback
                import sys

                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback_details = traceback.format_exception(exc_type, exc_value, exc_traceback)
                self._last_exception_traceback = "".join(traceback_details)

                logging.warning(
                    f"""
                Function {self.function_name} raised an exception: {self._last_exception_message}
                Traceback:
                {self._last_exception_traceback}
                """
                )

                for output_with_gui in self._outputs_with_gui:
                    output_with_gui.data_with_gui.value = ErrorValue

        self._dirty = False

    def on_exit(self) -> None:
        """Called when the application is exiting
        Will call the on_exit callback of all the inputs and outputs
        """
        for output_with_gui in self._outputs_with_gui:
            if output_with_gui.data_with_gui.callbacks.on_exit is not None:
                output_with_gui.data_with_gui.callbacks.on_exit()
        for input_with_gui in self._inputs_with_gui:
            if input_with_gui.data_with_gui.callbacks.on_exit is not None:
                input_with_gui.data_with_gui.callbacks.on_exit()

    def _can_emit_none_output(self) -> bool:
        """Return True if the function can emit None as output
        i.e.
        - either the function has no output
        - or the output can be None (i.e. the signature looks like `def f() -> int | None:`)
        if the function has multiple outputs, we consider that it can not emit None
        """
        if self.invoke_is_gui_only:
            return True
        if len(self._outputs_with_gui) > 1:
            return False
        if len(self._outputs_with_gui) == 0:
            return True
        output = self._outputs_with_gui[0]
        r = output.data_with_gui.can_be_none
        return r

    class _Serialize_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # --------------------------------------------------------------------------------------------
        #        Save and load to json
        # Here, we only save the options that the user entered manually in the GUI:
        #   - the options of the inputs
        #   - the options of the outputs
        # --------------------------------------------------------------------------------------------
        """

        pass

    def save_user_inputs_to_json(self) -> JsonDict:
        # This method is redefined in FunctionNode, where it saves only the unlinked inputs
        user_inputs = {}
        for input_param in self._inputs_with_gui:
            user_inputs[input_param.name] = input_param.save_self_value_to_dict()
        return user_inputs

    def load_user_inputs_from_json(self, json_data: JsonDict) -> None:
        # This method is redefined in FunctionNode, where it loads only the unlinked inputs
        for input_param in self._inputs_with_gui:
            input_param.load_self_value_from_dict(json_data[input_param.name])

    def save_gui_options_to_json(self) -> JsonDict:
        """Save the GUI options to a JSON file
        (i.e. any presentation options of the inputs and outputs, as well as of the internal GUI)
        """
        input_options = {}
        for input_with_gui in self._inputs_with_gui:
            input_options[input_with_gui.name] = input_with_gui.data_with_gui.call_save_gui_options_to_json()

        output_options = {}
        for i, output_with_gui in enumerate(self._outputs_with_gui):
            output_options[str(i)] = output_with_gui.data_with_gui.call_save_gui_options_to_json()

        r = {
            "inputs": input_options,
            "outputs": output_options,
        }
        if self.save_internal_gui_options_to_json is not None:
            r["internal_gui_options"] = self.save_internal_gui_options_to_json()
        return r

    def load_gui_options_from_json(self, json_data: JsonDict) -> None:
        """Load the GUI options from a JSON file"""
        input_options = json_data.get("inputs", {})
        for input_with_gui in self._inputs_with_gui:
            input_with_gui.data_with_gui.call_load_gui_options_from_json(input_options[input_with_gui.name])

        output_options = json_data.get("outputs", {})
        for i, output_with_gui in enumerate(self._outputs_with_gui):
            output_with_gui.data_with_gui.call_load_gui_options_from_json(output_options[str(i)])

        if "internal_gui_options" in json_data:
            internal_gui_options = json_data.get("internal_gui_options")
            if self.load_internal_gui_options_from_json is not None:
                self.load_internal_gui_options_from_json(internal_gui_options)  # type: ignore

    class _Doc_Section:  # Dummy class to create a section in the IDE # noqa
        # --------------------------------------------------------------------------------------------
        #       Function documentation & source code
        #       (This is a draft)
        # --------------------------------------------------------------------------------------------
        pass

    def get_function_doc(self) -> FunctionWithGuiDoc:
        if hasattr(self, "_cached_function_with_gui_doc"):
            return self._cached_function_with_gui_doc  # type: ignore
        r = FunctionWithGuiDoc()
        r.user_doc = self._get_function_userdoc()
        r.is_user_doc_markdown = self.doc_markdown
        r.source_code = self._get_function_source_code()
        self._cached_function_with_gui_doc = r
        return r

    def _get_function_userdoc(self) -> str | None:
        """Return the user documentation of the function"""
        from fiatlight.fiat_utils import docstring_utils

        if not self.doc_display:
            return ""
        if self.doc_user:
            r = self.doc_user
            r = docstring_utils.unindent_docstring(r)
            return r
        return self._get_function_docstring()

    def _get_function_docstring(self) -> str | None:
        """Return the docstring of the function"""
        from fiatlight.fiat_utils import docstring_utils

        if self._f_impl is None:
            return None
        if hasattr(self._f_impl, "__doc__"):
            docstring = self._f_impl.__doc__
            if docstring is None:
                return None
            docstring = docstring_utils.unindent_docstring(docstring)
            return docstring
        return None

    def _get_function_source_code(self) -> str | None:
        """Return the source code of the function"""
        if not self.doc_show_source:
            return None
        if self._f_impl is None:
            return None
        import inspect

        try:
            r = inspect.getsource(self._f_impl)
            return r
        except (OSError, TypeError):
            return None


FunctionWithGuiFactoryFromName: TypeAlias = Callable[[str], FunctionWithGui]
