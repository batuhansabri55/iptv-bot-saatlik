import requests
import re
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

# Taramasını istediğin devasa m3u havuz linki
RAW_GITHUB_URL = "https://raw.githubusercontent.com/Sword-Saint69/fifa/989a0fdbfce75e017a04a804df5ab2e62ca071cf/1.txt"

# Panellerin güvenlik duvarını aşmak için profesyonel oynatıcı kimliği
HEADERS = {
    "User-Agent": "IPTVIngest/1.0.0"
}

def havuzu_indir():
    """GitHub üzerindeki txt dosyasından tüm Xtream linklerini ayıklar"""
    print("📥 Büyük havuz listesi indiriliyor...")
    try:
        response = requests.get(RAW_GITHUB_URL, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            # get.php ile biten tüm panel linklerini yakalar
            linkler = re.findall(r'(http://[^\s"\']+get\.php\?[^\s"\']+)', response.text)
            temiz_linkler = list(dict.fromkeys(linkler))
            print(f"📋 Havuzdan toplam {len(temiz_linkler)} adet benzersiz panel linki söküldü.")
            return temiz_linkler
        return []
    except Exception as e:
        print(f"❌ Havuz indirilirken hata oluştu: {e}")
        return []

def yayin_canli_mi(test_url):
    """Bulunan kanal linkine anlık istek atarak gerçekten video akışı veriyor mu diye bakar"""
    try:
        with requests.get(test_url, headers=HEADERS, timeout=3, stream=True) as r:
            if r.status_code == 200:
                # İlk 512 baytlık video verisi tıkır tıkır geliyor mu kontrolü
                for chunk in r.iter_content(chunk_size=512):
                    if chunk: 
                        return True
    except Exception:
        pass
    return False

def paneli_ve_turkce_kanalları_test_et(url):
    """Paneli açar, içindeki TR kanalları bulur ve yayının çalışıp çalışmadığını test eder"""
    # TiviMate'in en sevdiği format olan m3u_plus formatına zorluyoruz
    test_url = url.replace("type=m3u_plus", "type=m3u").replace("type=m3u", "type=m3u_plus")
    
    # Türkçe kanalları yakalayacak filtre anahtarları
    tr_isaretleri = ["TR:", "TR|", "TR -", "TURKISH", "TÜRKÇE", "TURKCE", 'GROUP-TITLE="TR', "TÜRK"]
    
    try:
        # Panele bağlanıp içindeki tüm kanal listesini çekmeyi deniyoruz
        response = requests.get(test_url, headers=HEADERS, timeout=7)
        if response.status_code == 200 and "#EXTM3U" in response.text:
            satirlar = response.text.splitlines()
            bulunan_tr_kanallari = []
            sadece_tr_linkleri = []
            
            # M3U listesindeki satırları tek tek tarıyoruz
            for i in range(len(satirlar)):
                satir = satirlar[i]
                if satir.startswith("#EXTINF"):
                    satir_ust = satir.upper()
                    # Eğer kanal Türkçe etiketine sahipse
                    if any(isaret in satir_ust for isaret in tr_isaretleri):
                        if i + 1 < len(satirlar) and satirlar[i+1].startswith("http"):
                            kanal_linki = satirlar[i+1]
                            bulunan_tr_kanallari.append((satir, kanal_linki))
                            sadece_tr_linkleri.append(kanal_linki)
            
            # Eğer panelde en az 50 adet Türkçe kanal bulunduysa canlılık testine geç
            if len(sadece_tr_linkleri) >= 50:
                # Rastgele 3 adet Türkçe kanal seçip gerçekten oynatıyor mu diye bakıyoruz
                test_edilecekler = random.sample(sadece_tr_linkleri, min(3, len(sadece_tr_linkleri)))
                calisan_yayin_sayisi = sum(1 for link in test_edilecekler if yayin_canli_mi(link))
                
                # Eğer test edilen kanallardan en az 2 tanesi yağ gibi video akışı verdiyse, bu panel sağlamdır!
                if calisan_yayin_sayisi >= 2:
                    print(f"🟢 ÇALIŞIYOR: {url} (İçinde {len(sadece_tr_linkleri)} Türkçe kanal var ve yayınlar aktif!)")
                    return bulunan_tr_kanallari
    except Exception:
        pass
    return None

def en_iyi_paneli_tara_ve_sec(link_listesi):
    """Hızlıca çalışması için 40 kanaldan aynı anda paralel tarama yapar"""
    print("⚡ Çalışan ve canlı akışı olan Türkçe panel aranıyor, lütfen bekleyin...")
    
    with ThreadPoolExecutor(max_workers=40) as executor:
        gorevler = {executor.submit(paneli_and_turkce_kanalları_test_et, url): url for url in link_listesi}
        for gosterge in as_completed(gorevler):
            sonuc = gosterge.result()
            if sonuc:
                # Çalışan ilk kaliteli paneli bulduğu an taramayı durdurur ve onu seçer
                return sonuc
    return None

def ana_calistirici():
    link_listesi = havuzu_indir()
    if not link_listesi:
        print("❌ Havuzdan link alınamadığı için işlem iptal edildi.")
        return

    # Sadece çalışan ve Türkçe kanalları olan paneli söküyoruz
    ayiklanmis_tr_listesi = en_iyi_paneli_tara_ve_sec(link_listesi)
    
    if ayiklanmis_tr_listesi:
        try:
            with open("otomatik_liste.m3u", "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")
                # Sadece ayıklanan Türkçe kanalların isimlerini ve linklerini yazıyoruz
                for inf_satiri, link_satiri in ayiklanmis_tr_listesi:
                    f.write(f"{inf_satiri}\n")
                    f.write(f"{link_satiri}\n")
            print(f"🎉 İşlem Başarılı! Toplam {len(ayiklanmis_tr_listesi)} adet CANLI Türkçe kanal 'otomatik_liste.m3u' dosyasına yazıldı.")
        except Exception as e:
            print(f"❌ Dosya yazılırken hata oldu: {e}")
    else:
        print("❌ Maalesef havuzda hem aktif olan hem de yeterli Türkçe kanal barındıran bir panel bulunamadı.")

if __name__ == "__main__":
    ana_calistirici()
