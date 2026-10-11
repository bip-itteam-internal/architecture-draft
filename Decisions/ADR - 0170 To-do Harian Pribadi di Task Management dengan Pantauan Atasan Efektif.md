# ADR - 0170 To-do Harian Pribadi di Task Management dengan Pantauan Atasan Efektif

## Untuk Manajemen

- **Yang berubah di layar**: karyawan mencatat pekerjaan hariannya di MyBharata (kartu "To-do hari ini" di Beranda dan tab **Hari Ini** di menu Tugas), digabung dengan tiket yang ditugaskan kepadanya sehingga tak ada yang diketik dua kali. Yang belum selesai terbawa ke hari berikutnya berlabel "tertunda N hari". Atasan melihat daftar bawahannya, dibuka dengan ringkasan siapa yang tertunda tiga hari atau lebih, untuk menegur, membantu, atau membagi ulang pekerjaan.
- **Siapa terdampak**: seluruh 181 karyawan aktif sebagai pengisi (2026-10-11). Pemantau: 8 atasan langsung tercatat, plus 11 supervisor departemen yang memantau 97 karyawan yang atasan langsungnya belum diisi HR.
- **Tidak dijanjikan**: belum masuk KPI atau penilaian kinerja (diputuskan sesudah ada data satu sampai dua bulan); belum ada di Web ERP; belum ada pengingat pagi; bukti bisa dilampirkan tetapi belum bisa diwajibkan; laporan harian Excel milik SOP tidak otomatis tergantikan; "tertunda" dihitung hari kalender sehingga akhir pekan dan libur ikut terhitung.
- **Besaran kerja**: besar, yaitu dua PR backend (dua service) dan dua PR aplikasi MyBharata, berurutan.

## Deskripsi

*Karyawan mencatat to-do pribadi hariannya di MyBharata, bergabung dengan tiket yang ditugaskan kepadanya. Item yang belum selesai terbawa otomatis dengan hitungan tertunda yang diturunkan dari tanggal rencana awal yang tak bisa diubah. Atasan efektif (atasan langsung, atau supervisor departemen bila atasan langsung kosong) dapat melihatnya. To-do disimpan di koleksi baru di Task Management Service, terpisah dari tiket, tanpa triase dan tanpa SLA. Pondasi lampiran bukti ikut dibangun sejak tahap pertama, tetapi belum ditegakkan.*

- **Status**: 🟡 **Diusulkan**, 2026-10-11, kode belum ada. Analisa: [[ANALISA - To-do Harian Pribadi]]
- **Path di repo**: `bip-erp/services/employee/atasan_efektif.go` (baru) · `bip-erp/services/task-management/todo_*.go` (baru) · `bip-erp/docker-compose.yml` (env `EMPLOYEE_MODULE_URL` untuk task-management) · `mybharata-app/lib/src/features/task/` (tab Hari Ini, kartu Beranda, tampilan bawahan; baru)
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

Angka terakhir membantah dugaan bahwa orang sudah memakai Task Management sebagai to-do pribadi.

Pemeriksaan negatif (`git grep`, termasuk berkas biner) di `bip-erp` `origin/main`, `mybharata-app` `origin/dev`, dan vault: tidak ada entitas to-do, log kerja harian, mekanisme pindah ke besok, atau hitungan tertunda.

Dok yang menjadi dasar: [[Microservices - Task Management Service]] (⚠️ Implemented) dan [[HRIS - Organization Structure]] (⚠️ Implemented). Keduanya mencerminkan kode yang hidup, bukan rencana.

## Decision

### 1. To-do adalah entitas baru di Task Management Service, bukan tiket

Koleksi baru di `task_management_db`, terpisah dari `tasks`. **Tidak memakai tabel tiket**, karena setiap tiket lahir sebagai `Request` dengan SLA respons 24 jam dan memberi notifikasi ke supervisor space (`services/task-management/task_handlers.go:126-160`). To-do pribadi lewat jalur itu akan membanjiri antrean triase. To-do tidak punya prioritas, triase, persetujuan, maupun SLA.

Tempatnya Task Management, bukan service baru: daftar "hari ini" menggabungkan to-do dan tiket, dan service ini sudah memiliki tiketnya. Service baru menambah container dan rute gateway untuk pemakai pertama (ditolak, lihat Alternatif).

### 2. Isi item dan siapa boleh apa

