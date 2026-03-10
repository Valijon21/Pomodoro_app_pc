import os
from config import logger

# Biz endi dasturda saytlarni "hosts" fayli orqali bloklamaymiz, 
# chunki xatolik yuz bersa, saytlar doimo bloklanib qolishi mumkin.
# Uning o'rniga faqat ochiq oyna sarlavhasini tekshirib, yopish yoki tushirish
# (minimize) usuli qo'llaniladi. Bu mantiq "timer_view.py" dagi 
# "_enforce_focus_mode" metodida muvaffaqiyatli ishlaydi.

def block_websites(sites_string):
    """
    Saytlarni bloklash endi asosiy dasturdagi tsikl orqali (oynalarni tekshirib yopish) bilan bajariladi.
    Hosts faylga yozish bekor qilingan (xavfsizlik va xatoliklar oldini olish uchun).
    """
    sites = [s.strip() for s in sites_string.split(",") if s.strip()]
    if not sites:
        return True
        
    logger.info(f"Yangi bloklash faollashdi (oynalar kuzatilmoqda): {sites}")
    return True

def unblock_websites(sites_string):
    """
    Blokni ochish (oynalar kuzatuvi to'xtatildi).
    """
    sites = [s.strip() for s in sites_string.split(",") if s.strip()]
    if not sites:
        return True
        
    logger.info(f"Bloklangan saytlar kuzatuvi to'xtatildi: {sites}")
    return True

import re

def extract_keywords(blocked_sites: str) -> list[str]:
    """
    Kiritilgan durlardan sayt kalit so'zlarini xavfsiz ajratib olish moduli.
    Misol uchun: 'youtube.com, http://t.me/durov' -> ['youtube', 't.me']
    """
    words = re.split(r'[,;\s]+', blocked_sites.strip())
    keywords = []
    for w in words:
        if not w: continue
        w = w.lower()
        
        # Remove protocol and path
        if "://" in w:
            w = w.split("://")[-1]
        w = w.split("/")[0].split("?")[0]
        
        # Remove www.
        if w.startswith("www."):
            w = w[4:]
            
        added = False
        # Extract the base domain name (e.g., youtube from youtube.com)
        parts = w.split(".")
        if len(parts) >= 2:
            ignore_domains = ["com", "org", "net", "edu", "gov", "co", "io", "uz", "ru", "info", "me", "uzb", "www", "tv"]
            for p in reversed(parts[:-1]):
                if len(p) >= 3 and p not in ignore_domains:
                    keywords.append(p)
                    added = True
                    break
                    
        if not added and len(w) >= 3:
            keywords.append(w)
            
    # Remove duplicates
    return list(set([k for k in keywords if len(k) >= 3]))

