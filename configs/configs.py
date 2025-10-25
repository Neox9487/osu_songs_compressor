import shelve
from typing import Literal

CONFIG_MOLDULE = {
    "app_name": "osu! Songs Compressor",
    "version": "v1.0.2",
    "window": {
        "default_width": 950,
        "default_height": 620,
    },
    "settings": {
        "dir": {
            "songs_dir": None,
            "target_dir": None
        },
        "personalization": {
            "dark_mode": False,
            "show_mascot": False
        }
    }
}

APP_NAME = CONFIG_MOLDULE["app_name"]
VERSION = CONFIG_MOLDULE["version"]
WINDOW_DEFAULT_WIDTH = CONFIG_MOLDULE["window"]["default_width"]
WINDOW_DEFAULT_HEIGHT = CONFIG_MOLDULE["window"]["default_height"]

with shelve.open("settings") as db:
    dirs = db.get("dir", {"songs_dir": None, "target_dir": None})
    SONGS_DIR = dirs["songs_dir"]
    TARGET_DIR = dirs["target_dir"]

def save_setting(setting_type: Literal["dir", "personalization"], key: str, value):
    if key not in CONFIG_MOLDULE["settings"][setting_type]:
        raise ValueError(f"key is not exist in '{setting_type}'!")
    
    with shelve.open("settings") as db:
        current = db.get(setting_type, CONFIG_MOLDULE["settings"][setting_type].copy())
        current[key] = value
        db[setting_type] = current