from diffusers import DiffusionPipeline
import torch
import PIL.Image
import numpy as np
import cv2


pipe = DiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float16, use_safetensors=True, variant="fp16")
pipe.to("cuda")
pipe.enable_model_cpu_offload()

# if using torch < 2.0
# pipe.enable_xformers_memory_efficient_attention()

prompt = "An astronaut riding a green horse"

image: PIL.Image = pipe(prompt=prompt).images[0]
image_array = np.array(image)

cv2.imshow("SDXL", image_array)
while cv2.waitKey(1) != ord("q"):
    pass
