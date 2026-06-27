from pymongo import MongoClient
import os

# Kodun artık senin bilgisayardaki o uzun adrese değil,
# Render'ın içine sakladığımız o gizli "MONGO_URL" adresine bakacak.
MONGO_URL = os.environ.get("MONGO_URL")

# MongoDB'ye bağlantı açıyoruz
client = MongoClient(MONGO_URL)

# 'catering_db' adında bir veritabanı oluşturuyoruz
db = client["catering_db"]

# 1. Siparişlerin tutulacağı tablo
siparisler_koleksiyonu = db["siparisler"]

# 2. Adminin oluşturacağı menü kartlarının tutulacağı tablo
menuler_koleksiyonu = db["menuler"]

# 3. Slider ve 'Biz Kimiz' fotoğraflarının tutulacağı tablo
fotograflar_koleksiyonu = db["fotograflar"]

# 4. YENİ: Dinamik site ayarlarının (Hakkımda yazısı, Telefon) tutulacağı tablo
ayarlar_koleksiyonu = db["ayarlar"]
