import sys, random, threading
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsView,
    QGraphicsScene,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QGuiApplication

from models import *
from utils import Async_Bridge, COLOURS

from paths import *

class App(QApplication):
    def __init__(self):
        super().__init__(sys.argv)

        self.scene  = QGraphicsScene()
        self.view = QGraphicsView(self.scene)

        self._setup_view()

        self.bg     = GraphicsObject(0,0, ['bg'], z = 0, scale = 0.4)
        self.pascal = Snake(0, 0, scale=0.4)
        self.pascal_write = WriterSnake(0,0,scale=0.5)
        self.pascal_peek  = PeekSnake(0,0,scale=0.5)

        self.phrases = []

        self.letters = extract_paths()

        self.bg.load(self.scene)
        self.pascal.load(self.scene)
        self.pascal_write.load(self.scene)
        self.pascal_write.hide()
        self.pascal_peek.load(self.scene)
        self.pascal_peek.hide()

        self.peek_timer = QTimer()
        self.peek_timer.timeout.connect(self._peek)

        # Initialize async bridge:
        self.bridge = Async_Bridge()
        self.bridge.move_signal.connect(self.view.move)
        self.bridge.noisy_signal.connect(self._noisy)
        self.bridge.write_signal.connect(self._write)
        self.bridge.erase_signal.connect(self._erase)
        self.bridge.peek_signal.connect(self._peek)
        self.bridge.stop_peek_signal.connect(self._stop_peek)

        # Initialize async command loop:
        threading.Thread(target=self._cmd_loop, daemon=True).start()

        #self._flick()
        #self.pascal.activate_animation('shake')
        #self.pascal.activate_animation('blink')     

        self.bg.hide()
        self.pascal.hide()


    def _setup_view(self):
        
        # Window flags
        self.view.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint|
            Qt.WindowType.WindowTransparentForInput
        )

        # Remove view background
        self.view.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )
        self.view.viewport().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.view.setStyleSheet("""
            background: transparent;
            border: none;
        """)
        screens = QGuiApplication.screens()
        #if len(screens) > 1:
        #    self.view.setGeometry(screens[1].geometry())
        self.view.setGeometry(screens[0].geometry())
        screen_rect = screens[0].geometry()
        self.width  = screen_rect.width()
        self.height = screen_rect.height()

        
        self.view.setFrameShape(self.view.Shape.NoFrame)

        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.showFullScreen()
        self.view.setSceneRect(0, 0, screen_rect.width(), screen_rect.height())

        self.view.show()
    
    def _flick(self):
        if 'flick' in self.pascal.active_animations:
            self.pascal.deactivate_animation('flick')
            time = random.randint(1,10)
            QTimer.singleShot(time*1000, self._flick)
        else:
            if not 'noisy' in self.pascal.active_animations:
                self.pascal.activate_animation('flick')
            time = random.random()+0.3
            QTimer.singleShot(time*1000, self._flick)
    
    def _noisy(self):
        if 'noisy' in self.pascal.active_animations:
            self.pascal.deactivate_animation('noisy')
        else:
            self.pascal.activate_animation('noisy')

    def _write(self, text, x, y, col):
        self.pascal_write.recolour_pen(col)
        phrase = Phrase(text, self.letters, x, y, 10, COLOURS[col], screen_width = self.width)
        self.phrases.append(phrase)
        phrase.load(self.scene)
        
        self.pascal_write.write(phrase)

    def _erase(self):
        for phrase in self.phrases:
            phrase.delete(self.scene)

    def _peek(self):
        self.pascal_peek.peek_active = True
        self.pascal_peek.show()
        x_bounds = (min(self.width,200), max(0,self.width - 200))
        y_bounds = (min(self.height,200), max(0,self.height - 200))
        self.pascal_peek.peek(x_bounds,y_bounds,(0,self.height,0,self.width))

    def _stop_peek(self):
        self.pascal_peek.peek_active = False

    def _cmd_loop(self):
        while True:
            cmd = input('> ')

            if cmd == 'noisy':
                self.bridge.noisy_signal.emit()
            elif cmd == 'peek':
                self.bridge.peek_signal.emit()
            elif cmd == 'stop_peek':
                self.bridge.stop_peek_signal.emit()
            elif 'move' in cmd:
                crds = cmd.split(' ')
                try:
                    self.bridge.move_signal.emit(int(crds[1]), int(crds[2]))
                except:
                    print('move failed')
            elif 'write' in cmd:
                cmd = cmd.replace('\\n','\n')
                if "'" in cmd:
                    args = cmd.split("'")
                else:
                    args = cmd.split('"')

                if len(args) == 3:
                    crds = (500,100)
                    col  = 'red' 
                else:
                    crds = args[2].lstrip().rstrip().split(' ')
                    col = args[3]

                try:
                    self.bridge.write_signal.emit(args[1],int(crds[0]),int(crds[1]),col)
                except:
                    print('Write failed')
            elif cmd == 'erase':
                self.bridge.erase_signal.emit()