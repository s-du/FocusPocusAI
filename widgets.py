# standard libraries
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtUiTools import QUiLoader


class UiLoader(QUiLoader):
    """
    Subclass :class:`~PySide.QtUiTools.QUiLoader` to create the user interface
    in a base instance.

    Unlike :class:`~PySide.QtUiTools.QUiLoader` itself this class does not
    create a new instance of the top-level widget, but creates the user
    interface in an existing instance of the top-level class.

    This mimics the behaviour of :func:`PyQt4.uic.loadUi`.
    """

    def __init__(self, baseinstance, customWidgets=None):
        """
        Create a loader for the given ``baseinstance``.

        The user interface is created in ``baseinstance``, which must be an
        instance of the top-level class in the user interface to load, or a
        subclass thereof.

        ``customWidgets`` is a dictionary mapping from class name to class object
        for widgets that you've promoted in the Qt Designer interface. Usually,
        this should be done by calling registerCustomWidget on the QUiLoader, but
        with PySide 1.1.2 on Ubuntu 12.04 x86_64 this causes a segfault.

        ``parent`` is the parent object of this loader.
        """

        QUiLoader.__init__(self, baseinstance)
        self.baseinstance = baseinstance
        self.customWidgets = customWidgets

    def createWidget(self, class_name, parent=None, name=''):
        """
        Function that is called for each widget defined in ui file,
        overridden here to populate baseinstance instead.
        """

        if parent is None and self.baseinstance:
            # supposed to create the top-level widget, return the base instance
            # instead
            return self.baseinstance

        else:
            if class_name in self.availableWidgets():
                # create a new widget for child widgets
                widget = QUiLoader.createWidget(self, class_name, parent, name)

            else:
                # if not in the list of availableWidgets, must be a custom widget
                # this will raise KeyError if the user has not supplied the
                # relevant class_name in the dictionary, or TypeError, if
                # customWidgets is None
                try:
                    widget = self.customWidgets[class_name](parent)

                except (TypeError, KeyError) as e:
                    raise Exception(
                        'No custom widget ' + class_name + ' found in customWidgets param of UiLoader __init__.')

            if self.baseinstance:
                # set an attribute for the new child widget on the base
                # instance, just like PyQt4.uic.loadUi does.
                setattr(self.baseinstance, name, widget)

                # this outputs the various widget names, e.g.
                # sampleGraphicsView, dockWidget, samplesTableView etc.
                # print(name)

            return widget


def loadUi(uifile, baseinstance=None, customWidgets=None,
           workingDirectory=None):
    """
    Dynamically load a user interface from the given ``uifile``.

    ``uifile`` is a string containing a file name of the UI file to load.

    If ``baseinstance`` is ``None``, the a new instance of the top-level widget
    will be created.  Otherwise, the user interface is created within the given
    ``baseinstance``.  In this case ``baseinstance`` must be an instance of the
    top-level widget class in the UI file to load, or a subclass thereof.  In
    other words, if you've created a ``QMainWindow`` interface in the designer,
    ``baseinstance`` must be a ``QMainWindow`` or a subclass thereof, too.  You
    cannot load a ``QMainWindow`` UI file with a plain
    :class:`~PySide.QtGui.QWidget` as ``baseinstance``.

    ``customWidgets`` is a dictionary mapping from class name to class object
    for widgets that you've promoted in the Qt Designer interface. Usually,
    this should be done by calling registerCustomWidget on the QUiLoader, but
    with PySide 1.1.2 on Ubuntu 12.04 x86_64 this causes a segfault.

    :method:`~PySide.QtCore.QMetaObject.connectSlotsByName()` is called on the
    created user interface, so you can implemented your slots according to its
    conventions in your widget class.

    Return ``baseinstance``, if ``baseinstance`` is not ``None``.  Otherwise
    return the newly created instance of the user interface.
    """

    loader = UiLoader(baseinstance, customWidgets)

    if workingDirectory is not None:
        loader.setWorkingDirectory(workingDirectory)

    widget = loader.load(uifile)
    QMetaObject.connectSlotsByName(widget)
    return widget


