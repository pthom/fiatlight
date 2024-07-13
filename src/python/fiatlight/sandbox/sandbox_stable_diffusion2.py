from diffusers import DiffusionPipeline, DPMSolverMultistepScheduler
import torch
import cv2
import numpy as np

repo_id = "stabilityai/stable-diffusion-2-base"
pipe = DiffusionPipeline.from_pretrained(repo_id, torch_dtype=torch.float16, variant="fp16")  # type: ignore

pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)  # type: ignore
pipe = pipe.to("cuda")

prompt = "High quality photo of an astronaut riding a horse in space"
image_pil = pipe(prompt, num_inference_steps=25).images[0]
image_array = np.array(image_pil)
cv2.imshow("SDXL", image_array)
while cv2.waitKey(1) != ord("q"):
    pass