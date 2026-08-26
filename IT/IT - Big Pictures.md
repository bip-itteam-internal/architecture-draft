
Departemen IT menyediakan dukungan/teknis untuk seluruh perusahaan, sekaligus mengelola infrastruktur, deployment, jaringan, akun & akses, serta keandalan sistem ERP. Dokumen ini adalah peta domain IT.

- **Status**: 🟡 Overview — peta domain IT; tiap area berstatus sendiri di dok masing-masing.

## Ruang Lingkup Domain IT

- **Ringkasan divisi** — halaman `/it` di [[APP - Web ERP]]: satu layar yang meringkas kesehatan infrastruktur, helpdesk, skor KPI tim, dan **indeks layanan** (bagaimana karyawan di luar tim menilai layanan divisi ini tiap bulan; lihat [[IT - Form Builder]]). Ia **pintu, bukan tujuan** — tiap angka menautkan ke modul yang memiliki daftar dan aksinya, sehingga tak ada dua tempat yang bisa berbeda pendapat. Sejajar `/finance` dan `/hris`, tapi sengaja tanpa sumbu posisi; alasannya di dok itu. ✅ Merged; kartu indeks layanan menyusul 2026-08-25 dan **belum di-deploy**.
- **Layanan & dukungan** — [[IT - Helpdesk]] (ticketing): tim IT menangani tiket dari semua divisi
- **Manajemen akun & akses** — [[IT - Employee System]]: aktif/nonaktif akun, reset akun, set role, reset perangkat tertaut
- **Infrastruktur** — [[IT - Server, VMs and Databases]] (server/VM/DB) & [[IT - Network Management]] (LAN/WiFi/perangkat)
- **Deployment** — [[IT - CI-CD]] (GitHub Actions self-hosted runner; Codemagic untuk mobile)
- **Pemantauan & keandalan** — [[IT - Monitoring System]] & [[IT - Backup & DR]]
- **Tools pengembangan** — [[IT - Development Apps and Tools]]
- **Keamanan** — [[IT - Security]]: konsolidasi kontrol keamanan (auth/RBAC, jaringan, secret, backup) + peta gap (incident response, patch, proteksi data)

## Infra Inti di Core System

Beberapa komponen inti yang berkaitan erat dengan IT didokumentasikan di folder **Core System and Modules** (karena shared lintas-domain):

- [[CORE - API Master Gateway]] — gateway tunggal + auth
- [[CORE - SSO Flow]] — Single Sign-On antar aplikasi internal
- [[DB - Overview and Notes]] — database per service

## Dependencies

- [ ] [[BASE - Enterance Point]]
- [ ] [[IT - Helpdesk]]
- [ ] [[IT - Employee System]]
- [ ] [[IT - Server, VMs and Databases]]
- [ ] [[IT - Network Management]]
- [ ] [[IT - Monitoring System]]
- [ ] [[IT - Backup & DR]]
- [ ] [[IT - CI-CD]]
- [ ] [[IT - Development Apps and Tools]]
- [ ] [[IT - Security]]
