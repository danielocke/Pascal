import sys, random
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsEllipseItem,
    QWidget
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QBrush, QColor, QPainter

from models import Snake, GraphicsObject

class App(QApplication):
    def __init__(self):
        super().__init__(sys.argv)

        self.scene  = QGraphicsScene()
        self.pascal = Snake(0, 0, scale=0.4)

        self.pascal.load(self.scene)


        self.view = QGraphicsView(self.scene)

        self._setup_view()

        self._flick()
        self.pascal.activate_animation('shake')
        self.pascal.activate_animation('blink')
        

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
        self.view.resize(500, 500)
        self.view.move(0,0)
        
        self.view.show()
    
    def _flick(self):
        if 'flick' in self.pascal.active_animations:
            self.pascal.deactivate_animation('flick')
            time = random.randint(1,10)
            QTimer.singleShot(time*1000, self._flick)
        else:
            self.pascal.activate_animation('flick')
            time = random.random()
            QTimer.singleShot(time*1000, self._flick)