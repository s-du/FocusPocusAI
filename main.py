from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtCore import *

import widgets as wid
import resources as res
from lcm import *
from PIL import Image

import os

# Params
IMG_W = 512
IMG_H = 512


def new_dir(dir_path):
    """
    Simple function to verify if a directory exists and if not creating it
    :param dir_path: (str) the path to check
    :return:
    """
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)


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


class InputDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enter Width and Height")
        self.setGeometry(100, 100, 300, 150)

        self.width_label = QLabel("Width (1-2048):")
        self.width_edit = QLineEdit()

        self.height_label = QLabel("Height (1-2048):")
        self.height_edit = QLineEdit()

        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")

        layout = QVBoxLayout()
        layout.addWidget(self.width_label)
        layout.addWidget(self.width_edit)
        layout.addWidget(self.height_label)
        layout.addWidget(self.height_edit)
        layout.addWidget(self.ok_button)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def accept(self):
        width = self.width_edit.text()
        height = self.height_edit.text()

        try:
            width = int(width)
            height = int(height)
            if 1 <= width <= 2048 and 1 <= height <= 2048:
                super().accept()
            else:
                self.show_error_message("Width and height must be between 1 and 2048.")
        except ValueError:
            self.show_error_message("Invalid input. Please enter integers.")

    def show_error_message(self, message):
        error_dialog = QDialog(self)
        error_dialog.setWindowTitle("Error")
        error_label = QLabel(message)
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(error_dialog.accept)
        layout = QVBoxLayout()
        layout.addWidget(error_label)
        layout.addWidget(ok_button)
        error_dialog.setLayout(layout)
        error_dialog.exec_()


