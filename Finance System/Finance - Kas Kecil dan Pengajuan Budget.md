## Deskripsi

*Modul kas kecil per divisi beserta jalur pengajuan budget, menggantikan aturan yang kini berjalan lewat kesepakatan lisan dan chat. **Lintas divisi**, bukan fitur satu departemen: Finance yang menetapkan plafon dan aturannya, tiap divisi yang memakainya. Dokumen ini menggabungkan blueprint dari Finance dengan hasil pemeriksaan langsung ke data produksi, supaya lubang datanya terlihat sebelum ada yang mulai menulis kode.*

- **Status**: ⚠️ **Jalur pengeluaran kas kecil lengkap dan sudah merge** (delapan PR, 5 Agustus 2026), **belum deploy**. Pengajuan, approval berjenjang, top-up, tutup buku, laporan, dan jurnal belum ada. Empat lubang data dan tiga tabrakan arsitektur masih menghalangi bagian berikutnya.
- **Sumber requirement**: Blueprint Modul Kas Kecil & Pengajuan Budget v1.0 (draft), disusun dari percakapan WhatsApp dengan Finance.
- **Sumber angka sistem**: sensus langsung `employee_db` dan `procurement_db` produksi, **4 Agustus 2026**.
- **Terkait**: [[GA - Form Pengadaan dan Pengajuan Dana]] mencatat dua form kertas GA yang menjadi bagian dari alur ini.

## Tujuan

1. Plafon kas kecil per divisi terkontrol sistem, tidak bisa overbudget diam-diam.
2. Pemisahan jalur Kas Kecil dan Pengajuan berjalan otomatis menurut nominal.
3. Pembelian aset tidak bisa menyelinap lewat kas kecil.
4. Setiap pengeluaran punya jejak audit dan bukti.

## Aturan Bisnis (dari blueprint Finance)

### Plafon kas kecil per divisi, per bulan

| Kode | Divisi | Plafon | Tipe |
|---|---|---:|---|
| BH | Beautyhacks | Rp 10.000.000 | Tetap |
| KY | Kyura | Rp 10.000.000 | Tetap |
| GA | General Affair | Rp 15.000.000 | Tetap |
| PU | Purchasing | Rp 2.000.000 | Tetap, boleh top-up |
| GTJ | Gudang TJ | Rp 2.000.000 | Tetap, boleh top-up |
| BC | Bharata Club | dinamis | Sesuai pengajuan disetujui |
| SK | Sekretariat | Rp 3.000.000 | Tetap |

### Sembilan aturan

| ID | Kondisi | Aksi |
|---|---|---|
| R-01 | Nilai transaksi < Rp 500.000 | Jalur Kas Kecil, langsung pakai |
| R-02 | Nilai transaksi ≥ Rp 500.000 | Wajib jalur Pengajuan dengan approval |
| R-03 | Terpakai + nominal baru > plafon divisi | Blokir, tampilkan sisa saldo |
| R-04 | Divisi Bharata Club | Plafon = akumulasi pengajuan disetujui |
| R-05 | Purchasing atau Gudang TJ, saldo menipis | Boleh ajukan top-up; divisi lain tidak |
| R-06 | Beautyhacks atau Kyura, kategori aset | Blokir kas kecil, arahkan ke pengajuan aset |
| R-07 | Beautyhacks atau Kyura minta ke GA, kategori bukan aset | Blokir, ditanggung budget divisi sendiri |
| R-08 | Dua transaksi lebih, vendor/kategori sama, 1 sampai 3 hari, total ≥ Rp 500.000 | Tandai untuk review Finance (blokir lunak) |
| R-09 | Transaksi kas kecil tanpa bukti lebih dari N hari | Kunci pengajuan berikutnya untuk user itu |

Nilai pada R-01, R-02, R-03, R-05, dan R-06 **wajib disimpan sebagai data**, bukan di kode.

### Matriks approval yang diusulkan

| Jalur | Nominal | Approver 1 | Approver 2 | Approver 3 |
|---|---|---|---|---|
| Kas kecil | < Rp 500.000 | swalayan (PIC kas kecil divisi) | — | — |
| Pengajuan | Rp 500.000 sampai 5 juta | Kepala Divisi | Finance | — |
| Pengajuan | di atas Rp 5 juta | Kepala Divisi | Finance | Direksi |
| Pengajuan Aset | semua nominal | Kepala Divisi | GA | Finance |
| Top-Up | semua nominal | Kepala Divisi | Finance | — |

