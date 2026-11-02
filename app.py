import io
import re
import time

import fitz  # PyMuPDF
import pandas as pd
import requests
import streamlit as st

from openalex_api import yayinlari_getir, atiflari_getir


# ==================================================
# SAYFA AYARLARI
# ==================================================

st.set_page_config(
    page_title="AtıfBul",
    page_icon="📘",
    layout="wide"
)

OPENALEX_API = "https://api.openalex.org"

# OpenAlex kurum adlarını çoğunlukla İngilizce tutar ("Duzce University").
# Bu yüzden birebir eşleşme yerine anahtar kelime ile eşleştiriyoruz.
KURUM_ANAHTARLARI = {
    "Düzce Üniversitesi": ["düzce", "duzce"],
}


# ==================================================
# TASARIM
# ==================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #ffffff;
}

.block-container {
    max-width: 1150px;
    padding-top: 1rem;
    padding-bottom: 3rem;
}

header, footer, #MainMenu {
    visibility: hidden;
}

.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0 18px 0;
    border-bottom: 1px solid #e4eaf5;
    margin-bottom: 25px;
}

.logo {
    font-size: 25px;
    font-weight: 800;
    color: #102d61;
}

.logo-icon {
    background: #0755e9;
    color: white;
    padding: 9px 13px;
    border-radius: 10px;
    margin-right: 8px;
}

.nav-links {
    color: #102d61;
    font-size: 14px;
    font-weight: 600;
    display: flex;
    gap: 30px;
}

.hero {
    text-align: center;
    padding: 10px 0 20px;
}

.badge {
    display: inline-block;
    background: #edf3ff;
    color: #0755e9;
    padding: 8px 18px;
    border-radius: 30px;
    font-size: 13px;
    font-weight: 700;
    margin-bottom: 15px;
}

.hero h1 {
    color: #102d61;
    font-size: 38px;
    line-height: 1.2;
    font-weight: 800;
}

.hero p {
    color: #52647f;
    font-size: 16px;
    line-height: 1.5;
}

.section-title {
    color: #102d61;
    font-size: 21px;
    font-weight: 800;
    margin-top: 22px;
    margin-bottom: 5px;
}

.section-desc {
    color: #53647f;
    font-size: 13px;
    margin-bottom: 13px;
}

.stButton > button {
    border-radius: 10px;
    font-weight: 700;
    min-height: 40px;
}

.stTextInput input {
    border-radius: 9px;
}

div[data-testid="stDataFrame"] {
    border: 1px solid #d7e3fa;
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)


# ==================================================
# YARDIMCI FONKSİYONLAR
# ==================================================

def kisa_id(deger):
    """https://openalex.org/W123 -> W123"""
    return (deger or "").split("/")[-1]


def kurum_uyuyor_mu(kurum, kurum_adlari):
    anahtarlar = KURUM_ANAHTARLARI.get(kurum, [kurum.lower()])
    metin = " ".join(kurum_adlari).lower()
    return any(a in metin for a in anahtarlar)


def openalex_get(url, params=None, timeout=30, max_deneme=4):
    """OpenAlex isteklerinde 429 ve geçici sunucu hatalarında kontrollü tekrar dener."""
    son_yanit = None

    for deneme in range(max_deneme):
        yanit = requests.get(url, params=params, timeout=timeout)
        son_yanit = yanit

        if yanit.status_code not in (429, 500, 502, 503, 504):
            yanit.raise_for_status()
            return yanit

        if deneme == max_deneme - 1:
            yanit.raise_for_status()

        bekleme = yanit.headers.get("Retry-After")
        try:
            bekleme_suresi = float(bekleme) if bekleme else min(2 ** (deneme + 1), 20)
        except (ValueError, TypeError):
            bekleme_suresi = min(2 ** (deneme + 1), 20)

        time.sleep(bekleme_suresi)

    if son_yanit is not None:
        son_yanit.raise_for_status()
    raise RuntimeError("OpenAlex isteği tamamlanamadı.")


