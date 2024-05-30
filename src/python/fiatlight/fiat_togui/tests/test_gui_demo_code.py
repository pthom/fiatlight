from fiatlight.fiat_togui.make_gui_demo_code import make_gui_demo_code
from fiatlight.fiat_doc import code_utils


def test_int() -> None:
    from fiatlight.fiat_togui.primitives_gui import IntWithGui

    demo_code = make_gui_demo_code(IntWithGui())
    print(demo_code)

    code_utils.assert_are_codes_equal(
        demo_code,
        """
import typing
import fiatlight

@fiatlight.with_custom_attrs(
    range = (0, 10),
    edit_type = "input",
    format = "%d",
    width_em = 9.0,
    knob_size_em = 2.5,
    knob_steps = 10,
    knob_no_input = True,
    slider_no_input = False,
    slider_logarithmic = False)
def f(int_param: int) -> int:
    return int_param

fiatlight.fiat_run(f)
    """,
    )
