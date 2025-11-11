import sys
from PyQt6.QtWidgets import QApplication
from tailgui import TailGUI

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep app running when window is closed
    window = TailGUI()
    window.show()
    sys.exit(app.exec())