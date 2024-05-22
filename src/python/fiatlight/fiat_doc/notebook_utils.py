import nbformat
from nbformat import NotebookNode
import re
import os
from typing import List
from fiatlight.fiat_doc import code_utils
from dataclasses import dataclass
import difflib


THIS_DIR = os.path.dirname(__file__)
DOC_DIR = os.path.abspath(f"{THIS_DIR}/../doc")


@dataclass
class _WrappedString:
    value: str


@dataclass
class _CompositeMarkdown(_WrappedString):
    pass


@dataclass
class _Markdown(_WrappedString):
    pass


@dataclass
class _Code(_WrappedString):
    pass


class _NotebookContentParts:
    items: List[_Markdown | _Code]

    def __init__(self) -> None:
        self.items = []


def _replace_python_links_by_github_links(
    md_string: str, github_base_path: str = "https://github.com/pthom/fiatlight/tree/refact_io/src/python/fiatlight"
) -> str:
    # The code is available on github at
    #     https://github.com/pthom/fiatlight/tree/refact_io/src/python/fiatlight
    #
    # Any Markdown link to a Python file in the code will be replaced by a link to the corresponding file on github.
    # i.e. a link that looks like
    #    [fiat_image](../fiat_kits/fiat_image/__init__.py)
    # will be replaced by
    #    [fiat_image]({github_base_path}/fiat_kits/fiat_image/__init__.py)

    # Regular expression to find markdown links pointing to python files
    pattern = re.compile(r"\[([^\]]+)\]\(\.\./([^\)]+)\)")

    # Replacement function
    def replace_link(match):  # type: ignore
        link_text = match.group(1)
        relative_path = match.group(2)
        new_url = f"{github_base_path}/{relative_path}"
        return f"[{link_text}]({new_url})"

    # Replace all matching patterns
    return re.sub(pattern, replace_link, md_string)


def _md_to_notebook_content_parts(md_string: _CompositeMarkdown) -> _NotebookContentParts:
    md_string = _CompositeMarkdown(code_utils.unindent_code(md_string.value))
    # Create a new notebook
    notebook_content = _NotebookContentParts()

    # Regular expression to match code blocks
    code_block_re = re.compile(r"```python(.*?)```", re.DOTALL)

    # Split the Markdown string into parts, separating code blocks and Markdown
    parts = code_block_re.split(md_string.value)

    for i, part in enumerate(parts):
        part = code_utils.unindent_code(part, flag_strip_empty_lines=True)
        is_code = i % 2 == 1
        if is_code:
            notebook_content.items.append(_Code(part))
        else:
            part_with_github_links = _replace_python_links_by_github_links(part)
            notebook_content.items.append(_Markdown(part_with_github_links))

    return notebook_content


def _md_to_notebook(md_string: _CompositeMarkdown) -> NotebookNode:
    notebook_content = _md_to_notebook_content_parts(md_string)

    # Create a new notebook
    nb: NotebookNode = nbformat.v4.new_notebook()  # type: ignore
    for item in notebook_content.items:
        if isinstance(item, _Markdown):
            nb.cells.append(nbformat.v4.new_markdown_cell(item.value))  # type: ignore
        else:
            nb.cells.append(nbformat.v4.new_code_cell(item.value))  # type: ignore

    return nb


def _update_notebook_code_cells(notebook: NotebookNode, md_string: _CompositeMarkdown) -> None:
    notebook_content = _md_to_notebook_content_parts(md_string)

    for i, item in enumerate(notebook_content.items):
        if i < len(notebook.cells):
            notebook_cell = notebook.cells[i]
            if isinstance(item, _Code):
                if notebook_cell.cell_type != "code":
                    raise ValueError(f"Cell {i} is not a code cell.")
                notebook_cell.source = item.value
            if isinstance(item, _Markdown):
                if notebook.cells[i].cell_type != "markdown":
                    raise ValueError(f"Cell {i} is not a markdown cell.")
                notebook_cell.source = item.value
        else:
            if isinstance(item, _Code):
                notebook.cells.append(nbformat.v4.new_code_cell(item.value))  # type: ignore
            if isinstance(item, _Markdown):
                notebook.cells.append(nbformat.v4.new_markdown_cell(item.value))  # type: ignore


