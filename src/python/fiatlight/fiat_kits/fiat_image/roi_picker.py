"""Interactive ROI picker — lets the user drag a rectangle over an image.

Usage:
    picker = RoiPicker()
    graph.add_function(picker.bind())
    # downstream consumers receive a Rect2D each time the rect is updated.
"""

from typing import Optional, Tuple

import numpy as np
from imgui_bundle import ImVec2, imgui, immvision

from fiatlight.fiat_core.function_with_gui import FunctionWithGui

from .image_types import ImageU8
from .rect2d_type import Rect2D


_HANDLE_SCREEN_SIZE = 6.0
_OUTLINE_COLOR = 0xFF00FFFF  # ABGR yellow
_HANDLE_COLOR = 0xFFFFFFFF  # ABGR white


class RoiPicker:
    """Callable that exposes an `(image: ImageU8) -> Rect2D` node with a
    custom output `present` letting the user drag a rectangle on top of
    the incoming image."""

    rect: Rect2D
    _image: Optional[ImageU8]
    _initialized: bool
    _params: immvision.ImageParams
    _drag_state: Optional[str]
    _drag_anchor: Optional[Tuple[int, int]]
    _drag_anchor_rect: Optional[Rect2D]
    _last_returned_rect: Optional[Rect2D]

    def __init__(self) -> None:
        self.rect = Rect2D(x=0, y=0, w=0, h=0)
        self._image = None
        self._initialized = False
        self._params = immvision.ImageParams()
        self._params.image_display_size = (400, 0)
        self._params.zoom_with_mouse_wheel = True
        self._params.pan_with_mouse = True
        self._params.show_options_button = False
        self._params.show_zoom_buttons = False
        self._params.show_school_paper_background = False
        self._drag_state = None
        self._drag_anchor = None
        self._drag_anchor_rect = None
        self._last_returned_rect = None

    # ------------------------------------------------------------------
    # Function
    # ------------------------------------------------------------------

    def __call__(self, image: ImageU8) -> Rect2D:
        self._image = image
        if not self._initialized:
            h, w = image.shape[:2]
            self.rect = Rect2D(x=w // 4, y=h // 4, w=w // 2, h=h // 2)
            self._initialized = True
        else:
            self._clamp_to(image)
        snap = self.rect.model_copy()
        self._last_returned_rect = snap
        return snap

    def _clamp_to(self, image: np.ndarray) -> None:
        h, w = image.shape[:2]
        x = max(0, min(self.rect.x, w - 1))
        y = max(0, min(self.rect.y, h - 1))
        rw = max(1, min(self.rect.w, w - x))
        rh = max(1, min(self.rect.h, h - y))
        self.rect = Rect2D(x=x, y=y, w=rw, h=rh)

    # ------------------------------------------------------------------
    # GUI
    # ------------------------------------------------------------------

    def _px_to_screen(self, x_px: float, y_px: float, origin: ImVec2) -> Tuple[float, float]:
        m = self._params.zoom_pan_matrix
        sx = m[0][0] * x_px + m[0][1] * y_px + m[0][2]
        sy = m[1][0] * x_px + m[1][1] * y_px + m[1][2]
        return origin.x + sx, origin.y + sy

    def _present(self, _rect: Rect2D) -> None:
        if self._image is None:
            imgui.text("Connect an image input")
            return

        immvision.image("##roi-picker", self._image, self._params)
        widget_min = imgui.get_item_rect_min()

        x1s, y1s = self._px_to_screen(float(self.rect.x), float(self.rect.y), widget_min)
        x2s, y2s = self._px_to_screen(float(self.rect.x + self.rect.w), float(self.rect.y + self.rect.h), widget_min)

        dl = imgui.get_window_draw_list()
        dl.add_rect(ImVec2(x1s, y1s), ImVec2(x2s, y2s), _OUTLINE_COLOR, thickness=2.0)
        for cx, cy in ((x1s, y1s), (x2s, y1s), (x1s, y2s), (x2s, y2s)):
            dl.add_rect_filled(
                ImVec2(cx - _HANDLE_SCREEN_SIZE / 2, cy - _HANDLE_SCREEN_SIZE / 2),
                ImVec2(cx + _HANDLE_SCREEN_SIZE / 2, cy + _HANDLE_SCREEN_SIZE / 2),
                _HANDLE_COLOR,
            )

        self._handle_mouse(x1s, y1s, x2s, y2s)
        imgui.text(f"x={self.rect.x}  y={self.rect.y}  w={self.rect.w}  h={self.rect.h}")

    def _handle_mouse(self, x1s: float, y1s: float, x2s: float, y2s: float) -> None:
        mi = self._params.mouse_info
        # Mouse-up always ends the drag, even if the cursor left the image.
        if imgui.is_mouse_released(0):
            if self._image is not None:
                self._clamp_to(self._image)
            self._drag_state = None
            self._drag_anchor = None
            self._drag_anchor_rect = None
            return

        if not mi.is_mouse_hovering and self._drag_state is None:
            return

        mp = mi.mouse_position_displayed
        mx_px, my_px = int(mp[0]), int(mp[1])

        # Hit-test corner handles in SCREEN coords (handles have a fixed screen size).
        screen_pos = imgui.get_io().mouse_pos
        sx, sy = screen_pos.x, screen_pos.y
        hovered_corner: Optional[str] = None
        for name, cx, cy in (("NW", x1s, y1s), ("NE", x2s, y1s), ("SW", x1s, y2s), ("SE", x2s, y2s)):
            if abs(sx - cx) <= _HANDLE_SCREEN_SIZE and abs(sy - cy) <= _HANDLE_SCREEN_SIZE:
                hovered_corner = name
                break

        inside = self.rect.x <= mx_px <= self.rect.x + self.rect.w and self.rect.y <= my_px <= self.rect.y + self.rect.h

        if imgui.is_mouse_clicked(0) and mi.is_mouse_hovering:
            if hovered_corner is not None:
                self._drag_state = f"resizing-{hovered_corner}"
                self._drag_anchor = (mx_px, my_px)
                self._drag_anchor_rect = self.rect.model_copy()
            elif inside:
                self._drag_state = "moving"
                self._drag_anchor = (mx_px, my_px)
                self._drag_anchor_rect = self.rect.model_copy()
            else:
                self._drag_state = "creating"
                self._drag_anchor = (mx_px, my_px)
                self.rect = Rect2D(x=mx_px, y=my_px, w=1, h=1)
        elif imgui.is_mouse_down(0) and self._drag_state is not None:
            self._update_drag(mx_px, my_px)

    def _update_drag(self, mx: int, my: int) -> None:
        if self._drag_state is None or self._drag_anchor is None:
            return
        ax, ay = self._drag_anchor
        if self._drag_state == "moving" and self._drag_anchor_rect is not None:
            r = self._drag_anchor_rect
            self.rect = Rect2D(x=r.x + (mx - ax), y=r.y + (my - ay), w=r.w, h=r.h)
        elif self._drag_state == "creating":
            self.rect = Rect2D(
                x=min(ax, mx),
                y=min(ay, my),
                w=max(1, abs(mx - ax)),
                h=max(1, abs(my - ay)),
            )
        elif self._drag_state.startswith("resizing-") and self._drag_anchor_rect is not None:
            corner = self._drag_state.split("-")[1]
            r = self._drag_anchor_rect
            x1, y1 = r.x, r.y
            x2, y2 = r.x + r.w, r.y + r.h
            dx, dy = mx - ax, my - ay
            if "W" in corner:
                x1 += dx
            if "E" in corner:
                x2 += dx
            if "N" in corner:
                y1 += dy
            if "S" in corner:
                y2 += dy
            self.rect = Rect2D(x=min(x1, x2), y=min(y1, y2), w=max(1, abs(x2 - x1)), h=max(1, abs(y2 - y1)))

    # ------------------------------------------------------------------
    # Reactivity & persistence
    # ------------------------------------------------------------------

    def _on_heartbeat(self) -> bool:
        """Tell fiatlight to re-invoke when the user has dragged the rect."""
        if self._last_returned_rect is None:
            return False
        cur = self.rect
        last = self._last_returned_rect
        if (cur.x, cur.y, cur.w, cur.h) != (last.x, last.y, last.w, last.h):
            return True
        return False

    def _save_to_dict(self, _value: Rect2D) -> dict:  # type: ignore[type-arg]
        return {"x": self.rect.x, "y": self.rect.y, "w": self.rect.w, "h": self.rect.h, "init": self._initialized}

    def _load_from_dict(self, data: dict) -> Rect2D:  # type: ignore[type-arg]
        self.rect = Rect2D(
            x=int(data.get("x", 0)), y=int(data.get("y", 0)), w=int(data.get("w", 0)), h=int(data.get("h", 0))
        )
        self._initialized = bool(data.get("init", False))
        return self.rect.model_copy()

    # ------------------------------------------------------------------
    # Wiring
    # ------------------------------------------------------------------

    def bind(self) -> FunctionWithGui:
        """Build a `FunctionWithGui` with the custom present + reactivity hooks."""
        fnw = FunctionWithGui(self.__call__)
        fnw.function_name = "select_roi"
        out_gui = fnw._outputs_with_gui[0].data_with_gui
        out_gui.callbacks.present = self._present
        out_gui.callbacks.present_collapsible = False
        out_gui.callbacks.present_str = lambda r: f"Rect2D(x={r.x},y={r.y},{r.w}x{r.h})"
        out_gui.callbacks.on_heartbeat = self._on_heartbeat
        out_gui.callbacks.save_to_dict = self._save_to_dict
        out_gui.callbacks.load_from_dict = self._load_from_dict
        return fnw
