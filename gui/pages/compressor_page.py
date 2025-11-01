import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QProgressBar, QMessageBox, QFileDialog, QApplication, QAbstractItemView
)
from PyQt5.QtCore import Qt, QSize
from utils.songs import compress_songs, load_songs
from utils.settings import save_setting, fetch_setting

from configs import DARK_MODE_STYLES, LIGHT_MODE_STYLES

class CompressorPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)

        # 初始化參數
        self.songs_path = fetch_setting("dir", "songs_dir")
        self.output_path = fetch_setting("dir", "target_dir")

        # 進度條
        self.progress_bar = QProgressBar()
        main_layout.addWidget(self.progress_bar)

        # 左右清單
        lists_layout = QHBoxLayout()
        self.available_label = QLabel("可壓縮歌曲(共 0 首)")
        self.available_list = QListWidget()
        self.available_list.setIconSize(QSize(96, 54))
        self.available_list.setSelectionMode(QAbstractItemView.MultiSelection)

        self.selected_label = QLabel("已選取歌曲(共 0 首)")
        self.selected_list = QListWidget()
        self.selected_list.setIconSize(QSize(96, 54))
        self.selected_list.setSelectionMode(QAbstractItemView.MultiSelection)

        left = QVBoxLayout()
        right = QVBoxLayout()
        left.addWidget(self.available_label)
        left.addWidget(self.available_list)
        right.addWidget(self.selected_label)
        right.addWidget(self.selected_list)

        middle = QVBoxLayout()
        self.add_btn = QPushButton("→ 加入")
        self.remove_btn = QPushButton("← 移除")
        middle.addStretch()
        middle.addWidget(self.add_btn)
        middle.addWidget(self.remove_btn)
        middle.addStretch()

        lists_layout.addLayout(left)
        lists_layout.addLayout(middle)
        lists_layout.addLayout(right)
        main_layout.addLayout(lists_layout)

        # Folder 動作
        folder_btns = QHBoxLayout()
        self.select_btn = QPushButton("選擇 Songs 資料夾")
        self.output_btn = QPushButton("選擇輸出目的地")
        for b in (self.select_btn, self.output_btn):
            folder_btns.addWidget(b)
        main_layout.addLayout(folder_btns)

        # 底部
        self.compress_btn = QPushButton("開始壓縮")
        self.compress_btn.setEnabled(False)
        main_layout.addWidget(self.compress_btn)

        # 綁定事件
        self.select_btn.clicked.connect(self.select_songs_folder)
        self.output_btn.clicked.connect(self.select_output_folder)
        self.add_btn.clicked.connect(self.add_selected)
        self.remove_btn.clicked.connect(self.remove_selected)
        self.compress_btn.clicked.connect(self.compress_selected)
        self.available_list.itemSelectionChanged.connect(self.update_labels)
        self.selected_list.itemSelectionChanged.connect(self.update_labels)

        self.default_icon_path = os.path.join(os.path.dirname(__file__), "../assets/osu.png")

    # === initialize ===
    def initialize(self):
        self.load_song_folders()
        self.update_compress_button_state()

    # === folder selection ===
    def select_songs_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "選擇 osu! Songs 資料夾")
        if not folder:
            return
        self.selected_list.clear()
        self.songs_path = folder
        self.load_song_folders()
        self.update_compress_button_state()
        save_setting("dir", "songs_dir", self.songs_path)

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "選擇輸出目的地")
        if not folder:
            return
        self.output_path = folder
        self.update_compress_button_state()
        save_setting("dir", "target_dir", folder)
    
    # === load songs ===
    def load_song_folders(self):
        self.available_list.clear()
        if not self.songs_path:
            return
        folders = [d for d in sorted(os.listdir(self.songs_path))
                   if os.path.isdir(os.path.join(self.songs_path, d))]
        total = len(folders)
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(0)

        self.setEnabled(False)
        QApplication.setOverrideCursor(Qt.WaitCursor)

        loaded_count = load_songs(
            folders, self.songs_path, self.progress_bar,
            self.available_list, self.default_icon_path
        )

        self.update_labels()
        self.setEnabled(True)
        QApplication.restoreOverrideCursor()

        self.progress_bar.setMaximum(1)
        self.progress_bar.setValue(0)

        if loaded_count == 0:
            self.songs_path = None
            QMessageBox.warning(self, "提示", "目前選擇的來源資料夾沒有符合 osu! 格式的歌曲資料夾!")

    # === selection ===
    def add_selected(self):
        for item in self.available_list.selectedItems():
            text = item.text()
            if not any(text == self.selected_list.item(i).text()
                       for i in range(self.selected_list.count())):
                self.selected_list.addItem(item.clone())
        self.available_list.clearSelection()
        self.update_labels()

    def remove_selected(self):
        for item in self.selected_list.selectedItems():
            self.selected_list.takeItem(self.selected_list.row(item))
        self.update_labels()

    def compress_selected(self):
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

    # === ui ===
    def update_compress_button_state(self):
        self.compress_btn.setEnabled(bool(self.songs_path and self.output_path))

    def update_labels(self):
        total_left = self.available_list.count()
        total_right = self.selected_list.count()
        selected_left = len(self.available_list.selectedItems())
        selected_right = len(self.selected_list.selectedItems())
        self.available_label.setText(f"可壓縮歌曲(共 {total_left} 首，已選 {selected_left} 首)")
        self.selected_label.setText(f"已選取歌曲(共 {total_right} 首，已選 {selected_right} 首)")

    def update_style(self, styles: dict):
        # scroller
        border = styles.get("border")
        scroller_bg = styles.get("scroller_bg")
        scroller_handle = styles.get("scroller_handle")
        scroller_handle_hover = styles.get("scroller_handle_hover")
        scroller_handle_pressed = styles.get("scroller_handle_pressed")

        style = f"""
            QListWidget {{             
                border: 3px solid {border};     
                border-radius: 5px;
                padding: 5px;                
                outline: 0;                    
            }}
            QListWidget::item {{
                padding: 3px 1px;              
                margin: 2px 0;                 
                border-radius: 5px;    
            }}
            QScrollBar:vertical {{
                background: {scroller_bg};
                width: {12}px;
                border-radius: {6}px;
            }}
            QScrollBar::handle:vertical {{
                background: {scroller_handle};
                min-height: 20px;
                border-radius: {6}px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {scroller_handle_hover};
            }}
            QScrollBar::handle:vertical:pressed {{
                background: {scroller_handle_pressed};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """
        self.available_list.setStyleSheet(style)
        self.selected_list.setStyleSheet(style)
        self.available_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.selected_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # processor bar
        proccese_bg = styles.get("progress_bg")
        proccese_chunk = styles.get("progress_chunk")

        style = f"""
            QProgressBar {{
                background-color: {proccese_bg};
                border-radius: {8}px;
                text-align: center;
                height: {20}px;
            }}
            QProgressBar::chunk {{
                background-color: {proccese_chunk};
                border-radius: {8}px;
            }}
        """
        self.progress_bar.setStyleSheet(style)

        # 吉祥物圖片(未完成!)
        pass