# ANALISA - To-do Harian Pribadi

> ⛔ **Menunggu ADR [[ADR - 0170 To-do Harian Pribadi di Task Management dengan Pantauan Atasan Efektif]] Diterima: sebelum itu ANALISA ini BUKAN keputusan yang bisa ditunjuk `/brief`.**

- **Keputusan**: [[ADR - 0170 To-do Harian Pribadi di Task Management dengan Pantauan Atasan Efektif]]
- **Konsep domain**: [[HRIS - To-do Harian Pribadi (Modul)]]
- **Pemutus**: irfanarfianto
- **Tanggal analisa**: 2026-10-11
- **Ukuran**: **Besar**. Dua repo harus berubah, dan masing-masing butuh dua PR:
  - `bip-erp`: endpoint internal atasan efektif di employee-service, lalu koleksi dan rute to-do di task-management. Dua service, dan konvensi tim satu branch per service.
  - `my-bharata`: tab Hari Ini + kartu Beranda, lalu tampilan bawahan. Tidak ada layar to-do yang sudah merender bentuk ini secara generik (`git grep` atas `origin/dev`: nol entitas to-do; `getTasks` hanya punya param scope + status, `task_remote_datasource.dart:87-105`).
  - `erp-frontend` **tidak berubah**: tahap 1 hanya MyBharata (ADR §9).

## Urutan

| # | Issue | Repo | Bentuk | Urutan |
|---|---|---|---|---|
| 0 | To-do harian pribadi dengan pantauan atasan efektif | bip-erp | induk, tanpa PR | - |
| 1 | [BE] Endpoint internal atasan dan bawahan efektif (bagian 1/2) | bip-erp | sub-issue | pertama |
| 2 | [BE] Koleksi to-do, daftar hari ini, dan pantauan bawahan (bagian 2/2) | bip-erp | sub-issue | sesudah #1 merged |
| 3 | [Mobile] To-do hari ini di Beranda dan tab Hari Ini (bagian 1/2) | my-bharata | sub-issue | deploy sesudah #2 |
| 4 | [Mobile] Tampilan to-do bawahan untuk atasan efektif (bagian 2/2) | my-bharata | sub-issue | sesudah #3 merged |

---

## 0. To-do harian pribadi dengan pantauan atasan efektif

- **Repo**: bip-erp · **Bentuk**: induk (tanpa PR) · **Issue**: (diisi saat dibuat)

**Pemutus:** @irfanarfianto
**PIC:** @

### Masalah

Atasan baru tahu pekerjaan bawahan macet setelah terlambat. Pekerjaan harian yang tidak berbentuk tiket tidak tercatat di sistem. Laporan harian yang diwajibkan SOP beberapa posisi tersebar di Excel dan chat.

### Keputusan

[[ADR - 0170 To-do Harian Pribadi di Task Management dengan Pantauan Atasan Efektif]]. Layak `Siap Agent` sesudah ADR berstatus Diterima.

### Yang harus benar

- [ ] Keempat sub-issue merged, dan urutan deploy employee-service → task-management → MyBharata diikuti.

### Di luar cakupan

KPI, Web ERP, notifikasi/pengingat, kewajiban bukti, feed kalender.

### Data / bukti pendukung

Lihat bagian Context ADR (ukur prod 2026-10-11).

### Prasyarat

Tidak ada.

---

## 1. [BE] Endpoint internal atasan dan bawahan efektif (bagian 1/2)

- **Repo**: bip-erp (`services/employee`) · **Bentuk**: sub-issue induk #0 · **Issue**: (diisi saat dibuat)

**Pemutus:** @irfanarfianto
**PIC:** @

### Masalah

Task-management perlu tahu siapa atasan efektif seseorang (atasan langsung, atau supervisor departemen bila kosong) dan siapa bawahan efektif seseorang. Resolusinya sudah ada di employee-service sebagai `atasanPengingat` (`services/employee/contract_pengingat.go:183-199`), tetapi hanya dipakai pengingat kontrak dan tidak bisa dipanggil service lain. `/me/subordinates` (`services/employee/main.go:3306`) hanya mengenal `supervisor_id`, tanpa fallback.

### Keputusan

