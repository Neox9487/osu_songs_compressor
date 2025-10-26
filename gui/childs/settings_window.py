import shelve
from PyQt5.QtWidgets import (
    QVBoxLayout, QCheckBox, QPushButton, QDialog
)
from PyQt5.QtCore import pyqtSignal, Qt
from utils.settings import save_setting, fetch_setting

class SettingsWindow(QDialog):
    settings_changed = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("設定")
        self.setFixedSize(130, 100)
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowContextHelpButtonHint
        )

        layout = QVBoxLayout()

        # 載入個人化設定
        dark_mode = fetch_setting("personalization", "dark_mode")
        show_mascot = fetch_setting("personalization", "show_mascot")

        # 勾選框
        self.dark_mode_cb = QCheckBox("啟用深色模式")
        self.dark_mode_cb.setChecked(dark_mode)

        self.mascot_cb = QCheckBox("顯示吉祥物")
        self.mascot_cb.setChecked(show_mascot)

        # 按鈕
        apply_btn = QPushButton("套用")
        apply_btn.clicked.connect(self.apply_changes)

        layout.addWidget(self.dark_mode_cb)
        layout.addWidget(self.mascot_cb)
        layout.addWidget(apply_btn)
        self.setLayout(layout)

        self.update_this_window_style(dark_mode)

    def apply_changes(self):
        """儲存設定 + 通知主視窗"""
        new_settings = {
            "dark_mode": self.dark_mode_cb.isChecked(),
            "show_mascot": self.mascot_cb.isChecked()
        }

        save_setting("personalization", "dark_mode", self.dark_mode_cb.isChecked())
        save_setting("personalization", "show_mascot", self.mascot_cb.isChecked())

        self.settings_changed.emit(new_settings)
        self.accept()

        self.update_this_window_style(self.dark_mode_cb.isChecked())

    def update_this_window_style(self, dark_mode: bool):
        pass