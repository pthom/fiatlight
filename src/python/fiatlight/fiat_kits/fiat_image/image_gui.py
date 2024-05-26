import fiatlight
from fiatlight.fiat_types import JsonDict, ImagePath, Int_0_1000, CustomAttributesDict
from fiatlight.fiat_core import AnyDataWithGui, PossibleCustomAttributes
from fiatlight.fiat_kits.fiat_image.image_types import Image, ImageU8
from imgui_bundle import immvision, imgui
from imgui_bundle import portable_file_dialogs as pfd

from typing import Optional, Sequence, TypeAlias, Any
import numpy as np
import cv2
import json


ImagePresenterParams: TypeAlias = immvision.ImageParams


def _save_image_params_to_json(image_params: ImagePresenterParams) -> JsonDict:
    json_str = immvision.image_params_to_json(image_params)
    json_dict: JsonDict = json.loads(json_str)
    return json_dict


def _load_image_params_from_json(data: JsonDict, image_params: ImagePresenterParams) -> None:
    json_str = json.dumps(data)
    immvision.fill_image_params_from_json(json_str, image_params)


_INSPECT_ID: int = 0


def default_image_params() -> ImagePresenterParams:
    r = ImagePresenterParams()
    r.image_display_size = (200, 0)
    r.zoom_key = "z"
    return r


class _ImagePossibleAttributes(PossibleCustomAttributes):
    def __init__(self) -> None:
        super().__init__()

        def attr(name: str, type_: type, explanation: str, type_details: str | None = None) -> None:
            self.add_explained_attribute(name, type_, explanation, type_details=type_details)

        # Main attributes
        self.add_explained_section("Main attributes for the image viewer")
        attr("only_display", bool, "Only display the image, no info displayed, no zoom, no pan (default is False)")
        attr(
            "image_display_size",
            tuple,
            "Initial size of the displayed image (width, height). One of them can be 0 (default is (200, 0))",
            type_details="(int, int)",
        )
        attr(
            "zoom_key",
            str,
            'Key to zoom in the image. All images with the same zoom key will be zoomed together (default is "z")',
        )
        attr(
            "is_color_order_bgr",
            bool,
            "Color order is BGR (default is True). OpenCV uses BGR by default, unfortunately.",
        )
        attr(
            "can_resize",
            bool,
            "Can resize the image by dragging the mouse at the bottom right corner (default is True)",
        )

        # Channels
        self.add_explained_section("Channels")
        attr("show_channels", bool, "Show channels (default is False)")
        attr("channel_layout_vertically", bool, "Layout channels vertically (default is False)")

        # Zoom & Pan
        self.add_explained_section("Zoom & Pan")
        attr("pan_with_mouse", bool, "Pan with mouse (default is True)")
        attr("zoom_with_mouse_wheel", bool, "Zoom with mouse wheel (default is True)")

        # Info on Image
        self.add_explained_section("Info displayed on image")
        attr(
            "show_school_paper_background",
            bool,
            "Show school paper background, when the image is unzoomed (default is True)",
        )
        attr("show_alpha_channel_checkerboard", bool, "Show alpha channel checkerboard (default is True)")
        attr("show_grid", bool, "Show grid with the zoom level is high (default is True)")
        attr("draw_values_on_zoomed_pixels", bool, "Draw values on pixels, when the zoom is high (default is True)")

        # Info displayed under the image
        self.add_explained_section("Info displayed under the image")
        attr("show_image_info", bool, "Show image info, i.e image size and type (default is True)")
        attr(
            "show_pixel_info",
            bool,
            "Show pixel info, i.e. show pixel value and position under the mouse (default is True)",
        )

        # Control buttons under the image
        self.add_explained_section("Control buttons under the image")
        attr("show_zoom_buttons", bool, "Show zoom buttons (default is True)")
        attr("show_options_panel", bool, "Show options panel (default is True)")
        attr("show_options_button", bool, "Show options button (default is True)")


_IMAGE_POSSIBLE_ATTRIBUTES = _ImagePossibleAttributes()


def image_possible_attributes_documentation() -> str:
    return _IMAGE_POSSIBLE_ATTRIBUTES.documentation()


