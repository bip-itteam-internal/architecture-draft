---
publish: false
---
# ANALISA — Kesesuaian Materi oleh Peserta dan Kenaikan Skor KPI Peserta

Daftar task hasil `/analisa-kebutuhan` (2026-09-17). Keputusan: [[ADR - 0102 Kesesuaian Materi Dinilai Peserta dan Dampak Pelatihan dari Kenaikan Skor KPI]]. Papan kerja, berubah tiap item selesai; bukan arsitektur, bukan rencana per berkas.

**Urutan wajib**: learning-service dan employee-service naik BERSAMA begitu T3/T4 ikut (kontrak `GET /kpi/pelatihan` bertambah; untuk T1-T2 saja urutannya bebas, lihat ADR § Konsekuensi deploy), lalu erp-frontend, lalu rilis MyBharata. **Prod dijalankan MANUSIA.** Tanpa env baru, tanpa kategori inbox baru, tanpa migrasi.

## Fase 0 — Prasyarat

- [x] **T0. Ukur ulang prod sebelum mulai (baca saja).** `trainer_evaluation` (0 per 2026-09-17: bila sudah terisi, kiriman lama tak punya jawaban kesesuaian dan tak bisa dilengkapi), cakupan `kpi_score` per bulan (107-165 karyawan per 2026-09-17), dan jumlah peserta kelas `Completed` yang punya skor di bulan sebelum mulai dan sesudah selesai. Angka nol yang mencurigakan diperlakukan sebagai pertanyaan.
	- ✅ **Hasil 2026-09-17 11.42 WIB** (baca saja): `trainer_evaluation` **0**. `kpi_score` per bulan: 2026-08 108 karyawan, 2026-07 165, 2026-06 146, 2026-05 152, 2026-04 107. Kelas `Completed` berpeserta **2**: yang selesai 2026-09-13 (3 peserta) punya skor bulan sebelum mulai untuk 1 dari 3 dan bulan sesudah selesai belum ada; yang selesai 2026-07-06 (1 peserta) punya skor di kedua bulan. Artinya metrik kenaikan baru akan berangka dari segelintir orang untuk beberapa bulan pertama.

## Fase 1 — Backend learning (`bip-erp/services/learning/`)

- [ ] **T1. Jawaban kesesuaian pada kiriman evaluasi.** Satu angka 1-10 per kiriman, disimpan TERPISAH dari `Ratings` empat aspek trainer, bertipe opsional (tidak dijawab dibedakan dari nilai apa pun). `ValidateRatings` dan pembagi `*4` tidak disentuh. Kiriman tanpa jawaban kesesuaian tetap 200 (klien MyBharata lama). Test: kiriman tanpa jawaban tetap sah; 0 dan 11 ditolak; agregat kepuasan tak berubah dengan atau tanpa jawaban kesesuaian (kontrol hitung ganda). Dependensi: T0.
- [ ] **T2. Kontrak `GET /kpi/pelatihan` bertambah.** Jumlah responden dan jumlah nilai **kesesuaian** (terpisah dari evaluasi kepuasan), serta bulan mulai dan bulan selesai kelas per pendaftaran. Literal kontrak di test learning diperbarui, sehingga uji kontrak di employee yang membacanya verbatim ikut menjaga. Dependensi: T1.
	- 🔜 **T1 dan T2 selesai ditulis 2026-09-17** di branch bip-erp `feat/learning-kesesuaian-materi` (termasuk struct cermin dan penggabungan batch di employee-service), sudah `/review`; **belum PR, belum merged, belum deploy**. Rencana: `.task-plans/2026-09-17-learning-kesesuaian-materi-kontrak-kpi.md`. Kontrak dan aturan "jangan dijumlah" tercatat di [[API - Learning Service]], [[Microservices - Learning Service]], dan [[Microservices - Employee Service]].

## Fase 2 — Backend employee (`bip-erp/services/employee/`)

