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

def play_lofi(custom_path=None):
    """Play background music. If custom_path is provided, play that file on a loop."""
    if not _mixer_ready:
        return
    
    music_file = custom_path if custom_path and os.path.exists(custom_path) else LOFI_FILE
    
    if not os.path.exists(music_file):
        logger.warning(f"Musiqa fayli topilmadi: {music_file}")
        return
        
    try:
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)  # Loop indefinitely
        logger.info(f"Musiqa boshlandi: {os.path.basename(music_file)}")
    except Exception as e:
        logger.error(f"Musiqa ijro etishda xatolik ({music_file}): {e}")

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
