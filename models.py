from PySide6.QtWidgets import (
    QApplication,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from util import *

class GraphicsObject:
    def __init__(self):
        self.sprite = load_sprite('')