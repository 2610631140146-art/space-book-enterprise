import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime, timedelta
import csv

# ==============================================================================
# KONFIGURASI GLOBAL & PALET WARNA APLIKASI (ENTERPRISE UI THEME)
# ==============================================================================
DB_NAME = "space_book_enterprise.db"

THEME = {
    "bg_main": "#f1f5f9",        # Slate 100 - Latar belakang utama
    "bg_card": "#ffffff",        # Putih - Latar belakang kartu & form
    "sidebar_bg": "#0f172a",     # Slate 900 - Sidebar gelap elegan
    "sidebar_hover": "#1e293b",  # Slate 800 - Hover menu sidebar
    "sidebar_active": "#2563eb", # Blue 600 - Menu aktif
    "primary": "#2563eb",        # Blue 600 - Tombol utama
    "primary_hover": "#1d4ed8",  # Blue 700
    "secondary": "#475569",      # Slate 600
    "success": "#16a34a",        # Green 600 - Status lunas / kosong
    "success_bg": "#dcfce7",     # Green 100
    "warning": "#d97706",        # Amber 600 - Menunggu verifikasi
    "warning_bg": "#fef3c7",     # Amber 100
    "danger": "#dc2626",         # Red 600 - Batal / booked / bentrok
    "danger_bg": "#fee2e2",      # Red 100
    "text_dark": "#0f172a",      # Teks gelap utama
    "text_muted": "#64748b",     # Teks abu-abu sekunder
    "border": "#cbd5e1"          # Garis tepi halus
}

FONTS = {
    "title_lg": ("Segoe UI", 20, "bold"),
    "title_md": ("Segoe UI", 14, "bold"),
    "title_sm": ("Segoe UI", 11, "bold"),
    "body": ("Segoe UI", 10),
    "body_bold": ("Segoe UI", 10, "bold"),
    "small": ("Segoe UI", 9),
    "small_italic": ("Segoe UI", 9, "italic"),
    "mono": ("Consolas", 10),
    "kpi_num": ("Segoe UI", 22, "bold")
}

# ==============================================================================
# MODUL 1: MANAJEMEN DATABASE SQLITE RELASIONAL
# ==============================================================================
class DatabaseManager:
    def __init__(self, db_name=DB_NAME):
        self.db_name = db_name
        self.init_database()

    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama TEXT NOT NULL,
                no_hp TEXT NOT NULL,
                email TEXT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                tanggal_daftar TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fasilitas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama_fasilitas TEXT NOT NULL,
                jenis TEXT NOT NULL,
                kapasitas INTEGER DEFAULT 10,
                harga_per_jam INTEGER NOT NULL,
                deskripsi TEXT,
                status_aktif TEXT DEFAULT 'TERSEDIA'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS promo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kode_promo TEXT UNIQUE NOT NULL,
                diskon_persen INTEGER NOT NULL,
                keterangan TEXT,
                status TEXT DEFAULT 'AKTIF'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS booking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kode_booking TEXT UNIQUE NOT NULL,
                id_fasilitas INTEGER NOT NULL,
                id_user INTEGER NOT NULL,
                tanggal TEXT NOT NULL,
                jam_mulai TEXT NOT NULL,
                jam_selesai TEXT NOT NULL,
                durasi INTEGER NOT NULL,
                total_harga INTEGER NOT NULL,
                diskon INTEGER DEFAULT 0,
                total_bayar INTEGER NOT NULL,
                catatan TEXT,
                status_booking TEXT NOT NULL,
                status_bayar TEXT NOT NULL,
                waktu_buat TEXT NOT NULL,
                FOREIGN KEY(id_fasilitas) REFERENCES fasilitas(id) ON DELETE CASCADE,
                FOREIGN KEY(id_user) REFERENCES user(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pembayaran (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_booking INTEGER NOT NULL,
                metode TEXT NOT NULL,
                bank_tujuan TEXT,
                referensi TEXT NOT NULL,
                jumlah_bayar INTEGER NOT NULL,
                tanggal_bayar TEXT NOT NULL,
                FOREIGN KEY(id_booking) REFERENCES booking(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS log_aktivitas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                waktu TEXT NOT NULL,
                aktor TEXT NOT NULL,
                aksi TEXT NOT NULL,
                detail TEXT
            )
        """)

        self._seed_initial_data(cursor)
        conn.commit()
        conn.close()

    def _seed_initial_data(self, cursor):
        cursor.execute("SELECT COUNT(*) FROM user")
        if cursor.fetchone()[0] == 0:
            now_str = datetime.now().strftime("%d-%m-%Y %H:%M")
            users = [
                ("Administrator Utama", "081111111111", "admin@spacebook.id", "admin", "admin123", "admin", now_str),
                ("Budi Santoso", "081234567890", "budi01@email.com", "budi01", "123456", "user", now_str),
                ("Siti Aisyah", "081298765432", "siti.a@email.com", "siti02", "123456", "user", now_str)
            ]
            cursor.executemany("""
                INSERT INTO user (nama, no_hp, email, username, password, role, tanggal_daftar)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, users)

        cursor.execute("SELECT COUNT(*) FROM fasilitas")
        if cursor.fetchone()[0] == 0:
            fasilitas = [
                ("Lapangan Futsal A", "Olahraga", 14, 150000, "Rumput sintetis standar FIFA, pencahayaan LED, tribun penonton.", "TERSEDIA"),
                ("Lapangan Badminton B", "Olahraga", 4, 75000, "Karpet vinyl standar BWF, sirkulasi udara optimal, bebas silau.", "TERSEDIA"),
                ("Lapangan Basket Indoor", "Olahraga", 12, 120000, "Lantai kayu parket, ring standar FIBA, papan skor digital.", "TERSEDIA"),
                ("Ruang Meeting Alpha", "Coworking", 10, 60000, "Smart TV 65 inch, whiteboard kaca, Wi-Fi 300 Mbps, AC.", "TERSEDIA"),
                ("Ruang Meeting Beta", "Coworking", 6, 50000, "Ruang kedap suara, proyektor HD, cocok untuk diskusi tim kecil.", "TERSEDIA"),
                ("Creative Hall Coworking", "Coworking", 25, 100000, "Area terbuka luas untuk workshop, seminar mini, dan komunitas.", "TERSEDIA")
            ]
            cursor.executemany("""
                INSERT INTO fasilitas (nama_fasilitas, jenis, kapasitas, harga_per_jam, deskripsi, status_aktif)
                VALUES (?, ?, ?, ?, ?, ?)
            """, fasilitas)

        cursor.execute("SELECT COUNT(*) FROM promo")
        if cursor.fetchone()[0] == 0:
            promos = [
                ("MAHASISWA10", 10, "Diskon khusus mahasiswa sebesar 10%", "AKTIF"),
                ("WEEKEND20", 20, "Promo spesial akhir pekan 20%", "AKTIF"),
                ("OPENING15", 15, "Promo pembukaan fasilitas baru 15%", "AKTIF")
            ]
            cursor.executemany("""
                INSERT INTO promo (kode_promo, diskon_persen, keterangan, status)
                VALUES (?, ?, ?, ?)
            """, promos)

        cursor.execute("SELECT COUNT(*) FROM booking")
        if cursor.fetchone()[0] == 0:
            besok = (datetime.now() + timedelta(days=1)).strftime("%d-%m-%Y")
            now_str = datetime.now().strftime("%d-%m-%Y %H:%M")
            sample_bookings = [
                ("BK0001", 1, 2, besok, "18:00", "20:00", 2, 300000, 0, 300000, "Latihan rutin mingguan", "BOOKED", "LUNAS", now_str),
                ("BK0002", 4, 3, besok, "09:00", "11:00", 2, 120000, 12000, 108000, "Rapat koordinasi proyek", "BOOKED", "LUNAS", now_str)
            ]
            cursor.executemany("""
                INSERT INTO booking (kode_booking, id_fasilitas, id_user, tanggal, jam_mulai, jam_selesai,
                                     durasi, total_harga, diskon, total_bayar, catatan, status_booking, status_bayar, waktu_buat)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, sample_bookings)

    def catat_log(self, aktor, aksi, detail=""):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            waktu = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            cursor.execute("INSERT INTO log_aktivitas (waktu, aktor, aksi, detail) VALUES (?, ?, ?, ?)",
                           (waktu, aktor, aksi, detail))
            conn.commit()
            conn.close()
        except Exception:
            pass

# ==============================================================================
# MODUL 2: LOGIKA BISNIS, VALIDASI WAKTU & PERHITUNGAN
# ==============================================================================
class BookingEngine:
    OPERATIONAL_HOURS = [
        "08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00",
        "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00"
    ]

    def __init__(self, db_manager):
        self.db = db_manager

    @staticmethod
    def parse_jam_ke_menit(jam_str):
        try:
            parts = jam_str.strip().split(":")
            if len(parts) != 2:
                return None
            jam = int(parts[0])
            menit = int(parts[1])
            if not (0 <= jam <= 23 and 0 <= menit <= 59):
                return None
            return jam * 60 + menit
        except ValueError:
            return None

    def validasi_format_tanggal(self, tanggal_str):
        try:
            datetime.strptime(tanggal_str.strip(), "%d-%m-%Y")
            return True
        except ValueError:
            return False

    def validasi_jam_operasional(self, jam_mulai, jam_selesai):
        m_start = self.parse_jam_ke_menit(jam_mulai)
        m_end = self.parse_jam_ke_menit(jam_selesai)

        if m_start is None or m_end is None:
            return False, "Format jam harus HH:MM (contoh: 18:00)."
        if m_start < 8 * 60 or m_end > 22 * 60:
            return False, "Jam operasional fasilitas adalah pukul 08:00 - 22:00."
        if m_end <= m_start:
            return False, "Jam selesai harus lebih besar dari jam mulai."
        if (m_end - m_start) < 60:
            return False, "Durasi booking minimal adalah 1 jam (60 menit)."
        if (m_end - m_start) % 60 != 0:
            return False, "Durasi pemesanan harus dalam kelipatan jam penuh (misal: 1 jam, 2 jam)."
        return True, "Valid"

    def cek_bentrok_jadwal(self, id_fasilitas, tanggal, jam_mulai, jam_selesai):
        valid_jam, pesan_jam = self.validasi_jam_operasional(jam_mulai, jam_selesai)
        if not valid_jam:
            return False, pesan_jam

        if not self.validasi_format_tanggal(tanggal):
            return False, "Format tanggal salah! Gunakan format DD-MM-YYYY (contoh: 25-11-2026)."

        m_baru_mulai = self.parse_jam_ke_menit(jam_mulai)
        m_baru_selesai = self.parse_jam_ke_menit(jam_selesai)

        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT kode_booking, jam_mulai, jam_selesai, status_booking
            FROM booking
            WHERE id_fasilitas = ? AND tanggal = ? AND status_booking NOT IN ('DIBATALKAN', 'DITOLAK')
        """, (id_fasilitas, tanggal.strip()))
        existing = cursor.fetchall()
        conn.close()

        for kode, b_mulai, b_selesai, st in existing:
            m_lama_mulai = self.parse_jam_ke_menit(b_mulai)
            m_lama_selesai = self.parse_jam_ke_menit(b_selesai)
            if not (m_baru_selesai <= m_lama_mulai or m_baru_mulai >= m_lama_selesai):
                return False, f"Bentrok dengan pesanan {kode} pada pukul {b_mulai} - {b_selesai} ({st})."

        return True, "Slot tersedia dan siap dibooking!"

    def dapatkan_rekomendasi_slot(self, id_fasilitas, tanggal, durasi_jam=1):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT jam_mulai, jam_selesai FROM booking
            WHERE id_fasilitas = ? AND tanggal = ? AND status_booking NOT IN ('DIBATALKAN', 'DITOLAK')
        """, (id_fasilitas, tanggal.strip()))
        booked = cursor.fetchall()
        conn.close()

        rekomendasi = []
        for i in range(len(self.OPERATIONAL_HOURS) - durasi_jam):
            slot_m = self.OPERATIONAL_HOURS[i]
            slot_s = self.OPERATIONAL_HOURS[i + durasi_jam]
            m1 = self.parse_jam_ke_menit(slot_m)
            m2 = self.parse_jam_ke_menit(slot_s)

            bentrok = False
            for b_m, b_s in booked:
                bm1 = self.parse_jam_ke_menit(b_m)
                bm2 = self.parse_jam_ke_menit(b_s)
                if not (m2 <= bm1 or m1 >= bm2):
                    bentrok = True
                    break
            if not bentrok:
                rekomendasi.append(f"{slot_m} - {slot_s}")

        return rekomendasi

    def dapatkan_matriks_harian(self, id_fasilitas, tanggal):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.jam_mulai, b.jam_selesai, u.nama, b.status_booking
            FROM booking b JOIN user u ON b.id_user = u.id
            WHERE b.id_fasilitas = ? AND b.tanggal = ? AND b.status_booking NOT IN ('DIBATALKAN', 'DITOLAK')
        """, (id_fasilitas, tanggal.strip()))
        booked = cursor.fetchall()
        conn.close()

        matriks = []
        for i in range(len(self.OPERATIONAL_HOURS) - 1):
            m = self.OPERATIONAL_HOURS[i]
            s = self.OPERATIONAL_HOURS[i + 1]
            m1 = self.parse_jam_ke_menit(m)
            m2 = self.parse_jam_ke_menit(s)

            status_slot = "KOSONG"
            penyewa = "-"
            for b_m, b_s, nama_u, st_b in booked:
                bm1 = self.parse_jam_ke_menit(b_m)
                bm2 = self.parse_jam_ke_menit(b_s)
                if not (m2 <= bm1 or m1 >= bm2):
                    status_slot = f"BOOKED ({st_b})"
                    penyewa = nama_u
                    break
            matriks.append((f"{m} - {s}", status_slot, penyewa))
        return matriks

    def hitung_biaya(self, harga_per_jam, jam_mulai, jam_selesai, kode_promo=""):
        m1 = self.parse_jam_ke_menit(jam_mulai)
        m2 = self.parse_jam_ke_menit(jam_selesai)
        durasi = (m2 - m1) // 60
        subtotal = durasi * harga_per_jam
        diskon_nominal = 0
        persen = 0

        if kode_promo.strip():
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT diskon_persen FROM promo WHERE kode_promo = ? AND status = 'AKTIF'",
                           (kode_promo.strip().upper(),))
            row = cursor.fetchone()
            conn.close()
            if row:
                persen = row[0]
                diskon_nominal = int(subtotal * (persen / 100))

        total_akhir = subtotal - diskon_nominal
        return durasi, subtotal, diskon_nominal, total_akhir, persen

    def generate_kode_booking(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(id) FROM booking")
        max_id = cursor.fetchone()[0]
        conn.close()
        next_num = (max_id or 0) + 1
        return f"BK{next_num:04d}"

# ==============================================================================
# MODUL 3: KOMPONEN UI REUSABLE & HELPER WIDGETS
# ==============================================================================
class UIHelper:
    @staticmethod
    def create_card(parent, title="", padding=15):
        frame = tk.Frame(parent, bg=THEME["bg_card"], highlightbackground=THEME["border"], highlightthickness=1)
        if title:
            header = tk.Frame(frame, bg=THEME["bg_card"])
            header.pack(fill="x", padx=padding, pady=(padding, 5))
            tk.Label(header, text=title, font=FONTS["title_sm"], bg=THEME["bg_card"], fg=THEME["text_dark"]).pack(side="left")
            tk.Frame(frame, bg=THEME["border"], height=1).pack(fill="x", padx=padding, pady=(0, 10))
        body = tk.Frame(frame, bg=THEME["bg_card"])
        body.pack(fill="both", expand=True, padx=padding, pady=(0, padding))
        return frame, body

    @staticmethod
    def create_kpi_card(parent, title, value_var, accent_color, icon_text=""):
        card = tk.Frame(parent, bg=THEME["bg_card"], highlightbackground=THEME["border"], highlightthickness=1)
        top_strip = tk.Frame(card, bg=accent_color, height=4)
        top_strip.pack(fill="x")

        inner = tk.Frame(card, bg=THEME["bg_card"], padx=16, pady=14)
        inner.pack(fill="both", expand=True)

        header_row = tk.Frame(inner, bg=THEME["bg_card"])
        header_row.pack(fill="x")
        tk.Label(header_row, text=title, font=FONTS["small"], bg=THEME["bg_card"], fg=THEME["text_muted"]).pack(side="left")
        if icon_text:
            tk.Label(header_row, text=icon_text, font=("Segoe UI", 12), bg=THEME["bg_card"], fg=accent_color).pack(side="right")

        tk.Label(inner, textvariable=value_var, font=FONTS["kpi_num"], bg=THEME["bg_card"], fg=THEME["text_dark"]).pack(anchor="w", pady=(6, 0))
        return card

    @staticmethod
    def create_button(parent, text, command, style_type="primary", width=None, padx=14, pady=7):
        colors = {
            "primary": (THEME["primary"], "#ffffff", THEME["primary_hover"]),
            "success": (THEME["success"], "#ffffff", "#15803d"),
            "warning": (THEME["warning"], "#ffffff", "#b45309"),
            "danger": (THEME["danger"], "#ffffff", "#b91c1c"),
            "secondary": ("#e2e8f0", THEME["text_dark"], "#cbd5e1")
        }
        bg_c, fg_c, hover_c = colors.get(style_type, colors["primary"])
        btn = tk.Button(
            parent, text=text, command=command, bg=bg_c, fg=fg_c,
            font=FONTS["body_bold"], relief="flat", cursor="hand2",
            padx=padx, pady=pady, activebackground=hover_c, activeforeground=fg_c
        )
        if width:
            btn.config(width=width)
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_c))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg_c))
        return btn

    @staticmethod
    def create_styled_treeview(parent, columns, col_widths, height=10):
        container = tk.Frame(parent, bg=THEME["bg_card"])
        scrollbar_y = ttk.Scrollbar(container, orient="vertical")
        scrollbar_x = ttk.Scrollbar(container, orient="horizontal")

        tree = ttk.Treeview(
            container, columns=columns, show="headings", height=height,
            yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set
        )
        scrollbar_y.config(command=tree.yview)
        scrollbar_x.config(command=tree.xview)

        for col, w in zip(columns, col_widths):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor="center" if w < 120 else "w")

        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        tree.pack(fill="both", expand=True)
        return container, tree

    @staticmethod
    def format_rupiah(nominal):
        return f"Rp {int(nominal):,}".replace(",", ".")

