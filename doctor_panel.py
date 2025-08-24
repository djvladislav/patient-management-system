import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import database_connection
import secrets
import string
from functions import send_credentials
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.dates import DateFormatter
from tkcalendar import DateEntry
from PIL import Image, ImageTk
import PatientDetailsWindow

class DoctorPanel:
    def __init__(self, root, doktor_id):
        self.root = root
        self.doktor_id = doktor_id
        self.root.title("Doktor Paneli")
        self.root.geometry("1000x700")
        
        
        self.create_alert_widgets()
        self.conn = database_connection.create_connection()
        self.create_widgets()
        self.create_diet_exercise_tab()
        self.load_patients()


    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        
        self.patient_list_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.patient_list_frame, text="Hastalarım")
        
        self.add_patient_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.add_patient_frame, text="Yeni Hasta Ekle")
        
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)
        
        self.tree = ttk.Treeview(self.patient_list_frame, columns=("ID", "Ad", "TC", "Email"), show="headings")
        for col in ["ID", "Ad", "TC", "Email"]:
            self.tree.heading(col, text=col)
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)
        
        tk.Button(self.patient_list_frame, text="Hasta Detay", command=self.show_patient_details).pack(pady=5)
        
        tk.Label(self.add_patient_frame, text="Ad Soyad:").grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = tk.Entry(self.add_patient_frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(self.add_patient_frame, text="TC No:").grid(row=1, column=0, padx=5, pady=5)
        self.tc_entry = tk.Entry(self.add_patient_frame, width=30)
        self.tc_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(self.add_patient_frame, text="E-posta:").grid(row=2, column=0, padx=5, pady=5)
        self.email_entry = tk.Entry(self.add_patient_frame, width=30)
        self.email_entry.grid(row=2, column=1, padx=5, pady=5)
        
        tk.Label(self.add_patient_frame, text="Doğum Tarihi:").grid(row=3, column=0, padx=5, pady=5)
        self.birth_entry = tk.Entry(self.add_patient_frame, width=30)
        self.birth_entry.grid(row=3, column=1, padx=5, pady=5)
        
        tk.Label(self.add_patient_frame, text="Cinsiyet:").grid(row=4, column=0, padx=5, pady=5)
        self.gender_var = tk.StringVar()
        tk.Radiobutton(self.add_patient_frame, text="Erkek", variable=self.gender_var, value="E").grid(row=4, column=1, sticky="w")
        tk.Radiobutton(self.add_patient_frame, text="Kadın", variable=self.gender_var, value="K").grid(row=4, column=1)
        
        tk.Label(self.add_patient_frame, text="Profil Resmi:").grid(row=5, column=0, padx=5, pady=5)
        self.profile_image_path = tk.StringVar()
        tk.Button(self.add_patient_frame, text="Resim Seç", command=self.select_image).grid(row=5, column=1, sticky="w")
        
        tk.Button(self.add_patient_frame, text="Hasta Ekle", command=self.add_patient, bg="#4CAF50", fg="white").grid(row=6, column=1, pady=10)
    
    def select_image(self):
        filepath = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png")])
        if filepath:
            self.profile_image_path.set(filepath)
    
    def add_patient(self):
        ad_soyad = self.name_entry.get()
        tc_no = self.tc_entry.get()
        email = self.email_entry.get()
        dogum_tarihi = self.birth_entry.get()
        cinsiyet = self.gender_var.get()
        resim_path = self.profile_image_path.get()
        
        password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
        
        try:
            cursor = self.conn.cursor()
            hashed_password = database_connection.hash_password(password)
            
            cursor.execute("""
                INSERT INTO hastalar 
                (tc_no, ad_soyad, sifre, email, dogum_tarihi, cinsiyet, profil_fotografi, doktor_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (tc_no, ad_soyad, hashed_password, email, dogum_tarihi, cinsiyet, resim_path, self.doktor_id))
            
            self.conn.commit()
            send_credentials(email, tc_no, password)
            
            messagebox.showinfo("Başarılı", "Hasta başarıyla eklendi ve bilgileri gönderildi!")
            self.load_patients()
            
        except Exception as e:
            messagebox.showerror("Hata", f"Hasta eklenemedi: {str(e)}")
    
    def on_closing(window, conn=None):
     import matplotlib.pyplot as plt
     plt.close('all')
     if conn:
        conn.close()
     window.destroy()
        
    def load_patients(self):
     conn = database_connection.create_connection()
     try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT hasta_id, ad_soyad, tc_no, email
            FROM hastalar 
            WHERE doktor_id = %s
            ORDER BY ad_soyad
        """, (self.doktor_id,))
        
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        for hasta_id, ad, tc, email in cursor:
            self.tree.insert("", "end", values=(hasta_id, ad, tc, email))
     finally:
        cursor.close()
        conn.close()
    
    def show_patient_details(self):
     conn = database_connection.create_connection()
     try:
        cursor=conn.cursor()
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Uyarı", "Lütfen bir hasta seçin!")
            return
        
        hasta_id = self.tree.item(selected_item[0])['values'][0]
        details_window = PatientDetailsWindow.PatientDetailsWindow(self.root, hasta_id)
        
    
        cursor.execute("""
    SELECT hp.diyet_id, hp.egzersiz_id, hp.baslangic_tarihi, 
           dt.ad, et.ad
    FROM hasta_planlari hp
    LEFT JOIN diyet_tipleri dt ON hp.diyet_id = dt.diyet_id
    LEFT JOIN egzersiz_tipleri et ON hp.egzersiz_id = et.egzersiz_id
    WHERE hp.hasta_id = %s AND hp.aktif = TRUE
""", (hasta_id,))
        
    

        plan = cursor.fetchone()
        if plan:
         diyet_id, egzersiz_id, baslangic, diyet_adi, egzersiz_adi = plan
         tk.Label(details_window.window, 
           text=f"Aktif Plan:\nDiyet: {diyet_adi} (ID: {diyet_id})\n"
                f"Egzersiz: {egzersiz_adi} (ID: {egzersiz_id})\n"
                f"Başlangıç: {baslangic}",
           font=("Arial", 10, "bold")).pack(pady=10)
     finally:
        cursor.close()  
        conn.close()   
    def create_diet_exercise_tab(self):
   
     self.plan_frame = ttk.Frame(self.notebook)
     self.notebook.add(self.plan_frame, text="Tedavi Planları")

    
     tk.Label(self.plan_frame, text="Hasta Seç:").grid(row=0, column=0, padx=5, pady=5)
     self.hasta_combobox = ttk.Combobox(self.plan_frame, state="readonly")
     self.hasta_combobox.grid(row=0, column=1, padx=5, pady=5)
     self.hasta_combobox.bind("<<ComboboxSelected>>", self.load_patient_data)

   
     tk.Label(self.plan_frame, text="Son Kan Şekeri Seviyesi (mg/dL):").grid(row=1, column=0, padx=5, pady=5)
     self.kan_sekeri_label = tk.Label(self.plan_frame, text="-")
     self.kan_sekeri_label.grid(row=1, column=1, padx=5, pady=5)

    
     tk.Label(self.plan_frame, text="Son Belirtiler:").grid(row=2, column=0, padx=5, pady=5)
     self.belirtiler_label = tk.Label(self.plan_frame, text="-")
     self.belirtiler_label.grid(row=2, column=1, padx=5, pady=5)

     
     tk.Button(self.plan_frame, text="Öneri Getir", command=self.get_recommendation).grid(row=3, columnspan=2, pady=5)

    
     self.diyet_oneri_label = tk.Label(self.plan_frame, text="Önerilen Diyet: -")
     self.diyet_oneri_label.grid(row=4, columnspan=2, padx=5, pady=5)

     self.egzersiz_oneri_label = tk.Label(self.plan_frame, text="Önerilen Egzersiz: -")
     self.egzersiz_oneri_label.grid(row=5, columnspan=2, padx=5, pady=5)

     
     tk.Label(self.plan_frame, text="Diyet Tipi:").grid(row=6, column=0, padx=5, pady=5)
     self.diyetler = self.get_diyet_listesi()
     self.diyet_combobox = ttk.Combobox(self.plan_frame, values=list(self.diyetler.keys()))
     self.diyet_combobox.grid(row=6, column=1, padx=5, pady=5)

    
     tk.Label(self.plan_frame, text="Egzersiz Tipi:").grid(row=7, column=0, padx=5, pady=5)
     self.egzersizler = self.get_egzersiz_listesi()
     self.egzersiz_combobox = ttk.Combobox(self.plan_frame, values=list(self.egzersizler.keys()))
     self.egzersiz_combobox.grid(row=7, column=1, padx=5, pady=5)

    
     tk.Label(self.plan_frame, text="Başlangıç Tarihi:").grid(row=8, column=0, padx=5, pady=5)
     self.baslangic_entry = DateEntry(self.plan_frame)
     self.baslangic_entry.grid(row=8, column=1, padx=5, pady=5)

    
     tk.Button(self.plan_frame, text="Planı Kaydet", 
              command=self.save_plan, bg="#4CAF50", fg="white").grid(row=9, columnspan=2, pady=10)

    
     self.update_hasta_combobox()

    def load_patient_data(self, event):
   
     selected_hasta = self.hasta_combobox.get()
     if selected_hasta:
        hasta_id = self.hastalar.get(selected_hasta)
        cursor = self.conn.cursor()
        try:
            
            cursor.execute("""
                SELECT deger FROM kan_sekeri_olcumleri 
                WHERE hasta_id = %s 
                ORDER BY olcum_zamani DESC 
                LIMIT 1
            """, (hasta_id,))
            result = cursor.fetchone()
            if result:
                self.kan_sekeri_label.config(text=str(result[0]))
            else:
                self.kan_sekeri_label.config(text="Kayıt Yok")

            
            cursor.execute("""
                SELECT belirti_adi FROM hasta_belirtileri 
                WHERE hasta_id = %s 
                ORDER BY kayit_tarihi DESC 
                LIMIT 3
            """, (hasta_id,))
            belirtiler = cursor.fetchall()
            if belirtiler:
                self.belirtiler_label.config(text=", ".join([b[0] for b in belirtiler]))
            else:
                self.belirtiler_label.config(text="Kayıt Yok")
        finally:
            cursor.close()

    def get_recommendation(self):
    
     try:
        kan_sekeri = float(self.kan_sekeri_label.cget("text"))
        if kan_sekeri == "Kayıt Yok":
            messagebox.showwarning("Uyarı", "Hastanın kan şekeri kaydı bulunamadı.")
            return
     except ValueError:
        messagebox.showerror("Hata", "Kan şekeri değeri geçersiz.")
        return

     belirtiler_text = self.belirtiler_label.cget("text")
     belirtiler = belirtiler_text.split(", ") if belirtiler_text != "Kayıt Yok" else []

     
     if kan_sekeri < 70:  
        diyet = "Dengeli Beslenme"
        egzersiz = "Yok"
        if "Nöropati" in belirtiler or "Yorğunluk" in belirtiler:
            diyet = "Beslenme Desteği"
     elif 70 <= kan_sekeri <= 110:  
        diyet = "Dengeli Beslenme"
        egzersiz = "Yürüyüş"
        if "Polifaji" in belirtiler or "Polidipsi" in belirtiler:
            diyet = "Az Şekerli Diyet"
     elif kan_sekeri <= 180:  
        diyet = "Az Şekerli Diyet"
        egzersiz = "Yürüyüş"
        if "Bulanık Görme" in belirtiler or "Nöropati" in belirtiler:
            diyet = "Şekersiz Diyet"
     else:  
        diyet = "Şekersiz Diyet"
        egzersiz = "Yürüyüş"
        if "Yavaş İyileşme" in belirtiler or "Kilo Kaybı" in belirtiler:
            egzersiz = "Klinik Egzersiz"

    # update
     self.diyet_oneri_label.config(text=f"Önerilen Diyet: {diyet}")
     self.egzersiz_oneri_label.config(text=f"Önerilen Egzersiz: {egzersiz}")

    # update 
     self.diyet_combobox.set(diyet)
     self.egzersiz_combobox.set(egzersiz)

    def get_diyet_listesi(self):
     
     return {
        "Az Şekerli Diyet": 1,
        "Şekersiz Diyet": 2,
        "Dengeli Beslenme": 3
    }

    def get_egzersiz_listesi(self):
    
     return {
        "Yürüyüş": 1,
        "Bisiklet": 2,
        "Klinik Egzersiz": 3
    }

    def update_hasta_combobox(self):
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT hasta_id, ad_soyad FROM hastalar 
            WHERE doktor_id = %s ORDER BY ad_soyad
        """, (self.doktor_id,))
        
        self.hastalar = {row[1]: row[0] for row in cursor.fetchall()}
        self.hasta_combobox['values'] = list(self.hastalar.keys())

    def save_plan(self):
        
        hasta_adi = self.hasta_combobox.get()
        diyet_label = self.diyet_combobox.get()
        egzersiz_label = self.egzersiz_combobox.get()
        baslangic_tarihi = self.baslangic_entry.get_date()
        
        if not all([hasta_adi, diyet_label, egzersiz_label]):
            messagebox.showerror("Hata", "Tüm alanları doldurun!")
            return
            
        hasta_id = self.hastalar.get(hasta_adi)
        
        diyet_tipi = self.diyetler.get(diyet_label)       
        egzersiz_tipi = self.egzersizler.get(egzersiz_label) 

        try:
            cursor = self.conn.cursor()
            
           # first make the current plan passive
            cursor.execute("""
                UPDATE hasta_planlari 
                SET aktif = FALSE 
                WHERE hasta_id = %s
            """, (hasta_id,))
            
            # then insert new plans.......................................
            cursor.execute("""
                INSERT INTO hasta_planlari (
                    hasta_id, doktor_id, diyet_id, egzersiz_id, baslangic_tarihi
                ) VALUES (%s, %s, %s, %s, %s)
            """, (hasta_id, self.doktor_id, diyet_tipi, egzersiz_tipi, baslangic_tarihi))
            
            self.conn.commit()
            messagebox.showinfo("Başarılı", "Tedavi planı oluşturuldu!")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Plan kaydedilemedi: {str(e)}")

    def create_alert_widgets(self):
        
        self.alert_frame = tk.LabelFrame(self.root, text=" Bekleyen Uyarılar")
        self.alert_frame.pack(pady=10, padx=10, fill="x")
        
       
        self.alert_listbox = tk.Listbox(
            self.alert_frame, 
            height=4,
            selectmode=tk.SINGLE,
            width=80 
         
        )
        self.alert_listbox.pack(fill="both", expand=True)
        
        
        tk.Button(
            self.alert_frame,
            text="Yenile",
            command=self.refresh_alerts
        ).pack(pady=5)

       # read
        tk.Button(
    self.alert_frame,
    text="Okundu Olarak İşaretle",
    command=self.mark_alert_as_read
).pack(pady=5)
        
        self.refresh_alerts()  #to refresh alerts
    
    def refresh_alerts(self):
     
     from alerts import get_doctor_alerts

     self.alert_listbox.delete(0, tk.END)
     self.alerts = get_doctor_alerts(self.doktor_id)  

     for alert in self.alerts:
        display_text = f"{alert['hasta_adi']} - {alert['mesaj']} - {alert['tarih']}"
        self.alert_listbox.insert(tk.END, display_text)



    def mark_alert_as_read(self):
     selected = self.alert_listbox.curselection()
     if not selected:
        messagebox.showwarning("Uyarı", "Lütfen bir uyarı seçin.")
        return
    
     selected_index = selected[0]
     uyari_id = self.alerts[selected_index]["uyari_id"]  

     try:
        conn = database_connection.create_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE uyarilar
                SET okundu = TRUE
                WHERE uyari_id = %s
            """, (uyari_id,))
            conn.commit()
        messagebox.showinfo("Başarılı", "Uyarı okundu olarak işaretlendi.")
        self.refresh_alerts()
     except Exception as e:
        messagebox.showerror("Hata", f"Uyarı işaretlenemedi: {e}")
     finally:
        conn.close()

    
