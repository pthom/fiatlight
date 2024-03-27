from typing import NewType
from dataclasses import dataclass


@dataclass
class FloatInterval:
    lower_bound: float
    upper_bound: float


@dataclass
class IntInterval:
    lower_bound: int
    upper_bound: int


# Float types with specific ranges (bounds included)
Float_0_1 = NewType("Float_0_1", float)  # 0 to 1
Float__1_1 = NewType("Float__1_1", float)  # -1 to 1
Float_0_10 = NewType("Float_0_10", float)  # 0 to 10
Float_0_100 = NewType("Float_0_100", float)  # 0 to 100
Float_0_1000 = NewType("Float_0_1000", float)  # 0 to 1000
Float_0_10000 = NewType("Float_0_10000", float)  # 0 to 10000

# Int types with specific ranges (bounds included)
Int_0_10 = NewType("Int_0_10", int)  # 0 to 10
Int_0_255 = NewType("Int_0_255", int)  # 0 to 255
Int_0_100 = NewType("Int_0_100", int)  # 0 to 100

OddInt = NewType("OddInt", int)  # Odd integers
