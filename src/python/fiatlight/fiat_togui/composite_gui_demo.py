from enum import Enum


def sandbox_optional() -> None:
    from fiatlight import fiat_run_graph, FunctionsGraph

    def foo(x: int | None) -> int:
        if x is None:
            return 0
        else:
            return x + 2

    graph = FunctionsGraph.from_function_composition([foo])
    fiat_run_graph(graph)


def sandbox_enum() -> None:
    from fiatlight import fiat_run_graph, FunctionsGraph

    class MyEnum(Enum):
        A = 1
        B = 2
        C = 3

    def foo(x: MyEnum) -> int:
        return x.value

    graph = FunctionsGraph.from_function_composition([foo])
    fiat_run_graph(graph)


if __name__ == "__main__":
    # sandbox_optional()
    sandbox_enum()
