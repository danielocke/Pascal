from app import App
import sys
import signal

if __name__ == '__main__':
    app = App()

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    sys.exit(app.exec())