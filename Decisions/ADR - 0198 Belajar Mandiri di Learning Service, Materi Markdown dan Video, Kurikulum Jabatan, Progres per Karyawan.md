# ADR - 0198 Belajar Mandiri di Learning Service, Materi Markdown dan Video, Kurikulum Jabatan, Progres per Karyawan

> **Status**: 🟢 Diterima, 2026-10-22, oleh irfanarfianto (Pemutus). Butir 1 (materi Markdown, bukan PDF) adalah usul langsung Pemutus; butir 4 sampai 6 diputuskan orkestrator atas mandat Pemutus ("kerjakan, jangan tanya") dan ditulis di sini supaya bisa ditinjau. Melanjutkan [[ADR - 0196 Pelatihan Bisa Dipakai Penuh dari MyBharata, Soal Beragam, Buka Ulang Pre-test, dan Kelas Berulang]] dan desain LMS `docs/superpowers/specs/2026-08-05-lms-people-development-design.md` (Fase 1b sampai 3), dan **mengubah** dua keputusan desain LMS itu (butir 1 dan 4).

## Untuk Manajemen

**Apa yang berubah.**
- Karyawan bisa **belajar mandiri** dari MyBharata, tanpa kelas: materi bacaan (teks dan gambar) dan video, pre-test, post-test, lalu sertifikat.
- Materi wajib ditentukan **per jabatan** (kurikulum) dengan **tenggat**, dan HR bisa menugaskan materi tambahan ke orang tertentu.
- HR melihat progres tiap karyawan: belum mulai, berjalan, lulus, lewat tenggat.

**Yang tidak berubah.** Kelas tatap muka tetap seperti ADR 0196. Aturan lulus tetap "nilai post-test naik dari pre-test".

## Context

Diukur 2026-10-22 di `bip-erp` `origin/main`:
- `course` di learning-service sengaja tipis: judul, deskripsi, batas percobaan, bank soal pre/post. **Tidak ada isi materi**, kurikulum, penugasan, tenggat, maupun progres (`services/learning`, nol kemunculan `curriculum`, `course_progress`, `minio`).
- Pre-test dan post-test hanya bisa dimulai **lewat kelas** (`/me/pre-test/:trainingId/start`, `/me/post-test/:trainingId/start`). Sertifikat dan evaluasi juga terikat kelas.
- file-service membatasi unggahan **4 MB** untuk semua prefix (`services/file/main.go:337`). Desain LMS lama menetapkan PDF 20 MB.
- MyBharata sudah memuat `flutter_markdown_plus` dan `cached_network_image`; erp-frontend sudah memuat `@uiw/react-md-editor`, `react-markdown`, `rehype-sanitize`.
- Desain layar: Figma file design system MyBharata, halaman **Pelatihan** (bagian "Tatap muka vs Belajar mandiri" dan "Alur halaman LMS").

## Decision

1. **Isi materi = Markdown (teks + gambar) atau video tautan. PDF tidak dipakai** (usul Pemutus, untuk menghemat server).
   - Markdown disimpan di dokumen `course` (Mongo), maksimal 100 KB per materi. Gambar diunggah ke file-service dengan prefix sendiri `learning/` dan tetap tunduk pada batas 4 MB yang ada; file-service **tidak** diubah batasnya.
   - Gambar disajikan **lewat learning-service** (proxy yang memeriksa hak baca pemanggil), bukan lewat kunci baca MinIO di klien.
   - Video = tautan (YouTube unlisted / Drive), seperti desain LMS lama.
   - Markdown dirender aman: HTML mentah dimatikan/disanitasi di web dan mobile.
2. **Penugasan** punya dua sumber, keduanya menghasilkan baris penugasan per (karyawan, course):
   - **Kurikulum jabatan**: `{department_key, position_key, items[course_id, wajib, urutan], target_days}`. Tenggat = yang lebih akhir dari tanggal masuk karyawan dan tanggal kurikulum diterbitkan, ditambah `target_days` (aturan desain LMS lama).
   - **Penugasan manual HR** per karyawan, dengan tenggat tanggal.
