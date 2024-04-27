from typing import NewType, Tuple, TypeAlias


FloatInterval: TypeAlias = Tuple[float, float]
IntInterval: TypeAlias = Tuple[int, int]


# Float types with specific ranges (bounds included)
Float_0_1 = NewType("Float_0_1", float)  # 0 to 1
Float_0_2 = NewType("Float_0_2", float)  # 0 to 1
Float_0_3 = NewType("Float_0_3", float)  # 0 to 1
Float__1_1 = NewType("Float__1_1", float)  # -1 to 1
Float_0_10 = NewType("Float_0_10", float)  # 0 to 10
Float_0_100 = NewType("Float_0_100", float)  # 0 to 100
Float_0_1000 = NewType("Float_0_1000", float)  # 0 to 1000
Float_0_10000 = NewType("Float_0_10000", float)  # 0 to 10000
PositiveFloat = NewType("PositiveFloat", float)  # Any positive float ( strictly greater than 0)

# Int types with specific ranges (bounds included)
Int_0_10 = NewType("Int_0_10", int)  # 0 to 10
Int_0_255 = NewType("Int_0_255", int)  # 0 to 255
Int_0_100 = NewType("Int_0_100", int)  # 0 to 100
Int_0_1000 = NewType("Int_0_1000", int)  # 0 to 100
Int_0_10000 = NewType("Int_0_10000", int)  # 0 to 100

# Time
TimeSeconds = NewType("TimeSeconds", float)  # Time in seconds


def format_time_seconds_as_hh_mm_ss_cc(time_seconds: TimeSeconds) -> str:
    """Format a time in seconds as a string in the format HH:MM:SS.cc."""
    hours = int(time_seconds) // 3600
    minutes = (int(time_seconds) % 3600) // 60
    seconds = int(time_seconds) % 60
    centiseconds = int((time_seconds - int(time_seconds)) * 100)
    return f"{hours:02}:{minutes:02}:{seconds:02}.{centiseconds:02}"


def format_time_seconds_as_mm_ss_cc(time_seconds: TimeSeconds) -> str:
    """Format a time in seconds as a string in the format MM:SS.cc."""
    minutes = int(time_seconds) // 60
    seconds = int(time_seconds) % 60
    centiseconds = int((time_seconds - int(time_seconds)) * 100)
    return f"{minutes:02}:{seconds:02}.{centiseconds:02}"


def format_time_seconds_as_hh_mm_ss(time_seconds: TimeSeconds) -> str:
    """Format a time in seconds as a string in the format HH:MM:SS."""
    hours = int(time_seconds) // 3600
    minutes = (int(time_seconds) % 3600) // 60
    seconds = int(time_seconds) % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"


def _register_bound_floats() -> None:
    from fiatlight.fiat_core.to_gui import gui_factories

    float_intervals: dict[str, FloatInterval] = {
        "Float_0_1": (0.0, 1.0),
        "Float_0_2": (0.0, 2.0),
        "Float_0_3": (0.0, 3.0),
        "Float__1_1": (-1.0, 1.0),
        "Float_0_10": (0.0, 10.0),
        "Float_0_100": (0.0, 100.0),
        "Float_0_1000": (0.0, 1000.0),
        "Float_0_10000": (0.0, 10000.0),
    }
    for name, interval in float_intervals.items():
        gui_factories().register_bound_float(interval, name)


def _register_bound_ints() -> None:
    from fiatlight.fiat_core.to_gui import gui_factories

    int_intervals: dict[str, IntInterval] = {
        "Int_0_10": (0, 10),
        "Int_0_100": (0, 100),
        "Int_0_255": (0, 255),
        "Int_0_1000": (0, 1000),
        "Int_0_10000": (0, 10000),
    }
    for name, interval_int in int_intervals.items():
        gui_factories().register_bound_int(interval_int, name)


def _register_bound_numbers() -> None:
    _register_bound_floats()
    _register_bound_ints()
