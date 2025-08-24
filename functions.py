from tkinter import messagebox
import os
import smtplib
from email.mime.text import MIMEText
import database_connection
import matplotlib.pyplot as plt
from datetime import datetime

conn = database_connection.create_connection()
if conn:
        cursor = conn.cursor()



def send_credentials(email, tc_no, password):
    """Hastaya giriş bilgilerini e-posta ile gönderir"""
    try:
        msg = MIMEText(f"""
        Diyabet Takip Sistemine Giriş Bilgileriniz:
        
        Kullanıcı Adı (TC Kimlik No): {tc_no}
        Şifre: {password}
        
        Giriş Yapmak İçin Uygulamamızı İndirin!
        """)
        
        msg['Subject'] = 'Diyabet Takip Sistemi - Giriş Bilgileriniz'
        msg['From'] = 'noreply@diyabettakipsistemi.com'
        msg['To'] = email
        
        # SMTP ayarları (örnek)
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login('djvladislav24@gmail.com', 'kkwm kstb doho zfll')
            server.send_message(msg)
    except Exception as e:
        print(f"E-posta gönderilemedi: {e}")

def calculate_insulin(hasta_id):
    """5 ölçümün ortalamasına göre insülin dozu hesaplar"""
    cursor.execute("""
        SELECT deger FROM kan_sekeri_olcumleri 
        WHERE hasta_id = %s 
        ORDER BY olcum_zamani DESC LIMIT 5
    """, (hasta_id,))
    
    olcumler = [row[0] for row in cursor.fetchall()]
    if not olcumler:
        return None

    ortalama = sum(olcumler) / len(olcumler)
    
    if ortalama < 70:
        return {"doz": 0, "aciklama": "Hipoglisemi - İnsülin verilmez"}
    elif 70 <= ortalama <= 110:
        return {"doz": 0, "aciklama": "Normal seviye"}
    elif 111 <= ortalama <= 150:
        return {"doz": 1, "aciklama": "Hafif yüksek"}
    elif 151 <= ortalama <= 200:
        return {"doz": 2, "aciklama": "Yüksek seviye"}
    else:
        return {"doz": 3, "aciklama": "Acil müdahale gerekli"}    
 

def mark_as_read(uyari_id):
    """Uyarıyı okundu olarak işaretler"""
    cursor.execute("""
        UPDATE uyarilar SET okundu = TRUE 
        WHERE uyari_id = %s
    """, (uyari_id,))    

def olcum_tipini_belirle():
    saat = datetime.now().hour

    if 5 <= saat < 10:
        return "sabah"
    elif 10 <= saat < 14:
        return "oglen"
    elif 14 <= saat < 17:
        return "ikindi"
    elif 17 <= saat < 21:
        return "aksam"
    else:
        return "gece"