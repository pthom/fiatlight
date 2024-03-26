from typing import TypeVar, Generic, TypeAlias, Type


T = TypeVar("T")
RegistryIndex: TypeAlias = int


class AutoRegistry(Generic[T]):
    """A registry that automatically creates the keys when they are not found.
    The keys are of type RegistryIndex, which is a type alias for int."""

    _registry: dict[RegistryIndex, T]
    _item_class: Type[T]

    def __init__(self, item_class: Type[T]) -> None:
        self._registry = {}
        self._item_class = item_class

    def get(self, key: RegistryIndex) -> T:
        if key not in self._registry:
            self._registry[key] = self._create_new()
        return self._registry[key]

    def _create_new(self) -> T:
        return self._item_class()

    def __getitem__(self, key: RegistryIndex) -> T:
        return self.get(key)

    def __setitem__(self, key: RegistryIndex, value: T) -> None:
        self._registry[key] = value

    def __contains__(self, key: RegistryIndex) -> bool:
        return key in self._registry


def sandbox() -> None:
    class Foo:
        a: int

        def __init__(self, a: int = 0):
            self.a = a

        def __str__(self) -> str:
            return f"Foo(a={self.a})"

    registry = AutoRegistry(Foo)
    # print(registry[0].a)
    f = registry._create_new()  # noqa
    print(f)


if __name__ == "__main__":
    sandbox()
