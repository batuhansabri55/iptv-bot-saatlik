import requests
import re
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

# Büyük havuz listesi (1.txt)
RAW_GITHUB_URL = "https://raw.githubusercontent.com/Sword-Saint69/fifa/989a0fdbfce75e017a04a804df5ab2e62ca071cf/1.txt"

HEADERS = {
    "User-Agent": "IPTVIngest/1.0.0"
}

def havuzu_indir():
    print("📥 Büyük havuz listesi indiriliyor...")
    try:
        response = requests.get(RAW_GITHUB_URL, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            linkler = re.findall(r'(http://[^\s"\']+get\.php\?[^\s"\']+)', response.text)
            temiz_linkler = list(dict.fromkeys(linkler))
            print(f"📋 Havuzdan toplam {len(temiz_linkler)} adet panel linki söküldü.")
            return temiz_linkler
        return []
    except Exception as e:
        print(f"❌ Havuz indirilirken hata: {e}")
        return []

def yayin_canli_mi(test_url):
    try:
        with requests.get(test_url, headers=HEADERS, timeout=3, stream=True) as r:
            if r.status_code == 200:
                for chunk in r.iter_content(chunk_size=512):
                    if chunk: 
                        return True
    except Exception:
        pass
    return False

def paneli_ve_turkce_kanallari_test_et(url):
    test_url = url.replace("type=m3u_plus", "type=m3u").replace("type=m3u", "type=m3u_plus")
    tr_isaretleri = ["TR:", "TR|", "TR -", "TURKISH", "TÜRKÇE", "TURKCE", 'GROUP-TITLE="TR', "TÜRK"]
    
    try:
        response = requests.get(test_url, headers=HEADERS, timeout=7)
        if response.status_code == 200 and "#EXTM3U" in response.text:
            satirlar = response.text.splitlines()
            sadece_tr_linkleri = []
            
            for i in range(len(satirlar)):
                satir = satirlar[i]
                if satir.startswith("#EXTINF"):
                    satir_ust = satir.upper()
                    if any(isaret in satir_ust for isaret in tr_isaretleri):
                        if i + 1 < len(satirlar) and satirlar[i+1].startswith("http"):
                            sadece_tr_linkleri.append(satirlar[i+1])
            
            # En az 50 Türkçe kanal barındıran aktif paneli bul
            if len(sadece_tr_linkleri) >= 50:
                test_edilecekler = random.sample(sadece_tr_linkleri, min(3, len(sadece_tr_linkleri)))
                calisan_yayin_sayisi = sum(1 for link in test_edilecekler if yayin_canli_mi(link))
                
                if calisan_yayin_sayisi >= 2:
                    print(f"🟢 CANLI PANEL BULUNDU: {test_url}")
                    return test_url
    except Exception:
        pass
    return None

def en_iyi_paneli_tara_ve_sec(link_listesi):
    print("⚡ Çalışan ve canlı akışı olan Türkçe panel aranıyor...")
    with ThreadPoolExecutor(max_workers=40) as executor:
        gorevler = {executor.submit(paneli_ve_turkce_kanallari_test_et, url): url for url in link_listesi}
        for gosterge in as_completed(gorevler):
            sonuc = gosterge.result()
            if sonuc:
                return sonuc
    return None

def ana_calistirici():
    link_listesi = havuzu_indir()
    if not link_listesi:
        print("❌ Havuz boş olduğu için işlem iptal edildi.")
        return

    canli_panel_url = en_iyi_paneli_tara_ve_sec(link_listesi)
    
    if canli_panel_url:
        try:
            # Bulunan canlı paneli geçici bir metin dosyasına yazıyoruz
            with open("canli_panel.txt", "w", encoding="utf-8") as f:
                f.write(canli_panel_url)
            print(f"🎉 Başarılı! Canlı URL geçici hafızaya alındı: {canli_panel_url}")
        except Exception as e:
            print(f"❌ Dosya yazılırken hata oldu: {e}")
    else:
        print("❌ Havuzda aktif ve canlı Türkçe kanal barındıran bir panel bulunamadı.")

if __name__ == "__main__":
    ana_calistirici()
