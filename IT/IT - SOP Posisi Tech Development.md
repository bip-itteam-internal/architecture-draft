## Deskripsi

*Salinan **16 dokumen SOP** posisi **Tech Development** (unit Tech Development) PT Bharata Internasional Pharmaceutical, diambil dari kumpulan "SOP BHARATA 2026". Isinya proses kerja yang dijalankan orang, disalin apa adanya dari dokumen sumber, bukan gambaran perilaku sistem ERP.*

- **Status**: 🟡 **Rekaman SOP (proses bisnis, non-kode).** Kepatuhan sistem ERP terhadap SOP ini belum dipetakan (TBD).
- **Sumber**: `SOP BHARATA 2026/TECH DEVELOPMENT` (ekspor Google Drive 2026-10-10, di luar repo). Dokumen sumber yang menang bila salinan ini berbeda.
- **Disusun oleh (jabatan)**: Supervisor Tech Dev
- **Disetujui oleh (jabatan)**: Direktur
- **Peta seluruh posisi**: [[REF - SOP Bharata 2026 per Posisi]]

## Daftar SOP

| No | Dokumen | No. dokumen | Tanggal |
|---|---|---|---|
| 1 | 1. SOP Development Modul ERP | 001/IT/SOP/IV/2026 | 23-Apr-2026 |
| 2 | 2. SOP Testing Modul ERP | 002/IT/SOP/IV/2026 | 23-Apr-2026 |
| 3 | 3. SOP Deployment Modul ERP | 003/IT/SOP/IV/2026 | 23-Apr-2026 |
| 4 | 4. SOP Delivery Modul ERP | 004/IT/SOP/IV/2026 | 23-Apr-2026 |
| 5 | 5. SOP Bug Fixing | 005/IT/SOP/IV/2026 | 23-Apr-2026 |
| 6 | 6. SOP Perbaikan Laptop | 006/IT/SOP/IV/2026 | 23-Apr-2026 |
| 7 | 7. SOP Perbaikan Printer | 007/IT/SOP/IV/2026 | 23-Apr-2026 |
| 8 | 8. SOP Troubleshooting Jaringan Internet | 008/IT/SOP/IV/2026 | 23-Apr-2026 |
| 9 | 9. SOP Sistem Down | 009/IT/SOP/IV/2026 | 23-Apr-2026 |
| 10 | 10. SOP Server Down | 010/IT/SOP/IV/2026 | 23-Apr-2026 |
| 11 | 011. SOP E-Ticket Permintaan Pengembangan Software | 011/IT/SOP/VI/2026 | 05-Jun-2026 |
| 12 | 012. SOP Pemberian Akses Saat Onboarding Karyawan | 012/IT/SOP/VI/2026 | 08-Jun-2026 |
| 13 | 013. SOP Pencabutan Akses Saat Resign Karyawan | 013/IT/SOP/VI/2026 | 08-Jun-2026 |
| 14 | Berita Acara Pemberian Akses Karyawan Baru |   |   |
| 15 | Berita Acara Pencabutan Akses Karyawan |   |   |
| 16 | Template Blueprint Flowchart |   |   |

## Catatan Penyalinan

- Teks, urutan langkah, dan tabel disalin apa adanya, termasuk salah ketik di dokumen sumber. Tidak ada yang dirangkum atau ditambah.
- Nama orang di blok tanda tangan sengaja tidak disalin; yang dicatat hanya jabatannya.
- Flowchart berupa gambar: yang tersalin hanya teks kotaknya. Bentuk alur yang sah tetap di dokumen sumber.
- Kolom "No. dokumen" dan "Tanggal" diambil dari kop dokumen; kosong berarti kopnya tidak memuat nilai itu.

## 1. SOP Development Modul ERP

**Berkas sumber**: `1. SOP_Development_Modul_ERP.docx` · **No. dokumen**: 001/IT/SOP/IV/2026 · **Revisi**: 00 · **Tanggal**: 23-Apr-2026 · **Disusun oleh**: Supervisor Tech Dev · **Disetujui oleh**: Direktur

### Tujuan

Memberikan panduan yang jelas dan terstruktur bagi tim pengembang dalam proses pengembangan modul ERP, sehingga pengembangan berjalan secara sistematis, efisien, dan sesuai dengan standar kualitas yang ditetapkan.

### Ruang Lingkup

SOP ini berlaku untuk seluruh proses pengembangan modul ERP yang dilakukan oleh tim IT Development, mulai dari tahap analisis kebutuhan, perancangan sistem, pengembangan, pengujian, hingga serah terima modul kepada pengguna.

### Penanggung Jawab

1. Project Manager (PM): Bertanggung jawab menganalisa, mengkoordinasikan, merencanakan, dan memantau seluruh proses pengembangan modul ERP.
2. Developer / Programmer: Bertanggung jawab menulis kode program sesuai desain yang telah ditetapkan dan disepakati.
3. Quality Assurance (QA) dilakukan oleh User: Bertanggung jawab melakukan pengujian fungsional dan memastikan modul bebas dari bug.

### Definisi

1. ERP (Enterprise Resource Planning): Sistem informasi terintegrasi yang digunakan untuk mengelola dan mengintegrasikan proses bisnis utama dalam satu platform.
2. Modul ERP: Komponen fungsional dalam sistem ERP yang menangani area bisnis tertentu, seperti keuangan, inventori, atau SDM.
3. UAT (User Acceptance Testing): Proses pengujian yang dilakukan oleh pengguna akhir untuk memverifikasi bahwa sistem memenuhi kebutuhan dan persyaratan bisnis.
4. Bug: Kesalahan atau cacat pada program yang menyebabkan sistem tidak berjalan sesuai yang diharapkan.
5. SKS (Spesifikasi Kebutuhan Sistem): Dokumen yang mendeskripsikan kebutuhan fungsional dan non-fungsional dari sistem yang akan dikembangkan.

### Rincian Prosedur

1. Analisis Kebutuhan: PM mengumpulkan, menganalisis, dan mendokumentasikan kebutuhan pengguna dalam dokumen Spesifikasi Kebutuhan Sistem (SKS). Dokumen SKS harus disetujui oleh stakeholder terkait sebelum proses perancangan dimulai.
2. Perancangan Sistem: PM membuat desain teknis modul yang meliputi ERD (Entity Relationship Diagram), wireframe tampilan antarmuka, dan arsitektur sistem. Hasil perancangan harus direview dan disetujui oleh PM.
3. Pengembangan (Coding): Developer menulis kode program berdasarkan desain yang telah disetujui. Setiap developer wajib mengikuti standar penulisan kode (coding standard) yang telah ditetapkan perusahaan. Kemajuan pengembangan dilaporkan kepada PM secara berkala.
4. Pengujian Internal: QA dalam hal ini User melakukan pengujian fungsional menggunakan test case yang telah disiapkan. Setiap bug yang ditemukan dicatat dalam bug tracking system dan dilaporkan kepada developer yang bertanggung jawab.
5. Perbaikan Bug: Developer memperbaiki bug yang ditemukan oleh QA. Setiap perbaikan harus didokumentasikan dan diuji ulang oleh QA untuk memastikan bug telah terselesaikan.
6. Dokumentasi: Tim membuat dokumen teknis (technical documentation) dan panduan pengguna (user manual) sebelum modul diluncurkan ke lingkungan produksi jika diperlukan.
7. Serah Terima (Go-Live): Modul yang telah lulus UAT di-deploy ke lingkungan produksi. Serah terima modul kepada pengguna disertai dengan penandatanganan Berita Acara Serah Terima oleh pengguna dan PM.

### Dokumen Pendukung atau Lampiran

1. Dokumen perencanaan
2. User Manual / Panduan Pengguna (optional)

### Distribusi Dokumen

1. Departemen IT (Development Team, PM)
2. Departemen pengguna yang terkait dengan modul ERP yang dikembangkan

### Flowchart

Mulai → Analisis Kebutuhan → Perancangan Sistem → Pengembangan (Coding) → Pengujian Internal (Developer) → Bug Ditemukan? → Ya: Perbaikan Bug (kembali ke Pengujian) → Tidak: UAT → Revisi UAT? → Ya: Perbaikan (kembali ke UAT) → Tidak: Dokumentasi → Serah Terima (Go-Live) → Selesai

## 2. SOP Testing Modul ERP

**Berkas sumber**: `2. SOP_Testing_Modul_ERP.docx` · **No. dokumen**: 002/IT/SOP/IV/2026 · **Revisi**: 00 · **Tanggal**: 23-Apr-2026 · **Disusun oleh**: Supervisor Tech Dev · **Disetujui oleh**: Direktur

### Tujuan

Memastikan seluruh modul ERP yang dikembangkan berfungsi sesuai spesifikasi dan kebutuhan pengguna sebelum diluncurkan ke lingkungan produksi.

### Ruang Lingkup

SOP ini berlaku untuk seluruh proses pengujian modul ERP, mulai dari pengujian unit oleh Developer, pengujian penerimaan oleh User, hingga persetujuan final oleh PM.

### Penanggung Jawab

