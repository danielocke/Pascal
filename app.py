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

        self.phrases = []

        self.letters = extract_paths()

        self.bg.load(self.scene)
        self.pascal.load(self.scene)     

        # Initialize async bridge:
        self.bridge = Async_Bridge()
        self.bridge.move_signal.connect(self.view.move)
        self.bridge.noisy_signal.connect(self._noisy)
        self.bridge.write_signal.connect(self._write)
        self.bridge.erase_signal.connect(self._erase)

        # Initialize async command loop:
        threading.Thread(target=self._cmd_loop, daemon=True).start()

        self._flick()
        self.pascal.activate_animation('shake')
        self.pascal.activate_animation('blink')     

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
        if len(screens) > 1:
            self.view.setGeometry(screens[1].geometry())
        #self.view.setGeometry(screens[0].geometry())
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
        phrase = Phrase(text, self.letters, x, y, 10, COLOURS[col], screen_width = self.width)
        self.phrases.append(phrase)
        phrase.load(self.scene)
        phrase.start()

    def _erase(self):
        for phrase in self.phrases:
            phrase.delete(self.scene)

    def _cmd_loop(self):
        while True:
            cmd = input('> ')

            if cmd == 'noisy':
                self.bridge.noisy_signal.emit()
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
                
                crds = args[2].lstrip().rstrip().split(' ')
                try:
                    self.bridge.write_signal.emit(args[1],int(crds[0]),int(crds[1]),args[3])
                except:
                    print('Write failed')
            elif cmd == 'erase':
                self.bridge.erase_signal.emit()