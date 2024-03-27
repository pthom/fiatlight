from fiatlight.fiat_core.function_with_gui import FunctionWithGui, ParamWithGui
from fiatlight.fiat_types import JsonDict
from typing import Any, List


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
    """

    function_with_gui: FunctionWithGui
    output_links: list[FunctionNodeLink]
    input_links: list[FunctionNodeLink]

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

    def input_node_link_info(self, parameter_name: str) -> str | None:
        link = self.input_node_link(parameter_name)
        if link is None:
            return None
        fn_name = link.src_function_node.function_with_gui.name
        r = "linked to " + fn_name
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
            fn_name = link.dst_function_node.function_with_gui.name
            r.append(f"linked to {fn_name} (input {link.dst_input_name})")
        return r

    def user_editable_params(self) -> list[ParamWithGui[Any]]:
        r = [param for param in self.function_with_gui._inputs_with_gui if not self.has_input_link(param.name)]  # noqa
        return r

    def invoke_function(self) -> None:
        self.function_with_gui.invoke()
        for link in self.output_links:
            src_output = self.function_with_gui.output(link.src_output_idx)
            dst_input = link.dst_function_node.function_with_gui.input(link.dst_input_name)
            dst_input.value = src_output.value
            link.dst_function_node.function_with_gui._dirty = True
            link.dst_function_node.invoke_function()

    def save_user_inputs_to_json(self) -> JsonDict:
        input_params = {}
        for input_param in self.user_editable_params():
            input_params[input_param.name] = input_param.save_to_json()

        gui_options = self.function_with_gui.save_gui_options_to_json()
        r = {"inputs": input_params, "gui_options": gui_options}
        return r

    def load_user_inputs_from_json(self, json_data: JsonDict) -> None:
        input_params = json_data["inputs"]
        for input_param in self.user_editable_params():
            input_param.load_from_json(input_params[input_param.name])

        self.function_with_gui.load_gui_options_from_json(json_data["gui_options"])
