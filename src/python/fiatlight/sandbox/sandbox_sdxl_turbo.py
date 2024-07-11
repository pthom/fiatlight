# https://huggingface.co/stabilityai/sdxl-turbo
# SDXL-Turbo is a distilled version of SDXL 1.0, trained for real-time synthesis

from diffusers import AutoPipelineForText2Image
import torch
import cv2
import numpy as np
import time

# device = "cpu"
device = "cuda"
# device = "mps"

# Will download to ~/.cache/huggingface/transformers
pipe = AutoPipelineForText2Image.from_pretrained("stabilityai/sdxl-turbo", torch_dtype=torch.float16, variant="fp16")  # type: ignore
pipe = pipe.to(device)
# pipe.enable_model_cpu_offload()

generator = torch.Generator(device=device)
generator.manual_seed(42)

# pipe = AutoPipelineForText2Image.from_pretrained("stabilityai/sdxl-turbo", variant="fp16")
# pipe = pipe.to("cpu")

prompt = "A cinematic shot of a baby racoon wearing an intricate italian priest robe."


start = time.time()
r = pipe.__call__(prompt=prompt, num_inference_steps=1, guidance_scale=0.0, generator=generator)
image = r.images[0]
print("Time taken: ", time.time() - start)

# image = pipe(prompt=prompt, num_inference_steps=1, guidance_scale=0.0).images[0]
# image_array= image.to("cpu").numpy()
image_array = np.array(image)

cv2.imshow("SDXL-Turbo", image_array)
while cv2.waitKey(1) != ord("q"):
    pass
cv2.destroyAllWindows()
