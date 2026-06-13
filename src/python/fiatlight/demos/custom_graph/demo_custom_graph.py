import fiatlight as fl


def main() -> None:
    """Demo: run the graph composer with a multi-category palette.

    Combines the cv2 image pack, the math pack and the text pack. Each node
    already carries its `fiat_category` (image / math / text) and intent tags,
    so the palette's category selector and tag chips work out of the box.
    """
    from fiatlight.fiat_kits.fiat_image.cv2_nodes import cv2_nodes
    from fiatlight.fiat_kits.fiat_math import math_nodes
    from fiatlight.fiat_kits.fiat_text import text_nodes
    from fiatlight.fiat_kits.fiat_ai import invoke_sdxl_turbo

    functions: list[fl.fiat_types.Function] = [*cv2_nodes(), *math_nodes(), *text_nodes()]

    fl.add_fiat_attributes(invoke_sdxl_turbo, fiat_tags=["ai"], fiat_category="image")
    functions.append(invoke_sdxl_turbo)

    fl.run_graph_composer(functions=functions)


if __name__ == "__main__":
    main()
