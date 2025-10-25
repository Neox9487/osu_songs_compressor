import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import OsuCompressor

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OsuCompressor()
    window.show()
    window.initialize()
    sys.exit(app.exec_())