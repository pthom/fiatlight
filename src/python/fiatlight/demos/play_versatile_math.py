from fiatlight.node_gui.fiatlight_gui import fiatlight_run, FiatlightGuiParams
from fiatlight.functions_graph import FunctionsGraph

import math


def main() -> None:
    def float_source(x: float) -> float:
        return x

    def sin(x: float) -> float:
        return math.sin(x)

    def log(x: float) -> float:
        return math.log(x)

    def add_mul(a: float, b: float) -> tuple[float, float]:
        return a + b, a * b

    functions_graph = FunctionsGraph.from_function_composition([float_source, sin, add_mul, log, sin])
    functions_graph.add_function_composition([float_source, sin, log, sin])

    fiatlight_run(
        functions_graph,
        FiatlightGuiParams(
            app_title="play_versatile_math",
            window_size=(1600, 1000),
            show_image_inspector=True,
        ),
    )


if __name__ == "__main__":
    main()
