def clamp(value: float, lower_bound: float, upper_bound: float) -> float:
    return max(min(value, upper_bound), lower_bound)


def lerp(a: float, b: float, t: float) -> float:
    return a + t * (b - a)


def unlerp(a: float, b: float, value: float) -> float:
    return (value - a) / (b - a)
