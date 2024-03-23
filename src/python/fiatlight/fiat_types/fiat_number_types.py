from typing import NewType


# Float types with specific ranges (bounds included)
Float_0_1 = NewType("Float_0_1", float)  # 0 to 1
Float__1_1 = NewType("Float__1_1", float)  # -1 to 1
Float_0_10 = NewType("Float_0_10", float)  # 0 to 10
Float_0_100 = NewType("Float_0_100", float)  # 0 to 100

# Int types with specific ranges (bounds included)
Int_0_10 = NewType("Int_0_10", int)  # 0 to 10
Int_0_255 = NewType("Int_0_255", int)  # 0 to 255
Int_0_100 = NewType("Int_0_100", int)  # 0 to 100


__all__ = [
    "Float_0_1",
    "Float__1_1",
    "Float_0_10",
    "Float_0_100",
    "Int_0_10",
    "Int_0_100",
    "Int_0_255",
]
