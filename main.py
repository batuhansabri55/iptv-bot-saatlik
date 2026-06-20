import requests
import re
from concurrent.futures import ThreadPoolExecutor

# Taranacak olan büyük listenin raw adresi
RAW_GITHUB_URL = "https://raw.githubusercontent.com/Sword-Saint69/fifa/989a0fdbfce75e017a04a804df5ab2e62ca071cf/1.txt"

# IPTV panellerinin bot korumasını aşmak için tarayıcı taklidi yapıyoruz
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
            print(f"✅ Toplam {len(linkler)} benzersiz link toplandı. Kontrol başlıyor...\n")
            return linkler
        return []
    except Exception as e:
        print(f"❌ Liste çekilemedi: {e}")
        return []

def linki_kontrol_et(url):
    # Hızlı yanıt almak için m3u formatında test ediyoruz
    test_url = url.replace("type=m3u_plus", "type=m3u")
    try:
        # Stream=True yaparak listenin tamamını indirmeden parça parça okuyoruz
        response = requests.get(test_url, headers=HEADERS, timeout=6, stream=True)
        if response.status_code == 200:
            # İlk 2-3 parçayı birleştirerek dil kontrolünü garantiye alıyoruz (Yaklaşık 150KB)
            icerik_parcasi = response.iter_content(chunk_size=50000)
            bloklar = []
            for _ in range(3):
                try:
                    bloklar.append(next(icerik_parcasi, b"").decode('utf-8', errors='ignore').upper())
                except StopIteration:
                    break
            
            tam_blok = "".join(bloklar)
            
            # Türkçe kanalları yakalayacak anahtar kelimeler
            tr_kelimeler = ["TR:", "TURK", "TÜRK", "TR -", "TR|", "TURKISH"]
            if any(kelime in tam_blok for kelime in tr_kelimeler):
                print(f"💚 ÇALIŞIYOR VE TÜRKÇE: {url}")
                return url
    except Exception:
        pass
    return None

def ana_calistirici():
    link_listesi = linkleri_topla()
    if not link_listesi:
        print("❌ Taranacak link bulunamadı.")
        return

    calisan_tr_linkler = []
    
    # Aynı anda 20 istek atarak panelleri bloke etmeden hızlıca taratıyoruz
    with ThreadPoolExecutor(max_workers=20) as executor:
        sonuclar = executor.map(linki_kontrol_et, link_listesi)
        for sonuc in sonuclar:
            if sonuc:
                calisan_tr_linkler.append(sonuc)

    # Elde edilen çalışan linkleri otomatik_liste.m3u formatına uygun yazıyoruz
    print(f"\n✍️ {len(calisan_tr_linkler)} adet çalışan TR linki dosyaya yazılıyor...")
    
    with open("otomatik_liste.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n") # M3U dosyasının standart başlığı
        for sira, link in enumerate(calisan_tr_linkler, 1):
            # TiviMate veya OTT Navigator'da temiz görünmesi için başlık ekliyoruz
            f.write(f'#EXTINF:-1,--- ÇALIŞAN TR LİSTE {sira} ---\n')
            f.write(f'{link}\n')
            
    print("🎉 otomatik_liste.m3u başarıyla güncellendi!")

if __name__ == "__main__":
    ana_calistirici()
