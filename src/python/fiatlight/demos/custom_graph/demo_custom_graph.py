import fiatlight
from typing import List


def add(a: int, b: int) -> int:
    return a + b


def mul(a: int, b: int) -> int:
    return a * b


def sub(a: int, b: int) -> int:
    return a - b


def int_source(x: int) -> int:
    return x


def main() -> None:
    graph = fiatlight.FunctionsGraph.create_empty()
    params = fiatlight.FiatGuiParams()
    params.customizable_graph = True

    gui = fiatlight.fiat_runner.FiatGui(graph, params)

    # Add some functions to the collection
    from fiatlight.fiat_core import to_function_with_gui
    from fiatlight.fiat_core import FunctionWithGuiFactory
    from fiatlight.fiat_types import Function

    functions_collection = gui._functions_collection_gui.functions_collection

    def add_one_function_factory(f: FunctionWithGuiFactory, tags: List[str]) -> None:
        functions_collection.add_function(f, tags)

    def add_one_function(f: Function, tags: List[str]) -> None:
        def fn_factory() -> fiatlight.FunctionWithGui:
            return to_function_with_gui(f)

        functions_collection.add_function(fn_factory, tags)

    add_one_function(add, ["math"])
    add_one_function(mul, ["math"])
    add_one_function(sub, ["math"])
    add_one_function(int_source, ["math"])

    from fiatlight.fiat_image.fiat_img_proc import split_channels, overlay_alpha_image_precise

    add_one_function(split_channels, ["image"])
    add_one_function(overlay_alpha_image_precise, ["image"])

    # functions_collection.add_function(to_function_with_gui(add), ["math"])
    # functions_collection.add_function(to_function_with_gui(mul), ["math"])
    # functions_collection.add_function(to_function_with_gui(sub), ["math"])
    # functions_collection.add_function(to_function_with_gui(int_source), ["math"])

    # from fiatlight.fiat_image.fiat_img_proc import split_channels, overlay_alpha_image_precise
    #
    # functions_collection.add_function(to_function_with_gui(split_channels), ["image"])
    # functions_collection.add_function(to_function_with_gui(overlay_alpha_image_precise), ["image"])

    gui.run()


if __name__ == "__main__":
    main()
