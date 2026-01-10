import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import os

# Takip edilecek birimlerin kodları (HTML'deki ID'lere göre)
takip_listesi = [
    {"kod": "KULCEALTIN", "ad": "Gram Altın"},
    {"kod": "ONS", "ad": "Ons Altın"},
    {"kod": "USDTRY", "ad": "Dolar/TL"},
    {"kod": "EURTRY", "ad": "Euro/TL"},
    {"kod": "EURUSD", "ad": "Euro/Dolar"},
    {"kod": "USDKG", "ad": "Dolar/KG"},
    {"kod": "EURKG", "ad": "Euro/KG"},
    {"kod": "GUMUSTRY", "ad": "Gümüş/TL"}
]

dosya_adi = "altin_fiyatlari.csv"
url = "https://www.haremaltin.com/?lang=es"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def veri_cek():
    # Dosya yoksa başlıkları oluştur
    if not os.path.exists(dosya_adi):
        with open(dosya_adi, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Tarih", "Ad", "Kod", "Alış", "Satış"])

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            kayit_sayisi = 0

            with open(dosya_adi, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                for urun in takip_listesi:
                    kod = urun["kod"]
                    ad = urun["ad"]
                    
                    # HTML'deki özel ID'leri hedefliyoruz
                    alis_id = f"alis__genel__{kod}"
                    satis_id = f"satis__genel__{kod}"
                    
                    alis_element = soup.find("span", id=alis_id)
                    satis_element = soup.find("span", id=satis_id)
                    
                    # Eğer element bulunduysa metni al, bulunamazsa "Yok" yaz
                    alis_fiyat = alis_element.get_text(strip=True) if alis_element else "Bulunamadı"
                    satis_fiyat = satis_element.get_text(strip=True) if satis_element else "Bulunamadı"
                    
                    # Veriyi dosyaya yaz
                    writer.writerow([tarih, ad, kod, alis_fiyat, satis_fiyat])
                    kayit_sayisi += 1
            
            print(f"{kayit_sayisi} adet veri başarıyla eklendi.")
            
        else:
            print("Siteye erişilemedi.")
            
    except Exception as e:
        print(f"Hata oluştu: {e}")

if __name__ == "__main__":
    veri_cek()
