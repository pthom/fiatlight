from fiatlight.fiat_togui.make_gui_demo_code import make_gui_demo_code
from fiatlight.fiat_doc import code_utils


def test_int() -> None:
    from fiatlight.fiat_togui.primitives_gui import IntWithGui

    demo_code = make_gui_demo_code(IntWithGui())
    code_utils.assert_are_codes_equal(
        demo_code,
        """
import typing
import fiatlight


def f(int_param: int) -> int:
    return int_param

fiatlight.fiat_run(f)
    """,
    )


def test_image() -> None:
    from fiatlight.fiat_kits.fiat_image import ImageWithGui

    demo_code = make_gui_demo_code(ImageWithGui())
    code_utils.assert_are_codes_equal(
        demo_code,
        """
import typing
import fiatlight


def f(union_param: typing.Union[fiatlight.fiat_kits.fiat_image.image_types.ImageU8_1, fiatlight.fiat_kits.fiat_image.image_types.ImageU8_2, fiatlight.fiat_kits.fiat_image.image_types.ImageU8_3, fiatlight.fiat_kits.fiat_image.image_types.ImageU8_4, fiatlight.fiat_kits.fiat_image.image_types.ImageU8_RGB, fiatlight.fiat_kits.fiat_image.image_types.ImageU8_RGBA, fiatlight.fiat_kits.fiat_image.image_types.ImageU8_BGRA, fiatlight.fiat_kits.fiat_image.image_types.ImageU8_BGR, fiatlight.fiat_kits.fiat_image.image_types.ImageU8_GRAY, fiatlight.fiat_kits.fiat_image.image_types.ImageFloat_1, fiatlight.fiat_kits.fiat_image.image_types.ImageFloat_2, fiatlight.fiat_kits.fiat_image.image_types.ImageFloat_3, fiatlight.fiat_kits.fiat_image.image_types.ImageFloat_4]) -> typing.Union[fiatlight.fiat_kits.fiat_image.image_types.ImageU8_1, fiatlight.fiat_kits.fiat_image.image_types.ImageU8_2, fiatlight.fiat_kits.fiat_image.image_types.ImageU8_3, fiatlight.fiat_kits.fiat_image.image_types.ImageU8_4, fiatlight.fiat_kits.fiat_image.image_types.ImageU8_RGB, fiatlight.fiat_kits.fiat_image.image_types.ImageU8_RGBA, fiatlight.fiat_kits.fiat_image.image_types.ImageU8_BGRA, fiatlight.fiat_kits.fiat_image.image_types.ImageU8_BGR, fiatlight.fiat_kits.fiat_image.image_types.ImageU8_GRAY, fiatlight.fiat_kits.fiat_image.image_types.ImageFloat_1, fiatlight.fiat_kits.fiat_image.image_types.ImageFloat_2, fiatlight.fiat_kits.fiat_image.image_types.ImageFloat_3, fiatlight.fiat_kits.fiat_image.image_types.ImageFloat_4]:
    return union_param

fiatlight.fiat_run(f)
    """,
    )
