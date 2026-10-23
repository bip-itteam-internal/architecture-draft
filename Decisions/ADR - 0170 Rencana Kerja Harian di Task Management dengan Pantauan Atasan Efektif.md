# ADR - 0170 Rencana Kerja Harian di Task Management dengan Pantauan Atasan Efektif

## Untuk Manajemen

- **Yang berubah di layar**: karyawan mencatat pekerjaan hariannya lewat tab baru **Hari Ini** di menu Tugas, baik di MyBharata maupun Web ERP (Task Management › Daftar Tugas); tidak tampil di Beranda, digabung dengan tiket yang ditugaskan kepadanya sehingga tak ada yang diketik dua kali. Yang belum selesai terbawa ke hari berikutnya berlabel "tertunda N hari". Atasan melihat daftar bawahannya, dibuka dengan ringkasan siapa yang tertunda tiga hari atau lebih, untuk menegur, membantu, atau membagi ulang pekerjaan.
- **Siapa terdampak**: seluruh 181 karyawan aktif sebagai pengisi (2026-10-11). Pemantau: 8 atasan langsung tercatat, plus 11 supervisor departemen yang memantau 97 karyawan yang atasan langsungnya belum diisi HR.
- **Tidak dijanjikan**: belum masuk KPI atau penilaian kinerja (diputuskan sesudah ada data satu sampai dua bulan); belum ada pengingat pagi; bukti bisa dilampirkan tetapi belum bisa diwajibkan; laporan harian Excel milik SOP tidak otomatis tergantikan; "tertunda" dihitung hari kalender sehingga akhir pekan dan libur ikut terhitung.
- **Besaran kerja**: besar, yaitu dua PR backend (dua service), dua PR aplikasi MyBharata, dan dua PR Web ERP; backend lebih dulu, MyBharata dan Web bisa berjalan paralel.

## Deskripsi

*Karyawan mencatat rencana kerja hariannya di MyBharata, bergabung dengan tiket yang ditugaskan kepadanya. Item yang belum selesai terbawa otomatis dengan hitungan tertunda yang diturunkan dari tanggal rencana awal yang tak bisa diubah. Atasan efektif (atasan langsung, atau supervisor departemen bila atasan langsung kosong) dapat melihatnya. Rencana kerja disimpan di koleksi baru di Task Management Service, terpisah dari tiket, tanpa triase dan tanpa SLA. Pondasi lampiran bukti ikut dibangun sejak tahap pertama, tetapi belum ditegakkan.*

- **Status**: 🟢 **Diterima**, 2026-10-12, oleh irfanarfianto (Pemutus; perintah "kerjakan sekarang"). Kode belum ada. Analisa: [[ANALISA - Rencana Kerja Harian]]
- **Path di repo**: `bip-erp/services/employee/atasan_efektif.go` (baru) · `bip-erp/services/task-management/rencana_kerja_*.go` (baru) · `bip-erp/docker-compose.yml` (env `EMPLOYEE_MODULE_URL` untuk task-management) · `mybharata-app/lib/src/features/task/` (tab Hari Ini, tampilan bawahan; baru) · `erp-frontend/src/features/task-management/components/my-tasks-view.tsx` (tab baru) · `erp-frontend/src/features/task-management/components/rencana-kerja/` (baru)
- **Tanggal**: 2026-10-11

## Context

Kebutuhan datang sebagai solusi ("to-do list pribadi dengan tracking harian"). Wawancara memisahkan kebutuhannya: **atasan baru tahu pekerjaan bawahan macet setelah terlambat**, karena pekerjaan harian yang tidak berbentuk tiket tidak tercatat di sistem. Keputusan yang hendak diambil atasan: menegur atau membantu yang berulang kali tertunda, membagi ulang pekerjaan tim, dan kelak menilai kinerja.

Pencatatan hari ini tidak terstruktur. SOP banyak posisi sudah mewajibkan laporan harian (`WH - SOP Posisi Leader Warehouse Packing` baris 294, `Manufacture - SOP Posisi PPIC` baris 816, `Marketing - SOP Posisi Host Live Kyura` baris 247 yang memakai Excel, Google Sheet, atau formulir), tetapi hasilnya tidak terkumpul di sistem. Metrik KPI "kelengkapan laporan harian" untuk Buzzer BHS dan Kyura masih dinilai manual ([[HRIS - Matriks KPI per Departemen]] baris 281 dan 1244). `BUSINESS_LOGIC_IMPLEMENTATION.md` (Peraturan Perusahaan) tidak mengatur laporan kerja harian maupun sanksi atas tugas tertunda, jadi keputusan ini tidak menyentuh aturan uang atau sanksi.

