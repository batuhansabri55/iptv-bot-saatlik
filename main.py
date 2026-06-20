import requests
import re
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

def tek_link_test_et(url):
    """
    Panel linkinin içine girer. Ulusal, sinema, belgesel, çocuk dahil 
    tüm Türkçe kanalları ve kategorileri satır satır eksiksiz söker.
    """
    test_url = url.replace("type=m3u_plus", "type=m3u").replace("type=m3u", "type=m3u_plus")
    
    # Türkçe kanalları yakalayacak geniş ve kapsayıcı filtre havuzu
    tr_isaretleri = [
        "TR:", "TR|", "TR -", "TURKISH", "TÜRKÇE", "TURKCE", 
        'GROUP-TITLE="TR', 'GROUP-TITLE="TÜRK', 'GROUP-TITLE="TURK',
        'GROUP-TITLE="★ TÜRKİYE', 'GROUP-TITLE="TR |'
    ]
    
    try:
        # Bağlantı kalitesini ölçmek için zaman aşımını 7 saniye yapıyoruz
        response = requests.get(test_url, headers=HEADERS, timeout=7)
        if response.status_code == 200 and "#EXTM3U" in response.text:
            satirlar = response.text.splitlines()
            bulunan_kanallar = []
            
            for i in range(len(satirlar)):
                satir = satirlar[i]
                if satir.startswith("#EXTINF"):
                    satir_ust = satir.upper()
                    # Satırda veya grup adında Türkçe ibaresi var mı?
                    if any(isaret in satir_ust for isaret in tr_isaretleri):
                        if i + 1 < len(satirlar) and satirlar[i+1].startswith("http"):
                            bulunan_kanallar.append(satir)
                            bulunan_kanallar.append(satirlar[i+1])
            
            # GÜVENLİK FİLTRESİ: Eğer panelde en az 200 tane Türkçe kanal yoksa, 
            # o panel ya eksiktir ya patlaktır ya da sahtedir. Onu eliyoruz!
            if len(bulunan_kanallar) >= 400: # 400 satır = 200 kanal yapar
                return bulunan_kanallar, url
    except Exception:
        pass
    return None

def en_zengin_turkce_paneli_sec(link_listesi):
    print("⚡ Tüm kategorileri içeren (Ulusal, Sinema, Belgesel...) dolgun Türkçe panel aranıyor...")
    
    # 35 koldan hızlıca havuzun içine dalıyoruz
    with ThreadPoolExecutor(max_workers=35) as executor:
        gorevler = {executor.submit(tek_link_test_et, url): url for url in link_listesi}
        
        for gosterge in as_completed(gorevler):
            sonuc = gosterge.result()
            if sonuc:
                kanal_listesi, panel_url = sonuc
                print(f"\n💚 HARİKA VE DOLU PANEL BULUNDU: {panel_url}")
                print(f"📦 Tüm kategorilerden toplam {len(kanal_listesi) // 2} adet canlı Türkçe kanal sök
