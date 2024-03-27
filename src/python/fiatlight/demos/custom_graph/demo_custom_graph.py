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
    from fiatlight.demos.images.toon_edges import add_toon_edges, image_source
    from fiatlight.demos.images.canny import canny
    from fiatlight.demos.images.oil_paint import oil_paint
    from fiatlight.demos.ai.stable_diffusion_xl_wrapper import stable_diffusion_xl_gui

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

    add_one_function(image_source, ["image"])
    add_one_function(add_toon_edges, ["image"])
    add_one_function(canny, ["image"])
    add_one_function(oil_paint, ["image"])
    add_one_function_factory(stable_diffusion_xl_gui, ["image"])

    gui.run()


if __name__ == "__main__":
    main()