class TransparentBox(QWidget):
    def __init__(self, size):
        super().__init__()
        self.w, self.h = size
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.dragging = False
        self.setGeometry(100, 100, self.w + 12, self.h + 12)  # Initial position and size

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(QColor(0, 120, 215), 6)  # Increased pen width to 6px
        painter.setPen(pen)
        painter.drawRect(0, 0, self.width(), self.height())  # Draw box edges

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)

    def mouseReleaseEvent(self, event):
        self.dragging = False

    def enterEvent(self, event):
        self.setCursor(Qt.SizeAllCursor)

    def leaveEvent(self, event):
        self.unsetCursor()


class simpleCanvas(QGraphicsView):
    def __init__(self, img_size):
        super().__init__()

        self.w, self.h = img_size

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setSceneRect(0, 0, self.w, self.h)
        self.setMinimumSize(self.w, self.h)
        self.setMaximumSize(self.w, self.h)

        self._photo = QGraphicsPixmapItem()
        self.scene.addItem(self._photo)

        self.setBackgroundBrush(QBrush(QColor(180, 180, 180)))
        self.setContentsMargins(0, 0, 0, 0)
        self.setViewportMargins(0, 0, 0, 0)

        self.setRenderHint(QPainter.Antialiasing)

    def create_new_scene(self, w, h):
        self.w = w
        self.h = h
        self.scene.clear()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setSceneRect(0, 0, w, h)
        self.setMinimumSize(w, h)
        self.setMaximumSize(w, h)
        self.resetTransform()
        self.add_empty_photo()
        self.update()

    def add_empty_photo(self):
        self._photo = QGraphicsPixmapItem()
        self.scene.addItem(self._photo)

    def setPhoto(self, pixmap=None):
        if pixmap and not pixmap.isNull():
            # Get the size of the sceneRect
            targetSize = QSize(self.w, self.h)

            # Scale the pixmap to the new size
            scaledPixmap = pixmap.scaled(targetSize,
                                         Qt.IgnoreAspectRatio)  # Use Qt.IgnoreAspectRatio to change the aspect ratio

            self._photo.setPixmap(scaledPixmap)


