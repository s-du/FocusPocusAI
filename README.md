# Screen to Art !
Image generation from screen capture and/or simple brush strokes. It uses Stable Diffusion and LCM-Lora as AI backbone for the generative process.
The Gradio code from <a>https://github.com/flowtyone/flowty-realtime-lcm-canvas</a> was adapted to Pyside6, and upgraded with screen capture functionality.

<img src="paintlcm_lr3.gif" width="500" alt="Description">
<i>example showing a screen capture from CloudCompare (on the left)</i>

## Usage
Screen capture a 512 x 512 window on any app (can be adapted depending on your GPU). Then, paint with brush or add simple shapes and see the proposed image adapting live.
CTRL + wheel to adapt cursor size. The SD model can be adapted in the lcm.py file.
Voilà!

NB: Working with Pyside 6.5.2. Newer version can cause problem with the loading of ui elements.

## Credits
The 'lcm.py' is adapted from https://github.com/flowtyone


