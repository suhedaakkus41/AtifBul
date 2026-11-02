import requests
import json
from pathlib import Path


# REMZI BASAR - DUZCE UNIVERSITESI

AUTHOR_ID = "A5007768129"

OPENALEX_API = "https://api.openalex.org"


# ==========================================
# 1. AKADEMISYENIN YAYINLARINI GETIR
# ==========================================

def yayinlari_getir(author_id=AUTHOR_ID):

    url = f"{OPENALEX_API}/works"

    params = {
        "filter": f"author.id:{author_id}",
        "per-page": 100
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    yayinlar = []

    for yayin in data["results"]:

        yazarlar = [
            kayit["author"]["display_name"]
            for kayit in yayin.get("authorships", [])
            if kayit.get("author")
        ]

        yayin_bilgisi = {
            "baslik": yayin.get("display_name"),
            "yazarlar": yazarlar,
            "yil": yayin.get("publication_year"),
            "doi": yayin.get("doi"),
            "openalex_id": yayin.get("id"),
            "yayin_turu": yayin.get("type"),
            "atif_sayisi": yayin.get("cited_by_count", 0)
        }

        yayinlar.append(yayin_bilgisi)

    return yayinlar


# ==========================================
# 2. YAYINA YAPILAN ATIFLARI GETIR
# ==========================================

def atiflari_getir(yayin_id):

    yayin_id = yayin_id.split("/")[-1]

    url = f"{OPENALEX_API}/works"

    params = {
        "filter": f"cites:{yayin_id}",
        "per-page": 100
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    atiflar = []

    for eser in data["results"]:

        yazarlar = [
            kayit["author"]["display_name"]
            for kayit in eser.get("authorships", [])
            if kayit.get("author")
        ]

        atif_bilgisi = {
            "atif_yapan_eser": eser.get("display_name"),
            "yazarlar": yazarlar,
            "yil": eser.get("publication_year"),
            "doi": eser.get("doi"),
            "openalex_id": eser.get("id"),
            "atif_yapilan_yayin_id": f"https://openalex.org/{yayin_id}",
            "durum": "İncelenmeli"
        }

        atiflar.append(atif_bilgisi)

    return atiflar


# ==========================================
# 3. TEST VE JSON KAYDETME
# ==========================================

if __name__ == "__main__":

    print("OPENALEX API TESTI")
    print("=" * 50)

    # Akademisyen yayınlarını getir

    print("\nYayinlar getiriliyor...")

    yayinlar = yayinlari_getir()

    print("Toplam yayin:", len(yayinlar))

    for yayin in yayinlar:

        print("\nBaslik:", yayin["baslik"])
        print("Yazarlar:", ", ".join(yayin["yazarlar"]))
        print("Yil:", yayin["yil"])
        print("DOI:", yayin["doi"])

    # Atıf testi

    print("\nATIF TESTI")
    print("=" * 50)

    test_yayin_id = "W4412693716"

    atiflar = atiflari_getir(test_yayin_id)

    print("Toplam atif:", len(atiflar))

    # JSON dosyasına kaydet

    dosya_yolu = (
        Path(__file__).resolve().parent
        / "openalex_api_atiflar.json"
    )

    with open(dosya_yolu, "w", encoding="utf-8") as dosya:

        json.dump(
            atiflar,
            dosya,
            ensure_ascii=False,
            indent=4
        )

    print("\nJSON dosyasi olusturuldu!")
    print("Kaydedilen atif:", len(atiflar))
    print("Dosya:", dosya_yolu)