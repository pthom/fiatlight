"""Snapshot-based undo/redo for the function graph.

Each snapshot is a full-graph dict (`save_workspace_to_json()`); the current
state is the top of the undo stack. `undo()` restores the previous snapshot,
`redo()` re-applies. Outputs are derived (recomputed on restore), so they are
not part of a snapshot.

Coalescing of continuous gestures (slider / node drags) is the caller's job:
it calls `reconcile()` only once the graph has settled, so one gesture becomes
one undo step.
"""
import copy
from typing import Callable, List

from fiatlight.fiat_types.base_types import JsonDict

SnapshotFn = Callable[[], JsonDict]
RestoreFn = Callable[[JsonDict], None]


class UndoManager:
    def __init__(self, snapshot_fn: SnapshotFn, restore_fn: RestoreFn, max_depth: int = 50) -> None:
        self._snapshot_fn = snapshot_fn
        self._restore_fn = restore_fn
        self._max_depth = max_depth
        self._undo: List[JsonDict] = []
        self._redo: List[JsonDict] = []

    def reset(self) -> None:
        """Clear history and capture the current graph as the baseline."""
        self._undo = [self._snapshot_fn()]
        self._redo = []

    def reconcile(self) -> bool:
        """Capture a snapshot iff the graph differs from the current top. Call
        only when the graph has settled (no gesture in progress). Returns True if
        a new snapshot was captured.

        After undo()/redo() the graph equals the current top, so a reconcile on
        the next frame is a no-op by dedup — no extra guard needed."""
        snap = self._snapshot_fn()
        if self._undo and self._undo[-1] == snap:
            return False
        self._undo.append(snap)
        if len(self._undo) > self._max_depth:
            self._undo.pop(0)
        self._redo.clear()
        return True

    def current(self) -> JsonDict:
        """The current state (top of the undo stack); {} before the baseline."""
        return self._undo[-1] if self._undo else {}

    def can_undo(self) -> bool:
        return len(self._undo) > 1

    def can_redo(self) -> bool:
        return len(self._redo) > 0

    def undo(self) -> None:
        if not self.can_undo():
            return
        self._redo.append(self._undo.pop())
        self._restore(self._undo[-1])

    def redo(self) -> None:
        if not self.can_redo():
            return
        snap = self._redo.pop()
        self._undo.append(snap)
        self._restore(snap)

    def _restore(self, snap: JsonDict) -> None:
        # Deep-copy so restore_fn mutating the dict can't corrupt the stack.
        self._restore_fn(copy.deepcopy(snap))
