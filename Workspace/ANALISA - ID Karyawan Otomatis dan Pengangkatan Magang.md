# ANALISA - ID Karyawan Otomatis dan Pengangkatan Magang

Papan kerja untuk [[ADR - 0126 employee_id Diterbitkan Sistem, Magang yang Diangkat Mendapat ID Reguler dengan Migrasi Riwayat]]. Dibuat 2026-09-25 lewat `/analisa-kebutuhan`. Bukan dok terbit; keputusan dan alasannya di ADR, cara kerjanya di [[HRIS - Personalia]] §ID Karyawan & Pengangkatan Magang.

**Kebutuhan:** ID karyawan tidak lagi diketik manusia (hari ini 6 pasang nomor urut dobel dan 5 magang tanpa `MG`), dan magang yang diangkat berhenti ber-ID magang tanpa kehilangan riwayatnya.

## Konfirmasi yang ditunggu (bukan kode)

- [ ] **K1 HR**: aturan "nomor induk baru saat diangkat" tertulis di mana (SOP, SK)? Tidak ada di Peraturan Perusahaan 2026-2028 (dibaca 2026-09-25). Juga: apakah ada kartu karyawan FISIK yang dicetak ber-ID dan wajib dicetak ulang.
- [ ] **K2 Finance**: magang mana yang punya proyek Accurate bernomor `employee_id` (regex integration menerima `BIP-MG-`). Menentukan langkah manual di runbook T4.

## Task (berurutan)

- [ ] **T1 BE employee-service + orchestrator HRIS: alokator `employee_id` atomik.** Penghitung per (awalan, deret) dengan `FindOneAndUpdate`+`$inc`+upsert (pola terdekat: `services/learning/sertifikat.go:207-219`, kunci komposit); deret dari `employment_type` kontrak pertama; `MM-YY` dari `join_date` WIB; periksa ID rakitan belum dipakai lalu ulang; nilai `employee_id` dari body diabaikan/ditolak (`services/employee/main.go:494-527`, `orchestrator/hris/handler.go:26-34`). Seed idempoten diukur dari data saat deploy (nilai wajar, per awalan ID), bukan konstanta. Uji: alokasi paralel tak pernah kembar, `SystemInitAdmin` tak memanikkan parser, seed tak menerbitkan nomor terpakai, magang masuk deret `MG`. Dependensi: T5 sebaiknya selesai lebih dulu supaya seed magang diukur dari ID ber-`MG` (bila tidak, seed tetap harus memperhitungkan blok `BIP-1008..1012` tanpa `MG`). Deploy: employee-service + orchestrator sebelum T2.
- [ ] **T2 FE form Tambah Karyawan: hapus field ID.** Hapus `InputOTPForm` ID dan cek unik ID dari wizard (`create-employee/step1.tsx:137-142`, `index.tsx:306-360`); ID tampil di ringkasan/toast sesudah tersimpan; jalur "dari kandidat" memakai ID balasan backend untuk `link-employee` (`index.tsx:384-399`). i18n id+en. Dependensi: T1 deployed (BE dulu).
- [ ] **T3 Pemindaian koleksi besar.** Ukur rujukan `employee_id` di koleksi >50.000 dokumen yang dilewati pemindaian 2026-09-25 (22 koleksi: pesanan marketplace, `manufacture_resi`, `fulfillment_orders`, `webhook_logs`, dll.) lewat field terindeks, untuk satu magang dan satu karyawan pembanding. Hasilnya menentukan daftar "dipindai per field" di alat T4. Baca prod saja. Dependensi: tidak ada.
- [ ] **T4 Alat migrasi pengangkatan + runbook `RUN - Pengangkatan Magang (Ganti employee_id)`.** Menggeneralisasi `.task-plans/migrasi-id-magang.js`: target DITEMUKAN lewat pemindaian semua database (bukan daftar tangan, yang melewatkan `forms.subject.resolved` pada migrasi Agustus), koleksi besar per field dari T3, dry-run per koleksi/field, `mongodump`, tolak bila ID tujuan terpakai, alokasi ID dari penghitung reguler T1, gerbang sisa nol (kecuali path MinIO), dan daftar langkah manual (login ulang + biometrik, username = ID lama, Accurate, cache gateway). Diuji di DEV atas satu karyawan uji sebelum dipakai prod. Dependensi: T1 (penghitung), T3.
- [x] **T5 Rename 5 magang September ke `BIP-MG-`.** ✅ Dijalankan di PROD 2026-09-25 lewat `.task-plans/jalankan-migrasi-id-magang-september.ps1` (target dari pemindaian, gerbang field-tak-dikenal terbukti lewat kontrol negatif). Diverifikasi pemindaian ulang 20 container: 285 dokumen ber-ID baru, nol rujukan ID lama kecuali path berkas KTP/KK MinIO (disengaja). Kelima orang wajib login ulang di MyBharata. `BIP-1008..1012-09-26` → `BIP-MG-1008..1012-09-26`, nomor dipertahankan. Bisa memakai skrip Agustus yang diperbarui target-nya, atau alat T4 bila sudah jadi. Tulis prod = dijalankan manusia. Dependensi: sebelum seed T1 (lihat T1).
- [ ] **T6 Angkatan pertama: `BIP-MG-1004-06-26` (Fitri Baniaturrohmah).** Sudah PKWT (Evaluasi) tapi masih ber-ID magang, jadi kasus nyata pertama untuk alat T4. Dependensi: T4, K1.

## Terpisah, jangan disisipkan ke task di atas

- **`services/procurement/kas_katalog_accurate.go:100`** hanya menerima `^BIP-\d{4}-\d{2}-\d{2}$`: menolak `BIP-MG-` dan awalan perusahaan lain. Tak berdampak selama magang tak memegang kas; brief tersendiri bila berubah.
- **Hardcode ID** di `services/employee/main.go:2833` (Direktur) dan `services/attendance/main.go:3721` (supervisor IT) tak tersentuh keputusan ini, tetapi patah bila salah satu orang itu kelak berganti ID.
- **6 pasang nomor urut dobel** dibiarkan (ADR 0126 §6). Bila HR tetap ingin merapikannya, itu migrasi ganti ID biasa lewat T4, bukan pekerjaan fitur.
- **SPEC lama** `.task-plans/2026-08-19-employee-id-otomatis-SPEC.md` digantikan ADR 0126; jangan dikerjakan dari berkas itu.
