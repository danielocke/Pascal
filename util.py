import os
from PySide6.QtWidgets import (
    QGraphicsPixmapItem
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

ASSET_PATH = os.path.abspath('./assets')

def load_pixmap(filename,filetype = 'png'):
    return QPixmap(os.path.join(ASSET_PATH,filename + '.' + filetype))
    

def load_frames(files, filetype = 'png'):
    return [load_pixmap(file, filetype) for file in files]
