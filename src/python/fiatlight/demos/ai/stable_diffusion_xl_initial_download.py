from fiatlight.demos.ai.stable_diffusion_xl_wrapper import stable_diffusion_xl
import cv2

"""This script will download the model weights to ~/.cache/huggingface/transformers on the first run.

It will run the Stable Diffusion XL model on the given text and save the output image as image.jpg
Apart from this, it is useless.
"""


image = stable_diffusion_xl("A cinematic shot of a baby racoon wearing an intricate italian priest robe.")
cv2.imwrite("image.jpg", image)
