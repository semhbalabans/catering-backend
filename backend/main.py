from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId  # MongoDB ID'lerini işlemek için gerekli
import os

# Cloudinary importları
import cloudinary
import cloudinary.uploader
import cloudinary.api

# Model ve Veritabanı importlarımız (Yeni eklenen tablolar ve şemalar dahil edildi)
from backend.models import SiparisSemasi, MenuKartiSemasi, AyarlarSemasi
from backend.database import siparisler_koleksiyonu, menuler_koleksiyonu, fotograflar_koleksiyonu, ayarlar_koleksiyonu

app = FastAPI(title="Catering API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CLOUDINARY AYARLARI ---
# Render üzerindeki Environment Variables'dan (Çevre Değişkenleri) şifreleri alıyoruz
cloudinary.config(
  cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME"),
  api_key = os.environ.get("CLOUDINARY_API_KEY"),
  api_secret = os.environ.get("CLOUDINARY_API_SECRET"),
  secure = True
)


@app.get("/")
def read_root():
    return {"mesaj": "Catering Backend Sunucusu Başarıyla Çalışıyor!"}


# ==========================================
# 1. SİPARİŞ YÖNETİMİ
# ==========================================

@app.post("/siparisler")
def siparis_olustur(siparis: SiparisSemasi):
    yeni_siparis = siparis.model_dump()
    sonuc = siparisler_koleksiyonu.insert_one(yeni_siparis)
    return {"durum": "Başarılı", "mesaj": "Sipariş alındı", "siparis_id": str(sonuc.inserted_id)}


@app.get("/admin/siparisler")
def siparisleri_listele():
    tum_siparisler = []
    for siparis in siparisler_koleksiyonu.find():
        siparis["id"] = str(siparis["_id"])
        del siparis["_id"]
        tum_siparisler.append(siparis)
    return tum_siparisler


@app.delete("/admin/siparisler/{siparis_id}")
def siparis_sil(siparis_id: str):
    try:
        sonuc = siparisler_koleksiyonu.delete_one({"_id": ObjectId(siparis_id)})
        if sonuc.deleted_count == 1:
            return {"durum": "Başarılı", "mesaj": "Sipariş silindi."}
        raise HTTPException(status_code=404, detail="Sipariş bulunamadı.")
    except Exception:
        raise HTTPException(status_code=400, detail="Geçersiz format.")


@app.put("/admin/siparisler/{siparis_id}")
def siparis_duzenle(siparis_id: str, guncel_veri: SiparisSemasi):
    try:
        yenilenen_veri = guncel_veri.model_dump()
        sonuc = siparisler_koleksiyonu.update_one(
            {"_id": ObjectId(siparis_id)},
            {"$set": yenilenen_veri}
        )
        if sonuc.matched_count == 1:
            return {"durum": "Başarılı", "mesaj": "Sipariş güncellendi."}
        raise HTTPException(status_code=404, detail="Sipariş bulunamadı.")
    except Exception:
        raise HTTPException(status_code=400, detail="Geçersiz format.")


# ==========================================
# 2. MENÜ YÖNETİMİ
# ==========================================

@app.post("/admin/menuler")
def menu_ekle(menu: MenuKartiSemasi):
    yeni_menu = menu.model_dump()
    sonuc = menuler_koleksiyonu.insert_one(yeni_menu)
    return {"durum": "Başarılı", "mesaj": "Menü başarıyla eklendi.", "menu_id": str(sonuc.inserted_id)}


@app.get("/menuler")
def menuleri_getir():
    tum_menuler = []
    for menu in menuler_koleksiyonu.find():
        menu["id"] = str(menu["_id"])
        del menu["_id"]
        tum_menuler.append(menu)
    return tum_menuler


@app.delete("/admin/menuler/{menu_id}")
def menu_sil(menu_id: str):
    try:
        sonuc = menuler_koleksiyonu.delete_one({"_id": ObjectId(menu_id)})
        if sonuc.deleted_count == 1:
            return {"durum": "Başarılı", "mesaj": "Menü silindi."}
        raise HTTPException(status_code=404, detail="Menü bulunamadı.")
    except Exception:
        raise HTTPException(status_code=400, detail="Geçersiz format.")


# ==========================================
# 3. GALERİ / FOTOĞRAF YÖNETİMİ (CLOUDINARY ENTEGRELİ)
# ==========================================

@app.post("/admin/fotograflar")
def fotograf_yukle(bolum: str = Form(...), sira: int = Form(1), dosya: UploadFile = File(...)):
    # 1. KONTROL: Eğer slider ise, bu sıra numarasının dolu olup olmadığına bak
    if bolum == "slider":
        mevcut = fotograflar_koleksiyonu.find_one({"bolum": "slider", "sira": sira})
        if mevcut:
            raise HTTPException(status_code=400, detail=f"{sira}. sıra dolu! Lütfen başka numara seçin.")

    # 2. KONTROL: Eğer 'biz_kimiz' ise, eski fotoğrafı bul ve hem DB'den hem Cloudinary'den sil
    elif bolum == "biz_kimiz":
        eski = fotograflar_koleksiyonu.find_one({"bolum": "biz_kimiz"})
        if eski:
            if "public_id" in eski:
                cloudinary.uploader.destroy(eski["public_id"])
            fotograflar_koleksiyonu.delete_one({"_id": eski["_id"]})
        sira = 1  # Biz kimiz fotoğrafının sırası her zaman 1'dir

    try:
        # Dosyayı Cloudinary'ye yüklüyoruz
        upload_result = cloudinary.uploader.upload(dosya.file, folder="catering_app")
        
        foto_veri = {
            "dosya_adi": dosya.filename,
            "bolum": bolum,
            "sira": sira,
            "url": upload_result.get("secure_url"), # Cloudinary'den dönen güvenli (https) tam link
            "public_id": upload_result.get("public_id") # İleride silmek için gereken Cloudinary ID'si
        }

        sonuc = fotograflar_koleksiyonu.insert_one(foto_veri)
        return {"durum": "Başarılı", "mesaj": "Fotoğraf başarıyla yüklendi", "foto_id": str(sonuc.inserted_id)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fotoğraf yüklenemedi: {str(e)}")


@app.get("/fotograflar")
def fotograflari_getir():
    tum_fotolar = []
    # Veritabanından çekerken 'sira' numarasına göre küçükten büyüğe sıralı (1) getiriyoruz
    for foto in fotograflar_koleksiyonu.find().sort("sira", 1):
        foto["id"] = str(foto["_id"])
        del foto["_id"]
        tum_fotolar.append(foto)
    return tum_fotolar


@app.delete("/admin/fotograflar/{foto_id}")
def fotograf_sil(foto_id: str):
    try:
        foto = fotograflar_koleksiyonu.find_one({"_id": ObjectId(foto_id)})
        if not foto:
            raise HTTPException(status_code=404, detail="Fotoğraf bulunamadı.")

        # 1. Önce Cloudinary sunucularından resmi siliyoruz
        if "public_id" in foto:
            cloudinary.uploader.destroy(foto["public_id"])

        # 2. Sonra veritabanındaki kaydını siliyoruz
        fotograflar_koleksiyonu.delete_one({"_id": ObjectId(foto_id)})

        return {"durum": "Başarılı", "mesaj": "Fotoğraf tamamen silindi."}
    except Exception:
        raise HTTPException(status_code=400, detail="Geçersiz format.")

# ==========================================
# 4. SİTE AYARLARI (DİNAMİK METİNLER)
# ==========================================

@app.get("/ayarlar")
def ayarlar_getir():
    ayar = ayarlar_koleksiyonu.find_one({})
    if ayar:
        ayar["id"] = str(ayar["_id"])
        del ayar["_id"]
        return ayar
    # Eğer henüz ayar girilmemişse boş site çökmesin diye varsayılan döner
    return {
        "hakkimda_tr": "Lütfen admin panelinden hakkımda yazısını güncelleyin.",
        "hakkimda_en": "Please update about text from admin panel.",
        "hakkimda_nl": "Werk over mij-tekst bij via beheerderspaneel.",
        "telefon": "+31 6 00000000"
    }

@app.put("/admin/ayarlar")
def ayarlar_guncelle(guncel_ayarlar: AyarlarSemasi):
    # Veritabanında her zaman tek 1 satır ayar kaydı olacağı için filtreyi boş {} bırakıyoruz
    ayarlar_koleksiyonu.update_one(
        {}, 
        {"$set": guncel_ayarlar.model_dump()},
        upsert=True # Kayıt yoksa yeni oluşturur, varsa üstüne yazar (yer kaplamaz)
    )
    return {"durum": "Başarılı", "mesaj": "Ayarlar başarıyla güncellendi."}
