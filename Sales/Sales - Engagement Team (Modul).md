# Sales - Engagement Team (Modul)

## Deskripsi

*Modul **Engagement Tim** adalah alur tiket boosting media sosial: **Account Specialist** membuat permintaan (like/komentar/share/review pada sejumlah URL target), **menunjuk langsung** satu anggota tim Engagement yang mengerjakannya, lalu memverifikasi hasilnya. Tiket hidup di koleksi Mongo sendiri di dalam [[Microservices - Task Management Service]], terpisah dari tiket IT, dengan state machine dan nomor tiketnya sendiri. Angka penutupannya jadi sumber KPI `kinerja_engagement` di [[Microservices - Employee Service]].*

- **Status**: ⚠️ Implemented (ada catatan) — kode ada di `main` kedua repo (BE merge PR #1504 `feat/engagement-assign`, FE merge PR #1287), tetapi **audit 2026-08-29 menemukan 3 cacat yang membuat alurnya belum bisa dipakai utuh** (bukti pengerjaan tak bisa diunggah → tiket mustahil ditandai selesai; tab Pekerjaan Saya selalu kosong; keterlihatan tiket tak dibatasi departemen). Rinciannya di **## Cacat yang Diketahui**. **Belum diverifikasi lewat gateway** dev maupun prod.
- **Implementasi**: [[Microservices - Task Management Service]] (bagian *Modul Engagement Tim*) · kontrak endpoint di [[API - Task Management Service]]
- **Layar**: [[APP - Web ERP]] — menu **Marketing › Engagement** (`/marketing/engagement`)
- **Keputusan**: [[ADR - 0058 Tiket Engagement Memakai Koleksi dan State Machine Sendiri]] · [[ADR - 0059 Penugasan Langsung Menggantikan Antrian Bersama]]

## Latar Belakang

- Pekerjaan boosting selama ini diminta lewat kanal informal (chat), sehingga tak ada jejak siapa meminta apa, kapan tenggatnya, dan apakah hasilnya diterima. Tanpa jejak itu, tak ada dasar penilaian kinerja tim.
- [[HRIS - Matriks KPI per Departemen]] mencatat empat metrik posisi ini (*Early Engagement Speed*, *Engagement Quantity*, *Engagement Quality*, *Reporting & Account Readiness*) sebagai **"belum bisa otomatis — akun buzzer memakai akun personal, tidak ada integrasi API"**. Modul ini **tidak** menyelesaikan halangan itu; ia mengukur **proksi berbasis tiket** (kapan ditugaskan → kapan selesai, realisasi vs target volume, ada/tidaknya revisi, ada/tidaknya bukti). Lihat **## Konsumen Data** dan catatan gap-nya.
- Tim ini **dulu bernama "Buzzer"** dan di-rename HR jadi **"Engagement Team"**. Nama lama masih hidup di banyak tempat, dan itu jebakan nyata — lihat **## Sejarah Rename: Buzzer → Engagement Team**.

## Ruang Lingkup / Cakupan (business view)

### Siklus hidup satu permintaan

1. **Account Specialist membuat tiket**: client, campaign, platform, jenis pekerjaan, volume, deadline, prioritas, guideline/tone of voice/kata terlarang, plus **satu atau lebih baris target** (URL + jenis + volume target). Ia **wajib menunjuk pengerjanya** di formulir yang sama.
2. Sistem menerbitkan **nomor tiket** `ENG/YYYYMM/NNNN` (bulan menurut WIB) dan mengirim notifikasi ke orang yang ditunjuk.
3. **Pengerja** menandai *mulai* (opsional) lalu *sudah dikerjakan* — dengan **bukti pengerjaan wajib** (screenshot atau tautan).
4. **Account Specialist memverifikasi**: *tutup* bila sesuai, atau *minta revisi* (wajib alasan) yang mengembalikan tiket ke **pengerja yang sama**.
5. Bila pengerjanya berhalangan, **pembuat tiket atau admin/supervisor menugaskan ulang** (wajib alasan). Pembatalan juga milik keduanya, wajib alasan.

Status: `OPEN` → `IN_PROGRESS` → `DONE_BY_TEAM` → `CLOSED`, dengan jalur revisi `DONE_BY_TEAM` → `IN_PROGRESS`, jalur tugas-ulang `IN_PROGRESS` → `OPEN`, dan `CANCELLED` dari `OPEN`/`IN_PROGRESS`. Tabel transisi + peran yang berwenang ada di [[Microservices - Task Management Service]].

### Yang membedakannya dari tiket IT di service yang sama

| Hal | Tiket IT (`tasks`) | Tiket Engagement (`engagement_tickets`) |
|---|---|---|
| Stage | dinamis per space, wajib memuat `Request`/`Todo`/`Done` | lima status **tetap** di kode |
| Triase | supervisor menyetujui/menolak permintaan masuk | **tak ada triase** — tiket lahir sudah tertuju ke orang |
| Penugasan | supervisor/admin space saat approve (bisa round-robin) | **pemohon** menunjuk saat membuat |
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

⚠️ **Menu tak menyaring siapa pun.** Ketiga persona di atas memakai izin menu yang sama (`IZIN_MARKETING.po`, sama dengan "PO Barang Jadi" dan "Target Marketing"), dan halamannya menampilkan tab berbeda menurut peran orang pada tiap tiket — bukan menurut izin.

## Sejarah Rename: Buzzer → Engagement Team

**Wajib dibaca sebelum menyentuh modul ini.** Tim ini dulu bernama **Buzzer**; HR me-rename jabatannya jadi **Engagement Team**. Nama lama bertahan di kepala orang jauh lebih lama daripada di basis data.

- **Pencarian mengenali kedua nama.** `cocokAliasEngagement` (`engagement_alias.go`) mencocokkan kata kunci `engagement` **dan** `buzzer` dengan `Contains`, satu arah, tanpa mengubah data apa pun. Kalau kata kunci pencarian menunjuk modul ini, ia **tidak** dipakai sebagai penyaring isi tiket — sebab ia menunjuk *modul*, bukan isi, sehingga memakainya sebagai kata kunci justru mengosongkan hasil dan pembacanya menyimpulkan datanya hilang.
- Alias sengaja **tidak** memakai pencocokan awalan/kemiripan: `buzz` dan `engage` ditolak. Alias yang terlalu longgar membuat pencarian apa pun mengembalikan seluruh tiket engagement.
- **Nama lama masih hidup di luar modul ini**, dan itu bukan bug modul: template KPI produksi `Beauty Hacks / Buzzer` (termasuk satu template uji cacat, lihat [[HRIS - Otomasi Skor KPI]]), baris jabatan `Buzzer` di [[ADR - 0043 Peran Sistem Diturunkan dari Jabatan]], dan peta kepemilikan di [[Sales - ICC Account Manager Mapping]]. Pencarian di vault maupun di data yang hanya memakai satu dari dua nama akan **melewatkan separuh kenyataan**.
- ⚠️ **Penyaring kandidat penugasan TIDAK memakai nama jabatan.** Ini kebalikan dari dugaan yang wajar. `daftarKandidatPengerja` (`engagement_assign.go`) menyaring **`department` == departemen pemanggil**, dan komentar di kodenya menyebut alasannya eksplisit: menyaring `position == "Engagement Team"` akan terikat pada nama jabatan yang **baru saja di-rename**, dan rename berikutnya mengosongkan daftar itu **tanpa satu pun galat**. Konsekuensi yang diterima sadar: daftar kandidat memuat orang yang bukan pengerja engagement (Account Specialist sendiri ikut muncul).

## Konsumen Data

- [[Microservices - Employee Service]] — sumber KPI **`kinerja_engagement`** (`kpi_sumber_engagement.go`, grup `marketing`), menarik `GET /kpi/engagement` dari task-management. Empat metrik dari satu agregat, dipilih lewat `KPIAutoConfig.Metrik`:

| Metrik | Menjawab | Bentuk nilai | Penyebut |
|---|---|---|---|
| `speed` | *Early Engagement Speed* | menit `assigned_at` → `done_at`, per tiket | tiket `CLOSED` periode itu |
| `quantity` | *Engagement Quantity* | rasio `volume_realisasi/volume_target`, per tiket, boleh > 1 | tiket ber-target volume (`volume_terukur`) |
| `quality` | *Engagement Quality* | 1/0 per tiket, 1 = ditutup tanpa revisi | tiket `CLOSED` periode itu |
| `reporting` | *Reporting & Account Readiness* | 1/0 per tiket, 1 = punya lampiran bukti | tiket `CLOSED` periode itu |

- **Penyebut keempatnya sama: tiket `CLOSED` pada periode itu**, dan periodenya dari `closed_at`, bukan `created_at`. `DONE_BY_TEAM` sengaja tak masuk — menghitungnya gagal berarti menghukum pengerja atas kelambatan pemohon. `CANCELLED` juga tidak: permintaan yang batal bukan pekerjaan yang gagal.
- **Tak ada satu pun angka target/bobot/ambang di sumbernya** — seluruhnya milik HR/SPV lewat template KPI, sejalan [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]]. Yang dikirim pengukuran mentah per tiket; yang mencacah lolos/tidak adalah reduksi.
- ⚠️ **Konsekuensi yang perlu diketahui HR** (tertulis di kode): (a) metrik `speed` mengukur *berapa lama menyelesaikan*, bukan *berapa cepat merespons* — pengerja yang langsung mengerjakan tiket berat tampak sama lambatnya dengan yang menunda; (b) metrik `quality` ikut turun bila pemohon menekan Revisi karena **brief-nya sendiri** berubah, bukan karena hasilnya buruk. Alasan revisi wajib diisi dan tersimpan, sehingga sengketanya bisa ditelusuri.
- ⚠️ **Gap terhadap [[HRIS - Matriks KPI per Departemen]]**: matriks itu masih mencatat keempat metrik Buzzer sebagai tak-bisa-otomatis. Yang diukur di sini **bukan** engagement di platform (like/komentar yang benar-benar tayang) melainkan **kepatuhan alur tiket**. Halangan aslinya — akun boosting adalah akun personal tanpa API — tetap ada. **TBD**: apakah HR menerima proksi ini sebagai pengganti, dan bagaimana template KPI produksi (yang bernama `Buzzer`) diselaraskan.

