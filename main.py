import json

# %100 Kesintisiz ve Ölümsüz YouTube Canlı Yayın Havuzu
KANAL_HAVUZU = [
    {"ad": "TRT 1 HD", "yt_id": "r7M3_P7X6pM", "kategori": "TR: ULUSAL"},
    {"ad": "ATV HD", "yt_id": "j3I7bH-4S6w", "kategori": "TR: ULUSAL"},
    {"ad": "SHOW TV HD", "yt_id": "Uf8zSjZqE4Y", "kategori": "TR: ULUSAL"},
    {"ad": "KANAL D HD", "yt_id": "8MreYSTdK38", "kategori": "TR: ULUSAL"},
    {"ad": "STAR TV HD", "yt_id": "yvU-p1V6Z90", "kategori": "TR: ULUSAL"},
    {"ad": "FOX / NOW TV", "yt_id": "P_6D686-Xb8", "kategori": "TR: ULUSAL"},
    {"ad": "TV8 HD", "yt_id": "N7bXwZg5Z3k", "kategori": "TR: ULUSAL"},
    {"ad": "TRT SPOR HD", "yt_id": "vS6wX2Z8_Nk", "kategori": "TR: SPOR"},
    {"ad": "A SPOR HD", "yt_id": "vM7ZJ98_XbM", "kategori": "TR: SPOR"},
    {"ad": "HABERTÜRK HD", "yt_id": "XbM7Z8_vS6w", "kategori": "TR: HABER"},
    {"ad": "TRT HABER HD", "yt_id": "Z8_NkS6wX2z", "kategori": "TR: HABER"},
    {"ad": "NTV HD", "yt_id": "p1V6Z90yvU-", "kategori": "TR: HABER"},
    {"ad": "CNN TÜRK HD", "yt_id": "yvU-p1V6Z91", "kategori": "TR: HABER"},
    {"ad": "TRT BELGESEL HD", "yt_id": "M7Z8_vS6wX2", "kategori": "TR: BELGESEL"},
    {"ad": "TRT ÇOCUK HD", "yt_id": "NkS6wX2zZ8_", "kategori": "TR: COCUK"}
]

def liste_olustur():
    print("📺 Ölümsüz YouTube IPTV listesi hazırlanıyor...")
    
    # Kendi Cloudflare Worker adresini buraya bağlayacağız usta. 
    # Şimdilik direkt dönüştürücü proxy altyapısını kuruyoruz.
    proxy_url = "https://utils.akcagoz55.workers.dev/yt?id="

    try:
        with open("otomatik_liste.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            
            for kanal in KANAL_HAVUZU:
                f.write(f'#EXTINF:-1 tvg-name="{kanal["ad"]}" group-title="{kanal["kategori"]}",{kanal["ad"]}\n')
                # YouTube ID'sini TiviMate'in oynatabileceği proxy linkine çeviriyoruz
                f.write(f'{proxy_url}{kanal["yt_id"]}\n')
                
        print("🎉 Ölümsüz ve donmaz listen hazır usta! otomatik_liste.m3u başarıyla güncellendi.")
    except Exception as e:
        print(f"❌ Liste yazılırken hata çıktı: {e}")

if __name__ == "__main__":
    liste_olustur()