class ImagePresenter:
    # Cached image and channels
    image: Image
    image_channels: Sequence[Image]
    # User preferences below
    image_params: ImagePresenterParams
    show_channels: bool = False
    channel_layout_vertically: bool = False
    only_display: bool = False

    _was_image_size_custom_attr_handled: bool = False

    def __init__(self) -> None:
        self.image_params = default_image_params()

    def handle_custom_attrs(self, custom_attrs: dict[str, Any]) -> None:
        _IMAGE_POSSIBLE_ATTRIBUTES.raise_exception_if_bad_custom_attrs(custom_attrs, "fiat_image.ImageWithGui")

        if "image_display_size" in custom_attrs:
            image_display_size = custom_attrs["image_display_size"]
            if not isinstance(image_display_size, (tuple, list)):
                raise ValueError("image_display_size should be a tuple or a list")
            if len(image_display_size) != 2:
                raise ValueError("image_display_size should have two elements")
            if not isinstance(image_display_size[0], int) or not isinstance(image_display_size[1], int):
                raise ValueError("image_display_size elements should be integers")

            # We only take into account the custom attribute if it was not already handled,
            # so that the user can resize the image with the mouse after setting the image_display_size
            # (except if can_resize is False)
            shall_take_into_account = True
            if self.image_params.can_resize:
                shall_take_into_account = not self._was_image_size_custom_attr_handled
            if shall_take_into_account:
                self.image_params.image_display_size = tuple(image_display_size)
                self._was_image_size_custom_attr_handled = True

        if "show_channels" in custom_attrs:
            self.show_channels = custom_attrs["show_channels"]
        if "channel_layout_vertically" in custom_attrs:
            self.channel_layout_vertically = custom_attrs["channel_layout_vertically"]
        if "only_display" in custom_attrs:
            self.only_display = custom_attrs["only_display"]
        if "zoom_key" in custom_attrs:
            self.image_params.zoom_key = custom_attrs["zoom_key"]
        if "can_resize" in custom_attrs:
            self.image_params.can_resize = custom_attrs["can_resize"]
        if "is_color_order_bgr" in custom_attrs:
            self.image_params.is_color_order_bgr = custom_attrs["is_color_order_bgr"]
        if "pan_with_mouse" in custom_attrs:
            self.image_params.pan_with_mouse = custom_attrs["pan_with_mouse"]
        if "zoom_with_mouse_wheel" in custom_attrs:
            self.image_params.zoom_with_mouse_wheel = custom_attrs["zoom_with_mouse_wheel"]
        if "show_school_paper_background" in custom_attrs:
            self.image_params.show_school_paper_background = custom_attrs["show_school_paper_background"]
        if "show_alpha_channel_checkerboard" in custom_attrs:
            self.image_params.show_alpha_channel_checkerboard = custom_attrs["show_alpha_channel_checkerboard"]
        if "show_grid" in custom_attrs:
            self.image_params.show_grid = custom_attrs["show_grid"]
        if "draw_values_on_zoomed_pixels" in custom_attrs:
            self.image_params.draw_values_on_zoomed_pixels = custom_attrs["draw_values_on_zoomed_pixels"]
        if "show_image_info" in custom_attrs:
            self.image_params.show_image_info = custom_attrs["show_image_info"]
        if "show_pixel_info" in custom_attrs:
            self.image_params.show_pixel_info = custom_attrs["show_pixel_info"]
        if "show_zoom_buttons" in custom_attrs:
            self.image_params.show_zoom_buttons = custom_attrs["show_zoom_buttons"]
        if "show_options_panel" in custom_attrs:
            self.image_params.show_options_panel = custom_attrs["show_options_panel"]
        if "show_options_button" in custom_attrs:
            self.image_params.show_options_button = custom_attrs["show_options_button"]

    def set_image(self, image: Image) -> None:
        self.image = image
        self.image_params.refresh_image = True
        if len(image.shape) == 3:
            self.image_channels = cv2.split(image)  # type: ignore

    def _gui_channels(self) -> None:
        for i, image_channel in enumerate(self.image_channels):
            label = f"channel {i}"
            imgui.begin_group()
            immvision.image(label, image_channel, self.image_params)
            if imgui.small_button("Inspect"):
                global _INSPECT_ID
                immvision.inspector_add_image(image_channel, f"inspect {_INSPECT_ID} _ channel {i}")
                _INSPECT_ID += 1
            imgui.end_group()
            if not self.channel_layout_vertically:
                imgui.same_line()
        if not self.channel_layout_vertically:
            imgui.new_line()

    def _gui_image(self) -> None:
        immvision.image("##output", self.image, self.image_params)

        # Cancel refresh_image at the end of the frame
        # We need to delay that in case there is an opened pop-up with the same widget.
        def cancel_refresh_image() -> None:
            self.image_params.refresh_image = False

        if self.image_params.refresh_image:
            fiatlight.fire_once_at_frame_end(cancel_refresh_image)

        if imgui.small_button("Inspect"):
            global _INSPECT_ID
            immvision.inspector_add_image(self.image, f"inspect {_INSPECT_ID}")
            _INSPECT_ID += 1

    def gui(self) -> None:
        assert self.image is not None
        assert len(self.image.shape) > 0
        if len(self.image.shape) == 1:
            imgui.text("Image is 1D, cannot display")
            return
        nb_channels = 1 if len(self.image.shape) == 2 else self.image.shape[2]
        if nb_channels > 1:
            _, self.show_channels = imgui.checkbox("Show channels", self.show_channels)
            if self.show_channels:
                _, self.channel_layout_vertically = imgui.checkbox("Vertical layout", self.channel_layout_vertically)
        if self.show_channels and nb_channels > 1:
            self._gui_channels()
        else:
            self._gui_image()

    def save_gui_options_to_json(self) -> JsonDict:
        image_params = _save_image_params_to_json(self.image_params)
        r = {
            "image_params": image_params,
            "show_channels": self.show_channels,
            "channel_layout_vertically": self.channel_layout_vertically,
        }
        return r

    def load_gui_options_from_json(self, data: JsonDict) -> None:
        image_params = data["image_params"]
        _load_image_params_from_json(image_params, self.image_params)
        self.show_channels = data["show_channels"]
        self.channel_layout_vertically = data["channel_layout_vertically"]


