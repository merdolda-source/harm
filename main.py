import requests
import json
import csv
import os
from datetime import datetime

# Hedef URL (Senin verdiğin mobil link)
url = "https://mobil.haremaltin.com/index.php?islem=cur__history&device_id=6f8a00c36020b7f4&dil_kodu=tr"

# Dosya adı
dosya_adi = "mobil_veri_gecmis.csv"

# Bugünün tarihini al (Otomatik olması için)
# İstersen senin verdiğin '2026-01-11' tarihini de elle yazabilirsin.
bugun = datetime.now().strftime("%Y-%m-%d")
baslangic = f"{bugun} 00:00:00"
bitis = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# HEADERS: Burası çok önemli, siteye "Ben Android Uygulamasıyım" diyoruz.
headers = {
    "User-Agent": "okhttp/4.9.2",  # <-- Altın anahtar burası
    "Accept-Encoding": "gzip",
    "Connection": "Keep-Alive",
    # Cookie'yi ekleyelim ama genelde mobil API'ler cookiesiz de yeni session açar.
    "Cookie": "PHPSESSID=dtckdctcili54mmrmmudsf3dcm; AWSALB=nCxKHuwvi5Tb5wafu4GaiGBeptFoVopCXyiat0jDaCv9U4PMkoiZYBUg3MRVM6mzumLcspUoK/UaZF6kD1WteRuJdrEBNd6sVqluYi3RF4b2UirW5kan3so8H2+Y" 
}

# MULTIPART DATA: Senin gönderdiğin ham verinin Pythoncası
# kod[] alanını senin isteğindeki gibi çoğaltıyoruz.
payload = [
    ('device_id', '6f8a00c36020b7f4'),
    ('dil_kodu', 'tr'),
    ('kod[]', 'USDTRY'),
    ('kod[]', 'EURTRY'),
    ('kod[]', 'JPYTRY'),
    ('kod[]', 'GBPTRY'),
    ('kod[]', 'ALTIN'),      # Ekstra: Gram Altın
    ('kod[]', 'CEYREK_YENI'), # Ekstra: Çeyrek
    ('tarih1', baslangic),   # Senin verdiğin: 2026-01-11 00:00:00
    ('tarih2', bitis),       # Senin verdiğin: 2026-01-11 00:02:22
    ('interval', 'dakika')
]

def veri_cek():
    print(f"Mobil API'ye istek atılıyor... ({baslangic} - {bitis})")
    
    try:
        # verify=False SSL hatasını önler (Mobil sertifikaları bazen farklıdır)
        response = requests.post(url, headers=headers, files=payload, timeout=30)
        
        if response.status_code == 200:
            try:
                # Gelen veri JSON formatındadır
                json_data = response.json()
                
                if "data" in json_data and json_data["data"]:
                    veriler = json_data["data"]
                    print(f"Başarılı! {len(veriler)} adet veri geldi.")
                    
                    # CSV'ye kaydetme işlemi
                    dosya_var_mi = os.path.exists(dosya_adi)
                    
                    with open(dosya_adi, mode='a', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        
                        # Başlıkları sadece dosya yoksa yaz
                        if not dosya_var_mi:
                            # JSON'dan gelen anahtarları başlık yap (tarih, kod, alis, satis vs.)
                            header = list(veriler[0].keys())
                            writer.writerow(header)
                        
                        # Verileri yaz
                        for satir in veriler:
                            writer.writerow(satir.values())
                            
                    print("Veriler CSV dosyasına kaydedildi.")
                else:
                    print("API yanıt verdi ama veri boş döndü (Tarih aralığında veri olmayabilir).")
                    print("Gelen Yanıt:", json_data)
                    
            except json.JSONDecodeError:
                print("HATA: Gelen yanıt JSON değil.")
                print(response.text[:200]) # İlk 200 karakteri göster
        else:
            print(f"HATA: HTTP {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Bir hata oluştu: {e}")

if __name__ == "__main__":
    veri_cek()
