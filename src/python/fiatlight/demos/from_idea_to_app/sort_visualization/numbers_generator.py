from .number_list import NumbersList
from pydantic import BaseModel
from enum import Enum
import numpy as np
import fiatlight as fl


class GenerationType(str, Enum):
    """Enumeration of the different types of generation"""

    RANDOM = "Random"
    INCREASING = "Increasing"
    DECREASING = "Decreasing"


@fl.base_model_with_gui_registration(
    nb_values__range=(1, 10_000),  # range of the number of values. When the range is provided, a slider is displayed
    nb_values__slider_logarithmic=True,  # use a logarithmic scale for the slider
    nb_values__label="Nb values",  # label of the widget
    seed__range=(0, 30),  # range of the seed
    seed__label="Random seed",
    generation_type__label="Generation type",
)
class NumbersGenerationOptions(BaseModel):
    nb_values: int = 10  # number of values in the list
    seed: int = 0  # seed for the random number generator
    generation_type: GenerationType = GenerationType.RANDOM  # type of generation


# Add Fiat attribute to the function make_random_number_list
#   - invoke_manually=True: the function will not be called automatically
#     (you have to click on the "Call Manually" button to call it)
#   - invoke_always_dirty=True: the function can be called even if the input has not changed
#     (so that we can re-launch the generation of random numbers, and the sorting algorithms)
@fl.with_fiat_attributes(
    invoke_manually=True,
    invoke_always_dirty=True,
)
def make_random_number_list(options: NumbersGenerationOptions | None = None) -> NumbersList:
    """Create a random unordered set of numbers between 1 and a given maximum"""
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
    return NumbersList(np.array(all_numbers))