class ImageWithGui(AnyDataWithGui[Image]):
    image_presenter: ImagePresenter
    open_file_dialog: Optional[pfd.open_file]

    def __init__(self) -> None:
        super().__init__(Image)  # type: ignore
        self.image_presenter = ImagePresenter()
        self.open_file_dialog = None
        self.callbacks.edit = self.edit
        self.callbacks.present_custom = self.present_custom
        self.callbacks.on_change = self.on_change
        self.callbacks.default_value_provider = lambda: np.zeros((1, 1, 3), dtype=np.uint8)  # type: ignore
        self.callbacks.present_str = self.present_str
        self.callbacks.save_gui_options_to_json = self.save_gui_options_to_json
        self.callbacks.load_gui_options_from_json = self.load_gui_options_from_json
        self.callbacks.present_custom_popup_possible = True
        self.callbacks.on_custom_attrs_changed = self.on_custom_attrs_changed

    def on_custom_attrs_changed(self, custom_attrs: CustomAttributesDict) -> None:
        self.image_presenter.handle_custom_attrs(custom_attrs)

    def edit(self, value: Image) -> tuple[bool, Image]:
        changed = False
        if imgui.button("Select image file"):
            # self.open_file_dialog = pfd.open_file(
            #     "Select image file", filters=["*.png", "*.jpg", "*.jpeg", "*.bmp", "*.tga"]
            # )
            self.open_file_dialog = pfd.open_file("Select image file")
        if self.open_file_dialog is not None and self.open_file_dialog.ready():
            if len(self.open_file_dialog.result()) == 1:
                image_file = self.open_file_dialog.result()[0]
                new_image = cv2.imread(image_file)
                if new_image is not None:
                    value = new_image  # type: ignore
                    changed = True
            self.open_file_dialog = None
        return changed, value

    def present_custom(self, _image: Image) -> None:
        # _image is not used, as the image is set with on_change
        self.image_presenter.gui()

    @staticmethod
    def present_str(image: Image) -> str:
        r = f"Image {image.shape} {image.dtype}"
        # r += f"\n{image}"
        return r

    def on_change(self, image: Image) -> None:
        self.image_presenter.set_image(image)

    def save_gui_options_to_json(self) -> JsonDict:
        return self.image_presenter.save_gui_options_to_json()

    def load_gui_options_from_json(self, data: JsonDict) -> None:
        self.image_presenter.load_gui_options_from_json(data)


def image_source(image_file: ImagePath, max_image_size: Int_0_1000 | None = None) -> ImageU8:
    """A simple function that reads an image from a file and optionally resizes it if it is too large.

    Since image_file is of type ImagePath, it will be displayed as a file picker in the GUI
    (if not linked to another function).
    """
    image = cv2.imread(image_file)

    if max_image_size is not None:
        if image.shape[0] > max_image_size or image.shape[1] > max_image_size:
            k = max_image_size / max(image.shape[0], image.shape[1])
            assert k > 0.0
            image = cv2.resize(image, None, fx=k, fy=k)
    return image  # type: ignore