### Alur status

- **Kas kecil**: DRAFT, TERPAKAI, MENUNGGU_BUKTI, TERVERIFIKASI, TERJURNAL
- **Pengajuan**: DRAFT, DIAJUKAN, REVIEW_ATASAN, REVIEW_FINANCE, DISETUJUI / DITOLAK / REVISI, DICAIRKAN, REALISASI, SELESAI
- **Top-up**: DIAJUKAN, REVIEW_FINANCE, DISETUJUI, DANA_DITAMBAHKAN

## Sudah Ada di Kode

Delapan PR merge **5 Agustus 2026** (#986, #988, #990, #991, #992, #993, #994, #996), seluruhnya di `bip-erp/services/procurement/`. **Belum deploy.**

Jalur pengeluaran kas kecil sudah lengkap dari catat sampai pertanggungjawaban. Yang belum ada: pengajuan, approval berjenjang, top-up, tutup buku, laporan, dan jurnal.

### Aturan dan perhitungan (fungsi murni, tanpa Mongo dan tanpa HTTP)

| Berkas | Isi |
|---|---|
| `kas_periode.go` | Batas bulan WIB, `RentangPeriodeKas` dan `PeriodeKasDari` |
| `kas_parameter.go` | Parameter berversi, `ParameterBerlaku` memilih versi menurut tanggal |
| `kas_plafon.go` | `PlafonEfektif` (tetap vs dinamis) dan `SisaSaldo` |
| `kas_aturan.go` | `PutuskanJalurKas` untuk R-01 sampai R-07 dan R-09, `DugaPemecahanTransaksi` untuk R-08 |
| `kas_konteks.go` | `RakitKonteksKas`, titik sambung master ke mesin aturan |
| `kas_kategori.go` | `AsetKarena`, dua jalan sebuah barang disebut aset |
| `kas_transaksi.go` | Penomoran per periode, validasi, `AdaTunggakanBukti` (R-09) |
| `kas_bukti.go` | `ValidasiBuktiKas` dan letak berkas di penyimpanan |

Kesepuluh test case penerimaan blueprint §9 ditulis apa adanya sebagai tabel test dan seluruhnya lulus.

### Endpoint

Seluruhnya berprefix `/kas`, di belakang gateway `/api/procurement/*`.

| Rute | Izin | Keterangan |
|---|---|---|
| `GET /kas/unit` · `POST /kas/unit` | `kaskecil.view` · `kaskecil.master.save` | Master unit kas |
| `GET /kas/kategori` · `POST /kas/kategori` | `kaskecil.view` · `kaskecil.master.save` | Master kategori belanja |
| `GET /kas/saldo?unit=&periode=` | `kaskecil.view` | Plafon, terpakai, sisa |
| `GET /kas/transaksi` | `kaskecil.view` | Daftar, dapat disaring unit/periode/status/tertandai |
| `POST /kas/transaksi` | `kaskecil.transaksi.save` | **Satu-satunya rute yang mengeluarkan uang** |
| `POST /kas/transaksi/:nomor/bukti` | `kaskecil.transaksi.save` | Unggah bukti, hanya oleh pencatatnya |
| `POST /kas/transaksi/:nomor/verifikasi` | `kaskecil.approve.finance` | Verifikasi bukti oleh Finance |

Koleksi: `kas_unit`, `kas_kategori`, `kas_parameter`, `kas_plafon`, `kas_transaksi` di `procurement_db`.

**Pengajuan budget** (`/api/procurement/budget/*`): `POST /budget/pengajuan` (buat DRAFT; terima `tautan` URL opsional, divalidasi http/https) → `POST .../:nomor/ajukan` (bekukan JenjangWajib) → antrean `GET /budget/persetujuan` + aksi `POST .../:nomor/setujui|tolak|revisi`. Tahap ditentukan **nominal** (Finance; Direktur bila ≥ ambang), penyetuju dari izin `approve.finance`/`approve.direksi` dan disaring per-departemen (lihat §Izin). **Lampiran**: `POST .../:nomor/lampiran` (**append**, maks 5 berkas; pdf/jpg/png/webp/doc/docx/xls/xlsx) & `DELETE .../:nomor/lampiran?object=…`, boleh diubah sampai status final. Koleksi `pengajuan_budget`.

**Antarmuka (erp-frontend)**: menu "Ajukan Budget" + "Pengajuan Saya" **digabung** jadi satu menu **"Pengajuan Budget"** (halaman daftar); form pembuatan tampil sebagai **modal** dari tombol Ajukan. Lampiran banyak berkas dengan preview inline pdf/gambar (office = nama+ikon, buka tab baru; gambar dikonversi **WebP** di klien sebelum unggah) dan input **link** ada di form. Preview memakai presigned URL `GET /api/file/minio/preview` (dipakai ulang, bukan endpoint unduh baru).

### Kenapa menumpang procurement-service

Menghemat satu modul gateway. Isinya **bukan** cermin Accurate seperti sisa service itu; modul ini justru berhenti sebelum Accurate, dan pemakainya seluruh divisi. Rutenya berprefix `/kas` supaya batasnya terlihat dari URL.

### Izin: tidak ada fallback tier

Beda pokok dari modul lain di repo. Monitoring, payroll, dan procurement menyediakan fallback tier untuk menjaga akses yang sudah dipakai orang sebelum permission-set ada. Kas kecil belum punya satu pun pemakai, jadi tidak ada yang perlu dijaga; yang tersisa hanya risikonya. Memberi hak membelanjakan uang karena seseorang kebetulan supervisor di modul lain adalah cara termudah melahirkan pengeluaran yang tak seorang pun merasa memberikannya.

**Semua orang ditolak sampai ditugaskan eksplisit lewat permission-set.** Bila setelah deploy ada yang mengeluh tidak bisa masuk, itu perilaku yang benar. Tujuh paket bawaan tersedia di `common.DefaultKasKecilSets()`, dengan Reach menyempit untuk staf dan atasan divisi.

> ⚠️ **Celah seed yang sudah diperbaiki (2026-08-19).** Ketujuh paket terdefinisi di `common.DefaultKasKecilSets()` **tetapi tidak pernah ikut di-seed**: `DefaultPermissionSets()` (`shared-library/models/employee/permission_set.go`) merangkum seed modul lain (finance, procurement, ga, dst.) tapi **melewatkan kaskecil**, sehingga koleksi `master_permission_set` tak pernah berisi paket kaskecil. Karena modul ini paket-saja tanpa fallback tier (`KasKecilTierDefault` selalu nil), akibatnya **total** — bukan sekadar kode mati: tak seorang pun bisa diberi izin `kaskecil.*` lewat layar Hak per Posisi, dan menu **Kas Kecil & Budget** hilang dari sidebar tanpa satu pun galat. Terlihat di **dev**; **prod** sempat tampil karena master set + assignment-nya disuntik manual ke DB, di luar jalur seed. Perbaikan: tambah loop `DefaultKasKecilSets()` ke `DefaultPermissionSets()`, dikunci uji **`TestSetiapModulTerdaftarPunyaPaketBawaan`** (`services/employee`) yang mewajibkan tiap modul katalog terdaftar punya paket bawaan (kecuali `legal` yang dipensiunkan). Seed jalan idempoten lewat `migrateMissingDefaultPermissionSets()` saat employee-service start — di dev sudah terverifikasi menyisipkan 7 paket. **Prod masih menunggu deploy** (verifikasi dulu apakah suntikan manualnya selaras dengan key paket resmi).

> ⚠️ **Pengecualian super-akses SPV IT (2026-08-19).** Atas permintaan pemilik sistem, **Supervisor IT** (`system_roles["it"]=="supervisor"`) diloloskan SELURUH modul kaskecil **tanpa** penugasan permission-set — menyimpang sadar dari kebijakan "tanpa fallback" di atas. Diinjeksi di `izinKasEfektif` (`kas_gate.go`) sehingga gerbang rute, gerbang salah-satu, dan cek internal handler (approval) sepakat; guard FE (`KasKecilGuard`, `MasterKasKecil`, `portal-menu.ts`) diselaraskan. Konsekuensi diterima sadar: SPV IT bisa **menyetujui & mengelola master**, bukan hanya melihat.

> **Scoping persetujuan per departemen (2026-08-19).** `PengajuanBudget.Departemen` dibekukan dari `UnitKas.Departemen` saat pembuatan. Antrean (`ListPersetujuanBudget`) **dan** aksi (`Setujui`/`Tolak`/`Revisi`) disaring `departemenTerlihatKas`: penyetuju ber-reach `all` (paket Finance/Direktur default) & SPV IT melihat semua; reach `division`/`own` hanya departemen dalam `SupervisedDepartments` (departemen sendiri + supervisi, fallback token lama aman). Enforce **di aksi juga**, bukan cuma antrean, sebab API bisa dipanggil langsung dengan nomor mana pun. Migrasi `migrasiDepartemenPengajuanBudget` mengisi pengajuan lama dari unitnya saat service start.

### Satu tahap status di luar blueprint

Blueprint melompat dari `MENUNGGU_BUKTI` langsung ke `TERVERIFIKASI`, padahal keduanya dikerjakan pihak berbeda: pengaju yang mengunggah, Finance yang memeriksa. Ditambahkan `MENUNGGU_VERIFIKASI` di antaranya, sebab tanpa itu satu-satunya pilihan adalah membiarkan pengunggah memverifikasi buktinya sendiri, atau membiarkan status berbohong tentang apa yang sudah terjadi.

Konsekuensinya R-09 memakai **ada tidaknya bukti**, bukan statusnya. Aturannya berbunyi "transaksi tanpa upload bukti", dan bila ia menunggu verifikasi, pengaju yang sudah mengunggah tetap terkunci karena kelambatan Finance.

**Empat keputusan teknis yang perlu diketahui sebelum melanjutkan:**

- **Uang bertipe `int64`, bukan `float64`.** Rupiah adalah bilangan bulat, dan `float64` melahirkan sisa pecahan yang muncul sebagai selisih Rp 1 di rekonsiliasi lalu mustahil dijelaskan.
- **Batas bulan WIB**, memakai ulang `lokasiWIB` milik `accurate_vendor.go`. Dua konstanta WIB dalam satu package akan berbeda diam-diam suatu hari nanti.
- **R-08 berdiri terpisah** dari penentuan jalur, karena ia blokir lunak (tanda untuk Finance), bukan penolakan. Menggabungkannya akan menahan transaksi yang sah.
- **Setiap penolakan membawa saran jalan keluar.** Penolakan buntu membuat pemakai kembali ke kertas, dan kegagalan semacam itu tidak muncul di log mana pun.

### Pertentangan di dalam blueprint yang sudah dipilihkan sementara

Bagan alir §4.1 mengirim barang **aset di atas ambang** ke jalur pengajuan biasa bila divisinya boleh membeli aset lewat kas kecil. Matriks approval §5 berkata lain: baris "Pengajuan Aset" berlaku untuk **semua nominal**, dengan rantai Kepala Divisi, GA, lalu Finance.

Kode mengikuti **matriks approval**. Alasannya: melewatkan GA pada pembelian aset membuat aset masuk perusahaan tanpa sepengetahuan pihak yang mencatat register aset, dan itu baru ketahuan saat stock opname. Pilihan ini dikunci test `TestAsetDiAtasAmbangTetapLewatJalurAset` supaya terlihat, bukan tersembunyi. **Menunggu konfirmasi Finance**; bila jawabannya sebaliknya, yang berubah hanya satu cabang.

## Lubang Data (diukur langsung di produksi, 4 Agustus 2026)

Empat temuan berikut **bukan pendapat**, melainkan hasil hitung terhadap `employee_db` produksi. Semuanya menghalangi Fase 1 blueprint.

### 1. "Divisi" di blueprint bukan "departemen" di ERP

Ketujuh baris plafon punya **tiga bentuk yang berbeda**, dan hanya lima di antaranya sepadan dengan satu departemen utuh.

| Blueprint | Induk di ERP | Bentuk | Karyawan induk |
|---|---|---|---:|
| BH Beautyhacks | `Beauty Hacks` (ejaan berbeda) | departemen utuh | 48 |
| KY Kyura | `Kyura` | departemen utuh | 31 |
| GA General Affair | `General Affair` | departemen utuh | 21 |
| SK Sekretariat | `Kesekretariatan` (nama berbeda) | departemen utuh | 11 |
| PU Purchasing | `Procurement` (nama berbeda) | departemen utuh | 2 |
| **GTJ Gudang TJ** | **`Manufaktur`** | **sub-unit** | 36 |
| **BC Bharata Club** | **`Human Resource`** | **sub-unit** | 7 |

> **Koreksi 5 Agustus 2026.** Versi sebelumnya menyatakan Gudang TJ dan Bharata Club "belum menjadi departemen di sistem sama sekali" dan menyarankan keduanya didaftarkan sebagai departemen baru. **Itu keliru dan berbahaya**: keduanya sub-unit di dalam departemen yang sudah ada, dan mendaftarkannya sebagai departemen akan melahirkan dua departemen palsu sekaligus memisahkan orang keluar dari Manufaktur dan Human Resource. Dikoreksi setelah dikonfirmasi tim.

**Konsekuensinya plafon TIDAK BOLEH dikunci ke `department`.** `work_data` hanya menyimpan `department` dan `position`; tidak ada field sub-unit, lokasi, maupun site. Bila plafon dipasang per departemen, plafon Gudang TJ sebesar Rp 2 juta akan mengalir ke **seluruh 36 orang Manufaktur**, termasuk 19 Operator Production yang tidak berurusan dengan kas gudang.

Yang dibutuhkan: master **unit kas** tersendiri, dengan induk departemen dan daftar PIC yang boleh bertransaksi. Bentuk ini menampung ketiganya sekaligus, dan tidak menuntut perubahan apa pun pada struktur organisasi HRIS.

Catatan tambahan yang masih berlaku: `master_department` berisi **11** entri sedangkan `work_data` memakai **12** nilai departemen. `Human Resource` (7 orang) ada di data karyawan tetapi **tidak ada di master departemen**, sehingga dropdown apa pun yang bersumber dari master akan melewatkannya.

### 2. Empat departemen belum jelas status kas kecilnya

| Departemen | Karyawan | Keterangan |
|---|---:|---|
| Percetakan | 13 | belum jelas |
| Tech Development | 11 | belum jelas |
| Quality | 6 | belum jelas |
| Marketing Offline Distribution | 1 | belum jelas |

Totalnya **31 dari 206 karyawan**.

> **Koreksi 5 Agustus 2026.** Versi sebelumnya menyebut **tujuh** departemen dan **93** karyawan. Tiga di antaranya ternyata sudah terjelaskan: **Finance** (19) memang seharusnya tidak punya plafon karena perannya penyetuju dan pengatur aturan, bukan pembelanja; **Manufaktur** (36) tercakup lewat Gudang TJ; **Human Resource** (7) tercakup lewat Bharata Club.

Untuk keempat yang tersisa perlu dipastikan ke Finance: memang tidak punya kas kecil, atau terlewat dari daftar? Bila memang tidak punya, jalur kas kecilnya sebaiknya tidak ditampilkan sama sekali, bukan ditampilkan lalu diblokir R-03 dengan pesan "sisa saldo 0" yang membingungkan.

### 3. Matriks approval mengandaikan hierarki yang datanya belum lengkap

"Kepala Divisi" sebagai Approver 1 baru dapat diturunkan untuk **9 dari 12 departemen**. Yang belum punya penanda atasan: **General Affair, Procurement, dan Percetakan**.

Dua di antaranya justru pemeran utama modul ini: General Affair memegang plafon terbesar (Rp 15 juta) dan menjadi approver jalur aset, sedangkan Procurement adalah "Purchasing" yang mendapat hak top-up.

Di tingkat perorangan lebih tipis lagi: hanya **83 dari 206** karyawan punya atasan langsung terisi. Struktur atasan tersimpan di `work_data` (`is_supervisor` + `department`), **bukan** di `system_roles` yang hanya mengatur hak akses modul. Lihat [[HRIS - Organization Structure]].

### 4. Master kategori belanja belum ada dan tidak bisa dipinjam

R-06 dan R-07 seluruhnya bergantung pada `m_kategori_belanja` beserta flag `is_asset`. Master barang yang sudah ada di ERP berisi **955 item dari Accurate**, dan isinya bahan baku serta bahan kemas, justru yang dikecualikan dari alur ini. Master kategori belanja operasional harus dibuat dari nol dan diisi Finance.

## Tabrakan dengan Arsitektur

### Buku besar sendiri melawan [[ADR - 0001 Akuntansi via Accurate]]

Blueprint memuat tabel `t_jurnal` dan menyebut pengeluaran "langsung terjurnal ke akuntansi". Pembukuan perusahaan ada di Accurate dan ERP sengaja **tidak** punya buku besar. Membuat `t_jurnal` di ERP melahirkan dua sumber kebenaran akuntansi.

Dua jalan yang masuk akal, dan ini keputusan Finance:

1. **ERP berhenti di pencatatan.** Pengeluaran, bukti, dan status tersimpan di ERP; Finance mem-posting jurnalnya di Accurate seperti sekarang.
2. **ERP menulis ke Accurate lewat API.** Belum pernah dilakukan untuk dokumen transaksi. Yang sudah terbukti berjalan baru penulisan data master pemasok dan barang di [[Microservices - Procurement Service]].

### Model data relasional di atas database dokumen

Blueprint memakai bentuk relasional (`t_`, `m_`, kunci asing). bip-erp memakai MongoDB per-service ([[ADR - 0002 Database-per-Service]]). Penerjemahannya rutin, tetapi satu hal wajib dipertahankan apa adanya: **`m_parameter` dengan `berlaku_dari` dan `berlaku_sampai`**. Tanpa versi aturan, laporan bulan lalu akan diam-diam memakai plafon terbaru.

### Register aset belum ada ujungnya

R-06 mengarahkan pembelian aset ke jalur pengajuan aset, dan blueprint menyebut `m_aset`. Register aset belum ada di sistem mana pun; [[GA - Inventory Management]] masih konsep. Jalur ini boleh dibangun lebih dulu, asalkan disadari bahwa ujungnya belum tersedia.

## Pertanyaan Terbuka

Sepuluh pertanyaan pertama datang dari blueprint sendiri (§8), lengkap dengan asumsi sementaranya. Empat di antaranya sudah dapat dijawab sebagian dari sistem:

| # | Pertanyaan blueprint | Asumsi sementara | Catatan dari sistem |
|---|---|---|---|
| 1 | "Di bawah 500" = Rp 500.000? | Ya | — |
| 2 | Batas dihitung per transaksi atau per item? | Per nota | — |
| 3 | Nominal termasuk PPN? | Ya, bruto | — |
| 4 | Sisa saldo akhir bulan: hangus, kembali, atau carry-over? | Hangus | — |
| 5 | Bharata Club perlu pagar maksimum? | Tanpa pagar | Sub-unit di dalam `Human Resource`; perlu dipastikan ia tim atau anggaran kegiatan, sebab itu menentukan siapa yang boleh membelanjakan |
| 6 | Selain Purchasing dan Gudang TJ benar tidak boleh top-up? | Tidak boleh | Gudang TJ sub-unit di dalam `Manufaktur`; belum jelas apakah ia mencakup 11 orang berposisi Warehouse atau hanya sebagian |
| 7 | Larangan aset lewat kas kecil: hanya BH dan KY, atau semua? | Sebaiknya semua | — |
| 8 | Batas nilai barang disebut aset | Perlu angka Finance | Register asetnya juga belum ada |
| 9 | Berapa hari maksimal unggah bukti? | 3 hari kerja | — |
| 10 | Siapa approver definitif tiap level? | Perlu struktur resmi | Baru 9 dari 12 departemen punya penanda atasan; 83 dari 206 karyawan punya atasan langsung |

Ditambah tiga pertanyaan baru dari pemeriksaan sistem:

11. **Siapa anggota Gudang TJ dan Bharata Club?** Keduanya sub-unit (lihat Lubang Data nomor 1), jadi yang dibutuhkan bukan departemen baru melainkan daftar PIC yang boleh bertransaksi atas unit kas itu. Untuk Gudang TJ: seluruh 11 orang berposisi Warehouse di Manufaktur, atau sebagian? Untuk Bharata Club: sebuah tim, atau anggaran kegiatan yang dipegang PIC yang ditunjuk?
12. **Empat departemen tanpa plafon** (Percetakan, Tech Development, Quality, Marketing Offline Distribution, total 31 karyawan) memang tidak punya kas kecil, atau terlewat?
13. **Jurnal**: ERP berhenti di pencatatan, atau menulis ke Accurate?

## Tahapan Implementasi

Blueprint mengusulkan enam fase, kurang lebih 16 minggu. Satu perubahan yang perlu dipertimbangkan: **Fase 1 diperluas dengan pembenahan master data**, karena plafon tidak dapat diisi sebelum divisi dan penanda atasan beres.

| Fase | Ruang lingkup | Catatan |
|---|---|---|
| 0 | Isi penanda atasan untuk General Affair, Procurement, dan Percetakan; tambahkan `Human Resource` ke `master_department`; isi master unit kas beserta PIC-nya | **Tambahan**, bukan dari blueprint. Pekerjaan data, bukan kode. **Belum dikerjakan.** JANGAN mendaftarkan Gudang TJ atau Bharata Club sebagai departemen, lihat koreksi di Lubang Data nomor 1 |
| 1 | Master data (divisi, plafon, kategori, parameter) + dashboard saldo | **Backend selesai** (unit kas, kategori, parameter, plafon, saldo). Sisa: layar FE dan pengisian datanya |
| 2 | Transaksi kas kecil + R-01, R-03, R-06 + unggah bukti | **Backend selesai**, termasuk R-02, R-07, R-08, R-09 dan verifikasi Finance. Sisa: layar FE. **Unggah bukti butuh `MINIO_PROCUREMENT_KEY` dibuat lebih dulu di MinIO** |
| 3 | Modul pengajuan + approval berjenjang + R-02, R-07 | 3 minggu |
| 4 | Top-up (R-05) + tutup buku bulanan + laporan | 2 minggu |
| 5 | Register aset + R-08, R-09. **Integrasi jurnal menunggu keputusan** | 3 minggu |
| 6 | UAT, migrasi data, pelatihan, go-live paralel sebulan | 3 minggu |

## Perlu Tindakan Sebelum Deploy

Tiga hal berikut bukan pekerjaan kode. Tanpa ketiganya, modul yang sudah merge tidak akan menghasilkan apa-apa selain penolakan.

- **`MINIO_PROCUREMENT_KEY` belum ada, dan direktorinya belum dibuat di MinIO.** Kunci akses menentukan prefix object, sehingga modul ini butuh direktorinya sendiri: menumpang kunci employee akan mencampur bukti belanja dengan lampiran KPI di satu ruang yang sama. Selama belum dibuat, rute unggah bukti membalas 503 dengan pesan yang menyebut sebabnya, dan sisa procurement-service tetap jalan. Sengaja tidak divalidasi saat boot supaya satu env yang belum dipasang tidak mematikan master pemasok, barang, dan faktur.
- **Paket izin kas kecil harus ditugaskan ke posisi** lewat layar Hak per Posisi. Modul ini tidak punya fallback tier, jadi sebelum penugasan itu ada, **semua orang ditolak**. Itu perilaku yang benar, bukan kerusakan.
- **Master unit kas, kategori belanja, parameter, dan plafon periode berjalan harus diisi.** Plafon yang belum diatur diperlakukan sebagai saldo nol, bukan sebagai tanpa batas.

## Belum Diputuskan (TBD)

- ~~Service mana yang memuat modul ini~~ **Sudah diputuskan: `procurement-service`**, dengan rute berprefix `/kas`. Menghemat satu modul gateway, dan isinya sengaja dipisahkan namanya karena modul ini bukan cermin Accurate seperti sisa service itu.
- Penomoran pengajuan (penomoran transaksi sudah ada: `KK-<unit>-<YYYYMM>-<urut>`).
- Apakah unggah bukti memakai [[Microservices - File Service]] (batas 4 MB per berkas).

## Dependensi & Integrasi

- [[Microservices - Employee Service]] — divisi, atasan, dan struktur organisasi untuk rantai approval
- [[Microservices - File Service]] — penyimpanan bukti dan nota
- [[Microservices - Procurement Service]] — pola setelan modul dan penomoran yang dapat dicontoh; juga satu-satunya service yang pernah menulis ke Accurate
- [[CORE - RBAC dan Permission Set]] — tujuh peran yang disebut blueprint
- [[External - Accurate]] — tujuan akhir jurnal, bila jalan kedua dipilih

## Dokumen Terkait

- [[GA - Form Pengadaan dan Pengajuan Dana]] — dua form kertas GA yang menjadi bagian alur ini
- [[GA - Procurement System]] — rencana lama pengadaan GA
- [[HRIS - Organization Structure]] — sumber data atasan dan cakupan supervisi
- [[ADR - 0001 Akuntansi via Accurate]] · [[ADR - 0002 Database-per-Service]]
- [[Finance - Big Pictures]] — peta domain Finance
