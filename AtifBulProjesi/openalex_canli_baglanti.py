"""7. hafta: 2. kişinin canlı OpenAlex API'sini eşleştirme modülüne bağlar.

Bu modül yalnızca OpenAlex'in bildirdiği atıf ilişkisini gösterir.
Kaynakçadan bağımsız atıf doğrulaması yapmaz.
"""

import json
from pathlib import Path

from atifEslestirici import yayin_eslestir
from openalex_api import yayinlari_getir, atiflari_getir

KLASOR = Path(__file__).resolve().parent
ORNEK_HEDEF_ID = "W4412693716"


def kisa_id(deger):
    return str(deger or "").strip().rstrip("/").split("/")[-1].upper()


def kayitli_hedefler():
    """Önceki haftadan kalan ham yayın JSON'u varsa kimlik karşılaştırması için oku."""
    yol = KLASOR / "remzi_basar_yayinlar.json"
    if not yol.exists():
        return {}
    with yol.open(encoding="utf-8-sig") as dosya:
        return {kisa_id(y.get("id")): y for y in json.load(dosya) if y.get("id")}


def canli_eslestir(yayin_id=ORNEK_HEDEF_ID, yil=None, author_id=None):
    """API'den bir hedef yayının atıf adaylarını getirir; arayüze uygun liste verir.

    yayin_id: Tam OpenAlex URL'si veya W ile başlayan yayın ID'si.
    yil: İsteğe bağlı, atıf yapan çalışmanın yılı.
    author_id: İsteğe bağlı akademisyen OpenAlex ID'si.
    """
    yayinlar = yayinlari_getir(author_id) if author_id else yayinlari_getir()
    yayin_indeksi = {
        kisa_id(y.get("openalex_id")): y
        for y in yayinlar if y.get("openalex_id")
    }
    hedef_id = kisa_id(yayin_id)
    hedef = yayin_indeksi.get(hedef_id)
    if hedef is None:
        raise ValueError(f"{hedef_id} bu akademisyenin yayınları arasında bulunamadı.")

    # OpenAlex canlı verisini eski ham JSON ile DOI/başlık açısından karşılaştır.
    eski = kayitli_hedefler().get(hedef_id)
    kimlik_kontrolu = (
        yayin_eslestir(
            {"baslik": eski.get("title"), "doi": eski.get("doi")},
            {"baslik": hedef.get("baslik"), "doi": hedef.get("doi")},
        ) if eski else None
    )
    kaynak = ((eski.get("primary_location") or {}).get("source") or {}) if eski else {}
    dergi_makalesi = (
        (eski.get("type") == "article" and kaynak.get("type") == "journal")
        if eski else None
    )

    # Bir hedefle başlıyoruz; 18 yayına ayrı ayrı canlı istek gönderilmiyor.
    atiflar = atiflari_getir(hedef_id)
    sonuclar = []
    kullanilan = set()
    for atif in atiflar:
        atif_id = kisa_id(atif.get("openalex_id"))
        gelen_hedef_id = kisa_id(atif.get("atif_yapilan_yayin_id"))
        if not atif_id or not gelen_hedef_id:
            continue
        anahtar = (atif_id, gelen_hedef_id)
        if anahtar in kullanilan:
            continue
        kullanilan.add(anahtar)
        if yil is not None and str(atif.get("yil")) != str(yil):
            continue

        hedef_uygun = gelen_hedef_id == hedef_id
        sonuclar.append({
            "hedef_yayin_id": hedef.get("openalex_id"),
            "hedef_yayin": hedef.get("baslik"),
            "hedef_yayin_turu": hedef.get("yayin_turu"),
            "dergi_makalesi": dergi_makalesi,
            "atif_yapan_eser": atif.get("atif_yapan_eser"),
            "atif_yapan_eser_id": atif.get("openalex_id"),
            "atif_yapan_doi": atif.get("doi"),
            "atif_yapan_yazarlar": atif.get("yazarlar", []),
            "atif_yili": atif.get("yil"),
            "durum": "incelenmeli" if hedef_uygun else "hedef_uyusmazligi",
            "dogrulanmis_atif": False,
            "baslik_kontrolu": kimlik_kontrolu,
            "gerekce": (
                "OpenAlex cites ilişkisi bulundu; kaynakçadan bağımsız doğrulama yapılmadı."
                if hedef_uygun else "API kayıtlarındaki hedef yayın ID'si uyuşmuyor."
            ),
        })
    return sonuclar


def calistir():
    sonuc = canli_eslestir()
    cikti = KLASOR / "openalex_canli_sonuclari.json"
    cikti.write_text(json.dumps(sonuc, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Canlı OpenAlex eşleştirmesi çalıştı.")
    print("Hedef yayın:", ORNEK_HEDEF_ID)
    print("Atıf adayları:", len(sonuc))
    print("Bağımsız doğrulanmış atıf: 0")
    print("Arayüz çıktısı:", cikti.name)
    return sonuc


if __name__ == "__main__":
    calistir()
