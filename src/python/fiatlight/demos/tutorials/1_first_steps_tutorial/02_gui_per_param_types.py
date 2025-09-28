import fiatlight as fl
from enum import Enum


class Food(Enum):
    PIZZA = "Pizza"
    BURGER = "Burger"
    SUSHI = "Sushi"


def dummy(
    name: str,
    n: int,
    x: float,
    flag: bool,
    flag2: bool | None = None,
    food: Food = Food.PIZZA,
) -> str:
    """A dummy function, which takes parameters of different types"""
    return f"Hello {name}, you ordered {n} {food.value}(s) for {n * x:.2f}$. Flag1 is {flag}, Flag2 is {flag2}"


fl.run(dummy)
