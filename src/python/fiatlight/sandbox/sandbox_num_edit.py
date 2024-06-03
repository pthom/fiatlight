import fiatlight


def float_times_2(x: float) -> float:
    """Dummy function to test the versatile float input widget"""
    return x * 2


def int_times_2(x: int) -> float:
    """Dummy function to test the versatile int input widget"""
    return x * 2


def main() -> None:
    from fiatlight import FunctionsGraph

    graph = FunctionsGraph()
    graph.add_function(int_times_2)
    graph.add_function(float_times_2)

    fiatlight.run(graph)


if __name__ == "__main__":
    main()
