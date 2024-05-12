import math
import fiatlight


def my_asin(x: float = 0.5) -> float:
    return math.asin(x)


fiatlight.fiat_run(my_asin)