class PaintLCM(QMainWindow):
    def __init__(self, is_dark_theme):
        super().__init__()

        basepath = os.path.dirname(__file__)
        basename = 'interface'
        uifile = os.path.join(basepath, '%s.ui' % basename)
        wid.loadUi(uifile, self)

        self.setWindowTitle("FocusPocus!")

        # add actions to action group
        ag = QActionGroup(self)
        ag.setExclusive(True)
        ag.addAction(self.brush_action)
        ag.addAction(self.eraser_action)
        ag.addAction(self.rectangle_action)
        ag.addAction(self.ellipse_action)

        self.img_dim = (IMG_W, IMG_H)
        self.canvas = wid.Canvas(self.img_dim)
        self.horizontalLayout_4.addWidget(self.canvas)

        self.result_canvas = wid.simpleCanvas(self.img_dim)
        self.horizontalLayout_4.addWidget(self.result_canvas)

        # loads models
        self.models = model_list
        self.models_ids = model_ids

        self.comboBox.addItems(self.models)

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
        self.export_action.triggered.connect(self.save_output)
        self.sequence_action.triggered.connect(self.record_sequence)
        self.capture_action.triggered.connect(self.toggle_capture)
        self.webcam_action.triggered.connect(self.toggle_webcam_capture)
        self.size_action.triggered.connect(self.update_img_dim)
        self.pushButton.clicked.connect(self.update_image)

        self.checkBox_hide.stateChanged.connect(self.toggle_canvas)

        # when editing canvas --> update inference
        self.canvas.endDrawing.connect(self.update_image)

        # combobox
        self.comboBox.currentIndexChanged.connect(self.change_inference_model)

        # Connect the sliders to the update_image function
        self.step_slider.valueChanged.connect(self.update_image)
        self.cfg_slider.valueChanged.connect(self.update_image)
        self.strength_slider.valueChanged.connect(self.update_image)

        # Connect the text edit to the update_image function
        self.textEdit.setWordWrapMode(QTextOption.WordWrap)
        self.textEdit.setText('An architectural drawing, building concept, realistic render, ultra detailed, cinematic, Frank Lloyd Whright, Bauhaus')

        # drawing ends

        # add capture box
        self.box = wid.TransparentBox(self.img_dim)
        self.capture_interval = 1000  # milliseconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.captureScreen)

        # configure webcam capture
        self.camera_index = 1  # Assuming you are using the first camera
        self.capture_interval = 1000  # Set capture interval in milliseconds
        self.timer_webcam = QTimer()
        self.timer_webcam.timeout.connect(self.capture_webcam_image)
        self.opencv_capture = cv2.VideoCapture(self.camera_index)

        # prepare sequence recording
        self.is_recording = False
        self.record_folder = ''
        self.n_frame = 0

        if is_dark_theme:
            suf = '_white_tint'
            suf2 = '_white'
        else:
            suf = ''

        self.add_icon(res.find(f'img/brush{suf}.png'), self.brush_action)
        self.add_icon(res.find(f'img/eraser{suf}.png'), self.eraser_action)
        self.add_icon(res.find(f'img/circle{suf}.png'), self.ellipse_action)
        self.add_icon(res.find(f'img/rectangle{suf}.png'), self.rectangle_action)
        self.add_icon(res.find(f'img/palette{suf}.png'), self.color_action)
        self.add_icon(res.find(f'img/crop{suf}.png'), self.capture_action)
        self.add_icon(res.find(f'img/save_as{suf}.png'), self.export_action)
        self.add_icon(res.find(f'img/movie{suf}.png'), self.sequence_action)
        self.add_icon(res.find(f'img/camera{suf}.png'), self.webcam_action)

        # run first inference
        self.update_image()

    # general functions __________________________________________
    def add_icon(self, img_source, pushButton_object):
        """
        Function to add an icon to a pushButton
        """
        pushButton_object.setIcon(QIcon(img_source))

    def save_output(self):
        # add code for file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            None, "Save Image", "", "PNG Image (*.png);;JPEG Image (*.jpg *.jpeg *.JPEG)"
        )

        # Save the image if a file path was provided, using high-quality settings for JPEG
        if file_path:
            if file_path.lower().endswith('.jpg') or file_path.lower().endswith('.jpeg'):
                self.out.save(file_path, 'JPEG', 100)
            else:
                self.out.save(file_path)  # PNG is lossless by default

        print(f'result saved: {file_path}')

    def toggle_canvas(self):
        # Hide or show canvas based on checkbox state
        if self.checkBox_hide.isChecked():
            self.canvas.hide()
        else:
            self.canvas.show()

        # Adjust the size of the window
        self.adjustSize()

    # Sequence record functionality __________________________________________
    def record_sequence(self):
        if self.sequence_action.isChecked():
            # change flag
            self.is_recording = True

            # let the user choose an output folder
            out_dir = str(QFileDialog.getExistingDirectory(self, "Select output_folder"))
            while not os.path.isdir(out_dir):
                QMessageBox.warning(self, "Warning",
                                    "Oops! Not a folder!")
                out_dir = str(QFileDialog.getExistingDirectory(self, "Select output_folder"))

            self.record_folder = out_dir
            self.inf_folder = os.path.join(self.record_folder, 'inference')
            self.input_folder = os.path.join(self.record_folder, 'inputs')
            # create the new subfolders to save frames
            new_dir(self.inf_folder)
            new_dir(self.input_folder)

        else:
            # change flag
            self.is_recording = False
            self.compile_video()
            self.n_frame = 0

    def compile_video(self):
        path_inference = os.path.join(self.inf_folder, 'inference_video.mp4')
        path_input = os.path.join(self.input_folder, 'input_video.mp4')
        create_video(self.inf_folder, path_inference, 10)
        create_video(self.input_folder, path_input, 10)

    # Inference parameters __________________________________________
    def change_inference_model(self):
        idx = self.comboBox.currentIndex()
        model_id = self.models_ids[idx]
        self.infer = load_models(model_id=model_id)
        self.update_image()

    def update_img_dim(self):
        # open dialog for image size
        dialog = InputDialog()
        if dialog.exec_() == QDialog.Accepted:
            w = int(dialog.width_edit.text())
            h = int(dialog.height_edit.text())
            print(f"Width: {w}, Height: {h}")

        # compile parameters
        self.img_dim = (w, h)

        self.result_canvas.create_new_scene(w, h)
        self.canvas.create_new_scene(w, h)

        self.box = wid.TransparentBox(self.img_dim)

    # Webcam capture __________________________________________

    def toggle_webcam_capture(self):
        if self.webcam_action.isChecked():
            # disable tools
            self.brush_action.setEnabled(False)
            self.eraser_action.setEnabled(False)
            self.ellipse_action.setEnabled(False)
            self.rectangle_action.setEnabled(False)
            self.color_action.setEnabled(False)
            self.capture_action.setEnabled(False)

            # remove existing items
            self.canvas.clear_drawing()

            # launch capture
            self.timer_webcam.start(self.capture_interval)

        else:
            self.brush_action.setEnabled(True)
            self.eraser_action.setEnabled(True)
            self.ellipse_action.setEnabled(True)
            self.rectangle_action.setEnabled(True)
            self.color_action.setEnabled(True)
            self.capture_action.setEnabled(True)

            self.timer_webcam.stop()
            # stop capture

    def capture_webcam_image(self):
        ret, frame = self.opencv_capture.read()
        # check if 'inverse' checkbox
        if self.checkBox_inverse.isChecked():
            frame = cv2.flip(frame, 0)
            frame = cv2.flip(frame, 1)
        if ret:
            # Convert the captured frame to QImage then to QPixmap
            height, width, channels = frame.shape
            bytes_per_line = channels * width
            qimage = QImage(frame.data, width, height, bytes_per_line, QImage.Format_BGR888)
            pixmap = QPixmap.fromImage(qimage)
            self.canvas.clear_drawing()
            self.canvas.setPhoto(pixmap)

            if self.checkBox.isChecked():
                self.update_image()
        else:
            print("Failed to capture image")

    # Other methods...

    def closeEvent(self, event):
        # Make sure to release the camera when closing the application
        self.opencv_capture.release()
        super().closeEvent(event)

    # Screen capture __________________________________________
    def toggle_capture(self):
        if self.capture_action.isChecked():
            # disable tools
            self.brush_action.setEnabled(False)
            self.eraser_action.setEnabled(False)
            self.ellipse_action.setEnabled(False)
            self.rectangle_action.setEnabled(False)
            self.color_action.setEnabled(False)
            self.webcam_action.setEnabled(False)

            # remove existing items
            self.canvas.clear_drawing()

            # launch capture
            self.box.show()
            self.timer.start(self.capture_interval)

        else:
            self.brush_action.setEnabled(True)
            self.eraser_action.setEnabled(True)
            self.ellipse_action.setEnabled(True)
            self.rectangle_action.setEnabled(True)
            self.color_action.setEnabled(True)
            self.webcam_action.setEnabled(True)

            self.timer.stop()
            # stop capture
            self.box.hide()

    def captureScreen(self):
        # Get geometry of the transparent box
        x, y, width, height = self.box.geometry().getRect()
        print(width, height)

        screen = QApplication.primaryScreen()
        if screen is not None:
            pixmap = screen.grabWindow(0, x + 6, y + 6, width - 12, height - 12)

            self.canvas.setPhoto(pixmap)

        # should it update continuously
        if self.checkBox.isChecked():
            self.update_image()

    def closeEvent(self, event):
        # Explicitly close the transparent box when the main window is closed
        self.box.close()
        event.accept()

    def update_image(self):
        # gather slider parameters:
        steps = self.step_slider.value()
        cfg = self.cfg_slider.value() / 10
        image_strength = self.strength_slider.value() / 100

        # get prompt
        p = self.textEdit.toPlainText()

        print(
            f'here are the parameters \n steps: {steps}\n cfg: {cfg}\n image strength: {image_strength}\n prompt: {p}')

        print('capturing drawing')
        self.im = scene_to_image(self.canvas)
        print(self.im)

        # capture painted image

        print('running inference')
        self.out = self.infer(
            prompt=p,
            image=self.im,
            num_inference_steps=steps,
            guidance_scale=cfg,
            strength=image_strength,
            seed=1337
        )

        self.out.save('result.jpg')
        print('result saved')

        self.result_canvas.setPhoto(pixmap=QPixmap('result.jpg'))

        # save images if recording flag
        if self.is_recording:
            self.n_frame += 1
            frame_path = f"frame_{self.n_frame:04}.png"
            self.out.save(os.path.join(self.inf_folder, frame_path))
            self.im.save(os.path.join(self.input_folder, frame_path))


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
        app.setStyle('Breeze')

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
            QWidget { background-color: #17161c; }
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
