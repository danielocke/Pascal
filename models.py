from PySide6.QtWidgets import (
    QGraphicsScene,
    QGraphicsPixmapItem,
    QGraphicsTextItem
)
from PySide6.QtGui import QColor, QFont, QPixmap, QPainter
from PySide6.QtCore import QTimer

import numpy as np

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
    
    def move(self, x, y):
        self.x = x
        self.y = y
        for obj in self.body.values():
            obj.move(x,y)

class WriterSnake(Snake):
    def __init__(self, x, y, scale=1, write_speed = 2, move_speed = 5):
        self.x = x
        self.y = y
        self.scale = scale
        self.write_speed = write_speed
        self.move_speed  = move_speed

        # Destinations for movement animation
        self.dest_x = 0
        self.dest_y = 0
        self.moving = False
        self.tail_moving = False

        self.body = {
            'tail'       : GraphicsObject(x, y,  ['write_tail'],   z = 12, scale = scale),
            'head'       : GraphicsObject(x, y,  ['write_head','write_head_down'],   z = 13, scale = scale),
            'colour'     : GraphicsObject(x, y,  ['write_colour'], z = 11, scale = scale),
            'shadow'     : GraphicsObject(x, y,  ['write_shadow'], z = 11, scale = scale),
        }

        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
    
        self.current_phrase = None
        self.phrase_queue = []

        self.active_animations = set()
        self.define_animations()

    def define_animations(self):
        self.animations = {
            'bob'     : {'head'  : [ (WR_NEUTRAL, 500), (WR_DOWN, 250) ],
                         },
        }
    def goto(self, x, y):
        self.x = x
        self.y = y
        self.dest_x = x
        self.dest_y = y
        self.moving = False

    def move(self, x, y):
        self.dest_x = x
        self.dest_y = y
        self.moving = True

    def move_tail(self, x, y):
        # Based on location of pen tip on tail sprite
        self.dest_x = x - 100*self.scale
        self.dest_y = y - 575*self.scale
        self.tail_moving = True
    
    def recolour_pen(self, col):
        img = self.body['colour'].sprite.pixmap()
        col_img = QPixmap(img.size())
        col_img.fill(Qt.transparent)

        painter = QPainter(col_img)
        painter.drawPixmap(0,0, img)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(col_img.rect(), COLOURS[col])
        painter.end()

        self.body['colour'].sprite.setPixmap(col_img)

    def write(self, phrase):

        if self.current_phrase != None:
            self.phrase_queue.append(phrase)
            return

        self.current_phrase = phrase

        self.goto(0,0)

        self.show()

        #self.activate_animation('bob')

        self.move(self.current_phrase.start_x - 15*self.scale, self.current_phrase.start_y - 520*self.scale)
        
        self.timer.start(self.write_speed)


    def tick(self):
        
        # If writer is done writing a phrase. 
        if self.current_phrase.complete:
            if len(self.phrase_queue) > 0:
                self.current_phrase = self.phrase_queue.pop(0)
                self.move(self.current_phrase.start_x - 15*self.scale, self.current_phrase.start_y - 520*self.scale)
            else:
                self.current_phrase = None
                self.timer.stop()
                #self.deactivate_animation('bob')
                self.hide()
                return

        # If writer is moving to another letter/line, don't draw until reached.
        if self.moving:
            if abs(self.x - self.dest_x) < self.move_speed and abs(self.y - self.dest_y) < self.move_speed:
                self.moving = False
            else:
                direction = np.array([self.dest_x - self.x, self.dest_y - self.y])
                direction = direction / np.linalg.norm(direction)

                self.x += (direction[0] * self.move_speed) / 10
                self.y += (direction[1] * self.move_speed) / 10


                for obj in self.body.values():
                    obj.move(self.x, self.y)
            return

        if self.tail_moving:
            tail_x, tail_y = self.body['tail'].x, self.body['tail'].y

            if abs(tail_x - self.dest_x) < self.move_speed and abs(tail_y - self.dest_y) < self.move_speed:
                self.tail_moving = False
            else:
                direction = np.array([self.dest_x - tail_x, self.dest_y - tail_y])
                direction = direction / np.linalg.norm(direction)

                tail_x += direction[0] * self.move_speed
                tail_y += direction[1] * self.move_speed


                self.body['tail'].move(tail_x,tail_y)
                self.body['colour'].move(tail_x, tail_y)
            return

        move = self.current_phrase.tick()

        if move:
            current_letter = self.current_phrase.letters[self.current_phrase.current]
            self.move(current_letter.x - 15*self.scale, current_letter.y - 520*self.scale)
            return
        

        x_tail, y_tail = self.current_phrase.letters[self.current_phrase.current].get_point()

        self.move_tail(x_tail, y_tail)
        
class Bubble:
    def __init__(self,x,y,scale):
        self.x = x
        self.y = y
        self.scale = scale
        
        self.bubble = GraphicsObject(x,y,frames=['bubble'], z = 7, scale = scale)
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