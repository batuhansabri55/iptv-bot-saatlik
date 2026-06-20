import requests
import re

# Taranacak olan büyük havuzun raw adresi
RAW_GITHUB_URL = "https://raw.githubusercontent.com/Sword-Saint69/fifa/989a0fdbfce75e017a04a804df5ab2e62ca071cf/1.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def havuzu_indir():
    print("🔄 Kaynak havuz listesi indiriliyor...")
    try:
        response = requests.get(RAW_GITHUB_URL, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            linkler = re.findall(r'(http://[^\s"\']+get\.php\?[^\s"\']+)', response.text)
            # Benzersiz linkleri sıralı koruyarak ayıkla
            linkler = list(dict.fromkeys(linkler))
            print(f"✅ Havuzdan {len(linkler)} adet panel adresi toplandı. Test başlıyor...")
            return linkler
        return []
    except Exception as e:
        print(f"❌ Havuz indirilemedi: {e}")
        return []

def en_iyi_paneli_bul_ve_cek(link_listesi):
    """
    Listeyi sırayla tarar, İÇİNDE TÜRKÇE KANAL OLAN VE ÇALIŞAN İLK SAĞLAM PANELİ bulduğu an
    tüm içeriğini indirir ve aramayı durdurur. Havuzun şişmesini engeller.
    """
    tr_kelimeler = ["TR:", "TURK", "TÜRK", "TR -", "TR|", "TURKISH"]
    
    for sira, url in enumerate(link_listesi, 1):
        # İstek hızını artırmak ve temiz veri almak için m3u_plus formatına zorluyoruz
        test_url = url.replace("type=m3u", "type=m3u_plus")
        print(f"[{sira}/{len(link_listesi)}] Deneniyor: {test_url}")
        
        try:
            # Panelin aktif olup olmadığını ve içeriğini kontrol etmek için bağlanıyoruz
            response = requests.get(test_url, headers=HEADERS, timeout=7)
            if response.status_code == 200 and "#EXTM3U" in response.text:
                # Panel çalışıyor, şimdi içinde gerçekten Türkçe kanal var mı kontrol edelim
                icerik_buyuk = response.text.upper()
                if any(kelime in icerik_buyuk for kelime in tr_kelimeler):
                    print(f"\n💚 HARİKA PANEL BULUNDU! Türkçe kanallar içeriyor: {url}")
                    return response.text  # Panel içeriğini olduğu gibi döndür
        except Exception:
            continue
            
    return None

def ana_calistirici():
    link_listesi = havuzu_indir()
    if not link_listesi:
        print("❌ Taranacak panel adresi bulunamadı.")
        return

    # Sadece çalışan ve Türkçe olan TEK bir panelin tam listesini söküyoruz
    m3u_icerigi = en_iyi_paneli_bul_ve_cek(link_listesi)
    
    if m3u_icerigi:
        print("\n✍️ Seçilen panelin tüm m3u listesi depoya yazılıyor...")
        with open("otomatik_liste.m3u", "w", encoding="utf-8") as f:
            f.write(m3u_icerigi)
        print("🎉 otomatik_liste.m3u tertemiz şekilde güncellendi!")
    else:
        print("❌ Havuzda hem aktif olan hem de içinde Türkçe kanal barındıran bir panel bulunamadı.")

if __name__ == "__main__":
    ana_calistirici()