3. **Progres melekat pada (karyawan, course)**, bukan pada kurikulum: berpindah jabatan tidak mengulang course yang sudah lulus. Status: `belum_mulai`, `berjalan`, `lulus`; `lewat_tenggat` adalah keadaan turunan (tenggat lewat dan belum lulus), bukan status tersimpan.
4. **Urutan belajar** (MENGUBAH desain LMS lama, yang tidak mencatat pembukaan materi sama sekali):
   - Bila course punya pre-test, materi terbuka **setelah** pre-test dikirim (pre-test mengukur kemampuan awal).
   - Pembukaan materi **dicatat** per materi sebagai **penanda navigasi** ("sudah dibuka"), bukan bukti belajar.
   - Post-test terbuka setelah **semua** materi pernah dibuka (pola LMS umum: ujian akhir sesudah semua modul).
   - Kelulusan tetap ditentukan post-test: **naik dari pre-test** (aturan `NaikDariPreTest` yang ada).
5. **Test-out**: course boleh mengisi `test_out_persen` (0 = mati, **bawaan mati**). Bila skor pre-test (sudah final, termasuk essay yang sudah dinilai) mencapai ambang itu, course **lulus** tanpa post-test. Ini menutup celah "pre-test 100 mustahil naik".
6. **Lewat tenggat tetap bisa dikerjakan**; yang berubah hanya status tampilannya. Pengingat tenggat lewat notifikasi **di luar cakupan ADR ini** (issue tersendiri, karena menambah kategori inbox = deploy dua container).
7. **Sertifikat** belajar mandiri terbit begitu lulus (tidak ada penilaian trainer). **Penilaian materi** (kejelasan, kegunaan, kesesuaian; komponen form yang sama dengan kelas) opsional dan **tidak menahan** sertifikat.
8. **Satu mesin ujian**: pre/post-test mandiri memakai `quiz`, `quiz_attempt`, skoring, penilaian essay, batas percobaan, dan jeda yang SAMA dengan kelas. Yang ditambah hanya jalur mulai berbasis course (tanpa `trainingId`); aturan penilaian tidak disalin.
9. **Course diterbitkan** (`published`) hanya bila punya post-test dan minimal satu materi; draf tidak terlihat peserta.

## Alternatif yang Ditolak

- **PDF materi 20 MB lewat file-service.** Ditolak Pemutus (beban server), dan menuntut perubahan batas file-service.
- **Tidak mencatat pembukaan materi** (desain LMS lama). Ditolak: peserta dengan 4 materi kehilangan posisinya, dan post-test bisa dikerjakan tanpa pernah melihat materi.
- **Kelulusan ambang tetap (70%).** Ditolak: mengubah aturan lulus yang sudah diputuskan 2026-09-16; celahnya ditutup test-out.
- **Kunci baca MinIO di klien untuk gambar.** Ditolak: kunci baca yang sampai ke klien membuka seluruh prefix.

## Consequences

- learning-service bertambah koleksi `curriculum`, `course_assignment`, `course_progress`, `course_material_opened` (atau setara), dan `course` bertambah `contents`, `status`, `test_out_persen`.
- file-service bertambah satu kunci prefix `learning/` (env baru di file-service dan learning-service).
- Endpoint peserta baru `/me/courses*`; endpoint kelas yang ada tidak berubah.
- erp-frontend butuh layar kelola materi (editor Markdown + unggah gambar), kurikulum, penugasan, dan laporan progres.
- MyBharata menampilkan Markdown dengan gambar lewat proxy ber-token.
- KPI pelatihan (`rakitKPIPelatihan`) kelak menghitung course mandiri juga; di luar cakupan irisan pertama.

## Terkait

- [[ADR - 0196 Pelatihan Bisa Dipakai Penuh dari MyBharata, Soal Beragam, Buka Ulang Pre-test, dan Kelas Berulang]] · [[HRIS - Training Program]] · [[Microservices - Learning Service]]
