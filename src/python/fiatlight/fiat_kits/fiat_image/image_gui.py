from fiatlight.fiat_utils.fiat_attributes_decorator import with_fiat_attributes
from fiatlight.fiat_types import JsonDict, ImagePath, FiatAttributes, Unspecified, UnspecifiedValue
from fiatlight.fiat_core import AnyDataWithGui, PossibleFiatAttributes
from fiatlight.fiat_kits.fiat_image.image_types import Image, ImageU8
from fiatlight.fiat_utils.cache_per_imgui_view import CachePerImGuiView
from imgui_bundle import immvision, imgui, ImVec2
from imgui_bundle import portable_file_dialogs as pfd, hello_imgui

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


class _ImagePossibleAttributes(PossibleFiatAttributes):
    def __init__(self) -> None:
        super().__init__("fiat_image.ImageWithGui")

        # def attr(name: str, type_: type, explanation: str, type_details: str | None = None) -> None:
        #     self.add_explained_attribute(name, type_, explanation, type_details=type_details)

        attr = self.add_explained_attribute

        # Main attributes
        self.add_explained_section("Main attributes for the image viewer")
        attr("only_display", bool, "Only display the image, no info displayed, no zoom, no pan", default_value=False)
        attr(
            "image_display_size",
            tuple,
            "Initial size of the displayed image (width, height). One of them can be 0",
            default_value=(200, 0),
            tuple_types=(int, int),
        )
        attr(
            "zoom_key",
            str,
            "Key to zoom in the image. All images with the same zoom key will be zoomed together",
            default_value="z",
        )
        attr(
            "is_color_order_bgr",
            bool,
            "Color order is BGR (default is True). OpenCV uses BGR by default, unfortunately.",
            default_value=True,
        )
        attr(
            "can_resize",
            bool,
            "Can resize the image by dragging the mouse at the bottom right corner",
            default_value=True,
        )

        # Channels
        self.add_explained_section("Channels")
        attr("show_channels", bool, "Show channels", default_value=False)
        attr("channel_layout_vertically", bool, "Layout channels vertically", default_value=False)

        # Zoom & Pan
        self.add_explained_section("Zoom & Pan")
        attr("pan_with_mouse", bool, "Pan with mouse", default_value=True)
        attr("zoom_with_mouse_wheel", bool, "Zoom with mouse wheel", default_value=True)

        # Info on Image
        self.add_explained_section("Info displayed on image")
        attr(
            "show_school_paper_background",
            bool,
            "Show school paper background, when the image is unzoomed",
            default_value=True,
        )
        attr("show_alpha_channel_checkerboard", bool, "Show alpha channel checkerboard", default_value=True)
        attr("show_grid", bool, "Show grid with the zoom level is high", default_value=True)
        attr("draw_values_on_zoomed_pixels", bool, "Draw values on pixels, when the zoom is high", default_value=True)

        # Info displayed under the image
        self.add_explained_section("Info displayed under the image")
        attr("show_image_info", bool, "Show image info, i.e image size and type", default_value=True)
        attr(
            "show_pixel_info",
            bool,
            "Show pixel info, i.e. show pixel value and position under the mouse",
            default_value=True,
        )

        # Control buttons under the image
        self.add_explained_section("Control buttons under the image")
        attr("show_zoom_buttons", bool, "Show zoom buttons", default_value=True)
        attr("show_options_panel", bool, "Show options panel", default_value=True)
        attr("show_options_button", bool, "Show options button", default_value=True)
        attr(
            "show_inspect_button",
            bool,
            "Show the inspect button, that enables to open a large version of image in the Image Inspector",
            default_value=True,
        )


_IMAGE_POSSIBLE_ATTRIBUTES = _ImagePossibleAttributes()