class Canvas(QGraphicsView):
    endDrawing = Signal()

    def __init__(self, img_size):
        super().__init__()

        self.w, self.h = img_size

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setSceneRect(0, 0, self.w, self.h)
        self.setMinimumSize(self.w, self.h)
        self.setMaximumSize(self.w, self.h)

        self._photo = QGraphicsPixmapItem()
        self.scene.addItem(self._photo)

        self.current_tool = 'brush'
        self.current_color = QColor(Qt.black)
        self.brush_size = 10
        self.drawing = False
        self.last_point = None

        # custom paint cursor
        self.brush_cur = self.create_circle_cursor(10)

        self.temp_item = None

        self.setBackgroundBrush(QBrush(QColor(180, 180, 180)))
        self.setContentsMargins(0, 0, 0, 0)
        self.setViewportMargins(0, 0, 0, 0)

        self.setRenderHint(QPainter.Antialiasing)

    def create_new_scene(self, w, h):
        self.scene.clear()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setSceneRect(0, 0, w, h)
        self.setMinimumSize(w, h)
        self.setMaximumSize(w, h)
        self.resetTransform()
        self.add_empty_photo()
        self.update()

    def add_empty_photo(self):
        self._photo = QGraphicsPixmapItem()
        self.scene.addItem(self._photo)

    def setPhoto(self, pixmap=None):
        if pixmap and not pixmap.isNull():
            self._photo.setPixmap(pixmap)

    def change_to_brush_cursor(self):
        self.setCursor(self.brush_cur)

    def create_circle_cursor(self, diameter):
        # Create a QPixmap with a transparent background
        self.cursor_diameter = diameter

        scale_factor = self.transform().m11()
        # print(f'scale factor: {scale_factor}')
        scaledDiameter = diameter * scale_factor

        pixmap = QPixmap(scaledDiameter, scaledDiameter)
        pixmap.fill(Qt.transparent)

        # Create a QPainter to draw on the pixmap
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw a circle
        painter.setPen(QColor(0, 0, 0))  # Black color, you can change as needed
        painter.drawEllipse(0, 0, scaledDiameter - 1, scaledDiameter - 1)

        # End painting
        painter.end()

        # Create a cursor from the pixmap
        return QCursor(pixmap)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.start_point = self.mapToScene(event.pos())
            self.last_point = event.pos()

            if self.current_tool in ['ellipse', 'rectangle']:
                if self.current_tool == 'ellipse':
                    self.temp_item = QGraphicsEllipseItem(QRectF(self.start_point, self.start_point))
                elif self.current_tool == 'rectangle':
                    self.temp_item = QGraphicsRectItem(QRectF(self.start_point, self.start_point))

                if self.temp_item:
                    self.temp_item.setBrush(QBrush(self.current_color))
                    self.scene.addItem(self.temp_item)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self.drawing:
            end_point = self.mapToScene(event.pos())
            if self.current_tool in ['brush', 'eraser']:
                if self.current_tool == 'brush':
                    self.draw_line(event.pos())
                elif self.current_tool == 'eraser':
                    self.erase_line(event.pos())
            elif self.current_tool in ['ellipse', 'rectangle'] and self.temp_item:
                self.update_temp_shape(end_point)

    def mouseReleaseEvent(self, event):
        self.endDrawing.emit()
        if event.button() == Qt.LeftButton and self.drawing:
            self.drawing = False
            self.temp_item = None  # Reset temporary item

    def update_temp_shape(self, end_point):
        rect = QRectF(self.start_point, end_point).normalized()
        if self.current_tool == 'ellipse':
            self.temp_item.setRect(rect)
        elif self.current_tool == 'rectangle':
            self.temp_item.setRect(rect)

    def draw_line(self, end_point):
        path = QPainterPath(self.mapToScene(self.last_point))
        path.lineTo(self.mapToScene(end_point))
        pen = QPen(self.current_color, self.brush_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        self.scene.addPath(path, pen)
        self.last_point = end_point

    def erase_line(self, end_point):
        eraser_path = QPainterPath(self.mapToScene(self.last_point))
        eraser_path.lineTo(self.mapToScene(end_point))
        eraser = QPen(Qt.white, self.brush_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        self.scene.addPath(eraser_path, eraser)
        self.last_point = end_point

    def draw_ellipse(self, start_point, end_point):
        rect = QRectF(start_point, end_point)
        ellipse = QGraphicsEllipseItem(rect)
        ellipse.setBrush(QBrush(self.current_color))
        self.scene.addItem(ellipse)

    def draw_rectangle(self, start_point, end_point):
        rect = QRectF(start_point, end_point)
        rectangle = QGraphicsRectItem(rect)
        rectangle.setBrush(QBrush(self.current_color))
        self.scene.addItem(rectangle)

    def clear_drawing(self):
        for item in self.scene.items():
            if isinstance(item, QGraphicsPathItem) or \
                    isinstance(item, QGraphicsEllipseItem) or \
                    isinstance(item, QGraphicsRectItem):
                self.scene.removeItem(item)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        self.brush_size += delta / 120  # Adjust this factor if needed
        self.brush_size = max(1, min(self.brush_size, 50))  # Limit brush size

        self.brush_cur = self.create_circle_cursor(self.brush_size)
        self.change_to_brush_cursor()

    def set_tool(self, tool):
        self.current_tool = tool
        if tool == 'brush' or 'eraser':
            self.change_to_brush_cursor()
        else:
            self.setCursor(Qt.ArrowCursor)

    def set_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.current_color = color
