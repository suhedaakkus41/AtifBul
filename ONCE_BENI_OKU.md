# AtıfBul — Yasemin’in son kontrol paketi

Kontrol tarihi: 2 Kasım 2026. Şüheda’nın orijinal ZIP’i değiştirilmedi. Bu klasör, kontrol sırasında gerekli düzeltmeler yapılan ayrı sürümdür.

## Şimdi yapacağınız işlem

1. Bu ZIP’i Şüheda’ya gönderin; düzeltilmiş kopya olduğunu söyleyin. İki klasörün dosyalarını birbirine karıştırmayın.
2. ZIP’i tamamen çıkarın. Windows’ta klasördeki BASLAT_WINDOWS.bat dosyasını açın. Python 3.12 veya daha yeni bir sürüm gerekir. İlk kurulum internet gerektirir.
3. Açılan sayfada veri kaynağını kontrol edin. Kayıtlı demo varsayılan seçenektir; canlı API sorgusu yapmaz.
4. Akademisyen adı: Remzi Başar. Atıf yılı: 2025. Atıfları bul → Tümünü seç → Seçili yayınları analiz et.
5. Kayıtlı demoda 2025 için 5 sonuç beklenir. Hedonik/faydacı değer ve QR kod makalesini bulun; Kanıtı aç bağlantısıyla kaynakçayı gösterin.
6. Yılı 2026 yapın, analizi yeniden başlatın. Kayıtlı demoda 12 sonuç beklenir. Önceki sonuç yıl değişiminde temizlenir.
7. Hocaya götüreceğiniz bilgisayarda CSV/Excel indir düğmelerini ve bir kanıt bağlantısını bir kez açın. Bu son deneme, bilgisayarınızın kurulumu ve tarayıcısı için gereklidir.

Terminalden alternatif kurulum:

    python -m venv .venv
    .venv\Scripts\python -m pip install -r requirements.txt
    .venv\Scripts\python -m streamlit run app.py

Mac/Linux: aynı komutlarda Python yolu `.venv/bin/python` olur.

## Veriler ve etiketlerin anlamı

- Begüm/Emine’nin 18 yayın ve 25 atıf adayı, gönderilen JSON dosyalarıyla aynıdır; veriler değiştirilmedi.
- Tüm yılların toplamında 19 ilişki için daha önce yapılan elle kaynakça kontrolü bulunuyor; 6 ilişki incelenmeli. Yıl filtresi bu toplamı daraltır.
- `manuel_dogrulama.json` bu 25 ilişkiye ait kontrol sonucunu, kanıt URL’sini ve yerini taşır. Karar hedef yayın ID + atıf yapan eser ID çiftiyle bağlanır.
- İki doğrulanmış ilişki öz atıftır ve ayrıca işaretlidir. Diğer ilişkilerde öz atıf araştırması yapılmış varsayılmaz.
- “Doğrulandı” otomatik yapay zekâ/PDF kararından gelmez; elle yapılan kaynakça kontrolüdür.
- PDF bölümü yalnız metin çıkarır. Öğrenci ödevlerinin atıflarını otomatik kontrol eden son proje henüz tamamlanmış değildir. Bu sürüm, hocanın istediği Remzi Başar odaklı ara prototiptir.
- Başka yılda/yenilenen canlı sorguda çıkan yeni kayıtlar, bu 25’lik listede kanıtı yoksa incelenmeli kalır.
- Canlı servis başarısız olunca sessizce demo verisine geçilmez; hata gösterilir. Kullanıcı isterse veri kaynağını açıkça değiştirir.

## Kontrol sonucu

`TEST_RAPORU.md` dosyasını okuyun. 35 otomatik kontrol geçti. Fiziksel tarayıcıda tıklama, görünüm ve dosyanın indirilenler klasörüne düşmesi bu ortamda ayrıca denenmedi.

Bu klasörde Begüm’ün 17 makalelik başlık eşleştirme listesi kullanılmıyor. Dolayısıyla oradaki iki güvenilmez öneri bu demo listesinden sisteme aktarılmıyor.
