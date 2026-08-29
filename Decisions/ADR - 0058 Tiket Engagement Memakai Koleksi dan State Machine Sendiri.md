## Deskripsi

*Tiket Engagement Tim disimpan di koleksi Mongo sendiri (`engagement_tickets`) dengan state machine lima status yang ditulis di kode, BUKAN sebagai `tasks` ber-stage space seperti tiket IT — meski keduanya hidup di service yang sama. Menyimpang dari model satu-koleksi-satu-service yang berlaku di [[Microservices - Task Management Service]], dengan alasan yang dicatat di bawah.*

- **Status**: ⚠️ **Berlaku, kodenya sudah di `main`** (bip-erp PR [#1504](https://github.com/bip-itteam-internal/bip-erp/pull/1504) `feat/engagement-assign`; commit awalnya `3436ad95` "model, nomor tiket, dan repository"). ADR ini ditulis **setelah** kodenya ada — keputusannya selama ini hanya hidup sebagai komentar di `engagement_models.go:9-18` dan `engagement_state.go:3-13`. **Belum diverifikasi lewat gateway** dev maupun prod.
- **Path di repo**: `bip-erp/services/task-management/engagement_models.go` · `engagement_state.go` · `engagement_repo.go` · `engagement_nomor.go`
- **Tanggal**: keputusan diambil saat modul dibuat; didokumentasikan 2026-08-29

## Context

[[Microservices - Task Management Service]] sudah menjadi rumah tiket IT: koleksi `tasks`, board Kanban per space, stage yang **dinamis per space**. Ketika modul boosting Engagement Tim dibangun di service yang sama, pilihan yang paling murah tampaknya menumpang struktur itu — satu space baru untuk tim Engagement, tiketnya jadi `tasks` biasa.

Yang menghalangi bukan selera, melainkan penjaga yang sudah ada:

1. **`updateSpace` menolak `400` bila stage `Request`/`Todo`/`Done` hilang dari sebuah space** (`space_handlers.go`). Alur engagement (`OPEN` → `IN_PROGRESS` → `DONE_BY_TEAM` → `CLOSED`) tak dapat dinyatakan sebagai stage space tanpa menyeret tiga stage yang tak pernah dipakai, **plus** satu penjaga yang menolak menghapusnya.
2. **Kosakata alurnya memang berbeda.** Engagement tak punya triase supervisor dan tak punya tahap "Testing". Sebaliknya ia punya dua hal yang tak ada di tiket IT: verifikasi oleh **pemohon** (bukan supervisor) dan jalur revisi yang mengembalikan tiket ke **pengerja yang sama**.
3. **Siapa yang berwenang juga berbeda.** Di tiket IT, yang menutup tiket adalah supervisor/admin space. Di engagement, yang menutup adalah pembuat permintaannya — dan pengerja **tidak boleh** menutup pekerjaannya sendiri.

Ada pula pertimbangan risiko: tiket IT sudah live di produksi dengan ratusan dokumen, laporan, SLA, dan CSAT yang membacanya. Setiap perubahan pada `tasks` demi modul baru mempertaruhkan modul yang sudah jalan.

## Decision

**Modul Engagement memakai koleksi Mongo sendiri dan state machine yang ditulis di kode, di dalam service yang sama.**

### 1. Tiga koleksi terpisah

`engagement_tickets` (tiket) · `engagement_ticket_items` (baris target: URL + jenis + volume) · `engagement_logs` (audit trail). Nama-namanya dikumpulkan sebagai konstanta di satu tempat supaya nama yang dipakai query dan nama yang dipakai definisi index tidak pernah menyimpang.

**Baris target sengaja koleksi terpisah, bukan array embedded**, karena `volume_realisasi` diperbarui **per baris** saat pengerja melapor.

### 2. State machine di kode, bukan data

Lima status tetap (`OPEN` · `IN_PROGRESS` · `DONE_BY_TEAM` · `CLOSED` · `CANCELLED`) dan tabel transisi `transisiSah` yang memetakan tiap perpindahan ke **daftar peran yang boleh melakukannya**.

Daftar peran itu **setengah dari gerbangnya**: "siapa" sama menentukannya dengan "dari mana ke mana". Tanpa itu, pengerja bisa menutup tiketnya sendiri — menilai hasil pekerjaan sendiri — dan pemohon bisa menandai selesai pekerjaan yang tak ia kerjakan.

`bolehTransisi` adalah **satu-satunya** gerbang perpindahan status, dipanggil dari handler **sebelum** menulis, dan galatnya dikembalikan apa adanya ke klien. Menyembunyikan tombol di frontend bukan gerbang: gateway meneruskan permintaan apa adanya ([[CORE - API Master Gateway]]), jadi siapa pun bisa memanggil endpoint transisi langsung.

Status di luar kosakata **ditolak saat menulis**, persis (case-sensitive, tanpa trim). Nilai dari klien tidak dinormalisasi diam-diam, supaya salah ketik ditolak `400` alih-alih tersimpan sebagai status yang tak pernah cocok dengan apa pun.

### 3. Nomor tiket sendiri: `ENG/YYYYMM/NNNN`

Awalan bulan diambil dari **jam WIB**, bukan UTC — tiket yang dibuat 1 September 06:00 WIB adalah 31 Agustus 23:00 UTC, dan memakai UTC memberinya awalan bulan yang salah. Zonanya **memakai ulang** `feedWIB` milik modul kalender di service yang sama; dua pemuatan "Asia/Jakarta" berarti dua tempat yang bisa menyimpang.

Nomor di atas 9999 **melebar** jadi lima digit, tidak dipotong — memotongnya menerbitkan nomor yang sudah terpakai bulan itu.

Penjaga nomor ganda adalah **index unique `no_tiket`**, bukan pengecekan di aplikasi: dua permintaan bersamaan pasti membaca hitungan yang sama. Karena itu kegagalan membuat index inilah satu-satunya yang dicatat mencolok saat start; kegagalan index lain tidak mematikan service, sebab service yang menolak start membuat **modul tiket IT ikut padam karena tetangganya**.

### 4. Apa yang tetap dipakai bersama

Yang dipisah cuma bentuk datanya; infrastruktur di sekitarnya sengaja **tidak** diduplikasi:

- **Bukti pengerjaan memakai `FileAttachment` yang sama dengan tiket IT.** Bentuknya sudah menampung screenshot (`file`) maupun tautan (`link`), dan aturan upload/hapus/presigned-nya sudah dikelola [[Microservices - File Service]]. Koleksi bukti tersendiri akan menyalin aturan itu untuk kedua kalinya.
- **Notifikasi memakai `notifyMany()` yang sama** (Mongo + WebSocket + inbox + FCM lewat [[Microservices - Notification Service]]). Yang berbeda hanya siapa penerimanya.
- **Eskalasi menumpang scheduler per jam yang sudah ada** (`sla_scheduler.go`, lihat [[IT - Background Jobs & Schedulers]]). Dua penjadwal di satu service berarti dua tempat yang harus diperiksa saat sesuatu tak berjalan.
- **Bentuk paginasi mengikuti kontrak `MainTable`** di [[APP - Web ERP]] (`has_next`/`has_prev`/`limit`/`page`/`total_items`/`total_pages`). Bentuk yang berbeda memaksa tiap halaman menambal sendiri, dan tambalan itulah yang menyimpang satu per satu.

## Consequences

**Konsekuensi yang diterima:**

- **State machine engagement tak bisa dirusak oleh orang yang menyunting stage space**, dan tiket IT yang sudah live tidak tersentuh sama sekali. Ini keuntungan utamanya.
- **Sebaliknya, mengubah alur engagement menuntut deploy**, sedangkan stage tiket IT bisa diubah dari layar. Diterima: alur ini punya aturan wewenang per transisi yang memang tak pantas diserahkan ke layar pengaturan.
- **Laporan, SLA, CSAT, dan audit trail tiket IT tidak melihat tiket engagement sama sekali.** Modul ini punya dashboard dan log sendiri. Siapa pun yang ingin angka gabungan harus menggabungkannya sendiri.
- **`Notification.TaskID` tak bisa dipakai** — bertipe ObjectID tugas, dan menaruh id tiket engagement di sana akan membuat klien membuka detail tugas yang tak ada. Identitas tiket dititipkan lewat `meta` (`modul`, `engagement_ticket_id`, `no_tiket`), dan klien mana pun yang ingin membuka detail dari notifikasi harus membacanya dari sana.
- **Dua definisi "tiket" di satu service.** Pembaca berikutnya wajib memeriksa koleksi mana yang sedang dibicarakan sebuah fungsi. Sudah terbukti berbahaya sekali: rute lampiran yang ada beroperasi atas `tasks`, dan modul engagement **tak punya rute lampiran sama sekali** — sementara handler-nya mewajibkan lampiran. Lihat cacat nomor 1 di [[Sales - Engagement Team (Modul)]].

**Yang belum diputuskan (TBD):**

- **Apakah `engagement_tickets` perlu menyimpan `department`.** Saat ini tidak, dan akibatnya batas keterlihatan tiket belum bisa ditegakkan sama sekali. Keputusan itu punya ADR-nya sendiri begitu SPV memutuskan cakupannya.
- **Apakah tiket engagement kelak perlu masuk laporan gabungan** bersama tiket IT (mis. beban lintas modul per orang).

## Terkait

- [[Sales - Engagement Team (Modul)]] — konsep bisnis modul ini
- [[Microservices - Task Management Service]] — service tempat kedua model tiket hidup berdampingan · [[API - Task Management Service]] — kontrak endpoint
- [[ADR - 0059 Penugasan Langsung Menggantikan Antrian Bersama]] — keputusan pasangannya, tentang siapa yang menentukan pengerja
- [[ADR - 0002 Database-per-Service]] — batas yang TIDAK dilanggar di sini: koleksinya terpisah, databasenya tetap satu milik service ini
- [[Microservices - File Service]] · [[Microservices - Notification Service]] · [[CORE - API Master Gateway]]
