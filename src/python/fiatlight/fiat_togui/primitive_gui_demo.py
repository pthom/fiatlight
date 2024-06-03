import fiatlight


def main() -> None:
    def f(i: int = 0, f: float = 0.0, s: str = "", b: bool = False) -> None:
        pass

    fiatlight.run(f)


if __name__ == "__main__":
    main()
