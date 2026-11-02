"""Kayıtlı demo ve elle doğrulanmış atıf kanıtları; API sorgusu yapmaz."""
import json
import re
import unicodedata
from pathlib import Path

BASE = Path(__file__).resolve().parent

def oku(ad):
    return json.loads((BASE / ad).read_text(encoding="utf-8-sig"))

def kid(value):
    return (value or "").rstrip("/").rsplit("/", 1)[-1]

def normalize(value):
    value = unicodedata.normalize("NFKD", str(value).casefold().replace("ı", "i"))
    return re.sub(r"[^a-z0-9]", "", value)

def demo_akademisyen(ad):
    if normalize(ad) not in {"remzi", "basar", "remzibasar"}:
        return []
    return [{"id": "A5007768129", "name": "Remzi Başar",
             "institution": "Düzce Üniversitesi", "works_count": len(oku("remzi_basar_yayinlar.json")),
             "sample_work": oku("remzi_basar_yayinlar.json")[0]["display_name"]}]

def demo_yayinlar(author_id):
    if kid(author_id) != "A5007768129":
        return []
    return [{"baslik": p["display_name"], "yil": p.get("publication_year"),
             "doi": p.get("doi"), "openalex_id": p["id"]}
            for p in oku("remzi_basar_yayinlar.json")]

def demo_atiflar(yayin_id):
    return [{"atif_yapan_eser": r["atif_yapan_eser"], "yil": r["atif_yili"],
             "doi": r.get("doi"), "openalex_id": r["atif_yapan_eser_id"]}
            for r in oku("remzi_basar_atiflar.json") if kid(r["hedef_yayin_id"]) == kid(yayin_id)]

def demo_yayin_ara(deger):
    for p in oku("remzi_basar_yayinlar.json"):
        if normalize(deger) in {normalize(p.get("doi") or ""), normalize(p["display_name"])}:
            return p
    return None

def sonuc_satiri(kayit, hedef_id, hedef_baslik):
    atif_id = kid(kayit.get("openalex_id") or kayit.get("atif_yapan_eser_id"))
    proof = next((r for r in oku("manuel_dogrulama.json")
                  if r["hedef_id"] == kid(hedef_id) and r["atif_id"] == atif_id), None)
    verified = bool(proof and proof["dogrulandi"])
    doi = kayit.get("doi") or kayit.get("atif_yapan_doi") or ""
    return {
        "Atıf alan yayın": hedef_baslik,
        "Atıf yapan eser": kayit.get("atif_yapan_eser", ""),
        "Yıl": int(kayit.get("yil", kayit.get("atif_yili"))),
        "DOI": doi,
        "Atıf yapan eser ID": "https://openalex.org/" + atif_id if atif_id else "",
        "Atıf alan yayın ID": kid(hedef_id),
        "Durum": "Doğrulandı" if verified else "İncelenmeli",
        "Bağımsız doğrulama": "Elle kaynakça kontrolü · 02.11.2026" if verified else "Kaynakça doğrulanmadı",
        "Kanıt": proof["kanit"] if verified else "",
        "Kanıtın yeri": proof["yer"] if proof else "",
        "Yayın bağlantısı": doi or ("https://openalex.org/" + atif_id if atif_id else ""),
        "Öz atıf": "Evet" if proof and proof["oz_atif"] else "Belirlenmedi",
    }
