## Deskripsi

*Tiket Engagement DITUGASKAN langsung oleh Account Specialist saat permintaan dibuat — `assigned_to` wajib, tunggal, dan tak pernah kosong. Model lama, yaitu antrian bersama tempat anggota tim mengambil sendiri tiket ("claim"), DITINGGALKAN. Keputusan ini mengubah makna status `OPEN` tanpa mengubah namanya, dan sisa-sisa model lama masih berserak di kode — itulah sebab tiga cacat yang tercatat di [[Sales - Engagement Team (Modul)]].*

- **Status**: ⚠️ **Berlaku, kodenya sudah di `main`** — BE commit `06691bc8` "Account Specialist menugaskan, bukan anggota mengambil" (PR [#1504](https://github.com/bip-itteam-internal/bip-erp/pull/1504)), FE commit `ebb55961` "pemilih pengerja menggantikan tombol Ambil Tiket" (PR [#1287](https://github.com/bip-itteam-internal/erp-frontend/pull/1287)). ⚠️ **Pembersihan sisa model lama BELUM tuntas** — lihat Consequences. **Belum diverifikasi lewat gateway.**
- **Path di repo**: `bip-erp/services/task-management/engagement_assign.go` · `engagement_handlers.go` · `engagement_state.go` · `erp-frontend/src/features/marketing/engagement/**`
- **Tanggal**: keputusan diambil saat modul dibangun ulang; didokumentasikan 2026-08-29

## Context

Rancangan awal modul Engagement meniru pola antrian bersama: tiket lahir tanpa pemilik di status `OPEN`, seluruh anggota space diberi tahu, dan siapa pun boleh menekan **Ambil Tiket**. Pola itu masuk akal untuk tim yang bebannya seragam dan anggotanya setara.

Yang tidak cocok:

1. **Pekerjaan boosting tidak seragam.** Satu tiket menuntut akun pada platform tertentu, gaya bahasa tertentu, dan kadang akun yang sudah punya riwayat dengan client itu. Yang tahu siapa cocok mengerjakan apa adalah **pembuat permintaannya**, bukan siapa yang lebih dulu menekan tombol.
2. **Antrian bebas mendorong pemilihan yang menguntungkan pengambil.** Tiket mudah diambil lebih dulu; tiket sulit mengendap — dan tim ini **tak punya lead** yang menyadarinya.
3. **Account Specialist tetap bertanggung jawab atas hasilnya ke client.** Ia yang menutup atau meminta revisi, sehingga ia pula yang pantas memutuskan siapa mengerjakannya.

## Decision

**Account Specialist menunjuk satu pengerja saat membuat permintaan. Tiket engagement tak pernah berada di sistem tanpa pemilik.**

### 1. `assigned_to` wajib, tunggal, dan tanpa nilai bawaan

`POST /engagement/tickets` menolak `400` bila `assigned_to` kosong. Membiarkannya kosong akan menerbitkan tiket yatim yang tak muncul di papan kerja siapa pun — **dan tak ada lagi antrian bersama tempat ia bisa ditemukan**.

Sengaja **string tunggal**, bukan array seperti `Task.AssignTo` pada tiket IT: satu tiket dikerjakan satu orang, dan array membuka kemungkinan dua penanggung jawab yang tak punya arti di alur ini. `Task.AssignTo` yang sudah ada tidak disentuh.

### 2. Nilai `OPEN` dipertahankan meski maknanya berubah

`OPEN` kini berarti **"sudah ditugaskan, belum disentuh"**, bukan "menunggu diambil". Namanya tetap karena nilai itu sudah tersimpan di dokumen produksi, dan me-rename-nya menuntut migrasi data yang tak menambah apa pun selain risiko.

⚠️ **Ini konsekuensi yang paling mudah salah dibaca.** Siapa pun yang menyusun query papan kerja wajib **memasukkan `OPEN`**: di model penugasan langsung, `OPEN` justru isi utama papan kerja seseorang, bukan tiket yang belum jadi miliknya.

### 3. Kandidat penugasan disaring DEPARTEMEN, bukan jabatan

`daftarKandidatPengerja` membaca rekan **sedepartemen pemanggil** dari `employee_db` ERP (read-only, lihat [[Microservices - Employee Service]]), bukan menyaring `position == "Engagement Team"`.

Alasannya langsung: **tim ini baru saja di-rename dari "Buzzer" jadi "Engagement Team"**, dan penyaring berbasis nama jabatan akan mengosongkan daftar penugasan pada rename berikutnya **tanpa satu pun galat** — formulirnya tetap terbuka, dropdown-nya kosong, dan tak ada yang berbunyi salah. Departemen jauh lebih stabil. Sejarah rename ini dicatat di [[Sales - Engagement Team (Modul)]].

Konsekuensi yang diterima sadar: daftar memuat orang yang bukan pengerja engagement — Account Specialist sendiri ikut muncul. Menyaring terlalu ketat justru membuat orang yang seharusnya bisa ditugaskan menghilang tanpa penjelasan.

Aturan turunan:
- **Departemennya ditentukan SERVER** dari header identitas, bukan parameter yang boleh dipilih klien. Kalau bisa diminta lewat query, siapa pun bisa melihat daftar karyawan departemen lain lewat endpoint ini.
- **Akun non-aktif dibuang.** Menugaskan tiket ke orang yang sudah resign membuatnya mengendap sampai ada yang menyadarinya.
- **Daftar kosong adalah keadaan yang sah, bukan galat** — tapi layar tak boleh diam, karena pemakainya lalu mengira formulirnya rusak. Respons membawa `catatan` yang menyebut departemennya.

### 4. Penugasan ulang menggantikan "lepas tiket"

Karena tim ini tak punya lead, tanpa jalur ini tiket orang yang berhalangan (cuti, resign, salah tunjuk) **mengendap selamanya**. Aturannya:

- Yang boleh: **pembuat tiket atau admin/supervisor**. Pengerja **sengaja tidak boleh** memindahkan tiketnya sendiri — yang memutuskan siapa mengerjakan apa tetap Account Specialist.
- Tiket `IN_PROGRESS` kembali ke `OPEN` supaya pengerja barunya memulai dari awal; tiket `OPEN` dipindah tanpa transisi status.
- `started_at` dan `escalated_at` **dibersihkan**: bagi pengerja baru tiket ini benar-benar baru, dan membiarkan `started_at` lama membuat KPI-nya dihitung sejak orang **lain** memulainya.
- **Wajib alasan.** Tindakan ini membalikkan pekerjaan orang lain; tanpa alasan penerimanya tak tahu apa yang terjadi.
- `reassign_count` dicatat **tetapi sengaja bukan kolom peringkat di dashboard**: memindahkan tiket dari orang yang berhalangan adalah tindakan yang BENAR, dan mengangkatnya jadi angka yang dibandingkan antar-orang menghukum tepat tindakan itu. Tempatnya di detail tiket, sebagai riwayat.

### 5. Revisi kembali ke orang yang SAMA

`DONE_BY_TEAM` → `IN_PROGRESS` tidak menyentuh `assigned_to`. Ini yang membedakannya dari *reopen* tiket IT, yang melempar tiket ke stage pertama. Menugaskan ulang saat revisi membuat pengerja baru mewarisi pekerjaan setengah jadi tanpa konteksnya.

### 6. Notifikasi jadi personal, bukan siaran

Tiket baru menyapa **orang yang ditugaskan**, bukan seluruh anggota space. Eskalasi menyapa **pengerja + pemohon**: cuma dua orang itu yang bisa menindak — pengerjanya mengerjakan, pemohonnya menugaskan ulang bila yang bersangkutan berhalangan. Menyiarkannya ke semua orang hanya membuat pemberitahuan berhenti dibaca.

## Consequences

**Konsekuensi yang diterima:**

- **Beban tidak menyeimbangkan diri sendiri.** Account Specialist yang selalu menunjuk orang yang sama akan menumpuk pekerjaan padanya, dan **tak ada mekanisme yang menahannya** — hanya dashboard "tiket per anggota" yang membuatnya terlihat. Ini harga yang dibayar untuk penugasan yang tepat sasaran.
- **Makna metrik KPI ikut bergeser.** `menit_ambil` di `/kpi/engagement` **namanya tetap** karena sudah jadi kontrak yang dibaca [[Microservices - Employee Service]], tetapi yang diukur kini `assigned_at` → `done_at`, yaitu *berapa lama menyelesaikan*, bukan *berapa cepat merespons*. Konsekuensinya bagi HR: pengerja yang langsung mengerjakan tiket berat tampak sama lambatnya dengan yang menunda. `started_at` sudah tersimpan bila kelak perlu dibedakan.

**⚠️ Konsekuensi yang BELUM ditutup — sisa model lama masih di kode:**

Keputusan ini diambil dan diterapkan, tetapi pembersihannya tidak tuntas, dan itulah sebab langsung tiga cacat yang tercatat di [[Sales - Engagement Team (Modul)]]:

- Query papan kerja masih menyaring **`claimed_by`**, field model lama yang tak pernah ada di `EngagementTicket` dan tak pernah ditulis. Tab "Pekerjaan Saya" karena itu **selalu kosong dengan `200`** — tak ada galat sama sekali. Index `ix_pemegang` dan `hitungWIP` menunjuk field mati yang sama.
- Dua tipe notifikasi model lama (`engagement_ticket_open`, `engagement_released`) masih terdaftar lengkap sampai pemetaan FCM, tetapi **tak pernah dikirim**; pembaca `anggotaSpaceEngagement` juga tak ada lagi.
- **Komentar di kode masih menjanjikan model lama**: kepala berkas notifikasi menyatakan "menyapa SELURUH anggota space", ada doc-comment untuk fungsi `notifikasiTiketBaru` yang tidak ada, dan komentar antrian menyebut "antrian bersama". Bahayanya bukan biaya runtime melainkan **kebohongan dokumentasi**: pembaca berikutnya menyimpulkan modul ini menyiarkan tiket baru ke seluruh space, dan asumsi keliru itu melahirkan keputusan keliru.

Sisi FE punya sisa yang sama: kolom "Alasan" masih dirender untuk pengerja pada status `IN_PROGRESS`, padahal tak ada satu pun aksi pengerja yang memakai alasan (sisa aksi "lepas tiket" yang sudah dihapus).

**Yang belum diputuskan (TBD):**

- **Apakah notifikasi "tiket baru" ke seluruh space masih diinginkan** sebagai kesadaran situasi, di samping notifikasi personal ke yang ditugaskan. Kalau ya, kode yang menganggur itu adalah **fitur yang belum jadi**, bukan dead code — dan pembersihannya salah. Kalau tidak, ia dan komentar kepala berkasnya harus dibuang bersama.
- **Apakah batas WIP per anggota direncanakan.** `hitungWIP` ada tapi tak dipanggil dari mana pun; ia satu-satunya sisa model lama yang mungkin bukan sampah.

## Terkait

- [[Sales - Engagement Team (Modul)]] — konsep bisnis modul ini, termasuk daftar cacat yang jadi turunan keputusan ini
- [[ADR - 0058 Tiket Engagement Memakai Koleksi dan State Machine Sendiri]] — keputusan pasangannya, tentang di mana tiketnya disimpan
- [[Microservices - Task Management Service]] · [[API - Task Management Service]] · [[Microservices - Employee Service]] · [[APP - Web ERP]]
