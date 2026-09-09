# Sales - Engagement Team (Modul)

## Deskripsi

*Modul **Engagement Tim** adalah alur tiket boosting media sosial: **Account Specialist** membuat permintaan (like/komentar/share/review pada sejumlah URL target), sistem **mengalokasikan otomatis** satu anggota tim Engagement lewat round-robin, lalu Account Specialist memverifikasi hasilnya. Tiket hidup di koleksi Mongo sendiri di dalam [[Microservices - Task Management Service]], terpisah dari tiket IT, dengan state machine dan nomor tiketnya sendiri. Angka penutupannya jadi sumber KPI `kinerja_engagement` di [[Microservices - Employee Service]].*

- **Status**: ⚠️ Implemented (ada catatan) — kode maju banyak sejak audit awal (28-29 Agustus 2026): **3 dari 4 cacat blocker/risiko audit awal sudah diperbaiki** (bukti pengerjaan dilonggarkan jadi opsional, tab Pekerjaan Saya diperbaiki, keterlihatan disaring per departemen via [[ADR - 0060 Cakupan Keterlihatan Tiket Engagement]]), penugasan berpindah total dari manual ke **round-robin otomatis** ([[ADR - 0083 Alokasi Otomatis Round-Robin Menggantikan Penunjukan Manual AS]], 1 September), dan satu **bug baru ditemukan+diperbaiki 2026-09-09**: nama pengerja salah lookup collection sehingga tampil sebagai `employee_id` mentah di setiap layar (dropdown reassign, kolom Pengerja, pratinjau giliran). Rincian terkini di **## Cacat yang Diketahui**. **Belum diverifikasi lewat gateway** dev maupun prod.
- **Implementasi**: [[Microservices - Task Management Service]] (bagian *Modul Engagement Tim*) · kontrak endpoint di [[API - Task Management Service]]
- **Layar**: [[APP - Web ERP]] — menu **Marketing › Engagement** (`/marketing/engagement`)
- **Keputusan**: [[ADR - 0058 Tiket Engagement Memakai Koleksi dan State Machine Sendiri]] · [[ADR - 0059 Penugasan Langsung Menggantikan Antrian Bersama]] · [[ADR - 0060 Cakupan Keterlihatan Tiket Engagement]] · [[ADR - 0083 Alokasi Otomatis Round-Robin Menggantikan Penunjukan Manual AS]]

## Latar Belakang

- Pekerjaan boosting selama ini diminta lewat kanal informal (chat), sehingga tak ada jejak siapa meminta apa, kapan tenggatnya, dan apakah hasilnya diterima. Tanpa jejak itu, tak ada dasar penilaian kinerja tim.
- [[HRIS - Matriks KPI per Departemen]] mencatat empat metrik posisi ini (*Early Engagement Speed*, *Engagement Quantity*, *Engagement Quality*, *Reporting & Account Readiness*) sebagai **"belum bisa otomatis — akun buzzer memakai akun personal, tidak ada integrasi API"**. Modul ini **tidak** menyelesaikan halangan itu; ia mengukur **proksi berbasis tiket** (kapan ditugaskan → kapan selesai, realisasi vs target volume, ada/tidaknya revisi, ada/tidaknya bukti). Lihat **## Konsumen Data** dan catatan gap-nya.
- Tim ini **dulu bernama "Buzzer"** dan di-rename HR jadi **"Engagement Team"**. Nama lama masih hidup di banyak tempat, dan itu jebakan nyata — lihat **## Sejarah Rename: Buzzer → Engagement Team**.

## Ruang Lingkup / Cakupan (business view)

### Siklus hidup satu permintaan

