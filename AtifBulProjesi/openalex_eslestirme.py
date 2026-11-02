"""7. hafta: 2. kişinin OpenAlex JSON kayıtlarını 3. kişinin modülüne bağlar.

Uyarı: OpenAlex'teki cites ilişkisi, PDF kaynakçasında bağımsız
olarak doğrulanmış atıf değildir.
"""
import json
from pathlib import Path
from collections import Counter
from atifEslestirici import yayin_eslestir

KLASOR = Path(__file__).resolve().parent


def json_oku(ad):
    with (KLASOR / ad).open(encoding="utf-8-sig") as dosya:
        return json.load(dosya)


def openalex_eslestir(yayinlar, atiflar):
    yayin_indeksi = {x['id']: x for x in yayinlar if x.get('id')}
    kullanilan = set()
    sonuclar = []
    for kayit in atiflar:
        hedef_id = kayit.get('hedef_yayin_id')
        atif_id = kayit.get('atif_yapan_eser_id')
        # Tekrar kaydı: aynı atıf yapan eser + aynı hedef yayını bir kez işle.
        anahtar = (atif_id, hedef_id)
        if anahtar in kullanilan:
            continue
        kullanilan.add(anahtar)
        hedef = yayin_indeksi.get(hedef_id)
        if hedef is None:
            durum = 'hedef_bulunamadi'
            kimlik = None
            gerekce = 'Atıf kaydındaki hedef OpenAlex ID, yayın listesinde bulunamadı.'
        else:
            # Atıf kaydının hedef başlığını hedef yayınla karşılaştır.
            # Buradaki DOI hedef DOI'sidir; atıf yapanın DOI'si ile karşılaştırılmaz!
            kimlik = yayin_eslestir(
                {'baslik': kayit.get('hedef_yayin', ''), 'doi': None},
                {'baslik': hedef.get('title') or hedef.get('display_name', ''), 'doi': None}
            )
            durum = 'openalex_iliskisi_incelenmeli'
            gerekce = ('Hedef OpenAlex ID yayın listesiyle eşleşti. '
                       'Atıf OpenAlex cites ilişkisinden alınmıştır; bağımsız kaynakça doğrulaması yapılmadı. '
                       f"Hedef başlık benzerliği: {kimlik['puan']}/100.")
        sonuclar.append({
            'hedef_yayin_id': hedef_id,
            'hedef_yayin': (hedef.get('title') or hedef.get('display_name')) if hedef else kayit.get('hedef_yayin'),
            'hedef_yayin_turu': hedef.get('type') if hedef else None,
            'dergi_makalesi': (hedef.get('type') == 'article' and
                                ((hedef.get('primary_location') or {}).get('source') or {}).get('type') == 'journal') if hedef else False,
            'atif_yapan_eser': kayit.get('atif_yapan_eser'),
            'atif_yapan_eser_id': atif_id,
            'atif_yapan_doi': kayit.get('doi'),
            'atif_yili': kayit.get('atif_yili'),
            'durum': durum,
            'dogrulanmis_atif': False,
            'baslik_kontrolu': kimlik,
            'gerekce': gerekce,
        })
    return sonuclar


def calistir():
    yayinlar = json_oku('remzi_basar_yayinlar.json')
    atiflar = json_oku('remzi_basar_atiflar.json')
    sonuc = openalex_eslestir(yayinlar, atiflar)
    hedef_turleri = Counter(x.get('type', 'belirtilmemis') for x in yayinlar)
    dosya = KLASOR / 'openalex_eslesme_sonuclari.json'
    dosya.write_text(json.dumps(sonuc, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Yayın: {len(yayinlar)} | OpenAlex atıf ilişkisi: {len(atiflar)} | Tekilleştirilmiş: {len(sonuc)}')
    print('Yayın türleri:', dict(hedef_turleri))
    print('Hedefi bulunamayan:', sum(x['durum'] == 'hedef_bulunamadi' for x in sonuc))
    print('Bağımsız doğrulanmış atıf: 0 (kaynakça doğrulaması henüz yapılmadı)')
    print('Arayüz çıktısı:', dosya.name)
    return sonuc


if __name__ == '__main__':
    calistir()
