from pydantic import BaseModel
from typing import List, Optional

# 1. Sipariş Formu Yapısı
class SiparisSemasi(BaseModel):
    isim_soyisim: str
    telefon: str
    eposta: str
    adres: str
    siparis_icerigi: str

# 2. YENİ: Dinamik Menü Kartı Yapısı (3 Dilde)
class MenuKartiSemasi(BaseModel):
    # Kart Başlıkları
    baslik_tr: str
    baslik_en: str
    baslik_nl: str

    # Kart İçerikleri (Yemeklerin listesi, örn: ["Bruschetta", "Kiş"])
    icerik_tr: List[str]
    icerik_en: List[str]
    icerik_nl: List[str]

# 3. YENİ: Fotoğraf Verisi Yapısı
class FotografSiraSemasi(BaseModel):
    bolum: str  # Fotoğrafın yeri (Örn: "slider" veya "biz_kimiz")
    sira: int  # Slider'daki gösterim sırası (1, 2, 3 vb.)

class AyarlarSemasi(BaseModel):
    ana_baslik_tr: str
    ana_baslik_en: str
    ana_baslik_nl: str
    alt_baslik_tr: str
    alt_baslik_en: str
    alt_baslik_nl: str
    hakkimda_tr: str
    hakkimda_en: str
    hakkimda_nl: str
    telefon: str