Yang sudah ada dan dipakai ulang:

1. **Tiket yang ditugaskan ke saya** beserta aturan "belum selesai" yang bersandar pada `completed_at` dan `is_archived`, bukan nama status (`services/task-management/calendar_feed.go:90-104`, filter `:140-146`).
2. **Atasan langsung sebagai cakupan tampilan.** `work_data.supervisor_id` sengaja dipakai untuk "siapa melihat siapa", bukan wewenang persetujuan (`services/employee/subordinate.go:11-20`; [[HRIS - Organization Structure]]). Endpoint `/me/subordinates` sudah ada (`services/employee/main.go:3306`).
3. **Resolver atasan dengan fallback** `atasanPengingat` (`services/employee/contract_pengingat.go:183-199`): `supervisor_id` dulu, bila kosong jatuh ke rantai penyetuju cuti yang sudah menangani General Affair tanpa supervisor sendiri. Rantai yang menunjuk orang itu sendiri dianggap tanpa atasan.
4. **Pola lampiran lewat file-service** (`POST /tasks/:id/attachments`, struct `FileAttachment`, `services/task-management/routes.go:71-75`, `models_task.go:68`).

Yang diukur di prod (2026-10-11, baca saja):

| Ukuran | Nilai |
|---|---|
| Karyawan aktif / ber-`work_data` | 183 / 181 |
| Ber-`supervisor_id` | **84 (46%)**; Manufaktur 1 dari 33, Finance 0 dari 16, Percetakan 0 dari 13, Beautyhacks 40 dari 45 |
| Atasan langsung berbeda / bawahan per atasan | 8 / 22, 15, 12, 12, 11, 6, 4, 2 |
| `is_supervisor` | 11 |
| Tiket total / pemegang tiket aktif | 427 / 14 orang (61 penugasan aktif) |
| Tiket dibuat untuk diri sendiri | 155, **seluruhnya Tech Development** (12 orang) sebagai backlog pengembangan; **0 dalam 30 hari terakhir** |

Angka terakhir membantah dugaan bahwa orang sudah memakai Task Management sebagai rencana kerja.

Pemeriksaan negatif (`git grep`, termasuk berkas biner) di `bip-erp` `origin/main`, `mybharata-app` `origin/dev`, dan vault: tidak ada entitas rencana kerja, log kerja harian, mekanisme pindah ke besok, atau hitungan tertunda.

Dok yang menjadi dasar: [[Microservices - Task Management Service]] (⚠️ Implemented) dan [[HRIS - Organization Structure]] (⚠️ Implemented). Keduanya mencerminkan kode yang hidup, bukan rencana.

## Decision

### 1. Rencana kerja adalah entitas baru di Task Management Service, bukan tiket

Koleksi baru di `task_management_db`, terpisah dari `tasks`. **Tidak memakai tabel tiket**, karena setiap tiket lahir sebagai `Request` dengan SLA respons 24 jam dan memberi notifikasi ke supervisor space (`services/task-management/task_handlers.go:126-160`). Rencana kerja lewat jalur itu akan membanjiri antrean triase. Rencana kerja tidak punya prioritas, triase, persetujuan, maupun SLA.

Tempatnya Task Management, bukan service baru: daftar "hari ini" menggabungkan rencana kerja dan tiket, dan service ini sudah memiliki tiketnya. Service baru menambah container dan rute gateway untuk pemakai pertama (ditolak, lihat Alternatif).

### 2. Isi item dan siapa boleh apa

- Field inti: pemilik (`employee_id`), judul, catatan opsional, **`tanggal_rencana_awal` (tak bisa diubah sesudah dibuat)**, `tanggal_rencana` (bisa diubah pemilik), status `terbuka | selesai | dibatalkan`, `selesai_at`, `dibatalkan_at`.
- **Hanya pemilik** yang membuat, mengubah, mencentang selesai, mengubah tanggal rencana, dan membatalkan. Atasan **hanya membaca**.
- **Batal tidak menghapus.** Item dibatalkan tetap tersimpan dan tetap terlihat oleh atasan, supaya item yang menunggak tidak bisa dihilangkan diam-diam. Tidak ada rute hapus.

