import fiatlight
from fiatlight.fiat_types import Prompt


def get_prompt(txt: Prompt, a: int) -> str:
    return txt


get_prompt.invoke_automatically = False  # type: ignore


prompt_with_gui = fiatlight.to_function_with_gui(get_prompt)
prompt_with_gui.input("a").callbacks.edit_popup_possible = True

fiatlight.fiat_run(prompt_with_gui)
