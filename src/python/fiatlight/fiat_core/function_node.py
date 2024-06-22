from fiatlight.fiat_core.function_with_gui import FunctionWithGui
from fiatlight.fiat_core.param_with_gui import ParamWithGui
from fiatlight.fiat_types import JsonDict, ErrorValue
from typing import Any, List
import logging
import threading


class FunctionNodeLink:
    """A link from the one of the output of a FunctionNode to one of the inputs of another FunctionNode"""

    src_function_node: "FunctionNode"
    src_output_idx: int
    dst_function_node: "FunctionNode"
    dst_input_name: str

    def __init__(
        self,
        src_function_node: "FunctionNode",
        src_output_idx: int,
        dst_function_node: "FunctionNode",
        dst_input_name: str,
    ) -> None:
        self.src_function_node = src_function_node
        self.src_output_idx = src_output_idx
        self.dst_function_node = dst_function_node
        self.dst_input_name = dst_input_name

        assert src_output_idx < src_function_node.function_with_gui.nb_outputs()
        assert dst_input_name in dst_function_node.function_with_gui.all_inputs_names()

    def is_equal(self, other: "FunctionNodeLink") -> bool:
        return (
            self.src_function_node == other.src_function_node
            and self.src_output_idx == other.src_output_idx
            and self.dst_function_node == other.dst_function_node
            and self.dst_input_name == other.dst_input_name
        )


