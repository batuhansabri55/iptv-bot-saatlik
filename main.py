import requests

def guncelle():
    url = "https://m3uliste.gt.tc/?i=3"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=30)
        with open("otomatik_liste.m3u", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("Liste güncellendi!")
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    guncelle()
