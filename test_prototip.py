import sys,pathlib,json,collections,importlib
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
ROOT=pathlib.Path(__file__).resolve().parent;reviewed=ROOT
checks=[]
def check(name,ok,detail=''):
 checks.append({'test':name,'passed':bool(ok),'detail':detail});print(name, bool(ok),detail,flush=True)
def button(at,label):return next(b for b in at.button if label in b.label)
def prepare(path):
 sys.path.insert(0,str(path))
 for x in ['openalex_api','kontrol_destegi']:sys.modules.pop(x,None)
 return AppTest.from_file(str(path/'app.py'),default_timeout=20).run()
works=json.loads((reviewed/'remzi_basar_yayinlar.json').read_text());raw=json.loads((reviewed/'remzi_basar_atiflar.json').read_text())
class Resp:
 status_code=200
 def __init__(self,d):self.d=d
 def raise_for_status(self):pass
 def json(self):return self.d
def get(url,params=None,**kw):
 params=params or {}
 if url.endswith('/authors'):return Resp({'results':[{'id':'https://openalex.org/A5007768129','display_name':'Remzi Başar','last_known_institutions':[{'display_name':'Duzce University'}],'works_count':18}]})
 if params.get('filter','').startswith('cites:'):
  k=params['filter'].split(':')[1]
  return Resp({'results':[{'id':r['atif_yapan_eser_id'],'display_name':r['atif_yapan_eser'],'doi':r['doi'],'publication_year':r['atif_yili'],'authorships':[]} for r in raw if r['hedef_yayin_id'].endswith('/'+k)]})
 if params.get('select')=='title':return Resp({'results':[{'title':works[0]['display_name']}]})
 return Resp({'results':works})
a=prepare(reviewed)
check('Kontrollü: açılış',not a.exception)
button(a,'Atıfları bul').click().run();check('Boş isim uyarısı',any('adını girin' in w.value for w in a.warning))
a.text_input[0].set_value('Remzi Başar');button(a,'Atıfları bul').click().run();check('Kayıtlı 18 yayın',len(a.checkbox)==18)
button(a,'Seçili yayınları analiz et').click().run();check('Seçim olmadan analiz uyarısı',any('en az bir yayın' in w.value for w in a.warning))
button(a,'Tümünü seç').click().run();button(a,'Seçili yayınları analiz et').click().run()
check('Tümü seçili / 2026 sonucu',len(a.session_state['results'])==12 and not a.exception)
check('CSV ve Excel indirme düğmeleri',len(a.get('download_button'))==2)
a.number_input[0].set_value(2025).run();check('Yıl değişince eski sonuç silinir',a.session_state['results'] is None)
button(a,'Seçili yayınları analiz et').click().run();check('2025 sonucu',len(a.session_state['results'])==5 and set(a.session_state['results']['Yıl'])=={2025})
seen=[]
for year in sorted(set(r['atif_yili'] for r in raw)):
 a.number_input[0].set_value(year).run();button(a,'Seçili yayınları analiz et').click().run();d=a.session_state['results']
 check(f'{year} yıl filtresi',len(d)==sum(r['atif_yili']==year for r in raw))
 if not d.empty:seen.extend(d.to_dict('records'))
check('25 aday tüm yıllarda',len(seen)==25)
check('19 elle doğrulandı / 6 incelenmeli',collections.Counter(x['Durum'] for x in seen)=={'Doğrulandı':19,'İncelenmeli':6})
check('Doğrulanmış 19 kaydın kanıt URLsi',sum(bool(x['Kanıt']) for x in seen)==19)
check('İncelenmeli kanıt doğrulaması yapılmış gibi gösterilmez',all(not x['Kanıt'] for x in seen if x['Durum']=='İncelenmeli'))
check('2 öz atıf',sum(x['Öz atıf']=='Evet' for x in seen)==2)
check('Aynı hedef-atıf çifti tekrarsız',len({(x['Atıf alan yayın ID'],x['Atıf yapan eser ID']) for x in seen})==25)
for excel_no,index in [(1,23),(3,21),(6,20)]:
 check(f'Excel {excel_no} ortak kayıt',any(x['Atıf yapan eser ID']==raw[index]['atif_yapan_eser_id'] and x['Durum']=='Doğrulandı' and x['Kanıt'] for x in seen))
