import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import os

# Dosya adı
dosya_adi = "altin_fiyatlari.csv"

# 1. Dosya yoksa hemen oluştur (Hata almamak için)
if not os.path.exists(dosya_adi):
    with open(dosya_adi, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Tarih", "Kod", "Alış", "Satış", "Durum"])

# Site Bilgileri
url = "https://www.haremaltin.com/?lang=es"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def veri_cek():
    tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            container = soup.find("div", class_="tableContent viewContainer")
            
            if container:
                rows = container.find_all("tr")
                veri_bulundu = False
                
                with open(dosya_adi, mode='a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    for row in rows:
                        cols = row.find_all(["td", "th"])
                        data = [ele.get_text(strip=True) for ele in cols]
                        if len(data) >= 4:
                            writer.writerow([tarih, data[0], data[2], data[3], "OK"])
                            veri_bulundu = True
                
                if veri_bulundu:
                    print("Veriler kaydedildi.")
                else:
                    print("Tablo var ama satır bulunamadı.")
            else:
                print("Tablo div'i bulunamadı (JS ile yükleniyor olabilir).")
        else:
            print(f"Siteye girilemedi. Kod: {response.status_code}")
            
    except Exception as e:
        print(f"Hata oluştu: {e}")

if __name__ == "__main__":
    veri_cek()