## Cacat yang Diketahui

Dari audit modul 2026-08-29 (task `t_14519b55`). Dicatat di sini supaya dokumen ini **tidak** membaca seolah modulnya beres. Setiap butir grounded ke berkas:baris; usulan perbaikannya ada di laporan audit, bukan di sini.

**Menghalangi pemakaian (blocker):**

1. ⛔ **Tiket mustahil ditandai selesai.** `selesaiDikerjakanHandler` (`engagement_handlers.go:588`) menolak `400` bila `attachments` kosong, tetapi **tak ada satu pun rute atau kode yang menulis `attachments` ke `engagement_tickets`** — tak ada `POST /engagement/tickets/:id/attachments` maupun `/links`, dan rute lampiran yang ada beroperasi atas koleksi `tasks`. Sisi FE mengonfirmasi: tombol "Sudah Dikerjakan" permanen mati. Akibat berantai: `DONE_BY_TEAM` tak pernah tercapai → `CLOSED` tak pernah tercapai → **keempat metrik KPI selalu nol untuk semua orang**.
2. ⛔ **Tab "Pekerjaan Saya" selalu kosong.** `pekerjaanSaya` (`engagement_handlers.go:269`) menyaring `claimed_by`, field yang **tidak ada di model** dan tak pernah ditulis; yang benar `assigned_to`. Balasannya `200` berisi daftar kosong — tak ada galat, dan pengerja menyimpulkan tak ada tiket untuknya. Sisa peninggalan model antrian bersama; jejak yang sama ada di index `ix_pemegang` (`engagement_repo.go:66`) dan `hitungWIP` (`:140`, tak dipanggil dari mana pun).
3. ⛔ **Kolom "Pengerja" menampilkan `employee_id` mentah.** `assigned_name` tak pernah diisi saat membuat tiket (`engagement_handlers.go:149-170`) dan justru di-`$unset` saat menugaskan ulang (`:544`), padahal `requester_name` diisi. Datanya tersedia (kandidat penugasan sudah membawa `full_name`), hanya tidak disimpan.