- Field inti: pemilik (`employee_id`), judul, catatan opsional, **`tanggal_rencana_awal` (tak bisa diubah sesudah dibuat)**, `tanggal_rencana` (bisa diubah pemilik), status `terbuka | selesai | dibatalkan`, `selesai_at`, `dibatalkan_at`.
- **Hanya pemilik** yang membuat, mengubah, mencentang selesai, mengubah tanggal rencana, dan membatalkan. Atasan **hanya membaca**.
- **Batal tidak menghapus.** Item dibatalkan tetap tersimpan dan tetap terlihat oleh atasan, supaya item yang menunggak tidak bisa dihilangkan diam-diam. Tidak ada rute hapus.

### 3. "Tertunda" dihitung saat dibaca, tanpa job pemindah

Item terbuka yang `tanggal_rencana`-nya sudah lewat **tampil di daftar hari ini** dengan `tertunda_hari = hari ini (WIB) − tanggal_rencana_awal`, dalam **hari kalender**. Tidak ada job malam yang menulis ulang tanggal atau menaikkan counter. Alasannya: scheduler task-management berupa ticker per jam yang tidak sadar zona waktu (`sla_scheduler.go:15-30`), sehingga tik yang terlewat atau berganda menghasilkan counter salah tanpa satu pun galat. Nilai yang diturunkan dari dua tanggal tidak bisa melenceng. Riwayat "item ini ada di daftar hari apa saja" bisa direkonstruksi dari `tanggal_rencana_awal` sampai `selesai_at`/`dibatalkan_at`.

Memindahkan `tanggal_rencana` ke depan tidak mengubah `tanggal_rencana_awal`, jadi menjadwal ulang tidak menghapus riwayat keterlambatan. Batas hari memakai WIB, sama dengan `feedWIB` di `calendar_feed.go:22-28`.

### 4. Daftar "hari ini" = to-do pribadi + tiket saya

Satu endpoint di task-management mengembalikan dua jenis baris yang dibedakan eksplisit (`jenis: todo | tiket`): to-do terbuka dengan `tanggal_rencana` ≤ hari ini ditambah to-do yang selesai hari ini, serta tiket yang `assign_to` memuat pemanggil, belum selesai menurut aturan `calendar_feed.go:90-104`, dan `due_date` ≤ akhir hari ini. Tiket tetap diubah di halaman tiket; daftar ini hanya membaca dan menautkannya.

### 5. Atasan efektif, dan resolusinya tidak disalin

**Atasan efektif** seseorang = `supervisor_id` bila sah, bila kosong supervisor departemennya, persis aturan `atasanPengingat`. Supervisor departemen yang rantainya menunjuk dirinya sendiri tidak punya atasan efektif, dan to-do-nya hanya terlihat oleh dirinya.

Employee-service membuka **endpoint internal** yang memanggil resolver itu (atasan efektif seseorang, dan daftar bawahan efektif seseorang). Task-management **memanggilnya**, tidak menulis ulang resolusinya, walau task-management punya koneksi baca ke `employee_db`. Menyalin rantai berlapis itu melahirkan sumber kebenaran kedua (team-memory "Jangan menulis ulang resolusi milik modul lain"). Endpoint internal wajib memeriksa identitas pemanggil (kunci layanan), karena gateway tetap meneruskan `/internal/` dari internet.

Isolasi tenant mengikuti `validasiAtasan` (`subordinate.go`): atasan dan bawahan satu perusahaan.

### 6. Tampilan atasan dimulai dari ringkasan

Layar atasan dibuka dengan ringkasan per bawahan: jumlah to-do terbuka hari ini, jumlah yang **tertunda ≥ 3 hari**, dan jumlah yang dibatalkan dalam 7 hari terakhir. Rincian per orang dibuka dari ringkasan. Atasan dengan 22 bawahan, atau supervisor fallback dengan sekitar 32 orang, tidak akan membuka daftar satu per satu.

Tiket bawahan yang berasal dari space `Visibility: restricted` yang tidak bisa diakses atasan itu ditampilkan sebagai "1 tiket di space terbatas" tanpa judul. Pantauan atasan tidak boleh menjadi jalan pintas membaca tiket yang RBAC tiket tidak buka.

Ringkasan ini **bukan peringkat antar-orang**, sejalan dengan [[ADR - 0059 Penugasan Langsung Menggantikan Antrian Bersama]] baris 59: angka yang bisa dimainkan tidak dijadikan kolom pembanding.

### 7. Bukti: pondasi dibangun sekarang, penegakan menyusul

