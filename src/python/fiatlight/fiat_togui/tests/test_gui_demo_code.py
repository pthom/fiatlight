from fiatlight.fiat_togui.make_gui_demo_code import make_gui_demo_code
from fiatlight.fiat_doc import code_utils


def test_int() -> None:
    from fiatlight.fiat_togui.primitives_gui import IntWithGui

    demo_code = make_gui_demo_code(IntWithGui())
    # print(demo_code)

    code_utils.assert_are_codes_equal(
        demo_code,
        """
import typing
import fiatlight

@fiatlight.with_custom_attrs(
    #  Validation
    int_param__validate_value = None,
    #  Custom attributes
    int_param__range = (0, 10),
    int_param__edit_type = "input",
    int_param__format = "%d",
    int_param__width_em = 9.0,
    int_param__knob_size_em = 2.5,
    int_param__knob_steps = 10,
    int_param__knob_no_input = True,
    int_param__slider_no_input = False,
    int_param__slider_logarithmic = False)
def f(int_param: int) -> int:
    return int_param

fiatlight.fiat_run(f)
    """,
    )
