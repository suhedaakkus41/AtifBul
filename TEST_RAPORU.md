# Yasemin — prototip son kontrol raporu

Tarih: 2 Kasım 2026. İncelenen kaynak: Şüheda’nın AtifBulProjesi.zip dosyası.

## Sonuç

Düzeltilmiş kopyada 35/35 otomatik kontrol geçti. Streamlit AppTest kullanıldı; tarayıcı motorunda görsel düzen kontrolü ve gerçek indirme tıklaması yapılmadı. Canlı akışın tekrarlanabilir arayüz testlerinde HTTP yanıtları kontrollü olarak taklit edildi; bu testler canlı servis çalışırlığının kanıtı değildir.

## Gerçek canlı API denemesi

Gerçek HTTP sorgusunda Remzi Başar’ın 18 yayını alındı. Ardından QR kod yayınına ilişkin atıf sorgusu HTTP 429 (istek sınırı) döndürdü. Bu nedenle tüm canlı atıf akışı başarılı test edilmiş sayılmaz. API kullanılabilirliği yarın değişebilir; kayıtlı demo açıkça ayrı bir seçenek olarak sunuldu.

## Bulunan ve düzeltilenler

- Orijinalde yıl kutusu değiştiğinde analiz eski arama yılını kullanabiliyordu. Yıl güncelleniyor ve eski sonuç temizleniyor. Bu hata orijinal sürümde yeniden üretildi.
- Orijinalde tablo ayarında Kanıt sütunu tanımlıydı fakat sonuç satırlarında sütun yoktu. Hedef yayın adı, kanıt URL’si, kanıtın yeri ve elle doğrulama bilgisi eklendi. Eksiklik orijinal sürümde yeniden üretildi.
- Kişi / kaynak değişiminde ve API hatasında önceki sonuçların ekranda kalması engellendi.
- Mevcut JSON verileri için açıkça etiketli kayıtlı demo eklendi. Canlı sorgu seçeneği korundu.
- Aynı hedef–atıf yapan eser çiftinin birden fazla sayılması engellendi.
- Eksik yayın eklemede farklı yazarın kaydı ve tam başlıkla uyuşmayan ilk arama sonucu kabul edilmiyor; DOI ile araştırma öneriliyor.
- PDF bölümünün başlığı gerçek işlevi olan metin çıkarmaya göre düzeltildi. Yapay zekâ ile otomatik doğrulama yapıldığı iddiası kaldırıldı.
- Kurulum listesi uygulamanın kullandığı, burada test edilen kütüphanelerle UTF-8 olarak yazıldı. Önceki liste requirements_orijinal.txt adıyla korundu.

## Veriye ilişkin kontrol

- Kaynak JSON listeleri önce incelenen 18 yayın / 25 aday verileriyle JSON içeriği açısından aynı.
- 19 kaynakça kontrolü / 6 bekleyen kayıt, yeni arayüzde ilgili ID çiftiyle doğru bağlandı.
- Excel’in 1, 3 ve 6 numaralı kayıtları yeni sonuçlarda kanıtlarıyla bulundu.
- PDF yükleme için mevcut 01_Kanit.pdf kullanıldı; dosya örnekler klasöründe.

## Sonraya kalanlar

- Otomatik kaynakça ve metin içi atıf doğrulaması henüz yok. PDF metin çıkarma testi bu özelliğin tamamlandığı anlamına gelmez.
- API sayfalaması mevcut kodda yok; her çağrı en fazla 100 kayıt alır. Bu küçük kayıtlı demo için 25 aday zaten dosyadan okunuyor.
- Canlı sorguda başka bir yayın görünürse, kayıtsız atıflar elle kontrol edilmeden doğrulandı sayılmaz.
- Begüm’ün iki belirsiz makale başlığına önerilen ID’ler bu uygulamanın veri akışına dahil değil.

## Tekrar çalıştırılabilir kontroller

Kurulumdan sonra klasörde: `python test_prototip.py`

| Kontrol | Sonuç |
|---|---|
|Kontrollü: açılış|Geçti|
|Boş isim uyarısı|Geçti|
|Kayıtlı 18 yayın|Geçti|
|Seçim olmadan analiz uyarısı|Geçti|
|Tümü seçili / 2026 sonucu|Geçti|
|CSV ve Excel indirme düğmeleri|Geçti|
|Yıl değişince eski sonuç silinir|Geçti|
|2025 sonucu|Geçti|
|2017 yıl filtresi|Geçti|
|2019 yıl filtresi|Geçti|
|2022 yıl filtresi|Geçti|
|2023 yıl filtresi|Geçti|
|2024 yıl filtresi|Geçti|
|2025 yıl filtresi|Geçti|
|2026 yıl filtresi|Geçti|
|25 aday tüm yıllarda|Geçti|
|19 elle doğrulandı / 6 incelenmeli|Geçti|
|Doğrulanmış 19 kaydın kanıt URLsi|Geçti|
|İncelenmeli kanıt doğrulaması yapılmış gibi gösterilmez|Geçti|
|2 öz atıf|Geçti|
|Aynı hedef-atıf çifti tekrarsız|Geçti|
|Excel 1 ortak kayıt|Geçti|
|Excel 3 ortak kayıt|Geçti|
|Excel 6 ortak kayıt|Geçti|
|Toplu seçim temizleme|Geçti|
|Yeni arama eski sonuçları kaldırır|Geçti|
|Canlı akış / sahte HTTP: kişi ve yayın yükleme|Geçti|
|Canlı akış / sahte HTTP: filtre ve kanıt|Geçti|
|API hatası önceki sonucu temizler ve hata gösterir|Geçti|
|Son durumda yakalanmamış uygulama hatası yok|Geçti|
|Gerçek PDF yükleme ve metin çıkarma|Geçti|
|PDF metni otomatik doğrulama diye sunulmaz|Geçti|
|Bozuk PDF hata mesajı|Geçti|
|Bilinmeyen başlığa yanlış kayıt eklenmez|Geçti|
|Başka yazarın DOI kaydı reddedilir|Geçti|

Sunucu başlatma kontrolü: Geçti; /_stcore/health HTTP yanıtı ok. Test ortamının developmentMode ayarı kapatıldı. Bu kontrol tarayıcıdaki görsel düzeni doğrulamaz.
