import sys, random, threading
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsEllipseItem,
    QWidget
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QBrush, QColor, QPainter

from models import Snake, GraphicsObject
from util import Async_Bridge

class App(QApplication):
    def __init__(self):
        super().__init__(sys.argv)

        self.scene  = QGraphicsScene()
        self.bg     = GraphicsObject(0,0, ['bg'], z = 0, scale = 0.4)
        self.pascal = Snake(0, 0, scale=0.4)

        self.bg.load(self.scene)
        self.pascal.load(self.scene)


        self.view = QGraphicsView(self.scene)

        self._setup_view()

        # Initialize async bridge:
        self.bridge = Async_Bridge()
        self.bridge.move_signal.connect(self.view.move)
        self.bridge.noisy_signal.connect(self._noisy)

        # Initialize async command loop:
        threading.Thread(target=self._cmd_loop, daemon=True).start()

        self._flick()
        self.pascal.activate_animation('shake')
        self.pascal.activate_animation('blink')
        self._noisy()        

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

        self.view.setFrameShape(self.view.Shape.NoFrame)

        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.resize(500, 500)
        self.view.move(0,0)
        
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

    def _cmd_loop(self):
        while True:
            cmd = input('> ')

            if cmd == 'quit':
                self.quit()
            elif cmd == 'noisy':
                self.bridge.noisy_signal.emit()
            elif 'move' in cmd:
                crds = cmd.split(' ')
                try:
                    self.bridge.move_signal.emit(int(crds[1]), int(crds[2]))
                except:
                    print('move failed')