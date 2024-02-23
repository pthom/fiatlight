from fiatlight.fiatlight_gui import fiatlight_run, FiatlightGuiParams
from fiatlight.functions_graph import FunctionsGraph

import math


def main() -> None:
    # functions = [
    #     data_presenters.make_float_source(4,
    #                                       dp.FloatWithGuiParams(
    #                                           edit_type=data_presenters.FloatEditType.drag,
    #                                           input_step=0.1,
    #                                           input_step_fast=1,
    #                                           v_speed=3,
    #                                           v_min=-1000,
    #                                           v_max=1000,
    #                                       )),
    #     data_presenters.make_int_source(
    #         4,
    #         dp.IntWithGuiParams(
    #             edit_type=dp.IntEditType.knob,
    #             v_min=-1000,
    #             v_max=1000,
    #             # knob_size_em=3,
    #             knob_variant=dp.ImGuiKnobVariant_.tick.value,
    #         ),
    #     ),
    #     math.sin,
    #     math.log,
    #     math.exp,
    # ]

    def float_source(x: float) -> float:
        return x

    def sin(x: float) -> float:
        return math.sin(x)

    def log(x: float) -> float:
        return math.log(x)

    functions_graph = FunctionsGraph.from_function_composition([float_source, sin, log])

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
