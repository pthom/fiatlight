from enum import Enum


def sandbox_optional() -> None:
    import fiatlight as fl

    def foo(x: int | None) -> int:
        if x is None:
            return 0
        else:
            return x + 2

    graph = fl.FunctionsGraph.from_function_composition([foo])
    fl.run(graph)


def sandbox_enum() -> None:
    import fiatlight as fl

    class MyEnum(Enum):
        A = 1
        B = 2
        C = 3

    def foo(x: MyEnum) -> int:
        return x.value

    graph = fl.FunctionsGraph.from_function_composition([foo])
    fl.run(graph)


if __name__ == "__main__":
    # sandbox_optional()
    sandbox_enum()
