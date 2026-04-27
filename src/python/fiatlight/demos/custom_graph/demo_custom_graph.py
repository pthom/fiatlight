import fiatlight as fl


def main() -> None:
    """Demo: run the graph composer with a tagged palette of demo functions.

    The demo functions don't declare `fiat_tags` themselves, so we tag them
    at the registration site via `fl.add_fiat_attributes` before handing
    them to `fl.run_graph_composer`.
    """
    from fiatlight.demos.math import all_functions as all_math_functions
    from fiatlight.demos.images import all_functions as all_image_functions
    from fiatlight.demos.string import all_functions as all_string_functions
    from fiatlight.fiat_kits.fiat_ai import invoke_sdxl_turbo

    functions: list[fl.fiat_types.Function] = []

    def _tag_and_extend(fns: list[fl.fiat_types.Function], tags: list[str]) -> None:
        for f in fns:
            fl.add_fiat_attributes(f, fiat_tags=tags)
        functions.extend(fns)

    _tag_and_extend(all_math_functions(), ["math"])
    _tag_and_extend(all_image_functions(), ["images"])
    _tag_and_extend(all_string_functions(), ["string"])

    fl.add_fiat_attributes(invoke_sdxl_turbo, fiat_tags=["ai", "images"])
    functions.append(invoke_sdxl_turbo)

    fl.run_graph_composer(functions=functions)


if __name__ == "__main__":
    main()
