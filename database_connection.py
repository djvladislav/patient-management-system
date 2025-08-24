import psycopg2
from psycopg2 import OperationalError

from passlib.hash import bcrypt  # veya pbkdf2_sha256

def hash_password(password):
    
    return bcrypt.hash(password)

def verify_password(plain_password, hashed_password):
    
    return bcrypt.verify(plain_password, hashed_password)

def create_connection():
    try:
        conn = psycopg2.connect(
            dbname="hastane_veritabani",
            user="postgres",
            password="beratdayi33",
            host="localhost"
        )
        print("PostgreSQL bağlantısı başarılı!")
        return conn
    except OperationalError as e:
        print(f"Hata: '{e}'")
        return None

def create_tables(conn):
    try:
        cursor = conn.cursor()  
        
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS doktorlar (
            doktor_id SERIAL PRIMARY KEY,
            tc_no VARCHAR(11) UNIQUE NOT NULL,
            ad_soyad VARCHAR(100) NOT NULL,
            sifre VARCHAR(50) NOT NULL,
            email VARCHAR(100),
            cinsiyet CHAR(1),
            dogum_tarihi DATE,
            profil_fotografi VARCHAR(255)
        )""")
        
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS hastalar (
            hasta_id SERIAL PRIMARY KEY,
            tc_no VARCHAR(11) UNIQUE NOT NULL,
            ad_soyad VARCHAR(100) NOT NULL,
            sifre VARCHAR(50) NOT NULL,
            email VARCHAR(100),
            cinsiyet CHAR(1),
            dogum_tarihi DATE,
            profil_fotografi TEXT ,
            doktor_id INTEGER REFERENCES doktorlar(doktor_id)
        )""")
        
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS kan_sekeri_olcumleri (
            olcum_id SERIAL PRIMARY KEY,
            hasta_id INTEGER REFERENCES hastalar(hasta_id),
            olcum_zamani TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            deger INTEGER NOT NULL,
            olcum_tipi VARCHAR(20)  -- Sabah, Öğle, Akşam vb.
        )""")


               
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS uyarilar (
          uyari_id SERIAL PRIMARY KEY,
           hasta_id INTEGER REFERENCES hastalar(hasta_id),
          baslik VARCHAR(100) NOT NULL,
         mesaj TEXT NOT NULL,
          olusturulma_zamani TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
         okundu BOOLEAN DEFAULT FALSE
         )""")


        cursor.execute("""
        CREATE TABLE IF NOT EXISTS hasta_belirtileri (
    kayit_id SERIAL PRIMARY KEY,
    hasta_id INTEGER REFERENCES hastalar(hasta_id),
    belirti_adi VARCHAR(50) NOT NULL,
    kayit_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

        
        cursor.execute("""
CREATE TABLE IF NOT EXISTS diyet_tipleri (
    diyet_id SERIAL PRIMARY KEY,
    ad VARCHAR(50) NOT NULL UNIQUE,
    aciklama TEXT NOT NULL
)""")


        cursor.execute("""
CREATE TABLE IF NOT EXISTS egzersiz_tipleri (
    egzersiz_id SERIAL PRIMARY KEY,
    ad VARCHAR(50) NOT NULL UNIQUE,
    aciklama TEXT NOT NULL
)""")


        cursor.execute("""
CREATE TABLE IF NOT EXISTS hasta_planlari (
    plan_id SERIAL PRIMARY KEY,
    hasta_id INTEGER NOT NULL REFERENCES hastalar(hasta_id),
    doktor_id INTEGER NOT NULL REFERENCES doktorlar(doktor_id),
    diyet_id INTEGER REFERENCES diyet_tipleri(diyet_id),
    egzersiz_id INTEGER REFERENCES egzersiz_tipleri(egzersiz_id),
    baslangic_tarihi DATE NOT NULL,
    bitis_tarihi DATE,
    aktif BOOLEAN DEFAULT TRUE
)""")

        cursor.execute("""
                       CREATE UNIQUE INDEX unique_active_plan_per_patient ON hasta_planlari (hasta_id) WHERE aktif;""")

        cursor.execute("""
CREATE TABLE IF NOT EXISTS hasta_takip_loglari (
    log_id SERIAL PRIMARY KEY,
    hasta_id INTEGER NOT NULL REFERENCES hastalar(hasta_id),
    tarih DATE NOT NULL DEFAULT CURRENT_DATE,
    diyet_uygun BOOLEAN,
    egzersiz_yapildi BOOLEAN,
    yorum TEXT,
    UNIQUE(hasta_id, tarih)
)""")
        
        conn.commit()
        print("Tablolar başarıyla oluşturuldu!")
    except Exception as e:
        print(f"Tablo oluşturma hatası: {e}")
    finally:
        if conn:
            cursor.close()

# Test
if __name__ == "__main__":
    conn = create_connection()
    if conn:
        create_tables(conn)
        conn.close()