from diffusers import DiffusionPipeline, LCMScheduler
import torch
from os import path


cache_path = path.join(path.dirname(path.abspath(__file__)), "models")
model_id = "Lykon/dreamshaper-7"
lcm_lora_id = "latent-consistency/lcm-lora-sdv1-5"

pipe = DiffusionPipeline.from_pretrained(model_id, variant="fp16", cache_dir=cache_path)
pipe.load_lora_weights(lcm_lora_id)
pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
pipe.to(device="cuda", dtype=torch.float16)

def make_img(p):
    images = pipe(
        prompt=p,
        num_inference_steps=4,
        guidance_scale=1,
    ).images[0]

    return images