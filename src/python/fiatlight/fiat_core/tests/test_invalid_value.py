import fiatlight as fl


def validate_odd_int(odd_int: int) -> fl.DataValidationResult:
    if odd_int % 2 == 1:
        return fl.DataValidationResult.ok()
    return fl.DataValidationResult.error("must be an odd number")


def test_invalid_value() -> None:
    def f(odd_int: int) -> int:
        return odd_int + 1

    fl.add_custom_attrs(f, odd_int__range=(1, 100), odd_int__validate_value=validate_odd_int)

    f_gui = fl.FunctionWithGui(f)

    # Call with valid value
    r = f_gui.call_for_tests(odd_int=3)
    assert r == 4

    # Call with invalid value
    r2 = f_gui.call_for_tests(odd_int=4)
    assert r2 is fl.fiat_types.UnspecifiedValue
    odd_int_param = f_gui.param_gui("odd_int")
    assert isinstance(odd_int_param.value, fl.fiat_types.InvalidValue)
    assert odd_int_param.value.error_message == "must be an odd number"


test_invalid_value()