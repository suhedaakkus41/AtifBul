"""Akademik yayın kaydı eşleştirme modülü (3. kişi).

Bu modül aynı yayını temsil eden kayıtları DOI / başlık üzerinden karşılaştırır.
Bir eserin başka bir esere atıf yaptığını tek başına kanıtlamaz.
"""

import json
import re
from pathlib import Path

from rapidfuzz import fuzz


BASLIK_ESIGI = 70  # Başlangıç eşiği; ileride test sonuçlarına göre ayarlanacak.


def doi_temizle(doi):
    """DOI bağlantısını standart DOI değerine dönüştürür."""
    if not doi:
        return ""

    doi = str(doi).strip().lower()
    doi = re.sub(r"^doi:\s*", "", doi)
    doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi)
    return doi.strip()


def metin_temizle(metin):
    """Başlığı küçük harfe çevirir, noktalama ve fazla boşlukları temizler."""
    if not metin:
        return ""

    metin = str(metin).casefold().strip()
    metin = re.sub(r"[^\w\s]", " ", metin)
    return " ".join(metin.split())


def baslik_al(kayit):
    """Kendi formatımızdaki 'baslik' veya OpenAlex'in 'title' alanını okur."""
    return kayit.get("baslik") or kayit.get("title") or ""


def yayin_eslestir(kayit1, kayit2):
    """İki yayın kaydını karşılaştırır; durum, yöntem, puan ve gerekçe döndürür."""
    doi1 = doi_temizle(kayit1.get("doi"))
    doi2 = doi_temizle(kayit2.get("doi"))

    baslik1 = metin_temizle(baslik_al(kayit1))
    baslik2 = metin_temizle(baslik_al(kayit2))

    if doi1 and doi2:
        if doi1 == doi2:
            return {
                "eslesti": True,
                "durum": "dogrulandi",
                "yontem": "doi",
                "puan": 100,
                "gerekce": "İki kaydın DOI değeri aynı."
            }
        return {
            "eslesti": False,
            "durum": "eslesmedi",
            "yontem": "doi_farkli",
            "puan": 0,
            "gerekce": "İki kaydın DOI değeri farklı."
        }

    if not baslik1 or not baslik2:
        return {
            "eslesti": False,
            "durum": "yetersiz_veri",
            "yontem": "baslik",
            "puan": 0,
            "gerekce": "DOI karşılaştırması yapılamıyor ve başlık eksik."
        }

    puan = round(fuzz.ratio(baslik1, baslik2), 2)
    durum = "incelenmeli" if puan >= BASLIK_ESIGI else "eslesmedi"
    return {
        "eslesti": False,  # Başlık benzerliği tek başına kesin eşleşme değildir.
        "durum": durum,
        "yontem": "baslik_benzerligi",
        "puan": puan,
        "gerekce": (
            f"En az bir DOI eksik. Başlık benzerliği {puan}/100; "
            f"başlangıç eşiği {BASLIK_ESIGI}/100."
        )
    }


def toplu_eslestir(aranan_yayin, gelen_kayitlar):
    """Bir yayını birden fazla aday yayın kaydıyla karşılaştırır."""
    sonuclar = []
    for sira, kayit in enumerate(gelen_kayitlar, start=1):
        sonuc = yayin_eslestir(aranan_yayin, kayit)
        sonuclar.append({
            "sira": sira,
            "hedef_baslik": baslik_al(aranan_yayin),
            "kayit_baslik": baslik_al(kayit),
            "kayit_doi": kayit.get("doi"),
            "kayit_id": kayit.get("id"),
            **sonuc
        })
    return sonuclar


if __name__ == "__main__":
    # Kullanıcının başlangıç paketindeki GERÇEK hedef yayınını oku.
    # JSON'daki 'test_cases' atıf yapan BELGELERDİR; yayın eşleştirmesine
    # doğrudan sokulmaz. PDF kaynakçası henüz ayrıştırılmadı.
    veri_yolu = Path(__file__).with_name("test_beklentileri.json")
    if veri_yolu.exists():
        with veri_yolu.open("r", encoding="utf-8-sig") as dosya:
            veri = json.load(dosya)
        hedef_baslik = veri["target_publication"]["title"]
        print("Hedef yayın başlığı JSON dosyasından okundu.")
    else:
        hedef_baslik = "Artificial Intelligence in Education"
        print("JSON bulunamadı; örnek hedef yayın kullanılıyor.")

    hedef_yayin = {"baslik": hedef_baslik, "doi": None}

    # Buradaki adaylar yalnızca algoritmanın toplu çalışma demosudur.
    # Gerçek OpenAlex kayıtları gelince bu liste onların yerini alacak.
    aday_kayitlar = [
        {"id": "demo-1", "baslik": hedef_baslik, "doi": None},
        {"id": "demo-2", "baslik": hedef_baslik.replace("Yazılımının ", ""), "doi": None},
        {"id": "demo-3", "baslik": "Bilgisayar Ağlarında Güvenlik", "doi": None},
    ]

    print("\nTOPLU EŞLEŞTİRME DEMOSU (aday kayıtlar temsili)")
    for sonuc in toplu_eslestir(hedef_yayin, aday_kayitlar):
        print("-" * 50)
        print("Aday:", sonuc["kayit_baslik"])
        print("Durum:", sonuc["durum"])
        print("Yöntem:", sonuc["yontem"])
        print("Puan:", sonuc["puan"])
        print("Gerekçe:", sonuc["gerekce"])
