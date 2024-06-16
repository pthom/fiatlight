from fiatlight.fiat_core.any_data_with_gui import AnyDataWithGui
from fiatlight.fiat_types.base_types import FiatAttributes
from typing import Type, Any


def _try_find_range_annotation(
    base_type: Type[Any],
    annotations: list[Any],
    io_gui_type: AnyDataWithGui[Any],
) -> None:
    assert base_type is int or base_type is float

    import annotated_types

    range_min: int | float | None = None
    range_max: int | float | None = None
    for annotation in annotations:
        if isinstance(annotation, annotated_types.Ge):
            range_min = annotation.ge  # type: ignore
        elif isinstance(annotation, annotated_types.Gt):
            if base_type is int:
                range_min = annotation.gt + 1  # type: ignore
            else:
                range_min = annotation.gt  # type: ignore
        elif isinstance(annotation, annotated_types.Le):
            range_max = annotation.le  # type: ignore
        elif isinstance(annotation, annotated_types.Lt):
            if base_type is int:
                range_max = annotation.lt - 1  # type: ignore
            else:
                range_max = annotation.lt  # type: ignore

    if range_min is not None and range_max is not None:
        io_gui_type.merge_fiat_attributes(FiatAttributes({"range": (range_min, range_max)}))


def try_convert_type_annotations_to_fiat_attributes(
    base_type: Type[Any],
    annotations: list[Any],
    io_gui_type: AnyDataWithGui[Any],
) -> None:
    from pydantic import BaseModel  # noqa

    if base_type is int or base_type is float:
        _try_find_range_annotation(base_type, annotations, io_gui_type)

    # for v in annotations:
    #     t = fully_qualified_typename_or_str(type(v))
    #     print(t)
    # pass
