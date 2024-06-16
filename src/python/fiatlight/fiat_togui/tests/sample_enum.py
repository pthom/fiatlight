from enum import Enum


class SampleEnumNotRegistered(Enum):
    A = 1
    B = 2


class SampleEnumRegisteredManually(Enum):
    A = 1
    B = 2


class SampleEnumRegisteredDecorator(Enum):
    A = 1
    B = 2