button(a,'Seçimi temizle').click().run();check('Toplu seçim temizleme',all(not c.value for c in a.checkbox))
button(a,'Yeni arama').click().run();check('Yeni arama eski sonuçları kaldırır',not a.dataframe)
# Online mode uses real interface + mocked HTTP so flow tests are reproducible.
a=prepare(reviewed)
with patch('requests.get',side_effect=get):
 a.selectbox[0].select('Canlı OpenAlex').run();a.text_input[0].set_value('Remzi Başar');button(a,'Atıfları bul').click().run()
 check('Canlı akış / sahte HTTP: kişi ve yayın yükleme',len(a.checkbox)==18)
 button(a,'Tümünü seç').click().run();button(a,'Seçili yayınları analiz et').click().run()
 check('Canlı akış / sahte HTTP: filtre ve kanıt',len(a.session_state['results'])==12 and 'Kanıt' in a.session_state['results'])
with patch('requests.get',side_effect=ConnectionError('Test bağlantı hatası')):
 button(a,'Seçili yayınları analiz et').click().run()
 check('API hatası önceki sonucu temizler ve hata gösterir',a.session_state['results'] is None and bool(a.error))
check('Son durumda yakalanmamış uygulama hatası yok',not a.exception)
# PDF widget flow with a real existing evidence PDF.
a=prepare(reviewed)
pdfpath=ROOT/'ornekler/01_Kanit.pdf'
a.file_uploader[0].upload('01_Kanit.pdf',pdfpath.read_bytes(),'application/pdf').run()
button(a,"PDF'yi analiz et").click().run()
check('Gerçek PDF yükleme ve metin çıkarma',not a.exception and bool(a.text_area) and len(a.text_area[0].value)>100)
check('PDF metni otomatik doğrulama diye sunulmaz',any('henüz yapılmadı' in x.value for x in a.info))
a.file_uploader[0].clear().run()
a.file_uploader[0].upload('bozuk.pdf',b'not-a-pdf','application/pdf').run()
button(a,"PDF'yi analiz et").click().run()
check('Bozuk PDF hata mesajı',not a.exception and any('PDF analiz hatası' in x.value for x in a.error))
# Unknown manual title must not be mapped to an unrelated work.
a=prepare(reviewed)
a.text_input[0].set_value('Remzi Başar');button(a,'Atıfları bul').click().run()
a.text_input[1].set_value('Türkiye’deki YBS Bölümlerinin İş Piyasası Yetenek Talepleriyle Uyumu')
button(a,'Yayın ekle').click().run()
check('Bilinmeyen başlığa yanlış kayıt eklenmez',len(a.checkbox)==18 and any('bulunamadı' in x.value for x in a.warning))
# Actual online method boundary: different author's candidate must be rejected.
a.selectbox[0].select('Canlı OpenAlex').run()
with patch('requests.get',side_effect=get):
 button(a,'Atıfları bul').click().run()
wrong=Resp({'id':'https://openalex.org/W999999','title':'Yanlış yayın','publication_year':2026,'authorships':[{'author':{'id':'https://openalex.org/A999999'}}]})
with patch('requests.get',return_value=wrong):
 a.text_input[1].set_value('10.1234/wrong');button(a,'Yayın ekle').click().run()
 check('Başka yazarın DOI kaydı reddedilir',len(a.checkbox)==18 and any('Yazar kimliği' in x.value for x in a.warning))
(ROOT/'test_sonuclari.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2))
print('SUMMARY',sum(c['passed'] for c in checks),len(checks),flush=True)

assert all(c["passed"] for c in checks), "Başarısız kontroller var: test_sonuclari.json dosyasına bakın."