1. PM (Project Manager): Bertanggung jawab menyetujui rencana pengujian, memantau progress, dan memberikan keputusan final atas hasil UAT.
2. Developer: Bertanggung jawab menyiapkan test case, melakukan pengujian unit dan integrasi, serta memperbaiki bug yang ditemukan selama proses pengujian.
3. User: Bertanggung jawab melakukan User Acceptance Testing (UAT) sesuai skenario penggunaan nyata dan memberikan persetujuan atas hasil pengujian.

### Definisi

1. Test Case: Dokumen berisi skenario, langkah pengujian, dan hasil yang diharapkan untuk memvalidasi fungsi sistem.
2. Bug: Kesalahan atau cacat pada program yang menyebabkan sistem tidak berjalan sesuai yang diharapkan.
3. UAT (User Acceptance Testing): Proses pengujian yang dilakukan User untuk memverifikasi sistem memenuhi kebutuhan bisnis.
4. Regression Testing: Pengujian ulang setelah perbaikan bug untuk memastikan perubahan tidak menimbulkan masalah baru.
5. Test Environment: Lingkungan pengujian yang terpisah dari lingkungan produksi.

### Rincian Prosedur

1. Persiapan Pengujian: Developer menyiapkan test case berdasarkan spesifikasi kebutuhan sistem. PM mereview dan menyetujui test case sebelum pengujian dimulai.
2. Pengujian Unit: Developer melakukan pengujian terhadap setiap fungsi atau komponen modul secara individual untuk memastikan masing-masing bekerja dengan benar.
3. Pengujian Integrasi: PM / Developer menguji interaksi antar modul dan komponen untuk memastikan sistem berjalan secara terintegrasi.
4. Perbaikan Bug Internal: Bug yang ditemukan dicatat dan diperbaiki oleh Developer. Setiap perbaikan dilakukan regression testing ulang.
5. UAT (User Acceptance Testing): User melakukan pengujian sesuai skenario nyata. Setiap temuan dicatat dalam Bug Report dan diserahkan ke Developer.
6. Perbaikan Bug UAT: Developer memperbaiki bug hasil UAT. Perbaikan harus diverifikasi ulang oleh User sebelum dinyatakan selesai.
7. Persetujuan dan Penutupan: Setelah semua bug terselesaikan, PM dan User menandatangani Berita Acara UAT.

### Dokumen Pendukung atau Lampiran (Optional)

1. Test Plan Document
2. Test Case Document
3. Bug Report Form
4. Bug Tracking Log
5. Berita Acara UAT

### Distribusi Dokumen

1. Departemen IT (Developer, PM)
2. Departemen User terkait
3. Manajemen

### Flowchart

Mulai - Persiapan Test Case - Pengujian Unit (Developer) - Bug? - Ya: Perbaikan - Pengujian Integrasi - Bug? - Ya: Perbaikan - UAT (User) - Bug? - Ya: Perbaikan - Tidak: Persetujuan PM dan User - Berita Acara UAT – Selesai

## 3. SOP Deployment Modul ERP

**Berkas sumber**: `3. SOP_Deployment_Modul_ERP.docx` · **No. dokumen**: 003/IT/SOP/IV/2026 · **Revisi**: 00 · **Tanggal**: 23-Apr-2026 · **Disusun oleh**: Supervisor Tech Dev · **Disetujui oleh**: Direktur

### Tujuan

Memastikan proses deployment modul ERP dari lingkungan staging ke produksi berjalan dengan aman, terkendali, dan minim risiko gangguan operasional.

### Ruang Lingkup

SOP ini berlaku untuk seluruh proses deployment modul ERP baru maupun pembaruan modul yang sudah ada ke lingkungan produksi.

### Penanggung Jawab

1. PM (Project Manager): Bertanggung jawab menjadwalkan deployment, mengkoordinasikan seluruh pihak, dan memberikan keputusan Go/No-Go.
2. Developer: Bertanggung jawab menyiapkan paket deployment, melakukan backup, menjalankan proses deployment, dan memastikan sistem berjalan pasca deployment.
3. User: Bertanggung jawab melakukan verifikasi fungsional pasca deployment dan mengkonfirmasi sistem dapat digunakan kembali.

### Definisi

1. Deployment: Proses penerapan aplikasi/modul ke lingkungan yang dituju (staging atau produksi).
2. Staging Environment: Lingkungan pra-produksi untuk validasi akhir sebelum deployment ke produksi.
3. Production Environment: Lingkungan operasional nyata yang digunakan User sehari-hari.
4. Rollback: Proses mengembalikan sistem ke versi sebelumnya jika deployment bermasalah.
5. Deployment Window: Jangka waktu terjadwal untuk deployment, umumnya di luar jam kerja utama.

### Rincian Prosedur

1. Persiapan Deployment: Developer menyiapkan deployment package dan checklist. PM menjadwalkan deployment window dan menginformasikan User.
2. Backup Data dan Sistem: Developer melakukan backup lengkap database dan konfigurasi. Backup harus diverifikasi sebelum melanjutkan.
3. Deployment ke Staging: Developer deploy ke staging environment dan melakukan verifikasi fungsional.
4. Go/No-Go Decision: PM dan Developer mengevaluasi hasil staging. Jika ada masalah kritis, deployment ke produksi ditunda.
5. Deployment ke Production: Developer melakukan deployment ke produksi pada deployment window yang telah dijadwalkan.
6. Verifikasi Pasca Deployment: Developer melakukan pengecekan teknis dan User melakukan verifikasi fungsional.
7. Rollback jika Diperlukan: Jika ada masalah kritis, Developer melakukan rollback ke versi sebelumnya dan PM menginformasikan User.
8. Notifikasi Selesai: PM menginformasikan bahwa deployment berhasil dan sistem dapat digunakan kembali.

### Dokumen Pendukung atau Lampiran (Optional)

1. Deployment Plan dan Checklist
2. Backup Verification Log
3. Deployment Log
4. Rollback Plan
5. Berita Acara Deployment

### Distribusi Dokumen

1. Departemen IT (Developer, PM)
2. Seluruh User terkait modul ERP
3. Manajemen

### Flowchart

Mulai - Persiapan dan Penjadwalan - Backup Data dan Sistem - Deploy ke Staging - Verifikasi Staging - Masalah? - Ya: Perbaikan - Go/No-Go Decision - Go: Deploy ke Production - Verifikasi Production - Masalah Kritis? - Ya: Rollback - Notifikasi User – Selesai

## 4. SOP Delivery Modul ERP

**Berkas sumber**: `4. SOP_Delivery_Modul_ERP.docx` · **No. dokumen**: 004/IT/SOP/IV/2026 · **Revisi**: 00 · **Tanggal**: 23-Apr-2026 · **Disusun oleh**: Supervisor Tech Dev · **Disetujui oleh**: Direktur

### Tujuan

Memastikan proses serah terima modul ERP kepada pengguna berjalan sesuai prosedur, disertai pelatihan yang memadai, dan terdokumentasi dengan baik.

### Ruang Lingkup

SOP ini berlaku untuk seluruh proses serah terima modul ERP yang telah selesai dikembangkan dan diuji kepada departemen pengguna, termasuk pelatihan dan pendampingan awal.

### Penanggung Jawab

1. PM (Project Manager): Bertanggung jawab mengkoordinasikan seluruh proses delivery, memastikan kesiapan modul, dan menandatangani dokumen serah terima.
2. Developer: Bertanggung jawab menyiapkan user manual, melakukan demo sistem, memberikan pelatihan kepada User, dan memberikan dukungan teknis selama masa transisi.
3. User: Bertanggung jawab mengikuti pelatihan, melakukan verifikasi penerimaan modul, dan menandatangani Berita Acara Serah Terima.

### Definisi

1. Delivery: Proses penyerahan modul ERP yang telah siap pakai kepada departemen pengguna.
2. Go-Live: Kondisi dimana modul ERP mulai digunakan secara resmi dalam operasional.
3. User Manual: Dokumen panduan penggunaan sistem yang membantu pengguna mengoperasikan modul ERP.
4. Handover: Proses perpindahan tanggung jawab pengelolaan dari tim Developer kepada pengguna.
5. Hypercare Period: Masa pendampingan intensif oleh Developer setelah go-live, biasanya 1-2 minggu.

### Rincian Prosedur

1. Verifikasi Kesiapan Modul: PM memastikan checklist delivery terpenuhi - modul lulus UAT, dokumentasi lengkap, dan environment produksi siap.
2. Penyiapan Materi Pelatihan: Developer menyiapkan user manual dan materi pelatihan yang mudah dipahami sesuai kebutuhan User.
3. Pelaksanaan Pelatihan: Developer memberikan pelatihan penggunaan modul kepada User mencakup fitur utama, alur kerja, dan penanganan situasi umum.
4. Demo dan Tanya Jawab: Developer melakukan demo langsung dan membuka sesi tanya jawab untuk memastikan User memahami sistem.
5. Go-Live: Modul ERP mulai digunakan secara resmi. PM mengumumkan go-live kepada seluruh stakeholder.
6. Pendampingan Awal (Hypercare): Developer memberikan pendampingan intensif kepada User selama 1-2 minggu pertama.
7. Serah Terima Resmi: PM dan User menandatangani Berita Acara Serah Terima sebagai bukti resmi perpindahan tanggung jawab.

### Dokumen Pendukung atau Lampiran

