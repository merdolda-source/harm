from seleniumbase import SB
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import os

# Ana Site URL
url = "https://www.haremaltin.com/?lang=es"
dosya_adi = "altin_fiyatlari.csv"

# Takip Edilecek Tüm Ürünler
takip_listesi = [
    # --- ALTIN GRUBU ---
    {"kod": "ALTIN", "ad": "Has Altın"},
    {"kod": "KULCEALTIN", "ad": "Gram Altın"},
    {"kod": "ONS", "ad": "Ons Altın"},
    {"kod": "AYAR22", "ad": "22 Ayar Bilezik"},
    {"kod": "AYAR14", "ad": "14 Ayar"},
    {"kod": "CEYREK_YENI", "ad": "Yeni Çeyrek"},
    {"kod": "CEYREK_ESKI", "ad": "Eski Çeyrek"},
    {"kod": "YARIM_YENI", "ad": "Yeni Yarım"},
    {"kod": "YARIM_ESKI", "ad": "Eski Yarım"},
    {"kod": "TEK_YENI", "ad": "Yeni Tam"},
    {"kod": "TEK_ESKI", "ad": "Eski Tam"},
    {"kod": "ATA_YENI", "ad": "Yeni Ata"},
    {"kod": "ATA_ESKI", "ad": "Eski Ata"},
    {"kod": "GREMESE_YENI", "ad": "Yeni Gremese"},
    {"kod": "GREMESE_ESKI", "ad": "Eski Gremese"},
    
    # --- GÜMÜŞ & PLATİN ---
    {"kod": "GUMUSTRY", "ad": "Gümüş TL"},
    {"kod": "GUMUSUSD", "ad": "Gümüş USD"},
    {"kod": "PLATIN", "ad": "Platin"},
    
    # --- DÖVİZ GRUBU ---
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

def veri_cek():
    # UC Modu ile Robot Kontrolünü Geçiyoruz
    with SB(uc=True, test=True, headless=False) as sb:
        print("Siteye bağlanılıyor (Gizli Mod)...")
        try:
            sb.uc_open_with_reconnect(url, 5)
            
            # Sayfanın tam yüklenmesi için kritik bir element bekliyoruz (Örn: Gram Altın Satırı)
            print("Verilerin yüklenmesi bekleniyor...")
            sb.assert_element('tr[id*="KULCEALTIN"]', timeout=20)
            
            # Kaynak kodunu al
            page_source = sb.get_page_source()
            soup = BeautifulSoup(page_source, "html.parser")
            
            tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            kayit_sayisi = 0
            
            # Dosyayı oluştur/aç
            dosya_var_mi = os.path.exists(dosya_adi)
            with open(dosya_adi, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if not dosya_var_mi:
                    writer.writerow(["Tarih", "Ürün", "Kod", "Alış", "Satış"])
                
                for urun in takip_listesi:
                    kod = urun["kod"]
                    ad = urun["ad"]
                    
                    # Ana sitede 2 tip ID var, ikisini de deniyoruz
                    # Tip 1: alis__ALTIN
                    # Tip 2: alis__genel__ALTIN
                    
                    alis_element = soup.find("span", id=f"alis__{kod}")
                    satis_element = soup.find("span", id=f"satis__{kod}")
                    
                    if not alis_element:
                        alis_element = soup.find("span", id=f"alis__genel__{kod}")
                        satis_element = soup.find("span", id=f"satis__genel__{kod}")
                    
                    # Veriyi al
                    alis = alis_element.get_text(strip=True) if alis_element else "Yok"
                    satis = satis_element.get_text(strip=True) if satis_element else "Yok"
                    
                    if alis != "Yok":
                        writer.writerow([tarih, ad, kod, alis, satis])
                        kayit_sayisi += 1
            
            print(f"BAŞARILI: Toplam {kayit_sayisi} adet ürünün fiyatı çekildi.")
            
        except Exception as e:
            print(f"HATA OLUŞTU: {e}")
            sb.save_screenshot("hata_ana_sayfa.png")

if __name__ == "__main__":
    veri_cek()
