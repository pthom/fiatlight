"""UndoManager logic, driven by a fake in-memory 'graph'."""
from typing import Any, Dict, List

from fiatlight.fiat_runner.undo_manager import UndoManager


class _FakeGraph:
    """A stand-in graph: a dict we snapshot/restore."""

    def __init__(self) -> None:
        self.state: Dict[str, Any] = {"v": 0}
        self.restored: List[Dict[str, Any]] = []

    def snapshot(self) -> Dict[str, Any]:
        return dict(self.state)

    def restore(self, snap: Dict[str, Any]) -> None:
        self.state = dict(snap)
        self.restored.append(dict(snap))


def _mgr() -> tuple[UndoManager, _FakeGraph]:
    g = _FakeGraph()
    m = UndoManager(g.snapshot, g.restore)
    m.reset()
    return m, g


def test_baseline_has_nothing_to_undo() -> None:
    m, _ = _mgr()
    assert not m.can_undo()
    assert not m.can_redo()


def test_reconcile_captures_only_on_change() -> None:
    m, g = _mgr()
    m.reconcile()  # no change since reset
    assert not m.can_undo()
    g.state["v"] = 1
    m.reconcile()
    assert m.can_undo()
    m.reconcile()  # unchanged -> deduped
    assert m.can_undo() and not m.can_redo()


def test_undo_redo_restores_state() -> None:
    m, g = _mgr()
    g.state["v"] = 1
    m.reconcile()
    g.state["v"] = 2
    m.reconcile()

    m.undo()
    assert g.state["v"] == 1
    m.undo()
    assert g.state["v"] == 0
    assert not m.can_undo()
    m.redo()
    assert g.state["v"] == 1
    m.redo()
    assert g.state["v"] == 2
    assert not m.can_redo()


def test_new_change_clears_redo() -> None:
    m, g = _mgr()
    g.state["v"] = 1
    m.reconcile()
    m.undo()
    assert m.can_redo()
    g.state["v"] = 9
    m.reconcile()  # a fresh edit
    assert not m.can_redo()


def test_max_depth_caps_history() -> None:
    g = _FakeGraph()
    m = UndoManager(g.snapshot, g.restore, max_depth=3)
    m.reset()
    for i in range(10):
        g.state["v"] = i + 1
        m.reconcile()
    # at most max_depth snapshots are kept
    assert m._undo and len(m._undo) <= 3  # noqa: SLF001


def test_reconcile_after_undo_is_deduped() -> None:
    # After undo the graph equals the top, so a reconcile captures nothing and
    # keeps redo available (no spurious snapshot).
    m, g = _mgr()
    g.state["v"] = 1
    m.reconcile()
    m.undo()  # restores v=0
    m.reconcile()  # graph == top -> deduped
    assert g.state["v"] == 0
    assert m.can_redo()