1. Delivery Checklist
2. User Manual / Panduan Pengguna
3. Materi Pelatihan
4. Daftar Hadir Pelatihan
5. Berita Acara Serah Terima

### Distribusi Dokumen

1. Departemen IT (Developer, PM)
2. Departemen User penerima modul
3. Manajemen

### Flowchart

Mulai - Verifikasi Kesiapan Modul - Siapkan Materi Pelatihan - Pelaksanaan Pelatihan (Developer) - Demo dan Tanya Jawab - Go-Live - Pendampingan Intensif Hypercare 1-2 Minggu - Evaluasi Penggunaan - Tanda Tangan BA Serah Terima – Selesai

## 5. SOP Bug Fixing

**Berkas sumber**: `5. SOP_Bug_Fixing.docx` · **No. dokumen**: 005/IT/SOP/IV/2026 · **Revisi**: 00 · **Tanggal**: 23-Apr-2026 · **Disusun oleh**: Supervisor Tech Dev · **Disetujui oleh**: Direktur

### Tujuan

Memberikan panduan penanganan bug yang ditemukan pada sistem ERP secara cepat, terstruktur, dan terdokumentasi agar tidak mengganggu operasional.

### Ruang Lingkup

SOP ini berlaku untuk seluruh proses pelaporan, triase, perbaikan, dan verifikasi bug pada sistem ERP, baik saat pengembangan maupun setelah go-live.

### Penanggung Jawab

1. PM (Project Manager): Bertanggung jawab menerima laporan bug, menentukan prioritas penanganan, dan memastikan bug diselesaikan sesuai target waktu.
2. Developer: Bertanggung jawab menganalisis root cause, melakukan perbaikan kode, testing pasca perbaikan, dan mendokumentasikan solusi.
3. User: Bertanggung jawab melaporkan bug secara jelas melalui Bug Report Form dan memverifikasi bahwa bug telah terselesaikan.

### Definisi

1. Bug: Kesalahan pada program yang menyebabkan sistem tidak berjalan sesuai yang diharapkan.
2. Priority: Tingkat urgensi penanganan - Critical (sistem tidak bisa digunakan), High (fitur utama terganggu), Medium (fitur minor), Low (kosmetik).
3. Root Cause Analysis (RCA): Proses investigasi untuk menemukan penyebab utama dari suatu bug.
4. Hotfix: Perbaikan bug kritis yang perlu segera diterapkan ke produksi tanpa menunggu jadwal release.
5. Regression Testing: Pengujian ulang setelah perbaikan untuk memastikan tidak ada bug baru.

### Rincian Prosedur

1. Pelaporan Bug: User melaporkan bug kepada PM melalui Bug Report Form berisi deskripsi, langkah reproduksi, screenshot, dan dampak operasional.
2. Triase dan Prioritas: PM mengevaluasi laporan bug, menentukan prioritas (Critical/High/Medium/Low), dan menugaskan Developer.
3. Analisis Root Cause: Developer menganalisis penyebab utama bug. Hasil analisis didokumentasikan sebagai dasar perbaikan.
4. Perbaikan Bug: Developer melakukan perbaikan kode. Untuk bug Critical, perbaikan dilakukan sebagai hotfix dan di-deploy segera.
5. Regression Testing: Developer melakukan pengujian ulang untuk memastikan perbaikan benar dan tidak menimbulkan bug baru.
6. Verifikasi oleh User: User mengkonfirmasi apakah bug sudah terselesaikan sesuai ekspektasi.
7. Penutupan Bug: PM menutup bug di sistem tracking dan mendokumentasikan solusi untuk referensi mendatang.

### Dokumen Pendukung atau Lampiran

1. Bug Report Form
2. Bug Tracking Log
3. Root Cause Analysis (RCA) Document
4. Testing Log Pasca Perbaikan
5. Berita Acara Penyelesaian Bug (untuk Critical)

### Distribusi Dokumen

1. Departemen IT (Developer, PM)
2. User pelapor bug
3. Manajemen (untuk bug Critical)

### Flowchart

Mulai - User Lapor Bug - PM Triase dan Tentukan Prioritas - Penugasan Developer - Analisis Root Cause - Perbaikan Bug - Regression Testing - Benar? - Tidak: Analisis Ulang - Ya: Verifikasi User - Setuju? - Tidak: Perbaikan Ulang - Ya: Penutupan Bug - Dokumentasi – Selesai

## 6. SOP Perbaikan Laptop

**Berkas sumber**: `6. SOP_Perbaikan_Laptop.docx` · **No. dokumen**: 006/IT/SOP/IV/2026 · **Revisi**: 00 · **Tanggal**: 23-Apr-2026 · **Disusun oleh**: Supervisor Tech Dev · **Disetujui oleh**: Direktur

### Tujuan

Memberikan panduan yang jelas dalam penanganan kerusakan laptop milik perusahaan agar perbaikan berjalan cepat, terstruktur, dan meminimalisir downtime karyawan.

### Ruang Lingkup

SOP ini berlaku untuk seluruh proses penanganan kerusakan laptop milik perusahaan, baik kerusakan hardware maupun software, yang digunakan oleh seluruh karyawan.

### Penanggung Jawab

1. IT Manager: Bertanggung jawab menerima dan menyetujui permintaan perbaikan, menentukan prioritas, serta memutuskan penanganan internal atau vendor.
2. IT Support/Teknisi: Bertanggung jawab melakukan diagnosa, perbaikan internal atau koordinasi vendor, dan pengujian setelah perbaikan.
3. User (Karyawan): Bertanggung jawab melaporkan kerusakan secara jelas, menyerahkan laptop, dan memverifikasi kondisi laptop setelah perbaikan.

### Definisi

1. Hardware: Komponen fisik laptop seperti layar, keyboard, baterai, RAM, storage, dan komponen elektronik lainnya.
2. Software: Perangkat lunak pada laptop termasuk sistem operasi, driver, dan aplikasi.
3. Vendor: Pihak ketiga (service center resmi atau mitra IT) untuk perbaikan yang tidak bisa ditangani internal.
4. Garansi: Jaminan perbaikan atau penggantian komponen dari produsen dalam jangka waktu tertentu.
5. Backup Data: Pencadangan data penting sebelum perbaikan untuk mencegah kehilangan data.

### Rincian Prosedur

1. Pelaporan Kerusakan: User melaporkan kerusakan kepada PM melalui Form Permintaan Perbaikan (Tiket) berisi deskripsi kerusakan dan dampak terhadap pekerjaan.
2. Pemeriksaan dan Penerimaan: Teknisi menerima laptop, mencatat kondisi fisik awal, dan melakukan pemeriksaan awal.
3. Backup Data: Teknisi melakukan backup data penting User sebelum perbaikan dilakukan.
4. Diagnosa Kerusakan: Teknisi mendiagnosa kerusakan (hardware atau software) dan menentukan estimasi waktu perbaikan.
5. Perbaikan Internal: Jika kerusakan bisa ditangani internal, Teknisi melakukan perbaikan langsung (reinstall OS, ganti komponen minor, dll.).
6. Pengiriman ke Vendor: Jika tidak bisa ditangani internal, PM menyetujui pengiriman ke vendor/service center resmi.
7. Pengujian Pasca Perbaikan: Teknisi melakukan pengujian menyeluruh sebelum laptop dikembalikan ke User.
8. Pengembalian ke User: Teknisi mengembalikan laptop ke User disertai penjelasan perbaikan. User memverifikasi dan menandatangani Berita Acara.

### Dokumen Pendukung atau Lampiran

1. Form Permintaan Perbaikan Laptop (Tiket)
2. Log Perbaikan
3. Surat Pengiriman ke Vendor (jika perlu)

### Distribusi Dokumen

1. Departemen IT (Developer/IT Support, PM)
2. User pemilik laptop
3. Departemen HRD / Aset

### Flowchart

Mulai - User Lapor Kerusakan - Developer Terima dan Periksa Fisik - Backup Data User - Diagnosa Kerusakan - Bisa Internal? - Ya: Perbaikan Internal - Tidak: Kirim ke Vendor - Perbaikan Selesai - Pengujian - Normal? - Tidak: Perbaikan Lanjutan - Ya: Kembalikan ke User - Tanda Tangan BA – Selesai

## 7. SOP Perbaikan Printer

**Berkas sumber**: `7. SOP_Perbaikan_Printer.docx` · **No. dokumen**: 007/IT/SOP/IV/2026 · **Revisi**: 00 · **Tanggal**: 23-Apr-2026 · **Disusun oleh**: Supervisor Tech Dev · **Disetujui oleh**: Direktur

### Tujuan

Memberikan panduan yang jelas dalam penanganan kerusakan printer milik perusahaan agar perbaikan berjalan cepat dan kegiatan operasional tidak terganggu.

### Ruang Lingkup

SOP ini berlaku untuk seluruh proses penanganan kerusakan printer milik perusahaan, baik hardware maupun software/driver, di semua departemen.

### Penanggung Jawab

1. IT Manager: Bertanggung jawab menerima dan menyetujui permintaan perbaikan, menentukan prioritas, serta memutuskan penanganan internal atau vendor.
2. IT Support/Teknisi: Bertanggung jawab mendiagnosa kerusakan printer, melaksanakan perbaikan (toner, paper jam, driver, vendor), dan melakukan uji cetak.
3. User (Karyawan): Bertanggung jawab melaporkan kerusakan printer dengan jelas beserta gejala dan pesan error, serta memverifikasi fungsi printer setelah perbaikan.

