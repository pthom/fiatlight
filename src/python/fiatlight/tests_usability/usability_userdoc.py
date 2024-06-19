import fiatlight as fl


def usability_with_md_docstring() -> None:
    @fl.with_fiat_attributes(doc_display=True, doc_markdown=True, doc_show_source=True)
    def f(x: int) -> int:
        """# This is a markdown docstring

        Image types
        -----------
        Fiatlight provides several synonyms for Numpy arrays that denote different types of
        images. Each of these types will be displayed by the image widget.
        """
        return x + 1

    fl.run(f)


def usability_with_md_doc_user() -> None:
    @fl.with_fiat_attributes(
        doc_display=True,
        doc_markdown=True,
        doc_show_source=False,
        doc_user="""# This is a markdown docstring
        Fiatlight provides several synonyms for Numpy arrays that denote different types of
        images. Each of these types will be displayed by the image widget.
        """,
    )
    def f2(x: int) -> int:
        return x + 1

    fl.run(f2)


if __name__ == "__main__":
    # usability_with_md_docstring()
    usability_with_md_doc_user()
