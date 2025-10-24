import os
from typing import List

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