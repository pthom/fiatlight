import fiatlight as fl
from fiatlight.demos.tutorials.sort_competition.numbers_generator import make_random_number_list

# Add Fiat attribute to the function make_random_number_list
#   - invoke_manually=True: the function will not be called automatically
#   - invoke_always_dirty=True: the function will be called even if the input has not changed
#     (so that we can re-launch the generation of random numbers, and the sorting algorithms)
fl.add_fiat_attributes(
    make_random_number_list,
    label="Generate random numbers",
    invoke_manually=True,
    invoke_always_dirty=True,
)

# Run our function with Fiatlight
fl.run(make_random_number_list)
