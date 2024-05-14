import fiatlight
from fiatlight.fiat_togui.dataclass_gui import DataclassGui
from fiatlight import register_type


def main() -> None:
    from dataclasses import dataclass

    @dataclass
    class MyParam:
        x: int = 3
        y: str = "Hello"

    register_type(MyParam, lambda: DataclassGui.from_dataclass_type(MyParam))

    def f(param: MyParam) -> None:
        pass

    fiatlight.fiat_run(f)


if __name__ == "__main__":
    main()
