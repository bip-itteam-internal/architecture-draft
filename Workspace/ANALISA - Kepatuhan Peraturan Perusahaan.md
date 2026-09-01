# ANALISA - Kepatuhan Peraturan Perusahaan

Papan kerja hasil `/analisa-kebutuhan` 2026-09-01. Keputusannya di [[ADR - 0071 Peta Kepatuhan Peraturan Perusahaan dan Kewajiban ADR untuk Penyimpangan]], petanya di [[HRIS - Kepatuhan Peraturan Perusahaan]].

**Kebutuhan asal** (dari manajemen): "ingin tahu logika yang dijalankan sistem backend, terutama yang menentukan gaji dan sanksi". Usulan awalnya membangun MCP untuk backend. Wawancara menyempitkannya jadi **audit kepatuhan sekali jalan**, dan grounding menemukan bahwa alat baca tidak menjawabnya: penyimpangan terbesar sudah ditemukan dan ditulis sejak 2026-08-26, yang tidak terjadi adalah tindak lanjutnya.

---

## T1. Konfirmasi HRD: pengali mangkir sehari, 2 atau 1,5? ⛔ MENDESAK

**Bukan task kode.** Ini keputusan orang, dan ia memblokir T2.

Config produksi `alpha_multiplier_one_day` bernilai **2**, disetel Gilang Permatasari (Human Resource / Personalia) pada 2026-08-21 09:54 WIB. Peraturan Perusahaan Pasal 20 mengatur **1,5**. Dampak terukur pada dua run draft: kelebihan potong **Rp 141.266** atas 8 orang.

**Kenapa mendesak**: kedua `payroll_run` masih `draft`, jadi belum ada rupiah yang sampai ke karyawan. Begitu satu run di-`approve` lalu `published`, slip men-snapshot angkanya dan koreksi menuntut pembatalan run.

Dua kemungkinan hasil, keduanya sah:
- HRD menghendaki 2 → lanjut ke T3 (terbitkan ADR penyimpangan), config **tidak** diubah
- HRD tidak menghendaki 2 → lanjut ke T2 (kembalikan ke 1,5)

## T2. Kembalikan `alpha_multiplier_one_day` ke 1,5 di produksi

**Bergantung T1.** Hanya dikerjakan bila HRD menyatakan 1,5 yang benar.

Lewat tab **Potongan Kehadiran** di Pengaturan > Payroll (`PUT /config/attendance-deduction`), bukan deploy. ⛔ **Menulis ke produksi, jadi manusia yang menjalankannya**, bukan agent.

Gerbang verifikasi: baca ulang `payroll_config.attendance_deduction` di `Payroll-MongoDB` dan pastikan nilainya 1,5; lalu `recalculate` kedua run draft dan pastikan kedelapan baris ber-mangkir satu hari turun total Rp 141.266.

## T3. ADR penyimpangan ambang 4 jam uang makan

Peraturan menyatakan izin jam kerja memotong tunjangan kehadiran dan uang makan **tanpa ambang**; implementasi memakai ambang 4 jam (`meal_threshold_hours`), keputusan pemilik produk 2026-08-20. Sudah **dua kali** diminta jadi ADR di dokumennya sendiri dan belum pernah dibuat.

`/start-task terbitkan ADR untuk penyimpangan ambang 4 jam uang makan dari Pasal 20`

## T4. ADR "SP1 diusulkan, bukan terbit otomatis"

Peraturan menulis terlambat 3x per bulan "otomatis memicu SP1"; sistem sengaja hanya **mengusulkan** dan HR yang menerbitkan. Alasannya sudah ditulis di `services/employee/warning_suggest.go:22-31` tetapi belum jadi keputusan bernama.

## T5. Verifikasi ulang baris bertanda ° di peta, lalu lengkapi

Baris cuti dan ambang keterlambatan di [[HRIS - Kepatuhan Peraturan Perusahaan]] berasal dari penelusuran dan belum dibuka langsung. Yang perlu dipastikan satu per satu:

- katalog durasi izin dibayar versus tabel Pasal 18, baris per baris
- apakah 90 hari melahirkan sama dengan "1,5 bulan sebelum + 1,5 bulan sesudah"
- ibadah haji 50 hari, ada di katalog atau tidak
- perilaku cron reset cuti 1 Januari versus "hangus akhir tahun berikutnya"
- dua ambang di `company_attendance_setting`, nilai produksinya berapa

⚠️ Klaim "tidak ada" wajib dibuktikan `git grep` dengan kontrol positif, bukan `Grep`. Penelusuran pertama sempat melaporkan nol kecocokan untuk sesuatu yang sebenarnya ada delapan kemunculannya.

## T6. Klarifikasi perusahaan acuan

`payroll_config.company.name` di produksi berbunyi `CV Pure Glow Lux`, sementara Peraturan Perusahaan yang dipetakan milik PT Bharata Internasional Pharmaceutical. Config itu `_id: singleton`, satu untuk semua, padahal ada 41 dokumen `payroll_company`. Perlu dipastikan apakah aturan pajak, BPJS, dan potongan memang seragam lintas perusahaan.

## T7. Putuskan sanksi yang belum ada: sengaja atau tertunda

Enam aturan sanksi tidak punya implementasi sama sekali: SP II potong 25% gaji pokok, eskalasi SP1 ke SP2 ke SP3, masa perbaikan 1 bulan, skorsing 3 bulan dengan pencabutan akses, dan dua denda Pasal 54 (Rp 2 miliar dan Rp 5 miliar). `employee_warning` di produksi masih **0 dokumen**.

Yang diputuskan bukan "bangun sekarang", melainkan apakah ketiadaannya **sengaja**. Bila sengaja, tulis di [[HRIS - Disciplinary (Surat Peringatan)]] supaya berhenti terbaca sebagai lubang.

## T8. Aturan lembur: SPKL, tim produksi, dan tarif

Tiga aturan Pasal 25 belum berjalan, dan pembagi lembur `173` hardcode di `services/payroll/payroll_calc.go:327` sementara pembagi yang sama untuk potongan adalah config. Perbedaan itu membuat satu jam bernilai berbeda saat menambah dan saat mengurangi.

Kerjakan setelah T1 sampai T4 selesai; ini yang paling besar dan paling tidak mendesak, karena lembur belum pernah masuk slip yang terbit.

## T9. (Ditunda sadar) Gerbang otomatis dok versus config produksi

Membaca config produksi lalu membandingkannya dengan nilai yang didokumentasikan, dan gagal bila berbeda. **Jangan diputuskan sebelum T5 selesai**: jumlah penyimpangan yang ditemukan audit pertama yang menentukan apakah pengawas ini sepadan.

---

## Yang TIDAK jadi dikerjakan, beserta alasannya

- **MCP baca kode backend.** Sudah ada dua mekanisme (`bip-erp/tools/code-index` dengan `CODE-INDEX.json` basi sejak 30 Juli, dan `codebase-memory-mcp` yang mendukung Go tetapi belum diindeks untuk bip-erp). Yang ketiga akan jadi sumber kebenaran ketiga.
- **MCP baca data ERP.** Layak secara teknis (gateway punya `GET /auth/refresh` sehingga identitas pemakai bisa dipertahankan tanpa RBAC kedua), tetapi **tidak menjawab kebutuhan ini**: dua area yang paling ditanyakan justru datanya kosong, yaitu `employee_warning` 0 dokumen dan payroll 0 slip terbit. Dianalisis terpisah.
