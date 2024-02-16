from fiatlight import PureFunction
from fiatlight.fiatlight import FiatlightGui

import math


def main() -> None:
    functions: list[PureFunction] = [math.exp, math.sin, math.log, math.cos]
    fiatlight_gui = FiatlightGui(functions)
    fiatlight_gui.run("play_versatile_math", initial_value=2)


if __name__ == "__main__":
    main()