def _composite_markdown_to_notebook(
    composite_markdown: _CompositeMarkdown, notebook_to_update: NotebookNode | None = None
) -> NotebookNode:
    if notebook_to_update is None:
        notebook = _md_to_notebook(composite_markdown)
    else:
        notebook = notebook_to_update
        _update_notebook_code_cells(notebook, composite_markdown)
    return notebook


def _save_notebook_from_markdown(
    composite_markdown: _CompositeMarkdown, update_existing: bool, notebook_filename: str
) -> None:
    previous_notebook: NotebookNode | None = None
    if update_existing:
        if not os.path.exists(notebook_filename):
            raise ValueError(f"The notebook {notebook_filename} does not exist.")
        try:
            with open(notebook_filename) as f:
                previous_notebook = nbformat.read(f, as_version=4)  # type: ignore
        except Exception as e:
            raise ValueError(f"Error reading the notebook file {notebook_filename}: {e}")

    new_notebook = _composite_markdown_to_notebook(composite_markdown, previous_notebook)
    with open(notebook_filename, "w") as f:
        nbformat.write(new_notebook, f)  # type: ignore


def save_function_or_class_doc_to_notebook(obj: object, update_existing: bool) -> None:
    if not hasattr(obj, "__name__"):
        raise ValueError(f"{obj} does not have a name.")
    obj_name = obj.__name__
    obj_basename = obj_name.split(".")[-1]
    notebook_filename = f"{DOC_DIR}/{obj_basename}.ipynb"

    if obj.__doc__ is None:
        raise ValueError(f"{obj} does not have a docstring.")
    composite_markdown = _CompositeMarkdown(obj.__doc__)
    # Remove first line from the docstring (which is a summary, not intended for the notebook)
    composite_markdown.value = composite_markdown.value.split("\n", 1)[1]

    _save_notebook_from_markdown(composite_markdown, update_existing, notebook_filename)


def add_code_cell_to_notebook(code: str, notebook_filename: str, similarity_threshold: float = 0.9) -> None:
    try:
        with open(notebook_filename) as f:
            notebook = nbformat.read(f, as_version=4)  # type: ignore
    except Exception as e:
        raise ValueError(f"Error reading the notebook file {notebook_filename}: {e}")

    # Check that the code was not already added
    was_updated = False
    for cell in notebook.cells:
        if cell.cell_type == "code":
            similarity = difflib.SequenceMatcher(None, cell.source, code).ratio()
            if similarity >= similarity_threshold:
                cell.source = code
                was_updated = True

    if not was_updated:
        notebook.cells.append(nbformat.v4.new_code_cell(code))  # type: ignore

    with open(notebook_filename, "w") as f:
        nbformat.write(notebook, f)  # type: ignore


def add_obj_code_to_notebook(obj: object, notebook_filename: str) -> None:
    import inspect

    code = inspect.getsource(obj)  # type: ignore
    add_code_cell_to_notebook(code, notebook_filename)


def save_notebook_from_markdown_file(md_filename: str, notebook_filename: str, update_existing: bool) -> None:
    with open(md_filename) as f:
        md_string = f.read()
    composite_markdown = _CompositeMarkdown(md_string)
    _save_notebook_from_markdown(composite_markdown, update_existing, notebook_filename)


def look_at_python_code(obj: object) -> None:
    """Display the Python code of a function or class in a notebook cell."""
    import inspect
    import IPython.display as display

    code = inspect.getsource(obj)  # type: ignore  # noqa
    display.display(display.Code(code, language="python"))  # type: ignore


def display_markdown_from_file(md_filename: str) -> None:
    with open(md_filename) as f:
        content = f.read()
    import IPython.display as idisplay

    idisplay.display(idisplay.Markdown(content))  # type: ignore
