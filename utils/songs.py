import os
import zipfile
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import ( QListWidget, QListWidgetItem, QProgressBar, QApplication)

def find_background_image(folder_path: str):
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

def load_songs(folders, songs_path, progress_bar: QProgressBar, available_list: QListWidget, default_icon_path: str):
    """載入歌曲資料夾"""
    loaded_count = 0

    total = len(folders)
    progress_bar.setMaximum(total)
    progress_bar.setValue(0)

    def process_folder(folder_name):
        folder_path = os.path.join(songs_path, folder_name)
        try:
            files = os.listdir(folder_path)
        except PermissionError:
            return None 

        has_osu = any(f.lower().endswith('.osu') for f in files)
        has_music = any(f.lower().endswith(('.mp3', '.ogg', '.wav')) for f in files)
        if not (has_osu and has_music):
            return None

        bg = find_background_image(folder_path)
        return folder_name, bg

    max_workers = max(1, min(4, total))
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_folder, name): name for name in folders}

        for idx, future in enumerate(as_completed(futures), 1):
            result = future.result()
            if result:
                folder_name, bg = result
                pixmap = QPixmap(bg) if bg else QPixmap(default_icon_path)
                pixmap = pixmap.scaled(96, 54, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                icon = QIcon(pixmap)
                item = QListWidgetItem(icon, folder_name)
                available_list.addItem(item)
                results.append(folder_name)
                loaded_count += 1

            progress_bar.setValue(idx)
            QApplication.processEvents()

    progress_bar.setMaximum(1)
    progress_bar.setValue(0)
    return loaded_count

def compress_songs(folder_names, songs_path, output_path, progress_bar: QProgressBar):
    "壓縮待壓縮區的歌曲至輸出目的地資料夾"
    total = len(folder_names)
    progress_bar.setMaximum(total)
    progress_bar.setValue(0)

    def compress_song(folder_name):
        folder_path = os.path.join(songs_path, folder_name)
        osz_path = os.path.join(output_path, folder_name + ".osz")
        with zipfile.ZipFile(osz_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(folder_path):
                for f in files:
                    abs_path = os.path.join(root, f)
                    rel_path = os.path.relpath(abs_path, folder_path)
                    zf.write(abs_path, rel_path)
        return folder_name

    success = 0
    max_workers = max(1, min(4, total))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(compress_song, name) for name in folder_names]
        for _ in as_completed(futures):
            success += 1
            progress_bar.setValue(success)
            QApplication.processEvents()

    return success