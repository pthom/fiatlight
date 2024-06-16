def sandbox_optional() -> None:
    import fiatlight as fl

    def foo(x: int | None) -> int:
        if x is None:
            return 0
        else:
            return x + 2

    graph = fl.FunctionsGraph.from_function_composition([foo])
    fl.run(graph)


if __name__ == "__main__":
    sandbox_optional()
