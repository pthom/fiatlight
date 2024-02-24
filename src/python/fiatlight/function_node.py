from fiatlight.function_with_gui import FunctionWithGui


class FunctionNodeLink:
    """A link from the one of the output of a FunctionNode to one of the inputs of another FunctionNode"""

    src_function_node: "FunctionNode"
    src_output_name: str
    dst_function_node: "FunctionNode"
    dst_input_name: str

    def __init__(
        self,
        src_function_node: "FunctionNode",
        src_output_name: str,
        dst_function_node: "FunctionNode",
        dst_input_name: str,
    ) -> None:
        self.src_function_node = src_function_node
        self.src_output_name = src_output_name
        self.dst_function_node = dst_function_node
        self.dst_input_name = dst_input_name

        assert src_output_name in src_function_node.function_with_gui.all_outputs_ids()
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

    def invoke_function(self) -> None:
        self.function_with_gui.invoke()
        for link in self.output_links:
            src_output = self.function_with_gui.output_of_name(link.src_output_name)
            dst_input = link.dst_function_node.function_with_gui.input_of_name(link.dst_input_name)
            dst_input.value = src_output.value
            link.dst_function_node.invoke_function()
