import fiatlight


def main() -> None:
    from dataclasses import dataclass

    @dataclass
    class MyParam:
        x: int = 3
        y: str = "Hello"

    from fiatlight.fiat_togui import register_dataclass

    register_dataclass(MyParam)

    def f(param: MyParam) -> None:
        pass

    fiatlight.fiat_run(f)


if __name__ == "__main__":
    main()