1. **Account Specialist membuat tiket**: client, campaign, platform, jenis pekerjaan, volume, deadline, prioritas, guideline/tone of voice/kata terlarang, plus **satu atau lebih baris target** (URL + jenis + volume target). Ia **TIDAK LAGI menunjuk pengerjanya** — sejak [[ADR - 0083 Alokasi Otomatis Round-Robin Menggantikan Penunjukan Manual AS]] (1 September 2026), server mengalokasikan otomatis lewat giliran round-robin (sedepartemen requester secara default). Form menampilkan pratinjau read-only siapa yang AKAN dapat giliran (`GET /engagement/giliran-berikutnya`, sejak 2 September) — **perkiraan**, bisa berbeda dari hasil sungguhan bila giliran bergeser sebelum submit.
2. Sistem menerbitkan **nomor tiket** `ENG/YYYYMM/NNNN` (bulan menurut WIB) dan mengirim notifikasi ke orang yang teralokasi.
3. **Pengerja** menandai *mulai* (opsional) lalu *sudah dikerjakan* — **bukti pengerjaan OPSIONAL** sejak keputusan SPV melonggarkan syaratnya (semula wajib dan membuat tiket mustahil ditandai selesai, lihat ## Cacat yang Diketahui).
4. **Account Specialist memverifikasi**: *tutup* bila sesuai, atau *minta revisi* (wajib alasan) yang mengembalikan tiket ke **pengerja yang sama**.
5. Bila pengerjanya berhalangan, **pembuat tiket atau admin/supervisor menugaskan ulang** (wajib alasan). Pembatalan juga milik keduanya, wajib alasan.

Status: `OPEN` → `IN_PROGRESS` → `DONE_BY_TEAM` → `CLOSED`, dengan jalur revisi `DONE_BY_TEAM` → `IN_PROGRESS`, jalur tugas-ulang `IN_PROGRESS` → `OPEN`, dan `CANCELLED` dari `OPEN`/`IN_PROGRESS`. Tabel transisi + peran yang berwenang ada di [[Microservices - Task Management Service]].

### Yang membedakannya dari tiket IT di service yang sama

| Hal | Tiket IT (`tasks`) | Tiket Engagement (`engagement_tickets`) |
|---|---|---|
| Stage | dinamis per space, wajib memuat `Request`/`Todo`/`Done` | lima status **tetap** di kode |
| Triase | supervisor menyetujui/menolak permintaan masuk | **tak ada triase** — tiket lahir sudah tertuju ke orang |
| Penugasan | supervisor/admin space saat approve (bisa round-robin) | **server** mengalokasikan otomatis lewat round-robin saat dibuat (sejak 1 Sep 2026, [[ADR - 0083 Alokasi Otomatis Round-Robin Menggantikan Penunjukan Manual AS]]) — pemohon tak lagi memilih |
| Verifikasi hasil | supervisor meninjau `Testing → Done` | **pemohon** yang menutup atau minta revisi |
| SLA | dua dimensi (response + resolution), target per prioritas | `deadline` diisi pemohon; prioritas hanya mengurutkan tampilan |
| Eskalasi | breach SLA → supervisor divisi | tiket menganggur → pengerja + pemohon (tim flat, tak ada lead) |
| Kepuasan | CSAT 1–5 bintang | tidak ada; kualitas = "tanpa revisi" |

Alasan pemisahannya: [[ADR - 0058 Tiket Engagement Memakai Koleksi dan State Machine Sendiri]].

### Eskalasi tiket yang didiamkan

Tim ini **flat, tanpa lead** — tak ada satu orang pun yang bisa dijadikan tujuan tunggal pemberitahuan, dan tak ada yang menyadari sebuah tiket didiamkan. Penggantinya scheduler per jam yang menumpang scheduler SLA tiket IT ([[IT - Background Jobs & Schedulers]]):

- Ambang: **2 jam ATAU setengah sisa deadline, mana yang lebih dulu**. Batas tetap saja membuat tiket berdeadline 1 jam sudah telat sebelum ambang menyala; setengah-deadline saja membuat tiket berdeadline seminggu menganggur 3,5 hari tanpa ada yang tahu.
- Hanya tiket berstatus `OPEN` (ditugaskan tapi belum disentuh).
- Penerimanya **pengerja + pemohon**, bukan seluruh tim: cuma dua orang itu yang bisa menindak.
- Ada **penanda anti-spam** (`escalated_at`): tanpa itu satu tiket yang menganggur seharian mengirim 24 notifikasi, dan pemberitahuan yang membanjir berhenti dibaca. Penanda dikosongkan lagi saat tiket ditugaskan ulang, karena saat itu ia benar-benar menganggur lagi.

## Persona / Pengguna

| Persona | Peran & Divisi | Akses / RBAC | Device |
|---|---|---|---|
| Account Specialist | staf marketing (Kyura / Beauty Hacks), pemohon boosting | tier `staff`; menu digerbang `IZIN_MARKETING.po` | Web ERP |
| Anggota tim Engagement (dulu *Buzzer*) | staf marketing, pengerja boosting | tier `staff`; menu digerbang `IZIN_MARKETING.po` | Web ERP |
| Supervisor / Admin marketing | atasan divisi | tier `supervisor`/`admin`; boleh menugaskan ulang & membatalkan tiket **siapa pun** | Web ERP |

- **Tujuan**: pemohon ingin pekerjaan boostingnya dikerjakan tepat waktu dan bisa diverifikasi; pengerja ingin tahu apa yang harus ia kerjakan hari ini; supervisor ingin melihat beban tim dan siapa memegang apa.
- **Pain point**: permintaan lewat chat tak punya tenggat, bukti, maupun riwayat; tak ada dasar penilaian kinerja.
- **Aksi utama**: buat tiket + tunjuk pengerja → mulai/tandai selesai + lampirkan bukti → tutup atau minta revisi.

⚠️ **Peran adalah relasi terhadap tiket, bukan jabatan orangnya.** Orang yang sama bisa jadi pemohon di satu tiket dan pengerja di tiket lain; yang menentukan wewenangnya adalah `requester_id`/`assigned_to` pada tiket yang sedang disentuh. Gerbang rute hanya membuka pintu (`staff`/`supervisor`/`admin`); keputusan sebenarnya ada di handler.

⚠️ **Menu tak menyaring siapa pun.** Ketiga persona di atas memakai izin menu yang sama (`IZIN_MARKETING.po`, sama dengan "PO Barang Jadi"; menu "Target Marketing" yang dulu seizin ini sudah dicabut, [[ADR - 0079 Target Profit Satu Pintu di Insentif, KPI Membacanya]] §6), dan halamannya menampilkan tab berbeda menurut peran orang pada tiap tiket — bukan menurut izin.

## Sejarah Rename: Buzzer → Engagement Team

**Wajib dibaca sebelum menyentuh modul ini.** Tim ini dulu bernama **Buzzer**; HR me-rename jabatannya jadi **Engagement Team**. Nama lama bertahan di kepala orang jauh lebih lama daripada di basis data.

- **Pencarian mengenali kedua nama.** `cocokAliasEngagement` (`engagement_alias.go`) mencocokkan kata kunci `engagement` **dan** `buzzer` dengan `Contains`, satu arah, tanpa mengubah data apa pun. Kalau kata kunci pencarian menunjuk modul ini, ia **tidak** dipakai sebagai penyaring isi tiket — sebab ia menunjuk *modul*, bukan isi, sehingga memakainya sebagai kata kunci justru mengosongkan hasil dan pembacanya menyimpulkan datanya hilang.
- Alias sengaja **tidak** memakai pencocokan awalan/kemiripan: `buzz` dan `engage` ditolak. Alias yang terlalu longgar membuat pencarian apa pun mengembalikan seluruh tiket engagement.
- **Nama lama masih hidup di luar modul ini**, dan itu bukan bug modul: template KPI produksi `Beauty Hacks / Buzzer` (termasuk satu template uji cacat, lihat [[HRIS - Otomasi Skor KPI]]), baris jabatan `Buzzer` di [[ADR - 0043 Peran Sistem Diturunkan dari Jabatan]], dan peta kepemilikan di [[Sales - ICC Account Manager Mapping]]. Pencarian di vault maupun di data yang hanya memakai satu dari dua nama akan **melewatkan separuh kenyataan**.
- ⚠️ **Penyaring kandidat penugasan TIDAK memakai nama jabatan** — dan sejak [[ADR - 0060 Cakupan Keterlihatan Tiket Engagement]] §4 (29 Agustus 2026) juga **tidak lagi memakai departemen pemanggil**. `daftarKandidatPengerja` (`engagement_assign.go`) kini menyaring `position_key ∈ KunciJabatanPengerja` (data di `engagement_settings`, seed produksi cuma `'engagement_team'`) **lintas departemen** — versi lama dokumen ini pernah menyatakan penyaringannya `department == departemen pemanggil`, itu sudah tidak akurat. Alasan menghindari nama jabatan tetap sama: rename `Buzzer` → `Engagement Team` menerbitkan `position_key` baru dan mengosongkan daftar **tanpa satu pun galat** bila disaring by-nama. Konsekuensi yang diterima sadar sekarang bergeser: bukan lagi "AS ikut muncul di kandidat" (itu sudah tak terjadi karena position_key sudah spesifik), melainkan alokasi OTOMATIS (round-robin, [[ADR - 0083 Alokasi Otomatis Round-Robin Menggantikan Penunjukan Manual AS]]) yang menyempitkan kandidat ke sedepartemen requester secara default — dua sumbu (kolam vs giliran) yang gampang tertukar, lihat ADR-0060 TBD.

## Konsumen Data

- [[Microservices - Employee Service]] — sumber KPI **`kinerja_engagement`** (`kpi_sumber_engagement.go`, grup `marketing`), menarik `GET /kpi/engagement` dari task-management. Empat metrik dari satu agregat, dipilih lewat `KPIAutoConfig.Metrik`:

| Metrik | Menjawab | Bentuk nilai | Penyebut |
|---|---|---|---|
| `speed` | *Early Engagement Speed* | menit `assigned_at` → `done_at`, per tiket | tiket `CLOSED` periode itu |
| `quantity` | *Engagement Quantity* | rasio `volume_realisasi/volume_target`, per tiket, boleh > 1 | tiket ber-target volume (`volume_terukur`) |
| `quality` | *Engagement Quality* | 1/0 per tiket, 1 = ditutup tanpa revisi | tiket `CLOSED` periode itu |
| `reporting` | *Reporting & Account Readiness* | 1/0 per tiket, 1 = punya lampiran bukti | tiket `CLOSED` periode itu |

⛔ **`reporting` TERSTRUKTUR SELALU NOL untuk siapa pun, permanen** (bukan bug, konsekuensi keputusan yang belum ditutup) — lihat ## Cacat yang Diketahui #7. Tak ada satu pun rute yang menulis `attachments` ke `engagement_tickets` sejak syarat buktinya dilonggarkan jadi opsional; kalau tiket tak pernah bisa punya lampiran, `len(t.Attachments) > 0` tak pernah `true`.

- **Penyebut keempatnya sama: tiket `CLOSED` pada periode itu**, dan periodenya dari `closed_at`, bukan `created_at`. `DONE_BY_TEAM` sengaja tak masuk — menghitungnya gagal berarti menghukum pengerja atas kelambatan pemohon. `CANCELLED` juga tidak: permintaan yang batal bukan pekerjaan yang gagal.
- **Tak ada satu pun angka target/bobot/ambang di sumbernya** — seluruhnya milik HR/SPV lewat template KPI, sejalan [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]]. Yang dikirim pengukuran mentah per tiket; yang mencacah lolos/tidak adalah reduksi.
- ⚠️ **Konsekuensi yang perlu diketahui HR** (tertulis di kode): (a) metrik `speed` mengukur *berapa lama menyelesaikan*, bukan *berapa cepat merespons* — pengerja yang langsung mengerjakan tiket berat tampak sama lambatnya dengan yang menunda; (b) metrik `quality` ikut turun bila pemohon menekan Revisi karena **brief-nya sendiri** berubah, bukan karena hasilnya buruk. Alasan revisi wajib diisi dan tersimpan, sehingga sengketanya bisa ditelusuri.
- ⚠️ **Gap terhadap [[HRIS - Matriks KPI per Departemen]]**: matriks itu masih mencatat keempat metrik Buzzer sebagai tak-bisa-otomatis. Yang diukur di sini **bukan** engagement di platform (like/komentar yang benar-benar tayang) melainkan **kepatuhan alur tiket**. Halangan aslinya — akun boosting adalah akun personal tanpa API — tetap ada. **TBD**: apakah HR menerima proksi ini sebagai pengganti, dan bagaimana template KPI produksi (yang bernama `Buzzer`) diselaraskan.