- [ ] **T3. Metrik `kesesuaian_materi_skala10` di sumber `pelatihan`.** Rata-rata langsung 1-10 atas kelas selesai di periode itu, *belum dapat dihitung* di bawah 3 responden kesesuaian, reduksi `rata_rata`. Label dan keterangan dua locale di katalog. Dependensi: T2.
- [ ] **T4. Metrik `kenaikan_kpi_peserta_persen` di sumber `pelatihan`.** Periode P menarik pendaftaran kelas selesai di **P-2**. Per peserta, `kpi_score.score` bulan sebelum mulai lawan bulan sesudah selesai: 100 bila naik, 0 bila sama atau turun, keluar dari nilai tapi tetap di populasi bila salah satu skor tak ada. Tanpa ambang. Orang yang dinilai tak masuk populasinya sendiri (perilaku cakupan yang ada). Rincian wajib menyebut bulan kelas, dua bulan pembanding, dan berapa peserta tanpa skor. Test: naik/sama/turun, skor hilang di salah satu sisi, kelas multi-bulan, dan kontrol bahwa periode P tidak membaca kelas P-1. Dependensi: T2.

## Fase 3 — Web (`erp-frontend`)

- [ ] **T5. Pertanyaan kesesuaian di dialog penilaian pasca-pelatihan.** Skala 1-10 (kembangkan pola `SkalaAngka` atau komponen setara, jangan komponen shared baru demi satu pemanggil), tidak menghalangi kirim bila dikosongkan sesuai keputusan opsional. i18n dua locale. Dependensi: T1.
- [ ] **T6. Label dan satuan dua metrik baru di Atur Target / Otomasi KPI.** Pola `kepuasan_trainer_skala10` (keterangan wajib menyebut skala dan jeda dua bulan). Dependensi: T3, T4.

## Fase 4 — MyBharata

- [ ] **T7. Pertanyaan kesesuaian di lembar penilaian trainer.** Pakai ulang `SurveyScaleInput` + `CustomFormField`; model mengirim field baru hanya bila dijawab; test `toJson` diperbarui. l10n dua bahasa. Rilis menaikkan version name DAN code. Dependensi: T1.

## Fase 5 — Deploy, konfigurasi, verifikasi

- [ ] **T8. Deploy dan verifikasi lewat gateway.** learning + employee bersamaan, lalu frontend, lalu rilis MyBharata. Gerbang biner per service dengan kontrol positif dan negatif. Satu perjalanan utuh: peserta kelas `Completed` mengirim penilaian dengan dan tanpa kesesuaian; `GET /api/learning/kpi/pelatihan` memuat jumlah kesesuaian dan bulan kelas; metrik kesesuaian *belum dapat dihitung* di bawah 3 responden lalu berangka sesudahnya. **PROD: agent siapkan perintah, manusia jalankan.** Dependensi: T3-T7.
- [ ] **T9. HR memasang sumber di Atur Target** (`People and Development`): `Kesesuaian materi LMS dengan jobdesk` → `pelatihan` / `kesesuaian_materi_skala10`; `Skor Penilaian Training All Karyawan > 70` → `pelatihan` / `kenaikan_kpi_peserta_persen`. Sesudahnya verifikasi baca prod bahwa template memuat kedua blok `auto`. Dependensi: T8.

## Di luar daftar ini (keputusan terpisah)

- **Jobdesk per posisi dan kurikulum per jabatan**: jalankan `/analisa-kebutuhan` tersendiri bersama metrik Recruitment "Ketersediaan Dokumen Jobdesk diseluruh posisi" (0,25). Pertanyaan pokok: siapa menulis jobdesk 122 jabatan dan kapan; baru sesudah itu wadahnya (master per `position_key` di employee-service atau Dokumen HRD berjenis jobdesk).
- **Kelas "time management" yang terkunci** (Completed tanpa bank soal pre, 3 peserta): butuh keputusan penanganan terpisah.

## Cara Verifikasi (untuk gerbang `/wrap`)

- **Hitung ganda**: agregat dan metrik `kepuasan_trainer_skala10` identik sebelum dan sesudah jawaban kesesuaian ditambahkan pada data uji yang sama.
- **Klien lama**: kiriman penilaian tanpa field kesesuaian tetap 200 lewat gateway.
- **Jeda dua bulan**: metrik kenaikan pada periode P hanya membaca kelas yang selesai di P-2, dibuktikan test dengan kontrol kelas P-1.
- **Kontrak**: literal muatan `GET /kpi/pelatihan` di learning dibaca verbatim oleh uji kontrak employee.
- **Perjalanan orang**: satu peserta menilai di MyBharata versi baru dan satu di web; HR melihat metrik terisi di Atur Target sesudah konfigurasi.
