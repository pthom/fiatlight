import fiatlight as fl
from fiatlight.fiat_core import AnyDataWithGui, PossibleFiatAttributes
from fiatlight.fiat_types import DataValidationResult
from fiatlight.fiat_doc import code_utils


class Foo:
    x = int


def int_multiple_of_3(x: int) -> DataValidationResult:
    if x % 3 == 0:
        return DataValidationResult.ok()
    return DataValidationResult.error("must be a multiple of 3")


def make_possible_custom_attributes() -> PossibleFiatAttributes:
    custom_attrs = PossibleFiatAttributes("Foo")
    custom_attrs.add_explained_attribute(
        name="xrange",
        type_=tuple,
        explanation="Range for xrange",
        default_value=(0, 5),
        tuple_types=(int, int),
    )
    custom_attrs.add_explained_section("Validated attributes")
    custom_attrs.add_explained_attribute(
        name="m",
        type_=int,
        explanation="Multiple of 3",
        default_value=3,
        data_validation_function=int_multiple_of_3,
    )
    return custom_attrs


def test_possible_custom_attr_validation() -> None:
    possible_custom_attrs = make_possible_custom_attributes()

    r = possible_custom_attrs.validate_custom_attrs({"xrange": (0, 5)})
    assert r.is_valid

    # Test with wrong key: disabled, too much trouble
    # r = possible_custom_attrs.validate_custom_attrs({"badkey": 0})
    # assert not r.is_valid

    # Test with wrong type
    r = possible_custom_attrs.validate_custom_attrs({"xrange": 0})
    assert not r.is_valid

    # Test with wrong tuple len
    r = possible_custom_attrs.validate_custom_attrs({"xrange": (0, 5, 10)})
    assert not r.is_valid

    # Test with wrong tuple type
    r = possible_custom_attrs.validate_custom_attrs({"xrange": (0, "string!")})
    assert not r.is_valid

    # Test with good value (multiple of 3)
    r = possible_custom_attrs.validate_custom_attrs({"m": 9})
    assert r.is_valid

    # Test with wrong value (not multiple of 3)
    r = possible_custom_attrs.validate_custom_attrs({"m": 4})
    assert not r.is_valid
    assert "must be a multiple of 3" in r.error_message


def test_custom_attr_doc() -> None:
    possible_custom_attrs = make_possible_custom_attributes()
    doc = possible_custom_attrs.documentation()
    code_utils.assert_are_codes_equal(
        doc,
        """
    Available custom attributes for Foo:
    --------------------------------------------------------------------------------
    +--------+-----------------+-----------+--------------------------+
    | Name   | Type            | Default   | Explanation              |
    +========+=================+===========+==========================+
    | xrange | tuple[int, int] | (0, 5)    | Range for xrange         |
    +--------+-----------------+-----------+--------------------------+
    |        |                 |           | **Validated attributes** |
    +--------+-----------------+-----------+--------------------------+
    | m      | int             | 3         | Multiple of 3            |
    +--------+-----------------+-----------+--------------------------+
    """,
    )

    example_usage = possible_custom_attrs.example_usage("param")
    # print(example_usage)
    code_utils.assert_are_codes_equal(
        example_usage,
        """
        param__xrange = (0, 5),
        #  Validated attributes
        param__m = 3
    """,
    )


def test_possible_custom_attr_in_function() -> None:
    class FooWithGui(AnyDataWithGui[Foo]):
        def __init__(self) -> None:
            super().__init__(Foo)

        @staticmethod
        def possible_custom_attributes() -> PossibleFiatAttributes | None:
            custom_attrs = PossibleFiatAttributes("Foo")
            custom_attrs.add_explained_attribute(
                name="xrange", type_=tuple, explanation="Range for xrange", default_value=(0, 5), tuple_types=(int, int)
            )
            return custom_attrs

    fl.register_type(Foo, FooWithGui)

    #
    # Test register a function with correct custom attributes
    #
    @fl.with_fiat_attributes(foo__xrange=(5, 10))
    def f(foo: Foo) -> Foo:
        return foo

    f_gui = fl.FunctionWithGui(f)
    custom_attrs = f_gui.param("foo").data_with_gui.fiat_attributes
    assert "xrange" in custom_attrs
    assert custom_attrs["xrange"] == (5, 10)
