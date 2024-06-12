import fiatlight as fl
from fiatlight.fiat_types import PositiveFloat
from fiatlight.fiat_kits.fiat_image import ImageU8_GRAY, ImageU8_3, image_source
from fiatlight.demos.images.opencv_wrappers import canny, dilate, MorphShape, CannyApertureSize
from fiatlight.fiat_kits.fiat_image import overlay_alpha_image
import numpy as np
import cv2


@fl.with_custom_attrs(edges_intensity__range=(0.0, 1.0))
def merge_toon_edges(image: ImageU8_3, edges_images: ImageU8_GRAY, edges_intensity: float = 0.7) -> ImageU8_3:
    """Add toon edges to the image.
    :param image: Image: Input image
    :param edges_images: binary image with edges detected using Canny filter
    :param blur_edges_sigma: Optional sigma value for Gaussian Blur applied to edges (skip if 0)
    :param edges_intensity: Intensity of the edges
    """

    # Create a RGBA image that will be overlayed on the original image
    # Its color will be constant (edges_color) and its alpha channel will be the edges_images
    edges_color = (0, 0, 0)
    overlay_rgba = np.zeros((*image.shape[:2], 4), dtype=np.uint8)
    overlay_rgba[:, :, :3] = edges_color
    overlay_rgba[:, :, 3] = (edges_images * edges_intensity).astype(np.uint8)

    # Overlay the RGBA image on the original image
    r = overlay_alpha_image(image, overlay_rgba)  # type: ignore

    return r


@fl.with_custom_attrs(
    canny_blur_sigma__range=(0.0, 10.0),
    dilate_kernel_size__range=(0, 10),
    dilate_iterations__range=(0, 10),
    blur_edges_sigma__range=(0.0, 10.0),
    edges_intensity__range=(0.0, 1.0),
)
def add_toon_edges(
    image: ImageU8_3,
    canny_t_lower: PositiveFloat = PositiveFloat(1000.0),
    canny_t_upper: PositiveFloat = PositiveFloat(5000.0),
    canny_l2_gradient: bool = True,
    canny_blur_sigma: float = 0.0,
    dilate_kernel_size: int = 2,
    dilate_morph_shape: MorphShape = MorphShape.MORPH_ELLIPSE,
    dilate_iterations: int = 2,
    blur_edges_sigma: float = 0.0,
    edges_intensity: float = 0.8,
) -> ImageU8_3:
    # ) -> ToonEdgesOutput:
    canny_aperture_size = CannyApertureSize.APERTURE_5
    edges = canny(image, canny_t_lower, canny_t_upper, canny_aperture_size, canny_l2_gradient, canny_blur_sigma)
    dilated_edges = dilate(edges, dilate_kernel_size, dilate_morph_shape, dilate_iterations)
    if blur_edges_sigma > 0:
        dilated_edges = cv2.GaussianBlur(dilated_edges, (0, 0), sigmaX=blur_edges_sigma, sigmaY=blur_edges_sigma)  # type: ignore
    image_with_edges = merge_toon_edges(image, dilated_edges, edges_intensity)

    # Add internals for debugging
    from fiatlight.fiat_kits.fiat_image import ImageWithGui
    from fiatlight import AnyDataWithGui

    if not hasattr(add_toon_edges, "fiat_internals"):
        add_toon_edges.fiat_internals: dict[str, AnyDataWithGui] = {  # type: ignore
            "edges": ImageWithGui(),
            "dilated_edges": ImageWithGui(),
            "image_with_edges": ImageWithGui(),
        }
    add_toon_edges.fiat_internals["edges"].value = edges  # type: ignore
    add_toon_edges.fiat_internals["dilated_edges"].value = dilated_edges  # type: ignore
    add_toon_edges.fiat_internals["image_with_edges"].value = image_with_edges  # type: ignore

    # return
    return image_with_edges


def main() -> None:
    fl.run([image_source, add_toon_edges])


if __name__ == "__main__":
    main()
