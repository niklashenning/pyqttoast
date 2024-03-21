import sys
from PyQt5.QtWidgets import QApplication
from window import Window


# Run demo
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
