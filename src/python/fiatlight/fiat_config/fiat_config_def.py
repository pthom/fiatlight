from fiatlight.fiat_config.fiat_style_def import FiatStyle, FiatColorType


class FiatConfig:
    style: FiatStyle = FiatStyle()
    catch_function_exceptions: bool = True
    disable_input_during_execution: bool = False
    is_recording_snippet_screenshot: bool = False

    def __init__(self) -> None:
        self.style = FiatStyle()


_FIAT_CONFIG = FiatConfig()


def get_fiat_config() -> FiatConfig:
    return _FIAT_CONFIG


__all__ = [
    "FiatConfig",
    "FiatColorType",
    "get_fiat_config",
    "FiatStyle",
]
