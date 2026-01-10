from curl_cffi import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import os

# Yeni URL
url = "https://canlipiyasalar.haremaltin.com/"
dosya_adi = "canli_piyasa.csv"

def veri_cek():
    try:
        # Chrome taklidi yaparak siteye giriyoruz
        response = requests.get(url, impersonate="chrome110", timeout=20)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Senin verdiğin özel div sınıfını arıyoruz
            list_table = soup.find("div", class_="list-table")
            
            if list_table:
                # Div'in içindeki tabloyu bul
                table = list_table.find("table")
                
                if table:
                    rows = table.find_all("tr")
                    tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Dosyayı yazma modu (Varsa üzerine ekle)
                    dosya_var_mi = os.path.exists(dosya_adi)
                    
                    with open(dosya_adi, mode='a', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        
                        # Eğer dosya yeni oluşuyorsa başlıkları ekle
                        if not dosya_var_mi:
                            # Tablonun başlıklarını (th) otomatik bul
                            basliklar = ["Tarih"] + [th.get_text(strip=True) for th in rows[0].find_all(["th", "td"])]
                            writer.writerow(basliklar)
                        
                        # Satırları (td) tek tek gez ve kaydet
                        veri_sayisi = 0
                        # İlk satır başlık olduğu için 1. indexten başlıyoruz
                        for row in rows[1:]:
                            cols = row.find_all("td")
                            # Sütunları temizleyip listeye çevir
                            data = [ele.get_text(strip=True) for ele in cols]
                            
                            if data: # Boş satır değilse yaz
                                writer.writerow([tarih] + data)
                                veri_sayisi += 1
                                
                    print(f"BAŞARILI: {veri_sayisi} satır veri çekildi ve '{dosya_adi}' dosyasına kaydedildi.")
                else:
                    print("HATA: 'list-table' bulundu ama içinde 'table' yok.")
            else:
                print("HATA: 'list-table' sınıfına sahip div bulunamadı.")
                # Site içeriğini kontrol için (Debug)
                # print(soup.prettify()[:1000]) 
                
        else:
            print(f"HATA: Siteye girilemedi. Durum Kodu: {response.status_code}")

    except Exception as e:
        print(f"Bir hata oluştu: {e}")

if __name__ == "__main__":
    veri_cek()
