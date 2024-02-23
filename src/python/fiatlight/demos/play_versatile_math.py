from fiatlight.fiatlight_gui import fiatlight_run, FiatlightGuiParams
from fiatlight import data_presenters

import math


def sin(x: float) -> float:
    return math.sin(x)


def main() -> None:
    from fiatlight import data_presenters as dp

    functions = [
        # data_presenters.make_float_source(4,
        #                                   dp.FloatEditParams(
        #                                       edit_type=data_presenters.FloatEditType.drag,
        #                                       input_step=0.1,
        #                                       input_step_fast=1,
        #                                       v_speed=3,
        #                                       v_min=-1000,
        #                                       v_max=1000,
        #                                   )),
        data_presenters.make_int_source(
            4,
            dp.IntEditParams(
                edit_type=dp.IntEditType.knob,
                v_min=-1000,
                v_max=1000,
                # knob_size_em=3,
                knob_variant=dp.ImGuiKnobVariant_.tick.value,
            ),
        ),
        # math.sin,
        # math.log,
        # math.exp,
        # math.cos,
        # math.exp,
        # math.sin,
        # math.log,
        # math.cos,
        # math.exp,
        # math.sin,
        # math.log,
        # math.cos,
        # math.exp,
        # math.sin,
        # math.log,
        # math.cos,
    ]

    fiatlight_run(FiatlightGuiParams(functions_graph=functions, app_title="play_versatile_math", initial_value=0))


if __name__ == "__main__":
    main()
