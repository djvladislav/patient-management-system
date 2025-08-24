import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
import database_connection
# global treeview referansı (sadece bir tane olacaksa)
insulin_tree = None

def get_filtered_insulin_data(hasta_id, start_date, end_date):
    conn = database_connection.create_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT olcum_zamani, deger, insulin_dozu
            FROM kan_sekeri_olcumleri
            WHERE hasta_id = %s
            AND olcum_zamani BETWEEN %s AND %s
            ORDER BY olcum_zamani
        """, (hasta_id, start_date, end_date))
        
        return cursor.fetchall()
    finally:
        conn.close()

def create_insulin_filter_ui(current_hasta_id, parent_window):
    filter_window = tk.Toplevel(parent_window)
    filter_window.title("İnsülin Filtreleme")
    
    ttk.Label(filter_window, text="Başlangıç Tarihi:").grid(row=0, column=0, padx=5, pady=5)
    start_date = DateEntry(filter_window)
    start_date.grid(row=0, column=1, padx=5, pady=5)
    
    ttk.Label(filter_window, text="Bitiş Tarihi:").grid(row=1, column=0, padx=5, pady=5)
    end_date = DateEntry(filter_window)
    end_date.grid(row=1, column=1, padx=5, pady=5)
    
    def on_filter():
        display_insulin_data(current_hasta_id, start_date.get_date(), end_date.get_date(), filter_window)
    
    ttk.Button(filter_window, text="Filtrele", command=on_filter).grid(row=2, column=0, columnspan=2, pady=10)

def display_insulin_data(hasta_id, start_date, end_date, parent):
    global insulin_tree

    data = get_filtered_insulin_data(hasta_id, start_date, end_date)
    
    # Önceki tree varsa temizle
    if insulin_tree is not None:
        insulin_tree.destroy()
        insulin_tree = None

    insulin_tree = ttk.Treeview(parent, columns=("Tarih", "Değer", "İnsülin"), show='headings')
    insulin_tree.heading("Tarih", text="Tarih")
    insulin_tree.heading("Değer", text="Kan Şekeri (mg/dL)")
    insulin_tree.heading("İnsülin", text="İnsülin Dozu (ml)")
    
    insulin_tree.column("Tarih", width=150)
    insulin_tree.column("Değer", width=100)
    insulin_tree.column("İnsülin", width=100)
    
    for i, (tarih, deger, insulin) in enumerate(data):
        insulin_tree.insert("", "end", values=(tarih.strftime("%d/%m/%Y %H:%M"), deger, insulin))
    
    insulin_tree.grid(row=3, column=0, columnspan=2, pady=10)