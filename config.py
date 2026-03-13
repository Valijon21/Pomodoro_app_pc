import os
import logging
from dotenv import load_dotenv

# Get absolute path of the project directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load env variables
load_dotenv(os.path.join(BASE_DIR, '.env'))

# Data paths
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'pomodoro.db')
QUOTES_PATH = os.path.join(DATA_DIR, 'quotes.json')
TRANSLATIONS_PATH = os.path.join(DATA_DIR, 'translations.json')

import json
CURRENT_LANGUAGE = "uz"
FONT_SIZE = 14
translations = {}

def init_language():
    global CURRENT_LANGUAGE, translations, FONT_SIZE
    settings_file = os.path.join(DATA_DIR, 'settings.json')
    if os.path.exists(settings_file):
        try:
            with open(settings_file, "r", encoding="utf-8") as f:
                settings = json.load(f)
                CURRENT_LANGUAGE = settings.get("language", "uz")
                FONT_SIZE = settings.get("font_size", 14)
        except Exception:
            pass
            
    if os.path.exists(TRANSLATIONS_PATH):
        try:
            with open(TRANSLATIONS_PATH, "r", encoding="utf-8") as f:
                translations = json.load(f)
        except Exception:
            pass

def get_text(key):
    lang_dict = translations.get(CURRENT_LANGUAGE, translations.get("uz", {}))
    return lang_dict.get(key, key)

init_language()

# Logger setup
log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
log_level = getattr(logging, log_level_str, logging.INFO)

log_file_path = os.path.join(BASE_DIR, 'pomodoro.log')
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("PomodoroPro")

# Default Theme
DEFAULT_THEME = os.getenv("THEME", "Dark")

# UI Themes
THEMES = {
    "Dark": {
        "bg": "#1E1E1E",
        "fg": "#FFFFFF",
        "accent": "#BB86FC",
        "surface": "#2D2D2D",
        "error": "#CF6679",
        "success": "#03DAC6"
    },
    "Light": {
        "bg": "#F5F5F5",
        "fg": "#000000",
        "accent": "#6200EE",
        "surface": "#FFFFFF",
        "error": "#B00020",
        "success": "#018786"
    },
    "AMOLED": {
        "bg": "#000000",
        "fg": "#FFFFFF",
        "accent": "#FF0000",
        "surface": "#121212",
        "error": "#FF5252",
        "success": "#FF4081"
    }
}

# Default Theme
DEFAULT_THEME = "Dark"

# Time constants (in minutes)
POMODORO_TIME = 25
SHORT_BREAK = 5
LONG_BREAK = 15
