import fiatlight as fl
from enum import Enum


class Sex(Enum):
    Man = "male"
    Woman = "female"


def f(s: Sex | None) -> Sex | None:
    return s


fl.run(f, app_name="demo_enum")