[[ADR - 0170 To-do Harian Pribadi di Task Management dengan Pantauan Atasan Efektif]] §5. Layak `Siap Agent` sesudah ADR berstatus Diterima.
- Atasan efektif = `supervisor_id` bila sah, bila kosong rantai penyetuju cuti, persis `atasanPengingat`. Rantai yang menunjuk orang itu sendiri = tanpa atasan.
- Dua rute internal berkunci layanan: atasan efektif satu karyawan, dan daftar bawahan efektif satu atasan. Satu perusahaan saja.

### Yang harus benar

- [ ] Rute atasan efektif memanggil `atasanPengingat` (atau fungsi yang sama-sama dipakainya); tidak ada salinan kedua rantai resolusi. Uji: karyawan ber-`supervisor_id` sah → atasan itu; `supervisor_id` kosong → supervisor departemen; `supervisor_id` menunjuk akun nonaktif → jatuh ke rantai; supervisor departemen yang rantainya menunjuk dirinya → kosong.
- [ ] Untuk karyawan General Affair tanpa `supervisor_id`, atasan efektifnya supervisor HR (aturan `supervised_by`), dibuktikan uji.
- [ ] Rute bawahan efektif mengembalikan gabungan bawahan langsung (`supervisor_id` = pemanggil, akun aktif) dan karyawan tanpa atasan langsung sah yang rantainya menunjuk pemanggil; tanpa duplikat; hanya `company_id` yang sama.
- [ ] Kedua rute menolak permintaan tanpa kunci layanan yang benar dengan 401/403, diuji lewat `app.Test` (gateway meneruskan `/internal/` dari internet).
- [ ] Rute didaftarkan dengan memperhitungkan pemotongan prefix `/api/<module>` oleh gateway; ada uji yang memanggil path setelah pemotongan.
- [ ] Kunci layanan baru (bila ada) tercatat di `.env` dev sebelum merge dan disebut di badan PR.

### Di luar cakupan

Mengubah alur persetujuan pengajuan; mengubah `/me/subordinates`; endpoint publik untuk FE.

### Data / bukti pendukung

Prod 2026-10-11: 181 karyawan aktif ber-`work_data`, **84** ber-`supervisor_id` (8 atasan berbeda: 22, 15, 12, 12, 11, 6, 4, 2 bawahan), 11 `is_supervisor`. Per departemen ber-`supervisor_id`/total: Beautyhacks 40/45, Manufaktur 1/33, Kyura 16/30, Finance 0/16, General Affair 12/13, Percetakan 0/13, Kesekretariatan 7/8, Quality 0/6, Human Resource 4/5, Tech Development 4/5, Marketing Offline Distribution 0/4, Procurement 0/3. Semua `company_id` = BIP.

### Prasyarat

Tidak ada.

---

## 2. [BE] Koleksi to-do, daftar hari ini, dan pantauan bawahan (bagian 2/2)

- **Repo**: bip-erp (`services/task-management`, `docker-compose.yml`) · **Bentuk**: sub-issue induk #0 · **Issue**: (diisi saat dibuat)

**Pemutus:** @irfanarfianto
**PIC:** @

### Masalah

Belum ada tempat menyimpan to-do pribadi. Tabel tiket tidak cocok: setiap tiket lahir `Request`, ber-SLA 24 jam, dan memberi notifikasi supervisor space (`services/task-management/task_handlers.go:126-160`). Tidak ada endpoint yang menggabungkan pekerjaan pribadi dan tiket saya untuk satu hari (`GET /tasks/filter` tak punya param tanggal, `task_filter.go:232-240`).

### Keputusan

[[ADR - 0170 To-do Harian Pribadi di Task Management dengan Pantauan Atasan Efektif]] §1-§7. Layak `Siap Agent` sesudah ADR berstatus Diterima.
- Koleksi baru; field inti `employee_id`, judul, catatan, `tanggal_rencana_awal` (immutable), `tanggal_rencana`, status `terbuka|selesai|dibatalkan`, `selesai_at`, `dibatalkan_at`, `bukti[]`, `wajib_bukti` (bawaan false, tanpa penulis).
- Tertunda dihitung saat dibaca (hari kalender WIB dari `tanggal_rencana_awal`); tidak ada job pemindah. Hanya pemilik menulis; batal tidak menghapus; tidak ada rute hapus.
- Atasan efektif dari rute internal #1; task-management tidak menghitung ulangnya.

### Yang harus benar

