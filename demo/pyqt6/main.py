import sys
from PyQt6.QtWidgets import QApplication
from window import Window


# Run demo
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    app.exec()
