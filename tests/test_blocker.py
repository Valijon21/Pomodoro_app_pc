import unittest
from controllers.blocker import extract_keywords

class TestBlocker(unittest.TestCase):
    def test_extract_keywords_simple(self):
        # Basic domains
        self.assertCountEqual(extract_keywords("youtube.com"), ["youtube"])
        self.assertCountEqual(extract_keywords("instagram.com"), ["instagram"])
        
    def test_extract_keywords_multiple(self):
        # Multiple spacing formats
        self.assertCountEqual(
            extract_keywords("youtube.com, instagram.com test.com"), 
            ["youtube", "instagram", "test"]
        )
        
    def test_extract_keywords_with_protocols(self):
        # With http and https
        self.assertCountEqual(extract_keywords("https://kun.uz"), ["kun"])
        self.assertCountEqual(extract_keywords("http://daryo.uz/news"), ["daryo"])
        
    def test_extract_keywords_with_www(self):
        # With www.
        self.assertCountEqual(extract_keywords("www.google.com"), ["google"])
        self.assertCountEqual(extract_keywords("https://www.tiktok.com"), ["tiktok"])
        self.assertCountEqual(extract_keywords("www.t.me/durov"), ["t.me"])
        
    def test_extract_keywords_short_names(self):
        # Short TLDs
        self.assertCountEqual(extract_keywords("vk.com"), ["vk.com"])
        self.assertCountEqual(extract_keywords("ok.ru"), ["ok.ru"])

    def test_extract_keywords_newlines_and_spaces(self):
        # Mixed delimiters
        raw_input = "youtube \n instagram.com ; telegram, google   vk.com"
        expected = ["youtube", "instagram", "telegram", "google", "vk.com"]
        self.assertCountEqual(extract_keywords(raw_input), expected)

if __name__ == '__main__':
    unittest.main()
