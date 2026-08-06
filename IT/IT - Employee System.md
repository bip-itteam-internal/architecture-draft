## Deskripsi

*Ringkasan hal-hal yang dapat dilakukan **tim IT** di dalam ERP. Sebagian besar operasi admin IT berjalan lewat [[CORE - IT Orchestrator]] (semua route ber-guard `RequireITStaff`) dan diakses dari modul **IT** pada [[APP - Web ERP]].*

- **Status**: ✅ Implemented — operasi admin IT (akun aktif/nonaktif, reset, device, roles) via [[CORE - IT Orchestrator]] (guard RequireITStaff). ⚠️ **Penonaktifan akun bukan lagi eksklusif IT**: HR punya jalur kedua lewat catatan resign ([[ADR - 0035 HR Menonaktifkan Akun lewat Catatan Resign]]; ✅ live di produksi 2026-08-05).

## Yang Bisa Dilakukan Tim IT

### Manajemen Akun Karyawan
- **Aktifkan / nonaktifkan akun** karyawan (`is_active`) — menonaktifkan akun menghilangkan kemampuan karyawan login ke sistem perusahaan. (`/account/activate|deactivate|status|toggle`)
	- ⚠️ **Bukan satu-satunya jalur lagi.** HR menonaktifkan akun sendiri lewat catatan resign di [[HRIS - Personalia]], karena berhentinya karyawan adalah peristiwa HR dan meneruskannya sebagai permintaan ke IT membuat akses tetap hidup selama jeda itu. Keduanya menulis lewat fungsi yang **sama** (`terapkanStatusAkun` di [[Microservices - Employee Service]]), jadi perilakunya tak bisa menyimpang diam-diam. Gerbang jalur IT ini **tidak** dilonggarkan, dan HR tidak mendapat saklar telanjang — satu-satunya cara HR menonaktifkan akun adalah lewat catatan yang wajib memuat kategori, tanggal, dan alasan. Rinciannya: [[ADR - 0035 HR Menonaktifkan Akun lewat Catatan Resign]].
	- Sebaliknya berlaku juga: akun yang **IT** nonaktifkan tak akan ikut hidup kembali bila HR membatalkan catatan resign atas orang yang sama, karena pembatalan hanya menghidupkan akun yang dimatikan catatan itu sendiri.
- **Reset akun** karyawan — reset password ke `employee_id`, **clear PIN & device** (1-akun-1-device), role dipertahankan; sistem mengirim notif WhatsApp (akun di-reset) sehingga karyawan melakukan onboarding ulang. (`/reset-password`)
- **Reset perangkat tertaut** — saat reset akun, **seluruh registered device karyawan dibersihkan** (kebijakan 1-akun-1-device). Dengan ini karyawan bisa login di **perangkat berbeda** meskipun akunnya sebelumnya masih tertaut ke device lama (mis. ganti HP). Sistem melaporkan jumlah device yang dibersihkan (`devices_cleared`). Selain lewat reset akun, ada **endpoint khusus `/account/forget-device`** (Employee Service) yang me-revoke semua device & browser **tanpa** reset password — pas untuk ganti HP tanpa mengganggu kredensial; lihat [[Microservices - Employee Service]].

### Manajemen Role & Akses
- **Lihat / set `system_roles`** karyawan (peta `module → role`) — menentukan modul & level akses (admin/supervisor/staff/security, dll) yang dipakai gateway untuk otorisasi. (`/roles/get`, `/roles/set`)
- *(Role per-departemen sudah ada di kode tetapi endpoint-nya masih di-comment — belum diekspos.)*

### Manajemen Jaringan WiFi Kantor
- **Lihat / tambah / hapus** WiFi allow-list (SSID/MAC) kantor — dipakai sebagai validasi geofencing saat clock-in via mobile. Diproxy ke [[Microservices - Attendance Service]] (`/network` GET/POST/DELETE → `/networks`, `/internal/wifi/add|delete`).

### IT Helpdesk / Ticketing
- Divisi IT menjadi **pengelola IT Helpdesk**: menerima, mentriase, dan menyelesaikan tiket yang dibuat **semua divisi** melalui [[APP - Dynamic Task Tracker]] / [[Microservices - Task Management Service]] (Kanban, approval, SLA).

### IT Support & Monitoring
- **IT Support**: menyediakan daftar kontak helpdesk IT (termasuk WhatsApp) untuk karyawan.
- **Monitoring login logs** karyawan (fitur it-admin) — lihat juga [[IT - Monitoring System]].
- **Akses agregat data karyawan untuk IT** (`/v2/multi` → employee aggregate `/it`).

## Komponen Terlibat

- [[CORE - IT Orchestrator]] — mesin operasi admin IT (roles, reset password, status akun, network)
- [[Microservices - Employee Service]] — sumber data akun/role (`system_authentication`, `system_roles`)
- [[Microservices - Attendance Service]] — endpoint WiFi allow-list
- [[Microservices - Notification Service]] — notif WhatsApp (akun di-reset)
- [[CORE - API Master Gateway]] — routing `/api/it/*` + enforce JWT
- [[APP - Web ERP]] — UI modul IT (Employee, Network, KPI, IT Support)

## Dokumen Terkait

- [[IT - Big Pictures]]
- [[IT - Monitoring System]]
- [[APP - Dynamic Task Tracker]]