### Definisi

1. Printer: Perangkat keras untuk mencetak dokumen, baik berwarna maupun hitam-putih.
2. Toner/Tinta: Bahan habis pakai pada printer yang menghasilkan cetakan dan perlu diganti berkala.
3. Driver Printer: Perangkat lunak yang memungkinkan komputer berkomunikasi dengan printer.
4. Paper Jam: Kondisi kertas macet di dalam printer sehingga tidak bisa mencetak.
5. Vendor/Teknisi Eksternal: Pihak ketiga untuk perbaikan yang memerlukan keahlian atau suku cadang khusus.

### Rincian Prosedur

1. Pelaporan Kerusakan: User melaporkan kerusakan printer kepada PM melalui Form Permintaan Perbaikan (Tiket) berisi lokasi printer, deskripsi masalah, dan pesan error.
2. Pemeriksaan Awal: Teknisi melakukan pemeriksaan awal untuk mengidentifikasi jenis masalah (paper jam, toner, koneksi, atau hardware).
3. Diagnosa Masalah: Teknisi mendiagnosa lebih mendalam untuk menentukan penyebab dan solusi yang tepat.
4. Perbaikan Software/Driver: Untuk masalah software, Teknisi melakukan reinstall driver atau konfigurasi ulang.
5. Perbaikan Hardware Sederhana: Untuk hardware ringan (paper jam, ganti toner, bersihkan roller), Developer langsung melakukan perbaikan.
6. Pengiriman ke Vendor: Untuk kerusakan hardware serius, PM menyetujui pengiriman ke vendor/teknisi eksternal.
7. Uji Cetak: Teknisi melakukan uji cetak untuk memastikan printer berfungsi normal dan hasil cetak bersih.
8. Konfirmasi User: User melakukan verifikasi dan menandatangani Form Penyelesaian.

### Dokumen Pendukung atau Lampiran (Optional)

1. Form Permintaan Perbaikan Printer (Tiket)
2. Log Perbaikan Printer
3. Surat Pengiriman ke Vendor (jika perlu)

### Distribusi Dokumen

1. Departemen IT (Developer/IT Support, PM)
2. User / Departemen pelapor
3. Departemen Umum / Aset

### Flowchart

Mulai - User Lapor Kerusakan Printer - Developer Periksa Awal - Diagnosa - Software: Reinstall Driver - Hardware Ringan: Paper Jam/Toner - Hardware Berat: Vendor - Perbaikan Selesai - Uji Cetak - Normal? - Tidak: Lanjutan - Ya: Konfirmasi User - Tanda Tangan – Selesai

## 8. SOP Troubleshooting Jaringan Internet

**Berkas sumber**: `8. SOP_Troubleshooting_Jaringan_Internet.docx` · **No. dokumen**: 008/IT/SOP/IV/2026 · **Revisi**: 00 · **Tanggal**: 23-Apr-2026 · **Disusun oleh**: Supervisor Tech Dev · **Disetujui oleh**: Direktur

### Tujuan

Memberikan panduan penanganan gangguan jaringan internet di lingkungan perusahaan secara cepat dan sistematis agar konektivitas dapat dipulihkan dengan segera.

### Ruang Lingkup

SOP ini berlaku untuk seluruh penanganan gangguan jaringan internet, mulai dari gangguan sisi User (client-side) hingga gangguan dari penyedia layanan internet (ISP).

### Penanggung Jawab

1. IT Manager: Bertanggung jawab menerima eskalasi gangguan, mengambil keputusan lanjutan, berkoordinasi dengan ISP, dan menginformasikan status ke manajemen.
2. Network Admin: Bertanggung jawab merespons laporan, melakukan troubleshooting perangkat jaringan, memverifikasi koneksi, dan berkoordinasi dengan ISP.
3. User (Karyawan): Bertanggung jawab melaporkan gangguan secara jelas dan memberikan informasi yang diperlukan untuk proses troubleshooting.

### Definisi

1. ISP (Internet Service Provider): Perusahaan penyedia layanan koneksi internet yang digunakan perusahaan.
2. Router: Perangkat jaringan yang menghubungkan jaringan internal dengan internet.
3. Switch: Perangkat yang menghubungkan beberapa perangkat dalam jaringan lokal (LAN).
4. LAN (Local Area Network): Jaringan komputer dalam area terbatas seperti satu gedung atau kantor.
5. Bandwidth: Kapasitas transfer data dalam jaringan, diukur dalam Mbps atau Gbps.
6. DNS (Domain Name System): Sistem yang menerjemahkan nama domain menjadi alamat IP.

### Rincian Prosedur

1. Pelaporan Gangguan: User melaporkan gangguan koneksi kepada PM atau Network Admin disertai info lokasi, gejala, dan waktu mulai gangguan.
2. Identifikasi Skala: Network Admin mengidentifikasi apakah gangguan lokal (satu perangkat) atau menyeluruh (seluruh kantor).
3. Troubleshooting Sisi User: Untuk gangguan lokal, Network Admin memeriksa perangkat User (cek kabel/WiFi, restart adapter, flush DNS, cek IP).
4. Pengecekan Perangkat Jaringan: Jika gangguan menyeluruh, Network Admin memeriksa router/switch (indikator, restart, konfigurasi).
5. Pengecekan Koneksi ISP: Network Admin mengecek koneksi ke titik ISP. Jika tidak ada sinyal, segera hubungi ISP.
6. Koordinasi dengan ISP: PM dan Network Admin berkoordinasi dengan ISP untuk info status, estimasi pemulihan, dan eskalasi jika perlu.
7. Solusi Sementara: Selama menunggu ISP, Network Admin menyiapkan alternatif (koneksi backup/hotspot).
8. Verifikasi Pemulihan: Network Admin memverifikasi koneksi pulih di seluruh area kantor.
9. Notifikasi dan Dokumentasi: PM atau Network Admin menginformasikan koneksi pulih ke User. Gangguan dan solusi didokumentasikan.

### Dokumen Pendukung atau Lampiran

1. Form Laporan Gangguan Jaringan (Tiket)
2. Network Troubleshooting Log
3. Log Komunikasi dengan ISP
4. Incident Report (untuk gangguan lebih dari 4 jam)

### Distribusi Dokumen

1. Departemen IT (Developer/Network Admin, PM)
2. Seluruh User yang terdampak
3. Manajemen (untuk gangguan berdampak luas)

### Flowchart

Mulai - User Lapor Gangguan - Identifikasi Skala - Lokal: Troubleshooting Client - Teratasi? - Ya: Selesai - Menyeluruh: Cek Perangkat Jaringan - Masalah Internal? - Ya: Perbaiki - Tidak: Cek ISP - Hubungi ISP - Koordinasi - Solusi Sementara - Pulih - Verifikasi - Notifikasi User - Dokumentasi – Selesai

## 9. SOP Sistem Down

**Berkas sumber**: `9. SOP_Sistem_Down.docx` · **No. dokumen**: 009/IT/SOP/IV/2026 · **Revisi**: 00 · **Tanggal**: 23-Apr-2026 · **Disusun oleh**: Supervisor Tech Dev · **Disetujui oleh**: Direktur

### Tujuan

Memberikan panduan penanganan kondisi sistem ERP yang tidak dapat diakses secara cepat dan terstruktur untuk meminimalisir dampak terhadap operasional bisnis.

### Ruang Lingkup

SOP ini berlaku untuk kondisi sistem ERP mengalami gangguan atau tidak dapat diakses, baik sebagian maupun seluruh modul, yang disebabkan berbagai faktor teknis.

### Penanggung Jawab

1. IT Manager: Bertanggung jawab menerima laporan insiden, mengkoordinasikan tim, mengambil keputusan eskalasi, dan menginformasikan status ke manajemen dan User.
2. Network Admin: Bertanggung jawab menginvestigasi penyebab, melakukan tindakan pemulihan, memverifikasi sistem, dan membuat Root Cause Analysis (RCA).
3. User: Bertanggung jawab melaporkan kondisi sistem down secara jelas, menghentikan penggunaan sistem, dan memverifikasi saat sistem dinyatakan pulih.

### Definisi

1. Sistem Down: Kondisi sistem ERP tidak dapat diakses atau tidak berfungsi normal sehingga mengganggu operasional.
2. Downtime: Durasi waktu selama sistem tidak dapat digunakan oleh User.
3. Incident: Kejadian tidak terduga yang menyebabkan gangguan layanan sistem.
4. RCA (Root Cause Analysis): Analisis penyebab utama gangguan agar dapat dicegah di masa mendatang.
5. Failover: Mekanisme pengalihan ke sistem cadangan saat sistem utama gagal.

### Rincian Prosedur

