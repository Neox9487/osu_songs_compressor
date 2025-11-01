from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QCheckBox, QLabel, QFileDialog, QHBoxLayout)
from PyQt5.QtCore import Qt
from utils.settings import save_setting, fetch_setting
from configs import DARK_MODE_STYLES, LIGHT_MODE_STYLES

class SettingsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        self.dark_mode_cb = QCheckBox("啟用深色模式")
        self.mascot_cb = QCheckBox("顯示吉祥物")

        self.dark_mode_cb.setChecked(fetch_setting("personalization", "dark_mode"))
        self.mascot_cb.setChecked(fetch_setting("personalization", "show_mascot"))

        self.songs_path_label = QLabel(f"目前的 Songs 資料夾：{fetch_setting('dir', 'songs_dir') or '尚未設定'}")
        songs_layout = QHBoxLayout()
        songs_layout.addWidget(self.songs_path_label)

        self.output_path_label = QLabel(f"目前的輸出資料夾：{fetch_setting('dir', 'target_dir') or '尚未設定'}")
        output_layout = QHBoxLayout()
        output_layout.addWidget(self.output_path_label)

        apply_btn = QPushButton("套用")
        apply_btn.clicked.connect(self.apply_settings)

        layout.addWidget(self.dark_mode_cb)
        layout.addWidget(self.mascot_cb)
        layout.addLayout(songs_layout)
        layout.addLayout(output_layout)
        layout.addWidget(apply_btn)

    def update_info(self):
        self.songs_path_label.setText(f"目前的 Songs 資料夾：{fetch_setting('dir', 'songs_dir') or '尚未設定'}")
        self.output_path_label.setText(f"目前的輸出資料夾：{fetch_setting('dir', 'target_dir') or '尚未設定'}")

    def apply_settings(self):
        dark_mode = self.dark_mode_cb.isChecked()
        show_mascot = self.mascot_cb.isChecked()

        save_setting("personalization", "dark_mode", dark_mode)
        save_setting("personalization", "show_mascot", show_mascot)

        style = DARK_MODE_STYLES if dark_mode else LIGHT_MODE_STYLES
        self.main_window.update_windows_style(style)