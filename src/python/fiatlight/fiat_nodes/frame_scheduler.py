from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable

from imgui_bundle import imgui


class FramePhase(Enum):
    """Point within `FunctionsGraphGui.draw()` at which a scheduled action runs.

    The phase matters as much as the frame: each deferred action needs a specific
    render context to be valid. See the matching `run_due` pump sites in
    `FunctionsGraphGui.draw()`.
    """

    # In-node semaphore set, before ed.begin: node-vs-focused flags resolve to the node ones.
    BEFORE_ED_BEGIN = auto()
    # Between ed.begin / ed.end: `set_node_position` / `set_group_size` are valid here.
    INSIDE_ED = auto()
    # After ed.end(): `navigate_to_content` is valid only outside the editor block.
    AFTER_ED_END = auto()


@dataclass
class _ScheduledAction:
    key: str
    phase: FramePhase
    delay_frames: int
    fn: Callable[[], None]
    # Frame at which this action was first seen by a matching `run_due` pump.
    # None until then. It is anchored lazily (not at schedule time) because
    # scheduling may happen outside any imgui frame, e.g. during a headless
    # `load_workspace_from_json`, where `imgui.get_frame_count()` is invalid.
    anchored_frame: int | None = None


class FrameScheduler:
    """Run one-shot callbacks at a chosen frame and render phase.

    Replaces per-action "pending" fields on the GUI class: each action's data
    rides in its closure instead of a named attribute. A mandatory `key` makes
    the queue self-documenting and gives replace-on-reschedule semantics (a new
    schedule with the same key drops the previous one, mirroring how a single
    pending field used to be overwritten).

    Pump it with `run_due(phase)` at each render phase inside `draw()`. Only
    `run_due` reads the imgui frame count, so `schedule` is safe to call outside
    a frame (e.g. while loading a workspace headlessly).
    """

    def __init__(self) -> None:
        self._actions: list[_ScheduledAction] = []

    def schedule(
        self,
        key: str,
        fn: Callable[[], None],
        *,
        phase: FramePhase,
        delay_frames: int = 0,
    ) -> None:
        """Run `fn` once, at the `phase` pump reached `delay_frames` frames after
        the first pump that observes it (delay 0 = the next pump). Replaces any
        pending action sharing `key`."""
        self.cancel(key)
        self._actions.append(_ScheduledAction(key=key, phase=phase, delay_frames=delay_frames, fn=fn))

    def cancel(self, key: str) -> None:
        """Drop a pending action by key (e.g. its target node was deleted)."""
        self._actions = [a for a in self._actions if a.key != key]

    def clear(self) -> None:
        """Drop every pending action (e.g. the graph was emptied)."""
        self._actions = []

    def pending_keys(self) -> list[str]:
        """Keys of the currently-queued actions, in insertion order. For
        debugging the queue (and assertions in tests)."""
        return [a.key for a in self._actions]

    def run_due(self, phase: FramePhase) -> None:
        """Run + remove every action for `phase` whose delay has elapsed, in
        insertion order. Anchors each action's countdown on the first pump that
        observes it. Actions scheduled *during* this call are anchored only on a
        later pump, so self-rescheduling chains do not re-enter here."""
        frame = imgui.get_frame_count()
        due: list[_ScheduledAction] = []
        for a in self._actions:
            if a.phase != phase:
                continue
            if a.anchored_frame is None:
                a.anchored_frame = frame
            if frame - a.anchored_frame >= a.delay_frames:
                due.append(a)
        if not due:
            return
        due_ids = {id(a) for a in due}
        self._actions = [a for a in self._actions if id(a) not in due_ids]
        for action in due:
            action.fn()
