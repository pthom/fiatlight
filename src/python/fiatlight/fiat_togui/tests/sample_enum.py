import fiatlight as fl
from enum import Enum


class SampleEnumNotRegistered(Enum):
    A = 1
    B = 2


class SampleEnumRegisteredManually(Enum):
    A = 1
    B = 2


fl.register_enum(SampleEnumRegisteredManually)


@fl.enum_with_gui_registration
class SampleEnumRegisteredDecorator(Enum):
    A = 1
    B = 2
