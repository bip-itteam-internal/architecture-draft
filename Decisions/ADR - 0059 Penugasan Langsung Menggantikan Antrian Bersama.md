## Deskripsi

*Tiket Engagement DITUGASKAN langsung oleh Account Specialist saat permintaan dibuat — `assigned_to` wajib, tunggal, dan tak pernah kosong. Model lama, yaitu antrian bersama tempat anggota tim mengambil sendiri tiket ("claim"), DITINGGALKAN. Keputusan ini mengubah makna status `OPEN` tanpa mengubah namanya, dan sisa-sisa model lama masih berserak di kode — itulah sebab tiga cacat yang tercatat di [[Sales - Engagement Team (Modul)]].*

- **Status**: ⛔ **§1-§3 DIGANTIKAN 2026-09-01** oleh [[ADR - 0083 Alokasi Otomatis Round-Robin Menggantikan Penunjukan Manual AS]] — AS tidak lagi menunjuk pengerja, server mengalokasikan lewat round-robin. **§4 (penugasan ulang), §5 (revisi ke orang sama), §6 (notifikasi personal) TETAP BERLAKU**, tidak disentuh ADR-0083. Teks di bawah dipertahankan sebagai catatan sejarah keputusan awal — jangan dibaca sebagai perilaku saat ini untuk §1-§3.
- Riwayat: BE commit `06691bc8` "Account Specialist menugaskan, bukan anggota mengambil" (PR [#1504](https://github.com/bip-itteam-internal/bip-erp/pull/1504)), FE commit `ebb55961` "pemilih pengerja menggantikan tombol Ambil Tiket" (PR [#1287](https://github.com/bip-itteam-internal/erp-frontend/pull/1287)). ⚠️ **Pembersihan sisa model lama BELUM tuntas** — lihat Consequences.
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

> ⚠️ **Butir ini DIUBAH 2026-08-29 oleh [[ADR - 0060 Cakupan Keterlihatan Tiket Engagement]] §4.** Peringatannya (nama jabatan rapuh terhadap rename) tetap berlaku, tetapi kesimpulannya — memakai departemen **pemanggil** — dibatalkan: ia diam-diam mengandaikan requester dan pengerja sedepartemen, sedangkan permintaan datang dari Account Specialist di **Kyura & Beauty Hacks**. Penggantinya menyaring `position_key` yang daftarnya disimpan sebagai **data**, bukan literal di handler. Teks di bawah dipertahankan sebagai catatan sejarah.

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

- ✅ **DIPERBAIKI** (tanggal tak tercatat di commit message, terverifikasi ada di `main` per 2026-09-09): `pekerjaanSaya`, index `ix_pemegang`, dan `hitungWIP` kini menyaring/dibangun atas `assigned_to`, bukan `claimed_by` lagi. Dikunci `engagement_regresi_test.go` (T-02) yang memindai sumber ketiganya menolak kemunculan literal `claimed_by`.
- ⚠️ **Masih benar per 2026-09-09, walau [[ADR - 0060 Cakupan Keterlihatan Tiket Engagement]] §6 mengklaim ini sudah dibereskan**: dua tipe notifikasi model lama (`NotifEngagementOpen`/`engagement_ticket_open`, `NotifEngagementReleased`/`engagement_released`, `engagement_notify.go:21-23`) masih terdaftar lengkap sampai pemetaan FCM (`fcm.go:66`), tetapi **tak pernah dikirim** dari satu pun handler. `anggotaSpaceEngagement` (`engagement_notify.go:55`) juga **masih ada di kode**, bukan dibuang seperti yang dinyatakan ADR-0060 — ia sekadar tak dipanggil dari mana pun (dead code terbukti lewat Grep, bukan diasumsikan). `semuaTipeNotifEngagement()` (`engagement_notify.go:37-48`) memuat `NotifEngagementClaimed` DUA KALI dan tidak memuat `NotifEngagementOpen` sama sekali — penjaga test yang mengiterasi daftar ini karena itu tak bisa menangkap tipe yang hilang.
- **Komentar di kode masih menjanjikan model lama**: kepala berkas notifikasi menyatakan "menyapa SELURUH anggota space", ada doc-comment untuk fungsi `notifikasiTiketBaru` yang tidak ada, dan komentar antrian menyebut "antrian bersama". Bahayanya bukan biaya runtime melainkan **kebohongan dokumentasi**: pembaca berikutnya menyimpulkan modul ini menyiarkan tiket baru ke seluruh space, dan asumsi keliru itu melahirkan keputusan keliru.

Sisi FE punya sisa yang sama: kolom "Alasan" masih dirender untuk pengerja pada status `IN_PROGRESS`, padahal tak ada satu pun aksi pengerja yang memakai alasan (sisa aksi "lepas tiket" yang sudah dihapus).

**Yang belum diputuskan (TBD):**

- ~~**Apakah notifikasi "tiket baru" ke seluruh space masih diinginkan**~~ — **DIJAWAB 2026-08-29** oleh [[ADR - 0060 Cakupan Keterlihatan Tiket Engagement]] §6: `space_id` dicabut sebagai sumber keanggotaan. ⚠️ **Tapi pembersihan kode yang ADR-0060 klaim sudah terjadi TERNYATA BELUM** (diverifikasi Grep 2026-09-09) — `anggotaSpaceEngagement`, `NotifEngagementOpen`/`NotifEngagementReleased`, dan komentar kepala berkas yang menjanjikan "seluruh anggota space" semuanya **masih ada di kode**, sekadar tak terpanggil dari jalur manapun. Lihat baris di atas.
- **Apakah batas WIP per anggota direncanakan.** `hitungWIP` ada tapi tak dipanggil dari mana pun; ia satu-satunya sisa model lama yang mungkin bukan sampah.

## Terkait

- [[ADR - 0083 Alokasi Otomatis Round-Robin Menggantikan Penunjukan Manual AS]] — MENGGANTIKAN §1-§3 ADR ini (2026-09-01)
- [[Sales - Engagement Team (Modul)]] — konsep bisnis modul ini, termasuk daftar cacat yang jadi turunan keputusan ini
- [[ADR - 0058 Tiket Engagement Memakai Koleksi dan State Machine Sendiri]] — keputusan pasangannya, tentang di mana tiketnya disimpan
- [[Microservices - Task Management Service]] · [[API - Task Management Service]] · [[Microservices - Employee Service]] · [[APP - Web ERP]]
