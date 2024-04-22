from fiatlight.fiat_image.image_types import ImageU8_1, ImageU8, Image
from fiatlight.fiat_image.image_gui import ImageWithGui
from fiatlight.fiat_core import to_function_with_gui


def test_image_type() -> None:
    def foo1(img: ImageU8_1) -> None:
        pass

    foo1_gui = to_function_with_gui(foo1)
    assert isinstance(foo1_gui._inputs_with_gui[0].data_with_gui, ImageWithGui)

    def foo2(img: ImageU8) -> None:
        pass

    foo2_gui = to_function_with_gui(foo2)
    assert isinstance(foo2_gui._inputs_with_gui[0].data_with_gui, ImageWithGui)

    def foo3(img: Image) -> None:
        pass

    foo3_gui = to_function_with_gui(foo3)
    assert isinstance(foo3_gui._inputs_with_gui[0].data_with_gui, ImageWithGui)