class ImagePresenter:
    # Cached image and channels
    image: Image
    image_channels: Sequence[Image]
    # Cache
    need_refresh_cache_per_view: CachePerImGuiView[bool]
    # User preferences below
    image_params: ImagePresenterParams
    show_channels: bool = False
    channel_layout_vertically: bool = False
    only_display: bool = False
    size_when_only_display: ImVec2
    show_inspect_button: bool = True
    was_inspect_window_opened_on_first_log = False

    _was_image_size_fiat_attr_handled: bool = False

    def __init__(self) -> None:
        self.image_params = default_image_params()
        self.size_when_only_display = ImVec2(200, 0)
        self.need_refresh_cache_per_view = CachePerImGuiView("ImagePresenter_need_refresh", True)

    def handle_fiat_attrs(self, fiat_attrs: dict[str, Any]) -> None:
        if "image_display_size" in fiat_attrs:
            image_display_size = fiat_attrs["image_display_size"]

            # We only take into account the custom attribute if it was not already handled,
            # so that the user can resize the image with the mouse after setting the image_display_size
            # (except if can_resize is False)
            shall_take_into_account = True
            if self.image_params.can_resize:
                shall_take_into_account = not self._was_image_size_fiat_attr_handled
            if shall_take_into_account:
                self.image_params.image_display_size = tuple(image_display_size)
                self.size_when_only_display = ImVec2(image_display_size[0], image_display_size[1])
                self._was_image_size_fiat_attr_handled = True

        if "show_channels" in fiat_attrs:
            self.show_channels = fiat_attrs["show_channels"]
        if "channel_layout_vertically" in fiat_attrs:
            self.channel_layout_vertically = fiat_attrs["channel_layout_vertically"]
        if "only_display" in fiat_attrs:
            self.only_display = fiat_attrs["only_display"]
        if "zoom_key" in fiat_attrs:
            self.image_params.zoom_key = fiat_attrs["zoom_key"]
        if "can_resize" in fiat_attrs:
            self.image_params.can_resize = fiat_attrs["can_resize"]
        if "pan_with_mouse" in fiat_attrs:
            self.image_params.pan_with_mouse = fiat_attrs["pan_with_mouse"]
        if "zoom_with_mouse_wheel" in fiat_attrs:
            self.image_params.zoom_with_mouse_wheel = fiat_attrs["zoom_with_mouse_wheel"]
        if "show_school_paper_background" in fiat_attrs:
            self.image_params.show_school_paper_background = fiat_attrs["show_school_paper_background"]
        if "show_alpha_channel_checkerboard" in fiat_attrs:
            self.image_params.show_alpha_channel_checkerboard = fiat_attrs["show_alpha_channel_checkerboard"]
        if "show_grid" in fiat_attrs:
            self.image_params.show_grid = fiat_attrs["show_grid"]
        if "draw_values_on_zoomed_pixels" in fiat_attrs:
            self.image_params.draw_values_on_zoomed_pixels = fiat_attrs["draw_values_on_zoomed_pixels"]
        if "show_image_info" in fiat_attrs:
            self.image_params.show_image_info = fiat_attrs["show_image_info"]
        if "show_pixel_info" in fiat_attrs:
            self.image_params.show_pixel_info = fiat_attrs["show_pixel_info"]
        if "show_zoom_buttons" in fiat_attrs:
            self.image_params.show_zoom_buttons = fiat_attrs["show_zoom_buttons"]
        if "show_options_panel" in fiat_attrs:
            self.image_params.show_options_panel = fiat_attrs["show_options_panel"]
        if "show_options_button" in fiat_attrs:
            self.image_params.show_options_button = fiat_attrs["show_options_button"]
        if "show_inspect_button" in fiat_attrs:
            self.show_inspect_button = fiat_attrs["show_inspect_button"]

    def set_image(self, image: Image) -> None:
        self.image = image
        self.need_refresh_cache_per_view.set_for_all_views(True)
        if len(image.shape) == 3 or len(image.shape) == 4:
            self.image_channels = cv2.split(image)  # type: ignore

    def _show_image_inspector_on_first_call(self) -> None:
        if not self.was_inspect_window_opened_on_first_log:
            hello_imgui.get_runner_params().docking_params.dockable_window_of_name("Image Inspector").is_visible = True
            self.was_inspect_window_opened_on_first_log = True

    def _gui_channels(self) -> None:
        need_refresh = self.need_refresh_cache_per_view.get_for_current_view()
        for i, image_channel in enumerate(self.image_channels):
            imgui.push_id(str(i))
            label = f"channel {i}"
            imgui.begin_group()
            if self.only_display:
                immvision.image_display_resizable(
                    label_id=label,
                    mat=image_channel,
                    refresh_image=need_refresh,
                    resizable=self.image_params.can_resize,
                    size=self.size_when_only_display,
                    show_options_button=False,
                )
            else:
                self.image_params.refresh_image = need_refresh
                immvision.image(label, image_channel, self.image_params)
            if self.show_inspect_button and not self.only_display:
                if imgui.small_button("Inspect"):
                    global _INSPECT_ID
                    immvision.inspector_add_image(image_channel, f"inspect {_INSPECT_ID} _ channel {i}")
                    self._show_image_inspector_on_first_call()
                    _INSPECT_ID += 1
            imgui.end_group()
            if not self.channel_layout_vertically:
                imgui.same_line()
            imgui.pop_id()
        if not self.channel_layout_vertically:
            imgui.new_line()
        self.need_refresh_cache_per_view.set_for_current_view(False)

    def _gui_image(self) -> None:
        need_refresh = self.need_refresh_cache_per_view.get_for_current_view()
        if self.only_display:
            immvision.image_display_resizable(
                "##output",
                self.image,
                refresh_image=need_refresh,
                resizable=self.image_params.can_resize,
                size=self.size_when_only_display,
                show_options_button=False,
            )
        else:
            self.image_params.refresh_image = need_refresh
            immvision.image("##output", self.image, self.image_params)

        self.need_refresh_cache_per_view.set_for_current_view(False)

        if self.show_inspect_button and not self.only_display:
            if imgui.small_button("Inspect"):
                global _INSPECT_ID
                immvision.inspector_add_image(self.image, f"inspect {_INSPECT_ID}")
                self._show_image_inspector_on_first_call()
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
    """A highly sophisticated GUI for displaying and analysing images. Zoom/Pan, show channels, show pixel values, sync zoom accross images, etc."""

    image_presenter: ImagePresenter
    open_file_dialog: Optional[pfd.open_file]

    def __init__(self, image: Image | Unspecified = UnspecifiedValue) -> None:
        super().__init__(Image)  # type: ignore
        self.value = image
        self.image_presenter = ImagePresenter()
        self.open_file_dialog = None
        self.callbacks.edit = self.edit
        self.callbacks.present = self.present
        self.callbacks.on_change = self.on_change
        self.callbacks.default_value_provider = lambda: np.zeros((1, 1, 3), dtype=np.uint8)  # type: ignore
        self.callbacks.present_str = self.present_str
        self.callbacks.save_gui_options_to_json = self.save_gui_options_to_json
        self.callbacks.load_gui_options_from_json = self.load_gui_options_from_json
        self.callbacks.present_collapsible = True
        self.callbacks.on_fiat_attributes_changed = self.on_fiat_attributes_changes
        self.callbacks.present_detachable = True
        self.callbacks.edit_detachable = True

    @staticmethod
    def possible_fiat_attributes() -> PossibleFiatAttributes | None:
        return _IMAGE_POSSIBLE_ATTRIBUTES

    def on_fiat_attributes_changes(self, fiat_attrs: FiatAttributes) -> None:
        self.image_presenter.handle_fiat_attrs(fiat_attrs)

    def edit(self, value: Image) -> tuple[bool, Image]:
        from fiatlight.fiat_kits.fiat_image.imread_rgb import imread_rgb

        changed = False
        if imgui.button("Select image file"):
            # self.open_file_dialog = pfd.open_file(
            #     "Select image file", filters=["*.png", "*.jpg", "*.jpeg", "*.bmp", "*.tga"]
            # )
            self.open_file_dialog = pfd.open_file("Select image file")
        if self.open_file_dialog is not None and self.open_file_dialog.ready():
            if len(self.open_file_dialog.result()) == 1:
                image_file = self.open_file_dialog.result()[0]
                new_image = imread_rgb(image_file)
                if new_image is not None:
                    value = new_image
                    changed = True
            self.open_file_dialog = None
        return changed, value

    def present(self, _image: Image) -> None:
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


@with_fiat_attributes(
    image_file__label="Select Image",
    max_image_size__range=(1, 3000),
    max_image_size__label="Max Image Size",
    max_image_size__tooltip="If the image with or height is larger than this size, it will be resized",
    label="Image from file",
)
def image_source(image_file: ImagePath, max_image_size: int | None = None) -> ImageU8:
    """A simple function that reads an image from a file and optionally resizes it if it is too large.

    Since image_file is of type ImagePath, it will be displayed as a file picker in the GUI
    (if not linked to another function).
    """
    from fiatlight.fiat_kits.fiat_image.imread_rgb import imread_rgb

    image = imread_rgb(image_file)

    if max_image_size is not None:
        if image.shape[0] > max_image_size or image.shape[1] > max_image_size:
            k = max_image_size / max(image.shape[0], image.shape[1])
            assert k > 0.0
            image = cv2.resize(image, None, fx=k, fy=k)  # type: ignore
    return image
