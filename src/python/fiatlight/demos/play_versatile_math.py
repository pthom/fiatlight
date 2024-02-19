from fiatlight.fiatlight_gui import fiatlight_run, FiatlightGuiParams
from fiatlight import data_presenters

import math


def main() -> None:
    functions = [
        data_presenters.make_int_source(4),
        math.exp,
        math.sin,
        math.log,
        math.cos,
        math.exp,
        math.sin,
        math.log,
        math.cos,
        math.exp,
        math.sin,
        math.log,
        math.cos,
        math.exp,
        math.sin,
        math.log,
        math.cos,
    ]

    fiatlight_run(FiatlightGuiParams(functions_graph=functions, app_title="play_versatile_math", initial_value=0))


if __name__ == "__main__":
    main()