1. Deteksi dan Pelaporan: User melaporkan sistem down ke PM. Laporan mencakup waktu kejadian, modul yang tidak bisa diakses, dan pesan error.
2. Konfirmasi Insiden: PM mengkonfirmasi skala insiden bersama Network Admin dan beberapa User di lokasi berbeda.
3. Notifikasi Awal: PM menginformasikan kondisi down ke seluruh User disertai instruksi untuk menghentikan penggunaan sistem sementara.
4. Investigasi dan Diagnosa: Network Admin menginvestigasi penyebab (server, database, aplikasi, jaringan, atau perubahan konfigurasi).
5. Tindakan Pemulihan: Network Admin melakukan pemulihan sesuai penyebab (restart service, rollback konfigurasi, pemulihan database). Setiap tindakan dicatat dalam Incident Log.
6. Verifikasi Pemulihan: Network Admin memverifikasi sistem pulih normal. User diminta verifikasi dari sisi pengguna.
7. Notifikasi Pemulihan: PM menginformasikan sistem pulih ke seluruh User disertai imbauan untuk memverifikasi data.
8. Root Cause Analysis (RCA): Network admin membuat laporan RCA dengan penyebab, kronologi, tindakan, dan rekomendasi pencegahan dalam 1x24 jam.

### Dokumen Pendukung atau Lampiran

1. Incident Report Form (Tiket)
2. Incident Log (kronologi tindakan)
3. Root Cause Analysis (RCA) Report

### Distribusi Dokumen

1. Departemen IT (Developer/SysAdmin, PM)
2. Seluruh User sistem ERP
3. Manajemen (Direktur, Kepala Departemen)

### Flowchart

Mulai - User Deteksi Sistem Down - Lapor ke PM - Konfirmasi Skala - Notifikasi Awal ke User - Developer Investigasi dan Diagnosa - Tindakan Pemulihan - Pulih? - Tidak: Eskalasi dan Tindakan Lanjutan - Ya: Verifikasi Developer dan User - Notifikasi Pemulihan - Buat RCA 1x24 jam - Tindakan Pencegahan – Selesai

## 10. SOP Server Down

**Berkas sumber**: `10. SOP_Server_Down.docx` · **No. dokumen**: 010/IT/SOP/IV/2026 · **Revisi**: 00 · **Tanggal**: 23-Apr-2026 · **Disusun oleh**: Supervisor Tech Dev · **Disetujui oleh**: Direktur

### Tujuan

Memberikan panduan penanganan kondisi server yang tidak beroperasi secara cepat dan terstruktur untuk memulihkan layanan dan mencegah kehilangan data.

### Ruang Lingkup

SOP ini berlaku untuk kondisi server (fisik maupun virtual) yang menopang sistem ERP dan layanan IT perusahaan mengalami gangguan atau tidak dapat beroperasi.

### Penanggung Jawab

1. IT Manager: Bertanggung jawab menerima eskalasi, mengkoordinasikan tim, mengambil keputusan kritis termasuk aktivasi disaster recovery, dan melaporkan status ke manajemen.
2. Network Admin: Bertanggung jawab merespons insiden, mendiagnosa hardware dan software server, mengeksekusi pemulihan, memantau pasca pemulihan, dan membuat RCA.
3. User: Bertanggung jawab melaporkan dampak server down yang dirasakan, menghentikan aktivitas yang memperburuk kondisi, dan memverifikasi layanan setelah server pulih.

### Definisi

1. Server: Komputer atau sistem yang menyediakan layanan, data, dan sumber daya kepada perangkat lain dalam jaringan.
2. Server Down: Kondisi server tidak dapat beroperasi atau memberikan layanan kepada pengguna.
3. Hardware Failure: Kerusakan komponen fisik server seperti hard disk, RAM, power supply, atau motherboard.
4. Virtualisasi: Teknologi yang memungkinkan satu server fisik menjalankan beberapa server virtual secara bersamaan.
5. Disaster Recovery (DR): Prosedur dan sistem cadangan yang diaktifkan saat terjadi kegagalan total server utama.
6. UPS (Uninterruptible Power Supply): Perangkat sumber daya cadangan yang menjaga server saat gangguan listrik.

### Rincian Prosedur

1. Deteksi dan Pelaporan: Network Admin mendeteksi server down melalui monitoring atau laporan User. Insiden dilaporkan ke PM. Untuk kejadian di luar jam kerja, Developer on-call dihubungi.
2. Eskalasi dan Mobilisasi Tim: PM memobilisasi Network Admin untuk menangani insiden dan menginformasikan kondisi ke manajemen.
3. Notifikasi User: PM menginformasikan kondisi server down ke seluruh User terdampak beserta perkiraan waktu pemulihan.
4. Diagnosa Server: Network Admin mendiagnosa penyebab: cek status fisik, power supply, koneksi jaringan, log sistem, dan kondisi storage.
5. Pemulihan Server: Network Admin melakukan pemulihan sesuai penyebab: restart server, perbaikan konfigurasi, pemulihan dari backup, atau aktivasi server cadangan.
6. Aktivasi Disaster Recovery: Jika server utama tidak bisa dipulihkan segera, PM mengaktifkan DR untuk mengalihkan layanan ke server cadangan.
7. Verifikasi Layanan: Network Admin memverifikasi seluruh layanan pulih normal. Monitoring intensif dilakukan minimal 1 jam pasca pemulihan.
8. Notifikasi Pemulihan: PM menginformasikan ke User dan manajemen bahwa server pulih dan layanan dapat digunakan kembali.
9. Root Cause Analysis dan Pencegahan: Network Admin membuat laporan RCA lengkap dan rekomendasi pencegahan untuk insiden serupa.

### Dokumen Pendukung atau Lampiran

1. Server Monitoring Log
2. Incident Report Form
3. Server Diagnostic Log
4. Disaster Recovery Activation Record (jika diaktifkan)
5. Root Cause Analysis (RCA) Report
6. Rekomendasi Tindakan Pencegahan

### Distribusi Dokumen

1. Departemen IT (System Administrator, PM)
2. Manajemen (Direktur, Kepala Departemen)
3. Seluruh User yang terdampak

### Flowchart

Mulai - Deteksi Server Down - Lapor ke PM - Mobilisasi Developer - Notifikasi User - Diagnosa Server - Tindakan Pemulihan - Pulih? - Tidak: Aktivasi Disaster Recovery - DR Berhasil? - Tidak: Eskalasi Vendor/Manajemen - Ya: Verifikasi Layanan - Monitoring Intensif - Notifikasi Pemulihan - RCA dan Rekomendasi – Selesai

## 011. SOP E-Ticket Permintaan Pengembangan Software

**Berkas sumber**: `011. SOP E-Ticket Permintaan Pengembangan Software.docx` · **No. dokumen**: 011/IT/SOP/VI/2026 · **Revisi**: 00 · **Tanggal**: 05-Jun-2026 · **Disusun oleh**: Supervisor Tech Dev · **Disetujui oleh**: Direktur

### Tujuan

- SOP ini bertujuan untuk :
    - Menstandarkan proses pengajuan kebutuhan pengembangan software
    - Memastikan seluruh permintaan terdokumentasi dan dapat ditelusuri
    - Mengoptimalkan prioritas pekerjaan tim tech development
    - Memastikan kebutuhan bisnis diterjemahkan dengan jelas menjadi solusi sistem
    - Mengurangi miskomunikasi antara requester dan tim tech development
    - Memastikan setiap pengembangan mendapatkan approval yang sesuai.

### Ruang Lingkup

- SOP ini berlaku untuk seluruh permintaan terkait :
    - Pembuatan software/aplikasi baru
    - Penambahan fitur baru pada sistem yang sudah ada
    - Perubahan (enhancement) sistem existing
    - Integrasi sistem
    - Automasi proses bisnis
    - Pembuatan dashboard dan reporting
    - Perbaikan bug yang memerlukan pengembangan program
    - Pengembangan website, mobile application, ERP dan sistem internal perusahaan.

### Penanggung Jawab

1. Requester/User bertanggungjawab mengajukan kebutuhan melalui E-Ticket
2. Tech Development Lead bertanggungjawab analisa teknis dan penentuan prioritas
3. Programmer/Developer bertanggungjawab melaksanakan pengembangan sistem
4. Direktur bertanggungjawab approval pengembangan strategis.

### Definisi

1. E-Ticket yaitu sistem digital untuk pengajuan dan monitoring pekerjaan
2. Requester yaitu pengguna yang mengajukan kebutuhan sistem
3. Development yaitu pembuatan atau pengembangan aplikasi/sistem
4. Enhancement yaitu penambahan atau penyempurnaan fitur sistem
5. Bug yaitu kesalahan fungsi pada sistem
6. UAT yaitu User Acceptance Test
7. Go Live yaitu sistem siap digunakan secara operasional
8. SLA yaitu service level agreement penyelesaian pekerjaan
9. Urgensi yaitu kondisi sistem down, data loss atau isu legal/compliance yang memerlukan penanganan segera
10. BAST yaitu berita acara serah terima sebagai bukti penyelesaian pekerjaan
11. Change request yaitu pengajuan resmi atas penambahan scope/fitur di luar proposal awal.

### Rincian Prosedur

- 5.1 Periode Pengajuan E-Ticket
- Setiap divisi hanya boleh mengajukan project baru pada tanggal 1- 20 setiap bulan
- Project yang disetujui dikerjakan pada bulan berikutnya dan menjadi bagian KPI Tim IT
- Pengajuan di luar tanggal 1- 20 hanya untuk kategori Bug Fix / Emergency
- Wajib melampirkan Blueprint Aplikasi dan Flowchart Rancangan Aplikasi; tanpa lampiran ini tiket tidak diproses
    - 5.2 Pengajuan E-Ticket
