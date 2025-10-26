import os
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from PyQt5.QtWidgets import QProgressBar, QApplication

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
    max_workers = min(4, total)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(compress_song, name) for name in folder_names]
        for _ in as_completed(futures):
            success += 1
            progress_bar.setValue(success)
            QApplication.processEvents()

    return success