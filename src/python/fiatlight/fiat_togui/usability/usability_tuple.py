import fiatlight as fl


def f(v: tuple[int, str], v2: tuple[float, float]) -> float:
    return v[0] + len(v[1]) + v2[0] + v2[1]


fl.run(f)
