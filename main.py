import requests
import re
from concurrent.futures import ThreadPoolExecutor

# Taranacak olan büyük listenin raw adresi
RAW_GITHUB_URL = "https://raw.githubusercontent.com/Sword-Saint69/fifa/989a0fdbfce75e017a04a804df5ab2e62ca071cf/1.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def linkleri_topla():
    print("🔄 Kaynak GitHub listesi indiriliyor...")
    try:
        response = requests.get(RAW_GITHUB_URL, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            linkler = re.findall(r'(http://[^\s"\']+get\.php\?[^\s"\']+)', response.text)
            linkler = list(set(linkler))
            print(f"✅ Toplam {len(linkler)} benzersiz ana URL toplandı. Kanal ayıklama başlıyor...\n")
            return linkler
        return []
    except Exception as e:
        print(f"❌ Liste çekilemedi: {e}")
        return []

def kanallari_ayıkla(url):
    """
    Çalışan playlist linkinin içine girer ve sadece Türkçe olan kanalları satır satır söker.
    """
    # İçeriği tam okumak için formatı m3u_plus olarak bırakıyoruz veya m3u yapıyoruz
    test_url = url.replace("type=m3u", "type=m3u_plus")
    bulunan_kanallar = []
    
    try:
        # Sunuculardan veriyi çekiyoruz (Tam listeyi okumak için stream=False yapıyoruz)
        response = requests.get(test_url, headers=HEADERS, timeout=8)
        if response.status_code == 200 and "#EXTM3U" in response.text:
            satirlar = response.text.splitlines()
            
            # Satırları dönerek Türkçe olanları tespit ediyoruz
            for i in range(len(satirlar)):
                satir = satirlar[i]
                # Eğer satır bir kanal bilgisi (#EXTINF) ise ve Türkçe etiketleri içeriyorsa
                if satir.startswith("#EXTINF"):
                    # Türkçe kanalları yakalayacak filtreler
                    tr_kelimeler = ["TR:", "TURK", "TÜRK", "TR -", "TR|", "TURKISH"]
                    if any(kelime in satir.upper() for kelime in tr_kelimeler):
                        # Bir sonraki satır o kanalın gerçek yayın linkidir (.ts veya .m3u8)
                        if i + 1 < len(satirlar) and satirlar[i+1].startswith("http"):
                            bulunan_kanallar.append(satir)         # #EXTINF satırını ekle
                            bulunan_kanallar.append(satirlar[i+1])  # Hemen altındaki yayın linkini ekle
            
            if bulunan_kanallar:
                print(f"💚 BAŞARILI: {url} içerisinden {len(bulunan_kanallar) // 2} adet Türkçe kanal çekildi.")
                return bulunan_kanallar
    except Exception:
        pass
    return None

def ana_calistirici():
    link_listesi = linkleri_topla()
    if not link_listesi:
        print("❌ Taranacak link bulunamadı.")
        return

    tum_havuz_kanallari = []
    
    # 20 koldan hızlıca havuzdaki tüm m3u'ların içine dalıyoruz
    with ThreadPoolExecutor(max_workers=20) as executor:
        sonuclar = executor.map(kanallari_ayıkla, link_listesi)
        for sonuc in sonuclar:
            if sonuc:
                tum_havuz_kanallari.extend(sonuc)

    print(f"\n✍️ Toplam {len(tum_havuz_kanallari) // 2} adet benzersiz canlı TR kanal dosyaya yazılıyor...")
    
    # Kanalları birleştirip Notepad++ ekranındaki gibi gerçek bir M3U dosyası üretiyoruz
    with open("otomatik_liste.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for satir in tum_havuz_kanallari:
            f.write(f"{satir}\n")
            
    print("🎉 Oynatılmaya hazır gerçek otomatik_liste.m3u başarıyla güncellendi!")

if __name__ == "__main__":
    ana_calistirici()
