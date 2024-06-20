"""A Meme Generator: create an image using stable diffusion, and add a meme text on it"""
import fiatlight as fl
from fiatlight.fiat_kits.fiat_ai import invoke_sdxl_turbo
from fiatlight.fiat_kits.fiat_image.add_meme_text import add_meme_text

fl.run([invoke_sdxl_turbo, add_meme_text], app_name="Meme Generator")
