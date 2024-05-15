import fiatlight


def main() -> None:
    from dataclasses import dataclass
    from fiatlight.fiat_types import ImagePath, ImagePath_Save

    @dataclass
    class MyParam:
        image_in: ImagePath
        image_out: ImagePath_Save = "save.png"  # type: ignore
        x: int | None = None
        y: str = "Hello"

    from fiatlight.fiat_togui import register_dataclass

    register_dataclass(MyParam)

    def f(param: MyParam) -> MyParam:
        return param

    fiatlight.fiat_run(f)


if __name__ == "__main__":
    main()
