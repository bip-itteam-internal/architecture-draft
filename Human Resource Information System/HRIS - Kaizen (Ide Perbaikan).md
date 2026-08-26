# HRIS - Kaizen (Ide Perbaikan)

## Deskripsi

*Program pengumpulan ide perbaikan bulanan. Karyawan pada sasaran tertentu wajib mengirim sejumlah ide tiap bulan, jumlahnya diatur HR (satu angka bawaan untuk semua, boleh ditimpa per departemen). Ide masuk ke antrean komite Kaizen terpusat yang memutuskan diterima atau ditolak, lalu menandai mana yang benar-benar diterapkan. Ide yang disetujui tampil di papan yang bisa dibaca seluruh karyawan.*

- **Status**: ⚠️ **SELURUH tahap LIVE di dev DAN prod** sejak 2026-08-06, teruji end-to-end di dev. Backend, Web ERP, dan MyBharata semuanya sudah merge; lampiran berkas ikut menyusul dan terbukti bekerja. Yang tersisa bukan pekerjaan kode: **HR menetapkan sasaran/kuota/komite/tanggal mulai**, dan **MyBharata belum dirilis ke store**. Ringkasan per tahap di tabel di bawah.
- ✅ **Pengingat kuota TERBUKTI SAMPAI** setelah PR [#1044](https://github.com/bip-itteam-internal/bip-erp/pull/1044). Sebelumnya kategori `kaizen-reminder` dan `kaizen-decided` tak terdaftar di `shared-library` sehingga notification-service menolaknya `400` dan notifnya hilang tanpa jejak — persis kegagalan yang sudah diperingatkan di rencana tahap 5 di bawah, dan yang sudah pernah terjadi saat `form-published` lahir. Prosedur deploy yang mencegahnya terulang: [[RUN - Deploy Microservices bip-erp]] §3a.
- **Belum ada program kaizen SUNGGUHAN di prod**, jadi seluruh perilaku barunya masih **inert** di sana: cron pengingat tak punya apa pun untuk dikirim, dan menu Komite Kaizen menampilkan "tidak ada program untuk Anda tinjau" — jawaban yang memang benar. Program baru bisa dinyalakan setelah HR menetapkan sasaran, kuota, komite, dan tanggal mulai (lihat TBD).
- ⚠️ **Koreksi 2026-08-26**: pernyataan lama "belum ada satu pun form kaizen dibuat di prod" **sudah tidak akurat**. Diukur langsung ke `form_builder_db.forms` prod: **12 form total, 2 bertipe `kaizen`**. Keduanya jelas form uji milik Tech Development dan ber-status `closed` — `iiiii` (10 Agu 2026) dan `Kaizen` (23 Agu 2026), masing-masing cuma satu field `long_text`, dan yang pertama bahkan punya `quota_by_department` berisi departemen bernama `"2"`. Kesimpulan operasionalnya tak berubah (tak ada program aktif), tapi angkanya bukan nol lagi, dan verifikasi apa pun yang mematok "nol form kaizen" akan hijau untuk keadaan yang salah.
- ✅ **Alur inti TERUJI end-to-end di dev 2026-08-06** lewat gateway, dengan Mongo dan employee-service hidup. Lihat bagian tersendiri di bawah.
- ✅ **Prod lengkap sejak 2026-08-06**: #1016, #1018, dan [#1019](https://github.com/bip-itteam-internal/bip-erp/pull/1019) semuanya sudah naik (`23e8914a`). Diverifikasi probe biner dengan kontrol positif dan negatif, ditambah probe perilaku jalur galat. **Belum ada satu pun form kaizen dibuat di prod** — programnya baru bisa dinyalakan setelah HR menetapkan sasaran, kuota, dan komitenya.
- **Rumah kode yang dipilih**: [[Microservices - Form Builder Service]], sebagai **tipe form tersendiri** (`form_type: "kaizen"`; kelima saat ditambahkan, sebelum `request` dihapus). Bukan service baru, bukan space di [[Microservices - Task Management Service]].
- Rancangan lengkap: `docs/superpowers/specs/2026-08-06-kaizen-pengumpulan-ide-design.md`; rencana per tahap: `docs/superpowers/plans/2026-08-06-kaizen-pengumpulan-ide.md`. Keduanya di root workspace, bukan di vault.

> [!warning] Deploy ini tidak menyalakan program Kaizen bagi siapa pun
> Seluruh perilaku baru digerbang `form_type: "kaizen"`, dan belum ada satu pun form kaizen di database mana pun. Yang berpotensi menyentuh form berjalan hanyalah pekerjaan **tahap 1** (snapshot periode jadi penopang beban).
>
> **Diperiksa langsung ke database prod sebelum deploy 2026-08-06**: 4 form, **0 berulang**, **0 published**, 142 jawaban, 0 dokumen periode. Jadi tahap 1 pun inert di prod, karena tak ada satu pun form berulang yang perilakunya bisa berubah. Yang benar-benar berubah bagi pemakai prod hanyalah perbaikan 502 dari [#1018](https://github.com/bip-itteam-internal/bip-erp/pull/1018).
>
> Di lingkungan yang PUNYA form berulang, yang paling perlu diperhatikan setelah deploy bukan Kaizen melainkan form berulang yang sudah ada: pastikan pengisian dan analisanya tidak berubah artinya.

## Apa yang Sudah Ada di Kode

Ketiganya di `services/form-builder`, seluruhnya backend.

**Tahap 1, snapshot periode jadi penopang beban.** Memperbaiki cacat yang sudah hidup di semua form berulang, bukan cuma Kaizen: `FormPeriod.Fields` dulu ditulis tapi tak pernah dibaca. Kini menyajikan, memvalidasi, dan **membaca** (analisa, daftar jawaban, export ber-`?period=`) semuanya memakai snapshot periode, baru sesudah itu kunci `409` susunan pertanyaan dilonggarkan untuk form berulang. Urutan itu tak boleh dibalik; jalur baca sempat terlewat dan ketahuan saat review.

**Tahap 2, tipe `kaizen` dan kuota.** Tipe terikat dua arah dengan `settings.kaizen`, wajib berulang bulanan, `single_response` dan sasaran penilaian dilarang. Kuota global dengan override per departemen, dan kuota adalah **lantai bukan langit-langit** (ide melebihi kuota tetap diterima; entri berkuota `0` berarti dikecualikan tapi tetap boleh mengirim). Potret peserta diambil cron **tiap periode** sebagai penyebut papan kepatuhan. Satu program kaizen aktif per `company_id`.

**Tahap 3, keputusan komite.** Belum ditinjau → Diterima atau Ditolak → Diterapkan; menolak wajib beralasan, status terminal tak bisa diubah. Ditambah antrean komite, papan kepatuhan, dan export CSV.

### Penyimpangan dari rancangan, semuanya disengaja

| Yang direncanakan | Yang dikerjakan | Sebab |
|---|---|---|
| Rute komite di `/forms/:id/...` | Prefix **`/kaizen/*`** dengan gerbang per-form | Grup `/forms` digerbang `requireFormManager` yang menuntut peran pengelola dan departemen aktif; anggota komite bisa staf biasa dari departemen mana pun, jadi mereka akan kena `403` sebelum handler-nya jalan |
| `implemented_at` opsional | **Wajib diisi**, tidak default hari ini | Skor KPI menghitung ide yang diterapkan per periode; komite yang menandai terlambat akan menyetorkan angka ke bulan yang salah |
| (tak disebut) | Seluruh permukaan komite dikunci **`CompanyID`**, bukan `EffectiveCompanyID` | Memutuskan nasib ide adalah menulis, dan lingkup baca lintas perusahaan milik admin pusat tak boleh terbawa. Antrean dan papan ikut dikunci supaya yang dilihat dan yang bisa ditindak selalu sama |
| (tak disebut) | `settings.kaizen` **absen berarti jangan diubah** | `PATCH` berperilaku ganti-seluruhnya; tanpa aturan ini satu kiriman tanpa blok kaizen mengubah program yang masih draft jadi survei biasa dan membuang kuota berikut daftar komite, tanpa galat. Konsekuensinya **tipe kaizen tak bisa diubah lewat `PATCH`** |
| (tak disebut) | Periode yang dokumennya belum ada dianggap **potret parsial** | "Nol peserta" terbaca seolah tak seorang pun diwajibkan, padahal yang terjadi cuma cron belum sempat jalan |
| Aksi massal | Dibatasi **200** dan melapor **per id** | Menggagalkan 200 ide karena satu yang keburu diputuskan orang lain membuat komite mengulang pekerjaan yang sudah hampir selesai |

### Hasil uji end-to-end di dev (2026-08-06)

Dijalankan lewat gateway dev dengan akun nyata, sasaran dibatasi satu orang supaya tidak mengirim notifikasi ke karyawan lain, dan seluruh data ujinya dihapus setelah selesai.

| Langkah | Hasil |
|---|---|
| Buat form kaizen berulang bulanan | id terbentuk, `recurrence` tersimpan |
| Terbitkan | `published`, periode `2026-08` terbentuk sendiri |
| `GET /me/forms` | blok kaizen tampil: kuota 2, terkirim 0 |
| Kirim ide ke-1 | terkirim 1, **terpenuhi false** |
| Kirim ide ke-2 | terkirim 2, **terpenuhi true**, form ditandai selesai |
| Antrean komite | 2 ide, membawa `fields` snapshot periode |
| 8 transisi keputusan | 8 dari 8 sesuai aturan, termasuk dua `409` |
| Papan kepatuhan | peserta 1, terpenuhi 1, total ide 2, `partial=false`, rate 100 |
| Export CSV | `200`, kolom benar, tanpa header parsial |
| Saringan status antrean | `pending` 0, `rejected` 1, `implemented` 1 |

**Tiga hal yang sebelumnya ditandai paling rawan, semuanya terbukti bekerja:**

1. **Potret peserta dari cron.** Papan menampilkan nama dan jabatan karyawan, dan data itu hanya bisa datang dari [[Microservices - Employee Service]] — jadi panggilan tanpa `fiber.Ctx` dengan header `BIP-Company-ID` dipasang manual memang berhasil.
2. **Penjaga balapan keputusan.** Menerima ide yang sudah diterima dibalas `409`, mengubah ide yang sudah diterapkan juga `409`. Keduanya lewat `MatchedCount` dari driver Mongo, bukan fungsi murni.
3. **Agregasi hitungan ide per orang**, yang jadi pembilang papan kepatuhan.

Papan ide publik, pengingat berjenjang, setoran KPI, dan permukaan karyawan dibangun **setelah** uji ini, jadi diuji terpisah — lihat bagian berikut.

### Hasil uji end-to-end tahap 5 sampai 7 di dev (2026-08-06)

Dijalankan lewat gateway dev dengan Mongo dan employee-service hidup, sasaran dibatasi satu orang, dan seluruh data ujinya dihapus lalu diverifikasi bersih setelah selesai.

| Langkah | Hasil |
|---|---|
| `GET /me/kaizen` sebelum ada program | `has_program:false`, hanya field itu |
| Buat + terbitkan form kaizen berulang | periode `2026-08` terbentuk sendiri |
| `GET /me/kaizen` sesudah terbit | membawa `blocks_attendance` + `gate_end_date` (tahap #1039) |
| Kuota | 0 → 1 → 2; `fulfilled` berbalik tepat di ide kedua |
| `GET /me/kaizen/ideas` | terbaru dulu, membawa `fields` bahkan saat riwayat kosong |
| `form_type` di `GET /me/forms` | `kaizen` untuk program ini, `survey` untuk form lain |
| Tolak tanpa alasan | `400` |
| Putuskan ulang status terminal | `409` |
| **Notifikasi `kaizen-decided`** | **sampai** — kotak masuk 71 → 72, judul "Ide Kaizen Anda sudah diterapkan" |
| Papan ide | ide diterapkan tampil; field `biaya` **tersembunyi** sesuai `board_hidden_fields` |
| `GET /internal/kaizen/metrics` | `submitted:2, accepted:0, implemented:1` |

**Percobaan pertama notifikasi GAGAL total**, empat menit setelah PR #1044 merge — deploy dev belum mendarat. Percobaan ulang setelah deploy sampai berhasil. Itu sekaligus bukti langsung bahwa notification-service wajib ikut naik, dan alasan prosedurnya kini tertulis di [[RUN - Deploy Microservices bip-erp]] §3a.

### Verifikasi deploy prod (2026-08-06)

form-builder, notification-service, dan erp-frontend di-deploy manual (`--no-deps`). Verifikasinya butuh empat percobaan karena tiga yang pertama **tidak membedakan apa pun**, dan kontrol negatif yang menangkapnya:

1. Grep biner di path yang salah → `0` berarti "berkas tak ada", bukan "tidak cocok".
2. Probe lewat gateway publik → rute karangan pun dibalas `401`; gateway menolak sebelum meneruskan.
3. Probe langsung ke service tanpa header → semua `401` termasuk `/health`, karena ada gateway-key di dalam service.
4. Probe dengan gateway key **dan** identitas karyawan → akhirnya membedakan.

Hasil yang sah: rute karangan `404`, `/health` `200`, dan keempat rute Kaizen `200` dengan isi JSON yang benar termasuk `/me/kaizen/committee` → `{"is_committee":false}`. Untuk frontend, probe HTTP tak berguna (semua `307` ke login), jadi buktinya diambil dari artefak build: rute `(main)/hris/kaizen` ada, label "Komite Kaizen" ada di bundle, dan string karangan **0 berkas**.

### Diketahui, belum diperbaiki

- Menandai ide "diterapkan" padahal belum pernah diterima dibalas `400`, seharusnya `409`. Tak ada data yang rusak.
- `blocks_attendance` di `GET /me/forms` memakai penilai gerbang berbasis tanggal statis, sedangkan gerbang sesungguhnya memakai jendela periode. Temuan lama di luar lingkup Kaizen, laten sampai [[Microservices - Attendance Service]] naik.

## Latar Belakang

Ketiadaan modul Kaizen adalah lubang yang sudah terukur, bukan dugaan:

- [[HRIS - Otomasi Skor KPI]] mencatat **16 metrik KPI lintas departemen tidak punya sumber data** karena tidak ada modul Kaizen atau ide inovasi. Diverifikasi lewat pencarian `kaizen` dan `inovasi` di seluruh `services/` dan `shared-library/`: nol hasil.
- [[HRIS - Matriks KPI per Departemen]] memuat metrik Kaizen di Customer Service, Buzzer, Finance (AR, cost control, accounting, tax), Produksi, QC, sampai seluruh posisi developer.
- Targetnya **tidak seragam**. Mayoritas kuartalan ("minimal 5 ide inovasi baru per kuartal") dengan turunan bulanan ("minimal 2 ide terdaftar per bulan"), sebagian murni bulanan ("Jumlah Inovasi All Divisi 7/Bulan"), dan sebagian berbunyi level tim, bukan per orang.
- Redaksi yang paling sering muncul adalah "jumlah inisiatif perbaikan yang **diterapkan**", bukan jumlah ide yang masuk.

[[HRIS - Key Performance Index]] sudah berperiode `YYYY-MM`, sehingga cadence bulanan program ini cocok dengan yang sudah ada.

Butir 11 rencana bertahap di [[HRIS - Otomasi Skor KPI]] dulu menyebut kandidat implementasi paling hemat adalah space khusus di [[Microservices - Task Management Service]]. **Kandidat itu gugur setelah diperiksa ke kode**, alasannya di bawah.

## Persona / Pengguna

| Persona | Peran & Divisi | Akses/RBAC | Device |
|---|---|---|---|
| Karyawan pengaju | Departemen yang masuk `audience` form | Terautentikasi, tanpa syarat peran | Web, menyusul Mobile |
| Anggota komite Kaizen | Lintas departemen, ditunjuk HR | Terdaftar di `settings.kaizen.committee_employee_ids` | Web |
| Pengelola form (HR) | Human Resource | Tingkat peran pengelola + departemen aktif, lewat `requireFormManager` | Web |
| Pembaca papan ide | Semua karyawan | Terautentikasi | Web, menyusul Mobile |

- **Tujuan** — karyawan: memenuhi kewajiban bulanan sekaligus menyampaikan perbaikan yang dia lihat sendiri di lapangan. Komite: memilah ide yang layak diterapkan. HR: mengatur besaran kewajiban dan membaca kepatuhan per departemen.
- **Pain point** — sebelum ini tidak ada tempat mencatat ide perbaikan sama sekali, sehingga metrik KPI Kaizen dinilai manual tanpa bukti, dan ide yang disampaikan lisan hilang tanpa jejak.
- **Aksi utama** — karyawan: buka form Kaizen bulan berjalan, kirim ide. Komite: buka antrean, putuskan, tandai yang diterapkan. HR: atur kuota dan sasaran, baca papan kepatuhan.

## Keputusan Rancangan

| Pertanyaan | Keputusan |
|---|---|
| Sejauh apa siklus ide dilacak | Sampai **Diterapkan** |
| Siapa peninjau | **Komite Kaizen terpusat** (bawaan) — sejak [[ADR - 0054 Peninjau Ide Kaizen Bisa Atasan Departemen, Bukan Hanya Komite Terpusat]] bisa juga **atasan departemen pengaju**, dipilih per program lewat `settings.kaizen.reviewer_mode` |
| Kuota dihitung dari | Ide yang **diajukan** |
| Ruang lingkup pengaturan kuota | **Global + override per departemen** |
| Konsekuensi tidak memenuhi | Pengingat berjenjang + papan kepatuhan, dan masuk skor KPI. **Bukan** blokir presensi |
| Kedalaman isi form | **Standar**, 11 field |
| Kanal pengisian | **Web dulu**, [[APP - MyBharata]] menyusul |
| Visibilitas | Terbuka **setelah disetujui** |
| Jumlah form Kaizen | **Satu form aktif per `company_id`** |
| Lampiran | Sekalian bangun **upload file** di Form Builder (berlaku semua tipe form) |
| Gerbang presensi | Tersedia, default mati, tidak dilarang |

### Mode peninjau: komite atau atasan departemen

Sejak [[ADR - 0054 Peninjau Ide Kaizen Bisa Atasan Departemen, Bukan Hanya Komite Terpusat]], "siapa peninjau" dipilih per program lewat `settings.kaizen.reviewer_mode`. Bawaannya `committee`, jadi seluruh uraian di bawah tetap berlaku apa adanya untuk program yang tak menyentuh saklar ini.

Pemicunya form manual HR **"BERITA ACARA INOVASI"** yang memakai kolom "Catatan Evaluasi **Atasan**". Yang perlu diingat saat membaca sisa dokumen ini:

- **"Atasan" di sini berarti supervisor DEPARTEMEN, bukan atasan langsung per orang.** `work_data.supervisor_id` kosong pada **129 dari 207** karyawan prod (2026-08-26), jadi menggerbangnya di sana akan membangun antrean yatim untuk 62% orang — dan senyap, karena kepatuhan dihitung dari ide yang diajukan.
- Wewenangnya datang dari izin **`formbuilder.kaizen.review`** yang dipasang HR ke JABATAN, bukan dari `is_supervisor` (yang diturunkan frontend dari nama jabatan dan karena itu rapuh).
- Pada mode ini `committee_employee_ids` **wajib kosong**, dan **tak seorang pun boleh memutuskan idenya sendiri**.
- ⚠️ **Programnya tidak berfungsi sampai paket haknya dipasang**, dan tak ada gerbang yang mencegah penerbitan tanpa peninjau. Penggantinya: papan kepatuhan melaporkan `menganggur`, yaitu ide yang belum diputuskan siapa pun lebih dari 14 hari.

### Kenapa bukan space di Task Management

Jawaban pertanyaan per tipe di [[Microservices - Task Management Service]] **tidak disimpan sebagai data**. Klien merangkainya jadi markdown lalu mengirimnya sebagai `description` tugas, dan konsekuensinya sudah tertulis di dokumen itu sendiri: jawaban tidak bisa difilter atau dilaporkan per pertanyaan. Padahal laporan per kategori dan hitungan kuota per periode justru inti fitur ini. Tambahan: RBAC-nya per divisi, sedangkan komite di sini terpusat.

### Kenapa Form Builder, dan apa harganya

Yang sudah jadi di sana dan langsung terpakai: form berulang bulanan berikut snapshot pertanyaan per periode, sasaran `audience` tiga bentuk, analitik, export CSV, notifikasi terbit, dan pengisian di [[APP - MyBharata]].

Harganya, dan ini dicatat supaya dijalani sadar:

1. Service itu menyentuh **jalur clock-in** lewat `GET /internal/compliance`, jadi tiap perubahan berpotensi mengenai presensi.
2. Dokumen [[Microservices - Form Builder Service]] menyatakan "form approval yang sudah matang JANGAN dimigrasikan ke sini". Rancangan ini menambahkan alur keputusan, jadi pernyataan itu harus diberi pengecualian eksplisit untuk tipe `kaizen`, bukan dibiarkan bertentangan dengan kode.
3. `settings.single_response` hanya boolean, bukan kuota N, dan penyebut tingkat pengisian untuk sasaran `all`/`departments` masih diisi manual lewat `audience.estimated_size`. Keduanya ditutup rancangan ini.

## Prasyarat di Kode yang Harus Dibereskan Dulu

> [!warning] Snapshot periode ditulis tapi tidak pernah dibaca
> `FormPeriod.Fields` dibuat `ensurePeriod` dan didokumentasikan sebagai salinan beku pertanyaan per periode, dengan janji "pemilik form boleh menyunting pertanyaan kapan saja, perubahannya berlaku mulai periode berikutnya". **Janji itu tidak ditepati siapa pun**: jalur pengisian menyajikan dan memvalidasi dari `form.Fields`, dan snapshot-nya menganggur.
>
> Yang benar-benar menjaga konsistensi adalah kunci `409` di `updateForm`, yang mengunci susunan pertanyaan begitu ada **satu** jawaban masuk, tanpa memedulikan form itu berulang atau tidak. Untuk form Kaizen yang hidup bertahun-tahun, artinya HR tidak akan pernah bisa memperbaiki satu pun pertanyaan setelah ide pertama masuk.
>
> Urutan perbaikannya **tidak boleh dibalik**: jadikan snapshot penopang beban lebih dulu (sajikan dan validasi dari `Fields` periode berjalan untuk form berulang), baru longgarkan kuncinya. Kalau dibalik, menyunting pertanyaan di tengah bulan langsung merusak jawaban yang sudah masuk pada bulan itu.

## Cara Kerja

### Siapa yang wajib

Sasarannya adalah `audience` yang sudah ada (`all`, `departments`, `employees`). Tidak ada konsep baru, dan kewajiban berlaku persis pada sasaran form, **bukan otomatis pada semua karyawan**. Untuk sasaran `employees`, daftarnya eksplisit sehingga penyebut papan kepatuhan akurat tanpa memanggil service mana pun.

### Kuota

Departemen pengaju dicocokkan ke daftar override, kalau tidak ada pakai angka bawaan. Entri berkuota `0` berarti departemen itu dikecualikan dari kewajiban tapi tetap boleh mengirim.

**Kuota adalah lantai, bukan langit-langit.** Ide ke-(N+1) tetap diterima. Program yang tujuannya mengumpulkan ide tapi menolak ide keempat karena kuotanya tiga jelas keliru.

Nilai departemen **wajib dikanonikkan** saat menulis. Penyaringan Mongo memakai `$in` yang peka huruf, dan jebakan ini sudah pernah menggigit di service yang sama: nilai `"tech development"` lolos pemeriksaan akses lalu tersimpan apa adanya, dan datanya langsung lenyap dari daftar pemiliknya sendiri.

### Potret peserta per periode

Penyebut papan kepatuhan diambil sebagai potret peserta **saat periode dibuka**, berikut nama, departemen, jabatan, dan kuota tiap orang. Ini menggantikan `audience.estimated_size` yang diisi manual dan karenanya tidak bisa dipakai menyatakan seseorang menunggak.

Per periode, bukan sekali saat form terbit, karena tiga hal:

1. Karyawan masuk dan keluar tiap bulan. Potret sekali saat terbit akan menagih orang yang sudah resign selamanya, sekaligus tidak pernah menagih karyawan baru.
2. Laporan bulan lampau jadi kebal perubahan data karyawan. Ini penting karena kombinasi `account_deactivated` dan `is_active` pada karyawan non-aktif bisa membuat orang lenyap dari laporan lama seolah dia tidak pernah ada (lihat [[HRIS - Personalia]]).
3. Jalurnya cron, bukan jalur pengisian, sehingga prinsip "jalur pengisian tidak menyentuh service lain" milik Form Builder tetap utuh.

Ini **berbeda dari `subject.resolved`** pada form penilaian, yang justru harus beku sepanjang umur form demi keadilan pembanding. Di sini yang dijaga adalah kejujuran laporan tiap bulan.

Gagal memotret **tidak menggagalkan periode**: orang tetap bisa mengirim ide, potretnya ditandai belum lengkap, dan cron berikutnya mencoba lagi. Selama potret belum lengkap, papan kepatuhan menyebutkannya dan **tidak menampilkan persentase**, karena angka dari penyebut yang salah lebih menyesatkan daripada tidak ada angka.

### Keputusan komite

Alurnya: belum ditinjau, lalu **Diterima** atau **Ditolak**; yang diterima bisa lanjut ke **Diterapkan** dengan tanggal dan PIC. Status terminal tidak bisa diubah lagi.

**Menolak wajib menyertakan alasan**, meniru aturan CSAT di [[Microservices - Task Management Service]] yang mewajibkan komentar saat rating rendah. Penolakan tanpa alasan hanya mengajari orang berhenti mengirim ide.

Komite = anggota yang terdaftar eksplisit di form, **ditambah** siapa pun yang lolos gerbang pengelola untuk departemen pemilik form. Butir kedua bukan kelonggaran melainkan pengaman: tanpa itu, salah isi daftar komite membuat form jadi yatim dan tidak ada yang bisa memperbaikinya.

Komite terpusat berisiko jadi leher botol (sasaran ratusan orang dikali kuota bulanan menumpuk di beberapa orang). Penawarnya di rancangan: antrean bisa disaring per departemen, kategori, status, dan periode, serta menerima aksi massal.

### Papan ide

Memuat ide berstatus Diterima dan Diterapkan saja. Field yang tidak layak tampil publik (perkiraan biaya, misalnya) disembunyikan lewat daftar key di blok pengaturan kaizen, bukan lewat penanda baru di tiap field, supaya permukaannya tidak menyentuh semua tipe form.

Nama pengaju ikut tampil, disengaja: pengakuan adalah separuh alasan orang mau mengirim ide. Tidak ada mode anonim untuk Kaizen.

## Dua Angka yang Sengaja Dipisah

| Angka | Dihitung dari | Dipakai untuk |
|---|---|---|
| Kepatuhan | ide **diajukan** pada periode | papan kepatuhan, pengingat |
| Kaizen KPI | ide **diterapkan** | skor KPI |

Kepatuhan memakai ide yang diajukan supaya karyawan memegang kendali penuh atas kepatuhannya sendiri: komite yang lambat atau ketat tidak boleh membuat orang lain dinyatakan menunggak. Skor KPI memakai yang diterapkan karena begitulah redaksi metriknya di [[HRIS - Matriks KPI per Departemen]].

Perbedaan ini wajib terbaca jelas di UI. Kalau tidak, orang akan menganggap salah satu dari kedua angka itu bug.

Setorannya lewat satu endpoint internal yang **menggerbang dirinya sendiri** ([[ADR - 0031 Prefix internal Bukan Batas Keamanan]]), dengan identitas terkunci ke header. Yang menariknya adalah [[Microservices - Employee Service]], dan service itu pula yang menulis `kpi_score`, sesuai [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]]. Form Builder tidak pernah menulis skor KPI.

## Belum Diputuskan (TBD)

- **Siapa saja anggota komite Kaizen.** Nama-namanya belum ditetapkan HR, dan jumlahnya menentukan apakah leher botol yang disebut di atas nyata atau tidak.
- **Sasaran awal (`audience`) rilis pertama.** Sudah disepakati bukan semua karyawan, tapi daftar departemennya belum ditetapkan.
- **Angka kuota bawaan dan override per departemen.** Matriks KPI memberi rentang 1 sampai 2 ide per orang per bulan untuk sebagian besar posisi, tapi angka resminya belum disahkan HR.
- **Kapan kewajiban resmi berlaku.** Bergantung pada kesiapan kanal mobile untuk departemen yang tidak pegang komputer.

## Di Luar Lingkup

- Reward atau insentif atas ide, termasuk integrasi ke `insentive` service.
- Suka dan komentar di papan ide.
- Tahap Do dan Check PDCA penuh. Yang tersisa hanya tanggal implementasi, PIC, dan catatan.
- Mode anonim untuk pengaju.
- Kuota level tim atau kuartalan. Sebagian metrik memang berbunyi "5 ide dari tim per kuartal", dan itu **diturunkan** jadi kuota bulanan per orang. Bila nanti kurang, agregasi kuartalan bisa dihitung dari data bulanan yang sama tanpa mengubah bentuk data.
- Metrik bernama Kaizen yang sebenarnya **bukan hitungan ide** (misalnya "mengurangi jumlah CAPA produksi", "menjaga kualitas produk 98 persen", "review kesesuaian SOP 5 produk per bulan") tetap tidak tertutup fitur ini. Rubrik penilaiannya yang perlu diperbaiki, bukan otomasinya.

## Rencana Bertahap

Tiap tahap berdiri sendiri dan bisa di-deploy tanpa menunggu berikutnya.

| # | Tahap | Status per 2026-08-06 |
|---|---|---|
| 1 | **Prasyarat**: snapshot periode jadi penopang beban, lalu kunci `409` dilonggarkan untuk form berulang. BE saja, tanpa perubahan kontrak yang terlihat klien | ✅ merged, **live dev + prod**, teruji end-to-end |
| 2 | **Tipe `kaizen` + kuota + potret peserta**. BE saja | ✅ idem |
| 3 | **Keputusan komite + papan kepatuhan**. BE, lalu FE di [[APP - Web ERP]] | ✅ BE idem · FE **PR erp-frontend #815 open** |
| 4 | **Upload file** (tipe field `file` lewat [[Microservices - File Service]], berlaku semua tipe form) | ✅ PR [#1023](https://github.com/bip-itteam-internal/bip-erp/pull/1023) + [#1057](https://github.com/bip-itteam-internal/bip-erp/pull/1057), **live dev + prod, teruji end-to-end**. Yang menahannya selama ini ternyata bukan "access key belum dibuat" melainkan **sisi file-service belum tahu kunci itu memetakan ke prefix mana** |
| 5 | **Papan ide + pengingat**. Kategori inbox baru wajib didaftarkan di `shared-library`, dan [[Microservices - Notification Service]] **wajib ikut di-deploy**, kalau tidak notifnya ditolak `400` dan hilang tanpa jejak | ✅ PR [#1028](https://github.com/bip-itteam-internal/bip-erp/pull/1028). Peringatan di kolom kiri ini **justru terjadi** — kategorinya tak didaftarkan dan pengingatnya mati — lalu diperbaiki [#1044](https://github.com/bip-itteam-internal/bip-erp/pull/1044) dan **dibuktikan sampai** |
| 6 | **Setoran KPI** ke [[Microservices - Employee Service]] | ✅ PR [#1029](https://github.com/bip-itteam-internal/bip-erp/pull/1029), terverifikasi di dev |
| 7 | **[[APP - MyBharata]]**: pengisian dan papan ide di mobile. Kewajiban baru boleh diperluas ke departemen yang tidak pegang komputer **setelah** tahap ini naik | ✅ BE [#1034](https://github.com/bip-itteam-internal/bip-erp/pull/1034) + gerbang presensi [#1039](https://github.com/bip-itteam-internal/bip-erp/pull/1039) · Flutter **my-bharata #108 merged ke `dev`**, versionCode 137, **belum rilis ke store** |
| — | **Menu Komite Kaizen** (di luar rencana awal, lahir karena komite tak punya jalan ke layarnya) | ✅ BE [#1046](https://github.com/bip-itteam-internal/bip-erp/pull/1046) + FE [erp-frontend #827](https://github.com/bip-itteam-internal/erp-frontend/pull/827), keduanya live dev + prod |

Konvensi tim: **BE di-deploy lebih dulu, baru FE**. Produksi tidak auto-deploy.

> [!warning] Tiga cacat berturut-turut lolos karena test tak pernah menyentuh lingkungan nyata
> Fitur form berulang mustahil dibuat lewat API selama 3 hari "live", seluruh jalur galat `/forms/:id*` membalas `502`, dan kini pengingat kuota ditolak notification-service. Ketiganya lolos dengan seluruh unit test hijau. **Tiap tahap wajib sekali dijalankan lewat gateway sebelum diklaim selesai**, dan angka nol yang mencurigakan diperlakukan sebagai pertanyaan, bukan kabar baik.

### Yang mobile lakukan berbeda dari rencana awal

Rancangan awal menyebut "pengisian dan papan ide di mobile" seolah menumpang daftar survei yang sudah ada. Yang dibangun adalah **menu Kaizen tersendiri**, dan form Kaizen justru **dikeluarkan** dari section Survei.

Sebabnya program Kaizen bukan "satu form lagi" bagi pengisinya: berulang tiap periode, berkuota, punya riwayat keputusan. Satu kartu survei tak bisa menjelaskan semuanya, dan kartu yang menjelaskan setengahnya lebih membingungkan daripada tak ada. Menu itu memuat progres kuota, pengiriman ide, riwayat lintas periode, dan detail tiap ide berikut keputusan komitenya.

Konsekuensi yang harus diingat: **karena kartunya hilang dari beranda, gerbang presensi jadi tak terlihat** kalau HR menyalakannya. Itulah yang ditutup PR #1039.

## Dependensi & Integrasi

- [[Microservices - Form Builder Service]] — rumah kodenya. Koleksi baru `form_uploads`, lihat [[DB - Overview and Notes]].
- [[Microservices - Employee Service]] — potret peserta saat periode dibuka, dan penarik metrik ke `kpi_score`.
- [[Microservices - Notification Service]] — pengingat kuota dan pemberitahuan keputusan.
- [[Microservices - File Service]] — lampiran, cap 4 MB, prefix object `form/`.
- [[CORE - API Master Gateway]] — satu-satunya pintu masuk; identitas datang sebagai header `BIP-*`.
- Ter-scope `company_id` sejak awal, sesuai [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]].
- Teks user-facing dua bahasa sesuai [[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]]. Kata **Kaizen** sendiri istilah baku dan tidak diterjemahkan.

## Dokumen Terkait

- [[HRIS - Otomasi Skor KPI]] — asal-usul kebutuhan (16 metrik tanpa sumber data)
- [[HRIS - Matriks KPI per Departemen]] — redaksi metrik Kaizen per posisi
- [[HRIS - Key Performance Index]] — `kpi_score` berperiode `YYYY-MM`
- [[ADR - 0054 Peninjau Ide Kaizen Bisa Atasan Departemen, Bukan Hanya Komite Terpusat]] — mode peninjau atasan, dan kenapa "atasan langsung per orang" gugur
- [[Microservices - Form Builder Service]] · [[API - Form Builder Service]]
- [[Microservices - Task Management Service]] — kandidat yang gugur, berikut alasannya
- [[APP - Web ERP]] · [[APP - MyBharata]]
- [[HRIS - Organization Structure]] — sumber departemen dan cakupan supervisi
