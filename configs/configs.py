from pathlib import Path

CONFIG_MOLDULE = {
    "app_name": "osu! Songs Compressor",
    "version": "v1.0.2",
    "window": {
        "default_width": 950,
        "default_height": 620,
        "styles": {
            "dark_mode": {
                "background": "#121212",
                "foreground": "#E0E0E0",
                "secondary_text": "#A0A0A0",
                "button_bg": "#1F1F1F",
                "button_fg": "#FFFFFF",
                "highlight": "#BB86FC",
                "border": "#333333",
                "tooltip_bg": "#2C2C2C",
                "tooltip_fg": "#FFFFFF",
                "progress_bg": "#333333",
                "progress_chunk": "#BB86FC",
                "progress_height": 20,
                "progress_radius": 8,
            },
            "light_mode": {
                "background": "#FFFFFF",
                "foreground": "#000000",
                "secondary_text": "#555555",
                "button_bg": "#F0F0F0",
                "button_fg": "#000000",
                "highlight": "#62A6BBFF",
                "border": "#CCCCCC",
                "tooltip_bg": "#FFFFE0",
                "tooltip_fg": "#000000",
                "progress_bg": "#EEEEEE",
                "progress_chunk": "#B9D5FF",
                "progress_height": 20,
                "progress_radius": 8,
            }
        }
    }
}

APP_NAME = CONFIG_MOLDULE["app_name"]
VERSION = CONFIG_MOLDULE["version"]
WINDOW_DEFAULT_WIDTH = CONFIG_MOLDULE["window"]["default_width"]
WINDOW_DEFAULT_HEIGHT = CONFIG_MOLDULE["window"]["default_height"]
DARK_MODE_STYLES = CONFIG_MOLDULE["window"]["styles"]["dark_mode"]
LIGHT_MODE_STYLES = CONFIG_MOLDULE["window"]["styles"]["light_mode"]

user_data_dir = Path.home() / ".osu_compressor"
user_data_dir.mkdir(exist_ok=True)
DB_PATH = str(user_data_dir / "settings")