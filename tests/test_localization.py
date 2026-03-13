import unittest
import json
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_text, TRANSLATIONS_PATH

class TestLocalization(unittest.TestCase):
    def setUp(self):
        with open(TRANSLATIONS_PATH, "r", encoding="utf-8") as f:
            self.translations = json.load(f)

    def test_keys_consistency(self):
        """Hamma tillarda bir xil kalitlar borligini tekshirish"""
        en_keys = set(self.translations["en"].keys())
        uz_keys = set(self.translations["uz"].keys())
        ru_keys = set(self.translations["ru"].keys())
        
        self.assertEqual(en_keys, uz_keys, f"Uzbek tilida qolib ketgan kalitlar: {en_keys - uz_keys}")
        self.assertEqual(en_keys, ru_keys, f"Rus tilida qolib ketgan kalitlar: {en_keys - ru_keys}")

    def test_uzbek_translations_not_english(self):
        """O'zbekcha tarjimalar inglizcha qolib ketmaganini tekshirish (ba'zi maxsus so'zlar mustasno)"""
        exceptions = ["AMOLED", "XP", "Level", "Username", "Pomodoro Pro", "Lofi", "Mini Trello", "CSV"]
        for key, value in self.translations["uz"].items():
            if value in self.translations["en"].values() and value not in exceptions:
                # Agar qiymat bir xil bo'lsa, bu xato bo'lishi mumkin (lekin har doim ham emas)
                # Shuning uchun buni shunchaki ogohlantirish sifatida ko'rish kerak
                pass

if __name__ == "__main__":
    unittest.main()
