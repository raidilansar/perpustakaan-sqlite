import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import sqlite3
import os

class PerpustakaanApp:
    def __init__(self, master):
        self.master = master
        master.title("Aplikasi Peminjaman Buku Perpustakaan")
        master.geometry("500x630")
        master.configure(bg="#f0f4f8")

        self.buku_tersedia = [
            "Pemrograman Visual",
            "Python Lengkap",
            "UI/UX Design",
            "Belajar Teknologi",
            "Zaman Canggih",
            "Teknologi AI"
        ]

        self.buku_dipilih = None

        self.label_nama = tk.Label(master, text="Nama Peminjam:", bg="#f0f4f8", fg="#333", font=("Arial", 10, "bold"))
        self.label_nama.pack(pady=(10, 0))
        self.entry_nama = tk.Entry(master, width=40)
        self.entry_nama.pack()
        self.entry_nama.insert(0, "Raidil Anshar")

        self.label_buku = tk.Label(master, text="Pilih Buku:", bg="#f0f4f8", fg="#333", font=("Arial", 10, "bold"))
        self.label_buku.pack(pady=(10, 0))

        self.frame_buku = tk.Frame(master, bg="#f0f4f8")
        self.frame_buku.pack()

        for index, buku in enumerate(self.buku_tersedia):
            row = index // 3
            column = index % 3
            button = tk.Button(
                self.frame_buku,
                text=buku,
                width=15,
                height=2,
                bg="#6fa8dc",
                fg="white",
                font=("Arial", 9),
                command=lambda b=buku: self.pilih_buku(b)
            )
            button.grid(row=row, column=column, padx=10, pady=10)

        self.label_tgl_pinjam = tk.Label(master, text="Tanggal Pinjam:", bg="#f0f4f8", fg="#333", font=("Arial", 10, "bold"))
        self.label_tgl_pinjam.pack(pady=(5, 0))
        self.entry_tgl_pinjam = tk.Entry(master, width=40)
        self.entry_tgl_pinjam.pack()
        self.entry_tgl_pinjam.insert(0, datetime.now().strftime("%d-%m-%Y"))

        self.label_tgl_kembali = tk.Label(master, text="Tanggal Pengembalian:", bg="#f0f4f8", fg="#333", font=("Arial", 10, "bold"))
        self.label_tgl_kembali.pack(pady=(5, 0))
        self.entry_tgl_kembali = tk.Entry(master, width=40)
        self.entry_tgl_kembali.pack()
        tanggal_kembali = datetime.now() + timedelta(days=7)
        self.entry_tgl_kembali.insert(0, tanggal_kembali.strftime("%d-%m-%Y"))

        self.btn_pinjam = tk.Button(master, text="Pinjam Buku", command=self.pinjam_buku,
                                    bg="#38761d", fg="white", font=("Arial", 10, "bold"), width=20)
        self.btn_pinjam.pack(pady=5)

        self.btn_kembali = tk.Button(master, text="Kembalikan Buku", command=self.kembalikan_buku,
                                     bg="#cc0000", fg="white", font=("Arial", 10, "bold"), width=20)
        self.btn_kembali.pack(pady=(0, 10))

        self.label_daftar = tk.Label(master, text="Daftar Peminjaman:", bg="#f0f4f8", fg="#333", font=("Arial", 10, "bold"))
        self.label_daftar.pack()
        self.listbox_peminjaman = tk.Listbox(master, width=60, height=10, bg="#ffffff", fg="#000")
        self.listbox_peminjaman.pack()

        self.db_file = "peminjaman.db"
        self.inisialisasi_database()
        self.muat_data()

    def inisialisasi_database(self):
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS peminjaman_buku (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama TEXT,
                buku TEXT,
                tgl_pinjam TEXT,
                tgl_kembali TEXT
            )
        ''')
        self.conn.commit()

    def pilih_buku(self, buku):
        self.buku_dipilih = buku
        messagebox.showinfo("Buku Dipilih", f"Kamu memilih buku: {buku}")
        self.entry_tgl_pinjam.delete(0, tk.END)
        self.entry_tgl_pinjam.insert(0, datetime.now().strftime("%d-%m-%Y"))
        tanggal_kembali = datetime.now() + timedelta(days=7)
        self.entry_tgl_kembali.delete(0, tk.END)
        self.entry_tgl_kembali.insert(0, tanggal_kembali.strftime("%d-%m-%Y"))

    def pinjam_buku(self):
        nama = self.entry_nama.get().strip()
        tgl_pinjam = self.entry_tgl_pinjam.get().strip()
        tgl_kembali = self.entry_tgl_kembali.get().strip()

        if not nama:
            messagebox.showwarning("Peringatan", "Nama peminjam tidak boleh kosong.")
            return
        if not self.buku_dipilih:
            messagebox.showwarning("Peringatan", "Silakan pilih buku terlebih dahulu.")
            return

        # Cek duplikat
        self.cursor.execute('''SELECT * FROM peminjaman_buku WHERE nama=? AND buku=?''', (nama, self.buku_dipilih))
        if self.cursor.fetchone():
            messagebox.showinfo("Info", "Data peminjaman ini sudah tercatat.")
            return

        self.cursor.execute('''
            INSERT INTO peminjaman_buku (nama, buku, tgl_pinjam, tgl_kembali)
            VALUES (?, ?, ?, ?)
        ''', (nama, self.buku_dipilih, tgl_pinjam, tgl_kembali))
        self.conn.commit()

        data = f"{nama.ljust(20)} | Buku: {self.buku_dipilih.ljust(20)} | Pinjam: {tgl_pinjam} | Kembali: {tgl_kembali}"
        self.listbox_peminjaman.insert(tk.END, data)

    def kembalikan_buku(self):
        selected_index = self.listbox_peminjaman.curselection()
        if not selected_index:
            messagebox.showwarning("Peringatan", "Silakan pilih data peminjaman yang ingin dikembalikan.")
            return

        konfirmasi = messagebox.askyesno("Konfirmasi", "Apakah kamu yakin ingin mengembalikan buku ini?")
        if not konfirmasi:
            return

        item = self.listbox_peminjaman.get(selected_index)
        bagian = item.split("|")
        nama = bagian[0].strip()
        buku = bagian[1].split(":")[1].strip()

        self.cursor.execute('''
            DELETE FROM peminjaman_buku WHERE nama=? AND buku=?
        ''', (nama, buku))
        self.conn.commit()

        self.listbox_peminjaman.delete(selected_index)
        messagebox.showinfo("Pengembalian Berhasil", "Buku telah dikembalikan.")

    def muat_data(self):
        self.cursor.execute("SELECT * FROM peminjaman_buku")
        semua_data = self.cursor.fetchall()
        for row in semua_data:
            nama, buku, tgl_pinjam, tgl_kembali = row[1], row[2], row[3], row[4]
            data = f"{nama.ljust(20)} | Buku: {buku.ljust(20)} | Pinjam: {tgl_pinjam} | Kembali: {tgl_kembali}"
            self.listbox_peminjaman.insert(tk.END, data)

# Jalankan aplikasi
if __name__ == "__main__":
    root = tk.Tk()
    app = PerpustakaanApp(root)
    root.mainloop()

