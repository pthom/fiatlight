from fiatlight.fiat_notebook import notebook_utils
from fiatlight.fiat_doc import code_utils
import nbformat  # noqa


def test_md_to_notebook() -> None:
    md_string = notebook_utils._CompositeMarkdown(
        """
    FunctionWithGui: add GUI to a function
    ========================================
    Introduction
    ------------

    `FunctionWithGui` is ... blah blah ...

        ```python
        import fiatlight as ft
        def foo(a: int, b: float) -> float:
            return a + b
        ft.run(foo)
        ```

    ### Manual creation example:
    ...Blah blah...

        ```python
        import fiatlight as ft
        def blah(a: int) -> int:
            return a * 2
        ```
    """
    )

    notebook = notebook_utils._md_to_notebook(md_string)

    assert notebook.cells[0].cell_type == "markdown"
    code_utils.assert_are_codes_equal(
        notebook.cells[0].source,
        """
        FunctionWithGui: add GUI to a function
        ========================================
        Introduction
        ------------

        `FunctionWithGui` is ... blah blah ...
        """,
    )

    assert notebook.cells[1].cell_type == "code"
    code_utils.assert_are_codes_equal(
        notebook.cells[1].source,
        """
        import fiatlight as ft
        def foo(a: int, b: float) -> float:
            return a + b
        ft.run(foo)
            """,
    )


def test_replace_python_links_by_github_links() -> None:
    s = " a [fiat_image](../fiat_kits/fiat_image/__init__.py)"
    s_gh = notebook_utils._replace_python_links_by_github_links(s)
    assert (
        s_gh
        == " a [fiat_image](https://github.com/pthom/fiatlight/tree/refact_io/src/python/fiatlight/fiat_kits/fiat_image/__init__.py)"
    )
    print("Test passed!")


def test_regex() -> None:
    md = """
    Blah

    ```python
    x = 1
    ```

    Bluh

    ```magic
    y = 2
    z = 3
    ```

    ```python
    y = 2
    ```
    """
    parts = notebook_utils._md_to_notebook_content_parts(notebook_utils._CompositeMarkdown(md))
    assert len(parts.items) == 7

    assert isinstance(parts.items[0], notebook_utils._Markdown)
    assert parts.items[0].value.strip() == "Blah"

    assert isinstance(parts.items[1], notebook_utils._Code)
    assert parts.items[1].language == "python"
    assert parts.items[1].value.strip() == "x = 1"

    assert isinstance(parts.items[2], notebook_utils._Markdown)
    assert parts.items[2].value.strip() == "Bluh"

    assert isinstance(parts.items[3], notebook_utils._Code)
    assert parts.items[3].language == "magic"
    code_utils.assert_are_codes_equal(
        parts.items[3].value,
        """
        y = 2
        z = 3
    """,
    )

    # assert isinstance(parts.items[4], notebook_utils._Code)
    # assert parts.items[4].language == "python"
    # code_utils.assert_are_codes_equal(parts.items[4].value, "y = 2")
