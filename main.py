import requests
import json

def guncelle():
    # Hedef m3u linkin
    hedef_url = "https://m3uliste.gt.tc/?i=3"
    
    # AllOrigins servisi aracılığıyla sitenin bot korumasını atlıyoruz
    proxy_servis_url = f"https://api.allorigins.win/get?url={requests.utils.quote(hedef_url)}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    
    try:
        print("Güvenlik duvarı aşılıyor (Proxy kullanılıyor)...")
        response = requests.get(proxy_servis_url, headers=headers, timeout=30)
        
        # Gelen veriyi JSON olarak çözümle
        data = response.json()
        raw_content = data['contents']
        
        # Eğer içerik m3u formatındaysa kaydet
        if "#EXTM3U" in raw_content:
            with open("otomatik_liste.m3u", "w", encoding="utf-8") as f:
                f.write(raw_content)
            print("BAŞARILI: Gerçek m3u linkleri yakalandı ve kaydedildi!")
        else:
            print("HATA: Liste içeriği hala beklenen formatta değil.")
            # İncelemek için gelen veriyi yine de yazalım
            with open("otomatik_liste.m3u", "w", encoding="utf-8") as f:
                f.write(raw_content)
                
    except Exception as e:
        print(f"Bağlantı sırasında bir sorun oluştu: {e}")

if __name__ == "__main__":
    guncelle()
