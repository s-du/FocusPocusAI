from PySide6.QtGui import *
from PySide6.QtWidgets import *

import widgets as wid
import resources as res
from lcm import *
from PIL import Image

import os

# Params
IMG_SIZE = 300


def scene_to_image(viewer):
    # Define the size of the image (same as the scene's bounding rect)
    image = QImage(viewer.viewport().size(), QImage.Format_ARGB32_Premultiplied)

    # Create a QPainter to render the scene into the QImage
    painter = QPainter(image)
    viewer.render(painter)
    painter.end()

    file_path = 'input.png'
    image.save(file_path)

    # Convert the BytesIO object to a PIL Image
    pil_img = Image.open(file_path)
    return pil_img


class PaintLCM(QMainWindow):
    def __init__(self, is_dark_theme):
        super().__init__()

        basepath = os.path.dirname(__file__)
        basename = 'interface'
        uifile = os.path.join(basepath, '%s.ui' % basename)
        wid.loadUi(uifile, self)

        self.setWindowTitle("Paint!")

        # add actions to action group
        ag = QActionGroup(self)
        ag.setExclusive(True)
        ag.addAction(self.brush_action)
        ag.addAction(self.eraser_action)
        ag.addAction(self.rectangle_action)
        ag.addAction(self.ellipse_action)

        self.canvas = wid.Canvas(IMG_SIZE)
        self.horizontalLayout_4.addWidget(self.canvas)

        self.result_canvas = wid.simpleCanvas(IMG_SIZE)
        self.horizontalLayout_4.addWidget(self.result_canvas)

        # initial parameters
        self.infer = load_models()
        self.im = None

        # specific variables
        if not path.exists(cache_path):
            os.makedirs(cache_path, exist_ok=True)

        # connections
        self.brush_action.triggered.connect(lambda: self.canvas.set_tool('brush'))
        self.eraser_action.triggered.connect(lambda: self.canvas.set_tool('eraser'))
        self.ellipse_action.triggered.connect(lambda: self.canvas.set_tool('ellipse'))
        self.rectangle_action.triggered.connect(lambda: self.canvas.set_tool('rectangle'))
        self.color_action.triggered.connect(self.canvas.set_color)

        # when editing canvas --> update inference
        self.canvas.endDrawing.connect(self.update_image)

        # Connect the sliders to the update_image function
        self.step_slider.valueChanged.connect(self.update_image)
        self.cfg_slider.valueChanged.connect(self.update_image)
        self.strength_slider.valueChanged.connect(self.update_image)

        # Connect the text edit to the update_image function
        self.textEdit.editingFinished.connect(self.update_image)

        # drawing ends

        if is_dark_theme:
            suf = '_white_tint'
            suf2 = '_white'
        else:
            suf = ''

        self.add_icon(res.find(f'img/brush{suf}.png'), self.brush_action)
        self.add_icon(res.find(f'img/eraser{suf}.png'), self.eraser_action)
        self.add_icon(res.find(f'img/circle{suf}.png'), self.ellipse_action)
        self.add_icon(res.find(f'img/rectangle{suf}.png'), self.rectangle_action)
        self.add_icon(res.find(f'img/legend{suf}.png'), self.color_action)

    # general functions __________________________________________
    def add_icon(self, img_source, pushButton_object):
        """
        Function to add an icon to a pushButton
        """
        pushButton_object.setIcon(QIcon(img_source))

    def update_image(self):
        # gather slider parameters:
        steps = self.step_slider.value()
        cfg = self.cfg_slider.value() / 10
        image_strength = self.strength_slider.value() / 100

        # get prompt
        p = self.textEdit.text()

        print(
            f'here are the parameters \n steps: {steps}\n cfg: {cfg}\n image strength: {image_strength}\n prompt: {p}')

        print('capturing drawing')
        self.im = scene_to_image(self.canvas)
        print(self.im)

        # capture painted image

        print('running inference')
        out = self.infer(
            prompt=p,
            image=self.im,
            num_inference_steps=steps,
            guidance_scale=cfg,
            strength=image_strength,
            seed=1337
        )
        print(out)

        out.save('result.jpg')
        print('result saved')

        self.result_canvas.setPhoto(pixmap=QPixmap('result.jpg'))


def main(argv=None):
    """
    Creates the main window for the application and begins the \
    QApplication if necessary.

    :param      argv | [, ...] || None

    :return      error code
    """

    # Define installation path
    install_folder = os.path.dirname(__file__)

    app = None

    # create the application if necessary
    if (not QApplication.instance()):
        app = QApplication(argv)
        app.setStyle('Fusion')

        # test if dark theme is used
        palette = app.palette()
        bg_color = palette.color(QPalette.Window)

        is_dark_theme = bg_color.lightness() < 128
        print(f'Windows dark theme: {is_dark_theme}')

        if is_dark_theme:
            app.setStyleSheet("""
            QPushButton:checked {
                background-color: lightblue;
            }
            QPushButton:disabled {
                background-color: #666;
            }
            QWidget { background-color: #444; }
            QProgressBar {
                text-align: center;
                color: rgb(240, 240, 240);
                border-width: 1px; 
                border-radius: 10px;
                border-color: rgb(230, 230, 230);
                border-style: solid;
                background-color:rgb(207,207,207);
            }

            QProgressBar:chunk {
                background-color:rgb(50, 156, 179);
                border-radius: 10px;
            }
            """)

    # create the main window
    print('Launching the application')
    window = PaintLCM(is_dark_theme)
    window.show()

    # run the application if necessary
    if (app):
        return app.exec_()

    # no errors since we're not running our own event loop
    return 0


if __name__ == '__main__':
    import sys

    sys.exit(main(sys.argv))
