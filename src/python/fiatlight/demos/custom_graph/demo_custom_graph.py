import fiatlight
from typing import List
from fiatlight.fiat_core import FunctionWithGuiFactory
from fiatlight.fiat_runner.functions_collection import FunctionsCollection


def add_functions_to_collection(collection: FunctionsCollection) -> None:
    # Add some functions to the collection
    from fiatlight.demos.custom_graph.float_functions import all_functions as all_float_functions
    from fiatlight.demos.custom_graph.image_toy_functions import all_functions as all_image_functions
    from fiatlight.demos.images.opencv_wrappers import all_functions as all_opencv_image_functions

    def add_one_function(fn_factory: FunctionWithGuiFactory, tags: List[str]) -> None:
        collection.add_function(fn_factory, tags)

    for f in all_float_functions():
        add_one_function(f, ["math"])

    for f in all_image_functions():
        add_one_function(f, ["images"])

    for f in all_opencv_image_functions():
        add_one_function(f, ["images", "opencv"])


def main() -> None:
    graph = fiatlight.FunctionsGraph.create_empty()
    params = fiatlight.FiatGuiParams()
    params.customizable_graph = True

    gui = fiatlight.fiat_runner.FiatGui(graph, params)

    functions_collection = gui._functions_collection_gui.functions_collection
    add_functions_to_collection(functions_collection)

    gui.run()


if __name__ == "__main__":
    main()
