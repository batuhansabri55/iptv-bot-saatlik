import requests
import re
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

RAW_GITHUB_URL = "https://raw.githubusercontent.com/Sword-Saint69/fifa/989a0fdbfce75e017a04a804df5ab2e62ca071cf/1.txt"

# Panelleri kandırmak için en yaygın oynatıcı kimliğini kullanıyoruz
HEADERS = {
    "User-Agent": "IPTVIngest/1.0.0"
}

def havuzu_indir():
    try:
        response = requests.get(RAW_GITHUB_URL, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            linkler = re.findall(r'(http://[^\s"\']+get\.php\?[^\s"\']+)', response.text)
            return list(dict.fromkeys(linkler))
        return []
    except Exception:
        return []

def yayin_calisiyor_mu(test_url):
    try:
        with requests.get(test_url, headers=HEADERS, timeout=3, stream=True) as r:
            if r.status_code == 200:
                for chunk in r.iter_content(chunk_size=512):
                    if chunk: return True
    except Exception:
        pass
    return False

def tek_link_test_et(url):
    # Link formatını en kararlı olan m3u_plus'a çekip içeriği okuyoruz
    test_url = url.replace("type=m3u_plus", "type=m3u").replace("type=m3u", "type=m3u_plus")
    
    tr_isaretleri = ["TR:", "TR|", "TR -", "TURKISH", "TÜRKÇE", "TURKCE", 'GROUP-TITLE="TR']
    
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
                            # 🛑 TİVİMATE İÇİN LİNKİ .ts FORMATINA ÇEVİRİYORUZ (Garantili Oynatma)
                            temiz_link = satirlar[i+1].replace("type=m3u_plus", "output=ts").replace("type=m3u", "output=ts")
                            if "output=ts" not in temiz_link:
                                temiz_link += "&output=ts"
                                
                            bulunan_kanallar.append(satir)
                            bulunan_kanallar.append(temiz_link)
                            sadece_linkler.append(temiz_link)
            
            if len(bulunan_kanallar) >= 160: # En az 80 canlı kanal
                test_edilecekler = random.sample(sadece_linkler, min(3, len(sadece_linkler)))
                calisan_sayisi = sum(1 for link in test_edilecekler if yayin_calisiyor_mu(link))
                
                if calisan_sayisi >= 2:
                    return bulunan_kanallar, url
    except Exception:
        pass
    return None

def en_zengin_ve_calisan_paneli_sec(link_listesi):
    print("⚡ TiviMate uyumlu, canlı akışı olan panel aranıyor...")
    with ThreadPoolExecutor(max_workers=40) as executor:
        gorevler = {executor.submit(tek_link_test_et, url): url for url in link_listesi}
        for gosterge in as_completed(gorevler):
            sonuc = gosterge.result()
            if sonuc:
                return sonuc[0]
    return None

def ana_calistirici():
    link_listesi = havuzu_indir()
    if not link_listesi: return

    canli_tr_havuzu = en_zengin_ve_calisan_paneli_sec(link_listesi)
    
    if canli_tr_havuzu:
        with open("otomatik_liste.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for satir in canli_tr_havuzu:
                f.write(f"{satir}\n")
        print("🎉 İşlem başarılı! Çıktılar .ts formatına dönüştürüldü.")
    else:
        print("❌ Uygun panel bulunamadı.")

if __name__ == "__main__":
    ana_calistirici()
