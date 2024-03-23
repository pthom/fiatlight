from imgui_bundle import ImVec4


class FiatColors:
    error = ImVec4(1.0, 0.6, 0.3, 1)


class FiatConfig:
    colors = FiatColors()


FIATLIGHT_GUI_CONFIG = FiatConfig()