class FunctionNode:
    """A FunctionWithGui that is included in a FunctionGraph
    It stores:
        - the FunctionWithGui
        - a list of FunctionNodeLink

    It is able to invoke the function and propagate the outputs to the linked inputs of the other functions.
    It will invoke the function either synchronously or asynchronously, depending on the invoke_async flag.
    """

    function_with_gui: FunctionWithGui
    output_links: list[FunctionNodeLink]
    input_links: list[FunctionNodeLink]

    # Invoke related members
    _nb_inputs_changes = 0
    _input_changes_during_async = False
    _async_invoke_thread: threading.Thread | None = None
    _inputs_changed_again_during_async: bool = False

    def __init__(self, function_with_gui: FunctionWithGui) -> None:
        self.function_with_gui = function_with_gui
        self.output_links = []
        self.input_links = []

    def add_output_link(self, link: FunctionNodeLink) -> None:
        self.output_links.append(link)

    def add_input_link(self, link: FunctionNodeLink) -> None:
        self.input_links.append(link)

    def input_node_link(self, parameter_name: str) -> FunctionNodeLink | None:
        input_links = list(link for link in self.input_links if link.dst_input_name == parameter_name)
        assert len(list(input_links)) <= 1
        if len(input_links) == 1:
            return input_links[0]
        else:
            return None

    def has_input_link(self, parameter_name: str) -> bool:
        r = self.input_node_link(parameter_name) is not None
        return r

    def unlinked_input_names(self) -> List[str]:
        r = [
            param_name
            for param_name in self.function_with_gui.all_inputs_names()
            if not self.has_input_link(param_name)
        ]
        return r

    def unlinked_output_idxs(self) -> List[int]:
        r = [
            output_idx
            for output_idx in range(self.function_with_gui.nb_outputs())
            if not any(link.src_output_idx == output_idx for link in self.output_links)
        ]
        return r

    def nb_unlinked_outputs(self) -> int:
        return len(self.unlinked_output_idxs())

    def nb_unlinked_inputs(self) -> int:
        return len(self.unlinked_input_names())

    def input_node_link_info(self, parameter_name: str) -> str | None:
        link = self.input_node_link(parameter_name)
        if link is None:
            return None
        fn_label = link.src_function_node.function_with_gui.label
        r = "linked to " + fn_label
        if link.src_function_node.function_with_gui.nb_outputs() > 1:
            r += f" (output {link.src_output_idx})"
        return r

    def output_links_for_idx(self, output_idx: int) -> List[FunctionNodeLink]:
        output_links = list(link for link in self.output_links if link.src_output_idx == output_idx)
        return output_links

    def output_node_links_info(self, output_idx: int) -> List[str]:
        output_links = self.output_links_for_idx(output_idx)
        r = []
        for link in output_links:
            fn_label = link.dst_function_node.function_with_gui.label
            r.append(f"linked to {fn_label} (input {link.dst_input_name})")
        return r

    class _Serialization_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # ==================================================================================================================
        # Save and load user settings
        # ==================================================================================================================
        """

        pass

    def user_editable_params(self) -> list[ParamWithGui[Any]]:
        r = [param for param in self.function_with_gui._inputs_with_gui if not self.has_input_link(param.name)]  # noqa
        return r

    def save_user_inputs_to_json(self) -> JsonDict:
        user_inputs = {}
        for input_param in self.user_editable_params():
            user_inputs[input_param.name] = input_param.save_self_value_to_dict()
        return user_inputs

    def load_user_inputs_from_json(self, json_data: JsonDict) -> None:
        for input_param in self.user_editable_params():
            input_param.load_self_value_from_dict(json_data[input_param.name])

    def save_gui_options_to_json(self) -> JsonDict:
        return self.function_with_gui.save_gui_options_to_json()

    def load_gui_options_from_json(self, json_data: JsonDict) -> None:
        self.function_with_gui.load_gui_options_from_json(json_data)

    class _Invoke_Section:  # Dummy class to create a section in the IDE # noqa
        # ------------------------------------------------------------------------------------------------------------------
        #  Invoke
        # ------------------------------------------------------------------------------------------------------------------
        pass

    def is_running_async(self) -> bool:
        if self._async_invoke_thread is None:
            return False
        return True

    def heartbeat(self) -> bool:
        needs_refresh = False
        if self.function_with_gui.on_heartbeat is not None:
            if self.function_with_gui.on_heartbeat():
                needs_refresh = True

        for input_with_gui in self.function_with_gui._inputs_with_gui:
            input_heartbeat = input_with_gui.data_with_gui.callbacks.on_heartbeat
            if input_heartbeat is not None:
                if input_heartbeat():
                    needs_refresh = True

        for output_with_gui in self.function_with_gui._outputs_with_gui:
            output_heartbeat = output_with_gui.data_with_gui.callbacks.on_heartbeat
            if output_heartbeat is not None:
                if output_heartbeat():
                    needs_refresh = True

        # Handle async invoke
        # -------------------
        # delete _async_invoke_thread if it is not alive anymore
        if self._async_invoke_thread is not None:
            if not self._async_invoke_thread.is_alive():
                self._async_invoke_thread = None
        # Reinvoke the async call if needed (inputs changed during async)
        self._reinvoke_async_if_needed()

        # Handle function behavioral flags
        # --------------------------------
        if self.function_with_gui.invoke_always_dirty:
            self.function_with_gui.set_dirty()
        if self.function_with_gui.is_live():
            # self.function_with_gui.set_dirty()  # done already
            self.call_invoke_async_or_not()

        return needs_refresh

    def on_inputs_changed(self) -> None:
        """Called when one of the inputs of the function has changed.
        May or may not call the function depending on the invoke_manually flag."""
        self._nb_inputs_changes += 1
        msg = f"_on_inputs_changed: {self._nb_inputs_changes=}"
        if self.is_running_async():
            self._input_changes_during_async = True
            msg += " (changed while function is running)"
        # logging.debug(msg)
        self.function_with_gui._dirty = True
        if not self.function_with_gui.invoke_manually:
            self.call_invoke_async_or_not()

    def _invoke_function_sync(self) -> None:
        """Invoke the function and propagate the outputs to the linked inputs of the other functions.
        *not part of the API, but called by call_invoke_async_or_not()*
        """
        self.function_with_gui.invoke()
        for link in self.output_links:
            src_output = self.function_with_gui.output(link.src_output_idx)
            dst_input = link.dst_function_node.function_with_gui.input(link.dst_input_name)

            if src_output.value is not None:
                dst_input.value = src_output.value
            else:
                if not dst_input.can_be_none:
                    this_function_name = self.function_with_gui.function_name
                    other_function_name = link.dst_function_node.function_with_gui.function_name
                    msg = f"""{this_function_name} returned None, but {other_function_name} cannot accept it as param "{link.dst_input_name}"!\n\n"""
                    msg += "Fiatlight will not transmit None values to functions that cannot accept them.\n"
                    msg += "(This might be what you expect, as it is spares you from checking for\nNone values in your code, when using Fiatlight)\n\n"
                    msg += f"If you want to debug this, please place a breakpoint in {this_function_name},\n"
                    msg += "and inspect why the function returns none."

                    # logging.warning(msg)
                    self.function_with_gui._last_exception_message = msg
                    dst_input.value = ErrorValue
                else:
                    dst_input.value = None

            link.dst_function_node.on_inputs_changed()

    def call_invoke_async_or_not(self) -> None:
        """Call the function (maybe async)"""

        def _invoke_async() -> None:
            if self._async_invoke_thread is not None and self._async_invoke_thread.is_alive():
                return

            def async_target() -> None:
                logging.debug(f"Async invoke with {self._nb_inputs_changes=}")
                self._invoke_function_sync()

            self._async_invoke_thread = threading.Thread(target=async_target)
            self._async_invoke_thread.start()

        shall_invoke_async = self.function_with_gui.invoke_async
        if shall_invoke_async:
            _invoke_async()
        else:
            self._invoke_function_sync()

    def _reinvoke_async_if_needed(self) -> None:
        if self._input_changes_during_async and not self.is_running_async():
            logging.debug(f"Dirty after invoke: rerun {self._nb_inputs_changes=}")
            self.function_with_gui._dirty = True
            self._input_changes_during_async = False
            self.call_invoke_async_or_not()
