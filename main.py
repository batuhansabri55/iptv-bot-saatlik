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
    Panel linkini test eder. İçinde gerçekten TÜRKÇE KATEGORİSİ veya 
    net Türkçe kanal etiketi var mı diye bakar. Varsa sadece o Türkçe kanalları ayıklar.
    """
    test_url = url.replace("type=m3u_plus", "type=m3u").replace("type=m3u", "type=m3u_plus")
    
    # Gerçek Türkçe kanalları ayırt etmek için çok sıkı filtreler
    tr_kategori_filtreleri = [
        'GROUP-TITLE="TR', 'GROUP-TITLE="TÜRK', 'GROUP-TITLE="TURK',
        'TR:', 'TR|', 'TR -', 'TURKISH'
    ]
    
    try:
        response = requests.get(test_url, headers=HEADERS, timeout=6)
        if response.status_code == 200 and "#EXTM3U" in response.text:
            satirlar = response.text.splitlines()
            gecerli_tr_kanallari = []
            
            for i in range(len(satirlar)):
                satir = satirlar[i]
                if satir.startswith("#EXTINF"):
                    satir_ust = satir.upper()
                    # Satırda sıkı Türkçe filtrelerimizden biri var mı?
                    if any(filtre in satir_ust for filtre in tr_kategori_filtreleri):
                        # Altındaki satırın geçerli bir url olduğunu kontrol et
                        if i + 1 < len(satirlar) and satirlar[i+1].startswith("http"):
                            gecerli_tr_kanallari.append(satir)
                            gecerli_tr_kanallari.append(satirlar[i+1])
            
            # Eğer bu panelden gerçekten ayıklanmış en az 10 tane net Türkçe kanal bulabildiysek onay veriyoruz
            if len(gecerli_tr_kanallari) >= 20: 
                return gecerli_tr_kanallari, url
    except Exception:
        pass
    return None

def en_iyi_turkce_listeyi_sec(link_listesi):
    print("⚡ Sıkı filtreli Türkçe kanal taraması başlatıldı...")
    
    # 35 kanaldan hızlıca sunucuları tarıyoruz
    with ThreadPoolExecutor(max_workers=35) as executor:
        gorevler = {executor.submit(tek_link_test_et, url): url for url in link_listesi}
        
        for gosterge in as_completed(gorevler):
            sonuc = gosterge.result()
            if sonuc:
                kanal_listesi, panel_url = sonuc
                print(f"\n💚 %100 TÜRKÇE İÇERİKLİ SAĞLAM PANEL BULUNDU: {panel_url}")
                print(f"📦 Bu panelden {len(kanal_listesi) // 2} adet saf Türkçe kanal başarıyla söküldü!")
                return kanal_listesi
                
    return None

def ana_calistirici():
    link_listesi = havuzu_indir()
    if not link_listesi:
        print("❌ Taranacak panel adresi bulunamadı.")
        return

    # Sadece ve sadece Türkçe kanallardan oluşan temiz listeyi alıyoruz
    temiz_tr_kanallari = en_iyi_turkce_listeyi_sec(link_listesi)
    
    if temiz_tr_kanallari:
        print("✍️ Saf Türkçe kanallar otomatik_liste.m3u dosyasına yazılıyor...")
        with open("otomatik_liste.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for satir in temiz_tr_kanallari:
                f.write(f"{satir}\n")
        print("🎉 İşlem başarılı! Yabancı kanallardan arındırılmış liste hazır usta.")
    else:
        print("❌ Havuzda kriterlere uyan aktif bir Türkçe playlist bulunamadı.")

if __name__ == "__main__":
    ana_calistirici()
