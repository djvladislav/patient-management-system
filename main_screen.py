import tkinter as tk
from tkinter import ttk
from doctor_panel import DoctorPanel
from patient_panel import PatientPanel

class MainScreen:
    def __init__(self, user_type, user_id):
        self.root = tk.Tk()
        self.user_type = user_type
        self.user_id = user_id
        
        if user_type == "doktor":
            DoctorPanel(self.root, user_id)
        else:
            PatientPanel(self.root, user_id)
        
        self.root.mainloop()

    
    def create_widgets(self):
        tk.Label(self.root, text=f"Hoşgeldiniz, {self.user_type} ID: {self.user_id}", font=('Arial', 14)).pack(pady=20)
        
        if self.user_type == "hasta":
            tk.Button(self.root, text="Kan Şekeri Ölçümü Ekle", command=self.add_blood_sugar).pack(pady=10)
            tk.Button(self.root, text="Ölçüm Geçmişim", command=self.view_history).pack(pady=10)
        else:
            tk.Button(self.root, text="Hastalarımı Listele", command=self.list_patients).pack(pady=10)
    

if __name__ == "__main__":
    
    MainScreen("doktor", 1)
    #MainScreen("hasta", 2)