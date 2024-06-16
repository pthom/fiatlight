from fiatlight.fiat_kits.fiat_image.image_types import ImageU8_1, ImageU8, Image
from fiatlight.fiat_kits.fiat_image.image_gui import ImageWithGui

from fiatlight import FunctionWithGui
from fiatlight.fiat_togui.optional_with_gui import OptionalWithGui


def test_image_type() -> None:
    def foo1(_img: ImageU8_1) -> None:
        pass

    foo1_gui = FunctionWithGui(foo1)
    assert isinstance(foo1_gui._inputs_with_gui[0].data_with_gui, ImageWithGui)

    def foo2(_img: ImageU8) -> None:
        pass

    foo2_gui = FunctionWithGui(foo2)
    assert isinstance(foo2_gui._inputs_with_gui[0].data_with_gui, ImageWithGui)

    def foo3(_img: Image) -> None:
        pass

    foo3_gui = FunctionWithGui(foo3)
    assert isinstance(foo3_gui._inputs_with_gui[0].data_with_gui, ImageWithGui)

    def foo4() -> ImageU8 | None:
        pass

    foo4_gui = FunctionWithGui(foo4)
    output4_gui = foo4_gui._outputs_with_gui[0].data_with_gui
    assert isinstance(output4_gui, OptionalWithGui)
    assert isinstance(output4_gui.inner_gui, ImageWithGui)


test_image_type()
