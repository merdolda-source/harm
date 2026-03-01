import cloudscraper
from bs4 import BeautifulSoup
import re
import json
import time
import os

class DiziPal:
    def __init__(self):
        self.main_url = "https://dizipal.bar"
        # Cloudflare aşmak için gelişmiş scraper
        self.scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
        )
    
    def fix_url(self, url):
        if not url: return ""
        if url.startswith("http"): return url
        if url.startswith("//"): return f"https:{url}"
        return f"{self.main_url}{url}"
    
    def get_soup(self, url):
        try:
            response = self.scraper.get(url, timeout=20)
            if response.status_code != 200:
                print(f"⚠️ Site Hatası: {response.status_code}")
                return None
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"❌ Bağlantı Hatası: {e}")
            return None

    def tum_filmleri_topla(self, max_sayfa_limiti=3):
        print("🎬 Tarama başlatılıyor...")
        tum_filmler = {}
        film_id = 1
        
        # Test amaçlı sadece 'aksiyon' kategorisini örnek alalım (Hız için)
        kategoriler = {f"{self.main_url}/kategori/aksiyon/": "Aksiyon"} 
        
        for url, ad in kategoriler.items():
            print(f"📁 {ad} taranıyor...")
            for sayfa in range(1, max_sayfa_limiti + 1):
                target = url if sayfa == 1 else f"{url}page/{sayfa}/"
                soup = self.get_soup(target)
                if not soup: break
                
                items = soup.select("div.grid div.post-item, article")
                if not items: break
                
                for item in items:
                    a = item.select_one("a")
                    if a:
                        tum_filmler[str(film_id)] = {
                            'isim': a.get('title') or a.text.strip(),
                            'link': self.fix_url(a.get('href')),
                            'resim': "", # Hız için boş bırakıldı
                            'embed': "",
                            'kategori': ad
                        }
                        film_id += 1
                        print(".", end="", flush=True)
                time.sleep(1)
        return tum_filmler

    def html_olustur(self, filmler):
        filmler_str = json.dumps(filmler, ensure_ascii=False)
        # Senin orijinal HTML tasarımın (Özetlenmiş hali)
        html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>DiziPal TV</title>
        <style>body{{background:#0a0c0f;color:#fff;font-family:sans-serif;}} .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px;padding:20px;}}</style>
        </head><body><div class="grid" id="g"></div>
        <script>var d={filmler_str}; var g=document.getElementById('g'); Object.values(d).forEach(f=>{{ g.innerHTML+='<div onclick="window.open(\''+f.link+'\')">'+f.isim+'</div>'; }});</script>
        </body></html>"""
        
        with open('dizipal.html', 'w', encoding='utf-8') as f: f.write(html)
        with open('dizipal_tv.html', 'w', encoding='utf-8') as f: f.write(html)
        print("\n✅ Dosyalar yazıldı.")

if __name__ == "__main__":
    dizi = DiziPal()
    # HATA ÖNLEYİCİ: Dosyaları en başta boş oluştur
    open('dizipal.html', 'a').close()
    open('dizipal_tv.html', 'a').close()
    
    veriler = dizi.tum_filmleri_topla(max_sayfa_limiti=2)
    dizi.html_olustur(veriler)
