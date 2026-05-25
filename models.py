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
    def __init__(self, x:int, y:int, frames:list, z:int = 1, scale:float = 1.0, default_frame:int = 0):
        self.sprite = Sprite(frames, z)
        self.x = x
        self.y = y
        self.scale = scale
        self.animation = None
        self.animation_frame = 0
        self.default_frame = default_frame

        # Setting sprite info:
        self.sprite.setScale(scale)
        self.sprite.set_frame(default_frame)
        self.sprite.setPos(x, y)
        self.expired_animation = False

    def load(self, scene: QGraphicsScene):
        scene.addItem(self.sprite)

    def set_animation(self, animation: (list|None)):
        
        if self.animation != None:
            self.expired_animation = True


        self.animation = animation
        self.animation_frame = 0

        if self.animation == None:
            self.sprite.set_frame(self.default_frame)
        else:            
            self.sprite.set_frame(self.animation[self.animation_frame][0])
            
            # No timer neccesary if only one pose
            if not len(self.animation) == 1:
                # Set animation to advance after cooldown.
                QTimer.singleShot(self.animation[self.animation_frame][1], self.tick)
    
    def tick(self):
        if self.expired_animation:
            self.expired_animation = False
            return
        
        self.animation_frame = (self.animation_frame + 1) % len(self.animation)
        self.sprite.set_frame(self.animation[self.animation_frame][0])
        QTimer.singleShot(self.animation[self.animation_frame][1], self.tick)

class Sprite(QGraphicsPixmapItem):
    def __init__(self, frames, z):
        super().__init__()

        self.frames = load_frames(frames)
        self.current_frame = 0

        self.setZValue(z)
        

    def set_frame(self, frame):
        self.current_frame = frame

        if self.frames[self.current_frame] == None:
            self.hide()
        else:
            self.show()    
            self.setPixmap(self.frames[self.current_frame])


class Snake:
    def __init__(self, x, y, scale = 1.0):
        self.x = x
        self.y = y
        self.scale = scale

        self.body = {
            'eyes'   : GraphicsObject(x, y, ['eyes_neutral', 'eyes_closed'],                      z = 5, scale = scale),
            'tail'   : GraphicsObject(x, y, ['tail_neutral', 'tail_down'],                        z = 4, scale = scale),
            'head'   : GraphicsObject(x, y, ['head_neutral', 'head_smile'],                       z = 3, scale = scale),
            'tongue' : GraphicsObject(x, y, [None, 'tongue_neutral', 'tongue_up', 'tongue_down'], z = 2, scale = scale),
            'mat'    : GraphicsObject(x, y, ['mat_purple'],                                       z = 1, scale = scale),
        }

        self.active_animations = set()
        self.define_animations()

    def define_animations(self):
        self.animations = {
            'flick'   : {'head'  : [ (H_NEUTRAL, 0) ],
                         'tongue': [ (TG_NEUTRAL, 50), (TG_UP, 50), (TG_NEUTRAL, 50), (TG_DOWN, 50) ],
                         },
            'blink'   : {'eyes'  : [ (E_NEUTRAL, 6000), (E_CLOSED, 200) ],
                         },
            'shake'   : {'tail'  : [ (TL_NEUTRAL, 300), (TL_DOWN, 300) ],
                         },
            'smile'   : {'head'  : [ (H_SMILE, 0) ],
                         }
        }

    def activate_animation(self, animation):
        
        for obj in self.animations[animation].keys():
            for active in self.active_animations:
                if obj in self.animations[active].keys():
                    self.deactivate_animation(active)
                    break
        
        self.active_animations.add(animation)
        new_animation = self.animations[animation]

        for obj in new_animation.keys():
            self.body[obj].set_animation(new_animation[obj])

        return True

    def deactivate_animation(self, animation):
        if not animation in self.active_animations:
            return False
        
        self.active_animations.remove(animation)
        for obj in self.animations[animation].keys():
            self.body[obj].set_animation(None)

        return True

    def load(self, scene):
        for obj in self.body.values():
            obj.load(scene)
    
