"""Given a snippet of code, run the corresponding application and save a screenshot. """
from dataclasses import dataclass

from fiatlight import fiat_config
from fiatlight import fiat_image
from imgui_bundle import hello_imgui, imgui
import cv2
import os

PythonCode = str
ImageFile = str
MdLine = str
MdLines = list[str]

_NODES_BOUNDING: imgui.internal.ImRect | None = None

_TOKEN_SNIPPET = "*Visual example: "


@dataclass
class MarkdownLinesWithSnippetCode:
    token_line: MdLine | None
    snippet_code: PythonCode | None
    remaining_lines: MdLines


def set_screenshot_bounds(bounds: imgui.internal.ImRect) -> None:
    global _NODES_BOUNDING
    _NODES_BOUNDING = bounds


def _record_snippet_screenshot(snippet_code: PythonCode) -> fiat_image.ImageU8_3:
    fiat_config.get_fiat_config().is_recording_snippet_screenshot = True
    exec(snippet_code)
    fiat_config.get_fiat_config().is_recording_snippet_screenshot = False
    last_screen: fiat_image.ImageU8_3 = hello_imgui.final_app_window_screenshot()  # type: ignore
    boundings = _NODES_BOUNDING

    # Extract the image part
    if boundings is not None:
        last_screen = last_screen[  # type: ignore
            int(boundings.min.y) : int(boundings.max.y),
            int(boundings.min.x) : int(boundings.max.x),
        ]

    return last_screen


def save_snippet_screenshot(snippet_code: PythonCode, output_file: ImageFile) -> None:
    img = _record_snippet_screenshot(snippet_code)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # type: ignore
    ratio_resize = 0.5
    img = cv2.resize(img, (0, 0), fx=ratio_resize, fy=ratio_resize)  # type: ignore
    cv2.imwrite(output_file, img)


def _read_md_file(md_file: str) -> MdLines:
    file_content = open(md_file, "r").read()
    file_lines = file_content.split("\n")
    return file_lines


def _is_snippet_start(line: str) -> bool:
    return line.startswith(_TOKEN_SNIPPET)


def _split_md_around_snippets(file_lines: MdLines) -> list[MdLines]:
    parts: list[MdLines] = []
    current_part: list[MdLine] = []
    for line in file_lines:
        if _is_snippet_start(line):
            if current_part:
                parts.append(current_part)
            current_part = [line]
        else:
            current_part.append(line)
    parts.append(current_part)
    return parts


def _snippet_image_file_name(md_file: str, md_lines: MarkdownLinesWithSnippetCode) -> tuple[str, str]:
    """Return the image file name for the snippet: full path, relative path."""
    md_folder = os.path.dirname(md_file)
    md_basename = os.path.basename(md_file)
    # remove extension
    md_basename = os.path.splitext(md_basename)[0]
    image_folder = md_basename
    os.makedirs(md_folder + "/" + image_folder, exist_ok=True)

    images_prefix = image_folder + "/"

    # token_line look like
    # *Visual example: a function with a float parameter, and no specific range*
    token_line = md_lines.token_line
    assert token_line is not None
    # Remove token
    token_line = token_line.replace(_TOKEN_SNIPPET, "")  #
    # replace spaces and special characters by _
    filename = images_prefix
    for c in token_line:
        if c.isalnum():
            filename += c
        else:
            filename += "_"

    relative_path = filename + ".jpg"
    full_path = os.path.join(md_folder, relative_path)
    return relative_path, full_path


def _extract_markdown_lines_with_snippet_code(file_lines: MdLines) -> MarkdownLinesWithSnippetCode:
    # The md lines should look like a snippet:
    #
    # *Visual example: a function with a float parameter, and no specific range*    # token_line (0)
    #     ```python                                          (1)
    #     import math
    #     import fiatlight
    #
    #     def my_asin(x: float = 0.5) -> float:
    #         return math.asin(x)
    #
    #
    #     fiatlight.fiat_run(my_asin)
    #     ```                                                (6)
    #   Some other text
    #   on multiple lines

    if len(file_lines) == 0:
        return MarkdownLinesWithSnippetCode(None, None, [])
    if not _is_snippet_start(file_lines[0]):
        return MarkdownLinesWithSnippetCode(None, None, file_lines)

    # 1. Extract the token line
    token_line = file_lines[0]

    # 2. Extract the snippet code
    assert len(file_lines) >= 4  # at least 4 lines: token_line, ```python, code, ```
    assert file_lines[1].strip() == "```python"
    line_idx = 2
    snippet_code = []
    while line_idx < len(file_lines) and file_lines[line_idx].strip() != "```":
        snippet_code.append(file_lines[line_idx])
        line_idx += 1

    # 3. Extract the remaining lines
    remaining_lines = file_lines[line_idx + 1 :]

    # 4. Return the extracted parts
    return MarkdownLinesWithSnippetCode(token_line, "\n".join(snippet_code), remaining_lines)


def add_screenshots_to_markdown_file(markdown_file: str) -> None:
    file_lines = _read_md_file(markdown_file)

    # split the lines in parts beginning with the token
    snippet_parts = _split_md_around_snippets(file_lines)

    # process each part
    list_markdown_lines_with_snippet_code = [_extract_markdown_lines_with_snippet_code(part) for part in snippet_parts]

    all_markdown_lines = []

    # process each part
    for markdown_lines_with_snippet_code in list_markdown_lines_with_snippet_code:
        if markdown_lines_with_snippet_code.snippet_code is None:
            all_markdown_lines.extend(markdown_lines_with_snippet_code.remaining_lines)
        else:
            has_already_image = False

            assert markdown_lines_with_snippet_code.token_line is not None
            all_markdown_lines.append(markdown_lines_with_snippet_code.token_line)
            all_markdown_lines.append("```python")
            all_markdown_lines.extend(markdown_lines_with_snippet_code.snippet_code.split("\n"))
            all_markdown_lines.append("```")

            if len(markdown_lines_with_snippet_code.remaining_lines) > 0:
                if markdown_lines_with_snippet_code.remaining_lines[0].startswith("![image]("):
                    has_already_image = True
            if not has_already_image:
                image_file_relative, image_file_full = _snippet_image_file_name(
                    markdown_file, markdown_lines_with_snippet_code
                )
                save_snippet_screenshot(markdown_lines_with_snippet_code.snippet_code, image_file_full)
                all_markdown_lines.append("![image](" + image_file_relative + ")")

            all_markdown_lines.extend(markdown_lines_with_snippet_code.remaining_lines)

    # write the new content
    new_content = "\n".join(all_markdown_lines)
    # markdown_file_new = markdown_file + ".new.md"
    with open(markdown_file, "w") as f:
        f.write(new_content)
