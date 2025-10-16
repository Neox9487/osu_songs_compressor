import os
import sys
import zipfile
import shutil
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QListWidget, QMessageBox, QLabel, QListWidgetItem,
    QProgressBar
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize

from typing import List

# 對齊方式
# Qt.AlignLeft	 靠左對齊
# Qt.AlignRight	 靠右對齊
# Qt.AlignCenter 置中對齊
# Qt.AlignTop	 上對齊
# Qt.AlignBottom 下對齊

class OsuCompressor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("osu! 歌曲壓縮器 (.osz)")
        self.setGeometry(200, 150, 950, 620)

        main_layout = QVBoxLayout()

        # 路徑
        self.path_label = QLabel("尚未選擇 Songs 資料夾")
        self.path_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.path_label)

        self.output_label = QLabel("尚未選擇輸出資料夾")
        self.output_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.output_label)

        # 上面的按鈕列
        top_btns = QHBoxLayout()
        self.select_btn = QPushButton("選擇 Songs 資料夾")
        self.output_btn = QPushButton("選擇輸出目的地")
        self.refresh_btn = QPushButton("重新整理")
        self.compress_btn = QPushButton("壓縮右側清單至目的地資料夾")
        self.compress_btn.setEnabled(False)
        top_btns.addWidget(self.select_btn)
        top_btns.addWidget(self.output_btn)
        top_btns.addWidget(self.refresh_btn)
        top_btns.addWidget(self.compress_btn)
        main_layout.addLayout(top_btns)

        # 進度條
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)

        # 下面
        # 有歌曲跟新增刪除的地方
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

        # 綁定事件(按鈕的
        self.select_btn.clicked.connect(self.select_songs_folder)
        self.output_btn.clicked.connect(self.select_output_folder)
        self.refresh_btn.clicked.connect(self.load_song_folders)
        self.add_btn.clicked.connect(self.add_selected)
        self.remove_btn.clicked.connect(self.remove_selected)
        self.compress_btn.clicked.connect(self.compress_selected)
        self.available_list.itemSelectionChanged.connect(self.update_labels)
        self.selected_list.itemSelectionChanged.connect(self.update_labels)
        
        self.songs_path = None
        self.output_path = None

        # OSU 圖片路徑(給沒有 bg 的歌曲用
        self.default_icon_path = os.path.join(os.path.dirname(__file__), "assets", "osu.png")

    def select_songs_folder(self):
        "選 Songs 資料夾"
        folder = QFileDialog.getExistingDirectory(self, "選擇 osu! Songs 資料夾")
        if not folder:
            return
        self.songs_path = folder
        self.path_label.setText(f"已選擇 Songs 資料夾：{folder}")
        self.load_song_folders()
        self.update_compress_button_state()

    def select_output_folder(self):
        "選壓縮目osz要押去哪"
        folder = QFileDialog.getExistingDirectory(self, "選擇檔案輸出目的地")
        if not folder:
            return
        self.output_path = folder
        self.output_label.setText(f"已選擇輸出目的地：{folder}")
        self.update_compress_button_state()

    def update_compress_button_state(self):
        "更新壓縮按鈕(能不能開壓"
        self.compress_btn.setEnabled(bool(self.songs_path and self.output_path))

    def find_background_image(self, folder_path):
        "找歌曲的bg"
        osu_files: List[str] = [f for f in os.listdir(folder_path) if f.lower().endswith(".osu")]
        for osu_file in osu_files:
            osu_path = os.path.join(folder_path, osu_file)
            try:
                with open(osu_path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()

                in_events = False
                for line in lines:
                    line = line.strip()
                    if line.startswith("[Events]"):
                        in_events = True
                        continue
                    if in_events:
                        # 通常背景行長這樣：0,0,"bg.jpg",0,0
                        if line.startswith("0,0,") and '"' in line:
                            parts = line.split('"')
                            if len(parts) >= 2:
                                bg_filename = parts[1]
                                bg_path = os.path.join(folder_path, bg_filename)
                                if os.path.exists(bg_path):
                                    return bg_path
                                else:
                                    return None
            except Exception:
                continue
        return None

    def load_song_folders(self):
        "拿歌們"
        self.available_list.clear()
        if not self.songs_path:
            return
        
        folders = [d for d in sorted(os.listdir(self.songs_path)) if os.path.isdir(os.path.join(self.songs_path, d))]
        total = len(folders)
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(0)
    
        loaded_count = 0
        
        self.setEnabled(False)
        QApplication.setOverrideCursor(Qt.WaitCursor)

        for idx, folder_name in enumerate(folders, 1):
            folder_path = os.path.join(self.songs_path, folder_name)
    
            # 檢查格式
            has_osu = any(f.lower().endswith('.osu') for f in os.listdir(folder_path))
            has_music = any(f.lower().endswith(('.mp3', '.ogg', '.wav')) for f in os.listdir(folder_path))
            if not (has_osu and has_music):
                self.progress_bar.setValue(idx)
                QApplication.processEvents()
                continue
    
            # 處裡背景圖示
            bg = self.find_background_image(folder_path)
            pixmap = QPixmap(bg) if bg else QPixmap(self.default_icon_path)
            pixmap = pixmap.scaled(96, 54, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon = QIcon(pixmap)
    
            item = QListWidgetItem(icon, folder_name)
            self.available_list.addItem(item)
            loaded_count += 1
    
            self.progress_bar.setValue(idx)
            QApplication.processEvents()
            self.update_labels()

        self.setEnabled(True)
        QApplication.restoreOverrideCursor()

        self.progress_bar.setMaximum(1)
        self.progress_bar.setValue(0)

        if loaded_count == 0:
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

    # def delete_selected(self):
    #     "刪歌 用不到"
    #     if not self.songs_path:
    #         QMessageBox.warning(self, "錯誤", "請先選擇 Songs 資料夾！")
    #         return

    #     selected = self.selected_list.selectedItems()
    #     if not selected:
    #         QMessageBox.warning(self, "錯誤", "請先選擇要刪除的歌曲！")
    #         return

    #     reply = QMessageBox.question(
    #         self,
    #         "確認刪除",
    #         f"確定要刪除 {len(selected)} 首歌曲資料夾嗎？(無法復原)",
    #         QMessageBox.Yes | QMessageBox.No
    #     )
    #     if reply == QMessageBox.No:
    #         return

    #     deleted_count = 0
    #     for item in selected:
    #         folder_name = item.text()
    #         folder_path = os.path.join(self.songs_path, folder_name)
    #         if os.path.exists(folder_path):
    #             shutil.rmtree(folder_path)
    #             deleted_count += 1

    #     QMessageBox.information(self, "刪除完成", f"已刪除 {deleted_count} 首歌曲。")
    #     self.load_song_folders()
    #     self.selected_list.clear()
    #     self.update_labels()

    def compress_selected(self):
        "壓縮待壓縮區的歌曲至輸出目的地資料夾"
        if not (self.songs_path and self.output_path):
            QMessageBox.warning(self, "錯誤", "請先選擇 Songs 與輸出目的地！")
            return

        total = self.selected_list.count()
        if total == 0:
            QMessageBox.warning(self, "錯誤", "右側清單沒有歌曲可壓縮！")
            return

        self.setEnabled(False)  
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(0)

        success = 0
        for idx in range(total):
            folder_name = self.selected_list.item(idx).text()
            folder_path = os.path.join(self.songs_path, folder_name)
            osz_path = os.path.join(self.output_path, folder_name + ".osz")

            with zipfile.ZipFile(osz_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for root, _, files in os.walk(folder_path):
                    for f in files:
                        abs_path = os.path.join(root, f)
                        rel_path = os.path.relpath(abs_path, folder_path)
                        zf.write(abs_path, rel_path)

            success += 1
            self.progress_bar.setValue(idx + 1)
            QApplication.processEvents()  

        self.setEnabled(True)
        QApplication.restoreOverrideCursor()

        
        if total == success:
            QMessageBox.information(self, "完成", f"壓縮 {success} 首歌曲至\n{self.output_path}")
        else:
            QMessageBox.information(self, "完成", f"壓縮 {success} 首歌曲至\n{self.output_path}\n 有 {total-success} 首失敗")
        self.selected_list.clear()
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OsuCompressor()
    window.show()
    sys.exit(app.exec_())
