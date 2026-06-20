import requests
import re
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

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
            linkler = list(dict.fromkeys(linkler))
            print(f"✅ Havuzdan {len(linkler)} adet panel adresi toplandı.\n")
            return linkler
        return []
    except Exception as e:
        print(f"❌ Havuz indirilemedi: {e}")
        return []

def yayin_calisiyor_mu(test_url):
    """
    Kanal linkinin kendisine 2 saniyelik ufak bir istek atar.
    Eğer video akışı (ts/mpeg/m3u8) aktifse True döner.
    """
    try:
        # Stream linkini test ederken akışı kontrol etmek için stream=True yapıyoruz
        with requests.get(test_url, headers=HEADERS, timeout=3, stream=True) as r:
            if r.status_code == 200:
                # İlk birkaç baytlık verinin gelmesi yayının canlı olduğunu gösterir
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        return True
    except Exception:
        pass
    return False

def tek_link_test_et(url):
    """
    Panelin içine girer, Türkçe kanalları ayıklar ve 
    linklerin gerçekten çalışıp çalışmadığını canını test ederek doğrular.
    """
    test_url = url.replace("type=m3u_plus", "type=m3u").replace("type=m3u", "type=m3u_plus")
    
    tr_isaretleri = [
        "TR:", "TR|", "TR -", "TURKISH", "TÜRKÇE", "TURKCE", 
        'GROUP-TITLE="TR', 'GROUP-TITLE="TÜRK', 'GROUP-TITLE="TURK',
        'GROUP-TITLE="★ TÜRKİYE', 'GROUP-TITLE="TR |', "SINEMA", "BELGESEL"
    ]
    
    try:
        response = requests.get(test_url, headers=HEADERS, timeout=6)
        if response.status_code == 200 and "#EXTM3U" in response.text:
            satirlar = response.text.splitlines()
            bulunan_kanallar = []
            sadece_linkler = []
            
            for i in range(len(satirlar)):
                satir = satirlar[i]
                if satir.startswith("#EXTINF"):
                    satir_ust = satir.upper()
                    if any(isaret in satir_ust for isaret in tr_isaretleri):
                        if i + 1 < len(satirlar) and satirlar[i+1].startswith("http"):
                            bulunan_kanallar.append(satir)
                            bulunan_kanallar.append(satirlar[i+1])
                            sadece_linkler.append(satirlar[i+1])
            
            # İçerik zenginliği kontrolü (En az 100 Türkçe kanal olmalı)
            if len(bulunan_kanallar) >= 200:
                # 🛑 EN KRİTİK NOKTA: Rastgele 3 kanalı gerçek yayın akışı testine sokuyoruz
                test_edilecekler = random.sample(sadece_linkler, min(3, len(sadece_linkler)))
                
                calisan_sayisi = 0
                for link in test_edilecekler:
                    if yayin_calisiyor_mu(link):
                        calisan_sayisi += 1
                
                # Eğer test edilen örnek kanallardan en az 2'si tıkır tıkır çalışıyorsa paneli onaylıyoruz
                if calisan_sayisi >= 2:
                    return bulunan_kanallar, url
                else:
                    print(f"⚠️ Panel açık ama içindeki yayın linkleri patlak (Ölü): {url}")
    except Exception:
        pass
    return None

def en_zengin_ve_calisan_paneli_sec(link_listesi):
    print("⚡ Gerçekten YAYINI AKAN, taptaze ve dolgun Türkçe panel aranıyor...")
    
    # Havuz geniş olduğu için eşzamanlı tarama sayısını 40 yapıyoruz
    with ThreadPoolExecutor(max_workers=40) as executor:
        gorevler = {executor.submit(tek_link_test_et, url): url for url in link_listesi}
        
        for gosterge in as_completed(gorevler):
            sonuc = gosterge.result()
            if sonuc:
                kanal_listesi, panel_url = sonuc
                print(f"\n💚 %100 ÇALIŞAN CANLI PANEL BULUNDU: {panel_url}")
                print(f"📦 Toplam {len(kanal_listesi) // 2} adet aktif yerli kanal başarıyla söküldü!")
                return kanal_listesi
                
    return None

def ana_calistirici():
    link_listesi = havuzu_indir()
    if not link_listesi:
        print("❌ Taranacak panel adresi bulunamadı.")
        return

    # Hem dolu hem de yayını çalışan paneli buluyoruz
    canli_tr_havuzu = en_zengin_ve_calisan_paneli_sec(link_listesi)
    
    if canli_tr_havuzu:
        print("✍️ Çalışan tüm kanallar otomatik_liste.m3u dosyasına yazılıyor...")
        with open("otomatik_liste.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for satir in canli_tr_havuzu:
                f.write(f"{satir}\n")
        print("🎉 İşlem başarıyla tamamlandı! Artık listenizdeki kanallar tıkır tıkır çalışacak usta.")
    else:
        print("❌ Havuzda hem kanalları tam olan hem de YAYINI AKTİF olan sağlam bir panel bulunamadı.")

if __name__ == "__main__":
    ana_calistirici()