- Login ke sistem E-Ticket
- Memilih kategori: New Development, Enhancement, Integration, Automation, Bug Fix
- Mengisi informasi: nama departemen, nama PIC, judul permintaan, latar belakang, tujuan pengembangan, proses bisnis saat ini dan yang diinginkan, dampak bisnis, deadline, lampiran flow process, blueprint, dan flowchart rancangan aplikasi
- Submit tiket
    - 5.3 Review Atasan
- Meninjau permintaan
- Memastikan kebutuhan bukan duplikasi
- Menentukan urgensi
- Memberikan approval atau reject
    - 5.4 Validasi Kebutuhan Bisnis
- Memahami kebutuhan bisnis
- Melakukan diskusi dengan user bila diperlukan
- Menentukan manfaat dan dampak bisnis
- Menyusun business requirement
    - 5.5 Analisa Tim Tech Development
- Menganalisa kebutuhan: kompleksitas, estimasi waktu, resource, risiko
- Menentukan kategori: Minor (1-5 hari), Medium (6-15 hari), Major (>15 hari)
- Menetapkan buffer waktu toleransi sebesar 20% dari estimasi awal
- Menyampaikan estimasi pengerjaan
    - 5.6 Konsolidasi dan Penentuan Scope oleh Tim IT
- Merekap seluruh pengajuan yang masuk selama periode 1 - 20
- Melakukan review terhadap blueprint dan flowchart tiap pengajuan
- Menentukan scope pengerjaan bulan depan berdasarkan kapasitas tim, prioritas bisnis, dan kompleksitas
- Menyerahkan hasil rekap dan usulan scope kepada Direktur untuk filter final, karena skala prioritas berada di Direktur
- Hasil scope (masuk/ditunda) dikomunikasikan kembali ke requester
    - 5.7 Approval Pengembangan
- Review hasil analisa
- Menentukan prioritas: Critical, High, Medium, Low
- Memberikan approval pengerjaan
    - 5.8 Development
- Membuat task development, melakukan coding, unit testing, update progres pada E-Ticket
- Project yang sedang berjalan tidak boleh diganggu-gugat, kecuali untuk Bug Fix / urgensi kebutuhan
- Requester wajib bersedia berkontribusi langsung, termasuk mengikuti weekly sync/meeting progress agar tetap inline
- Ketidakhadiran requester tanpa alasan tidak menghentikan progres; pengerjaan tetap lanjut sesuai asumsi terakhir Tim IT dan dicatat pada log
    - 5.9 Perubahan Selama Pengerjaan (Anti Scope-Creep)
- Buffer waktu 20% dari estimasi awal berlaku untuk kompleksitas yang meleset dari estimasi; jika terlampaui, wajib eskalasi ke Direktur
- Minor addition (perubahan kecil, estimasi < 1 hari kerja): cukup approval Tech Development Lead, dicatat pada log
- Major addition / fitur baru di luar proposal awal: wajib mengajukan Change Request baru, mendapat approval Direktur sebelum dikerjakan, dan dapat diputuskan masuk ke project berjalan atau ditunda ke periode pengajuan berikutnya
- Seluruh perubahan dicatat pada Change Request Log agar scope project dapat ditelusuri dari proposal awal hingga realisasi
    - 5.10 Internal Testing
- Functional testing, integration testing, security testing
- Dokumentasi hasil testing
    - 5.11 User Acceptance Test (UAT)
- User mencoba sistem dan memastikan kebutuhan telah terpenuhi
- Mencatat bug atau improvement tambahan
- Memberikan approval UAT (form dan sign-off digabung dalam satu dokumen)
    - 5.12 Go Live
- Deployment sistem, verifikasi fungsi, sosialisasi kepada user, monitoring pasca implementasi
    - 5.13 Penutupan Ticket
- Memastikan seluruh kebutuhan telah terpenuhi
- Menerbitkan BAST sebagai syarat untuk melanjutkan ke project berikutnya
- Mengunggah dokumen final, mengubah status tiket menjadi closed, mengarsipkan dokumen proyek

### Dokumen Pendukung atau Lampiran

1. Form E-Ticket Development
2. Business Requirement Document(BRD)
3. Functional Requirement Document(FRD)
4. Technical Analysis Document
5. Development Approval Form
6. UAT Form
7. UAT Sign-Off
8. Release Note
9. Deployment Checklist
10. Project Closure Report
11. Blueprint Aplikasi

### Flowchart Rancangan Aplikasi

1. Rekap dan Scope Pengembangan Bulanan
2. Change Request Log
3. BAST (Berita Acara Serah Terima)

### Distribusi Dokumen

1. Requester
2. Supervisor Departemen
3. Internal Control
4. Tech Development Lead
5. Developer
6. Direktur
7. Arsip IT Departemen

### Flowchart E-Ticket Permintaan Pengembangan Software

- **Bagian 1 - Pengajuan sampai Approval Direktur**
- Pengajuan E-Ticket (tgl 1 – 20 setap bulan, wajib blueprint + flowchart)
- Review SPV (approve / reject)
- Analisa Tim Tech Development (estimasi + buffer 20%)
- Konsolidasi & Penentuan Scope Tim IT (rekap seluruh pengajuan)
- Approval Direktur (filter prioritas final)
- Lanjut ke Development
- **Bagian 2 - Development sampai Penutupan**
- Development (weekly sync + buffer 20%)
- Internal Testing (functional, integration, security)
- UAT (form + sign-off)
- Go Live (deployment + monitoring)
- Penutupan Ticket (BAST + arsip proyek)
- **Bagian 3 - Alur Change Request (Fitur Baru di Luar Proposal)**
- Fitur Baru Muncul Saat Development (di luar proposal awal)
- Submit Change Request (bukan lanjut otomatis)
- Approval Direktur (wajib sebelum dikerjakan)

| Masuk Project Berjalan | Ditunda ke Periode Berikutnya |
|---|---|

- **Dicatat pada Change Request Log**

## 012. SOP Pemberian Akses Saat Onboarding Karyawan

**Berkas sumber**: `012. SOP Pemberian Akses Saat Onboarding Karyawan.docx` · **No. dokumen**: 012/IT/SOP/VI/2026 · **Revisi**: 00 · **Tanggal**: 08-Jun-2026 · **Disusun oleh**: Supervisor Tech Dev · **Disetujui oleh**: Direktur

### Tujuan

- SOP ini dibuat sebagai pedoman dalam proses pemberian akses kepada karyawan baru saat onboarding agar:
    - Memastikan karyawan mendapatkan akses kerja yang sesuai dengan jabatan dan tanggung jawabnya.
    - Menjamin keamanan informasi dan data perusahaan.
    - Mempercepat proses adaptasi dan produktivitas karyawan baru.
    - Menghindari pemberian akses yang tidak sesuai atau berlebihan.
    - Menciptakan proses onboarding yang terstandarisasi dan terdokumentasi.

### Ruang Lingkup

1. SOP ini berlaku untuk seluruh karyawan baru, baik:
    - Karyawan Tetap
    - Karyawan Kontrak
    - Karyawan Magang
    - Freelance (jika diperlukan)
    - Konsultan Internal
2. Akses yang diberikan meliputi :
    - Email perusahaan
    - Sistem HRIS
    - ERP/CRM
    - Software internal perusahaan
    - Shared folder/cloud storage
    - Absensi
    - VPN
    - Website admin
    - Marketplace admin
    - Media sosial perusahaan
    - Grup komunikasi internal
    - Akses gedung dan fasilitas kerja

### Penanggung Jawab

1. HRGA bertanggungjawab mengajukan kebutuhan akses onboarding
2. User Departemen bertanggungjawab menentukan akses yang dibutuhkan
3. IT Support bertanggungjawab membuat akun dan memberikan akses sistem
4. Karyawan Baru bertanggungjawab menjaga kerahasiaan akun yang diberikan
5. Internal Control bertanggungjawab monitoring kepatuhan pemberian akses.

### Definisi

Pengajuan Permintaan Akses, Verifikasi Kebutuhan Akses, Pembuatan Akun dan Hak Akses, Verifikasi dan Pengujian Akses, Serah Terima Akun dan Akses, Monitoring Masa Onboarding, Dokumentasi dan Pengarsipan.

### Rincian Prosedur

- Prosedur pengajuan permintaan akses :
    1. Menerima data karyawan baru yang telah dinyatakan diterima
    2. Mengisi form permintaan akses onboarding
    3. Melengkapi informasi :
        - Nama karyawan
        - NIK
        - Jabatan
        - Departemen
        - Atasan langsung
        - Tanggal bergabung
        - Daftar akses yang dibutuhkan
    4. Mengisi form kepada IT dan pihak terkait.
- Prosedur verifikasi kebutuhan akses :
    1. Meninjau kebutuhan akses
    2. Menentukan level akses berdasarkan jabatan dan kebutuhan
    3. Menyetujui atau merevisi daftar akses
    4. Mengirim approval kepada tim IT