**Risiko keterlihatan data:**

4. ⚠️ **Antrian dan dashboard tidak menyaring departemen sama sekali.** Komentar `antrianEngagement` (`engagement_handlers.go:209-213`) menyatakan "seluruh tiket aktif satu departemen", tetapi querynya hanya menyaring status; `dashboardEngagement` sama. Gerbangnya cuma `requireRoles("staff","supervisor","admin")` — yaitu **setiap pemakai ERP**. Akibatnya siapa pun yang bisa login melihat seluruh tiket lintas departemen berikut `client`, `campaign`, `guideline`, `tone_of_voice`, `kata_terlarang`, dan `target_url` kampanye. `detailTiket`/`riwayatTiket` juga tak memeriksa keterkaitan pemanggil dengan tiket. Bandingkan: `daftarKandidatPengerja` menyaring departemen, dan muatan `/kpi/engagement` sengaja disempitkan justru untuk alasan ini — standarnya sudah ada dan tidak diterapkan di jalur pemakai.

**Cacat lain yang tercatat:** saringan prioritas diabaikan di ketiga endpoint daftar (saringan status juga diabaikan di tab Tiket Tim) meski FE menawarkannya; nomor tiket ganda dijanjikan di-retry tetapi pemanggilnya tidak me-retry sehingga permintaan bersamaan berujung `500`; tiket bisa lahir tanpa baris target (item disisipkan setelah tiket, tanpa rollback, dan baris ber-URL kosong dilewati diam-diam); dua tipe notifikasi (`engagement_ticket_open`, `engagement_released`) terdaftar lengkap sampai FCM tetapi **tak pernah dikirim**; label riwayat memakai teks tombol ("Mulai Kerjakan") alih-alih teks peristiwa ("Mulai dikerjakan").

