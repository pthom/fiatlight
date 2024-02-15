from typing import List, Tuple
from imgui_bundle import immapp
from fiatlux.versatile import VersatileFunctionsCompositionGraph

import math


def main() -> None:
    functions = [
        math.exp,
        math.sin,
        math.log,
        math.cos
    ]
    functions_graph = VersatileFunctionsCompositionGraph(functions)  # type: ignore

    functions_graph.set_input(2)

    def gui() -> None:
        functions_graph.draw()

    immapp.run(gui, with_node_editor=True, window_size=(1400, 600), window_title="play_versatile_math")


if __name__ == "__main__":
    main()
