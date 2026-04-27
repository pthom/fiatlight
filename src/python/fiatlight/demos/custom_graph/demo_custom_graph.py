import fiatlight as fl
from fiatlight.fiat_runner.functions_collection import FunctionsCollection


def _tag_and_add(
    collection: FunctionsCollection,
    fns: list[fl.fiat_types.Function],
    tags: list[str],
) -> None:
    """Bulk-tag a list of demo functions, then add them to the collection.

    `FunctionsCollection.add_function*` no longer accepts a `tags` arg —
    every function must carry its own `fiat_tags` (set via
    `@fl.with_fiat_attributes(fiat_tags=[...])` or `fl.add_fiat_attributes`).
    These demo functions don't declare tags themselves, so we tag them at
    the registration site.
    """
    for f in fns:
        fl.add_fiat_attributes(f, fiat_tags=tags)
    collection.add_function_list(fns)


def add_functions_to_collection(collection: FunctionsCollection) -> None:
    # Add some functions to the collection
    from fiatlight.demos.math import all_functions as all_math_functions
    from fiatlight.demos.images import all_functions as all_image_functions
    from fiatlight.demos.string import all_functions as all_string_functions
    from fiatlight.fiat_kits.fiat_ai import invoke_sdxl_turbo

    _tag_and_add(collection, all_math_functions(), ["math"])
    _tag_and_add(collection, all_image_functions(), ["images"])
    _tag_and_add(collection, all_string_functions(), ["string"])

    fl.add_fiat_attributes(invoke_sdxl_turbo, fiat_tags=["ai", "images"])
    collection.add_function(invoke_sdxl_turbo)


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
