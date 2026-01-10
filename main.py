from seleniumbase import SB
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import os
import time

url = "https://canlipiyasalar.haremaltin.com/"
dosya_adi = "canli_piyasa.csv"

def veri_cek():
    # UC=True modu Cloudflare'i "Ben insanım" diye kandırır
    with SB(uc=True, test=True, headless=False) as sb: 
        
        print("Siteye gizli modda gidiliyor...")
        try:
            # Cloudflare kontrolü için özel bağlantı
            sb.uc_open_with_reconnect(url, 6) 
            
            # Eğer ekranda 'Robot musun' kutucuğu varsa tıkla
            sb.uc_gui_click_captcha() 
            
            print("Tablo yüklenmesi bekleniyor...")
            # Tablonun yüklenmesi için 20 saniye mühlet veriyoruz
            sb.assert_element("div.list-table", timeout=20)
            
            # Sayfanın yüklenmiş son halini alıyoruz
            page_source = sb.get_page_source()
            soup = BeautifulSoup(page_source, "html.parser")
            
            list_table = soup.find("div", class_="list-table")
            
            if list_table:
                table = list_table.find("table")
                if table:
                    rows = table.find_all("tr")
                    tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    dosya_var_mi = os.path.exists(dosya_adi)
                    
                    with open(dosya_adi, mode='a', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        
                        # Dosya yoksa başlıkları ekle
                        if not dosya_var_mi:
                            basliklar = ["Tarih"] + [th.get_text(strip=True) for th in rows[0].find_all(["th", "td"])]
                            writer.writerow(basliklar)
                        
                        veri_sayisi = 0
                        # Verileri kaydet
                        for row in rows[1:]:
                            cols = row.find_all("td")
                            data = [ele.get_text(strip=True) for ele in cols]
                            
                            if data:
                                writer.writerow([tarih] + data)
                                veri_sayisi += 1
                                
                    print(f"BAŞARILI: {veri_sayisi} satır veri çekildi.")
                else:
                    print("HATA: Tablo bulundu ama içi boş.")
            else:
                print("HATA: Sayfa açıldı ama tablo div'i bulunamadı.")
                
        except Exception as e:
            print(f"Bir hata oluştu: {e}")
            # Hata anında ekran görüntüsü alır (debug için)
            sb.save_screenshot("hata.png")

if __name__ == "__main__":
    veri_cek()
