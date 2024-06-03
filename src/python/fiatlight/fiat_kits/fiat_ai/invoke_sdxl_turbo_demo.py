from fiatlight.fiat_kits.fiat_ai import invoke_sdxl_turbo


def main_test_sdxl() -> None:
    import fiatlight

    fiatlight.run(invoke_sdxl_turbo)


if __name__ == "__main__":
    main_test_sdxl()
