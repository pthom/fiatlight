"""Tests for `make_simple_gui` and `register_callbacks`."""

from typing import NewType

import pytest

from fiatlight.fiat_core.any_data_gui_callbacks import AnyDataGuiCallbacks
from fiatlight.fiat_togui.gui_registry import gui_factories
from fiatlight.fiat_togui.simple_gui import (
    _CALLBACK_FIELDS,
    make_simple_gui,
    register_callbacks,
)
from fiatlight.fiat_types.typename_utils import fully_qualified_typename


# ---------------------------------------------------------------------------
# make_simple_gui
# ---------------------------------------------------------------------------


class _Plain:
    """A plain class registered through make_simple_gui."""


def test_callback_field_set_matches_dataclass() -> None:
    """Drift guard: kwargs allowlist must mirror AnyDataGuiCallbacks annotations."""
    declared = set(AnyDataGuiCallbacks.__annotations__.keys())
    assert _CALLBACK_FIELDS == declared, (
        f"missing in helper: {declared - _CALLBACK_FIELDS}, " f"extra in helper: {_CALLBACK_FIELDS - declared}"
    )


def test_kwargs_are_applied_to_callbacks() -> None:
    factory = make_simple_gui(_Plain, present_str=lambda v: "P!")
    gui = factory()
    assert gui.callbacks.present_str is not None
    assert gui.callbacks.present_str(_Plain()) == "P!"


def test_unknown_kwarg_raises_typeerror() -> None:
    with pytest.raises(TypeError, match="unknown callback"):
        make_simple_gui(_Plain, totally_invented=lambda: None)


def test_default_alias_targets_default_value_provider() -> None:
    factory = make_simple_gui(_Plain, default=lambda: _Plain())
    gui = factory()
    assert gui.callbacks.default_value_provider is not None
    assert isinstance(gui.callbacks.default_value_provider(), _Plain)


def test_default_and_default_value_provider_conflict() -> None:
    with pytest.raises(TypeError, match="both target"):
        make_simple_gui(
            _Plain,
            default=lambda: _Plain(),
            default_value_provider=lambda: _Plain(),
        )


def test_callbacks_param_form() -> None:
    cb: AnyDataGuiCallbacks[_Plain] = AnyDataGuiCallbacks()
    cb.present_str = lambda v: "via-callbacks"
    factory = make_simple_gui(_Plain, callbacks=cb)
    gui = factory()
    assert gui.callbacks.present_str is not None
    assert gui.callbacks.present_str(_Plain()) == "via-callbacks"


def test_callbacks_param_excludes_perfield_kwargs() -> None:
    cb: AnyDataGuiCallbacks[_Plain] = AnyDataGuiCallbacks()
    with pytest.raises(TypeError, match="either `callbacks=` OR per-field"):
        make_simple_gui(_Plain, callbacks=cb, present_str=lambda v: "x")


def test_collapsible_defaults_false_for_helper() -> None:
    """Helper overrides AnyDataGuiCallbacks defaults: small pins shouldn't collapse."""
    factory = make_simple_gui(_Plain, present_str=lambda v: "x")
    gui = factory()
    assert gui.callbacks.present_collapsible is False
    assert gui.callbacks.edit_collapsible is False


def test_explicit_present_collapsible_true_is_preserved() -> None:
    factory = make_simple_gui(_Plain, present_str=lambda v: "x", present_collapsible=True)
    gui = factory()
    assert gui.callbacks.present_collapsible is True


def test_factory_returns_fresh_instances() -> None:
    factory = make_simple_gui(_Plain, present_str=lambda v: "x")
    a = factory()
    b = factory()
    assert a is not b
    assert a.callbacks is not b.callbacks


# ---------------------------------------------------------------------------
# register_callbacks
# ---------------------------------------------------------------------------


class _RegPlain:
    """A plain class registered via register_callbacks."""


def test_register_callbacks_plain_type() -> None:
    register_callbacks(_RegPlain, present_str=lambda v: "ok")
    typename = fully_qualified_typename(_RegPlain)
    assert gui_factories().can_handle_typename(typename)
    gui = gui_factories().get_factory(typename)()
    assert gui.callbacks.present_str is not None
    assert gui.callbacks.present_str(_RegPlain()) == "ok"


_DocumentedNT = NewType("_DocumentedNT", int)
_DocumentedNT.__doc__ = "Test NewType with a real docstring."


def test_register_callbacks_documented_newtype() -> None:
    register_callbacks(_DocumentedNT, present_str=lambda v: f"int={v}")
    typename = fully_qualified_typename(_DocumentedNT)
    assert gui_factories().can_handle_typename(typename)


_UndocumentedNT = NewType("_UndocumentedNT", int)


def test_register_callbacks_undocumented_newtype_rejected() -> None:
    """register_callbacks routes NewType inputs through the docstring-checking path."""
    with pytest.raises(ValueError, match="docstring"):
        register_callbacks(_UndocumentedNT, present_str=lambda v: "x")


# ---------------------------------------------------------------------------
# Edit-able worked example (smoke test for the spec's MyPoint3D pattern)
# ---------------------------------------------------------------------------


class _MyPoint3D:
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        self.x, self.y, self.z = x, y, z


def _edit_my_point3d(p: _MyPoint3D) -> tuple[bool, _MyPoint3D]:
    # Test edit hook — returns unchanged value, signals no change.
    return False, p


def test_register_callbacks_edit_able_type() -> None:
    register_callbacks(
        _MyPoint3D,
        present_str=lambda p: f"P({p.x}, {p.y}, {p.z})",
        default=lambda: _MyPoint3D(0.0, 0.0, 0.0),
        edit=_edit_my_point3d,
    )
    typename = fully_qualified_typename(_MyPoint3D)
    gui = gui_factories().get_factory(typename)()
    assert gui.callbacks.edit is not None
    assert gui.callbacks.default_value_provider is not None
    p = gui.callbacks.default_value_provider()
    assert isinstance(p, _MyPoint3D) and p.x == 0.0
    assert gui.callbacks.present_str is not None
    assert gui.callbacks.present_str(_MyPoint3D(1, 2, 3)) == "P(1, 2, 3)"
