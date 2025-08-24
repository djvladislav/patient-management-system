import tkinter as tk
import database_connection
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.dates import DateFormatter
from tkcalendar import DateEntry
from PIL import Image, ImageTk
import os

class PatientDetailsWindow:
    def __init__(self, parent, hasta_id):
        self.window = tk.Toplevel(parent)
        self.window.title("Hasta Detayları")
        self.window.geometry("800x600")
        self.window.protocol("WM_DELETE_WINDOW", self.window.destroy)  # Bu satır önemli!
        
        self.hasta_id = hasta_id
        self.conn = database_connection.create_connection()
        self.build_ui()

    

    def build_ui(self):
        cursor = self.conn.cursor()
        
        # Hasta bilgilerini al
        cursor.execute("""
            SELECT ad_soyad, tc_no, email, dogum_tarihi, cinsiyet, profil_fotografi
            FROM hastalar WHERE hasta_id = %s
        """, (self.hasta_id,))
        ad, tc, email, dogum, cinsiyet, profil_fotografi = cursor.fetchone()

        # Üst bölüm - bilgiler
        frame_info = tk.Frame(self.window)
        frame_info.pack(pady=10)

        tk.Label(frame_info, text=f"Ad Soyad: {ad}", font=("Arial", 12)).grid(row=0, column=0, sticky='w')
        tk.Label(frame_info, text=f"TC No: {tc}").grid(row=1, column=0, sticky='w')
        tk.Label(frame_info, text=f"E-posta: {email}").grid(row=2, column=0, sticky='w')
        tk.Label(frame_info, text=f"Doğum Tarihi: {dogum}").grid(row=3, column=0, sticky='w')
        tk.Label(frame_info, text=f"Cinsiyet: {cinsiyet}").grid(row=4, column=0, sticky='w')

        # Sağ tarafa profil fotoğrafı
        if profil_fotografi and os.path.exists(profil_fotografi):
         image = Image.open(profil_fotografi)
         image = image.resize((100, 100))  # Fotoğraf boyutu ayarlanıyor
         photo = ImageTk.PhotoImage(image)

         image_label = tk.Label(frame_info, image=photo)
         image_label.image = photo  # Referansı kaybetmemek için
         image_label.grid(row=0, column=1, rowspan=5, padx=20)
        else:
         tk.Label(frame_info, text="Profil fotoğrafı yok").grid(row=0, column=1, rowspan=5, padx=20)



        # Kan şekeri ölçümleri (son 7 gün)
        cursor.execute("""
            SELECT olcum_zamani, deger FROM kan_sekeri_olcumleri 
            WHERE hasta_id = %s ORDER BY olcum_zamani DESC LIMIT 20
        """, (self.hasta_id,))
        olcumler = cursor.fetchall()
        if olcumler:
            tarih, degerler = zip(*olcumler)
            fig, ax = plt.subplots(figsize=(6,3))
            ax.plot(tarih[::-1], degerler[::-1], marker='o', color='blue')
            ax.set_title("Kan Şekeri Ölçümleri")
            ax.set_ylabel("mg/dL")
            # Tarih formatını belirle
            formatter = DateFormatter("%d.%m.%Y %H:%M")
            for label in ax.get_xticklabels():
             label.set_fontsize(8)  # Buradaki sayıyı küçülterek yazıyı küçültürsün
            ax.xaxis.set_major_formatter(formatter)
            canvas = FigureCanvasTkAgg(fig, master=self.window)
            canvas.get_tk_widget().pack(pady=10)
            canvas.draw()

        # Son belirtiler
        cursor.execute("""
            SELECT belirti_adi, kayit_tarihi FROM hasta_belirtileri 
            WHERE hasta_id = %s ORDER BY kayit_tarihi DESC LIMIT 5
        """, (self.hasta_id,))
        belirtiler = cursor.fetchall()
        if belirtiler:
            tk.Label(self.window, text="Son Belirtiler:", font=("Arial", 10, "bold")).pack(pady=(10, 0))
            for belirti, tarih in belirtiler:
                tk.Label(self.window, text=f"- {belirti} ({tarih})").pack(anchor='w', padx=20)

        # Uyarılar
        cursor.execute("""
            SELECT baslik, mesaj, olusturulma_zamani FROM uyarilar 
            WHERE hasta_id = %s AND okundu = FALSE ORDER BY olusturulma_zamani DESC
        """, (self.hasta_id,))
        uyarilar = cursor.fetchall()
        if uyarilar:
            tk.Label(self.window, text="⚠️ Uyarılar:", font=("Arial", 10, "bold"), fg="red").pack(pady=(10, 0))
            for baslik, mesaj, zaman in uyarilar:
                tk.Label(self.window, text=f"{baslik} ({zaman}): {mesaj}", fg="red", wraplength=600, justify="left").pack(anchor='w', padx=20)

    
    
        
        cursor.close()

    def on_closing(self):
        import matplotlib.pyplot as plt
        plt.close('all')
        if self.conn:
            self.conn.close()
        self.window.destroy()