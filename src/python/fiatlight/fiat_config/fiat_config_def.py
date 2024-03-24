from fiatlight.fiat_config.fiat_style_def import FiatStyle, FiatColorType
from fiatlight.fiat_config.fiat_exception_config_def import FiatExceptionConfig


class FiatConfig:
    style: FiatStyle = FiatStyle()
    exception_config: FiatExceptionConfig = FiatExceptionConfig()

    def __init__(self) -> None:
        self.style = FiatStyle()
        self.exception_config = FiatExceptionConfig()


_FIAT_CONFIG = FiatConfig()


def get_fiat_config() -> FiatConfig:
    return _FIAT_CONFIG


__all__ = [
    "FiatConfig",
    "FiatColorType",
    "get_fiat_config",
    "FiatStyle",
    "FiatExceptionConfig",
]
