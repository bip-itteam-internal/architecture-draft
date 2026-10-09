## Deskripsi

*Layar **Anggaran & Cost Control** (`/finance/anggaran`) menunjukkan per pos biaya berapa Anggaran, berapa Terpakai, dan berapa Sisa, ditambah dana yang terserap lewat Pengajuan Barang/Dana. Dok ini adalah **satu-satunya tempat** aturan membaca angka di layar itu: kolom mana bagian dari kolom mana, dan apa yang sengaja tidak dijumlahkan. Keputusan produknya ada di [[ADR - 0159 Serapan Anggaran Dibaca dari Pengajuan sebagai Bagian dari Terpakai, Rute Tulis Anggaran Digerbang Izin Sendiri]].*

- **Status**: ⚠️ Implemented (ada catatan), **kode merged ke `main` 2026-10-08, deploy prod TBD**. Catatan: belum ada layar yang dilihat di browser dan belum ada endpoint yang dicoba lewat gateway (catatan penutup bip-erp#2779, 2026-10-08); keputusan terbuka dilacak di bip-erp#2814.
- **Implementasi**: [[API - Procurement Service]] (`/pengajuan-barang/serapan-anggaran*`) · [[API - Integration Service]] (`/accounting/anggaran*`) · [[Microservices - Procurement Service]] · [[APP - Web ERP]] (layar) · izin: [[CORE - RBAC dan Permission Set]]
- **Path di repo**: `bip-erp/services/procurement/pengajuan_barang_serapan.go` · `bip-erp/services/integration/internal/domain/entity/anggaran.go` · `erp-frontend/src/features/finance/anggaran/` · `erp-frontend/src/features/pengajuan-barang/` (kotak sisa pos, kartu Anggaran)

## Latar Belakang

- Master anggaran OPEX per **akun Accurate × departemen Accurate × bulan** sudah ada ([[Finance - Rancangan Finance Service]], pemilik data: [[REF - Kepemilikan Data]]), tetapi layarnya tidak memperlihatkan dana yang terserap lewat pengajuan, dan layar isian terkubur di dasar tab Master di bawah tiga panel laporan.
- Pengajuan Barang/Dana ([[Finance - Proses Pengajuan Pengeluaran dan Persetujuan]]) baru menjadi beban di Accurate setelah Accounting mencatatnya (jurnal terbit), jadi ada jeda antara "pengajuan lolos" dan "angka Terpakai naik".

## Ruang Lingkup (business view)

Tab di `/finance/anggaran`, urutan di layar (`tab-anggaran.ts`, array `TAB_ANGGARAN`):

| Tab | Isi |
|---|---|
| **Serapan** (bawaan) | Kartu Anggaran · Terpakai · Sisa dan kartu Menunggu dicatat; peringatan pos lewat anggaran dengan tautan **Buat rekomendasi** per pos; tabel serapan per pos (saringan Departemen dan Akun beban); tabel **Menunggu dicatat Accounting** per departemen pengaju; tombol **Rincian** per pos membuka sheet (terpakai per departemen Accurate, pengajuan pembentuknya, Jurnal lain); panel Admin & Non-Ops |
| Opex Marketing | Panel OPEX Marketing yang sudah ada; **tidak** disatukan ke Serapan |
| Rekomendasi | Pencatatan rekomendasi efisiensi (bekas `/finance/cost-control`); periodenya mengikuti Tahun/Bulan halaman, akun dari katalog |
| **Anggaran Bulanan** | Isian anggaran: unduh template, unggah Excel, tambah baris, koreksi, hapus (hapus meminta konfirmasi). `?tab=master` lama dipetakan **eksplisit** ke tab ini |
| **Forecast Mingguan** | Panel lama apa adanya, ditambah rincian per akun per minggu. **Tidak** mengubah forecast kas maupun KPI Cost Control #4. 🟡 Direncanakan: porsi proyeksi tiap minggu bisa diatur, lihat §Proyeksi Mingguan Diatur per Minggu |

### Proyeksi Mingguan Diatur per Minggu (🟡 Direncanakan, kode belum ada)

Keputusan: [[ADR - 0161 Proyeksi Forecast Kas Mingguan Diatur Porsinya per Minggu oleh Cost Control, Jumlah Sebulan Tetap RAPB]]. Yang berlaku hari ini tetap pembagian menurut jumlah hari, tanpa isian.

Cara kerja yang direncanakan:

- Cost Control (pemegang `finance.anggaran.kelola`) mengetik **total rupiah per minggu**. Jumlah seluruh minggu harus sama dengan anggaran RAPB kas-keluar bulan itu, kalau tidak simpan ditolak.
- Sistem menyimpan **porsi** tiap minggu, bukan nominalnya. Proyeksi tiap akun pada sebuah minggu = anggaran akun × porsi minggu itu, jadi tabel rincian per akun mengikuti tabel ringkasan. Semua akun memakai porsi yang sama.
- Minggu terkunci sejak hari pertamanya (WIB). Pergeseran hanya antar-minggu yang belum mulai.
- Tiap minggu paling banyak 2 kali diubah per periode; sekali simpan menghitung tiap minggu yang angkanya berubah.
- Riwayat perubahan (siapa, kapan, sebelum → sesudah per minggu) tampil di bawah tabel.
- Periode tanpa isian tetap memakai pembagian menurut jumlah hari.
- Bila RAPB diunggah ulang, porsi yang tersimpan diterapkan ke anggaran baru untuk semua minggu, termasuk yang sudah terkunci. Bulan mendatang boleh diatur sebelum bulannya mulai. Tidak ada tombol kembalikan ke bawaan.

⚠️ **Jangan dibaca sebagai cara menaikkan KPI.** Akurasi bulan dan KPI Cost Control #4 dihitung dari **total** sebulan, dan total itu tidak berubah saat porsi digeser antar-minggu. Yang berubah hanya akurasi **per minggu**.

Tambahan di luar halaman ini: kotak **sisa pos** di bawah tiap baris form pencatatan Accounting, dan kartu **Anggaran** baca-saja di tahap Cost Control pada detail pengajuan (pos yang sudah lewat anggaran bulan ini, maksimal 5, sisanya diringkas, plus tautan ke tab Serapan). Kartu itu tidak memperkirakan pos pengajuan, karena pos baru ditetapkan Accounting.

## Aturan Membaca Angka

⛔ **Wajib dibaca sebelum merancang layar atau laporan yang memakai kolom-kolom ini.** Kegagalannya bukan galat, melainkan rupiah yang sama terhitung dua kali atau pos tanpa anggaran yang terbaca Rp 0. Aturan ini semula hanya hidup sebagai komentar kode.

| Kolom / angka | Artinya | Aturan pemakaian |
|---|---|---|
| **Anggaran** | Nominal master anggaran pos (akun, departemen, bulan). Baris `departemen` kosong = seluruh perusahaan | Hanya baris yang anggarannya **terdefinisi** yang membawa angka |
| **Terpakai** | **Realisasi Accurate** pos itu, dari salinan lokal yang disegarkan harian dan lewat tombol Segarkan | Satu-satunya angka "terpakai"; **tidak pernah bertambah** karena angka dari pengajuan |
| **Sisa** | **Anggaran − Terpakai** (`HitungVarians`, `entity/anggaran.go:299`); bisa negatif | Bukan "anggaran − dari pengajuan" |
| **Lewat anggaran** | Terpakai **lebih besar** dari Anggaran (`anggaran.go:300`), yaitu di atas 100% | Satu-satunya ambang; "mendekati" belum ada. Hanya **peringatan**: tombol "Catat & kirim ke Accurate" tidak pernah dinonaktifkan oleh kondisi anggaran (`form-isian-accounting.tsx:309`). Persentase `null` bila Anggaran 0 (`anggaran.go:301-304`) |
| **Dari pengajuan** | **BAGIAN dari Terpakai**, keterangan atas pengajuan yang sudah berjurnal pada pos itu | ⛔ **Tidak dijumlahkan** ke Terpakai maupun Sisa (`gabungSerapan`, `serapan.ts:129-143`, realisasi baris tidak disentuh). Baris pos "seluruh perusahaan" menjumlah semua departemen akun itu. Total kartu hanya menghitung entri yang jatuh ke baris varians **terdefinisi** (`totalDariPengajuan`, `serapan.ts:150-165`) |
| **Jurnal lain** (sheet rincian) | Terpakai − dari pengajuan | Tidak pernah tampil negatif (menurut deskripsi PR erp-frontend#2188; tidak dibaca ulang barisnya di kode) |
| **Menunggu dicatat** | Pengajuan yang sudah lolos Cost Control tetapi belum berjurnal: antrean **per departemen pengaju** (departemen organisasi, **bukan** departemen Accurate) dan per tipe | ⛔ **Tidak dipetakan ke pos** (K5) dan **tidak ikut** Terpakai/Sisa. Tidak dibatasi periode: ini antrean berjalan (`pengajuan_barang_serapan.go:102-109`). Kalimat "bila dicatat ke akun X, Terpakai naik menjadi …" sengaja tidak dirender |
| **Total Anggaran / Terpakai / Sisa** (kartu ringkas) | Jumlah baris **terdefinisi** saja (`RingkasVarians`, `anggaran.go:338-364`) | Baris yang anggarannya belum diisi, realisasinya belum tersinkron, atau departemennya tak dikenal **tidak ikut** dan dicacah terpisah (`ada_baris_tak_terdefinisi`); layar wajib mengakuinya, bukan menampilkan Rp 0 |
| **Pos tanpa anggaran** | Tidak ada baris anggaran sama sekali | ⛔ Tampil "tidak punya anggaran", **bukan Rp 0**: Sisa Rp 0 berarti anggaran ada dan habis tepat. Baris yang hanya ada karena realisasinya (anggaran `belum_diisi`) **tidak** dihitung sebagai pos (`cariPos`, `serapan.ts:47-61`) |
| **Sisa sesudah dicatat** (form Accounting) | Sisa varians − nominal baris yang sedang diisi (`sisa-pos-anggaran.ts:97-108`); nominal minus (potongan) menambah sisa | Dihitung **per baris**: dua baris ber-akun dan departemen sama tidak saling menjumlah, jadi sisa bisa tampak lebih besar dan peringatan bisa tidak muncul (keputusan terbuka, §Belum Diputuskan). Periode kotak = bulan WIB berjalan |

### Dari mana angka "dari pengajuan" dan "menunggu dicatat"

- **`tercatat` bukan realisasi Accurate.** Ia dibangun dari baris Accounting dokumen pengajuan yang **sudah berjurnal** (`jurnal_nomor` terisi), per (akun COA, departemen Accurate) (`pengajuan_barang_serapan.go:24-28`). Realisasi baru menyusul pada sinkron berikutnya; antara pencatatan dan sinkron itu keduanya boleh berbeda. Bila dari pengajuan lebih besar dari Terpakai, layar menampilkannya **apa adanya** dengan keterangan "menunggu sinkron", tidak dipotong dan tidak ditambahkan (`serapan.ts:104-108`).
- **Periode `tercatat`** = bulan **WIB** dari **tanggal jurnal di Accurate**, bukan tanggal Accounting menekan tombol. Tanggal jurnal = tanggal transfer, dengan waktu pencatatan sebagai cadangan (`tanggalJurnalPengajuan`, `pengajuan_barang_jurnal_kirim.go:23-28`), fungsi yang **sama** dengan pembangun jurnal. Dua salinan aturan tanggal berarti serapan Oktober bisa memuat jurnal yang di Accurate jatuh di September.
- **Penanda pencatatan** di riwayat pengajuan berbunyi `dicatat`, **bukan** `disetujui` (`waktuDicatatPengajuan`, `pengajuan_barang_serapan.go:149-157`). Pembaca yang mencari `disetujui` di tahap itu mendapat serapan kosong yang terbaca "belum ada yang tercatat".
- **Syarat masuk antrean Menunggu dicatat** (`menungguDicatat`, `pengajuan_barang_serapan.go:262-278`): tipe berjurnal dan bukan dokumen pembelian, status berjalan, pernah dituntaskan tahap Finance setujui-bayar, `jurnal_nomor` kosong, belum pernah dicatat, jurnal tidak gagal terbit.
- ⚠️ **Dokumen yang tidak masuk daftar mana pun** (disengaja dan dilaporkan di komentar kode, belum diukur jumlahnya): pengajuan yang jurnalnya **gagal terbit**; yang sudah dicatat **tanpa nomor jurnal** (mis. kill switch jurnal mati); dan dokumen berjurnal **tanpa riwayat pencatatan** (jurnal terbit sebelum tahap pencatatan Accounting ada). Uangnya tidak muncul di `tercatat` maupun Menunggu dicatat. Keputusannya terbuka (§Belum Diputuskan).

## Persona / Pengguna

| Persona | Peran & Divisi | Akses / RBAC | Device |
|---|---|---|---|
| Cost Control | Finance; memegang anggaran dan rekomendasi efisiensi | Paket `finance_anggaran` (membaca laporan akuntansi + mengelola anggaran) | Web ERP |
| Supervisor Finance | Finance | Tier supervisor/admin finance memuat izin kelola anggaran | Web ERP |
| Accounting | Finance; mencatat pengajuan | Tahap pencatatan pengajuan (`budget.accounting.pencatatan`); membaca varians untuk kotak sisa pos | Web ERP |
| Staf finance lain | Finance | Boleh membaca laporan; **tidak** melihat tombol tulis anggaran | Web ERP |

Gerbang rute dan rincian izin hidup di [[API - Procurement Service]], [[API - Integration Service]], dan [[CORE - RBAC dan Permission Set]], bukan di sini.

- **Tujuan**: tahu pos mana yang hampir atau sudah lewat anggaran sebelum akhir bulan, dan seberapa besar dana yang masih antre dicatat.
- **Pain point**: dana yang terserap lewat pengajuan tidak terlihat, dan isian anggaran sulit ditemukan.
- **Aksi utama**: lihat Serapan, buka Rincian pos, buat rekomendasi untuk pos yang lewat, unggah RAPB di Anggaran Bulanan.

## Alur Pengguna

1. **Cost Control, awal bulan**: unduh template di tab Anggaran Bulanan, isi, unggah RAPB (`GET /accounting/anggaran/template?tahun=` lalu `POST /accounting/anggaran/upload`).
2. **Cost Control, harian**: buka Serapan, Rincian pos, dan untuk pos lewat anggaran klik **Buat rekomendasi** (akun terbawa ke form Rekomendasi). Di tahap Cost Control sebuah pengajuan, kartu Anggaran baca-saja menyebut pos yang sudah lewat.
3. **Accounting**: buka pengajuan tahap pencatatan (COA, project, departemen terisi seperti sebelumnya), lihat kotak sisa pos per baris, lalu **Catat & kirim**. Sesudah realisasi tersinkron, pengajuan berpindah dari Menunggu dicatat ke "dari pengajuan" pada posnya.

## Urutan Deploy (dijalankan MANUSIA)

Prod: **TBD (belum deploy per 2026-10-08)**. Urutan menurut bip-erp#2811 dan bip-erp#2779: employee-service naik, **pasang paket `finance_anggaran` ke posisi Cost Control** (layar Hak per Posisi) dan pastikan SPV Finance memegang tier supervisor, lalu integration-service naik, lalu **login ulang** pemegang paket (izin dibawa klaim token), baru FE. BE (procurement, integration, employee) sebelum FE. Bila paket terlewat, Cost Control mendapat 403 saat mengunggah RAPB; saat employee-service start cek log `[Migrate]` untuk memastikan paket tersisip. Bukti yang diminta: akun Cost Control mengunduh template, mengisi satu angka, mengunggah tanpa baris ditolak; akun staf finance mendapat 403 di unggah. Prosedur umumnya: [[RUN - Deploy Microservices bip-erp]].

## Belum Diputuskan (TBD)

Dilacak di bip-erp#2814 (Pemutus: wirkancil):

- **Sheet rincian pos**: tiga bagian mockup belum dirender (kalimat antrean IKLAN per akun, tautan "Lihat di buku besar", paragraf "Per orang (marketing)"); butuh penanda akun iklan dari backend dan rute buku besar per akun beban.
- **Dokumen di luar kedua daftar** (lihat §Aturan Membaca Angka): dibiarkan, atau ditambah daftar ketiga / periode dari tanggal transfer. Jumlahnya di prod belum diukur.
- **Gerbang endpoint serapan lebih sempit dari gerbang layar**: tanpa cadangan tier finance. Menyamakannya menuntut aturan cadangan dipindah ke `shared-library`.
- **Sisa sesudah dicatat**: dijumlahkan per pos, atau cukup diberi keterangan.
- **Template unggah bergantung pada Accurate**: daftar akun OPEX diambil langsung dari Accurate, jadi Accurate mati → 502.
- **Konfirmasi paket izin** `finance_anggaran` oleh Pemutus (K9).
- Sisa teknis yang tercatat di issue yang sama: aturan "supervisor/admin finance" untuk izin kelola tertulis di dua tempat di FE; `GET /katalog/departemen` terdaftar dua kali di procurement (yang terpakai mengirim nama; bila urutan berubah, kotak sisa pos salah tanpa galat).
- **Verifikasi**: belum ada layar yang dilihat di browser dan belum ada endpoint yang dicoba lewat gateway.

Untuk proyeksi mingguan yang diatur (ADR 0161, Diterima 2026-10-09): yang tersisa hanya asal nama pengubah di riwayat (diserahkan ke pelaksana). Sudah diputuskan di ADR-nya: unggah ulang RAPB menerapkan porsi ke anggaran baru untuk semua minggu, bulan mendatang boleh diatur, dan tidak ada tombol kembalikan ke bawaan.

## Dokumen Terkait

- [[ADR - 0159 Serapan Anggaran Dibaca dari Pengajuan sebagai Bagian dari Terpakai, Rute Tulis Anggaran Digerbang Izin Sendiri]]
- [[ADR - 0161 Proyeksi Forecast Kas Mingguan Diatur Porsinya per Minggu oleh Cost Control, Jumlah Sebulan Tetap RAPB]]
- [[Finance - Rancangan Finance Service]] · [[Finance - Proses Pengajuan Pengeluaran dan Persetujuan]] · [[Finance - FAT Persona]]
- [[API - Procurement Service]] · [[API - Integration Service]] · [[Microservices - Procurement Service]]
- [[CORE - RBAC dan Permission Set]] · [[APP - Web ERP]] · [[REF - Kepemilikan Data]]
- [[ADR - 0130 Dashboard FAT Diringkas, Isi Posisi Pindah ke Modul Kerjanya]]