### 3. "Tertunda" dihitung saat dibaca, tanpa job pemindah

Item terbuka yang `tanggal_rencana`-nya sudah lewat **tampil di daftar hari ini** dengan `tertunda_hari = hari ini (WIB) − tanggal_rencana_awal`, dalam **hari kalender**. Tidak ada job malam yang menulis ulang tanggal atau menaikkan counter. Alasannya: scheduler task-management berupa ticker per jam yang tidak sadar zona waktu (`sla_scheduler.go:15-30`), sehingga tik yang terlewat atau berganda menghasilkan counter salah tanpa satu pun galat. Nilai yang diturunkan dari dua tanggal tidak bisa melenceng. Riwayat "item ini ada di daftar hari apa saja" bisa direkonstruksi dari `tanggal_rencana_awal` sampai `selesai_at`/`dibatalkan_at`.

Memindahkan `tanggal_rencana` ke depan tidak mengubah `tanggal_rencana_awal`, jadi menjadwal ulang tidak menghapus riwayat keterlambatan. Batas hari memakai WIB, sama dengan `feedWIB` di `calendar_feed.go:22-28`.

### 4. Daftar "hari ini" = rencana kerja + tiket saya

Satu endpoint di task-management mengembalikan dua jenis baris yang dibedakan eksplisit (`jenis: rencana | tiket`): rencana kerja terbuka dengan `tanggal_rencana` ≤ hari ini ditambah rencana kerja yang selesai hari ini, serta tiket yang `assign_to` memuat pemanggil, belum selesai menurut aturan `calendar_feed.go:90-104`, dan `due_date` ≤ akhir hari ini, ditambah tiket saya yang `completed_at`-nya hari ini (bagian "selesai hari ini"). Tiket `Request` otomatis tidak ikut karena `due_date` baru diisi saat disetujui.

**Baris tiket tidak punya ceklis** (keputusan user 2026-10-11). Status tiket ditentukan stage space masing-masing (bawaan `Request → Todo → On Going → Testing → Done`, tetapi space bisa menambah stage, dan beberapa space memakai `Archive`), dan `Testing → Done` menuntut tinjauan supervisor atau admin space. Satu centang tidak bisa dipetakan ke satu status tanpa melompati tinjauan atau menyalin urutan stage. Karena itu baris tiket menampilkan **chip berisi nama status aslinya apa adanya** (Testing diberi keterangan "menunggu tinjauan"), tenggatnya (dengan tanda "lewat tenggat" bila `due_date` sudah lewat), dan mengetuknya membuka detail tiket. Status diubah di sana lewat alur yang sudah ada. Daftar ini hanya membaca tiket, tidak pernah menulisnya.

Hitungan "tertunda" (§3) dan ringkasan atasan (§6) **hanya untuk rencana kerja**. Keterlambatan tiket sudah punya ukurannya sendiri (SLA, `/report/sla-breaches`), dan menjumlahkan keduanya menghitung satu pekerjaan dengan dua aturan berbeda.

### 5. Atasan efektif, dan resolusinya tidak disalin

**Atasan efektif** seseorang = `supervisor_id` bila sah, bila kosong supervisor departemennya, persis aturan `atasanPengingat`. Supervisor departemen yang rantainya menunjuk dirinya sendiri tidak punya atasan efektif, dan rencana kerjanya hanya terlihat oleh dirinya.

Employee-service membuka **endpoint internal** yang memanggil resolver itu (atasan efektif seseorang, dan daftar bawahan efektif seseorang). Task-management **memanggilnya**, tidak menulis ulang resolusinya, walau task-management punya koneksi baca ke `employee_db`. Menyalin rantai berlapis itu melahirkan sumber kebenaran kedua (team-memory "Jangan menulis ulang resolusi milik modul lain"). Endpoint internal wajib memeriksa identitas pemanggil (kunci layanan), karena gateway tetap meneruskan `/internal/` dari internet.

Isolasi tenant mengikuti `validasiAtasan` (`subordinate.go`): atasan dan bawahan satu perusahaan.

