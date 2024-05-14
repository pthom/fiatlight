from typing import NewType


# A string used as a prompt (displayed as a textarea in the GUI)
# Mainly used for AI text and image generation models.
Prompt = NewType("Prompt", str)
