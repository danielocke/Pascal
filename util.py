import os
from PySide6.QtWidgets import (
    QGraphicsPixmapItem
)
from PySide6.QtGui import QPixmap

ASSET_PATH = os.path.abspath('./assets')

def load_sprite(filename):
    pixmap = QPixmap(ASSET_PATH.join(filename + ".png"))
    return QGraphicsPixmapItem(pixmap)
    