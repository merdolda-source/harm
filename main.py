import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import os

# URL
url = "https://www.haremaltin.com/?lang=es"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def veri_cek():
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            container = soup.find("div", class_="tableContent viewContainer")
            
            # Verileri CSV dosyasına ekleyelim
            dosya_adi = "altin_fiyatlari.csv"
            dosya_var_mi = os.path.exists(dosya_adi)
            
            with open(dosya_adi, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Dosya yeni oluşturuluyorsa başlık ekle
                if not dosya_var_mi:
                    writer.writerow(["Tarih", "Kod", "Alış", "Satış"])
                
                if container:
                    rows = container.find_all("tr")
                    tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    for row in rows:
                        cols = row.find_all(["td", "th"])
                        data = [ele.get_text(strip=True) for ele in cols]
                        if len(data) >= 4:
                            # Tarih + İlgili sütunları al (Örn: Kod, Alış, Satış)
                            writer.writerow([tarih, data[0], data[2], data[3]])
                    
                    print("Veriler başarıyla kaydedildi.")
                else:
                    print("Tablo bulunamadı.")
        else:
            print("Siteye erişilemedi.")
            
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    veri_cek()
