import pytest

import fiatlight as fl


def test_no_custom_attributes() -> None:
    def f() -> None:
        pass

    # This should not raise any exception
    _f_gui = fl.FunctionWithGui(f)


def test_param_custom_attributes() -> None:
    @fl.with_fiat_attributes(x__range=(0, 10), return__range=(0, 10))
    def f(x: int) -> int:
        return x

    # This should not raise any exception
    _f_gui = fl.FunctionWithGui(f)


def test_function_attributes() -> None:
    @fl.with_fiat_attributes(
        invoke_async=True,
        invoke_manually=True,
        invoke_always_dirty=True,
        doc_display=True,
        doc_markdown=False,
        doc_user="This is a test",
    )
    def f(x: int) -> int:
        return x

    _f_gui = fl.FunctionWithGui(f)
    assert _f_gui.invoke_async
    assert _f_gui.invoke_manually
    assert _f_gui.invoke_always_dirty
    assert _f_gui.doc_display
    assert not _f_gui.doc_markdown
    assert _f_gui.doc_user == "This is a test"


def test_function_attributes_wrong_type() -> None:
    @fl.with_fiat_attributes(
        invoke_async="True",
    )
    def f(x: int) -> int:
        return x

    with pytest.raises(fl.FiatToGuiException):
        _f_gui = fl.FunctionWithGui(f)


def test_function_attributes_wrong_key() -> None:
    @fl.with_fiat_attributes(
        wrong_key=True,
    )
    def f(x: int) -> int:
        return x

    # This should not raise an exception:
    # we accept other custom attributes
    # since libraries like pydantic may add their own
    _f_gui = fl.FunctionWithGui(f)
