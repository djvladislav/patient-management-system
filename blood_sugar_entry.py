import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import database_connection

class BloodSugarMeasurement:
    def __init__(self, root, hasta_id):
        self.root = root
        self.hasta_id = hasta_id
        
    def add_blood_sugar(self):
        self.top = tk.Toplevel(self.root)
        self.top.title("Kan Şekeri Ölçümü Ekle")
        self.top.geometry("400x350")
        
        ttk.Label(self.top, text="Kan şekeri değeri (mg/dL):").pack(pady=5)
        self.value_entry = ttk.Entry(self.top)
        self.value_entry.pack(pady=5)
        
        ttk.Label(self.top, text="Ölçüm zamanı seçin:").pack(pady=5)
        
        self.time_var = tk.StringVar(value="sabah")
        
        options = [
            ("Sabah Ölçümü (07:00 - 08:00)", "sabah", 
             "Uyanış sonrası kan şekeri ölçümü yapılır."),
            ("Öğle Ölçümü (12:00 - 13:00)", "ogle", 
             "Öğle yemeğinden önce veya öğle yemeği sonrası kan şekeri ölçümü yapılır."),
            ("İkindi Ölçümü (15:00 - 16:00)", "ikindi", 
             "Ara öğün veya günün sonrasında ölçüm yapılır."),
            ("Akşam Ölçümü (18:00 - 19:00)", "aksam", 
             "Akşam yemeğinden önce veya akşam yemeği sonrası kan şekeri ölçümü yapılır."),
            ("Gece Ölçümü (22:00 - 23:00)", "gece", 
             "Gece yatmadan önce kan şekeri ölçümü yapılır.")
        ]
        
        for text, val, desc in options:
            frame = ttk.Frame(self.top)
            frame.pack(anchor="w", padx=10, pady=2, fill="x")
            
            rb = ttk.Radiobutton(frame, text=text, variable=self.time_var, value=val)
            rb.pack(side="left")
            
            lbl = ttk.Label(frame, text=desc, foreground="gray")
            lbl.pack(side="left", padx=10)
        
        ttk.Button(self.top, text="Kaydet", command=self.save_measurement).pack(pady=15)
    
    def save_measurement(self):
     try:
        value = float(self.value_entry.get())  # Float girdiyi integer'a çevir
        if value <= 0:
            raise ValueError("Değer pozitif olmalı")
     except ValueError:
        messagebox.showerror("Hata", "Lütfen geçerli bir kan şekeri değeri girin!")
        return
    
     olcum_tipi = self.time_var.get() 
    
     conn = database_connection.create_connection()
     try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO kan_sekeri_olcumleri (hasta_id, deger, olcum_tipi)
                VALUES (%s, %s, %s)
            """, (self.hasta_id, value, olcum_tipi))
            conn.commit()
     finally:
        conn.close()
    
     messagebox.showinfo("Başarılı", "Kan şekeri ölçümü kaydedildi.")
     self.top.destroy()