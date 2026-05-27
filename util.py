import os
from PySide6.QtWidgets import (
    QGraphicsPixmapItem
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QObject, Signal

ASSET_PATH = os.path.abspath('./assets')

# Asset constants:

# Head
H_NEUTRAL = 0
H_SMILE   = 1
H_UPSET   = 2

# Tail
TL_NEUTRAL = 0
TL_DOWN    = 1

# Eyes
E_NEUTRAL  = 0
E_CLOSED   = 1

# Tongue   
TG_NEUTRAL = 1
TG_UP      = 2
TG_DOWN    = 3

# Headphones
HP_ON = 1


def load_pixmap(filename: (str|None), filetype:str = 'png'):
    if filename == None:
        return None
    return QPixmap(os.path.join(ASSET_PATH,filename + '.' + filetype))
    

def load_frames(files:list[str|None], filetype:str = 'png'):
    return [load_pixmap(file, filetype) for file in files]


class Async_Bridge(QObject):
    move_signal  = Signal(int, int)
    noisy_signal = Signal() 