⚠️ **Test hijau di modul ini menyesatkan.** `go test ./...` di `services/task-management` lolos (45 subtest engagement), tetapi seluruhnya berhenti sebelum menyentuh Mongo, sehingga kelas cacat "query menunjuk field yang tak pernah ditulis" — yaitu cacat nomor 2 — mustahil tertangkap. Penjaga notifikasinya sendiri bolong: daftar tipe yang diiterasi test memuat satu tipe dua kali dan **melewatkan** satu tipe lain.

## Kendala

- **Tim flat tanpa lead.** Tak ada peran perantara yang bisa menyeimbangkan beban, memindahkan tiket macet, atau menerima eskalasi. Konsekuensinya: penugasan ulang jadi wewenang pemohon/admin, dan eskalasi menyapa pengerja+pemohon langsung.
- **Beban tak menyeimbangkan diri sendiri.** Pemohon yang selalu menunjuk orang yang sama akan menumpuk pekerjaan padanya, dan tak ada mekanisme yang menahannya — hanya dashboard yang membuatnya terlihat.
- **Akun boosting adalah akun personal tanpa API.** Sistem tak punya cara memverifikasi bahwa like/komentar benar-benar tayang; yang tercatat hanya klaim pengerja plus bukti yang ia lampirkan sendiri.

## Belum Diputuskan (TBD)

Enam keputusan lingkup ini menunggu SPV; sampai diputuskan, **jangan** menuliskannya sebagai rancangan di dokumen mana pun.

- **Bukti pengerjaan**: tambah rute lampiran engagement, atau longgarkan syarat buktinya jadi opsional? Yang kedua mengubah kontrak metrik `reporting` dan menuntut ADR sendiri. Juga TBD: batas ukuran/jumlah lampiran, dan apakah pemohon boleh melampirkan referensi saat membuat tiket.
- **Batas keterlihatan tiket** (per-departemen / per-space / global-untuk-supervisor). `EngagementTicket` belum menyimpan `department`, jadi apa pun pilihannya menuntut penambahan field + migrasi. Keputusan ini layak jadi ADR tersendiri begitu diambil.
- **Apakah `CLOSED`/`CANCELLED` boleh disaring** di tab Tiket Tim, yang dimaksudkan untuk beban berjalan.
- **Notifikasi "tiket baru" ke seluruh space** — fitur yang belum jadi, atau dead code yang harus dibuang? Kodenya terdaftar sampai FCM tapi tak pernah dikirim.
- **Batas WIP per anggota** — apakah memang direncanakan? `hitungWIP` ada tapi tak dipanggil.
- **Penyelarasan template KPI produksi** yang masih bernama `Buzzer` dengan sumber `kinerja_engagement`.

## Dokumen Terkait

- [[Microservices - Task Management Service]] — implementasi service (bagian *Modul Engagement Tim*)
- [[API - Task Management Service]] — daftar endpoint `/engagement/*` + `/kpi/engagement`
- [[ADR - 0058 Tiket Engagement Memakai Koleksi dan State Machine Sendiri]] · [[ADR - 0059 Penugasan Langsung Menggantikan Antrian Bersama]]
- [[Microservices - Employee Service]] — sumber KPI `kinerja_engagement` · [[HRIS - Otomasi Skor KPI]] · [[HRIS - Matriks KPI per Departemen]]
- [[APP - Web ERP]] — layar Marketing › Engagement · [[Sales - Big Pictures]] · [[Sales - ICC Account Manager Mapping]]
- [[ADR - 0043 Peran Sistem Diturunkan dari Jabatan]] — jabatan `Buzzer` di peta peran sistem
