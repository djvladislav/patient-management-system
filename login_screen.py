import tkinter as tk
from tkinter import messagebox
from main_screen import MainScreen


import database_connection  

class LoginScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Diyabet Takip Sistemi - Giriş")
        self.root.geometry("400x300")
        
        self.conn = database_connection.create_connection()
        self.create_widgets()
    
    def create_widgets(self):
        tk.Label(self.root, text="TC Kimlik No:").pack(pady=5)
        self.tc_entry = tk.Entry(self.root)
        self.tc_entry.pack(pady=5)
        
        tk.Label(self.root, text="Şifre:").pack(pady=5)
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack(pady=5)
        
        self.user_type = tk.StringVar(value="hasta")
        tk.Radiobutton(self.root, text="Hasta", variable=self.user_type, value="hasta").pack()
        tk.Radiobutton(self.root, text="Doktor", variable=self.user_type, value="doktor").pack()
        
        tk.Button(self.root, text="Giriş Yap", command=self.login).pack(pady=20)
    
    def login(self):
     tc_no = self.tc_entry.get()
     password = self.password_entry.get()
     user_type = self.user_type.get()
    
     if not tc_no or not password:
        messagebox.showerror("Hata", "TC No ve şifre giriniz!")
        return
    
     conn = self.conn
     try:
        cursor = conn.cursor()
        if user_type == "hasta":
            cursor.execute("SELECT hasta_id, sifre FROM hastalar WHERE tc_no=%s", (tc_no,))
        else:
            cursor.execute("SELECT doktor_id, sifre FROM doktorlar WHERE tc_no=%s", (tc_no,))
        
        result = cursor.fetchone()
        if result:
            user_id, hashed_password = result
            if database_connection.verify_password(password, hashed_password):
                self.root.destroy()
                MainScreen(user_type, user_id)
            else:
                messagebox.showerror("Hata", "Geçersiz bilgiler!")
        else:
            messagebox.showerror("Hata", "Kullanıcı bulunamadı!")
     except Exception as e:
        messagebox.showerror("Hata", f"Bir sorun oluştu: {e}")
     finally:
        cursor.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginScreen(root)
    root.mainloop()