@st.cache_data(ttl=3600, show_spinner=False)
def akademisyen_ara(ad, kurum=None):
    """Akademisyen aramasını bir saat önbellekte tutar; aday başına ek istek göndermez."""
    response = openalex_get(
        f"{OPENALEX_API}/authors",
        params={"search": ad, "per-page": 25},
        timeout=30,
    )

    sonuclar = []

    for kisi in response.json().get("results", []):
        kurumlar = kisi.get("last_known_institutions") or []
        kurum_adlari = [
            x.get("display_name", "")
            for x in kurumlar
        ]

        if kurum and not kurum_uyuyor_mu(kurum, kurum_adlari):
            continue

        sonuclar.append({
            "id": kisa_id(kisi.get("id", "")),
            "name": kisi.get("display_name", ""),
            "institution": ", ".join(kurum_adlari) or "Kurum bilgisi yok",
            "works_count": kisi.get("works_count", 0),
            "sample_work": "",
        })

    return sonuclar[:8]


@st.cache_data(ttl=3600, show_spinner=False)
def yayinlari_getir_onbellek(author_id):
    """Akademisyenin yayın listesini bir saat önbellekte tutar."""
    return yayinlari_getir(author_id)


@st.cache_data(ttl=3600, show_spinner=False)
def atiflari_getir_onbellek(yayin_id):
    """Bir yayının atıf listesini bir saat önbellekte tutar."""
    return atiflari_getir(yayin_id)


