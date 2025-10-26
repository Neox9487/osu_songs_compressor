import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import OsuCompressor
from utils.settings import initailize_settings_file
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OsuCompressor()
    initailize_settings_file()
    window.initialize()
    window.show()
    sys.exit(app.exec_())