- Prosedur pembuatan akun dan hak akses :
    1. Membuat akun email perusahaan
    2. Membuat akun sistem yang diperlukan
    3. Menambahkan user ke grup atau role yang sesuai
    4. Mengaktifkan akses perangkat dan jaringan
    5. Mendokumentasikan seluruh akun yang dibuat
- Prosedur verifikasi dan pengujian akses :
    1. Melakukan login testing
    2. Memastikan akses sesuai role
    3. Memastikan tidak ada akses berlebih
    4. Melakukan perbaikan apabila ditemukan kendala
- Prosedur serah terima akun dan akses
1. Menyerahkan :
    - Email perusahaan
    - Username
    - Password sementara
    - Panduan penggunaan sistem
2. Menginstruksikan perubahan password pertama
3. Menjelaskan kebijakan keamanan informasi perusahaan
4. Meminta tanda terima akses
    - Prosedur monitoring masa onboarding
5. Melakukan pengecekan pada minggu pertama
6. Memastikan tidak ada kendala akses
7. Menindaklanjuti permintaan tambahan yang telah disetujui
8. Mendokumentasikan hasil monitoring
    - Prosedur dokumentasi dan pengarsipan
9. Mengarsipan :
    - Form permintaan akses
    - Approval akses
    - Daftar akun
    - Berita acara serah terima
    - Monitoring onboarding
10. Menyimpan dokumen secara digital dan fisik
11. Menjaga kerahasiaan data akses

### Dokumen Pendukung atau Lampiran

1. Form Permintaan Akses Onboarding
2. Data Karyawan Baru
3. Approval Pemberian Akses
4. Daftar User Account
5. Berita Acara Serah Terima Akses
6. Form Monitoring Onboarding
7. Kebijakan Keamanan Informasi

### Distribusi Dokumen

1. HRGA
2. IT Support
3. User Departemen
4. Internal Control
5. Arsip HRGA
6. Arsip Tech Development

### Flowchart Pemberian Akses Saat Onboarding

*Teks kotak flowchart, menurut urutan tersimpan di dokumen. Panah dan percabangan tidak ikut tersalin.*

1. Karyawan Baru Dinyatakan Diterima
2. HRGA Mengajukan Permintaan Akses
3. Verifikasi Atasan Langsung
4. Approval Akses
5. Pembuatan Akun oleh IT Support
6. Verifikasi & Testing Akses
7. Serah Terima Akun & Password
8. Monitoring Masa Onboarding
9. Dokumentasi & Pengarsipan

## 013. SOP Pencabutan Akses Saat Resign Karyawan

**Berkas sumber**: `013. SOP Pencabutan Akses Saat Resign Karyawan.docx` · **No. dokumen**: 013/IT/SOP/VI/2026 · **Revisi**: 00 · **Tanggal**: 08-Jun-2026 · **Disusun oleh**: Supervisor Tech Dev · **Disetujui oleh**: Direktur

### Tujuan

- SOP ini dibuat sebagai pedoman dalam proses pencabutan akses karyawan yang mengundurkan diri (resign), diberhentikan, pensiun, atau berakhir masa kontraknya agar:
    - Menjaga keamanan data dan informasi perusahaan.
    - Mencegah penggunaan sistem perusahaan oleh pihak yang sudah tidak memiliki hubungan kerja.
    - Memastikan seluruh akses digital dan fisik dicabut secara tepat waktu.
    - Mengurangi risiko kebocoran data, penyalahgunaan akun, dan akses tidak sah.
    - Mendukung proses offboarding karyawan yang terkontrol dan terdokumentasi.

### Ruang Lingkup

1. SOP ini berlaku untuk seluruh karyawan yang mengalami pemutusan hubungan kerja, meliputi :
    - Resign(mengundurkan diri)
    - PHK
    - Pensiun
    - Berakhir kontrak kerja
    - Mutasi keluar grup perusahaan
    - Konsultan atau tenga outsourcing yang masa kerjanya berakhir.
2. Jenis akses yang dicabut, meliputi :
    - Email perusahaan
    - HRIS
    - ERP
    - Sistem internal
    - Shared folder/cloud storage
    - VPN
    - Database
    - Website admin
    - Marketplace admin
    - Media sosial perusahaan
    - Grup komunikasi internal
    - Akses gedung
    - Kartu akses(id card karyawan)
    - Laptop/perangkat kerja

### Penanggung Jawab

1. HRGA bertanggungjawab menginformasikan status resign dan menginisiasi proses offboarding
2. User Departemen bertanggungjawab memastikan seluruh pekerjaan dan aset diserahterimakan
3. IT Support bertanggungjawab menonaktifkan seluruh akses sistem
4. General Affair bertanggungjawab menarik kembali kartu akses dan fasilitas perusahaan
5. Internal Control bertanggungjawab melakukan verifikasi kepatuhan proses pencabutan akses
6. Karyawan resign bertanggungjawab mengembalikan seluruh aset dan akses perusahaan.

### Definisi

Pemberitahuan Resign atau Terminasi, Identifikasi Hak Akses Karyawan, Pengembalia Aset Perusahaan, Pencabutan Akses Sistem, Pencabutan Akses Fisik, Verifikasi Exit Clearance, Dokumentasi dan Pengarsipan.

### Rincian Prosedur

- Prosedur pemberitahuan resign atau terminasi :
    1. Menerima surat resign atau keputusan terminasi
    2. Memverifikasi tanggal efektif berakhirnya hubungan kerja
    3. Mengirim pemberitahuan kepada :
        - Tech Development Departemen
        - General Affair
        - User Departemen
        - Internal Control
    4. Membuat Exit Clearance Form
- Prosedur identifikasi hak akses karyawan :
    1. Meninjau daftar akun dan sistem yang digunakan
    2. Mengidentifikasi :
        - Email
        - ERP
        - HRIS
        - Cloud storage
        - VPN
        - Website admin
        - Marketplace
        - Social media
        - Database
    3. Membuat daftar pencabutan akses
- Prosedur pengembalian aset perusahaan :
    1. Melakukan pengecekan aset :
        - Laptop
        - Handphone perusahaan
        - Access card
        - ID Card
        - Dokumen perusahaan
    2. Membuat berita acara pengembalian aset
    3. Mendokumentasikan kondisi aset
- Prosedur pencabutan akses sistem :
    1. Menonaktifkan akun email perusahaan
    2. Menonaktifkan akun ERP/HRIS
    3. Menghapus akses VPN
    4. Menghapus akses cloud storage
    5. Menghapus akses database
    6. Menghapus akses admin website dan marketplace
    7. Menghapus akses grup komunikasi perusahaan
    8. Mengubah atau reset password sistem yang diketahui oleh karyawan tersebut
- Prosedur pencabutan akses fisik
1. Menarik kembali :
    - ID Card
    - Access card
    - Kunci kendaraan operasional
2. Menonaktifkan akses pintu elektronik yang kaitannya dengan perusahaan
3. Memastikan tidak ada akses fisik yang masih aktif
    - Prosedur verifikasi exit clearance
4. Memeriksa checklist offboarding
5. Memastikan :
    - Aset telah dikembalikan
    - Akun telah dinonaktifkan
    - Tidak ada akses aktif tersisa
6. Meminta approval dari :
    - HRGA
    - IT
    - GA
    - Atasan langsung
7. Menyelesaikan exit clearance
    - Prosedur dokumentasi dan pengarsipan
8. Mengarsipan :
    - Surat resign/terminasi
    - Exit clearance form
    - Checklist pencabutan akses
    - Berita acara pengembalian aset
    - Bukti penonaktifan akun
9. Menyimpan dokumen secara digital dan fisik
10. Menjaga kerahasiaan data karyawan

### Dokumen Pendukung atau Lampiran

1. Surat Resign/Terminasi
2. Form Exit Clearance
3. Checlist Pencabutan Akses
4. Form Pengembalian Aset
5. Berita Acara Pengembalian Aset
6. Bukti Penonaktifan Akun

### Distribusi Dokumen

1. HRGA
2. IT Support
3. General Affair
4. Atasan Langsung
5. Internal Control
6. Arsip HRGA
7. Arsip Tech Development

### Flowchart Pencabutan Akses Saat Resign

*Teks kotak flowchart, menurut urutan tersimpan di dokumen. Panah dan percabangan tidak ikut tersalin.*

1. Pemberitahuan Resign/Terminasi
2. Identifikasi Hak Akses Karyawan
3. Pengembalian Aset Perusahaan
4. Pencabutan Akses Fisik
5. Verifikasi Exit Clearance
6. Approval Exit Clearance
7. Dokumentasi & Pengarsipan

## Berita Acara Pemberian Akses Karyawan Baru

**Berkas sumber**: `Berita Acara Pemberian Akses Karyawan Baru.docx`

- **BERITA ACARA PEMBERIAN AKSES KARYAWAN BARU**
- Nomor: ............................................
- Pada hari ini, \_________\_ tanggal \___\_ bulan \_________\_ tahun \_______\_, telah dilakukan pemberian akses kerja kepada karyawan baru dengan data sebagai berikut:
    1. **DATA KARYAWAN**

| Keterangan | Informasi |
|---|---|
| Nama Karyawan |   |
| NIK KTP |   |
| Jabatan |   |
| Departemen |   |
| Atasan Langsung |   |
| Tanggal Bergabung |   |

