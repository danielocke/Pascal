from PySide6.QtWidgets import (
    QApplication,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer

from util import *

class GraphicsObject:
    def __init__(self, x, y, frames, z = 1, scale = 1.0, anim_cd = 1000):
        self.sprite = Sprite(frames, z, anim_cd)
        self.x = x
        self.y = y
        self.scale = scale
        self.sprite.setPos(x, y)
        self.sprite.setScale(scale)
    
    def load(self, scene):
        scene.addItem(self.sprite)

class Sprite(QGraphicsPixmapItem):
    def __init__(self, frames, z, cd):
        self.frames = load_frames(frames)
        self.current = 0
        super().__init__(self.frames[0])
        self.setZValue(z)
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(cd)
    
    def tick(self):
        self.current = (self.current + 1) % len(self.frames)
        self.setPixmap(self.frames[self.current])

class EyeSprite(Sprite):
    def __init__(self, z, cd, cd_blink):

        self.CLOSED = 2
        self.OPEN = 0

        frames = ['eyes_front','eyes_back','eyes_closed']
        super().__init__(frames, z, cd)
        
        self.cd = cd
        self.cd_blink = cd_blink

        self.blink_timer = QTimer()
        self.blink_timer.singleShot(self.cd, self._blink_start)

    def _blink_start(self):
        self.current = self.CLOSED
        self.setPixmap(self.frames[self.current])
        self.blink_timer.singleShot(self.cd_blink, self._blink_end)
    
    def _blink_end(self):
        self.current = self.OPEN
        self.setPixmap(self.frames[self.current])
        self.blink_timer.singleShot(self.cd, self._blink_start)

    def tick(self):
        return
    
class Eyes(GraphicsObject):
    def __init__(self, x, y, z=1, scale = 1.0, cd=1000, cd_blink = 100):
        super().__init__(x, y, ['eyes_back'], z, scale, cd)
        self.sprite = EyeSprite(z, cd, cd_blink)
        self.sprite.setScale(scale)

class Snake:
    def __init__(self, x, y, scale = 1.0):
        self.x = x
        self.y = y
        self.scale = scale

        self.eyes = Eyes(x, y, z = 3, cd = 9 * 1000, cd_blink = 200, scale = scale)
        self.head = GraphicsObject(x, y, ['head_closed','head_open'], z = 1, anim_cd = 10 * 1000, scale = scale)
        self.tail = GraphicsObject(x, y, ['tail_neutral','tail_up'],  z = 2, anim_cd =      300, scale = scale)
    
    def load(self,scene):
        self.tail.load(scene)
        self.head.load(scene)
        self.eyes.load(scene)