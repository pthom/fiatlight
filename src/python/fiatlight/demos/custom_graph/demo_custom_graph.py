import fiatlight as fl
from fiatlight.fiat_runner.functions_collection import FunctionsCollection


def add_functions_to_collection(collection: FunctionsCollection) -> None:
    # Add some functions to the collection
    from fiatlight.demos.math import all_functions as all_math_functions
    from fiatlight.demos.images import all_functions as all_image_functions
    from fiatlight.demos.string import all_functions as all_string_functions
    from fiatlight.fiat_kits.fiat_ai import invoke_sdxl_turbo

    collection.add_function_list(all_math_functions(), ["math"])
    collection.add_function_list(all_image_functions(), ["images"])
    collection.add_function_list(all_string_functions(), ["string"])
    collection.add_function(invoke_sdxl_turbo, ["ai", "images"])


def main() -> None:
    graph = fl.FunctionsGraph.create_empty()
    params = fl.FiatRunParams()
    params.customizable_graph = True

    gui = fl.fiat_runner.FiatGui(graph, params)

    functions_collection = gui._functions_collection_gui.functions_collection
    add_functions_to_collection(functions_collection)

    gui.run()


if __name__ == "__main__":
    main()
