from configs import DB_PATH
import shelve
from typing import Literal

# SETTINGS = {
#     "dir": {
#         "songs_dir": None,
#         "target_dir": None
#     },
#     "personalization": {
#         "dark_mode": False,
#         "show_mascot": False
#     }
# }

def initailize_settings_file():
    with shelve.open(DB_PATH) as db:
        
        db.get("dir", {"songs_dir": None, "target_dir": None})
        db.get("personalization", {"dark_mode": False, "show_mascot": True})

def save_setting(setting_type: Literal["dir", "personalization"], key: str, value):
    with shelve.open(DB_PATH) as db:
        # dirs
        if setting_type == "dir":
            dirs = db.get("dir", {"songs_dir": None, "target_dir": None})
            dirs[key] = value
            db[setting_type] = dirs
        # personalization
        else:
            personalization = db.get("personalization", {"dark_mode": False, "show_mascot": True})
            personalization[key] = value
            db[setting_type] = personalization

def fetch_setting(setting_type: Literal["dir", "personalization"], key: str):
    with shelve.open(DB_PATH) as db:
        if setting_type == "dir":
            dirs = db.get("dir", {"songs_dir": None, "target_dir": None})
            return dirs[key]
        # personalization
        else:
            personalization = db.get("personalization", {"dark_mode": False, "show_mascot": True})
            return personalization[key]
            
