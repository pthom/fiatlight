import fiatlight as fl
from fiatlight.demos.from_idea_to_app.sort_visualization.numbers_generator import make_random_number_list


# 2. Add fiat attributes that set options for the widgets associated with the function
from fiatlight.demos.from_idea_to_app.sort_visualization.numbers_generator import NumbersGenerationOptions

fl.register_base_model(
    NumbersGenerationOptions,
    nb_values__range=(1, 10_000),  # range of the number of values. When the range is provided, a slider is displayed
    nb_values__slider_logarithmic=True,  # use a logarithmic scale for the slider
    nb_values__label="Nb values",  # label of the widget
    seed__range=(0, 30),  # range of the seed (Note, will be set by Pydantic annotation later)
    seed__label="Random seed",
    generation_type__label="Generation type",
)


# 3. Add Fiat attribute to the function make_random_number_list
#   - invoke_manually=True: the function will not be called automatically
#   - invoke_always_dirty=True: the function will be called even if the input has not changed
#     (so that we can re-launch the generation of random numbers, and the sorting algorithms)
fl.add_fiat_attributes(
    make_random_number_list,
    invoke_manually=True,
    invoke_always_dirty=True,
)

# 4. explain decorators


# Simply run the function with Fiatlight
# 1. Explain fl.run
fl.run(make_random_number_list)
