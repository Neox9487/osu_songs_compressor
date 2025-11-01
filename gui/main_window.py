from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedLayout
from utils.settings import fetch_setting
from configs import (APP_NAME, WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT, DARK_MODE_STYLES, LIGHT_MODE_STYLES)

from gui.pages import CompressorPage
from gui.pages import SettingsPage

class OsuCompressor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setGeometry(0, 0, WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT)

        # 主結構
        root_layout = QVBoxLayout(self)
        self.setLayout(root_layout)

        # 上方選單
        menu_bar = QHBoxLayout()
        self.compressor_btn = QPushButton("Compressor")
        self.settings_btn = QPushButton("Settings")
        menu_bar.addWidget(self.compressor_btn)
        menu_bar.addWidget(self.settings_btn)
        root_layout.addLayout(menu_bar)

        # 頁面堆疊
        self.pages = QStackedLayout()
        root_layout.addLayout(self.pages)

        # 建立頁面
        self.compressor_page = CompressorPage()
        self.settings_page = SettingsPage(self)

        self.pages.addWidget(self.compressor_page)
        self.pages.addWidget(self.settings_page)

        # 綁定切換
        self.compressor_btn.clicked.connect(self.select_compressor_page)
        self.settings_btn.clicked.connect(self.select_settings_page)

    # 初始化設定與樣式
    def initialize(self):
        dark_mode = fetch_setting("personalization", "dark_mode")
        show_mascot = fetch_setting("personalization", "show_mascot")
        style = DARK_MODE_STYLES if dark_mode else LIGHT_MODE_STYLES
        self.update_windows_style(style)
        self.compressor_page.initialize()

    # select page
    def select_compressor_page(self):
        self.pages.setCurrentWidget(self.compressor_page)

    def select_settings_page(self):
        self.settings_page.update_info()
        self.pages.setCurrentWidget(self.settings_page)

    # === styles ===
    def update_windows_style(self, style):
        bg = style.get("background")
        fg = style.get("foreground")
        button_bg = style.get("button_bg")
        button_fg = style.get("button_fg")
        highlight = style.get("highlight")

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg};
                color: {fg};
                font-size: 12px;
                font-weight: bold; 
            }}
            QPushButton {{
                background-color: {button_bg};
                color: {button_fg};
                font-size: 12px;
                border-radius: {8}px;     
                padding: {4}px {6}px;         
                font-weight: bold;        
            }}
            QListWidget::item:selected {{
                background-color: {highlight};
            }}
        """)

        self.compressor_page.update_style(style)
