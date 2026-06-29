import os
from svgpathtools import svg2paths
from utils import ASSET_PATH

from PySide6.QtGui import QPainterPath, QPen
from PySide6.QtWidgets import (
    QGraphicsPathItem
)
from PySide6.QtCore import Qt, QTimer

A = [0,1]
B = [2]
C = [3]
D = [4]
E = [5,6,7,8]
F = [9,10]
G = [11,12,13]
H = [14,15,16]
I = [17,18,19]
J = [20]
K = [21,22]
L = [23]
M = [24]
N = [25]
O = [26]
P = [27,28]
Q = [29,30]
R = [31,32,33]
S = [34]
T = [35,36]
U = [37]
V = [38]
W = [39]
X = [40,41]
Y = [42,43]
Z = [44]

N0 = [0,1]
N1 = [2]
N2 = [3]
N3 = [4]
N4 = [5,6]
N5 = [7]
N6 = [8]
N7 = [9]
N8 = [10]
N9 = [11]


LETTERS = [A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z]
NUMS = [N0,N1,N2,N3,N4,N5,N6,N7,N8,N9]

BASE_WIDTH = 12
BASE_HEIGHT = 30

def extract_paths():

    raw_let_paths, _ = svg2paths(os.path.join(ASSET_PATH,'sprites','handwriting_final.svg'))
    raw_num_paths, _ = svg2paths(os.path.join(ASSET_PATH,'sprites','numbers.svg'))
    points = []

    for letter in LETTERS:
        letter_paths = []        
        for path in letter:
            num_segs = len(raw_let_paths[path])
            stroke = []
            for segment in raw_let_paths[path]:
                seg_points = 100//num_segs
                stroke += [(segment.points(t).real, segment.points(t).imag) for t in [i/seg_points for i in range(seg_points + 1)]]
            letter_paths.append(stroke)
        points.append(letter_paths)
    
    for num in NUMS:
        num_paths = []        
        for path in num:
            num_segs = len(raw_num_paths[path])
            stroke = []
            for segment in raw_num_paths[path]:
                seg_points = 100//num_segs
                stroke += [(segment.points(t).real, segment.points(t).imag) for t in [i/seg_points for i in range(seg_points + 1)]]
            num_paths.append(stroke)
        points.append(num_paths)


    return points

class PenStroke(QGraphicsPathItem):
    def __init__(self, points, x, y, z, colour, stroke_size, scale):
        super().__init__()
        self.points = list(map(lambda p: (p[0]*scale + x,p[1]*scale + y), points))
        self.current = 1
 
        pen = QPen()
        pen.setColor(colour)
        pen.setWidth(stroke_size)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)

        self.setPen(pen)

        self.complete = False

        self.setZValue(z)
    
    def tick(self):
        
        path = QPainterPath()
        x0, y0 = self.points[0]
        path.moveTo(x0, y0)
        for x, y in self.points[1:self.current]:
            path.lineTo(x,y)
        
        self.setPath(path)

        self.current += 1
    
        if self.current >= len(self.points):
            # Reset index for writer animation
            self.current = len(self.points) - 1
            self.complete = True
            return

    def load(self, scene):
        scene.addItem(self)
    def delete(self, scene):
        scene.removeItem(self)

    def get_point(self):
        return self.points[self.current]

class Letter:
    def __init__(self, paths, x, y, z, colour, stroke_size, scale):
        self.x = x
        self.y = y
        self.strokes = []
        for path in paths:
            self.strokes.append(PenStroke(path, x, y, z, colour, stroke_size, scale))
        
        self.current = 0
        self.complete = False
        
    
    def tick(self):
        if self.strokes[self.current].complete:
            self.current += 1
        
        if self.current >= len(self.strokes):
            # Reset current for writer animation
            self.current = len(self.strokes) - 1
            self.complete = True
            return
        
        self.strokes[self.current].tick()

    def load(self, scene):
        for stroke in self.strokes:
            stroke.load(scene)

    def delete(self, scene):
        for stroke in self.strokes:
            stroke.delete(scene)
        self.strokes = []

    def get_point(self):
        return self.strokes[self.current].get_point()

class Phrase:
    def __init__(self, phrase, all_chars, x, y, z, colour, screen_width, stroke_size = 10, scale = 5):
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        nums = '0123456789'
        self.phrase = phrase.upper()

        self.letters = []
        self.current = 0

        self.start_x = x
        self.start_y = y

        cur_x = x
        cur_y = y

        self.complete = False

        for char in self.phrase: 
            if char in alphabet:
                paths = all_chars[alphabet.index(char)]

                self.letters.append(Letter(paths, cur_x, cur_y, z, colour, stroke_size, scale))
            
                cur_x += BASE_WIDTH * scale
            elif char in nums:
                paths = all_chars[len(alphabet) + nums.index(char)]
                self.letters.append(Letter(paths, cur_x, cur_y, z, colour, stroke_size, scale))
                cur_x += BASE_WIDTH * scale

            elif char == ' ':
                cur_x += (BASE_WIDTH * scale)/2

            elif char == '\n':
                cur_y += (BASE_HEIGHT * scale)
                cur_x = x


    def tick(self):
        move_writer = False

        if self.letters[self.current].complete:
            self.current += 1
            if self.current < len(self.letters):
                move_writer = True

        if self.current >= len(self.letters):
            self.complete = True
            # reset current to avoid indexing issues.
            self.current -= 1
            return move_writer
        
        self.letters[self.current].tick()

        return move_writer

    def load(self, scene):
        for letter in self.letters:
            letter.load(scene)
    
    def delete(self, scene):
        for letter in self.letters:
            letter.delete(scene)