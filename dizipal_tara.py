import cloudscraper
from bs4 import BeautifulSoup
import re
import json
import time
import os

class DiziPal:
    def __init__(self):
        self.name = "DiziPal"
        self.main_url = "https://dizipal.bar"
        # Cloudflare aşmak için scraper oluştur
        self.scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
        )
        
        self.kategoriler = {
            f"{self.main_url}/kategori/aile/": "Aile",
            f"{self.main_url}/kategori/aksiyon/": "Aksiyon",
            f"{self.main_url}/kategori/animasyon/": "Animasyon",
            f"{self.main_url}/kategori/belgesel/": "Belgesel",
            f"{self.main_url}/kategori/bilim-kurgu/": "Bilim Kurgu",
            f"{self.main_url}/kategori/dram/": "Dram",
            f"{self.main_url}/kategori/fantastik/": "Fantastik",
            f"{self.main_url}/kategori/gerilim/": "Gerilim",
            f"{self.main_url}/kategori/gizem/": "Gizem",
            f"{self.main_url}/kategori/komedi/": "Komedi",
            f"{self.main_url}/kategori/korku/": "Korku",
            f"{self.main_url}/kategori/macera/": "Macera",
            f"{self.main_url}/kategori/muzik/": "Müzik",
            f"{self.main_url}/kategori/romantik/": "Romantik",
            f"{self.main_url}/kategori/savas/": "Savaş",
            f"{self.main_url}/kategori/suc/": "Suç",
            f"{self.main_url}/kategori/tarih/": "Tarih",
            f"{self.main_url}/kategori/vahsi-bati/": "Vahşi Batı",
            f"{self.main_url}/kategori/yerli/": "Yerli",
        }
    
    def fix_url(self, url):
        if not url: return ""
        if url.startswith("http"): return url
        if url.startswith("//"): return f"https:{url}"
        return f"{self.main_url}{url}"
    
    def get_soup(self, url):
        try:
            response = self.scraper.get(url, timeout=15)
            if response.status_code != 200: return None
            response.encoding = 'utf-8'
            return BeautifulSoup(response.text, 'html.parser')
        except: return None
    
    def toplam_sayfa_bul(self, kategori_url):
        soup = self.get_soup(kategori_url)
        if not soup: return 1
        sayfalama = soup.select("a.page-numbers")
        en_buyuk = 1
        for link in sayfalama:
            try:
                match = re.search(r'/page/(\d+)/', link.get('href', ''))
                if match:
                    num = int(match.group(1))
                    if num > en_buyuk: en_buyuk = num
            except: pass
        return en_buyuk

    def tum_filmleri_topla(self, max_sayfa_limiti=5):
        tum_filmler = {}
        film_id = 1
        for kategori_url, kategori_adi in self.kategoriler.items():
            toplam_sayfa = self.toplam_sayfa_bul(kategori_url)
            toplam_sayfa = min(toplam_sayfa, max_sayfa_limiti)
            print(f"Taranan: {kategori_adi} ({toplam_sayfa} sayfa)")
            
            for sayfa in range(1, toplam_sayfa + 1):
                url = kategori_url if sayfa == 1 else f"{kategori_url}page/{sayfa}/"
                soup = self.get_soup(url)
                if not soup: break
                
                for veri in soup.select("div.grid div.post-item, article"):
                    a_tag = veri.select_one("a")
                    if a_tag:
                        film_url = self.fix_url(a_tag.get('href', ''))
                        # Film detayına gir
                        try:
                            f_resp = self.scraper.get(film_url, timeout=10)
                            f_soup = BeautifulSoup(f_resp.text, 'html.parser')
                            
                            # Embed bul
                            embed = ""
                            iframe = f_soup.select_one("iframe")
                            if iframe: embed = self.fix_url(iframe.get('src') or iframe.get('data-src'))
                            
                            # Resim bul
                            img = ""
                            meta_img = f_soup.select_one("meta[property='og:image']")
                            if meta_img: img = meta_img.get('content', '')

                            tum_filmler[str(film_id)] = {
                                'isim': a_tag.get('title', '') or a_tag.text.strip(),
                                'resim': img,
                                'link': film_url,
                                'embed': embed,
                                'kategori': kategori_adi
                            }
                            film_id += 1
                            print(".", end="", flush=True)
                            time.sleep(0.3)
                        except: continue
        return tum_filmler

    def html_olustur(self, filmler):
        filmler_str = json.dumps(filmler, ensure_ascii=False)
        html_content = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <title>DiziPal TV Arşiv</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {{ background: #0a0c0f; color: #fff; font-family: sans-serif; }}
        .film-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 20px; padding: 20px; }}
        .film-card {{ background: #15161a; border-radius: 10px; overflow: hidden; border: 2px solid #323442; cursor: pointer; position: relative; }}
        .film-card:focus {{ border-color: #ffd700; transform: scale(1.05); outline: none; }}
        .film-card img {{ width: 100%; aspect-ratio: 2/3; object-fit: cover; }}
        .film-title {{ padding: 10px; font-size: 14px; text-align: center; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="film-grid" id="grid"></div>
    <script>
        var data = {filmler_str};
        var grid = document.getElementById('grid');
        Object.values(data).forEach(film => {{
            var card = document.createElement('div');
            card.className = 'film-card';
            card.tabIndex = 0;
            card.innerHTML = '<img src="' + film.resim + '"><div class="film-title">' + film.isim + '</div>';
            card.onclick = () => window.open(film.embed || film.link, '_blank');
            grid.appendChild(card);
        }});
    </script>
</body>
</html>"""
        with open('dizipal.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        with open('dizipal_tv.html', 'w', encoding='utf-8') as f:
            f.write(html_content)

if __name__ == "__main__":
    bot = DiziPal()
    # GitHub Action'ın hızlı bitmesi için limiti düşük tutuyorum (max_sayfa_limiti=2 gibi)
    veriler = bot.tum_filmleri_topla(max_sayfa_limiti=2)
    if veriler:
        bot.html_olustur(veriler)
    else:
        # Hata almamak için boş dosya oluştur
        open('dizipal.html', 'a').close()
