from typing import NewType, Tuple, TypeAlias, Type, Any

FloatInterval: TypeAlias = Tuple[float, float]
IntInterval: TypeAlias = Tuple[int, int]


# Float types with specific ranges (bounds included)
Float_0_1 = NewType("Float_0_1", float)  # 0 to 1
Float_0_1.__doc__ = "synonym for float in [0, 1] (NewType)"

Float__1_1 = NewType("Float__1_1", float)  # -1 to 1
Float__1_1.__doc__ = "synonym for float in [-1, 1] (NewType)"

PositiveFloat = NewType("PositiveFloat", float)  # Any positive float ( strictly greater than 0)
PositiveFloat.__doc__ = "synonym for float > 0 (strictly greater than 0) (NewType)"

# Int types with specific ranges (bounds included)
Int_0_255 = NewType("Int_0_255", int)  # 0 to 255
Int_0_255.__doc__ = "synonym for int in [0, 255] (NewType)"

# Time
TimeSeconds = NewType("TimeSeconds", float)  # Time in seconds
TimeSeconds.__doc__ = "Time in seconds (synonym for float) (NewType)"


def format_time_seconds(time_seconds: TimeSeconds, show_centiseconds: bool = False) -> str:
    """Format a time in seconds as a string in the format HH:MM:SS.cc."""
    hours = int(time_seconds) // 3600
    minutes = (int(time_seconds) % 3600) // 60
    seconds = int(time_seconds) % 60
    centiseconds = int((time_seconds - int(time_seconds)) * 100)
    r = ""
    if hours > 0:
        r += f"{hours:02}:"
    r += f"{minutes:02}:"
    r += f"{seconds:02}"
    if show_centiseconds:
        r += f".{centiseconds:02}"
    return r


def _register_bound_floats() -> None:
    from fiatlight.fiat_togui.gui_registry import gui_factories

    float_intervals: dict[Type[Any], FloatInterval] = {
        Float_0_1: (0.0, 1.0),
        Float__1_1: (-1.0, 1.0),
    }
    for type_, interval in float_intervals.items():
        gui_factories().register_bound_float(type_, interval)


def _register_bound_ints() -> None:
    from fiatlight.fiat_togui.gui_registry import gui_factories

    int_intervals: dict[Type[Any], IntInterval] = {
        Int_0_255: (0, 255),
    }
    for type_, interval_int in int_intervals.items():
        gui_factories().register_bound_int(type_, interval_int)


def _register_bound_numbers() -> None:
    _register_bound_floats()
    _register_bound_ints()
