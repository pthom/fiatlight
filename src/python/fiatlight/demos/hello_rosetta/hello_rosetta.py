"""hello_rosetta - Doc for the user interface developer
=====================================================

Given the function below, which includes hints for the graphical user interface developer as well as documentation for the final user, write a program that implements a GUI for this function.

Parameters input:
-----------------
- The age should be entered via a slider.
  It should take into account the hints given in the user documentation.
- The name should be entered via a text input. It should occupy one line only.
  A placeholder "your name..." should be displayed when it is empty.

Output
------
- The program should display the function result as a string. It should be displayed in a text box or label

User documentation:
-------------------
- The documentation inside the function below is a user facing doc and should
  be displayed in an optional tooltip or dialog box that can be opened from the function.
  Bonus points: display the doc with a nice renderer such as a markdown renderer (for example)
"""


def hello_rosetta(name: str, age: int) -> str:
    """hello_rosetta: A function that greets a person by name and age
    ====================================================================
    Args
    ----
    * `name` (str) : The name of the person.
    * `age` (int)  : The age of the person. Should be between 0 and 125
    Returns
    -------
    * `str`        : A greeting message, with a special welcome message for newcomers.

    *Rosetta is an old-fashioned lady, and can only understand non-accentuated latin letters,
    spaces, and "-". Her memory is failing, and she cannot remember more than 10 characters.
    Her keyboard is broken, and she can only type one time the letter 'a' or 'A' per day.*

    Poor Rosetta!
    """

    # Check input, Rosetta is intransigent
    letters_a = list(filter(lambda x: x == "a" or x == "A", name))
    if len(letters_a) > 1:
        return "My keyboard is broken, I can only type one time the letter 'a' or 'A' per day."

    if len(name) == 0:
        return "Please enter your name."
    elif len(name) > 10:
        return "My memory is failing, please enter a name with less than 10 characters."
    elif not name.isalpha():
        return "Hey, I'm an old-fashioned lady, I can only understand non-accentuated latin letters."
    elif not 0 <= age <= 125:
        return "Sure you are not a ghost? Please enter an age between 0 and 125."

    if age == 0:
        return f"Hello, {name}, welcome to the world!"
    elif age == 1:
        return f"Hello, {name}, you are {age} year old."
    else:
        return f"Hello, {name}, you are {age} years old."


# ======================================================================================================

import fiatlight as fl  # noqa


def validate_name(name: str) -> str:
    if len(name) == 0:
        raise ValueError("Please enter your name.")
    if len(name) > 10:
        raise ValueError("No more than 10 characters, please")
    if not name.isalpha():
        raise ValueError("Only non-accentuated latin letters are allowed")
    letters_a = list(filter(lambda x: x == "a" or x == "A", name))
    if len(letters_a) > 1:
        raise ValueError("Only one 'a' or 'A' is allowed")
    return name


fl.add_fiat_attributes(
    hello_rosetta,
    age__range=(0, 125),
    name__hint="Enter your name",
    name__validator=validate_name,
    doc_display=True,
)

fl.run(hello_rosetta)
