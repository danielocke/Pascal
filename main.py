from app import App
import sys
import signal
from PySide6.QtWidgets import QMainWindow


if __name__ == '__main__':
    app = App()
    window = QMainWindow()

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    sys.exit(app.exec())