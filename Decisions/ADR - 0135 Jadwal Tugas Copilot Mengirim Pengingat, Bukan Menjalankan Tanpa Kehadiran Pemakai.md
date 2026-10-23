# ADR - 0135 Jadwal Tugas Copilot Mengirim Pengingat, Bukan Menjalankan Tanpa Kehadiran Pemakai

> **Status**: 🟡 **Diusulkan**, 2026-09-28. ~~Kode belum ada.~~ **Kodenya sudah di `main`** (diukur 2026-10-08: backend bip-erp #2382 merged 2026-09-30 dan #2788 merged 2026-10-08; layar erp-frontend #2179 merged 2026-10-08), lihat § Catatan implementasi. Status keputusannya sendiri belum diubah siapa pun yang berwenang. Disetujui pemilik proposal lewat `/analisa-kebutuhan`. Dikerjakan **sesudah** fondasi [[ADR - 0132 Asisten AI Tanya-Jawab Lintas Modul, Lapisan Data Bisnis per Service Bukan Terpusat]] (klien AI, service, gate akses, minimal satu modul percontohan) terbukti jalan — keputusan eksplisit, bukan ditunda diam-diam.
>
> **Issue GitHub**: [bip-erp#2355](https://github.com/bip-itteam-internal/bip-erp/issues/2355) (Project #15, dibuat 2026-09-29 dari verifikasi kode + data prod).

%% Status ditulis di blockquote atas, alasan sama dengan ADR 0120/0127/0132:
## Untuk Manajemen mendorong Deskripsi melewati baris ke-15 sehingga status tak terbaca VAULT-INDEX.json. %%

## Untuk Manajemen

**Apa yang berubah di layar.** Di menu Copilot akan ada bagian "Jadwal Tugas". Orang yang boleh
memakai Copilot bisa menyimpan satu pertanyaan atau template laporan (misalnya "Laporan Rapat
Mingguan") beserta jadwalnya — harian, mingguan, atau bulanan pada jam tertentu. Saat jadwalnya
tiba, orang itu menerima notifikasi berisi tautan; sekali klik, Copilot terbuka dengan pertanyaan
yang sudah terisi dan langsung menjawab.

**Siapa yang terdampak.** Sama dengan pemakai Copilot: Supervisor, Direktur, dan tim IT.

**Apa yang TIDAK dijanjikan.**
- Copilot **tidak** menjalankan pertanyaan sendiri saat orangnya tidak ada. Laporan tidak
  "sudah jadi" menunggu di kotak masuk; orangnya tetap mengklik sekali untuk menjalankannya.
- Tidak ada ringkasan otomatis "ada yang penting / tidak ada yang penting" di notifikasinya,
  karena itu menuntut pertanyaannya dijalankan lebih dulu.
- Tidak ada kanal WhatsApp/Telegram; notifikasi lewat kotak masuk ERP dan notifikasi push yang
  sudah ada.
- Tidak bisa dipakai sebelum Copilot sendiri bisa menjawab pertanyaan.

**Perkiraan besaran kerja.** Kecil-menengah, karena hampir semua bahannya sudah ada: penjadwal,
notifikasi, dan layar Copilot. Yang baru hanya penyimpanan jadwal, satu jenis notifikasi, dan
layar kelola jadwal. Jauh lebih kecil dari alternatif "jalan otomatis penuh", yang menuntut
mekanisme keamanan baru di jantung sistem login.

## Deskripsi

*Jadwal Tugas menyimpan instruksi atau template Copilot beserta jadwalnya, dan saat jatuh tempo
hanya mengirim PENGINGAT berisi tautan yang sudah terisi instruksinya. Pertanyaan baru dijalankan
ketika pemakainya membuka tautan itu, sehingga seluruh panggilan tetap memakai JWT hidup miliknya
persis seperti Tanya Jawab biasa. Tidak ada eksekusi tanpa kehadiran pemakai, dan karena itu tidak
ada mekanisme identitas baru.*

- **Path di repo**: `bip-erp/services/assistant/` (penjadwal + koleksi jadwal; kini `jadwal_rute.go`,
  `pengingat.go`, `internal/jadwal/`);
  `bip-erp/shared-library/models/notification/models.go` (kategori inbox `copilot-jadwal`);
  ~~`erp-frontend/src/features/assistant/`~~ `erp-frontend/src/features/copilot/` (layar Jadwal Tugas +
  penerima tautan; folder `features/assistant` tidak ada di `origin/main`)
- **Tanggal**: 2026-09-28

## Context

**Kebutuhan sebenarnya, bukan solusi yang diusulkan.** Usulan awalnya PRD "Scheduled Tasks" gaya
claude.ai: tugas dijalankan agent otomatis sesuai jadwal, dengan mode izin, pilihan model, konteks
project, dan notifikasi cerdas. Kebutuhan di baliknya lebih sempit: orang **mengulang pertanyaan
yang sama** tiap hari/minggu/bulan, **lupa** melakukannya, dan tidak ada jejak apa yang sudah
ditanyakan. Ketiganya bisa dijawab tanpa agent berjalan sendiri.

**Yang dibuang dari PRD asli, dan alasannya.**
- *Mode izin (Manual / Auto / Skip all approvals)*: seluruh konsepnya soal menyetujui AKSI agent.
  Asisten ini tidak pernah beraksi — murni baca
  ([[ADR - 0132 Asisten AI Tanya-Jawab Lintas Modul, Lapisan Data Bisnis per Service Bukan Terpusat]]
  § Consequences, sejalan
  [[ADR - 0058 Kapabilitas AI Digerbang Kelayakan Data, Bukan Kelayakan Teknologi]] §5).
- *Pilihan model*: ADR-0132 §2a mematok id model literal `cc/claude-*`.
- *Project (berkas + instruksi konteks)*: konsep ini tidak ada di ERP; template Copilot sudah jadi
  titik awal yang terstruktur.
- *WhatsApp/Telegram*: tidak ada infrastrukturnya.
- *Skema Postgres (`SELECT … FOR UPDATE SKIP LOCKED`)*: stack-nya MongoDB.

**Masalah inti: identitas saat jadwal jatuh tempo.** ADR-0132 mewarisi hak akses lewat JWT HIDUP
milik penanya, yang diisi ulang gateway ke header `BIP-*` tiap permintaan
(`shared-library/routes/gateway_request.go`). Tugas terjadwal berjalan jam atau hari kemudian,
saat JWT itu sudah kedaluwarsa. Grounding ke kode 2026-09-28 menemukan **tidak ada** mekanisme
yang bisa menggantikannya:

- Cron yang memanggil service lain hari ini memakai `routes.InternalRequest(nil, …)` — contoh
  nyata `services/employee/cron.go:153` — dan dengan `Ctx` nil fungsi itu **tidak mengirim satu
  pun header identitas RBAC**, hanya kunci gateway internal. Endpoint yang menggerbang lewat
  `BIP-System-Roles`/`BIP-Permissions` akan menolak, atau lebih buruk, menjawab sebagai tak-bertuan.
- Bentuk identitas parsial ini sudah menggigit: cron kewajiban kalender harus mengirim perusahaan
  secara eksplisit, karena tanpa itu employee-service jatuh ke perusahaan bawaan dan menagih orang
  dari tenant yang salah ([[Microservices - Calendar Service]] § Mesin kewajiban).
- Perhitungan izin efektif (peran efektif, izin karyawan, gabungan paket posisi, departemen yang
  disupervisi) **hanya hidup privat** di empat titik penerbitan JWT di `services/employee/main.go`,
  tidak diekspor, tidak ada di `shared-library`.
- [[ADR - 0031 Prefix internal Bukan Batas Keamanan]] mencatat sebagai TBD yang belum pernah
  dijawab: cara membedakan permintaan service-ke-service dari permintaan lewat gateway. Kunci
  internal hari ini satu rahasia bersama; header di baliknya dipercaya apa adanya.

Tiga jalan ditimbang:

| Opsi | Cara | Nasib |
|---|---|---|
| 1. Snapshot izin saat tugas dibuat | Simpan izin pembuat, pakai terus | **Ditolak** — orang yang dimutasi, turun jabatan, atau resign tetap menjalankan tugas dengan izin lama. Melanggar inti ADR-0132 ("hak akses identik dengan hak akses orang itu SEKARANG"), dan gagalnya senyap. |
| 2. Endpoint internal "izin efektif terkini" | Ekspor perhitungan izin dari employee-service, dicek ulang tiap run | **Ditunda** — benar secara prinsip, tetapi membuka pintu "bertindak atas nama siapa pun" di sistem yang menurut ADR-0031 belum bisa membedakan pemanggil tepercaya. Keputusan sebesar itu layak ADR sendiri, bukan menumpang fitur ini. |
| 3. Pengingat, bukan eksekusi | Jatuh tempo = notifikasi bertautan; pemakai yang membuka, JWT-nya yang hidup | **Dipilih** |

**Bahan yang sudah ada.** Penjadwal `robfig/cron` dengan zona Asia/Jakarta dipakai luas
(employee, attendance, notification, form-builder, calendar), dengan pola idempoten per periode
dari form berulang ([[Microservices - Form Builder Service]]). Satu-satunya kunci terdistribusi
yang aman lintas replika ada di `services/integration/internal/worker/lock.go` (klaim atomik
`FindOneAndUpdate`). Notifikasi inbox + push sudah hidup ([[Microservices - Notification Service]]).

⚠️ **Status landasan.** ADR-0132 dan [[Microservices - Assistant Service]] masih 🟡 — Copilot
belum bisa menjawab apa pun (baru klien AI dasar T1 dan menu placeholder). ADR ini berdiri di atas
rencana, bukan kenyataan, dan karena itu tidak bisa dikerjakan sebelum fondasinya ada: tautan
pengingat menunjuk ke layar Tanya Jawab yang belum ada.
**Keadaan 2026-10-08**: paragraf di atas adalah keadaan saat ADR ditulis. Tanya Jawab Copilot dan Jadwal
Tugas kini ada di `main` kedua repo; rinciannya di [[Microservices - Assistant Service]].

## Decision

### §1 Jatuh tempo mengirim pengingat, bukan menjalankan pertanyaan

Saat jadwal tiba, `services/assistant` mengirim notifikasi (inbox + push) ke pembuat tugas berisi
nama tugas dan tautan ke Tanya Jawab Copilot dengan instruksi/template tugas sudah terisi.
Pertanyaan dijalankan ketika pemakai membuka tautan itu — lewat jalur normal, JWT hidup, gateway
seperti biasa. **Tidak ada panggilan model AI maupun endpoint data tanpa kehadiran pemakai.**

### §2 Siapa boleh membuat jadwal: gate yang sama dengan Tanya Jawab

Mengikuti ADR-0132 §3 apa adanya, tanpa gate kedua. Saat tautan dibuka, gate Tanya Jawab dinilai
ULANG dengan JWT saat itu: orang yang sudah kehilangan haknya menerima penolakan normal, bukan
jawaban.

### §3 Isi tugas: nama, instruksi atau template, jadwal, notifikasi

Tanpa mode izin, pilihan model, maupun project (lihat § Context). Frekuensi: harian, hari kerja,
mingguan (hari), bulanan (tanggal), pada jam tertentu, zona Asia/Jakarta. "Jalankan sekarang"
tidak butuh fitur khusus — itu sama dengan membuka tautannya.

### §4 Penjadwal: pola yang sudah ada, idempoten per slot

`robfig/cron` di `services/assistant`, meniru pola form berulang. Satu slot jadwal menghasilkan
paling banyak satu pengingat, dijaga indeks unik (tugas, slot). Kunci terdistribusi pola
integration-service hanya dipasang bila service ini dijalankan lebih dari satu replika.

### §5 Satu kategori inbox baru

Kategori baru di `notification.InboxCategories` (nama final saat `/plan`). Karena daftar-izinnya
tersalin ke biner tiap service, **notification-service naik lebih dulu, baru assistant-service**;
urutan terbalik membuat pengiriman ditolak 400 dan hilang tanpa jejak.

### §6 Riwayat: kapan pengingat terkirim dan kapan dibuka

Menjawab kebutuhan "tidak ada jejak". Yang dicatat adalah pengingat, bukan hasil jawaban — hasil
jawaban mengikuti keputusan penyimpanan riwayat percakapan Tanya Jawab yang masih TBD di
[[Microservices - Assistant Service]].

### §7 Eksekusi otomatis penuh ditunda ke ADR terpisah

Bila kelak terbukti dibutuhkan (mis. pemantauan tiap jam tanpa orang membuka), itu menuntut
Opsi 2 dan wajib ADR sendiri yang sekaligus menjawab TBD
[[ADR - 0031 Prefix internal Bukan Batas Keamanan]]. Opsi 1 (snapshot izin) tidak boleh dipakai
sebagai jalan pintas.

## Consequences

### Yang membaik

- Pertanyaan berulang tidak perlu diketik ulang dan tidak terlupa; ada jejak kapan pengingat
  terkirim dan dibuka.
- **Nol mekanisme identitas baru**: tak ada permukaan serangan baru, dan hak akses yang dicabut
  langsung berlaku di pembukaan berikutnya.
- **Biaya AI hanya terjadi saat orang benar-benar membuka.** Jadwal yang diabaikan tidak memakan
  token, jadi batas jumlah tugas per orang lebih soal spam notifikasi daripada biaya.

### Yang memburuk atau tetap terbuka

- Tidak otomatis penuh: laporan tidak menunggu siap di kotak masuk, dan tidak ada ringkasan
  "penting/tidak" di notifikasi (F5 PRD asli).
- Pemantauan tanpa orang (contoh PRD: cek alert tiap jam) tidak terlayani.
- Batas jumlah tugas per orang dan interval minimum belum diputuskan; angka PRD asli (20 tugas,
  minimal 1 jam) adalah angka claude.ai, bukan hasil ukur di sini.

### Yang sengaja tidak dilakukan

- Eksekusi tanpa kehadiran pemakai, dalam bentuk apa pun.
- Menyimpan atau membekukan izin pemakai.
- WhatsApp/Telegram.

## Catatan implementasi (2026-10-08, diukur ke `origin/main` bip-erp `ff3ea482` dan erp-frontend `a4151449c`)

Bagian ini hanya mencatat apa yang dilakukan kode terhadap tiap butir keputusan; ia tidak mengubah keputusan
maupun statusnya. Cara kerja lengkapnya di [[Microservices - Assistant Service]] § Jadwal Tugas.

| Butir | Di kode |
|---|---|
| §1 pengingat, bukan eksekusi | Sesuai. Pemindai hanya mengirim inbox; tak ada panggilan model atau endpoint data (`internal/jadwal/`, `pengingat.go`). Instruksi tidak ikut di notifikasi; layar mengambilnya lewat `GET /jadwal/:id` saat tautan dibuka |
| §2 gate yang sama | Sesuai. Semua rute `/jadwal*` di belakang `common.RequireCopilot`; milik orang lain dibalas 404 |
| §3 isi tugas | Sesuai: nama, instruksi, frekuensi (harian, hari kerja, mingguan, bulanan), jam, zona Asia/Jakarta. Bulanan dibatasi tanggal 1 sampai 28. "Jalankan sekarang" ada sebagai tombol yang mengisi kotak tanya (`sheet-jadwal.tsx`) |
| §4 penjadwal | **Berbeda dari rencana**: ticker 1 menit di proses service, bukan `robfig/cron` (tak ada di `go.mod` service ini). Idempoten per slot lewat indeks unik (jadwal, slot) tetap sesuai. Tambahan implementasi: pengingat yang telat lebih dari 2 jam tidak dikirim |
| §5 kategori inbox | `copilot-jadwal`. Tujuan klik web diturunkan notification-service dari `AppRoute` (bip-erp #2788) |
| §6 riwayat | Sesuai: `GET /jadwal/:id/riwayat` dan `POST /jadwal/:id/dibuka` |
| Batas jumlah tugas dan interval minimum | Tetap **TBD**, tak ada di kode (`internal/jadwal/jadwal.go` menyatakannya) |

⚠️ Belum ada pengukuran PROD atas fitur ini pada 2026-10-08.

## Dokumen Terkait

- [[ADR - 0132 Asisten AI Tanya-Jawab Lintas Modul, Lapisan Data Bisnis per Service Bukan Terpusat]] — fondasi yang harus ada lebih dulu, gate §3 dipakai ulang
- [[Microservices - Assistant Service]] — cara kerja Jadwal Tugas (§ Jadwal Tugas)
- [[ADR - 0031 Prefix internal Bukan Batas Keamanan]] — TBD yang membuat Opsi 2 belum layak
- [[ADR - 0058 Kapabilitas AI Digerbang Kelayakan Data, Bukan Kelayakan Teknologi]] — batas "murni baca"
- [[Microservices - Notification Service]] — kategori inbox dan urutan deploy
- [[Microservices - Form Builder Service]] — preseden penjadwal idempoten per periode
- [[Microservices - Calendar Service]] — bukti nyata identitas parsial di cron yang salah tenant