@st.cache_data(ttl=3600, show_spinner=False)
def yayin_ara(deger):
    """DOI ise doğrudan DOI ile, değilse başlıkla arar. Bulamazsa None döner."""
    deger = deger.strip()
    doi = re.search(r"10\.\d{4,9}/\S+", deger)

    if doi:
        response = openalex_get(
            f"{OPENALEX_API}/works/https://doi.org/{doi.group(0)}",
            timeout=30,
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()

    response = openalex_get(
        f"{OPENALEX_API}/works",
        params={"search": deger, "per-page": 1},
        timeout=30,
    )
    response.raise_for_status()
    sonuc = response.json().get("results", [])
    return sonuc[0] if sonuc else None


def atiflari_getir_arayuz(yayin_id, yil):

    ham_veriler = atiflari_getir(yayin_id)

    st.write("Seçilen yıl:", yil)
    st.write("API'den gelen toplam kayıt:", len(ham_veriler))

    st.write(
        "API'den gelen yıllar:",
        sorted(set(
            str(k.get("yil", k.get("atif_yili", "YIL YOK")))
            for k in ham_veriler
        ))
    )

    sonuclar = []

    for kayit in ham_veriler:

        kayit_yili = kayit.get("yil", kayit.get("atif_yili"))

        if kayit_yili is None:
            continue

        if str(kayit_yili).strip() != str(yil).strip():
            continue

        sonuclar.append({
            "Atıf yapan eser": kayit.get("atif_yapan_eser", ""),
            "Yıl": kayit_yili,
            "DOI": kayit.get("doi", ""),
            "Durum": "İncelenmeli"
        })

    st.write("Filtre sonrası kayıt:", len(sonuclar))

    return sonuclar


def tumunu_sec(author_id, idler, deger):
    """Onay kutularını güvenli şekilde (callback ile) toplu değiştirir."""
    for yid in idler:
        st.session_state[f"yayin_{author_id}_{yid}"] = deger


def yeni_arama_yap():
    st.session_state.clear()

# ==================================================
# ÜST MENÜ
# ==================================================

st.html("""
<div class="navbar">
    <div class="logo">
        <span class="logo-icon">▣</span>AtıfBul
    </div>
    <div class="nav-links">
        <span>Nasıl çalışır</span>
        <span>Yöntem</span>
        <span>Doğrulama</span>
        <span>Hakkında</span>
    </div>
</div>
""")


# ==================================================
# ANA BAŞLIK
# ==================================================

st.html("""
<div class="hero">
    <div class="badge">Yapay zekâ destekli atıf tarama</div>
    <h1>
        Bir akademisyenin aldığı atıfları<br>
        kanıtlarıyla birlikte bulun
    </h1>
    <p>
        Akademisyen adını ve yılı girin; OpenAlex verileriyle atıf yapan eserleri
        <br>listeleyelim, belirsiz kayıtları doğrulama için işaretleyelim.
    </p>
</div>
""")

# ==================================================
# ARAMA ALANI
# ==================================================

with st.container(border=True):

    col1, col2, col3 = st.columns([1.2, 1, 0.9])

    with col1:
        akademisyen_adi = st.text_input(
            "Akademisyen adı",
            placeholder="Örn. Remzi Başar"
        )

    with col2:
        kurum = st.selectbox(
            "Kurum",
            ["Tüm kurumlar", "Düzce Üniversitesi"]
        )

    with col3:
        atif_yili = st.number_input(
            "Atıf yılı",
            min_value=2000,
            max_value=2035,
            value=2026
        )

    c1, c2 = st.columns([4, 1])

    with c1:
        ara = st.button(
            "⌕  Atıfları bul",
            type="primary",
            width="stretch"
        )

    with c2:
        st.button(
            "↻  Yeni arama",
            width="stretch",
            on_click=yeni_arama_yap
        )


if ara:

    if not akademisyen_adi.strip():

        st.warning("Lütfen akademisyen adını girin.")

    else:

        try:

            kurum_filtre = None if kurum == "Tüm kurumlar" else kurum

            with st.spinner("Akademisyenler aranıyor..."):
                bulunanlar = akademisyen_ara(akademisyen_adi, kurum_filtre)

            # Yeni aramada eski durumu temizle
            st.session_state.pop("akademisyen_secimi", None)
            st.session_state.authors = bulunanlar
            st.session_state.year = int(atif_yili)
            st.session_state.results = None
            st.session_state.selected_author = None
            st.session_state.loaded_author_id = None
            st.session_state.manual_works = {}

        except requests.exceptions.HTTPError as hata:
            if getattr(hata.response, "status_code", None) == 429:
                st.error(
                    "OpenAlex şu anda çok fazla istek alıyor (429). "
                    "Lütfen birkaç dakika sonra tekrar deneyin. "
                    "Başarılı aramalar bir saat önbellekte tutulur."
                )
            else:
                st.error(f"Akademisyen aranırken hata oluştu: {hata}")

        except Exception as hata:
            st.error(f"Akademisyen aranırken hata oluştu: {hata}")


# ==================================================
# 1. AKADEMİSYEN SEÇİMİ
# ==================================================

authors = st.session_state.get("authors")

if authors is not None and len(authors) == 0:

    st.warning(
        "Bu arama için akademisyen bulunamadı. "
        "Adı farklı yazmayı veya kurum filtresini 'Tüm kurumlar' yapmayı deneyin."
    )

if authors:

    st.markdown(
        '<div class="section-title">1. Doğru kişiyi seçin</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-desc">Benzer isimli kişiler varsa kurum ve örnek yayın bilgilerini kontrol edin.</div>',
        unsafe_allow_html=True
    )

    # Aynı ad/kurum/yayın sayısına sahip adaylar karışmasın diye indeks kullanıyoruz
    secilen_index = st.radio(
        "Aday akademisyenler",
        options=list(range(len(authors))),
        format_func=lambda i: (
            f"{authors[i]['name']} · {authors[i]['institution']} · "
            f"{authors[i]['works_count']} yayın"
        ),
        key="akademisyen_secimi"
    )

    author = authors[secilen_index]
    st.session_state.selected_author = author

    st.info(
        f"Seçilen akademisyen: {author['name']} | "
        f"Kurum: {author['institution']} | "
        f"Örnek yayın: {author['sample_work'] or 'Bilgi yok'}"
    )


# ==================================================
# 2. YAYIN LİSTESİ
# ==================================================

author = st.session_state.get("selected_author")

if author:

    st.markdown(
        '<div class="section-title">2. Yayın listesini kontrol edin</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-desc">Atıfı aranacak yayınları işaretleyin.</div>',
        unsafe_allow_html=True
    )

    try:

        if st.session_state.get("loaded_author_id") != author["id"]:

            with st.spinner("Yayınlar getiriliyor..."):
                st.session_state.works = yayinlari_getir_onbellek(author["id"])

            st.session_state.loaded_author_id = author["id"]

        manuel = st.session_state.setdefault("manual_works", {})
        eklenenler = manuel.setdefault(author["id"], [])

        # OpenAlex'ten gelen + elle eklenen yayınlar tek listede
        tum_yayinlar = list(st.session_state.get("works", [])) + eklenenler

        idler = [kisa_id(w.get("openalex_id", "")) for w in tum_yayinlar]

        if tum_yayinlar:

            b1, b2 = st.columns(2)

            with b1:
                st.button(
                    "☑ Tümünü seç",
                    on_click=tumunu_sec,
                    args=(author["id"], idler, True)
                )

            with b2:
                st.button(
                    "▣ Seçimi temizle",
                    on_click=tumunu_sec,
                    args=(author["id"], idler, False)
                )

            secili = []

            for w, yayin_id in zip(tum_yayinlar, idler):

                baslik = w.get("baslik") or "Başlıksız yayın"
                yil = w.get("yil") or "-"
                doi = w.get("doi") or "DOI bulunmuyor"

                anahtar = f"yayin_{author['id']}_{yayin_id}"
                st.session_state.setdefault(anahtar, False)

                if st.checkbox(
                    f"**{baslik}**  \nDOI: {doi} · {yil}",
                    key=anahtar
                ):
                    secili.append(yayin_id)

            st.write(f"**Seçili yayın:** {len(secili)} / {len(tum_yayinlar)}")

        else:

            secili = []
            st.warning("Bu akademisyene ait yayın bulunamadı. Aşağıdan elle ekleyebilirsiniz.")

        # ---------- Eksik yayın ekleme ----------

        with st.expander("Eksik yayın ekle"):

            ekle_degeri = st.text_input("DOI veya yayın başlığı")

            if st.button("Yayın ekle"):

                if not ekle_degeri.strip():

                    st.warning("Lütfen DOI veya başlık girin.")

                else:

                    try:
                        bulunan = yayin_ara(ekle_degeri)
                    except Exception as hata:
                        bulunan = None
                        st.error(f"Yayın aranırken hata oluştu: {hata}")
                    else:
                        if not bulunan:
                            st.warning("Yayın bulunamadı.")
                        else:
                            yeni_id = kisa_id(bulunan.get("id", ""))

                            if yeni_id in idler:
                                st.info("Bu yayın zaten listede.")
                            else:
                                eklenenler.append({
                                    "baslik": bulunan.get("title"),
                                    "openalex_id": yeni_id,
                                    "doi": bulunan.get("doi"),
                                    "yil": bulunan.get("publication_year"),
                                })
                                st.session_state[f"yayin_{author['id']}_{yeni_id}"] = True
                                st.rerun()

        # ---------- Atıf analizi ----------

        if st.button(
            "▷  Seçili yayınları analiz et",
            type="primary",
            use_container_width=True
        ):

            if not secili:

                st.warning("Önce en az bir yayın seçin.")

            else:

                baslik_haritasi = {
                    kisa_id(w.get("openalex_id", "")): w.get("baslik")
                    for w in tum_yayinlar
                }

                tum_sonuclar = []

                try:
                    with st.spinner("Atıflar analiz ediliyor..."):
                        for yayin_id in secili:
                            bulunanlar = atiflari_getir_onbellek(yayin_id)

                            for kayit in bulunanlar:
                                # Atıf yapan eserin yayın yılını farklı olası alanlardan al.
                                kayit_yili = kayit.get("yil")
                                if kayit_yili is None:
                                    kayit_yili = kayit.get("atif_yili")

                                try:
                                    kayit_yili = int(kayit_yili)
                                except (ValueError, TypeError):
                                    continue

                                # Yalnızca kullanıcının seçtiği atıf yılını göster.
                                if kayit_yili != int(st.session_state.year):
                                    continue

                                tum_sonuclar.append({
                                    "Atıf yapan eser": kayit.get("atif_yapan_eser", ""),
                                    "Yıl": kayit_yili,
                                    "DOI": kayit.get("doi") or kayit.get("atif_yapan_doi") or "DOI bulunmuyor",
                                    "Atıf yapan eser ID": kayit.get("openalex_id") or kayit.get("atif_yapan_eser_id", ""),
                                    "Atıf alan yayın ID": yayin_id,
                                    "Durum": "İncelenmeli",
                                    "Bağımsız doğrulama": "Henüz yapılmadı"
                                })

                    st.session_state.results = pd.DataFrame(tum_sonuclar)
                    st.success(
                        f"{st.session_state.year} yılı için "
                        f"{len(tum_sonuclar)} atıf kaydı bulundu."
                    )

                except Exception as hata:
                    st.error(f"Atıf analizi sırasında hata oluştu: {hata}")

    except Exception as hata:
        st.error(f"Yayınlar yüklenirken hata oluştu: {hata}")

# ==================================================
# 3. SONUÇLAR
# ==================================================

sonuc = st.session_state.get("results")

if sonuc is not None:

    st.markdown(
        '<div class="section-title">3. Sonuçlar</div>',
        unsafe_allow_html=True
    )

    if not sonuc.empty:

        st.dataframe(
            sonuc,
            width="stretch",
            hide_index=True,
            column_config={
                "Kanıt": st.column_config.LinkColumn(
                    "Kanıt", display_text="Kaynağı aç"
                )
            }
        )

        col1, col2 = st.columns(2)

        with col1:

            st.download_button(
                "↓ CSV indir",
                sonuc.to_csv(index=False).encode("utf-8-sig"),
                file_name="atifbul_sonuclari.csv",
                mime="text/csv"
            )

        with col2:

            # openpyxl kurulu değilse sayfa çökmesin
            try:
                excel = io.BytesIO()

                with pd.ExcelWriter(excel, engine="openpyxl") as writer:
                    sonuc.to_excel(
                        writer,
                        index=False,
                        sheet_name="Atıf Sonuçları"
                    )

                st.download_button(
                    "▣ Excel indir",
                    excel.getvalue(),
                    file_name="atifbul_sonuclari.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except ImportError:
                st.caption("Excel indirme için: pip install openpyxl")

    else:

        st.info("Seçilen yayınlar için bu yılda atıf bulunamadı.")


# ==================================================
# PDF YÜKLEME
# ==================================================

st.markdown("---")

st.markdown(
    '<div class="section-title">PDF yükle ve kaynakçayı doğrula</div>',
    unsafe_allow_html=True
)

st.write(
    "Atıf yapan eserin PDF dosyasını yükleyerek "
    "kaynakça metnini çıkarabilirsiniz."
)

pdf = st.file_uploader("PDF dosyası seçin", type=["pdf"])

if pdf:

    if st.button("PDF'yi analiz et", type="primary"):

        try:

            with fitz.open(stream=pdf.read(), filetype="pdf") as belge:
                sayfa_sayisi = len(belge)
                metin = "\n".join(sayfa.get_text() for sayfa in belge)

            st.success(f"PDF okundu. Toplam {sayfa_sayisi} sayfa.")

            st.text_area(
                "PDF'den çıkarılan metin",
                metin[:10000],
                height=250
            )

            st.info(
                "PDF metni çıkarıldı. Kaynakça eşleştirmesi ve "
                "bağımsız atıf doğrulaması henüz yapılmadı."
            )

        except Exception as hata:

            st.error(f"PDF analiz hatası: {hata}")


# ==================================================
# ALT BİLGİ
# ==================================================

st.markdown("---")

st.markdown("""
<div style="text-align:center;color:#8492a8;font-size:12px;padding:15px;">
    AtıfBul · Akademik Atıf Analiz Platformu
    <br>
    OpenAlex verileri kullanılarak geliştirilmiştir.
</div>
""", unsafe_allow_html=True)