2. **DAFTAR AKSES YANG DIBERIKAN**

| No | Jenis Akses | Ceklis | Keterangan |
|---|---|---|---|
| 1 | Email Perusahaan |   |   |
| 2 | HRIS |   |   |
| 3 | ERP / Sistem Internal |   |   |
| 4 | Shared Folder/Cloud Storage |   |   |
| 5 | Absensi |   |   |
| 6 | VPN |   |   |
| 7 | Website Admin |   |   |
| 8 | Marketplace Admin |   |   |
| 9 | Media Sosial Perusahaan |   |   |
| 10 | Grup Komunikasi Internal |   |   |
| 11 | Access Card |   |   |
| 12 | ID Card Karyawan |   |   |
| 13 | Laptop / Perangkat Kerja |   |   |

3. **PERNYATAAN KARYAWAN**
- Saya yang bertanda tangan di bawah ini menyatakan bahwa:
    1. Telah menerima akses dan fasilitas kerja sebagaimana tercantum pada berita acara ini.
    2. Bersedia menjaga kerahasiaan username, password, data perusahaan, dan informasi yang diperoleh selama bekerja.
    3. Tidak akan memberikan atau meminjamkan akses kepada pihak lain tanpa izin perusahaan.
    4. Bersedia mematuhi seluruh kebijakan keamanan informasi dan penggunaan sistem yang berlaku di PT. Bharata Internasional Pharmaceutical.
    5. Bersedia bertanggung jawab atas penggunaan akun dan akses yang diberikan kepada saya.
    6. Bersedia mengembalikan seluruh aset dan akses perusahaan apabila hubungan kerja berakhir.
- Demikian berita acara ini dibuat untuk digunakan sebagaimana mestinya.
- Cilacap,.……,……………………
- **PIHAK YANG MENYERAHKAN PIHAK YANG MENERIMA**

| …………………………. |
|---|
| KARYAWAN YBS |

| ………………………….. |
|---|
| PENANGGUNGJAWAB |

- **MENGETAHUI**
- **………………………..**
- **ATASAN LANGSUNG**

## Berita Acara Pencabutan Akses Karyawan

**Berkas sumber**: `Berita Acara Pencabutan Akses Karyawan.docx`

- **BERITA ACARA PENCABUTAN AKSES KARYAWAN**
- Nomor: ............................................
- Pada hari ini, \_________\_ tanggal \___\_ bulan \_________\_ tahun \_______\_, telah dilakukan proses pencabutan akses karyawan berikut:
    1. **DATA KARYAWAN**

| Keterangan | Informasi |
|---|---|
| Nama Karyawan |   |
| NIK KTP |   |
| Jabatan Terakhir |   |
| Departemen |   |
| Atasan Langsung |   |
| Tanggal Efektif Resign/Terminasi |   |
| Status Karyawan | ☐ Resign ☐ PHK ☐ Pensiun ☐ Berakhir Kontrak ☐ Lainnya |

2. **DAFTAR AKSES YANG DICABUT**

| No | Jenis Akses | Ceklis | Keterangan |
|---|---|---|---|
| 1 | Email Perusahaan |   |   |
| 2 | HRIS |   |   |
| 3 | ERP / Sistem Internal |   |   |
| 4 | Shared Folder/Cloud Storage |   |   |
| 5 | Absensi |   |   |
| 6 | VPN |   |   |
| 7 | Website Admin |   |   |
| 8 | Marketplace Admin |   |   |
| 9 | Media Sosial Perusahaan |   |   |
| 10 | Grup Komunikasi Internal |   |   |
| 11 | Access Card |   |   |
| 12 | ID Card Karyawan |   |   |
| 13 | Laptop / Perangkat Kerja |   |   |

3. **PENGEMBALIAN ASET PERUSAHAAN**

| No | Jenis Akses | Ceklis | Keterangan |
|---|---|---|---|
| 1 | Laptop |   |   |
| 2 | Handphone |   |   |
| 3 | ID Card |   |   |
| 4 | Access Card |   |   |
| 5 | Dokumen Perusahaan |   |   |
| 6 | Peralatan Kerja lainnya |   |   |

4. **HASIL VERIFIKASI**
- Berdasarkan pemeriksaan yang telah dilakukan, seluruh akses yang dimiliki karyawan tersebut telah dicabut sesuai dengan ketentuan perusahaan dan seluruh aset perusahaan yang menjadi tanggung jawab karyawan telah diperiksa status pengembaliannya sebagaimana tercantum dalam berita acara ini.
- Catatan :
- 1.
- 2.
- 3.
1. **PERNYATAAN KARYAWAN**
    - Dengan ditandatanganinya berita acara ini, maka proses pencabutan akses karyawan dinyatakan telah dilaksanakan sesuai prosedur yang berlaku di PT. Bharata Internasional Pharmaceutical.
    - Cilacap,.……,……………………
    - **PIHAK YANG MELAKUKAN**
    - **PENCABUTAN AKSES, DIVERIFIKASI OLEH,**

| …………………………. |
|---|
| HRGA |

| ………………………….. |
|---|
| PENANGGUNGJAWAB |

- **MENGETAHUI,**
- **………………………..**
- **ATASAN LANGSUNG**

## Template Blueprint Flowchart

**Berkas sumber**: `Template Blueprint Flowchart.docx`

- **Template Proposal, Blueprint, dan Flowchart**
- Lampiran E-Ticket Permintaan Pengembangan Software
- **1\. Template Proposal (Form E-Ticket Development)**

| Nama Departemen |   |
|---|---|
| Nama PIC |   |
| Judul Permintaan |   |
| Kategori (New Dev/Enhancement/Integration/Automation/Bug Fix) |   |
| Latar Belakang Kebutuhan |   |
| Tujuan Pengembangan |   |
| Proses Bisnis Saat Ini |   |
| Proses Bisnis yang Diinginkan |   |
| Dampak Bisnis |   |
| Deadline yang Diharapkan |   |
| Estimasi Kompleksitas (diisi Tim IT: Minor/Medium/Major) |   |
| Lampiran |   |

- Catatan: Lampiran wajib mencakup Blueprint Aplikasi dan Flowchart Rancangan Aplikasi (lihat template bagian 2 dan 3). Tanpa lampiran ini, tiket tidak diproses ke tahap analisa.
- **2\. Template Blueprint Aplikasi**
- **2.1 Ringkasan Aplikasi**

| Nama Aplikasi/Fitur |   |
|---|---|
| Tujuan Utama |   |
| Target Pengguna |   |
| Platform (Web/Mobile/Desktop/Internal Tool) |   |

- **2.2 Ruang Lingkup Fungsional**
    - Fitur utama 1 : ..........................................
    - Fitur utama 2 : ..........................................
    - Fitur utama 3 : ..........................................
    - Batasan/di luar scope : ..........................................
- **2.3 Arsitektur & Komponen Teknis**

| Frontend/Interface |   |
|---|---|
| Backend/Service |   |
| Database |   |
| Integrasi Sistem Lain |   |
| Keamanan (autentikasi, hak akses) |   |

- **2.4 Data & Struktur Utama**
    - Entitas/tabel utama : ..........................................
    - Sumber data : ..........................................
    - Kebutuhan laporan/dashboard : ..........................................
- **2.5 Alur Data & Proses (Data Flow)**
- Jelaskan data mengalir dari mana ke mana, diproses apa, dan disimpan di mana.

| Data Masuk (Input) | Sumber | Proses / Rumus / Logika | Output / Disimpan Di |
|---|---|---|---|
|   |   |   |   |
|   |   |   |   |
|   |   |   |   |

- Contoh: Input = jam masuk & jam keluar karyawan | Sumber = mesin absensi | Proses = total jam kerja = jam keluar - jam masuk, lembur jika > 8 jam | Output = tabel rekap_absensi, tampil di dashboard HR
- **2.6 Risiko dan Ketergantungan**
    - Risiko teknis : ..........................................
    - Ketergantungan sistem lain : ..........................................
- **3\. Template Flowchart Rancangan Aplikasi**
- Gambarkan alur penggunaan aplikasi dari sisi user, dari mulai akses hingga proses selesai. Setiap kotak proses wajib disertai keterangan data & rumus/logika di bawahnya.
- Mulai / User Mengakses Aplikasi
- Login / Autentikasi
- Input Data / Pilih Menu Utama
- Data yang diinput : .......................................... | Sumber : ..........................................
- Proses Sistem (validasi, perhitungan, penyimpanan)
- Rumus/Logika : .......................................... | Disimpan di tabel : ..........................................
- Output / Hasil ditampilkan ke User
- Bentuk output : (tabel/grafik/notifikasi/laporan) ..........................................
- Selesai
- Catatan: Setiap kotak 'Proses Sistem' harus dijabarkan rumus/logika perhitungannya (bukan hanya nama proses), agar Developer tidak menerka-nerka. Jika ada banyak proses berbeda, tambahkan kotak & keterangan terpisah untuk masing-masing. Percabangan (valid/tidak valid) ditambahkan sebagai kotak keputusan dengan dua anak panah keluar.

## Dokumen Terkait

- [[REF - SOP Bharata 2026 per Posisi]]
