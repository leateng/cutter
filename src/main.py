import sys
from PySide6.QtWidgets import QApplication
from cutter.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.resize(1200, 900)
    win.show()
    app.exec()
