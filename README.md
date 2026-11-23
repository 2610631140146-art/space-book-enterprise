# space-book-enterprise
SPACE-BOOK Enterprise adalah sistem manajemen reservasi dan pemesanan berbasis desktop yang dirancang secara komprehensif untuk mengelola penyewaan fasilitas olahraga (seperti lapangan futsal, badminton) serta ruang kerja bersama (coworking space) secara terintegrasi.
Dibangun menggunakan bahasa pemrograman Python dengan antarmuka grafis Tkinter serta penyimpanan basis data relasional SQLite, aplikasi ini mengusung arsitektur modular yang memisahkan komponen logika, antarmuka, dan manajemen data guna menjaga integritas fungsionalitas sistem.

Fitur Utama Sistem:
Multi-User Role-Based Access (Admin & Pengguna):

Portal Pengguna (Penyewa): Memungkinkan penyewa untuk mendaftar akun, masuk ke sistem, memilih fasilitas, melakukan pemesanan, melihat matriks ketersediaan jadwal secara real-time, memasukkan kode promo diskon, serta mengelola riwayat transaksi.

Panel Administrator: Memberikan hak akses penuh bagi pengelola untuk memantau statistik dan grafik penggunaan fasilitas, melakukan validasi status pembayaran atau booking (approve/reject), mengelola data fasilitas dan kode promo, serta melihat log audit aktivitas (audit trail) sistem.

Validasi Bentrok Jadwal Otomatis (Booking Engine): Mencegah terjadinya pemesanan ganda pada waktu dan fasilitas yang sama secara otomatis demi kelancaran operasional.

Manajemen Pembayaran & Tiket Elektronik: Mendukung pencatatan metode pembayaran serta fitur pembuatan bukti transaksi atau tiket digital.

Pelaporan & Ekspor Data: Memungkinkan administrator untuk mengeksport data laporan transaksi dan operasional ke dalam format
