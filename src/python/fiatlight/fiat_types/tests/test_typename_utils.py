from fiatlight.fiat_types import typename_utils as tu
from typing import List, NewType


def test_runtime_typename() -> None:
    from fiatlight.fiat_togui.tests.sample_enum import SampleEnum

    assert tu.fully_qualified_runtime_typename(int) == "builtins.int"
    assert tu.base_runtime_typename(int) == "int"

    assert tu.fully_qualified_runtime_typename(list) == "builtins.list"
    assert tu.base_runtime_typename(list) == "list"

    assert tu.fully_qualified_runtime_typename(SampleEnum) == "fiatlight.fiat_togui.tests.sample_enum.SampleEnum"

    assert tu.fully_qualified_runtime_typename(list[int]) == "builtins.list[builtins.int]"
    assert tu.base_runtime_typename(list[int]) == "list[int]"

    assert tu.fully_qualified_runtime_typename(dict[str, int]) == "builtins.dict[builtins.str, builtins.int]"
    assert tu.base_runtime_typename(dict[str, int]) == "dict[str, int]"

    assert (
        tu.fully_qualified_runtime_typename(list[SampleEnum])
        == "builtins.list[fiatlight.fiat_togui.tests.sample_enum.SampleEnum]"
    )
    assert tu.base_runtime_typename(list[SampleEnum]) == "list[SampleEnum]"


def test_generic_typename() -> None:
    assert tu.fully_qualified_generic_typename(list[int]) == "builtins.list[builtins.int]"
    assert tu.base_generic_typename(list[int]) == "list[int]"

    assert tu.fully_qualified_generic_typename(dict[str, int]) == "builtins.dict[builtins.str, builtins.int]"
    assert tu.base_generic_typename(dict[str, int]) == "dict[str, int]"

    assert tu.fully_qualified_generic_typename(int | None) == "types.UnionType[builtins.int, builtins.NoneType]"
    assert tu.base_generic_typename(int | None) == "UnionType[int, NoneType]"


MyNewType = NewType("MyNewType", int)


def test_newtype_typename() -> None:
    assert tu.fully_qualified_newtype_typename(MyNewType) == "fiatlight.fiat_types.tests.test_typename_utils.MyNewType"
    assert tu.base_newtype_typename(MyNewType) == "MyNewType"


def test_typename() -> None:
    assert tu.fully_qualified_typename(int) == "builtins.int"
    assert tu.base_typename(int) == "int"

    assert tu.fully_qualified_typename(list[int]) == "builtins.list[builtins.int]"
    assert tu.base_typename(list[int]) == "list[int]"

    assert tu.fully_qualified_typename(int | None) == "types.UnionType[builtins.int, builtins.NoneType]"
    assert tu.base_typename(int | None) == "UnionType[int, NoneType]"

    from fiatlight.fiat_togui.tests.sample_enum import SampleEnum

    assert (
        tu.fully_qualified_generic_typename(list[SampleEnum])
        == "builtins.list[fiatlight.fiat_togui.tests.sample_enum.SampleEnum]"
    )
    assert tu.base_generic_typename(list[SampleEnum]) == "list[SampleEnum]"

    assert (
        tu.fully_qualified_typename(List[SampleEnum])
        == "builtins.list[fiatlight.fiat_togui.tests.sample_enum.SampleEnum]"
    )
    assert tu.base_typename(List[SampleEnum]) == "list[SampleEnum]"

    assert tu.fully_qualified_typename(MyNewType) == "fiatlight.fiat_types.tests.test_typename_utils.MyNewType"
    assert tu.base_typename(MyNewType) == "MyNewType"


def test_image_types() -> None:
    from fiatlight.fiat_kits.fiat_image import ImageU8_1, ImageU8_2

    _ImageU8_1_name = tu.fully_qualified_typename(ImageU8_1)
    # print(ImageU8_1_name)

    MyImage = ImageU8_1 | ImageU8_2
    _ImageU8_name = tu.fully_qualified_typename(MyImage)
    # print(_ImageU8_name)


test_image_types()
