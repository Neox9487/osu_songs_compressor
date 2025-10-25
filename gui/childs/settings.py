import shelve
from PyQt5.QtWidgets import (
    QVBoxLayout, QCheckBox, QPushButton, QDialog
)
from PyQt5.QtCore import pyqtSignal, Qt
from configs import save_setting

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

        # 個人化設定
        with shelve.open("settings") as db:
            personalization = db.get("personalization", {"dark_mode": False, "show_mascot": True})
            DARK_MODE = personalization["dark_mode"]
            SHOW_MASCOT = personalization["show_mascot"]

        # 勾選框
        self.dark_mode_cb = QCheckBox("啟用深色模式")
        self.dark_mode_cb.setChecked(DARK_MODE)

        self.mascot_cb = QCheckBox("顯示吉祥物")
        self.mascot_cb.setChecked(SHOW_MASCOT)

        # 按鈕
        apply_btn = QPushButton("套用")
        apply_btn.clicked.connect(self.apply_changes)

        layout.addWidget(self.dark_mode_cb)
        layout.addWidget(self.mascot_cb)
        layout.addWidget(apply_btn)
        self.setLayout(layout)

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