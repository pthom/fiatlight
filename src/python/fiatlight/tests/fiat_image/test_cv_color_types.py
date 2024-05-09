from fiatlight.fiat_kits.fiat_image import cv_color_type


def test_truc() -> None:
    color = cv_color_type.ColorType.BGR
    outputs = color.available_conversion_outputs()
    print(outputs)
