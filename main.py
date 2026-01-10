import cloudscraper # Requests yerine bunu kullanıyoruz
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import os

# TAKİP LİSTESİ
takip_listesi = [
    # --- ALTIN & GÜMÜŞ ---
    {"kod": "ALTIN", "ad": "Has Altın"},
    {"kod": "KULCEALTIN", "ad": "Gram Altın"},
    {"kod": "ONS", "ad": "Ons Altın"},
    {"kod": "USDKG", "ad": "Dolar/KG"},
    {"kod": "EURKG", "ad": "Euro/KG"},
    {"kod": "AYAR22", "ad": "22 Ayar Bilezik"},
    {"kod": "AYAR14", "ad": "14 Ayar"},
    {"kod": "XAUXAG", "ad": "Altın/Gümüş Rasyo"},
    {"kod": "GUMUSTRY", "ad": "Gümüş TL"},
    {"kod": "GUMUSUSD", "ad": "Gümüş USD"},
    {"kod": "XAGUSD", "ad": "Silver USD (Ons)"},
    {"kod": "PLATIN", "ad": "Platin"},
    {"kod": "XPTUSD", "ad": "Platin USD"},
    {"kod": "PALADYUM", "ad": "Paladyum"},
    {"kod": "XPDUSD", "ad": "Paladyum USD"},
    
    # --- Ziynet / Sarrafiye (YENİ) ---
    {"kod": "CEYREK_YENI", "ad": "Yeni Çeyrek"},
    {"kod": "YARIM_YENI", "ad": "Yeni Yarım"},
    {"kod": "TEK_YENI", "ad": "Yeni Tam"},
    {"kod": "ATA_YENI", "ad": "Yeni Ata"},
    {"kod": "ATA5_YENI", "ad": "Yeni Ata 5"},
    {"kod": "GREMESE_YENI", "ad": "Yeni Gremese"},

    # --- Ziynet / Sarrafiye (ESKİ) ---
    {"kod": "CEYREK_ESKI", "ad": "Eski Çeyrek"},
    {"kod": "YARIM_ESKI", "ad": "Eski Yarım"},
    {"kod": "TEK_ESKI", "ad": "Eski Tam"},
    {"kod": "ATA_ESKI", "ad": "Eski Ata"},
    {"kod": "ATA5_ESKI", "ad": "Eski Ata 5"},
    {"kod": "GREMESE_ESKI", "ad": "Eski Gremese"},

    # --- DÖVİZ ---
    {"kod": "USDTRY", "ad": "Dolar/TL"},
    {"kod": "EURTRY", "ad": "Euro/TL"},
    {"kod": "EURUSD", "ad": "Euro/Dolar"},
    {"kod": "GBPTRY", "ad": "Sterlin/TL"},
    {"kod": "CHFTRY", "ad": "İsviçre Frangı"},
    {"kod": "AUDTRY", "ad": "Avustralya Doları"},
    {"kod": "CADTRY", "ad": "Kanada Doları"},
    {"kod": "SARTRY", "ad": "Suudi Riyali"},
    {"kod": "JPYTRY", "ad": "Japon Yeni"},
]

dosya_adi = "altin_fiyatlari.csv"
url = "https://www.haremaltin.com/?lang=es"

def veri_cek():
    # Dosya yoksa başlıkları oluştur
    if not os.path.exists(dosya_adi):
        with open(dosya_adi, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Tarih", "Grup", "Kod", "Alış", "Satış"])

    try:
        # Cloudscraper ile bir tarayıcı oturumu oluşturuyoruz
        scraper = cloudscraper.create_scraper() 
        response = scraper.get(url) # requests.get yerine bunu kullanıyoruz
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            kayit_sayisi = 0

            with open(dosya_adi, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                for urun in takip_listesi:
                    kod = urun["kod"]
                    ad = urun["ad"]
                    
                    # 1. YÖNTEM
                    alis_id = f"alis__{kod}"
                    satis_id = f"satis__{kod}"
                    
                    alis_element = soup.find("span", id=alis_id)
                    satis_element = soup.find("span", id=satis_id)

                    # 2. YÖNTEM (Yedek)
                    if not alis_element:
                         alis_element = soup.find("span", id=f"alis__genel__{kod}")
                         satis_element = soup.find("span", id=f"satis__genel__{kod}")

                    alis_fiyat = alis_element.get_text(strip=True) if alis_element else "Bulunamadı"
                    satis_fiyat = satis_element.get_text(strip=True) if satis_element else "Bulunamadı"
                    
                    writer.writerow([tarih, ad, kod, alis_fiyat, satis_fiyat])
                    kayit_sayisi += 1
            
            print(f"BAŞARILI: {kayit_sayisi} veri çekildi.")
            
        else:
            print(f"HATA: Site yine engelledi. Kod: {response.status_code}")
            
    except Exception as e:
        print(f"Bir hata oluştu: {e}")

if __name__ == "__main__":
    veri_cek()
