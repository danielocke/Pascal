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


class App(QApplication):
    def __init__(self):
        super().__init__(sys.argv)

        self.scene = QGraphicsScene()
        
        self.circle = QGraphicsEllipseItem(0, 0, 100, 100)
        self.circle.setBrush(QBrush(QColor(255, 0, 0, 255)))        

        self.scene.addItem(self.circle)

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
        
        self.view.setStyleSheet("""
            background: transparent;
            border: none;
        """)

        self.view.setFrameShape(self.view.Shape.NoFrame)

        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.view.resize(400, 300)
        self.view.show()