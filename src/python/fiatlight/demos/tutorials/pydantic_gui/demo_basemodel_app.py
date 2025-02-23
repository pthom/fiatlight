"""A basic example showing how you can use the advanced GUI creation capabilities of Fiatlight,
inside a standalone application.

Here, we demonstrate how to create a GUI for a nested Pydantic model, with custom validation and labels:

we simply call `fl.immediate_edit`, and the GUI will be generated automatically, taking into account the
Pydantic model structure and the customizations and validations we have set.
`"""

import fiatlight as fl
from enum import Enum
from pydantic import BaseModel, Field
from imgui_bundle import immapp


# An Enum which will be associated to a Gui automatically
class TrainingDataType(Enum):
    Test = "test"
    Train = "train"
    Validation = "validation"


# GeographicInfo: a pydantic model, with validation on latitude and longitude
# which will be reflected in the GUI
# (the sliders will be limited to the specified ranges)
@fl.base_model_with_gui_registration()
class GeographicInfo(BaseModel):
    latitude: float = Field(ge=0, le=90, default=0)
    longitude: float = Field(ge=-180, lt=180, default=0)


# A custom validator, which will be used to validate the short description
def validate_short_description(value: str) -> str:
    if len(value) > 30:
        raise ValueError("Description is too long")
    return value


# A second model, which nests the first one (GeographicInfo)
# It also has a validated parameter, via a custom Fiatlight validator
@fl.base_model_with_gui_registration(
    width__range=(0, 2000),
    height__range=(0, 2000),
    description__label="Description",
    description__validator=validate_short_description,
    geo_info__label="Geographic Info",
)
class ImageInfo(BaseModel):
    geo_info: GeographicInfo = GeographicInfo()
    description: str = "Short Description..."
    width: int = 0
    height: int = 0


# A third model, which nests the second one (ImageInfo)
# In total, it has 3 levels: TrainingImage -> ImageInfo -> GeographicInfo
@fl.base_model_with_gui_registration(
    image_path__label="Select Image",
    training_type__label="Training Set",
    info__label="Image Info",
)
class TrainingImage(BaseModel):
    image_path: fl.fiat_types.ImagePath = ""  # type: ignore
    training_type: TrainingDataType = TrainingDataType.Test
    info: ImageInfo = ImageInfo(width=0, height=0)


def main() -> None:
    """Main function, which will be run when the script is executed."""
    training_image = TrainingImage()

    def gui() -> None:
        # Display the GUI: we simply call the GUI object's gui_edit method
        nonlocal training_image
        _changed, training_image = fl.immediate_edit("Training Image", training_image)

    immapp.run(gui)


if __name__ == "__main__":
    main()
