import os
import random
from os import path
from contextlib import nullcontext
import time
from sys import platform
import torch
import cv2

"""
All credits to https://github.com/flowtyone/flowty-realtime-lcm-canvas!!
"""

cache_path = path.join(path.dirname(path.abspath(__file__)), "models")

os.environ["TRANSFORMERS_CACHE"] = cache_path
os.environ["HF_HUB_CACHE"] = cache_path
os.environ["HF_HOME"] = cache_path
is_mac = platform == "darwin"

model_list = ['Dreamshaper7','Dreamshaper8','AbsoluteReality', 'RevAnimated','Protogen']
model_ids = ["Lykon/dreamshaper-7", "Lykon/dreamshaper-8","Lykon/absolute-reality-1.81", "danbrown/RevAnimated-v1-2-2", "darkstorm2150/Protogen_x5.8_Official_Release"]

def create_video(image_folder, video_name, fps):
    images = [img for img in os.listdir(image_folder) if img.endswith(".jpg") or img.endswith(".png")]
    images.sort()  # Sort the images if needed

    # Determine the width and height from the first image
    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, layers = frame.shape

    # Initialize video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # For mp4 videos
    video = cv2.VideoWriter(video_name, fourcc, fps, (width, height))

    for image in images:
        video.write(cv2.imread(os.path.join(image_folder, image)))

    cv2.destroyAllWindows()
    video.release()

def should_use_fp16():
    if is_mac:
        return True

    gpu_props = torch.cuda.get_device_properties("cuda")

    if gpu_props.major < 6:
        return False

    nvidia_16_series = ["1660", "1650", "1630"]

    for x in nvidia_16_series:
        if x in gpu_props.name:
            return False

    return True

class timer:
    def __init__(self, method_name="timed process"):
        self.method = method_name

    def __enter__(self):
        self.start = time.time()
        print(f"{self.method} starts")

    def __exit__(self, exc_type, exc_val, exc_tb):
        end = time.time()
        print(f"{self.method} took {str(round(end - self.start, 2))}s")


def load_models(model_id="Lykon/dreamshaper-7"):
    from diffusers import AutoPipelineForImage2Image, LCMScheduler
    from diffusers.utils import load_image

    if not is_mac:
        torch.backends.cuda.matmul.allow_tf32 = True

    use_fp16 = should_use_fp16()

    lcm_lora_id = "latent-consistency/lcm-lora-sdv1-5"

    if use_fp16:
        pipe = AutoPipelineForImage2Image.from_pretrained(
            model_id,
            cache_dir=cache_path,
            torch_dtype=torch.float16,
            variant="fp16",
            safety_checker=None
        )
    else:
        pipe = AutoPipelineForImage2Image.from_pretrained(
            model_id,
            cache_dir=cache_path,
            safety_checker=None
        )

    pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)

    pipe.load_lora_weights(lcm_lora_id)
    pipe.fuse_lora()

    device = "mps" if is_mac else "cuda"

    pipe.to(device=device)

    generator = torch.Generator()

    def infer(
            prompt,
            image,
            num_inference_steps=4,
            guidance_scale=1,
            strength=0.9,
            seed=random.randrange(0, 2**63)
    ):
        with torch.inference_mode():
            with torch.autocast("cuda") if device == "cuda" else nullcontext():
                with timer("inference"):
                    return pipe(
                        prompt=prompt,
                        image=load_image(image),
                        generator=generator.manual_seed(seed),
                        num_inference_steps=num_inference_steps,
                        guidance_scale=guidance_scale,
                        strength=strength
                    ).images[0]

    return infer