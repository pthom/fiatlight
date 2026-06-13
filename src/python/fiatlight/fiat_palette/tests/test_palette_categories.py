"""Tests for fiat_category + optional-tags + category filtering in the palette."""
import fiatlight as fl
from fiatlight.fiat_utils.fiat_attributes_decorator import add_fiat_tags
from fiatlight.fiat_palette.palette import FunctionPalette, PaletteFilter


@fl.with_fiat_attributes(fiat_tags=["blur"], fiat_category="image")
def img_fn(x: int) -> int:
    return x


@fl.with_fiat_attributes(fiat_tags=["token"], fiat_category="text")
def txt_fn(x: int) -> int:
    return x


def untagged_fn(x: int) -> int:
    return x


def test_untagged_function_does_not_raise_and_defaults_to_other() -> None:
    # Previously this raised; now it is accepted and grouped under "other".
    p = FunctionPalette()
    p.add_function(untagged_fn)
    (fi,) = p._functions
    assert fi.tags == ["other"]
    assert fi.category == "other"


def test_category_is_read_and_defaults() -> None:
    p = FunctionPalette()
    p.add_function(img_fn)
    p.add_function(untagged_fn)
    by_name = {fi.name: fi for fi in p._functions}
    assert by_name["img_fn"].category == "image"
    assert by_name["untagged_fn"].category == "other"


def test_categories_set_and_scoped_tags() -> None:
    p = FunctionPalette()
    p.add_function(img_fn)
    p.add_function(txt_fn)
    assert p.categories_set() == ["image", "text"]
    assert p.tags_set("image") == ["blur"]
    assert p.tags_set("text") == ["token"]
    assert p.tags_set() == ["blur", "token"]


def test_filter_by_category() -> None:
    p = FunctionPalette()
    p.add_function(img_fn)
    p.add_function(txt_fn)
    filt = PaletteFilter(selected_category="image")
    result = [fi.name for fi in p.filter(filt)]
    assert result == ["img_fn"]


def test_add_fiat_tags_merges_without_duplicates() -> None:
    @fl.with_fiat_attributes(fiat_tags=["a"])
    def f(x: int) -> int:
        return x

    add_fiat_tags(f, "b", "a", "cv2")
    assert getattr(f, "fiat_tags") == ["a", "b", "cv2"]
