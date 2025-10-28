import os

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QListWidget, QMessageBox, QLabel, QProgressBar, QApplication
)
from PyQt5.QtCore import Qt, QSize

from utils.songs import compress_songs, load_songs
from utils.settings import save_setting, fetch_setting

from configs import (
    APP_NAME, WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT,
    DARK_MODE_STYLES, LIGHT_MODE_STYLES
)

from gui.childs import SettingsWindow

class OsuCompressor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME}")
        self.setGeometry(0, 0, WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT)

        main_layout = QVBoxLayout()

        # 輸入輸出路徑
        self.songs_path = fetch_setting("dir", "songs_dir")
        self.output_path = fetch_setting("dir", "target_dir")

        if not self.output_path:
            self.output_label = QLabel("尚未選擇輸出目的地")
        else :
            self.output_label = QLabel(f"已選擇輸出目的地： {self.output_path}")
        self.output_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.output_label)

        # 上面的按鈕列
        top_btns = QHBoxLayout()
        self.select_btn = QPushButton("選擇 Songs 資料夾")
        self.output_btn = QPushButton("選擇輸出目的地")
        self.refresh_btn = QPushButton("重新整理")
        self.setting_btn = QPushButton("UI 設定")
        top_btns.addWidget(self.select_btn)
        top_btns.addWidget(self.output_btn)
        top_btns.addWidget(self.refresh_btn)
        top_btns.addWidget(self.setting_btn)
        main_layout.addLayout(top_btns)

        # 進度條
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)

        # 下面 
        lists_layout = QHBoxLayout()
        # 左邊
        left_layout = QVBoxLayout()
        self.available_label = QLabel("可壓縮歌曲(共 0 首)")
        left_layout.addWidget(self.available_label)
        self.available_list = QListWidget()
        self.available_list.setIconSize(QSize(96, 54))
        self.available_list.setSelectionMode(QListWidget.MultiSelection)
        left_layout.addWidget(self.available_list)

        # 中間的按鈕
        middle_btns = QVBoxLayout()
        self.add_btn = QPushButton("→ 加入")
        self.remove_btn = QPushButton("← 移除")
        middle_btns.addStretch()
        middle_btns.addWidget(self.add_btn)
        middle_btns.addWidget(self.remove_btn)
        middle_btns.addStretch()

        # 右邊
        right_layout = QVBoxLayout()
        self.selected_label = QLabel("已選取歌曲0 首)")
        right_layout.addWidget(self.selected_label)
        self.selected_list = QListWidget()
        self.selected_list.setIconSize(QSize(96, 54))
        self.selected_list.setSelectionMode(QListWidget.MultiSelection)
        right_layout.addWidget(self.selected_list)

        lists_layout.addLayout(left_layout)
        lists_layout.addLayout(middle_btns)
        lists_layout.addLayout(right_layout)
        main_layout.addLayout(lists_layout)

        self.setLayout(main_layout)

        # 底部動作
        button_btns = QHBoxLayout()
        self.compress_btn = QPushButton("開始壓縮")
        self.compress_btn.setEnabled(False)
        button_btns.addWidget(self.compress_btn)
        main_layout.addLayout(button_btns)

        # 綁定事件
        self.select_btn.clicked.connect(self.select_songs_folder)
        self.output_btn.clicked.connect(self.select_output_folder)
        self.refresh_btn.clicked.connect(self.load_song_folders)
        self.setting_btn.clicked.connect(self.open_ui_settings_window)
        self.add_btn.clicked.connect(self.add_selected)
        self.remove_btn.clicked.connect(self.remove_selected)
        self.available_list.itemSelectionChanged.connect(self.update_labels)
        self.selected_list.itemSelectionChanged.connect(self.update_labels)
        self.compress_btn.clicked.connect(self.compress_selected)

        # OSU 圖片路徑(給沒有 bg 的歌曲用)
        self.default_icon_path = os.path.join(os.path.dirname(__file__), "../assets/osu.png")

    def initialize(self):
        if fetch_setting("personalization", "dark_mode"):
            style = DARK_MODE_STYLES
        else:
            style = LIGHT_MODE_STYLES

        self.update_windows_style(style, fetch_setting("personalization", "show_mascot"))
        self.load_song_folders()
        self.update_compress_button_state()

    def select_songs_folder(self):
        "選 Songs 資料夾"
        
        folder = QFileDialog.getExistingDirectory(self, "選擇 osu! Songs 資料夾")
        if not folder:
            return
        
        self.selected_list.clear()
        self.songs_path = folder

        self.load_song_folders()
        
        self.update_compress_button_state()
        save_setting("dir", "songs_dir", folder)

    def select_output_folder(self):
        "選壓縮目osz要押去哪"
        folder = QFileDialog.getExistingDirectory(self, "選擇檔案輸出目的地")
        if not folder:
            return
        
        self.output_path = folder
        self.output_label.setText(f"已選擇輸出目的地：{folder}")
        self.update_compress_button_state()
        save_setting("dir", "target_dir", folder)

    def open_ui_settings_window(self):
        dlg = SettingsWindow()
        dlg.settings_changed.connect(self.on_ui_settings_changed)
        dlg.exec_()

    def on_ui_settings_changed(self, settings: dict):
        """
        settings: dict
            {
                "dark_mode": bool,
                "show_mascot": bool
            }
        """
        # 選擇樣式
        if settings.get("dark_mode"):
            style = DARK_MODE_STYLES
        else:
            style = LIGHT_MODE_STYLES

        self.update_windows_style(style, settings.get("show_mascot"))

    def update_windows_style(self, style: dict, show_mascot: bool):
        "套用 style 到主視窗 UI"

        bg = style.get("background")
        fg = style.get("foreground")
        button_bg = style.get("button_bg")
        button_fg = style.get("button_fg")
        highlight = style.get("highlight")

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg};
                color: {fg};
            }}
            QPushButton {{
                background-color: {button_bg};
                color: {button_fg};
            }}
            QListWidget::item:selected {{
                background-color: {highlight};
            }}
        """)

        # processor bar
        p_bg = style.get("progress_bg")
        p_chunk = style.get("progress_chunk")
        p_height = style.get("progress_height", 20)
        p_radius = style.get("progress_radius", 8)

        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {p_bg};
                border-radius: {p_radius}px;
                text-align: center;
                height: {p_height}px;
            }}
            QProgressBar::chunk {{
                background-color: {p_chunk};
                border-radius: {p_radius}px;
            }}
        """)

        # 吉祥物圖片(未完成!)
        pass

    def update_compress_button_state(self):
        "更新壓縮按鈕(能不能開壓"
        self.compress_btn.setEnabled(bool(self.songs_path and self.output_path))

    def load_song_folders(self):
        "拿歌們"
        self.available_list.clear()
        if not self.songs_path:
            return
        
        folders = [d for d in sorted(os.listdir(self.songs_path)) if os.path.isdir(os.path.join(self.songs_path, d))]
        total = len(folders)
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(0)
        
        self.setEnabled(False)
        QApplication.setOverrideCursor(Qt.WaitCursor)

        loaded_count = load_songs(
            folders,
            self.songs_path,
            self.progress_bar,
            self.available_list,
            self.default_icon_path,
        )

        self.update_labels()
        self.setEnabled(True)
        QApplication.restoreOverrideCursor()

        self.progress_bar.setMaximum(1)
        self.progress_bar.setValue(0)

        if loaded_count == 0:
            self.songs_path = None
            QMessageBox.warning(self, "提示", "目前資料夾沒有符合 osu! 格式的歌曲資料夾!")
        
    def add_selected(self):
        "把左邊選的歌加到待壓縮區(右邊"
        for item in self.available_list.selectedItems():
            text = item.text()
            if not any(text == self.selected_list.item(i).text() for i in range(self.selected_list.count())):
                self.selected_list.addItem(item.clone())
        self.available_list.clearSelection()
        self.update_labels()

    def remove_selected(self):
        "把右邊選的歌丟刪掉(從待壓縮區刪 不是刪資料夾"
        for item in self.selected_list.selectedItems():
            self.selected_list.takeItem(self.selected_list.row(item))
        self.update_labels()

    def compress_selected(self):
        "壓縮待壓縮區的歌曲至輸出目的地資料夾"
        if not (self.songs_path and self.output_path):
            QMessageBox.warning(self, "錯誤", "請先選擇 Songs 與輸出目的地！")
            return

        total = self.selected_list.count()
        if total == 0:
            QMessageBox.warning(self, "錯誤", "右側清單沒有歌曲可壓縮！")
            return

        folder_names = [self.selected_list.item(i).text() for i in range(total)]
        self.setEnabled(False)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        
        try:
            success = compress_songs(folder_names, self.songs_path, self.output_path, self.progress_bar)
        except PermissionError:
            QMessageBox.warning(self, "Permission Denined", "請嘗試其他目標資料夾")
            self.setEnabled(True)
            self.progress_bar.setValue(0)
            QApplication.restoreOverrideCursor()
            return

        self.setEnabled(True)
        QApplication.restoreOverrideCursor()

        QMessageBox.information(self, "完成", f"壓縮 {success} 首歌曲至\n{self.output_path}")
        self.progress_bar.setValue(0)
        self.update_labels()

    def update_labels(self):
        "更新標籤(數量"
        total_left = self.available_list.count()
        total_right = self.selected_list.count()
        selected_left = len(self.available_list.selectedItems())
        selected_right = len(self.selected_list.selectedItems())

        self.available_label.setText(f"可壓縮歌曲(共 {total_left} 首，已選 {selected_left} 首)")
        self.selected_label.setText(f"已選取歌曲(共 {total_right} 首，已選 {selected_right} 首)")