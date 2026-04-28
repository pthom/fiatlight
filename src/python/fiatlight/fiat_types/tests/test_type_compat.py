"""Unit tests for fiatlight.fiat_types.type_compat."""

from typing import Any, NewType, Optional, Union, List

import numpy as np

from fiatlight.fiat_types.type_compat import is_link_compatible, explain_incompatibility


# ---------------------------------------------------------------------------
#  Identical / primitive types
# ---------------------------------------------------------------------------
def test_same_primitive_types_match() -> None:
    assert is_link_compatible(int, int)
    assert is_link_compatible(float, float)
    assert is_link_compatible(str, str)


def test_int_does_not_match_float() -> None:
    """Strict numeric typing: user must add an explicit cast node."""
    assert not is_link_compatible(int, float)
    assert not is_link_compatible(float, int)


def test_int_does_not_match_str() -> None:
    assert not is_link_compatible(int, str)


# ---------------------------------------------------------------------------
#  `Any` escape hatch
# ---------------------------------------------------------------------------
def test_any_accepts_anything() -> None:
    assert is_link_compatible(Any, int)
    assert is_link_compatible(int, Any)
    assert is_link_compatible(Any, Any)


# ---------------------------------------------------------------------------
#  NewType supertype walking (one-directional)
# ---------------------------------------------------------------------------
MyInt = NewType("MyInt", int)
MyMyInt = NewType("MyMyInt", MyInt)


def test_newtype_to_supertype_accepted() -> None:
    assert is_link_compatible(MyInt, int)
    assert is_link_compatible(MyMyInt, MyInt)
    assert is_link_compatible(MyMyInt, int)  # transitive


def test_supertype_to_newtype_rejected() -> None:
    assert not is_link_compatible(int, MyInt)
    assert not is_link_compatible(MyInt, MyMyInt)


def test_sibling_newtypes_rejected() -> None:
    Sibling = NewType("Sibling", int)
    assert not is_link_compatible(MyInt, Sibling)
    assert not is_link_compatible(Sibling, MyInt)


# ---------------------------------------------------------------------------
#  Bound-numbers (fiat_number_types) — they are NewTypes over float/int
# ---------------------------------------------------------------------------
def test_float_0_1_to_float() -> None:
    from fiatlight.fiat_types.fiat_number_types import Float_0_1

    assert is_link_compatible(Float_0_1, float)
    assert not is_link_compatible(float, Float_0_1)


def test_int_0_255_to_int() -> None:
    from fiatlight.fiat_types.fiat_number_types import Int_0_255

    assert is_link_compatible(Int_0_255, int)
    assert not is_link_compatible(int, Int_0_255)


def test_int_0_255_does_not_match_float() -> None:
    from fiatlight.fiat_types.fiat_number_types import Int_0_255

    assert not is_link_compatible(Int_0_255, float)


# ---------------------------------------------------------------------------
#  Optional / Union
# ---------------------------------------------------------------------------
def test_optional_input_accepts_inner() -> None:
    assert is_link_compatible(int, Optional[int])
    assert is_link_compatible(MyInt, Optional[int])  # via supertype


def test_optional_input_rejects_unrelated() -> None:
    assert not is_link_compatible(str, Optional[int])


def test_union_input_accepts_any_member() -> None:
    assert is_link_compatible(int, Union[int, str])
    assert is_link_compatible(str, Union[int, str])
    assert not is_link_compatible(float, Union[int, str])


def test_union_output_requires_all_members_match() -> None:
    """If the producer might emit any of the union, every branch must be legal."""
    assert is_link_compatible(Union[int, MyInt], int)  # both → int via supertype
    assert not is_link_compatible(Union[int, str], int)  # str doesn't match


def test_same_union_on_both_sides_accepted() -> None:
    """Regression: identical Union output -> Union input must accept."""
    U = Union[int, str, float]
    assert is_link_compatible(U, U)


def test_image_full_union_to_itself_accepted() -> None:
    """Regression: this is the case that broke graph reload — an image_source
    output typed `Image` connecting to a consumer typed `Image`."""
    from fiatlight.fiat_kits.fiat_image.image_types import Image

    assert is_link_compatible(Image, Image)


def test_narrow_output_union_to_wider_input_union() -> None:
    """Union[A,B] -> Union[A,B,C]: every output value is a legal input."""
    assert is_link_compatible(Union[int, str], Union[int, str, float])


def test_wider_output_union_to_narrower_input_union_rejected() -> None:
    """Union[A,B,C] -> Union[A,B]: producer might emit C, which input rejects."""
    assert not is_link_compatible(Union[int, str, float], Union[int, str])


# ---------------------------------------------------------------------------
#  Image types — the main motivating use-case
# ---------------------------------------------------------------------------
def test_image_rgb_to_imageu8_3() -> None:
    from fiatlight.fiat_kits.fiat_image.image_types import ImageRgb, ImageU8_3

    assert is_link_compatible(ImageRgb, ImageU8_3)
    assert not is_link_compatible(ImageU8_3, ImageRgb)


def test_image_rgb_to_image() -> None:
    from fiatlight.fiat_kits.fiat_image.image_types import ImageRgb, Image

    assert is_link_compatible(ImageRgb, Image)


def test_image_rgb_to_imageu8() -> None:
    from fiatlight.fiat_kits.fiat_image.image_types import ImageRgb, ImageU8

    assert is_link_compatible(ImageRgb, ImageU8)


def test_image_rgb_does_not_match_image_float() -> None:
    from fiatlight.fiat_kits.fiat_image.image_types import ImageRgb, ImageFloat

    assert not is_link_compatible(ImageRgb, ImageFloat)


def test_image_rgb_does_not_match_image_bgr() -> None:
    """Sibling role types must not auto-link — semantics differ."""
    from fiatlight.fiat_kits.fiat_image.image_types import ImageRgb, ImageBgr

    assert not is_link_compatible(ImageRgb, ImageBgr)
    assert not is_link_compatible(ImageBgr, ImageRgb)


def test_image_u8_to_image_float_rejected() -> None:
    from fiatlight.fiat_kits.fiat_image.image_types import ImageU8, ImageFloat

    assert not is_link_compatible(ImageU8, ImageFloat)


# ---------------------------------------------------------------------------
#  numpy bare-ndarray escape hatch
# ---------------------------------------------------------------------------
def test_bare_ndarray_accepts_image_newtype() -> None:
    from fiatlight.fiat_kits.fiat_image.image_types import ImageRgb

    assert is_link_compatible(np.ndarray, ImageRgb)
    assert is_link_compatible(ImageRgb, np.ndarray)


def test_bare_ndarray_does_not_bridge_two_newtypes() -> None:
    """ImageRgb -> ImageBgr must stay rejected even though both wrap np.ndarray."""
    from fiatlight.fiat_kits.fiat_image.image_types import ImageRgb, ImageBgr

    assert not is_link_compatible(ImageRgb, ImageBgr)


# ---------------------------------------------------------------------------
#  Generics — invariant for now
# ---------------------------------------------------------------------------
def test_list_int_to_list_int() -> None:
    assert is_link_compatible(List[int], List[int])
    assert is_link_compatible(list[int], list[int])


def test_list_int_does_not_match_list_float() -> None:
    assert not is_link_compatible(List[int], List[float])


# ---------------------------------------------------------------------------
#  explain_incompatibility
# ---------------------------------------------------------------------------
def test_explain_empty_when_compatible() -> None:
    assert explain_incompatibility(int, int) == ""


def test_explain_mentions_both_types() -> None:
    msg = explain_incompatibility(int, str)
    assert "int" in msg
    assert "str" in msg
