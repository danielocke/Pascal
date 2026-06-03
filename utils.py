import os, random
from PySide6.QtWidgets import (
    QGraphicsPixmapItem
)
from PySide6.QtGui import QPixmap, QColor
from PySide6.QtCore import Qt, QObject, Signal
import pandas as pd

ASSET_PATH = os.path.abspath('./assets')

COLOURS = {
    'white'  : QColor(255, 255, 255),
    'black'  : QColor(  0,   0,   0),
    'red'    : QColor(255,   0,   0),
    'green'  : QColor(  0, 255,   0),
    'blue'   : QColor(  0,   0, 255),
    'yellow' : QColor(255, 255,   0),
    'orange' : QColor(255, 125,   0),
}

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
    return QPixmap(os.path.join(ASSET_PATH,'sprites',filename + '.' + filetype))
    

def load_frames(files:list[str|None], filetype:str = 'png'):
    return [load_pixmap(file, filetype) for file in files]

def generate_line(category):
    data = pd.read_csv(os.path.join(ASSET_PATH,'dialogue','lines.csv'))
    lines = data.loc[(data['category'] == category), 'line']
    return lines.loc[random.randint(0,len(lines) - 1)]    

class Async_Bridge(QObject):
    move_signal  = Signal(int, int)
    noisy_signal = Signal()
    write_signal = Signal(str, int, int, str)
