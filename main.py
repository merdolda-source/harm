import requests
import csv
import os
import json
from datetime import datetime, timedelta

# Hedef URL
url = "https://mobil.haremaltin.com/index.php?islem=cur__history&device_id=6f8a00c36020b7f4&dil_kodu=tr"
dosya_adi = "mobil_veri_son.csv"

# Tarih Ayarı (Otomatik Bugün)
# Senin raw isteğindeki gibi 00:00:00 ile şu anki saat arasını alıyoruz.
bugun = datetime.now().strftime("%Y-%m-%d")
su_an = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
baslangic = f"{bugun} 00:00:00"

# Eğer gece yarısıysa ve veri yoksa, dünü al (Güvenlik önlemi)
if datetime.now().hour < 1:
    duman = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    baslangic = f"{duman} 00:00:00"

print(f"Tarih Aralığı: {baslangic} -> {su_an}")

# Özel Sınır Belirteci (Senin gönderdiğin raw paketten)
boundary = "b637ad9c-65e7-4cb9-ac2e-e9df7e2cae18"

# HEADERS (Senin verdiğin raw headerlar)
headers = {
    "Host": "mobil.haremaltin.com",
    "Content-Type": f"multipart/form-data; boundary={boundary}",
    "Accept-Encoding": "gzip",
    "Cookie": "PHPSESSID=dtckdctcili54mmrmmudsf3dcm; AWSALB=nCxKHuwvi5Tb5wafu4GaiGBeptFoVopCXyiat0jDaCv9U4PMkoiZYBUg3MRVM6mzumLcspUoK/UaZF6kD1WteRuJdrEBNd6sVqluYi3RF4b2UirW5kan3so8H2+Y",
    "User-Agent": "okhttp/4.9.2",
    "Connection": "Keep-Alive"
}

# İstenen Kodlar (PHP formatında array olarak gidecek)
kodlar = ["USDTRY", "EURTRY", "JPYTRY", "GBPTRY", "ALTIN", "CEYREK_YENI", "ONS", "AYAR22"]

# Manuel Body Oluşturma Fonksiyonu
def create_raw_body(fields, boundary):
    body = []
    for key, value in fields:
        body.append(f"--{boundary}")
        body.append(f'Content-Disposition: form-data; name="{key}"')
        # Content-Length hesaplamaya gerek yok, requests halleder ama format önemli
        body.append("")
        body.append(str(value))
    
    body.append(f"--{boundary}--")
    body.append("")
    return "\r\n".join(body)

# Gönderilecek Veriler (Sırası Önemli Olabilir)
form_data = [
    ("device_id", "6f8a00c36020b7f4"),
    ("dil_kodu", "tr")
]

# Kodları dizi mantığıyla ekle (kod[] şeklinde)
for k in kodlar:
    form_data.append(("kod[]", k))

# Tarih ve Aralık
form_data.append(("tarih1", baslangic))
form_data.append(("tarih2", su_an))
form_data.append(("interval", "dakika")) # 'gun' veya 'dakika'

def veri_cek():
    try:
        # Body'yi string olarak oluşturup byte'a çeviriyoruz
        payload = create_raw_body(form_data, boundary).encode('utf-8')
        
        # verify=False, SSL hatası almamak için (Mobil API sertifikası bazen uyuşmaz)
        response = requests.post(url, headers=headers, data=payload, timeout=30)
        
        if response.status_code == 200:
            try:
                json_data = response.json()
                
                # Veri kontrolü
                if "data" in json_data and isinstance(json_data["data"], list) and len(json_data["data"]) > 0:
                    veriler = json_data["data"]
                    print(f"BAŞARILI: {len(veriler)} adet veri satırı çekildi.")
                    
                    dosya_var_mi = os.path.exists(dosya_adi)
                    with open(dosya_adi, mode='a', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        if not dosya_var_mi:
                            # Başlıkları dinamik al
                            keys = veriler[0].keys()
                            writer.writerow(keys)
                        
                        for satir in veriler:
                            writer.writerow(satir.values())
                            
                    print(f"Veriler '{dosya_adi}' dosyasına yazıldı.")
                else:
                    print("SUNUCU CEVABI BOŞ: Tarih aralığında işlem yok veya parametre hatası.")
                    print("Dönen Mesaj:", json_data)
                    
            except json.JSONDecodeError:
                print("JSON ÇÖZÜMLEME HATASI. Gelen Ham Veri:")
                print(response.text)
        else:
            print(f"HTTP HATA KODU: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"Bağlantı Hatası: {e}")

if __name__ == "__main__":
    veri_cek()