### 6. Tampilan atasan dimulai dari ringkasan

Layar atasan dibuka dengan ringkasan per bawahan: jumlah rencana kerja terbuka hari ini, jumlah yang **tertunda ≥ 3 hari**, dan jumlah yang dibatalkan dalam 7 hari terakhir. Rincian per orang dibuka dari ringkasan. Atasan dengan 22 bawahan, atau supervisor fallback dengan sekitar 32 orang, tidak akan membuka daftar satu per satu.

Tiket bawahan yang berasal dari space `Visibility: restricted` yang tidak bisa diakses atasan itu ditampilkan sebagai "1 tiket di space terbatas" tanpa judul. Pantauan atasan tidak boleh menjadi jalan pintas membaca tiket yang RBAC tiket tidak buka.

Ringkasan ini **bukan peringkat antar-orang**, sejalan dengan [[ADR - 0059 Penugasan Langsung Menggantikan Antrian Bersama]] baris 59: angka yang bisa dimainkan tidak dijadikan kolom pembanding.

### 7. Bukti: pondasi dibangun sekarang, penegakan menyusul

- Sejak tahap 1 ada **rute unggah bukti** per item (memakai pola file-service yang sama dengan lampiran tiket, prefix tersendiri) beserta rute pratinjau dan lepas bukti. Bukti opsional.
- Field `wajib_bukti` (bool, bawaan `false`) disimpan sejak awal. Di tahap 1 **tidak ada penulis selain bawaan** dan tidak ditegakkan.
- Tahap berikutnya memutuskan: siapa boleh mewajibkan (atasan per item, atau per posisi), dan apakah item ber-`wajib_bukti` ditolak saat diselesaikan tanpa bukti.

Pondasi wajib menyertakan **rute pengisinya**, bukan field saja. Preseden: metrik `reporting` modul Engagement selalu nol karena field lampirannya ada tetapi rute pengisinya tidak pernah dibuat ([[Marketing - Engagement Team (Modul)]]).

### 8. Tidak masuk KPI di tahap 1

Rencana kerja ditulis sendiri, jadi bila langsung dinilai orang akan menulis item yang mudah diselesaikan. Sumber KPI (`DaftarkanSumberBermetrik`, `services/employee/kpi_sumber.go:186`; draft yang diverifikasi supervisor menurut [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]]) diputuskan dengan ADR terpisah sesudah ada data satu sampai dua bulan.

### 9. Platform

Tahap 1 di **MyBharata dan Web ERP**, dan di keduanya **hanya di dalam menu Tugas**: tab **Hari Ini** paling depan, dengan tombol tambah. Di Web ERP tempatnya halaman Task Management › Daftar Tugas (`/task-management/my-tickets`), sebagai tab di `CustomTabs` yang sudah ada (`erp-frontend` `my-tasks-view.tsx:321`), sehingga bukan menu sidebar baru dan tidak menuntut entri panduan. Detail rencana dan rincian bawahan dibuka dalam `Sheet` berangka tiga; tabel atasan memakai `MainTable`; chip tiket memakai `StatusBadge` yang sudah dipakai halaman itu (`task-ui.tsx:62`, termasuk warna stage space). Tab **Rencana Tim** untuk atasan efektif terpisah dari tab **Tugas Tim** yang ada, karena gerbang tab itu (supervisor/admin atau pemegang space, `my-tasks-view.tsx:54-64`) tidak sama dengan "punya bawahan efektif". State tab pindah ke query string (`?tab=`) karena halaman itu kini punya lima tab; hari ini tab hanya `useState` lokal (`my-tasks-view.tsx:66`). Web ERP ditambahkan atas permintaan user 2026-10-11, setelah keputusan awal "MyBharata dulu". Sekalian, label tab `created` di Web diganti dari "Tugas Saya" / "My Tasks" jadi **"Diajukan" / "Submitted"**, sama dengan MyBharata (`taskScopeMine`); kunci i18n `taskManagement.tabCreated` tidak berubah (keputusan user 2026-10-12). **Tidak ada kartu atau ringkasan di Beranda** (keputusan user 2026-10-11): rencana kerja baru terlihat saat orang membuka halaman manajemen tugas. Konsekuensinya diterima sadar: tanpa pengingat di Beranda, orang yang jarang membuka menu Tugas bisa lupa mengisi. Tampilan bawahan muncul untuk siapa pun yang **punya bawahan efektif**, tidak menumpang syarat tab Tim yang ada (`task_page.dart:101-104`, yang mensyaratkan supervisor tiket atau role supervisor/admin dan tidak dipenuhi semua atasan langsung).