- Sejak tahap 1 ada **rute unggah bukti** per item (memakai pola file-service yang sama dengan lampiran tiket, prefix tersendiri) beserta rute pratinjau dan lepas bukti. Bukti opsional.
- Field `wajib_bukti` (bool, bawaan `false`) disimpan sejak awal. Di tahap 1 **tidak ada penulis selain bawaan** dan tidak ditegakkan.
- Tahap berikutnya memutuskan: siapa boleh mewajibkan (atasan per item, atau per posisi), dan apakah item ber-`wajib_bukti` ditolak saat diselesaikan tanpa bukti.

Pondasi wajib menyertakan **rute pengisinya**, bukan field saja. Preseden: metrik `reporting` modul Engagement selalu nol karena field lampirannya ada tetapi rute pengisinya tidak pernah dibuat ([[Marketing - Engagement Team (Modul)]]).

### 8. Tidak masuk KPI di tahap 1

To-do ditulis sendiri, jadi bila langsung dinilai orang akan menulis item yang mudah diselesaikan. Sumber KPI (`DaftarkanSumberBermetrik`, `services/employee/kpi_sumber.go:186`; draft yang diverifikasi supervisor menurut [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]]) diputuskan dengan ADR terpisah sesudah ada data satu sampai dua bulan.

### 9. Platform

Tahap 1 hanya MyBharata: kartu "To-do hari ini" di Beranda (di bawah kartu presensi) dengan tombol tambah, dan tab **Hari Ini** paling depan di menu Tugas. Tampilan bawahan muncul untuk siapa pun yang **punya bawahan efektif**, tidak menumpang syarat tab Tim yang ada (`task_page.dart:101-104`, yang mensyaratkan supervisor tiket atau role supervisor/admin dan tidak dipenuhi semua atasan langsung).

### Asumsi eksplisit

1. Pencatatan yang berjalan sekarang belum terstruktur. Yang terbukti hanya kewajiban laporan harian di SOP.
2. Hari kalender, bukan hari kerja, karena roster shift bervariasi per orang.
3. Ambang ringkasan atasan **3 hari** adalah titik awal, direvisi sesudah ada data.
4. Tanpa pilot: rilis untuk semua karyawan. Pilot (misalnya marketing, yang data atasannya paling lengkap) bisa diputuskan saat adopsi tanpa mengubah keputusan ini.
5. HR bersedia melengkapi `supervisor_id`. Sampai itu terjadi, beban pantauan jatuh ke supervisor departemen lewat fallback.

## Consequences

- **Deploy**: task-management butuh env baru `EMPLOYEE_MODULE_URL` (hari ini ia hanya membaca `employee_db` langsung). Naik dengan `docker compose up -d --force-recreate`, bukan `restart`. Isi `.env` dev sebelum merge. Urutan: employee-service → task-management → MyBharata. Tidak ada kategori inbox baru.
- **Beban supervisor fallback**: supervisor Manufaktur praktis memantau sekitar 32 orang. Bila itu terlalu berat, obatnya melengkapi `supervisor_id`, bukan mengubah aturan ini.
- **Data pribadi**: isi to-do bisa memuat hal pribadi. Atasan efektif melihatnya. Ini keputusan sadar (pilihan user 2026-10-11) dan perlu disampaikan ke karyawan saat rilis.
- **Kalender**: to-do **tidak** masuk feed kalender di tahap 1. Bila kelak masuk, hanya sebagai milik pemiliknya: prinsip tiga lapis melarang to-do bawahan tampil di kalender atasan ([[Microservices - Calendar Service]]).
- **Laporan harian SOP**: fitur ini dapat menggantikan laporan Excel, tetapi tidak otomatis. Bila pemilik SOP tetap meminta Excel, karyawan mengisi dua kali dan fitur ditinggalkan.

### Alternatif yang ditolak

- **To-do sebagai tiket di "space pribadi"**: ditolak, lihat §1.
- **Job per jam yang memindahkan item dan menaikkan counter**: ditolak, lihat §3.
- **Service to-do tersendiri**: menambah container, compose, dan rute gateway, sementara tetap harus memanggil task-management untuk tiket. Satu pemakai belum membenarkan batas service baru.
- **Atasan hanya dari `supervisor_id`**: ditolak, 54% karyawan tidak akan terlihat siapa pun.
- **Langsung jadi sumber KPI**: ditunda, lihat §8.

## Dokumen Terkait

- [[HRIS - To-do Harian Pribadi (Modul)]] · [[ANALISA - To-do Harian Pribadi]]
- [[Microservices - Task Management Service]] · [[HRIS - Organization Structure]] · [[APP - MyBharata]]
- [[ADR - 0059 Penugasan Langsung Menggantikan Antrian Bersama]] · [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]]