- [ ] Pemilik bisa membuat, mengubah judul/catatan, mengubah `tanggal_rencana`, menyelesaikan, dan membatalkan item miliknya. Permintaan yang sama atas item milik orang lain ditolak 403, termasuk dari atasannya.
- [ ] `tanggal_rencana_awal` tidak berubah oleh rute apa pun sesudah dibuat (uji: ubah `tanggal_rencana` lalu baca ulang).
- [ ] Tidak ada rute DELETE untuk item to-do. Item dibatalkan tetap terbaca oleh pemilik dan atasan efektif.
- [ ] Daftar hari ini pemilik berisi: to-do `terbuka` dengan `tanggal_rencana` ≤ hari ini WIB, to-do `selesai` dengan `selesai_at` hari ini WIB, dan tiket dengan `assign_to` memuat pemanggil, `completed_at` nil, `is_archived` bukan true, status bukan Ditolak, `due_date` ≤ akhir hari ini WIB. Tiap baris membawa `jenis: todo|tiket`.
- [ ] Baris to-do membawa `tertunda_hari` = selisih hari kalender WIB antara hari ini dan `tanggal_rencana_awal` (0 bila belum lewat). Uji batas hari pada 23:30 dan 00:30 WIB.
- [ ] Tidak ada scheduler atau goroutine baru yang menulis ke koleksi to-do.
- [ ] Rute ringkasan bawahan untuk atasan efektif: per bawahan, jumlah to-do terbuka hari ini, jumlah tertunda ≥ 3 hari, dan jumlah dibatalkan 7 hari terakhir. Pemanggil yang bukan atasan efektif orang itu menerima 403 untuk rincian bawahan tersebut.
- [ ] Rincian daftar hari ini seorang bawahan bisa dibaca atasan efektifnya. Baris tiket dari space `restricted` yang tak bisa diakses atasan itu tidak memuat judul, keluhan, atau deskripsi.
- [ ] Rute unggah, pratinjau, dan lepas bukti per item memakai file-service dengan pola `uploadTaskAttachment`; hanya pemilik yang boleh mengunggah atau melepas; atasan efektif boleh pratinjau. Ada uji `app.Test` untuk jalur galat tiap rute baru.
- [ ] Env `EMPLOYEE_MODULE_URL` (dan kunci layanan #1) ditambahkan ke blok task-management di compose tanpa kunci YAML ganda, terisi di `.env` dev sebelum merge; badan PR menyebut `--force-recreate`.
- [ ] Gagal memanggil rute internal #1 menghasilkan galat yang terbaca (bukan daftar bawahan kosong yang terlihat seperti "tidak punya bawahan").

### Di luar cakupan

Penegakan `wajib_bukti`; notifikasi atau kategori inbox baru; feed kalender; sumber KPI; perubahan tabel `tasks`.

### Data / bukti pendukung

Prod 2026-10-11 `task_management_db.tasks`: 427 tiket; status Done 289, Request 51, Todo 35, Archive 22, Ditolak 14, On Going 9, Testing 5, UpComing 2. 14 orang memegang 61 penugasan aktif (semuanya ber-`due_date`). Field `assign_to` berbentuk array (`["BIP-0135-03-25"]`), pembuat di `created_by`, waktu buat `createdAt` (camelCase) sedangkan `due_date`/`completed_at` snake_case. Koleksi space bernama `space` (tunggal), 15 dokumen.

### Prasyarat

#1 merged dan employee-service ter-deploy di lingkungan yang dituju.

---

## 3. [Mobile] To-do hari ini di Beranda dan tab Hari Ini (bagian 1/2)

- **Repo**: my-bharata (folder lokal `mybharata-app`, branch `dev`) · **Bentuk**: sub-issue induk #0 · **Issue**: (diisi saat dibuat)

**Pemutus:** @irfanarfianto
**PIC:** @

### Masalah

MyBharata tidak punya tempat mencatat pekerjaan harian pribadi. Menu Tugas hanya punya tab Diajukan, Ditugaskan, dan Tim (`lib/src/features/task/presentation/pages/task_page.dart:192-200`), dan tak ada tampilan tugas per hari.

### Keputusan

[[ADR - 0170 To-do Harian Pribadi di Task Management dengan Pantauan Atasan Efektif]] §2-§4, §7, §9. Layak `Siap Agent` sesudah ADR berstatus Diterima.
- Kartu "To-do hari ini" di Beranda tepat di bawah `AttendanceActivityCard` (`home_page.dart:262`), dengan tombol tambah.
- Tab **Hari Ini** paling depan di menu Tugas: to-do + tiket saya; tiket membuka detail tiket yang ada.

### Yang harus benar

- [ ] Menambah item cukup judul; tanggal rencana bawaan hari ini dan bisa diganti lewat pemilih tanggal. Tanpa field prioritas.
- [ ] Tab Hari Ini menampilkan baris to-do dan tiket dari endpoint #2, tiket ditandai berbeda dan mengetuknya membuka detail tiket.
- [ ] Baris to-do yang tertunda menampilkan label "tertunda N hari" dari `tertunda_hari` backend, bukan dihitung di aplikasi.
- [ ] Centang selesai, ubah tanggal, dan batalkan bekerja dengan umpan balik; batalkan meminta konfirmasi dan menyebut bahwa item tetap terlihat oleh atasan.
- [ ] Lampirkan bukti (foto/berkas) dari detail item, dan bukti yang ada bisa dipratinjau dan dilepas.
- [ ] Kartu Beranda menampilkan sampai 3 item teratas + jumlah total + "Lihat semua" ke tab Hari Ini; menyembunyikan diri saat endpoint membalas 404 (rute belum rilis), meniru `task_remote_datasource.dart:152-154`, dan ikut `refreshKey` tarik-menyegarkan.
- [ ] Loading memakai `ShimmerBox`, padding memakai `AppDimens`; lima keadaan layar (memuat, kosong, galat, berisi, sebagian) tertangani.
- [ ] Teks baru lewat l10n `app_id.arb` dan `app_en.arb`.

### Di luar cakupan

Tampilan atasan (#4); notifikasi; Web ERP.

### Data / bukti pendukung

Tidak perlu data prod tambahan.

### Prasyarat

#2 merged **dan ter-deploy** sebelum rilis aplikasi ini (deploy sesudah `bip-erp` sub-issue #2). Merge lebih dulu boleh; rilis store lebih dulu tidak.

---

## 4. [Mobile] Tampilan to-do bawahan untuk atasan efektif (bagian 2/2)

- **Repo**: my-bharata (folder lokal `mybharata-app`, branch `dev`) · **Bentuk**: sub-issue induk #0 · **Issue**: (diisi saat dibuat)

**Pemutus:** @irfanarfianto
**PIC:** @

### Masalah

Atasan tidak punya layar untuk melihat pekerjaan harian bawahan. Tab Tim yang ada mensyaratkan supervisor tiket atau role supervisor/admin (`task_page.dart:101-104`), syarat yang tidak dipenuhi semua atasan langsung.

### Keputusan

[[ADR - 0170 To-do Harian Pribadi di Task Management dengan Pantauan Atasan Efektif]] §5, §6, §9. Layak `Siap Agent` sesudah ADR berstatus Diterima.
- Tampilan muncul untuk siapa pun yang punya bawahan efektif (dari endpoint #2), tidak menumpang syarat tab Tim.
- Dibuka dengan ringkasan; rincian per orang dari ringkasan; atasan hanya membaca.

### Yang harus benar

- [ ] Pintu masuk tampilan bawahan hanya muncul bila daftar bawahan efektif tidak kosong; karyawan tanpa bawahan tidak melihatnya.
- [ ] Ringkasan per bawahan menampilkan jumlah to-do terbuka hari ini, tertunda ≥ 3 hari, dan dibatalkan 7 hari terakhir; tidak diurutkan sebagai peringkat berdasarkan angka tertunda (urutan nama).
- [ ] Mengetuk seorang bawahan membuka daftar hari ininya; tidak ada tombol ubah, selesai, batal, atau unggah.
- [ ] Baris tiket dari space terbatas tampil sebagai "1 tiket di space terbatas" tanpa judul, sesuai balasan backend.
- [ ] Galat memuat daftar bawahan tampil sebagai galat, bukan sebagai "tidak punya bawahan".
- [ ] `ShimmerBox`, `AppDimens`, l10n dua bahasa, lima keadaan layar.

### Di luar cakupan

Menegur atau membagi ulang dari dalam aplikasi; notifikasi ke atasan; KPI.

### Data / bukti pendukung

Prod 2026-10-11: bawahan per atasan langsung 22, 15, 12, 12, 11, 6, 4, 2; supervisor departemen fallback bisa memantau sekitar 32 orang (Manufaktur, 1 dari 33 ber-atasan langsung). Daftar harus nyaman untuk 30+ orang.

### Prasyarat

#3 merged. #2 ter-deploy.