# ==============================================================================
# MODUL 4: POPUP E-TICKET DIGITAL & STRUK PEMBAYARAN
# ==============================================================================
class ReceiptPopup(tk.Toplevel):
    def __init__(self, parent, booking_data):
        super().__init__(parent)
        self.title(f"E-Ticket & Struk Booking - {booking_data['kode']}")
        self.geometry("460x620")
        self.configure(bg=THEME["bg_main"])
        self.resizable(False, False)
        self.booking_data = booking_data
        self.build_ui()

    def build_ui(self):
        header = tk.Frame(self, bg=THEME["sidebar_bg"], pady=15)
        header.pack(fill="x")
        tk.Label(header, text="🎟️ E-TICKET RESERVASI SPACE-BOOK", font=FONTS["title_sm"], bg=THEME["sidebar_bg"], fg="white").pack()
        tk.Label(header, text="Tunjukkan bukti digital ini kepada petugas lokasi", font=FONTS["small"], bg=THEME["sidebar_bg"], fg="#94a3b8").pack()

        card = tk.Frame(self, bg="white", padx=25, pady=20, highlightbackground=THEME["border"], highlightthickness=1)
        card.pack(fill="both", expand=True, padx=20, pady=15)

        self.receipt_text = self._generate_receipt_string()
        text_box = tk.Text(card, font=FONTS["mono"], bg="#f8fafc", fg=THEME["text_dark"], relief="flat", height=22, width=44, padx=10, pady=10)
        text_box.insert("1.0", self.receipt_text)
        text_box.config(state="disabled")
        text_box.pack(fill="both", expand=True)

        btn_frame = tk.Frame(self, bg=THEME["bg_main"], pady=10)
        btn_frame.pack(fill="x", padx=20)
        UIHelper.create_button(btn_frame, "💾 Simpan Struk (.txt)", self.save_txt, "success").pack(side="left", expand=True, fill="x", padx=(0, 5))
        UIHelper.create_button(btn_frame, "Tutup", self.destroy, "secondary").pack(side="right", expand=True, fill="x", padx=(5, 0))

    def _generate_receipt_string(self):
        d = self.booking_data
        lines = [
            "========================================",
            "       SPACE-BOOK RESERVATION SYSTEM    ",
            "    Smart Sports & Coworking Center     ",
            "========================================",
            f"Kode Booking   : {d['kode']}",
            f"Waktu Cetak    : {datetime.now().strftime('%d-%m-%Y %H:%M')}",
            "----------------------------------------",
            f"Nama Penyewa   : {d['penyewa']}",
            f"No. Telepon    : {d['no_hp']}",
            f"Fasilitas      : {d['fasilitas']}",
            f"Kategori       : {d['jenis']}",
            f"Tanggal Main   : {d['tanggal']}",
            f"Jam Booking    : {d['jam']} ({d['durasi']} Jam)",
            "----------------------------------------",
            f"Subtotal       : {UIHelper.format_rupiah(d['subtotal'])}",
            f"Diskon Promo   : -{UIHelper.format_rupiah(d['diskon'])}",
            f"TOTAL BAYAR    : {UIHelper.format_rupiah(d['total_bayar'])}",
            "----------------------------------------",
            f"Status Booking : {d['status_booking']}",
            f"Status Bayar   : {d['status_bayar']}",
            f"Catatan        : {d['catatan'] or '-'}",
            "========================================",
            "  * Harap datang 15 menit sebelum jadwal",
            "  * Terima kasih telah menggunakan",
            "    layanan digital SPACE-BOOK!",
            "========================================"
        ]
        return "\n".join(lines)

    def save_txt(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=f"Tiket_{self.booking_data['kode']}.txt",
            filetypes=[("Text File", "*.txt")]
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.receipt_text)
            messagebox.showinfo("Tersimpan", f"E-Ticket berhasil disimpan di:\n{path}", parent=self)

