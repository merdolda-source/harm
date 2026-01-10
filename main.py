import requests
import csv
import os
import json
from datetime import datetime, timedelta

# URL
url = "https://mobil.haremaltin.com/index.php?islem=cur__history&device_id=6f8a00c36020b7f4&dil_kodu=tr"
csv_dosya_adi = "harem_gecmis.csv"
json_dosya_adi = "harem_gecmis.json"

# Tarih Ayarı (Otomatik Bugün)
bugun = datetime.now().strftime("%Y-%m-%d")
su_an = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
baslangic = f"{bugun} 00:00:00"

# Gece yarısı koruması
if datetime.now().hour < 1:
    duman = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    baslangic = f"{duman} 00:00:00"

print(f"Tarih Aralığı: {baslangic} -> {su_an}")

boundary = "b637ad9c-65e7-4cb9-ac2e-e9df7e2cae18"

headers = {
    "Host": "mobil.haremaltin.com",
    "Content-Type": f"multipart/form-data; boundary={boundary}",
    "Accept-Encoding": "gzip",
    "Cookie": "PHPSESSID=dtckdctcili54mmrmmudsf3dcm",
    "User-Agent": "okhttp/4.9.2",
    "Connection": "Keep-Alive"
}

# Takip Edilecekler
kodlar = ["USDTRY", "EURTRY", "JPYTRY", "GBPTRY", "ALTIN", "CEYREK_YENI", "ONS", "AYAR22"]

# Manuel Body Oluşturucu (Bu kısım harika çalışıyor, aynen kalsın)
def create_raw_body(fields, boundary):
    body = []
    for key, value in fields:
        body.append(f"--{boundary}")
        body.append(f'Content-Disposition: form-data; name="{key}"')
        body.append("")
        body.append(str(value))
    body.append(f"--{boundary}--")
    body.append("")
    return "\r\n".join(body)

form_data = [("device_id", "6f8a00c36020b7f4"), ("dil_kodu", "tr")]
for k in kodlar:
    form_data.append(("kod[]", k))
form_data.append(("tarih1", baslangic))
form_data.append(("tarih2", su_an))
form_data.append(("interval", "dakika"))

def veri_cek():
    try:
        payload = create_raw_body(form_data, boundary).encode('utf-8')
        response = requests.post(url, headers=headers, data=payload, timeout=30)
        
        if response.status_code == 200:
            try:
                # Gelen yanıtı al
                ham_veri = response.json()
                
                # --- YENİ PARÇALAMA MANTIĞI BURADA ---
                islenmis_liste = []
                
                # Gelen yanıt bir sözlük (dict). Her anahtarı (örn: USDTRY) tek tek geziyoruz.
                if isinstance(ham_veri, dict):
                    for para_birimi, icerik in ham_veri.items():
                        # Eğer bu anahtarın içinde 'data' listesi varsa
                        if isinstance(icerik, dict) and "data" in icerik and isinstance(icerik["data"], list):
                            for satir in icerik["data"]:
                                # Hangi para birimi olduğunu satıra ekleyelim
                                satir["KOD"] = para_birimi 
                                islenmis_liste.append(satir)
                
                # Veri Var mı Kontrolü
                if len(islenmis_liste) > 0:
                    print(f"BAŞARILI: Toplam {len(islenmis_liste)} satır veri bulundu.")
                    
                    # 1. JSON OLARAK KAYDET (İstediğin Gibi)
                    with open(json_dosya_adi, 'w', encoding='utf-8') as f:
                        json.dump(islenmis_liste, f, indent=4, ensure_ascii=False)
                    print(f"-> Veriler '{json_dosya_adi}' dosyasına kaydedildi.")

                    # 2. CSV OLARAK KAYDET (Excel için)
                    dosya_var_mi = os.path.exists(csv_dosya_adi)
                    with open(csv_dosya_adi, mode='a', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        
                        # Sütun başlıklarını belirle (KOD, kayit_tarihi, alis, satis)
                        basliklar = ["KOD", "kayit_tarihi", "alis", "satis"]
                        
                        if not dosya_var_mi:
                            writer.writerow(basliklar)
                        
                        for satir in islenmis_liste:
                            # Sadece istediğimiz sütunları sırayla alalım
                            writer.writerow([
                                satir.get("KOD"), 
                                satir.get("kayit_tarihi"), 
                                satir.get("alis"), 
                                satir.get("satis")
                            ])
                    print(f"-> Veriler '{csv_dosya_adi}' dosyasına da eklendi.")
                    
                else:
                    print("SUNUCU YANIT VERDİ AMA İÇİNDE VERİ YOK.")
                    # Debug için ham veriyi yazdıralım
                    print(json.dumps(ham_veri, indent=2)[:500]) 

            except json.JSONDecodeError:
                print("JSON HATASI. Gelen veri bozuk olabilir.")
        else:
            print(f"HTTP HATA: {response.status_code}")

    except Exception as e:
        print(f"Kritik Hata: {e}")

if __name__ == "__main__":
    veri_cek()
