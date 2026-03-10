import os
import pygame
from config import DATA_DIR, logger

# Ensure assets directory exists
AUDIO_DIR = os.path.join(os.path.dirname(DATA_DIR), 'assets', 'sounds')
os.makedirs(AUDIO_DIR, exist_ok=True)
LOFI_FILE = os.path.join(AUDIO_DIR, "lofi_bg.mp3")

try:
    pygame.mixer.init()
    _mixer_ready = True
except Exception as e:
    logger.warning(f"Pygame mixer ishga tushmadi: {e}")
    _mixer_ready = False

def play_lofi():
    """Play the background lofi music on a loop if file exists."""
    if not _mixer_ready:
        return
    if not os.path.exists(LOFI_FILE):
        logger.info("Lo-Fi fayl topilmadi. assets/sounds/lofi_bg.mp3 faylini o'zingiz qo'ying.")
        return
    try:
        pygame.mixer.music.load(LOFI_FILE)
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)  # Loop indefinitely
        logger.info("Lo-Fi musiqa boshlandi")
    except Exception as e:
        logger.error("Lo-Fi play qilishda xatolik", exc_info=True)

def stop_lofi():
    """Stop the background music."""
    if not _mixer_ready:
        return
    try:
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.fadeout(2000)
            logger.info("Lo-Fi musiqa to'xtatildi")
    except Exception as e:
        logger.error("Lo-Fi stop qilishda xatolik", exc_info=True)
