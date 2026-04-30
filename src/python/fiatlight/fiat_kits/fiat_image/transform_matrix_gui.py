"""GUI registration for `Matrix2x3` and `Matrix3x3` — table-formatted display."""

from imgui_bundle import imgui

from fiatlight.fiat_togui.simple_gui import register_callbacks

from .transform_matrix_types import Matrix2x3, Matrix3x3


def _present_matrix(m: object, rows: int, cols: int) -> None:
    arr = m  # ndarray-like
    if imgui.begin_table("##matrix", cols):
        for i in range(rows):
            imgui.table_next_row()
            for j in range(cols):
                imgui.table_set_column_index(j)
                imgui.text(f"{float(arr[i, j]): .4f}")  # type: ignore[index]
        imgui.end_table()


def _present_matrix2x3(m: Matrix2x3) -> None:
    _present_matrix(m, 2, 3)


def _present_matrix3x3(m: Matrix3x3) -> None:
    _present_matrix(m, 3, 3)


def _present_str_2x3(m: Matrix2x3) -> str:
    return f"Matrix2x3 {tuple(m.shape)} {m.dtype}"


def _present_str_3x3(m: Matrix3x3) -> str:
    return f"Matrix3x3 {tuple(m.shape)} {m.dtype}"


def _register() -> None:
    import numpy as np

    register_callbacks(
        Matrix2x3,
        present=_present_matrix2x3,
        present_str=_present_str_2x3,
        default=lambda: Matrix2x3(np.eye(2, 3, dtype=np.float64)),
    )
    register_callbacks(
        Matrix3x3,
        present=_present_matrix3x3,
        present_str=_present_str_3x3,
        default=lambda: Matrix3x3(np.eye(3, dtype=np.float64)),
    )
