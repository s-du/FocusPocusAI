# CaptureCraft
Image generation from screen capture and/or simple brush strokes. It uses Stable Diffusion and LCM-Lora as AI backbone for the generative process.
The Gradio code from <a>https://github.com/flowtyone/flowty-realtime-lcm-canvas</a> was adapted to Pyside6, and upgraded with the screen capture functionality.

Examples of captures that could be a great source of information for diffusion :
- Creating simple shapes in Blender
- Painting in Photoshop/Krita
- Stop a video on a specific frame
- ...

<img src="paintlcm_lr3.gif" width="500" alt="Description">
<i>example showing a screen capture from CloudCompare (on the left)</i>

## Usage
Screen capture a 512 x 512 window on top any app (the dimensions can be adapted depending on your GPU). By default, the capture timestep is 1 second. Then, paint with a brush or add simple shapes and see the proposed image adapting live.
CTRL + wheel to adapt cursor size. The SD model can be adapted in the lcm.py file.
Voilà!

NB: Working with Pyside 6.5.2. Newer version can cause problem with the loading of ui elements.

## Credits
The 'lcm.py' is adapted from https://github.com/flowtyone


