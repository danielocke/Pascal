from PySide6.QtWidgets import (
    QGraphicsScene,
    QGraphicsPixmapItem,
    QGraphicsTextItem
)
from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import QTimer

from utils import *

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

        self.width = self.sprite.boundingRect().width()
        self.height = self.sprite.boundingRect().height()

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
    
    def hide(self):
        self.sprite.hide()

    def show(self):
        self.sprite.show()

    def move(self, x, y):
        self.sprite.setPos(x,y)
        self.x = x
        self.y = y

class TextObject(QGraphicsTextItem):
    def __init__(self, x, y, font, size, txt = '', z = 1, col = 'red'):
        super().__init__(txt)
        
        self.z = z
        self.font = QFont(font,size)
        if type(col) == str:
            self.col = QColor(col)
        else:
            self.col = col

        self.setZValue(z)
        self.setFont(self.font)
        self.setDefaultTextColor(self.col)

        self.width = self.boundingRect().width()
        self.height = self.boundingRect().height()
        self.x = x - self.width//2
        self.y = y - self.height//2
        self.setPos(self.x, self.y)
        

    def changeText(self,txt):
        self.setPlainText(txt)
    def load(self, scene: QGraphicsScene):
        scene.addItem(self)

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
            'headphones' : GraphicsObject(x, y, [None, 'headphones'],                                 z = 6, scale = scale),
            'eyes'       : GraphicsObject(x, y, ['eyes_neutral', 'eyes_closed'],                      z = 5, scale = scale),
            'tail'       : GraphicsObject(x, y, ['tail_neutral', 'tail_down'],                        z = 4, scale = scale),
            'head'       : GraphicsObject(x, y, ['head_neutral', 'head_smile', 'head_upset'],         z = 3, scale = scale),
            'tongue'     : GraphicsObject(x, y, [None, 'tongue_neutral', 'tongue_up', 'tongue_down'], z = 2, scale = scale),
            'mat'        : GraphicsObject(x, y, ['mat_purple'],                                       z = 1, scale = scale),
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
                         },
            'noisy'   : {'head'  : [ (H_UPSET, 0) ],
                         'eyes'  : [ (E_CLOSED, 0) ],
                         'headphones'  : [ (HP_ON, 0) ],
                         },
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
    
    def hide(self):
        for obj in self.body.values():
            obj.hide()
    def show(self):
        for obj in self.body.values():
            obj.show()

class WriterSnake(Snake):
    def __init__(self, x, y, scale=1):
        self.x = x
        self.y = y
        self.scale = scale
        self.body = {
            'tail'       : GraphicsObject(x, y,  ['write_tail'],   z = 14, scale = scale),
            'body'       : GraphicsObject(x, y,  ['write_body'],   z = 12, scale = scale),
            'head'       : GraphicsObject(x, y,  ['write_head'],   z = 13, scale = scale),
            'shadow'     : GraphicsObject(x, y,  ['write_shadow'], z = 11, scale = scale),
        }
        self.tot_segments = 10
        self.body_segments = [GraphicsObject(x-i*10, y-i*10,  ['write_body'],   z = 12, scale = scale) for i in range(self.tot_segments)]
        self.visible_segments = 0
        self.hide_segments()
    
    def move(self, x, y):
        for i in range(self.tot_segments):
            self.body_segments[i].move(x - i*10, y - i*10)

        self.x = x
        self.y = y
        for obj in self.body.values():
            obj.move(x,y)
    
    def move_write(self, x, y):
        num_segs = int(max(min(10 - (y - self.y) // 10, 10),0))
        print(num_segs)

        if self.visible_segments < num_segs:
            for i in range(self.visible_segments, num_segs):
                self.body_segments[i].show()

        elif self.visible_segments > num_segs:
            for i in range(num_segs, self.visible_segments):
                self.body_segments[i].hide()

        self.visible_segments = num_segs

        for obj in self.body.values():
            obj.move(x + 10 * (num_segs-1),self.y)

        for i in range(self.tot_segments):
            self.body_segments[i].move(x - i*10 + 10 * (num_segs-1), self.y - i*10)

        self.body['tail'].move(x , self.y - 10 * (num_segs-1))

        self.x = x
    
    def hide(self):
        for obj in self.body.values():
            obj.hide()
        for obj in self.body_segments:
            obj.hide()
    
    def load(self, scene):
        for obj in self.body.values():
            obj.load(scene)
        for obj in self.body_segments:
            obj.load(scene)
    
    def hide_segments(self):
        for seg in self.body_segments:
            seg.hide()

class Bubble:
    def __init__(self,x,y,scale):
        self.x = x
        self.y = y
        self.scale = scale
        
        self.bubble = GraphicsObject(x,y,frames=['bubble'], z = 7, scale = scale)
        print(x + self.bubble.width//2)
        print(y + self.bubble.width//2)
        self.text   = TextObject(x + self.bubble.width//2,y + self.bubble.height//2,font='Times New Roman',size=24,txt='Hello World',z = 8)
    
    def load(self, scene):
        self.bubble.load(scene)
        self.text.load(scene)
    def hide(self):
        self.bubble.hide()
        self.text.hide()
    def show(self):
        self.bubble.show()
        self.text.show()