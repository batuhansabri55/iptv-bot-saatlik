import requests

def guncelle():
    url = "https://m3uliste.gt.tc/?i=3"
    
    # Siteye gerçek bir tarayıcı gibi görünüyoruz
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://google.com'
    }
    
    try:
        print("Bağlantı kuruluyor...")
        # Session kullanarak çerez desteği ekliyoruz
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=30)
        
        # Eğer gelen veri m3u formatında değilse hata bas
        if "#EXTM3U" not in response.text:
            print("Uyarı: M3U formatı alınamadı, koruma hala aktif olabilir.")
        
        with open("otomatik_liste.m3u", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("Dosya başarıyla tazelendi.")
        
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    guncelle()
