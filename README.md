# FocusPocusAI
Image generation from screen capture, webcam capture and/or simple brush strokes. The functions have been designed primarily for use in architecture, and for sketching in the early stages of a project. It uses Stable Diffusion and LCM-LoRA as AI backbone for the generative process. IP Adapter support is included!
Initially, the Gradio code from <a>https://github.com/flowtyone/flowty-realtime-lcm-canvas</a> was adapted to Pyside6, and upgraded with the screen capture functionality.

![example_focus](https://github.com/s-du/FocusPocusAI/assets/53427781/b23c1329-76ba-4e50-8741-f3b245dca41c)

Any app can be used as a design inspiration source!

Examples of screen captures that could be a great source of information for diffusion :
- Creating simple shapes in Blender
- Painting in Photoshop/Krita
- Stop a video on a specific frame
- Google Earth or Google Street View
- ...

<div style="text-align: center;">
    <img src="anims/paintlcm_lr2.gif" width="800" alt="Description" style="display: block; margin: 0 auto;">
    <p>
    <i style="display: block; margin-top: 5px;">example showing a screen capture from Blender (on the left)</i>
    </p>
</div>

<div style="text-align: center;">
    <img src="anims/paintlcm_lr8.gif" width="800" alt="Description" style="display: block; margin: 0 auto;">
    <p>
    <i style="display: block; margin-top: 5px;">example showing a screen capture from a video (on the left)</i>
    </p>
</div>


## Installation
- Install CUDA (if not done already)
- Clone the repo and install a venv.
- Install torch. Example for CUDA 11.8:
```
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```
 (see https://pytorch.org/get-started/locally/)
- Install other dependencies (see requirements):
    - opencv-python
    - accelerate
    - diffusers
    - transformers
    - Pyside6. Note: It works with Pyside 6.5.2. Newer versions can cause problem with the loading of ui elements.
- Launch main.py


## Usage
Screen capture a 512 x 512 window on top any app (the dimensions can be adapted depending on your GPU). By default, the capture timestep is 1 second. Then, paint with a brush or add simple shapes and see the proposed image adapting live.

CTRL + wheel to adapt cursor size. The SD model can be adapted in the lcm.py file or chosen in a drop-down menu.
Voilà!

https://github.com/s-du/FocusPocusAI/assets/53427781/0c641573-599f-4bdb-b210-20576d7482a6

# Included models
The user can choose the inference model from within the UI (beware of hard drive space!). Here are the available built-in models:
- https://huggingface.co/darkstorm2150/Protogen_x5.8_Official_Release
- https://huggingface.co/Lykon/dreamshaper-7
- https://huggingface.co/Lykon/dreamshaper-8
- https://huggingface.co/danbrown/RevAnimated-v1-2-2
- ...

## Credits
The 'lcm.py' is adapted from https://github.com/flowtyone


