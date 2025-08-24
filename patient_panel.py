import tkinter as tk
from tkinter import ttk, messagebox
import database_connection
from PIL import Image, ImageTk
from io import BytesIO
from datetime import datetime
from datetime import timedelta
from blood_sugar_entry import BloodSugarMeasurement
from alerts import check_blood_sugar
import os



class PatientPanel:
    def __init__(self, root, hasta_id):
        self.root = root
        self.hasta_id = hasta_id
        self.root.title("Hasta Paneli")
        self.root.geometry("800x600")
        self.blood_sugar_measurement = BloodSugarMeasurement(self.root, self.hasta_id)
        self.conn = database_connection.create_connection()
        self.load_profile()
        self.create_widgets()

    
    def load_profile(self):
     conn = database_connection.create_connection()  
     try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ad_soyad, profil_fotografi, dogum_tarihi, cinsiyet 
            FROM hastalar 
            WHERE hasta_id = %s
        """, (self.hasta_id,))
        
        self.ad_soyad, self.profil_fotografi, self.dogum_tarihi, self.cinsiyet = cursor.fetchone()
     finally:
        cursor.close()  # Cursor'ı kapat
        conn.close()    # Bağlantıyı kapat
    def create_widgets(self):
        # profile info FRAME
        profile_frame = ttk.LabelFrame(self.root, text="Profil Bilgileri")
        profile_frame.pack(pady=10, padx=10, fill="x")
        
        # Profil pic
        if self.profil_fotografi and os.path.exists(self.profil_fotografi):
         image = Image.open(self.profil_fotografi)
         image = image.resize((100, 100))  
         photo = ImageTk.PhotoImage(image)

         image_label = tk.Label(profile_frame, image=photo)
         image_label.image = photo  
         image_label.pack(padx=20)
        else:
         tk.Label(profile_frame, text="Profil fotoğrafı yok").pack(padx=20)
        
        # INFO
        info_frame = ttk.Frame(profile_frame)
        info_frame.pack(side="left", fill="both", expand=True)
        
        tk.Label(info_frame, text=f"Ad Soyad: {self.ad_soyad}", font=("Arial", 12)).pack(anchor="w")
        tk.Label(info_frame, text=f"Doğum Tarihi: {self.dogum_tarihi}").pack(anchor="w")
        tk.Label(info_frame, text=f"Cinsiyet: {self.cinsiyet}").pack(anchor="w")
        
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)

        #  all da buttons
        tk.Button(
            button_frame, 
            text="Kan Şekeri Ölçümü Ekle", 
            command=self.blood_sugar_measurement.add_blood_sugar,
            bg="#2196F3",
            fg="white",
            width=20
        ).pack(side="left", padx=5)

            
        tk.Button(
        button_frame,
        text="Günlük Sonuç Göster",
        command=self.show_results,
        bg="#2196F3",
        fg="white",
        width=20
        ).pack(side="left", padx=5)

        tk.Button(
    button_frame,
    text="Günlük Takip",
    command=self.daily_tracking_window,
    bg="#4CAF50",
    fg="white",
    width=20
).pack(side="left", padx=5)
        
        tk.Button(
    button_frame,
    text="Geçmiş Ölçümler",
    command=self.show_history,
    bg="#4CAF50",
    fg="white",
    width=20
).pack(side="left", padx=5)
        
        tk.Button(
    button_frame,
    text="İnsülin Geçmişi",
    command=self.show_insulin_history,
    bg="#4CAF50",
    fg="white",
    width=20
).pack(side="left", padx=5)
        

    def show_results(self):
     sonuc = check_blood_sugar(self.hasta_id)
     uyari = sonuc.get("uyari") or "Uyarı yok."
     seviye = sonuc.get("seviye") or "bilinmiyor"

     cursor = self.conn.cursor()
     bugun_baslangic = datetime.combine(datetime.today(), datetime.min.time())
     bugun_bitis = datetime.combine(datetime.today(), datetime.max.time())
     cursor.execute("""
        SELECT olcum_id, olcum_zamani, deger, olcum_tipi FROM kan_sekeri_olcumleri 
        WHERE hasta_id = %s AND olcum_zamani BETWEEN %s AND %s
        ORDER BY olcum_zamani ASC
     """, (self.hasta_id, bugun_baslangic, bugun_bitis))
     olcumler = cursor.fetchall()

     if not olcumler:
        messagebox.showinfo("Günlük Ölçümler", "Bugün için kan şekeri ölçümü bulunmamaktadır.")
        return

     ortalama = sum(d[2] for d in olcumler) / len(olcumler)

     if ortalama < 70:
        insulin_uyari = f"Hipoglisemi riski! Ortalama şeker: {ortalama:.1f}. İnsülin dozu önerilmez."
        doz = 0
     elif 70 <= ortalama <= 110:
        insulin_uyari = f"Ortalama şeker {ortalama:.1f} (normal). İnsülin dozu önerisi yok."
        doz = 0
     elif 111 <= ortalama <= 150:
        insulin_uyari = f"Ortalama şeker {ortalama:.1f} (orta yüksek). Yaklaşık insülin dozu önerilir: 1 ml."
        doz = 1
     elif 151 <= ortalama <= 200:
        insulin_uyari = f"Ortalama şeker {ortalama:.1f} (yüksek). Yaklaşık insülin dozu önerilir: 2 ml."
        doz = 2
     else:
        insulin_uyari = f"Ortalama şeker {ortalama:.1f} (çok yüksek). Yaklaşık insülin dozu önerilir: 3 ml."
        doz = 3

    
     for olcum_id, _, _, _ in olcumler:
        cursor.execute("""
            UPDATE kan_sekeri_olcumleri SET insulin_dozu = %s WHERE olcum_id = %s
        """, (doz, olcum_id))
     self.conn.commit()

     olcum_metni = "Bugünkü Kan Şekeri Ölçümleri:\n"
     for _, olcum_zamani, deger, olcum_tipi in olcumler:
        zaman_str = olcum_zamani.strftime("%H:%M")
        olcum_metni += f"- {olcum_tipi.capitalize()} ({zaman_str}): {deger} mg/dL\n"

     top = tk.Toplevel(self.root)
     top.title("Kan Şekeri Sonuçları")
     top.geometry("400x400")

     lbl_uyari = tk.Label(top, text=f"Uyarı Seviyesi: {seviye.upper()}", font=("Arial", 14, "bold"))
     lbl_uyari.pack(pady=10)

     txt_uyari = tk.Text(top, height=6, width=50)
     txt_uyari.pack(padx=10)
     txt_uyari.insert("1.0", uyari)
     txt_uyari.config(state="disabled")

     lbl_olcum = tk.Label(top, text=olcum_metni, justify="left", font=("Arial", 11))
     lbl_olcum.pack(pady=10)

     lbl_insulin = tk.Label(top, text=insulin_uyari, fg="red", font=("Arial", 12, "bold"))
     lbl_insulin.pack(pady=10)

     ttk.Button(top, text="Kapat", command=top.destroy).pack(pady=10)

    def show_insulin_history(self):
     """
     Son 3 gün için günlük uygulanan toplam insülin dozlarını gösterir.
     """
     conn = database_connection.create_connection()
     try:
        cursor = conn.cursor()
        
        today = datetime.today().date()
        three_days_ago = today - timedelta(days=6)  

        #ftech daily insulin dose
        cursor.execute("""
            SELECT DATE(olcum_zamani) as tarih, MAX(insulin_dozu) as insulin_dozu
            FROM kan_sekeri_olcumleri
            WHERE hasta_id = %s AND olcum_zamani BETWEEN %s AND %s
            GROUP BY DATE(olcum_zamani)
            ORDER BY tarih ASC
        """, (self.hasta_id, three_days_ago, today))

        results = cursor.fetchall()

        if not results:
            messagebox.showinfo("Bilgi", "Son 3 gün için insülin uygulaması bulunmamaktadır.")
            return

       
        metin = "Son 3 Günlük Uygulanan İnsülin Dozları:\n\n"
        for tarih, toplam in results:
            metin += f"{tarih.strftime('%d-%m-%Y')}: {toplam} ml\n"

        
        top = tk.Toplevel(self.root)
        top.title("Uygulanan İnsülin Geçmişi")
        top.geometry("300x250")

        label = tk.Label(top, text=metin, justify="left", font=("Arial", 12))
        label.pack(padx=10, pady=10)

        ttk.Button(top, text="Kapat", command=top.destroy).pack(pady=10)

     finally:
        cursor.close()
        conn.close()

    def show_history(self):
     cursor = self.conn.cursor()
     cursor.execute("""
        SELECT olcum_zamani, deger, olcum_tipi
        FROM kan_sekeri_olcumleri
        WHERE hasta_id = %s
        ORDER BY olcum_zamani DESC
        LIMIT 20
     """, (self.hasta_id,))
     results = cursor.fetchall()
     cursor.close()

     if not results:
        messagebox.showinfo("Geçmiş Ölçümler", "Hiç kayıt bulunamadı.")
        return

     history_win = tk.Toplevel(self.root)
     history_win.title("Son 20 Kan Şekeri Ölçümü")

     for idx, (zaman, deger, tip) in enumerate(results):
        label = tk.Label(history_win, text=f"{idx+1}. {zaman.strftime('%Y-%m-%d %H:%M')} - {tip.capitalize()}: {deger} mg/dL")
        label.pack(anchor="w", padx=10)

    def daily_tracking_window(self):
     window = tk.Toplevel()
     window.title("Günlük Takip")
     window.geometry("400x500")

    
     tk.Label(window, text="Diyete Uydunuz mu?").pack(pady=5)
     diyet_var = tk.BooleanVar()
     tk.Checkbutton(window, variable=diyet_var).pack()

    
     tk.Label(window, text="Egzersiz Yaptınız mı?").pack(pady=5)
     egzersiz_var = tk.BooleanVar()
     tk.Checkbutton(window, variable=egzersiz_var).pack()

    
     tk.Label(window, text="Bugün Hissettiğiniz Belirtiler (Birden fazla seçebilirsiniz):").pack(pady=5)
     belirtiler_frame = ttk.Frame(window)
     belirtiler_frame.pack(pady=5)

    
     belirtiler_listesi = ["Yorgunluk", "Nöropati", "Polifaji", "Polidipsi", "Bulanık Görme", "Yavaş İyileşme", "Kilo Kaybı", "Polüri"]
     belirtiler_vars = {belirti: tk.BooleanVar() for belirti in belirtiler_listesi}

    
     for i, belirti in enumerate(belirtiler_listesi):
        tk.Checkbutton(belirtiler_frame, text=belirti, variable=belirtiler_vars[belirti]).grid(row=i//2, column=i%2, sticky="w", padx=5)

    
     tk.Label(window, text="Diğer Belirtiler (Varsa, virgülle ayırarak yazın):").pack(pady=5)
     diger_belirtiler_entry = tk.Entry(window, width=40)
     diger_belirtiler_entry.pack()

    
     tk.Label(window, text="Yorum:").pack(pady=5)
     yorum_entry = tk.Text(window, height=3, width=40)
     yorum_entry.pack()

    
     tk.Button(window, text="Kaydet", 
              command=lambda: self.save_tracking(
                  diyet_var.get(),
                  egzersiz_var.get(),
                  yorum_entry.get("1.0", tk.END).strip(),
                  belirtiler_vars,
                  diger_belirtiler_entry.get()
              )).pack(pady=10)

    def save_tracking(self, diyet_uygun, egzersiz_yapildi, yorum, belirtiler_vars, diger_belirtiler):
     
     conn = database_connection.create_connection()
     try:
        with conn.cursor() as cursor:
            
            cursor.execute("""
                INSERT INTO hasta_takip_loglari (
                    hasta_id, diyet_uygun, egzersiz_yapildi, yorum
                ) VALUES (%s, %s, %s, %s)
                ON CONFLICT (hasta_id, tarih) DO UPDATE SET
                    diyet_uygun = EXCLUDED.diyet_uygun,
                    egzersiz_yapildi = EXCLUDED.egzersiz_yapildi,
                    yorum = EXCLUDED.yorum
            """, (self.hasta_id, diyet_uygun, egzersiz_yapildi, yorum))

            
            for belirti, var in belirtiler_vars.items():
                if var.get():  
                    cursor.execute("""
                        INSERT INTO hasta_belirtileri (hasta_id, belirti_adi)
                        VALUES (%s, %s)
                    """, (self.hasta_id, belirti))

            
            if diger_belirtiler.strip():
                diger_belirtiler_listesi = [b.strip() for b in diger_belirtiler.split(",") if b.strip()]
                for belirti in diger_belirtiler_listesi:
                    cursor.execute("""
                        INSERT INTO hasta_belirtileri (hasta_id, belirti_adi)
                        VALUES (%s, %s)
                    """, (self.hasta_id, belirti))

            conn.commit()
            messagebox.showinfo("Başarılı", "Günlük takip ve belirtiler kaydedildi!")
     except Exception as e:
        messagebox.showerror("Hata", f"Kayıt sırasında hata: {str(e)}")
     finally:
        conn.close()
