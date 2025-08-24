#adıüstünde
import database_connection
from datetime import datetime


import database_connection
from datetime import datetime

def check_blood_sugar(hasta_id: int) -> dict:
   
    conn = database_connection.create_connection()
    try:
        with conn.cursor() as cursor:
            
            cursor.execute("""
                SELECT deger FROM kan_sekeri_olcumleri
                WHERE hasta_id = %s
                ORDER BY olcum_zamani DESC
                LIMIT 5
            """, (hasta_id,))

            olcumler = cursor.fetchall()
            degerler = [d[0] for d in olcumler if d[0] is not None]

            mesajlar = []
            uyari_mesaji = None
            seviye = None

            if len(degerler) == 0:
                
                return {"uyari": None, "seviye": None}
            if len(degerler) < 5:
                mesajlar.append("Ölçüm eksik! Ortalama alınırken bu ölçüm hesaba katılmadı.")
            if len(degerler) <= 3:
                mesajlar.append("Yetersiz veri! Ortalama hesaplaması güvenilir değildir.")

            
            ortalama = sum(degerler) / len(degerler)

            
            if ortalama < 70:
                mesajlar.append(f"ACİL - Ortalama Hipoglisemi ({ortalama:.1f} mg/dL)")
                seviye = "acil"
            elif ortalama > 200:
                mesajlar.append(f"ACİL - Ortalama Hiperglisemi ({ortalama:.1f} mg/dL)")
                seviye = "acil"
            elif ortalama > 150:
                mesajlar.append(f"Yüksek Şeker ({ortalama:.1f} mg/dL)")
                seviye = "uyari"
            else:
                seviye = "normal"

            uyari_mesaji = "\n".join(mesajlar) if mesajlar else None

            
            if seviye in ("acil", "uyari"):
                cursor.execute("""
                    INSERT INTO uyarilar 
                    (hasta_id, baslik, mesaj, okundu)
                    VALUES (%s, %s, %s, FALSE)
                """, (hasta_id, "Kan Şekeri Uyarısı", uyari_mesaji))
                conn.commit()

            return {"uyari": uyari_mesaji, "seviye": seviye}

    finally:
        conn.close()


def get_doctor_alerts(doktor_id: int) -> list:
    
    conn = database_connection.create_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT u.uyari_id, h.ad_soyad, u.mesaj, u.olusturulma_zamani 
                FROM uyarilar u
                JOIN hastalar h ON u.hasta_id = h.hasta_id
                WHERE h.doktor_id = %s AND u.okundu = FALSE
                ORDER BY u.olusturulma_zamani DESC
                LIMIT 10
            """, (doktor_id,))
            
            results = cursor.fetchall()
            return [
                {
                    "uyari_id": row[0],
                    "hasta_adi": row[1],
                    "mesaj": row[2],
                    "tarih": row[3].strftime("%d.%m.%Y %H:%M")
                } 
                for row in results
            ]
    finally:
        conn.close()