## Cacat yang Diketahui

Dari audit modul 2026-08-29 (task `t_14519b55`), **diverifikasi ulang ke kode 2026-09-09** — banyak yang sudah berubah sejak audit awal, dicatat di sini apa adanya (termasuk yang ternyata TIDAK seperti diklaim commit/ADR-nya).

**Sudah diperbaiki sejak audit awal:**

1. ✅ **Bukti pengerjaan dilonggarkan jadi opsional.** `selesaiDikerjakanHandler` (`engagement_handlers.go:767`) tidak lagi mewajibkan `attachments` — komentarnya eksplisit menyebut ini keputusan SPV, karena syarat lama membuat tiket mustahil ditandai selesai (tak ada rute yang bisa menulis `attachments`). Konsekuensinya: metrik KPI `reporting` (lihat ## Konsumen Data) kini **terstruktur permanen nol**, bukan cuma nol karena tiket tak bisa `CLOSED` — rute untuk mengisi `attachments` tetap tidak ada.
2. ✅ **Tab "Pekerjaan Saya" diperbaiki.** `pekerjaanSaya`, index `ix_pemegang`, dan `hitungWIP` kini menyaring/dibangun atas `assigned_to`, bukan `claimed_by`. Dikunci `engagement_regresi_test.go` (T-02).
3. ✅ **Keterlihatan tiket kini dibatasi departemen requester.** [[ADR - 0060 Cakupan Keterlihatan Tiket Engagement]] terimplementasi penuh (`engagement_visibility.go`): field `requester_department`, lima aturan OR (pembuat/pengerja/kolam pengerja/supervisor tercakup/admin), gerbang `POST /engagement/tickets` menolak `403` di luar departemen requester yang di-seed.

**Cacat BARU ditemukan+diperbaiki 2026-09-09** (testing manual, sebelum ada di produksi):

4. ⛔→✅ **Kolom "Pengerja" (dan seluruh layar yang menampilkan nama kandidat) menampilkan `employee_id` mentah** (`BIP-0099-10-24` alih-alih nama orang) — root cause BARU, bukan yang dicatat audit lama. `daftarKandidatPengerja` (`engagement_assign.go`) melakukan `$lookup` nama dari koleksi `system_authentication`, yang **tidak punya field `full_name` sama sekali** (`shared-library/models/employee/models.go`), sehingga `$ifNull` SELALU jatuh ke `employee_id` — bukan cacat "belum diisi" seperti audit lama duga, melainkan salah collection. Diperbaiki dengan mengarahkan lookup ke `personal_data` (pola yang sama dengan `fetchFullName` di `notify.go`), diekstrak jadi `daftarKandidatPengerjaPipeline` supaya bentuk query-nya teruji tanpa Mongo.
5. ⛔→✅ **FE form "Buat Request" masih menawarkan dropdown assign manual** padahal backend sudah mengabaikan total `assigned_to` sejak round-robin berlaku ([[ADR - 0083 Alokasi Otomatis Round-Robin Menggantikan Penunjukan Manual AS]], 1 September). AS memilih orang X, tiket jatuh ke orang Y hasil round-robin, **tanpa satu pun indikasi di layar**. Diperbaiki: dropdown diganti pratinjau read-only dari `GET /engagement/giliran-berikutnya`.

**Masih terbuka:**

6. ⚠️ **Notifikasi model lama TIDAK dibuang seperti diklaim ADR-0060 §6.** `anggotaSpaceEngagement`, `NotifEngagementOpen`/`NotifEngagementReleased`, dan komentar kepala berkas yang menjanjikan "menyapa SELURUH anggota space" (`engagement_notify.go`) semua masih ada di kode — dead code yang tak dibuang, bukan fitur yang jalan. Rincian di [[ADR - 0059 Penugasan Langsung Menggantikan Antrian Bersama]] (Consequences).
7. ⚠️ **KPI `reporting` (Berbukti) terstruktur selalu nol** — lihat butir 1. Bukan bug baru, tapi konsekuensi permanen dari keputusan melonggarkan syarat bukti tanpa menambah cara mengisinya.

**Cacat lain yang BELUM diverifikasi ulang** (dicatat audit 2026-08-29, statusnya sekarang tidak diketahui — jangan dipercaya tanpa Grep ulang): saringan prioritas/status di endpoint daftar; retry nomor tiket ganda; tiket lahir tanpa baris target; label riwayat memakai teks tombol alih-alih teks peristiwa.

⚠️ **Test hijau di modul ini menyesatkan untuk kelas cacat tertentu.** Suite `services/task-management` lolos jauh melebihi 45 subtest lama, tapi kelas "query Mongo menunjuk collection/field yang salah" (butir 4 di atas) tetap tak tertangkap unit test — lingkungan test paket ini memang tanpa Mongo asli (dicatat eksplisit di `engagement_giliran_test.go`). Yang bisa dan sudah dikunci: BENTUK pipeline (`engagement_assign_test.go`), bukan hasil eksekusinya. Penjaga notifikasi juga masih bolong: `semuaTipeNotifEngagement()` memuat satu tipe dua kali dan melewatkan satu tipe lain (lihat butir 6).

## Kendala

- **Tim flat tanpa lead.** Tak ada peran perantara yang bisa menyeimbangkan beban, memindahkan tiket macet, atau menerima eskalasi. Konsekuensinya: penugasan ulang jadi wewenang pemohon/admin, dan eskalasi menyapa pengerja+pemohon langsung.
- **Beban tak menyeimbangkan diri sendiri.** Pemohon yang selalu menunjuk orang yang sama akan menumpuk pekerjaan padanya, dan tak ada mekanisme yang menahannya — hanya dashboard yang membuatnya terlihat.
- **Akun boosting adalah akun personal tanpa API.** Sistem tak punya cara memverifikasi bahwa like/komentar benar-benar tayang; yang tercatat hanya klaim pengerja plus bukti yang ia lampirkan sendiri.

## Belum Diputuskan (TBD)

Sisa keputusan lingkup yang menunggu SPV; sampai diputuskan, **jangan** menuliskannya sebagai rancangan di dokumen mana pun.

- **Bukti pengerjaan**: syaratnya sudah dilonggarkan jadi opsional (## Cacat yang Diketahui #1), tapi rute untuk MENGISI `attachments` tak pernah ditambahkan — jadi metrik KPI `reporting` terstruktur nol permanen. TBD yang sebenarnya sekarang: apakah rute lampiran akan ditambahkan (menghidupkan metrik ini), atau metrik `reporting` dicabut/diganti dari katalog KPI karena tak pernah bisa terisi.
- ~~Batas keterlihatan tiket~~ — **SELESAI**, lihat [[ADR - 0060 Cakupan Keterlihatan Tiket Engagement]] (kodenya sudah ada, diverifikasi 2026-09-09).
- ~~Siapa menunjuk pengerja~~ — **SELESAI**, lihat [[ADR - 0083 Alokasi Otomatis Round-Robin Menggantikan Penunjukan Manual AS]]: server, bukan AS.
- **Apakah `CLOSED`/`CANCELLED` boleh disaring** di tab Tiket Tim, yang dimaksudkan untuk beban berjalan.
- ⚠️ **Notifikasi "tiket baru" ke seluruh space** — ADR-0060 §6 mengklaim ini **DIJAWAB 2026-08-29** (dead code dibuang), tapi diverifikasi 2026-09-09 kodenya (`anggotaSpaceEngagement`, dua tipe notifikasi) **masih ada**, cuma tak terpanggil. Bukan TBD desain lagi, tapi utang pembersihan kode yang belum dikerjakan — lihat ## Cacat yang Diketahui #6.
- **Batas WIP per anggota** — apakah memang direncanakan? `hitungWIP` ada tapi tak dipanggil.
- **Penyelarasan template KPI produksi** yang masih bernama `Buzzer` dengan sumber `kinerja_engagement`.

## Dokumen Terkait

- [[Microservices - Task Management Service]] — implementasi service (bagian *Modul Engagement Tim*)
- [[API - Task Management Service]] — daftar endpoint `/engagement/*` + `/kpi/engagement`
- [[ADR - 0058 Tiket Engagement Memakai Koleksi dan State Machine Sendiri]] · [[ADR - 0059 Penugasan Langsung Menggantikan Antrian Bersama]] · [[ADR - 0060 Cakupan Keterlihatan Tiket Engagement]] · [[ADR - 0083 Alokasi Otomatis Round-Robin Menggantikan Penunjukan Manual AS]]
- [[Microservices - Employee Service]] — sumber KPI `kinerja_engagement` · [[HRIS - Otomasi Skor KPI]] · [[HRIS - Matriks KPI per Departemen]]
- [[APP - Web ERP]] — layar Marketing › Engagement · [[Sales - Big Pictures]] · [[Sales - ICC Account Manager Mapping]]
- [[ADR - 0043 Peran Sistem Diturunkan dari Jabatan]] — jabatan `Buzzer` di peta peran sistem
