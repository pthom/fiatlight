from fiatlight.core.function_with_gui import FunctionWithGui, ParamWithGui
from fiatlight.core import JsonDict
from typing import Any


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

        assert src_output_idx < len(src_function_node.function_with_gui.outputs_with_gui)
        assert dst_input_name in dst_function_node.function_with_gui.all_inputs_ids()


class FunctionNode:
    """A FunctionWithGui that is included in a FunctionGraph
    It stores:
        - the FunctionWithGui
        - a list of FunctionNodeLink
    """

    function_with_gui: FunctionWithGui
    output_links: list[FunctionNodeLink]
    input_links: list[FunctionNodeLink]

    def __init__(self, function_with_gui: FunctionWithGui, name: str) -> None:
        self.function_with_gui = function_with_gui
        self.output_links = []
        self.input_links = []

    def add_output_link(self, link: FunctionNodeLink) -> None:
        self.output_links.append(link)

    def add_input_link(self, link: FunctionNodeLink) -> None:
        self.input_links.append(link)

    def has_input_link(self, parameter_name: str) -> bool:
        r = any(link.dst_input_name == parameter_name for link in self.input_links)
        return r

    def user_editable_params(self) -> list[ParamWithGui[Any]]:
        r = [param for param in self.function_with_gui.inputs_with_gui if not self.has_input_link(param.name)]
        return r

    def invoke_function(self) -> None:
        self.function_with_gui.invoke()
        for link in self.output_links:
            src_output = self.function_with_gui.outputs_with_gui[link.src_output_idx]
            dst_input = link.dst_function_node.function_with_gui.input_of_name(link.dst_input_name)
            dst_input.value = src_output.data_with_gui.value
            link.dst_function_node.invoke_function()

    def save_user_inputs_to_json(self) -> JsonDict:
        r = {}
        for param in self.user_editable_params():
            r[param.name] = param.data_with_gui.to_json()
        return r

    def fill_user_inputs_from_json(self, json_data: JsonDict) -> None:
        for param in self.user_editable_params():
            if param.name in json_data:
                param.data_with_gui.fill_from_json(json_data[param.name])
