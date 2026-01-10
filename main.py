from seleniumbase import SB
from datetime import datetime
import csv
import os
import json
import time

# --- PHP DOSYASINDAN ALINAN AYARLAR ---

# Kodları Türkçe İsimlere Çeviren Liste (PHP'deki $GLOBALS['titles'])
TITLES = {
    "ALTIN": "HAS", "USDPURE": "USDPURE", "ONS": "ONS", "USDKG": "USD/KG", 
    "EURKG": "EUR/KG", "AYAR22": "22 AYAR", "KULCEALTIN": "ALTIN", "XAUXAG": "GÜMÜŞ", 
    "CEYREK_YENI": "ÇEYREK", "CEYREK_ESKI": "ÇEYREK", "YARIM_YENI": "YARIM", 
    "YARIM_ESKI": "YARIM", "TEK_YENI": "TAM", "TEK_ESKI": "TAM", "ATA_YENI": "ATA", 
    "ATA_ESKI": "ATA", "ATA5_YENI": "ATA-5", "ATA5_ESKI": "ATA-5", 
    "GREMESE_YENI": "GREMSE", "GREMESE_ESKI": "GREMSE", "AYAR14": "14 AYAR", 
    "GUMUSTRY": "GÜMÜŞ TL", "XAGUSD": "GÜMÜŞ ONS", "GUMUSUSD": "GÜMÜŞ USD", 
    "XPTUSD": "PLATİN ONS", "XPDUSD": "PALADYUM ONS", "PLATIN": "PLATİN/USD", 
    "PALADYUM": "PALADYUM/USD", "USDTRY": "Amerikan Doları", "OMRUSD": "OMRUSD", 
    "EURTRY": "Euro", "EURUSD": "EUR/USD", "GBPTRY": "İngiliz Sterlini", 
    "CHFTRY": "İsviçre Frangı", "AEDUSD": "AEDUSD", "AUDTRY": "Avustralya Doları", 
    "KWDUSD": "KWDUSD", "JODTRY": "JODTRY", "USDILS": "USDILS", "CADTRY": "Kanada Doları", 
    "USDMAD": "USDMAD", "OMRTRY": "OMRTRY", "USDQAR": "USDQAR", 
    "SARTRY": "Suudi Arabistan Riyali", "JODUSD": "JODUSD", 
    "AEDTRY": "Birleşik Arap Emirlikleri Dirhemi", "QARTRY": "Katar Riyali", 
    "USDCHF": "USDCHF", "KWDTRY": "KWDTRY", "AUDUSD": "AUDUSD", "ILSTRY": "ILSTRY", 
    "USDCAD": "USDCAD", "MADTRY": "MADTRY", "JPYTRY": "Japon Yeni", 
    "USDSAR": "USDSAR", "USDJPY": "USDJPY", "GBPUSD": "GBPUSD"
}

# Takip Edilecek Altınlar (PHP'deki $GLOBALS['altinlar'])
# PHP listesi çok kısaydı, buraya eksik olanları ekledim (Çeyrek vb.)
ALTIN_LISTESI = [
    "ALTIN", "ONS", "USDKG", "USDTRY", "KULCEALTIN", "AYAR22", "AYAR14", 
    "CEYREK_YENI", "CEYREK_ESKI", "YARIM_YENI", "YARIM_ESKI", 
    "TEK_YENI", "TEK_ESKI", "ATA_YENI", "ATA_ESKI", "GREMESE_YENI"
]

# Takip Edilecek Dövizler (PHP'deki $GLOBALS['dovizler'])
DOVIZ_LISTESI = [
    "USDTRY", "EURTRY", "EURUSD", "GBPTRY", "CHFTRY", "AUDTRY", 
    "CADTRY", "SARTRY", "AEDTRY", "QARTRY", "JPYTRY"
]

# ----------------------------------------

dosya_adi = "altin_fiyatlari.csv"
base_url = "https://www.haremaltin.com/"

def veri_cek():
    with SB(uc=True, test=True, headless=False) as sb:
        print("Siteye bağlanılıyor...")
        try:
            # Önce ana sayfaya git (Cookie ve Cloudflare izni almak için)
            sb.uc_open_with_reconnect(base_url, 5)
            
            tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            tum_veriler = []

            # --- API 1: ALTIN VERİLERİ ---
            print("Altın verileri API'den çekiliyor...")
            # Javascript ile tarayıcı içinden POST isteği atıyoruz (PHP curl taklidi)
            js_script_altin = """
                var callback = arguments[arguments.length - 1];
                fetch('https://www.haremaltin.com/dashboard/ajax/altin', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({"dil_kodu":"tr"})
                })
                .then(response => response.json())
                .then(data => callback(data))
                .catch(error => callback({"error": error}));
            """
            json_altin = sb.execute_async_script(js_script_altin)
            
            if json_altin and "data" in json_altin:
                for item in json_altin["data"]:
                    # Sadece PHP listesindekileri al
                    if item["code"] in ALTIN_LISTESI:
                        ad = TITLES.get(item["code"], item["code"]) # İsmi listeden bul
                        tum_veriler.append([tarih, "ALTIN", ad, item["code"], item["alis"], item["satis"]])

            # --- API 2: DÖVİZ VERİLERİ ---
            print("Döviz verileri API'den çekiliyor...")
            js_script_doviz = """
                var callback = arguments[arguments.length - 1];
                fetch('https://www.haremaltin.com/dashboard/ajax/doviz', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({"dil_kodu":"tr"})
                })
                .then(response => response.json())
                .then(data => callback(data))
                .catch(error => callback({"error": error}));
            """
            json_doviz = sb.execute_async_script(js_script_doviz)

            if json_doviz and "data" in json_doviz:
                for item in json_doviz["data"]:
                    # Sadece PHP listesindekileri al
                    if item["code"] in DOVIZ_LISTESI:
                        ad = TITLES.get(item["code"], item["code"])
                        tum_veriler.append([tarih, "DOVIZ", ad, item["code"], item["alis"], item["satis"]])

            # --- KAYDETME ---
            if tum_veriler:
                dosya_var_mi = os.path.exists(dosya_adi)
                with open(dosya_adi, mode='a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    if not dosya_var_mi:
                        writer.writerow(["Tarih", "Tur", "Urun", "Kod", "Alis", "Satis"])
                    
                    writer.writerows(tum_veriler)
                
                print(f"BAŞARILI: Toplam {len(tum_veriler)} satır veri API üzerinden çekildi.")
            else:
                print("HATA: Hiç veri çekilemedi. API yanıt vermedi.")

        except Exception as e:
            print(f"Bir hata oluştu: {e}")
            sb.save_screenshot("api_hata.png")

if __name__ == "__main__":
    veri_cek()
