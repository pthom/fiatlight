from .number_list import NumbersList
from .sort_algorithms import set_aborting
from enum import Enum
import numpy as np
import fiatlight as fl
from pydantic import BaseModel, Field


class GenerationType(str, Enum):
    """Different types of generation"""

    RANDOM = "Random"
    INCREASING = "Increasing"
    DECREASING = "Decreasing"
    HAT = "Hat"


# Register our BaseModel, i.e. associate it with a GUI provided by Fiatlight
# We also add fiat_attributes, which are options for the GUI, and enable to set the range of the sliders, the labels, etc.
#
# Note: if we do not want to "pollute" the data definition code with Fiatlight-specific code,
#       we could have used the function fl.register_base_model instead of the decorator
#       somewhere else in the code, e.g. in the main function, like this:
#            fl.register_base_model(NumbersGenerationOptions, nb_values__range=(1, 100_000), ...)
@fl.base_model_with_gui_registration(
    # Options for the nb_values member
    nb_values__range=(1, 100_000),  # range of the number of values. When the range is provided, a slider is displayed
    nb_values__slider_logarithmic=True,  # use a logarithmic scale for the slider
    nb_values__label="Nb values",  # label of the widget
    # Options for the seed member
    seed__label="Random seed",
    seed__edit_type="knob",  # use a knob to edit the value
    # Options for the generation_type member
    generation_type__label="Generation type",
)
class NumbersGenerationOptions(BaseModel):
    nb_values: int = 10  # number of values in the list

    # seed for the random number generator
    # `ge` and `le` signify that pydantic will validate that the value is greater or equal to 0 and less or equal to 100
    # Fiatlight will detect their presence, and set the range of the slider accordingly!
    seed: int = Field(default=1, ge=0, le=100)

    generation_type: GenerationType = GenerationType.RANDOM  # type of generation


def make_random_number_list(options: NumbersGenerationOptions | None = None) -> NumbersList:
    """Create an unordered set of numbers between 1 and a given maximum.
    Depending on the options, the numbers can be generated in increasing, decreasing or random order.
    """
    if options is None:
        options = NumbersGenerationOptions()
    import random

    random.seed(options.seed)
    all_numbers = list(range(1, options.nb_values + 1))
    if options.generation_type == GenerationType.RANDOM:
        random.shuffle(all_numbers)
    elif options.generation_type == GenerationType.INCREASING:
        pass
    elif options.generation_type == GenerationType.DECREASING:
        all_numbers.reverse()
    elif options.generation_type == GenerationType.HAT:
        if options.nb_values % 2 == 0:
            options.nb_values += 1
        evens = list(range(1, options.nb_values, 2))
        odds = list(range(options.nb_values - 1, 2, -2))
        all_numbers = evens + odds

    set_aborting(False)
    return NumbersList(np.array(all_numbers))
