import sys
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsEllipseItem,
    QWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QPainter

from models import Snake, GraphicsObject

class App(QApplication):
    def __init__(self):
        super().__init__(sys.argv)

        self.scene  = QGraphicsScene()
        self.bg     = GraphicsObject(0,0,['background'],z = 0,scale=0.5)
        self.pascal = Snake(0, 0,scale=0.5)

        self.bg.load(self.scene)
        self.pascal.load(self.scene)


        self.view = QGraphicsView(self.scene)

        self._setup_view()
        

    def _setup_view(self):
        
        # Window flags
        self.view.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint|
            Qt.WindowType.WindowTransparentForInput
        )

        # Remove view background
        self.view.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )
        self.view.viewport().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.view.setStyleSheet("""
            background: transparent;
            border: none;
        """)

        self.view.setFrameShape(self.view.Shape.NoFrame)

        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.move(0,0)
        self.view.resize(256, 512)
        self.view.show()