# ==============================================================================
# MODUL 5: HALAMAN OTENTIKASI (LOGIN & REGISTRASI MODERN)
# ==============================================================================
class AuthView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=THEME["bg_main"])
        self.controller = controller
        self.db = controller.db
        self.build_ui()

    def build_ui(self):
        left_panel = tk.Frame(self, bg=THEME["sidebar_bg"], width=380)
        left_panel.pack(side="left", fill="y")
        left_panel.pack_propagate(False)

        brand_box = tk.Frame(left_panel, bg=THEME["sidebar_bg"])
        brand_box.place(relx=0.5, rely=0.45, anchor="center")

        tk.Label(brand_box, text="🏟️", font=("Segoe UI", 48), bg=THEME["sidebar_bg"], fg="white").pack()
        tk.Label(brand_box, text="SPACE-BOOK", font=("Segoe UI", 26, "bold"), bg=THEME["sidebar_bg"], fg="white").pack(pady=(5, 2))
        tk.Label(brand_box, text="ENTERPRISE EDITION", font=("Segoe UI", 10, "bold"), bg=THEME["sidebar_bg"], fg="#38bdf8").pack()
        tk.Frame(brand_box, bg="#334155", height=2, width=220).pack(pady=20)
        tk.Label(
            brand_box,
            text="Sistem Reservasi Lapangan Olahraga\n& Coworking Space Terintegrasi.\n\n✔ Cek Jadwal Real-Time\n✔ Anti Bentrok Otomatis\n✔ E-Ticket & Laporan Keuangan",
            font=FONTS["body"], bg=THEME["sidebar_bg"], fg="#cbd5e1", justify="center"
        ).pack()

        right_panel = tk.Frame(self, bg=THEME["bg_main"])
        right_panel.pack(side="right", fill="both", expand=True)

        center_card = tk.Frame(right_panel, bg="white", padx=40, pady=35, highlightbackground=THEME["border"], highlightthickness=1)
        center_card.place(relx=0.5, rely=0.5, anchor="center")

        notebook = ttk.Notebook(center_card)
        notebook.pack(fill="both", expand=True)

        tab_login = tk.Frame(notebook, bg="white", padx=20, pady=20)
        tab_reg = tk.Frame(notebook, bg="white", padx=20, pady=15)
        notebook.add(tab_login, text="   🔑 Masuk Akun   ")
        notebook.add(tab_reg, text="   📝 Daftar Baru   ")

        tk.Label(tab_login, text="Selamat Datang Kembali", font=FONTS["title_md"], bg="white", fg=THEME["text_dark"]).pack(anchor="w")
        tk.Label(tab_login, text="Silakan masuk menggunakan akun terdaftar Anda", font=FONTS["small"], bg="white", fg=THEME["text_muted"]).pack(anchor="w", pady=(0, 20))

        tk.Label(tab_login, text="Username", font=FONTS["body_bold"], bg="white").pack(anchor="w")
        self.ent_login_user = tk.Entry(tab_login, font=FONTS["body"], width=34, relief="solid", bd=1)
        self.ent_login_user.pack(pady=(4, 14), ipady=5)

        tk.Label(tab_login, text="Password", font=FONTS["body_bold"], bg="white").pack(anchor="w")
        self.ent_login_pass = tk.Entry(tab_login, font=FONTS["body"], width=34, show="•", relief="solid", bd=1)
        self.ent_login_pass.pack(pady=(4, 20), ipady=5)

        UIHelper.create_button(tab_login, "MASUK KE SISTEM", self.handle_login, "primary", width=30, pady=9).pack()

        info_box = tk.Frame(tab_login, bg="#f8fafc", padx=12, pady=10, highlightbackground="#e2e8f0", highlightthickness=1)
        info_box.pack(fill="x", pady=(20, 0))
        tk.Label(info_box, text="Akun Demo Pengujian:", font=FONTS["small"], bg="#f8fafc", fg=THEME["text_dark"]).pack(anchor="w")
        tk.Label(info_box, text="• Admin : admin / admin123\n• User  : budi01 / 123456", font=FONTS["small"], bg="#f8fafc", fg=THEME["text_muted"], justify="left").pack(anchor="w")

        tk.Label(tab_reg, text="Buat Akun Penyewa", font=FONTS["title_md"], bg="white", fg=THEME["text_dark"]).pack(anchor="w")
        tk.Label(tab_reg, text="Lengkapi formulir di bawah untuk mulai memesan", font=FONTS["small"], bg="white", fg=THEME["text_muted"]).pack(anchor="w", pady=(0, 12))

        fields = [
            ("Nama Lengkap *", "reg_nama", False),
            ("Nomor HP (Min 10 digit) *", "reg_hp", False),
            ("Email (Opsional)", "reg_email", False),
            ("Username *", "reg_user", False),
            ("Password (Min 6 karakter) *", "reg_pass", True)
        ]
        self.reg_entries = {}
        for label_txt, key, is_pass in fields:
            tk.Label(tab_reg, text=label_txt, font=FONTS["small"], bg="white", fg=THEME["text_dark"]).pack(anchor="w")
            ent = tk.Entry(tab_reg, font=FONTS["body"], width=34, show="•" if is_pass else "", relief="solid", bd=1)
            ent.pack(pady=(2, 8), ipady=4)
            self.reg_entries[key] = ent

        UIHelper.create_button(tab_reg, "DAFTAR AKUN BARU", self.handle_register, "success", width=30, pady=8).pack(pady=(8, 0))

    def handle_login(self):
        username = self.ent_login_user.get().strip()
        password = self.ent_login_pass.get().strip()

        if not username or not password:
            messagebox.showwarning("Peringatan", "Username dan password wajib diisi!")
            return

        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nama, no_hp, email, username, role
            FROM user WHERE username = ? AND password = ?
        """, (username, password))
        row = cursor.fetchone()
        conn.close()

        if row:
            user_data = {
                "id": row[0], "nama": row[1], "no_hp": row[2],
                "email": row[3], "username": row[4], "role": row[5]
            }
            self.db.catat_log(username, "LOGIN", f"Masuk sebagai {row[5]}")
            self.controller.login_success(user_data)
        else:
            messagebox.showerror("Login Gagal", "Username atau Password yang Anda masukkan salah!")

    def handle_register(self):
        nama = self.reg_entries["reg_nama"].get().strip()
        hp = self.reg_entries["reg_hp"].get().strip()
        email = self.reg_entries["reg_email"].get().strip()
        user = self.reg_entries["reg_user"].get().strip()
        pw = self.reg_entries["reg_pass"].get().strip()

        if not nama or not hp or not user or not pw:
            messagebox.showwarning("Data Kurang", "Kolom bertanda (*) wajib diisi!")
            return
        if not hp.isdigit() or len(hp) < 10:
            messagebox.showwarning("Validasi No HP", "Nomor HP harus berupa angka minimal 10 digit!")
            return
        if len(pw) < 6:
            messagebox.showwarning("Validasi Password", "Password minimal harus terdiri dari 6 karakter!")
            return

        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            now_str = datetime.now().strftime("%d-%m-%Y %H:%M")
            cursor.execute("""
                INSERT INTO user (nama, no_hp, email, username, password, role, tanggal_daftar)
                VALUES (?, ?, ?, ?, ?, 'user', ?)
            """, (nama, hp, email, user, pw, now_str))
            conn.commit()
            conn.close()

            self.db.catat_log(user, "REGISTRASI", f"Akun baru terdaftar: {nama}")
            messagebox.showinfo("Registrasi Berhasil", "Akun berhasil dibuat! Silakan berpindah ke tab 'Masuk Akun' untuk login.")
            for ent in self.reg_entries.values():
                ent.delete(0, tk.END)
        except sqlite3.IntegrityError:
            messagebox.showerror("Username Terpakai", f"Username '{user}' sudah digunakan oleh pengguna lain.")

# ==============================================================================
# MODUL 6: DASHBOARD PENYEWA (USER PORTAL LENGKAP)
# ==============================================================================
class UserDashboardView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=THEME["bg_main"])
        self.controller = controller
        self.db = controller.db
        self.engine = controller.engine
        self.user = controller.current_user
        self.menu_buttons = {}
        self.build_layout()
        self.switch_page("booking")

    def build_layout(self):
        sidebar = tk.Frame(self, bg=THEME["sidebar_bg"], width=240)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        logo_area = tk.Frame(sidebar, bg=THEME["sidebar_bg"], pady=22, padx=20)
        logo_area.pack(fill="x")
        tk.Label(logo_area, text="🏟️ SPACE-BOOK", font=FONTS["title_md"], bg=THEME["sidebar_bg"], fg="white").pack(anchor="w")
        tk.Label(logo_area, text="Portal Penyewa Fasilitas", font=FONTS["small"], bg=THEME["sidebar_bg"], fg="#94a3b8").pack(anchor="w")

        tk.Frame(sidebar, bg="#1e293b", height=1).pack(fill="x", padx=15, pady=(0, 15))

        menus = [
            ("booking", "📅  Booking & Cek Jadwal"),
            ("jadwal", "🕒  Matriks Jadwal Harian"),
            ("riwayat", "💳  Riwayat & Pembayaran"),
            ("promo", "🎁  Info Kode Promo"),
            ("profil", "👤  Profil Saya")
        ]
        for key, label in menus:
            btn = tk.Button(
                sidebar, text=label, font=FONTS["body_bold"], bg=THEME["sidebar_bg"],
                fg="#cbd5e1", relief="flat", anchor="w", padx=22, pady=12, cursor="hand2",
                activebackground=THEME["sidebar_active"], activeforeground="white",
                command=lambda k=key: self.switch_page(k)
            )
            btn.pack(fill="x", pady=2)
            self.menu_buttons[key] = btn

        bottom_box = tk.Frame(sidebar, bg="#1e293b", padx=15, pady=15)
        bottom_box.pack(side="bottom", fill="x")
        tk.Label(bottom_box, text=self.user["nama"], font=FONTS["body_bold"], bg="#1e293b", fg="white").pack(anchor="w")
        tk.Label(bottom_box, text=f"@{self.user['username']}", font=FONTS["small"], bg="#1e293b", fg="#94a3b8").pack(anchor="w", pady=(0, 10))
        UIHelper.create_button(bottom_box, "🚪 Keluar (Logout)", self.controller.logout, "danger", pady=6).pack(fill="x")

        self.content_area = tk.Frame(self, bg=THEME["bg_main"])
        self.content_area.pack(side="right", fill="both", expand=True)

    def switch_page(self, page_key):
        for k, btn in self.menu_buttons.items():
            if k == page_key:
                btn.config(bg=THEME["sidebar_active"], fg="white")
            else:
                btn.config(bg=THEME["sidebar_bg"], fg="#cbd5e1")

        for w in self.content_area.winfo_children():
            w.destroy()

        if page_key == "booking":
            self.render_page_booking()
        elif page_key == "jadwal":
            self.render_page_matriks_jadwal()
        elif page_key == "riwayat":
            self.render_page_riwayat()
        elif page_key == "promo":
            self.render_page_promo()
        elif page_key == "profil":
            self.render_page_profil()

    def render_page_booking(self):
        header = tk.Frame(self.content_area, bg="white", padx=25, pady=18, highlightbackground=THEME["border"], highlightthickness=1)
        header.pack(fill="x")
        tk.Label(header, text="Reservasi Fasilitas & Cek Ketersediaan", font=FONTS["title_md"], bg="white", fg=THEME["text_dark"]).pack(anchor="w")
        tk.Label(header, text="Pilih fasilitas, tentukan tanggal & jam, dan sistem akan memvalidasi bentrok secara otomatis.", font=FONTS["small"], bg="white", fg=THEME["text_muted"]).pack(anchor="w")

        main_scroll = tk.Frame(self.content_area, bg=THEME["bg_main"], padx=25, pady=20)
        main_scroll.pack(fill="both", expand=True)

        card_fas, body_fas = UIHelper.create_card(main_scroll, "1. Daftar Fasilitas Tersedia")
        card_fas.pack(fill="x", pady=(0, 15))

        cols = ("ID", "Nama Fasilitas", "Kategori", "Kapasitas", "Tarif / Jam", "Keterangan")
        widths = (50, 180, 100, 90, 120, 320)
        tree_wrap, self.tree_fas = UIHelper.create_styled_treeview(body_fas, cols, widths, height=5)
        tree_wrap.pack(fill="x")

        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nama_fasilitas, jenis, kapasitas, harga_per_jam, deskripsi FROM fasilitas WHERE status_aktif = 'TERSEDIA'")
        self.fasilitas_data = cursor.fetchall()
        conn.close()

        for f in self.fasilitas_data:
            self.tree_fas.insert("", "end", values=(f[0], f[1], f[2], f"{f[3]} Org", UIHelper.format_rupiah(f[4]), f[5]))

        bottom_grid = tk.Frame(main_scroll, bg=THEME["bg_main"])
        bottom_grid.pack(fill="both", expand=True)

        card_form, body_form = UIHelper.create_card(bottom_grid, "2. Formulir Pemesanan")
        card_form.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Label(body_form, text="Pilih Fasilitas:", font=FONTS["body_bold"], bg="white").grid(row=0, column=0, sticky="w", pady=6)
        self.cb_fas = ttk.Combobox(body_form, values=[f"{f[0]} - {f[1]} ({UIHelper.format_rupiah(f[4])}/jam)" for f in self.fasilitas_data], width=36, state="readonly", font=FONTS["body"])
        self.cb_fas.grid(row=0, column=1, padx=10, pady=6, sticky="w")
        if self.fasilitas_data:
            self.cb_fas.current(0)

        tk.Label(body_form, text="Tanggal (DD-MM-YYYY):", font=FONTS["body_bold"], bg="white").grid(row=1, column=0, sticky="w", pady=6)
        self.ent_tgl = tk.Entry(body_form, font=FONTS["body"], width=20, relief="solid", bd=1)
        self.ent_tgl.insert(0, (datetime.now() + timedelta(days=1)).strftime("%d-%m-%Y"))
        self.ent_tgl.grid(row=1, column=1, padx=10, pady=6, sticky="w", ipady=3)

        jam_frame = tk.Frame(body_form, bg="white")
        jam_frame.grid(row=2, column=1, padx=10, pady=6, sticky="w")
        tk.Label(body_form, text="Waktu Mulai - Selesai:", font=FONTS["body_bold"], bg="white").grid(row=2, column=0, sticky="w", pady=6)

        self.cb_mulai = ttk.Combobox(jam_frame, values=BookingEngine.OPERATIONAL_HOURS[:-1], width=8, state="readonly", font=FONTS["body"])
        self.cb_mulai.set("18:00")
        self.cb_mulai.pack(side="left")
        tk.Label(jam_frame, text="  s/d  ", bg="white", font=FONTS["body_bold"]).pack(side="left")
        self.cb_selesai = ttk.Combobox(jam_frame, values=BookingEngine.OPERATIONAL_HOURS[1:], width=8, state="readonly", font=FONTS["body"])
        self.cb_selesai.set("20:00")
        self.cb_selesai.pack(side="left")

        tk.Label(body_form, text="Kode Promo (Opsional):", font=FONTS["body_bold"], bg="white").grid(row=3, column=0, sticky="w", pady=6)
        self.ent_promo = tk.Entry(body_form, font=FONTS["body"], width=20, relief="solid", bd=1)
        self.ent_promo.grid(row=3, column=1, padx=10, pady=6, sticky="w", ipady=3)

        tk.Label(body_form, text="Catatan Tambahan:", font=FONTS["body_bold"], bg="white").grid(row=4, column=0, sticky="w", pady=6)
        self.ent_catatan = tk.Entry(body_form, font=FONTS["body"], width=38, relief="solid", bd=1)
        self.ent_catatan.grid(row=4, column=1, padx=10, pady=6, sticky="w", ipady=3)

        card_calc, body_calc = UIHelper.create_card(bottom_grid, "3. Estimasi Biaya & Validasi")
        card_calc.pack(side="right", fill="both", expand=True, padx=(10, 0))

        self.lbl_estimasi = tk.Label(
            body_calc,
            text="Klik 'Hitung & Cek Jadwal' untuk melihat\nketersediaan slot serta rincian biaya.",
            font=FONTS["body"], bg="#f8fafc", fg=THEME["text_dark"],
            justify="left", padx=15, pady=15, highlightbackground=THEME["border"], highlightthickness=1
        )
        self.lbl_estimasi.pack(fill="x", pady=(0, 15))

        btn_row = tk.Frame(body_calc, bg="white")
        btn_row.pack(fill="x")
        UIHelper.create_button(btn_row, "🔍 Cek Jadwal & Hitung", self.aksi_cek_dan_hitung, "warning").pack(fill="x", pady=(0, 8))
        UIHelper.create_button(btn_row, "✅ Konfirmasi & Buat Booking", self.aksi_submit_booking, "primary").pack(fill="x")

    def _get_selected_fasilitas(self):
        idx = self.cb_fas.current()
        if idx < 0 or not self.fasilitas_data:
            return None
        return self.fasilitas_data[idx]

    def aksi_cek_dan_hitung(self):
        fas = self._get_selected_fasilitas()
        if not fas:
            return
        id_f, nama_f, jenis_f, kap, harga, _ = fas
        tgl = self.ent_tgl.get().strip()
        m = self.cb_mulai.get()
        s = self.cb_selesai.get()
        promo = self.ent_promo.get().strip()

        aman, pesan = self.engine.cek_bentrok_jadwal(id_f, tgl, m, s)
        if not aman:
            rek = self.engine.dapatkan_rekomendasi_slot(id_f, tgl, 1)
            rek_str = ", ".join(rek[:5]) if rek else "Penuh seharian"
            self.lbl_estimasi.config(
                text=f"❌ STATUS: JADWAL TIDAK TERSEDIA\nAlasan: {pesan}\n\n💡 Rekomendasi Jam Kosong (1 Jam):\n{rek_str}",
                bg=THEME["danger_bg"], fg=THEME["danger"]
            )
            return False

        durasi, sub, disk, total, persen = self.engine.hitung_biaya(harga, m, s, promo)
        promo_info = f" ({promo.upper()} -{persen}%)" if persen > 0 else ""
        teks = (
            f"✅ STATUS: JADWAL TERSEDIA!\n"
            f"Fasilitas : {nama_f} ({tgl})\n"
            f"Waktu     : {m} - {s} ({durasi} Jam)\n"
            f"Subtotal  : {UIHelper.format_rupiah(sub)}\n"
            f"Diskon    : -{UIHelper.format_rupiah(disk)}{promo_info}\n"
            f"TOTAL     : {UIHelper.format_rupiah(total)}"
        )
        self.lbl_estimasi.config(text=teks, bg=THEME["success_bg"], fg="#14532d")
        return True

    def aksi_submit_booking(self):
        if not self.aksi_cek_dan_hitung():
            messagebox.showerror("Booking Ditolak", "Jadwal yang dipilih bentrok atau tidak valid. Silakan periksa pesan status!")
            return

        fas = self._get_selected_fasilitas()
        id_f, nama_f, _, _, harga, _ = fas
        tgl = self.ent_tgl.get().strip()
        m = self.cb_mulai.get()
        s = self.cb_selesai.get()
        promo = self.ent_promo.get().strip()
        catatan = self.ent_catatan.get().strip()

        durasi, sub, disk, total, _ = self.engine.hitung_biaya(harga, m, s, promo)
        kode_bk = self.engine.generate_kode_booking()
        now_str = datetime.now().strftime("%d-%m-%Y %H:%M")

        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO booking (kode_booking, id_fasilitas, id_user, tanggal, jam_mulai, jam_selesai,
                                 durasi, total_harga, diskon, total_bayar, catatan, status_booking, status_bayar, waktu_buat)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'MENUNGGU PEMBAYARAN', 'BELUM LUNAS', ?)
        """, (kode_bk, id_f, self.user["id"], tgl, m, s, durasi, sub, disk, total, catatan, now_str))
        conn.commit()
        conn.close()

        self.db.catat_log(self.user["username"], "BOOKING BARU", f"{kode_bk} - {nama_f} ({tgl} {m}-{s})")
        messagebox.showinfo(
            "Booking Berhasil!",
            f"Reservasi Anda telah tercatat!\n\nKode Booking : {kode_bk}\nTotal Tagihan: {UIHelper.format_rupiah(total)}\nStatus       : MENUNGGU PEMBAYARAN\n\nSilakan menuju menu 'Riwayat & Pembayaran' untuk menyelesaikan transaksi."
        )
        self.switch_page("riwayat")

    def render_page_matriks_jadwal(self):
        header = tk.Frame(self.content_area, bg="white", padx=25, pady=18, highlightbackground=THEME["border"], highlightthickness=1)
        header.pack(fill="x")
        tk.Label(header, text="Kalender & Matriks Ketersediaan Slot Harian", font=FONTS["title_md"], bg="white", fg=THEME["text_dark"]).pack(anchor="w")
        tk.Label(header, text="Pantau slot jam operasional (08:00 - 22:00) secara visual untuk menghindari bentrok.", font=FONTS["small"], bg="white", fg=THEME["text_muted"]).pack(anchor="w")

        body = tk.Frame(self.content_area, bg=THEME["bg_main"], padx=25, pady=20)
        body.pack(fill="both", expand=True)

        card_filter, body_filter = UIHelper.create_card(body, "Filter Pencarian Jadwal")
        card_filter.pack(fill="x", pady=(0, 15))

        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nama_fasilitas FROM fasilitas")
        fas_list = cursor.fetchall()
        conn.close()

        row_f = tk.Frame(body_filter, bg="white")
        row_f.pack(fill="x")

        tk.Label(row_f, text="Fasilitas:", font=FONTS["body_bold"], bg="white").pack(side="left")
        self.cb_mat_fas = ttk.Combobox(row_f, values=[f"{x[0]} - {x[1]}" for x in fas_list], width=28, state="readonly", font=FONTS["body"])
        self.cb_mat_fas.pack(side="left", padx=10)
        if fas_list:
            self.cb_mat_fas.current(0)

        tk.Label(row_f, text="Tanggal (DD-MM-YYYY):", font=FONTS["body_bold"], bg="white").pack(side="left", padx=(15, 0))
        self.ent_mat_tgl = tk.Entry(row_f, font=FONTS["body"], width=16, relief="solid", bd=1)
        self.ent_mat_tgl.insert(0, (datetime.now() + timedelta(days=1)).strftime("%d-%m-%Y"))
        self.ent_mat_tgl.pack(side="left", padx=10, ipady=3)

        UIHelper.create_button(row_f, "Tampilkan Matriks", self.muat_matriks_jadwal, "primary", pady=5).pack(side="left", padx=10)

        card_tbl, body_tbl = UIHelper.create_card(body, "Status Slot Per Jam (08:00 - 22:00)")
        card_tbl.pack(fill="both", expand=True)

        cols = ("Slot Waktu", "Status Ketersediaan", "Keterangan Pemesan")
        widths = (180, 220, 260)
        wrap, self.tree_matriks = UIHelper.create_styled_treeview(body_tbl, cols, widths, height=14)
        wrap.pack(fill="both", expand=True)

        self.tree_matriks.tag_configure("kosong", background="#dcfce7", foreground="#166534")
        self.tree_matriks.tag_configure("booked", background="#fee2e2", foreground="#991b1b")

        self.muat_matriks_jadwal()

    def muat_matriks_jadwal(self):
        if not self.cb_mat_fas.get():
            return
        id_f = int(self.cb_mat_fas.get().split(" - ")[0])
        tgl = self.ent_mat_tgl.get().strip()

        if not self.engine.validasi_format_tanggal(tgl):
            messagebox.showwarning("Format Tanggal", "Gunakan format DD-MM-YYYY!")
            return

        for item in self.tree_matriks.get_children():
            self.tree_matriks.delete(item)

        matriks = self.engine.dapatkan_matriks_harian(id_f, tgl)
        for slot, status, penyewa in matriks:
            tag = "kosong" if status == "KOSONG" else "booked"
            self.tree_matriks.insert("", "end", values=(slot, status, penyewa), tags=(tag,))

    def render_page_riwayat(self):
        header = tk.Frame(self.content_area, bg="white", padx=25, pady=18, highlightbackground=THEME["border"], highlightthickness=1)
        header.pack(fill="x")
        tk.Label(header, text="Riwayat Pemesanan & Konfirmasi Pembayaran", font=FONTS["title_md"], bg="white", fg=THEME["text_dark"]).pack(anchor="w")
        tk.Label(header, text="Klik salah satu transaksi pada tabel untuk melakukan pembayaran, pembatalan, atau mencetak E-Ticket.", font=FONTS["small"], bg="white", fg=THEME["text_muted"]).pack(anchor="w")

        body = tk.Frame(self.content_area, bg=THEME["bg_main"], padx=25, pady=20)
        body.pack(fill="both", expand=True)

        card_tbl, body_tbl = UIHelper.create_card(body, "Daftar Transaksi Booking Anda")
        card_tbl.pack(fill="both", expand=True, pady=(0, 15))

        cols = ("Kode", "Fasilitas", "Tanggal", "Jam", "Total Bayar", "Status Booking", "Status Bayar")
        widths = (90, 180, 100, 110, 120, 160, 140)
        wrap, self.tree_riw = UIHelper.create_styled_treeview(body_tbl, cols, widths, height=9)
        wrap.pack(fill="both", expand=True)

        card_pay, body_pay = UIHelper.create_card(body, "Panel Pembayaran & Aksi Tiket")
        card_pay.pack(fill="x")

        row_p = tk.Frame(body_pay, bg="white")
        row_p.pack(fill="x")

        tk.Label(row_p, text="Metode:", font=FONTS["body_bold"], bg="white").pack(side="left")
        self.cb_metode = ttk.Combobox(row_p, values=["Transfer Bank", "Bayar di Tempat"], width=16, state="readonly", font=FONTS["body"])
        self.cb_metode.current(0)
        self.cb_metode.pack(side="left", padx=8)

        tk.Label(row_p, text="Bank / Ref:", font=FONTS["body_bold"], bg="white").pack(side="left")
        self.ent_ref = tk.Entry(row_p, font=FONTS["body"], width=20, relief="solid", bd=1)
        self.ent_ref.insert(0, "BCA - TRF88912")
        self.ent_ref.pack(side="left", padx=8, ipady=3)

        UIHelper.create_button(row_p, "💳 Bayar Tagihan", self.aksi_bayar_booking, "success", pady=5).pack(side="left", padx=6)
        UIHelper.create_button(row_p, "🎟️ Cetak E-Ticket", self.aksi_cetak_tiket, "primary", pady=5).pack(side="left", padx=6)
        UIHelper.create_button(row_p, "❌ Batalkan", self.aksi_batalkan_user, "danger", pady=5).pack(side="left", padx=6)

        self.muat_data_riwayat()

    def muat_data_riwayat(self):
        for item in self.tree_riw.get_children():
            self.tree_riw.delete(item)
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.kode_booking, f.nama_fasilitas, b.tanggal, b.jam_mulai, b.jam_selesai,
                   b.total_bayar, b.status_booking, b.status_bayar
            FROM booking b JOIN fasilitas f ON b.id_fasilitas = f.id
            WHERE b.id_user = ? ORDER BY b.id DESC
        """, (self.user["id"],))
        for r in cursor.fetchall():
            self.tree_riw.insert("", "end", values=(
                r[0], r[1], r[2], f"{r[3]}-{r[4]}", UIHelper.format_rupiah(r[5]), r[6], r[7]
            ))
        conn.close()

    def aksi_bayar_booking(self):
        sel = self.tree_riw.selection()
        if not sel:
            messagebox.showwarning("Pilih Transaksi", "Pilih salah satu baris booking pada tabel terlebih dahulu!")
            return
        vals = self.tree_riw.item(sel[0])["values"]
        kode_bk = vals[0]
        st_bayar = vals[6]

        if st_bayar != "BELUM LUNAS":
            messagebox.showinfo("Info Pembayaran", f"Transaksi {kode_bk} berstatus '{st_bayar}' dan tidak memerlukan pembayaran ulang.")
            return

        metode = self.cb_metode.get()
        ref = self.ent_ref.get().strip()
        if metode == "Transfer Bank" and not ref:
            messagebox.showwarning("Validasi", "Masukkan nama bank dan nomor referensi transfer!")
            return
        if metode == "Bayar di Tempat":
            ref = "CASH-ONSITE"

        status_baru = "MENUNGGU VERIFIKASI" if metode == "Transfer Bank" else "BELUM LUNAS"
        status_bk_baru = "MENUNGGU VERIFIKASI" if metode == "Transfer Bank" else "BOOKED (BAYAR DITEMPAT)"

        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, total_bayar FROM booking WHERE kode_booking = ?", (kode_bk,))
        row = cursor.fetchone()
        if row:
            id_b, tot_b = row
            now_str = datetime.now().strftime("%d-%m-%Y %H:%M")
            cursor.execute("""
                INSERT INTO pembayaran (id_booking, metode, bank_tujuan, referensi, jumlah_bayar, tanggal_bayar)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (id_b, metode, ref.split("-")[0].strip(), ref, tot_b, now_str))
            cursor.execute("UPDATE booking SET status_booking = ?, status_bayar = ? WHERE id = ?",
                           (status_bk_baru, status_baru, id_b))
            conn.commit()
        conn.close()

        self.db.catat_log(self.user["username"], "PEMBAYARAN", f"{kode_bk} via {metode} ({ref})")
        messagebox.showinfo("Pembayaran Diproses", f"Konfirmasi pembayaran untuk {kode_bk} berhasil dikirim!")
        self.muat_data_riwayat()

    def aksi_cetak_tiket(self):
        sel = self.tree_riw.selection()
        if not sel:
            messagebox.showwarning("Pilih Transaksi", "Pilih transaksi yang ingin dicetak E-Ticket-nya!")
            return
        kode_bk = self.tree_riw.item(sel[0])["values"][0]

        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.kode_booking, u.nama, u.no_hp, f.nama_fasilitas, f.jenis, b.tanggal,
                   b.jam_mulai, b.jam_selesai, b.durasi, b.total_harga, b.diskon, b.total_bayar,
                   b.status_booking, b.status_bayar, b.catatan
            FROM booking b
            JOIN user u ON b.id_user = u.id
            JOIN fasilitas f ON b.id_fasilitas = f.id
            WHERE b.kode_booking = ?
        """, (kode_bk,))
        r = cursor.fetchone()
        conn.close()

        if r:
            data = {
                "kode": r[0], "penyewa": r[1], "no_hp": r[2], "fasilitas": r[3],
                "jenis": r[4], "tanggal": r[5], "jam": f"{r[6]} - {r[7]}",
                "durasi": r[8], "subtotal": r[9], "diskon": r[10], "total_bayar": r[11],
                "status_booking": r[12], "status_bayar": r[13], "catatan": r[14]
            }
            ReceiptPopup(self, data)

    def aksi_batalkan_user(self):
        sel = self.tree_riw.selection()
        if not sel:
            messagebox.showwarning("Pilih Transaksi", "Pilih booking yang ingin dibatalkan!")
            return
        vals = self.tree_riw.item(sel[0])["values"]
        kode_bk, st_bk = vals[0], vals[5]

        if st_bk in ("SELESAI", "DIBATALKAN"):
            messagebox.showinfo("Tidak Dapat Dibatalkan", f"Booking berstatus '{st_bk}' tidak dapat dibatalkan.")
            return

        if messagebox.askyesno("Konfirmasi Pembatalan", f"Yakin ingin membatalkan reservasi {kode_bk}?"):
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE booking SET status_booking = 'DIBATALKAN' WHERE kode_booking = ?", (kode_bk,))
            conn.commit()
            conn.close()
            self.db.catat_log(self.user["username"], "BATAL BOOKING", kode_bk)
            self.muat_data_riwayat()

    def render_page_promo(self):
        header = tk.Frame(self.content_area, bg="white", padx=25, pady=18, highlightbackground=THEME["border"], highlightthickness=1)
        header.pack(fill="x")
        tk.Label(header, text="Daftar Kode Promo & Diskon Aktif", font=FONTS["title_md"], bg="white", fg=THEME["text_dark"]).pack(anchor="w")

        body = tk.Frame(self.content_area, bg=THEME["bg_main"], padx=25, pady=20)
        body.pack(fill="both", expand=True)

        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT kode_promo, diskon_persen, keterangan FROM promo WHERE status = 'AKTIF'")
        promos = cursor.fetchall()
        conn.close()

        for kode, persen, ket in promos:
            card, c_body = UIHelper.create_card(body, f"🏷️ KODE: {kode}  —  DISKON {persen}%")
            card.pack(fill="x", pady=(0, 12))
            tk.Label(c_body, text=ket, font=FONTS["body"], bg="white", fg=THEME["text_muted"]).pack(anchor="w")

    def render_page_profil(self):
        header = tk.Frame(self.content_area, bg="white", padx=25, pady=18, highlightbackground=THEME["border"], highlightthickness=1)
        header.pack(fill="x")
        tk.Label(header, text="Informasi Profil Akun", font=FONTS["title_md"], bg="white", fg=THEME["text_dark"]).pack(anchor="w")

        body = tk.Frame(self.content_area, bg=THEME["bg_main"], padx=25, pady=20)
        body.pack(fill="both", expand=True)

        card, c_body = UIHelper.create_card(body, "Data Pengguna Terdaftar")
        card.pack(fill="x")

        info_items = [
            ("Nama Lengkap", self.user["nama"]),
            ("Username", self.user["username"]),
            ("Nomor Telepon", self.user["no_hp"]),
            ("Alamat Email", self.user["email"] or "-"),
            ("Hak Akses", self.user["role"].upper())
        ]
        for lbl, val in info_items:
            row = tk.Frame(c_body, bg="white")
            row.pack(fill="x", pady=6)
            tk.Label(row, text=f"{lbl:<18}:", font=FONTS["body_bold"], bg="white", width=18, anchor="w").pack(side="left")
            tk.Label(row, text=val, font=FONTS["body"], bg="white", fg=THEME["text_dark"]).pack(side="left")

# ==============================================================================
# MODUL 7: DASHBOARD ADMINISTRATOR (ENTERPRISE MANAGEMENT PORTAL)
# ==============================================================================
class AdminDashboardView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=THEME["bg_main"])
        self.controller = controller
        self.db = controller.db
        self.engine = controller.engine
        self.user = controller.current_user
        self.menu_buttons = {}
        self.build_layout()
        self.switch_page("overview")

    def build_layout(self):
        sidebar = tk.Frame(self, bg=THEME["sidebar_bg"], width=250)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        logo_area = tk.Frame(sidebar, bg=THEME["sidebar_bg"], pady=22, padx=20)
        logo_area.pack(fill="x")
        tk.Label(logo_area, text="🛡️ ADMIN PANEL", font=FONTS["title_md"], bg=THEME["sidebar_bg"], fg="white").pack(anchor="w")
        tk.Label(logo_area, text="SPACE-BOOK Enterprise", font=FONTS["small"], bg=THEME["sidebar_bg"], fg="#38bdf8").pack(anchor="w")

        tk.Frame(sidebar, bg="#1e293b", height=1).pack(fill="x", padx=15, pady=(0, 15))

        menus = [
            ("overview", "📊  Ringkasan & Statistik"),
            ("bookings", "📋  Kelola Booking & Bayar"),
            ("fasilitas", "🏟️  Manajemen Fasilitas"),
            ("promo", "🏷️  Kelola Kode Promo"),
            ("users", "👥  Data Pengguna"),
            ("logs", "📜  Log Aktivitas Sistem")
        ]
        for key, label in menus:
            btn = tk.Button(
                sidebar, text=label, font=FONTS["body_bold"], bg=THEME["sidebar_bg"],
                fg="#cbd5e1", relief="flat", anchor="w", padx=22, pady=12, cursor="hand2",
                activebackground=THEME["sidebar_active"], activeforeground="white",
                command=lambda k=key: self.switch_page(k)
            )
            btn.pack(fill="x", pady=2)
            self.menu_buttons[key] = btn

        bottom_box = tk.Frame(sidebar, bg="#1e293b", padx=15, pady=15)
        bottom_box.pack(side="bottom", fill="x")
        tk.Label(bottom_box, text=self.user["nama"], font=FONTS["body_bold"], bg="#1e293b", fg="white").pack(anchor="w")
        tk.Label(bottom_box, text="Role: Super Administrator", font=FONTS["small"], bg="#1e293b", fg="#38bdf8").pack(anchor="w", pady=(0, 10))
        UIHelper.create_button(bottom_box, "🚪 Keluar (Logout)", self.controller.logout, "danger", pady=6).pack(fill="x")

        self.content_area = tk.Frame(self, bg=THEME["bg_main"])
        self.content_area.pack(side="right", fill="both", expand=True)

    def switch_page(self, page_key):
        for k, btn in self.menu_buttons.items():
            btn.config(bg=THEME["sidebar_active"] if k == page_key else THEME["sidebar_bg"],
                       fg="white" if k == page_key else "#cbd5e1")

        for w in self.content_area.winfo_children():
            w.destroy()

        pages = {
            "overview": self.render_admin_overview,
            "bookings": self.render_admin_bookings,
            "fasilitas": self.render_admin_fasilitas,
            "promo": self.render_admin_promo,
            "users": self.render_admin_users,
            "logs": self.render_admin_logs
        }
        pages[page_key]()

    def render_admin_overview(self):
        header = tk.Frame(self.content_area, bg="white", padx=25, pady=18, highlightbackground=THEME["border"], highlightthickness=1)
        header.pack(fill="x")
        tk.Label(header, text="Dashboard Statistik & Laporan Penggunaan", font=FONTS["title_md"], bg="white", fg=THEME["text_dark"]).pack(side="left")
        UIHelper.create_button(header, "📥 Export Laporan Lengkap (.CSV)", self.export_laporan_csv, "success", pady=6).pack(side="right")

        body = tk.Frame(self.content_area, bg=THEME["bg_main"], padx=25, pady=20)
        body.pack(fill="both", expand=True)

        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM booking")
        tot_bk = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM booking WHERE status_booking IN ('BOOKED', 'BOOKED (BAYAR DITEMPAT)')")
        aktif_bk = cursor.fetchone()[0]
        cursor.execute("SELECT COALESCE(SUM(total_bayar), 0) FROM booking WHERE status_bayar = 'LUNAS'")
        tot_pendapatan = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM user WHERE role = 'user'")
        tot_user = cursor.fetchone()[0]

        cursor.execute("""
            SELECT f.nama_fasilitas, COUNT(b.id) as jml, COALESCE(SUM(CASE WHEN b.status_bayar='LUNAS' THEN b.total_bayar ELSE 0 END), 0)
            FROM fasilitas f LEFT JOIN booking b ON f.id = b.id_fasilitas
            GROUP BY f.id ORDER BY jml DESC
        """)
        stat_fasilitas = cursor.fetchall()
        conn.close()

        kpi_row = tk.Frame(body, bg=THEME["bg_main"])
        kpi_row.pack(fill="x", pady=(0, 20))

        v1, v2, v3, v4 = tk.StringVar(value=str(tot_bk)), tk.StringVar(value=str(aktif_bk)), tk.StringVar(value=UIHelper.format_rupiah(tot_pendapatan)), tk.StringVar(value=str(tot_user))
        c1 = UIHelper.create_kpi_card(kpi_row, "TOTAL RESERVASI", v1, THEME["primary"], "📋")
        c2 = UIHelper.create_kpi_card(kpi_row, "BOOKING AKTIF", v2, THEME["warning"], "⏳")
        c3 = UIHelper.create_kpi_card(kpi_row, "PENDAPATAN LUNAS", v3, THEME["success"], "💰")
        c4 = UIHelper.create_kpi_card(kpi_row, "TOTAL PENYEWA", v4, "#8b5cf6", "👥")

        for idx, c in enumerate((c1, c2, c3, c4)):
            c.grid(row=0, column=idx, sticky="nsew", padx=(0 if idx == 0 else 8, 0 if idx == 3 else 8))
            kpi_row.columnconfigure(idx, weight=1)

        card_chart, body_chart = UIHelper.create_card(body, "Visualisasi Tingkat Penggunaan & Pendapatan Per Fasilitas")
        card_chart.pack(fill="both", expand=True)

        canvas = tk.Canvas(body_chart, bg="white", highlightthickness=0, height=280)
        canvas.pack(fill="both", expand=True, pady=10)

        max_jml = max([x[1] for x in stat_fasilitas] + [1])
        bar_colors = ["#2563eb", "#16a34a", "#d97706", "#8b5cf6", "#0891b2", "#db2777"]

        for i, (nama_f, jml_b, omzet) in enumerate(stat_fasilitas):
            y_top = 15 + i * 42
            y_bot = y_top + 24
            bar_max_w = 360
            bar_w = int((jml_b / max_jml) * bar_max_w) if jml_b > 0 else 6
            color = bar_colors[i % len(bar_colors)]

            canvas.create_text(10, y_top + 12, text=nama_f, anchor="w", font=FONTS["body_bold"], fill=THEME["text_dark"])
            canvas.create_rectangle(210, y_top, 210 + bar_w, y_bot, fill=color, outline="")
            canvas.create_text(
                220 + bar_w, y_top + 12,
                text=f"{jml_b} Booking  |  Omzet Lunas: {UIHelper.format_rupiah(omzet)}",
                anchor="w", font=FONTS["small"], fill=THEME["text_muted"]
            )

    def export_laporan_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=f"Laporan_SpaceBook_{datetime.now().strftime('%Y%m%d')}.csv",
            filetypes=[("CSV Files", "*.csv")]
        )
        if not path:
            return
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.kode_booking, u.nama, u.no_hp, f.nama_fasilitas, f.jenis,
                   b.tanggal, b.jam_mulai, b.jam_selesai, b.durasi, b.total_harga,
                   b.diskon, b.total_bayar, b.status_booking, b.status_bayar, b.waktu_buat
            FROM booking b
            JOIN user u ON b.id_user = u.id
            JOIN fasilitas f ON b.id_fasilitas = f.id
            ORDER BY b.id DESC
        """)
        rows = cursor.fetchall()
        conn.close()

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Kode Booking", "Nama Penyewa", "No HP", "Fasilitas", "Kategori",
                "Tanggal", "Jam Mulai", "Jam Selesai", "Durasi (Jam)", "Subtotal",
                "Diskon", "Total Bayar", "Status Booking", "Status Bayar", "Waktu Transaksi"
            ])
            writer.writerows(rows)

        self.db.catat_log("admin", "EXPORT CSV", path)
        messagebox.showinfo("Export Berhasil", f"Laporan transaksi berhasil diekspor ke:\n{path}")

    def render_admin_bookings(self):
        header = tk.Frame(self.content_area, bg="white", padx=25, pady=18, highlightbackground=THEME["border"], highlightthickness=1)
        header.pack(fill="x")
        tk.Label(header, text="Validasi Pembayaran & Manajemen Status Booking", font=FONTS["title_md"], bg="white", fg=THEME["text_dark"]).pack(anchor="w")

        body = tk.Frame(self.content_area, bg=THEME["bg_main"], padx=25, pady=20)
        body.pack(fill="both", expand=True)

        filter_bar = tk.Frame(body, bg=THEME["bg_main"])
        filter_bar.pack(fill="x", pady=(0, 12))
        tk.Label(filter_bar, text="Filter Status:", font=FONTS["body_bold"], bg=THEME["bg_main"]).pack(side="left")
        self.cb_adm_filter = ttk.Combobox(
            filter_bar,
            values=["SEMUA", "MENUNGGU PEMBAYARAN", "MENUNGGU VERIFIKASI", "BOOKED", "SELESAI", "DIBATALKAN"],
            width=24, state="readonly", font=FONTS["body"]
        )
        self.cb_adm_filter.current(0)
        self.cb_adm_filter.pack(side="left", padx=10)
        UIHelper.create_button(filter_bar, "Terapkan Filter", self.muat_admin_bookings, "secondary", pady=4).pack(side="left")

        card_tbl, body_tbl = UIHelper.create_card(body, "Seluruh Transaksi Pemesanan")
        card_tbl.pack(fill="both", expand=True, pady=(0, 15))

        cols = ("Kode", "Penyewa", "Fasilitas", "Tanggal", "Jam", "Total", "Ref Bayar", "Status Booking", "Status Bayar")
        widths = (80, 130, 150, 95, 100, 110, 130, 145, 125)
        wrap, self.tree_adm_bk = UIHelper.create_styled_treeview(body_tbl, cols, widths, height=11)
        wrap.pack(fill="both", expand=True)

        act_card, act_body = UIHelper.create_card(body, "Aksi Validasi Administrator")
        act_card.pack(fill="x")

        btn_row = tk.Frame(act_body, bg="white")
        btn_row.pack(fill="x")
        UIHelper.create_button(btn_row, "✔ Verifikasi LUNAS (Approve)", lambda: self.ubah_status_booking("BOOKED", "LUNAS"), "success", pady=6).pack(side="left", padx=(0, 8))
        UIHelper.create_button(btn_row, "🏁 Tandai SELESAI", lambda: self.ubah_status_booking("SELESAI", "LUNAS"), "primary", pady=6).pack(side="left", padx=8)
        UIHelper.create_button(btn_row, "❌ Tolak Pembayaran / Batalkan", lambda: self.ubah_status_booking("DIBATALKAN", "DITOLAK"), "danger", pady=6).pack(side="left", padx=8)

        self.muat_admin_bookings()

    def muat_admin_bookings(self):
        for item in self.tree_adm_bk.get_children():
            self.tree_adm_bk.delete(item)

        flt = self.cb_adm_filter.get()
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = """
            SELECT b.kode_booking, u.nama, f.nama_fasilitas, b.tanggal, b.jam_mulai, b.jam_selesai,
                   b.total_bayar, COALESCE(p.referensi, '-'), b.status_booking, b.status_bayar
            FROM booking b
            JOIN user u ON b.id_user = u.id
            JOIN fasilitas f ON b.id_fasilitas = f.id
            LEFT JOIN pembayaran p ON b.id = p.id_booking
        """
        if flt != "SEMUA":
            query += " WHERE b.status_booking = ?"
            cursor.execute(query + " ORDER BY b.id DESC", (flt,))
        else:
            cursor.execute(query + " ORDER BY b.id DESC")

        for r in cursor.fetchall():
            self.tree_adm_bk.insert("", "end", values=(
                r[0], r[1], r[2], r[3], f"{r[4]}-{r[5]}", UIHelper.format_rupiah(r[6]), r[7], r[8], r[9]
            ))
        conn.close()

    def ubah_status_booking(self, st_booking, st_bayar):
        sel = self.tree_adm_bk.selection()
        if not sel:
            messagebox.showwarning("Pilih Baris", "Pilih transaksi yang ingin diubah statusnya!")
            return
        kode = self.tree_adm_bk.item(sel[0])["values"][0]

        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE booking SET status_booking = ?, status_bayar = ? WHERE kode_booking = ?",
                       (st_booking, st_bayar, kode))
        conn.commit()
        conn.close()

        self.db.catat_log("admin", "VALIDASI BOOKING", f"{kode} -> {st_booking} / {st_bayar}")
        messagebox.showinfo("Berhasil", f"Status {kode} berhasil diperbarui menjadi {st_booking} ({st_bayar}).")
        self.muat_admin_bookings()

    def render_admin_fasilitas(self):
        header = tk.Frame(self.content_area, bg="white", padx=25, pady=18, highlightbackground=THEME["border"], highlightthickness=1)
        header.pack(fill="x")
        tk.Label(header, text="Manajemen Data Fasilitas & Tarif Sewa", font=FONTS["title_md"], bg="white", fg=THEME["text_dark"]).pack(anchor="w")

        body = tk.Frame(self.content_area, bg=THEME["bg_main"], padx=25, pady=20)
        body.pack(fill="both", expand=True)

        card_f, body_f = UIHelper.create_card(body, "Tambah atau Perbarui Fasilitas")
        card_f.pack(fill="x", pady=(0, 15))

        grid = tk.Frame(body_f, bg="white")
        grid.pack(fill="x")

        tk.Label(grid, text="Nama Fasilitas:", font=FONTS["body_bold"], bg="white").grid(row=0, column=0, sticky="w", pady=5)
        self.ent_f_nama = tk.Entry(grid, font=FONTS["body"], width=28, relief="solid", bd=1)
        self.ent_f_nama.grid(row=0, column=1, padx=10, pady=5, ipady=3)

        tk.Label(grid, text="Kategori:", font=FONTS["body_bold"], bg="white").grid(row=0, column=2, sticky="w", pady=5)
        self.cb_f_jenis = ttk.Combobox(grid, values=["Olahraga", "Coworking"], width=18, state="readonly", font=FONTS["body"])
        self.cb_f_jenis.current(0)
        self.cb_f_jenis.grid(row=0, column=3, padx=10, pady=5)

        tk.Label(grid, text="Kapasitas (Org):", font=FONTS["body_bold"], bg="white").grid(row=1, column=0, sticky="w", pady=5)
        self.ent_f_kap = tk.Entry(grid, font=FONTS["body"], width=28, relief="solid", bd=1)
        self.ent_f_kap.insert(0, "10")
        self.ent_f_kap.grid(row=1, column=1, padx=10, pady=5, ipady=3)

        tk.Label(grid, text="Harga / Jam (Rp):", font=FONTS["body_bold"], bg="white").grid(row=1, column=2, sticky="w", pady=5)
        self.ent_f_harga = tk.Entry(grid, font=FONTS["body"], width=20, relief="solid", bd=1)
        self.ent_f_harga.insert(0, "100000")
        self.ent_f_harga.grid(row=1, column=3, padx=10, pady=5, ipady=3)

        tk.Label(grid, text="Deskripsi:", font=FONTS["body_bold"], bg="white").grid(row=2, column=0, sticky="w", pady=5)
        self.ent_f_desk = tk.Entry(grid, font=FONTS["body"], width=65, relief="solid", bd=1)
        self.ent_f_desk.grid(row=2, column=1, columnspan=3, padx=10, pady=5, sticky="w", ipady=3)

        btn_f = tk.Frame(body_f, bg="white")
        btn_f.pack(fill="x", pady=(10, 0))
        UIHelper.create_button(btn_f, "➕ Tambah Fasilitas Baru", self.tambah_fasilitas, "primary", pady=5).pack(side="left", padx=(0, 8))
        UIHelper.create_button(btn_f, "🗑️ Hapus Fasilitas Terpilih", self.hapus_fasilitas, "danger", pady=5).pack(side="left")

        card_t, body_t = UIHelper.create_card(body, "Daftar Fasilitas Terdaftar")
        card_t.pack(fill="both", expand=True)

        cols = ("ID", "Nama Fasilitas", "Kategori", "Kapasitas", "Harga/Jam", "Deskripsi")
        widths = (50, 180, 100, 90, 120, 320)
        wrap, self.tree_adm_fas = UIHelper.create_styled_treeview(body_t, cols, widths, height=8)
        wrap.pack(fill="both", expand=True)
        self.muat_admin_fasilitas()

    def muat_admin_fasilitas(self):
        for i in self.tree_adm_fas.get_children():
            self.tree_adm_fas.delete(i)
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nama_fasilitas, jenis, kapasitas, harga_per_jam, deskripsi FROM fasilitas")
        for r in cursor.fetchall():
            self.tree_adm_fas.insert("", "end", values=(r[0], r[1], r[2], f"{r[3]} Org", UIHelper.format_rupiah(r[4]), r[5]))
        conn.close()

    def tambah_fasilitas(self):
        nama = self.ent_f_nama.get().strip()
        jenis = self.cb_f_jenis.get()
        kap = self.ent_f_kap.get().strip()
        harga = self.ent_f_harga.get().strip()
        desk = self.ent_f_desk.get().strip()

        if not nama or not kap.isdigit() or not harga.isdigit():
            messagebox.showwarning("Input Tidak Valid", "Pastikan nama terisi serta kapasitas dan harga berupa angka!")
            return

        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO fasilitas (nama_fasilitas, jenis, kapasitas, harga_per_jam, deskripsi)
            VALUES (?, ?, ?, ?, ?)
        """, (nama, jenis, int(kap), int(harga), desk))
        conn.commit()
        conn.close()

        self.db.catat_log("admin", "TAMBAH FASILITAS", nama)
        messagebox.showinfo("Sukses", f"Fasilitas '{nama}' berhasil ditambahkan!")
        self.ent_f_nama.delete(0, tk.END)
        self.ent_f_desk.delete(0, tk.END)
        self.muat_admin_fasilitas()

    def hapus_fasilitas(self):
        sel = self.tree_adm_fas.selection()
        if not sel:
            messagebox.showwarning("Pilih Data", "Pilih fasilitas yang ingin dihapus!")
            return
        vals = self.tree_adm_fas.item(sel[0])["values"]
        id_f, nama_f = vals[0], vals[1]

        if messagebox.askyesno("Konfirmasi Hapus", f"Hapus fasilitas '{nama_f}' beserta data booking terkait?"):
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM fasilitas WHERE id = ?", (id_f,))
            conn.commit()
            conn.close()
            self.db.catat_log("admin", "HAPUS FASILITAS", nama_f)
            self.muat_admin_fasilitas()

    def render_admin_promo(self):
        header = tk.Frame(self.content_area, bg="white", padx=25, pady=18, highlightbackground=THEME["border"], highlightthickness=1)
        header.pack(fill="x")
        tk.Label(header, text="Manajemen Kode Promo & Voucher Diskon", font=FONTS["title_md"], bg="white", fg=THEME["text_dark"]).pack(anchor="w")

        body = tk.Frame(self.content_area, bg=THEME["bg_main"], padx=25, pady=20)
        body.pack(fill="both", expand=True)

        card_p, body_p = UIHelper.create_card(body, "Buat Kode Promo Baru")
        card_p.pack(fill="x", pady=(0, 15))

        row = tk.Frame(body_p, bg="white")
        row.pack(fill="x")
        tk.Label(row, text="Kode:", font=FONTS["body_bold"], bg="white").pack(side="left")
        self.ent_p_kode = tk.Entry(row, font=FONTS["body"], width=16, relief="solid", bd=1)
        self.ent_p_kode.pack(side="left", padx=8, ipady=3)

        tk.Label(row, text="Diskon (%):", font=FONTS["body_bold"], bg="white").pack(side="left")
        self.ent_p_persen = tk.Entry(row, font=FONTS["body"], width=8, relief="solid", bd=1)
        self.ent_p_persen.pack(side="left", padx=8, ipady=3)

        tk.Label(row, text="Keterangan:", font=FONTS["body_bold"], bg="white").pack(side="left")
        self.ent_p_ket = tk.Entry(row, font=FONTS["body"], width=30, relief="solid", bd=1)
        self.ent_p_ket.pack(side="left", padx=8, ipady=3)

        UIHelper.create_button(row, "Simpan Promo", self.tambah_promo, "success", pady=4).pack(side="left", padx=8)

        card_t, body_t = UIHelper.create_card(body, "Daftar Kode Promo")
        card_t.pack(fill="both", expand=True)

        cols = ("ID", "Kode Promo", "Diskon (%)", "Keterangan", "Status")
        widths = (60, 150, 100, 350, 100)
        wrap, self.tree_promo = UIHelper.create_styled_treeview(body_t, cols, widths, height=9)
        wrap.pack(fill="both", expand=True)
        self.muat_promo()

    def muat_promo(self):
        for i in self.tree_promo.get_children():
            self.tree_promo.delete(i)
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, kode_promo, diskon_persen, keterangan, status FROM promo")
        for r in cursor.fetchall():
            self.tree_promo.insert("", "end", values=(r[0], r[1], f"{r[2]}%", r[3], r[4]))
        conn.close()

    def tambah_promo(self):
        kode = self.ent_p_kode.get().strip().upper()
        persen = self.ent_p_persen.get().strip()
        ket = self.ent_p_ket.get().strip()
        if not kode or not persen.isdigit() or not (1 <= int(persen) <= 100):
            messagebox.showwarning("Validasi", "Isi kode promo dan angka diskon (1 - 100)!")
            return
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO promo (kode_promo, diskon_persen, keterangan) VALUES (?, ?, ?)", (kode, int(persen), ket))
            conn.commit()
            conn.close()
            self.muat_promo()
            messagebox.showinfo("Sukses", f"Promo {kode} berhasil ditambahkan!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Kode promo sudah ada!")

    def render_admin_users(self):
        header = tk.Frame(self.content_area, bg="white", padx=25, pady=18, highlightbackground=THEME["border"], highlightthickness=1)
        header.pack(fill="x")
        tk.Label(header, text="Daftar Pengguna & Penyewa Terdaftar", font=FONTS["title_md"], bg="white", fg=THEME["text_dark"]).pack(anchor="w")

        body = tk.Frame(self.content_area, bg=THEME["bg_main"], padx=25, pady=20)
        body.pack(fill="both", expand=True)

        card_t, body_t = UIHelper.create_card(body, "Database Akun Pengguna")
        card_t.pack(fill="both", expand=True)

        cols = ("ID", "Nama Lengkap", "No. HP", "Email", "Username", "Role", "Tanggal Daftar")
        widths = (50, 180, 130, 180, 120, 90, 140)
        wrap, tree_u = UIHelper.create_styled_treeview(body_t, cols, widths, height=14)
        wrap.pack(fill="both", expand=True)

        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nama, no_hp, COALESCE(email, '-'), username, role, tanggal_daftar FROM user")
        for r in cursor.fetchall():
            tree_u.insert("", "end", values=r)
        conn.close()

    def render_admin_logs(self):
        header = tk.Frame(self.content_area, bg="white", padx=25, pady=18, highlightbackground=THEME["border"], highlightthickness=1)
        header.pack(fill="x")
        tk.Label(header, text="Audit Trail & Log Aktivitas Sistem", font=FONTS["title_md"], bg="white", fg=THEME["text_dark"]).pack(anchor="w")

        body = tk.Frame(self.content_area, bg=THEME["bg_main"], padx=25, pady=20)
        body.pack(fill="both", expand=True)

        card_t, body_t = UIHelper.create_card(body, "Riwayat Aktivitas Real-Time")
        card_t.pack(fill="both", expand=True)

        cols = ("ID", "Waktu", "Aktor", "Jenis Aksi", "Detail Keterangan")
        widths = (60, 160, 130, 180, 360)
        wrap, tree_l = UIHelper.create_styled_treeview(body_t, cols, widths, height=15)
        wrap.pack(fill="both", expand=True)

        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, waktu, aktor, aksi, detail FROM log_aktivitas ORDER BY id DESC LIMIT 100")
        for r in cursor.fetchall():
            tree_l.insert("", "end", values=r)
        conn.close()

# ==============================================================================
# MODUL 8: CONTROLLER UTAMA APLIKASI (MAIN ENTRY POINT)
# ==============================================================================
class SpaceBookEnterpriseController:
    def __init__(self, root):
        self.root = root
        self.root.title("SPACE-BOOK ENTERPRISE v2.0 | Smart Reservation & Booking Management System")
        self.root.geometry("1180x720")
        self.root.minsize(1024, 640)
        self.root.configure(bg=THEME["bg_main"])

        self.db = DatabaseManager()
        self.engine = BookingEngine(self.db)
        self.current_user = None
        self.current_view = None

        self._setup_global_styles()
        self.show_auth_view()

    def _setup_global_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background=THEME["bg_card"], borderwidth=0)
        style.configure("TNotebook.Tab", font=FONTS["body_bold"], padding=[16, 8], background="#e2e8f0", foreground=THEME["text_dark"])
        style.map("TNotebook.Tab", background=[("selected", THEME["primary"])], foreground=[("selected", "white")])
        style.configure("Treeview.Heading", font=FONTS["body_bold"], background="#e2e8f0", foreground=THEME["text_dark"], relief="flat")
        style.configure("Treeview", font=FONTS["small"], rowheight=28, background="white", fieldbackground="white")
        style.map("Treeview", background=[("selected", "#bfdbfe")], foreground=[("selected", THEME["text_dark"])])

    def _switch_view(self, view_class):
        if self.current_view is not None:
            self.current_view.destroy()
        self.current_view = view_class(self.root, self)
        self.current_view.pack(fill="both", expand=True)

    def show_auth_view(self):
        self.current_user = None
        self._switch_view(AuthView)

    def login_success(self, user_data):
        self.current_user = user_data
        if user_data["role"] == "admin":
            self._switch_view(AdminDashboardView)
        else:
            self._switch_view(UserDashboardView)

    def logout(self):
        if self.current_user:
            self.db.catat_log(self.current_user["username"], "LOGOUT", "Keluar dari sistem")
        self.show_auth_view()

if __name__ == "__main__":
    root = tk.Tk()
    app = SpaceBookEnterpriseController(root)
    root.mainloop()