### 10. Nama: "Rencana Kerja", bukan "To-do"

Fitur ini bernama **Rencana Kerja** di layar ("Rencana kerja hari ini"), dan di kode `rencana_kerja` (koleksi, berkas, rute, kunci l10n). Kata **"to-do" / "todo" dilarang** untuk fitur ini, karena di modul yang sama `Todo` sudah berarti **status tiket** (`Request → Todo → On Going → Testing → Done`, 35 tiket berstatus itu di prod 2026-10-11) dan `todo_approval` adalah field tiket (`mybharata-app` `task_model.dart`, `approval_rules.dart`). Dua arti untuk satu kata di menu yang sama membuat pemakai mengira daftar ini berisi tiket berstatus Todo, dan membuat pencarian kode ambigu. Status tiket tidak diganti namanya: nilainya sudah tersimpan di data produksi. Diputuskan user 2026-10-11.

### Asumsi eksplisit

1. Pencatatan yang berjalan sekarang belum terstruktur. Yang terbukti hanya kewajiban laporan harian di SOP.
2. Hari kalender, bukan hari kerja, karena roster shift bervariasi per orang.
3. Ambang ringkasan atasan **3 hari** adalah titik awal, direvisi sesudah ada data.
4. Tanpa pilot: rilis untuk semua karyawan. Pilot (misalnya marketing, yang data atasannya paling lengkap) bisa diputuskan saat adopsi tanpa mengubah keputusan ini.
5. HR bersedia melengkapi `supervisor_id`. Sampai itu terjadi, beban pantauan jatuh ke supervisor departemen lewat fallback.

## Consequences

- **Deploy**: task-management butuh env baru `EMPLOYEE_MODULE_URL` (hari ini ia hanya membaca `employee_db` langsung). Naik dengan `docker compose up -d --force-recreate`, bukan `restart`. Isi `.env` dev sebelum merge. Urutan: employee-service → task-management → MyBharata. Tidak ada kategori inbox baru.
- **Beban supervisor fallback**: supervisor Manufaktur praktis memantau sekitar 32 orang. Bila itu terlalu berat, obatnya melengkapi `supervisor_id`, bukan mengubah aturan ini.
- **Data pribadi**: isi rencana kerja bisa memuat hal pribadi. Atasan efektif melihatnya. Ini keputusan sadar (pilihan user 2026-10-11) dan perlu disampaikan ke karyawan saat rilis.
- **Kalender**: rencana kerja **tidak** masuk feed kalender di tahap 1. Bila kelak masuk, hanya sebagai milik pemiliknya: prinsip tiga lapis melarang rencana kerja bawahan tampil di kalender atasan ([[Microservices - Calendar Service]]).
- **Laporan harian SOP**: fitur ini dapat menggantikan laporan Excel, tetapi tidak otomatis. Bila pemilik SOP tetap meminta Excel, karyawan mengisi dua kali dan fitur ditinggalkan.

### Alternatif yang ditolak

- **Rencana kerja sebagai tiket di "space pribadi"**: ditolak, lihat §1.
- **Job per jam yang memindahkan item dan menaikkan counter**: ditolak, lihat §3.
- **Service rencana kerja tersendiri**: menambah container, compose, dan rute gateway, sementara tetap harus memanggil task-management untuk tiket. Satu pemakai belum membenarkan batas service baru.
- **Atasan hanya dari `supervisor_id`**: ditolak, 54% karyawan tidak akan terlihat siapa pun.
- **Langsung jadi sumber KPI**: ditunda, lihat §8.

## Dokumen Terkait

- [[HRIS - Rencana Kerja Harian (Modul)]] · [[ANALISA - Rencana Kerja Harian]]
- [[Microservices - Task Management Service]] · [[HRIS - Organization Structure]] · [[APP - MyBharata]]
- [[ADR - 0059 Penugasan Langsung Menggantikan Antrian Bersama]] · [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]]
