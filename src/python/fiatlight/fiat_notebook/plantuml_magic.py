# inspired from https://github.com/jbn/iplantuml

# Download plantuml from https://github.com/plantuml/plantuml/releases/download/v1.2024.4/plantuml-lgpl-1.2024.4.jar

import os
import uuid
import subprocess
from IPython.core.magic import register_cell_magic, register_line_magic
from IPython.display import SVG


if "PLANTUMLPATH" in os.environ:
    PLANTUMLPATH = os.environ["PLANTUMLPATH"]
else:
    PLANTUMLPATH = "/usr/local/bin/plantuml.jar"


def _plantuml(uml_content: str, use_local: bool) -> SVG:
    base_name = str(uuid.uuid4())
    shall_retain_file = False
    uml_path = base_name + ".uml"
    svg_filename = base_name + ".svg"

    with open(uml_path, "w") as fp:
        fp.write(uml_content)

    try:
        if use_local:
            if not os.path.exists(PLANTUMLPATH):
                raise FileNotFoundError(
                    f"""
                    PlantUML not found at {PLANTUMLPATH}: please place plantuml.jar there,
                    or set environment variable PLANTUMLPATH to the path of the plantuml.jar file.
                    """
                )
            cmd = ["java", "-splash:no", "-jar", PLANTUMLPATH, "-tsvg", uml_path]
        else:
            cmd = ["plantweb", "--format", "auto", uml_path]
        # print(f"cmd={cmd}")
        subprocess.check_call(cmd, shell=False, stderr=subprocess.STDOUT, stdout=subprocess.DEVNULL)
        svg_object = SVG(filename=svg_filename)  # type: ignore
    finally:
        if not shall_retain_file:
            if os.path.exists(uml_path):
                os.unlink(uml_path)
            if os.path.exists(svg_filename):
                os.unlink(svg_filename)

    return svg_object


@register_cell_magic  # type: ignore
def plantuml_web(_magic_args: str, cell: str) -> SVG:
    return _plantuml(cell, use_local=False)


@register_cell_magic  # type: ignore
def plantuml_local(_magic_args: str, cell: str) -> SVG:
    return _plantuml(cell, use_local=True)


@register_line_magic  # type: ignore
def plantuml_include(_magic_args: str) -> SVG:
    uml_code = f"""
@startuml
!include {_magic_args}
@enduml
    """
    return _plantuml(uml_code, use_local=True)
