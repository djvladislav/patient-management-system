from database_connection import create_connection



def calculate_insulin(hasta_id: int) -> dict:
    
    conn = create_connection()
    try:
        with conn.cursor() as cursor:
            
            cursor.execute("""
                SELECT deger FROM kan_sekeri_olcumleri
                WHERE hasta_id = %s 
                ORDER BY olcum_zamani DESC 
                LIMIT 5 
            """, (hasta_id,))
            
            olcumler = [row[0] for row in cursor.fetchall()]
            if not olcumler:
                return {"doz": 0, "uyari": "Ölçüm bulunamadı"}
            
            
            ortalama = sum(olcumler) / len(olcumler)
            
            if ortalama < 70:
                return {"doz": 0, "uyari": "ACİL - Hipoglisemi"}
            elif 70 <= ortalama <= 110:
                return {"doz": 0, "uyari": "Normal"}
            elif 111 <= ortalama <= 150:
                return {"doz": 1, "uyari": "Hafif Yüksek"}
            elif 151 <= ortalama <= 200:
                return {"doz": 2, "uyari": "Yüksek Risk"}
            else:
                return {"doz": 3, "uyari": "ACİL - Hiperglisemi"}
                
    finally:
        conn.close()