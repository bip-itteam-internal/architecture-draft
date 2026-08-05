## Deskripsi

*Modul kas kecil per divisi beserta jalur pengajuan budget, menggantikan aturan yang kini berjalan lewat kesepakatan lisan dan chat. **Lintas divisi**, bukan fitur satu departemen: Finance yang menetapkan plafon dan aturannya, tiap divisi yang memakainya. Dokumen ini menggabungkan blueprint dari Finance dengan hasil pemeriksaan langsung ke data produksi, supaya lubang datanya terlihat sebelum ada yang mulai menulis kode.*

- **Status**: ⚠️ Pondasi aturan **sudah merge** (PR #986, 5 Agustus 2026), **belum deploy** dan **belum punya satu pun endpoint**. Yang ada baru mesin perhitungannya. Empat lubang data dan tiga tabrakan arsitektur masih menghalangi bagian berikutnya.
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

## Sudah Ada di Kode (PR #986, merge 5 Agustus 2026)

Seluruhnya **fungsi murni** di `bip-erp/services/procurement/`: tanpa Mongo, tanpa HTTP, tanpa jam dinding. Belum ada handler, koleksi, rute, maupun katalog izin. Bagian yang menentukan pengeluaran seseorang diterima atau ditolak sengaja dibuat dapat dibaca dan diuji tanpa menyalakan apa pun.

| Berkas | Isi |
|---|---|
| `kas_periode.go` | Batas bulan WIB, `RentangPeriodeKas` dan `PeriodeKasDari` |
| `kas_parameter.go` | Parameter berversi, `ParameterBerlaku` memilih versi menurut tanggal |
| `kas_plafon.go` | `PlafonEfektif` (tetap vs dinamis) dan `SisaSaldo` |
| `kas_aturan.go` | `PutuskanJalurKas` untuk R-01 sampai R-07 dan R-09, `DugaPemecahanTransaksi` untuk R-08 |

Kesepuluh test case penerimaan blueprint §9 ditulis apa adanya sebagai tabel test dan seluruhnya lulus.

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

### 1. Tiga dari tujuh divisi tidak cocok dengan master data

| Blueprint | Yang ada di sistem | Karyawan |
|---|---|---:|
| BH Beautyhacks | `Beauty Hacks` (ejaan berbeda) | 48 |
| KY Kyura | `Kyura` | 31 |
| GA General Affair | `General Affair` | 21 |
| PU Purchasing | `Procurement` (nama berbeda) | 2 |
| SK Sekretariat | `Kesekretariatan` (nama berbeda) | 11 |
| **GTJ Gudang TJ** | **tidak ada** | — |
| **BC Bharata Club** | **tidak ada** | — |

Gudang TJ dan Bharata Club belum menjadi departemen di sistem sama sekali. Bila plafon dikunci ke nama divisi, tiga baris ini gagal sejak hari pertama.

Catatan tambahan: `master_department` berisi **11** entri, sedangkan `work_data` memakai **12** nilai departemen. `Human Resource` (7 orang) ada di data karyawan tetapi **tidak ada di master departemen**, sehingga dropdown apa pun yang bersumber dari master akan melewatkannya.

### 2. Tujuh departemen tidak punya plafon

Finance (19), Manufaktur (36), Percetakan (13), Tech Development (11), Human Resource (7), Quality (6), Marketing Offline Distribution (1). Totalnya **93 dari 206 karyawan**, atau 45 persen.

Perlu dipastikan ke Finance: memang tidak punya kas kecil, atau terlewat dari daftar? Bila memang tidak punya, R-03 akan memblokir mereka dengan pesan "sisa saldo 0" yang membingungkan; lebih baik jalur kas kecilnya tidak ditampilkan sama sekali.

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
| 5 | Bharata Club perlu pagar maksimum? | Tanpa pagar | Divisinya belum ada di sistem |
| 6 | Selain Purchasing dan Gudang TJ benar tidak boleh top-up? | Tidak boleh | Gudang TJ belum ada di sistem |
| 7 | Larangan aset lewat kas kecil: hanya BH dan KY, atau semua? | Sebaiknya semua | — |
| 8 | Batas nilai barang disebut aset | Perlu angka Finance | Register asetnya juga belum ada |
| 9 | Berapa hari maksimal unggah bukti? | 3 hari kerja | — |
| 10 | Siapa approver definitif tiap level? | Perlu struktur resmi | Baru 9 dari 12 departemen punya penanda atasan; 83 dari 206 karyawan punya atasan langsung |

Ditambah tiga pertanyaan baru dari pemeriksaan sistem:

11. **Gudang TJ dan Bharata Club** didaftarkan sebagai departemen di master data, atau diperlakukan sebagai unit di bawah departemen yang sudah ada?
12. **Tujuh departemen tanpa plafon** memang tidak punya kas kecil, atau terlewat?
13. **Jurnal**: ERP berhenti di pencatatan, atau menulis ke Accurate?

## Tahapan Implementasi

Blueprint mengusulkan enam fase, kurang lebih 16 minggu. Satu perubahan yang perlu dipertimbangkan: **Fase 1 diperluas dengan pembenahan master data**, karena plafon tidak dapat diisi sebelum divisi dan penanda atasan beres.

| Fase | Ruang lingkup | Catatan |
|---|---|---|
| 0 | Bereskan master divisi (Gudang TJ, Bharata Club, penyeragaman nama) dan penanda atasan minimal untuk General Affair dan Procurement | **Tambahan**, bukan dari blueprint. Pekerjaan data, bukan kode. **Belum dikerjakan** |
| 1 | Master data (divisi, plafon, kategori, parameter) + dashboard saldo | 2 minggu. **Mesin aturannya sudah ada** (PR #986); sisanya koleksi, endpoint, dan layar |
| 2 | Transaksi kas kecil + R-01, R-03, R-06 + unggah bukti | 3 minggu |
| 3 | Modul pengajuan + approval berjenjang + R-02, R-07 | 3 minggu |
| 4 | Top-up (R-05) + tutup buku bulanan + laporan | 2 minggu |
| 5 | Register aset + R-08, R-09. **Integrasi jurnal menunggu keputusan** | 3 minggu |
| 6 | UAT, migrasi data, pelatihan, go-live paralel sebulan | 3 minggu |

## Belum Diputuskan (TBD)

- Service mana yang memuat modul ini. Karena lintas divisi dan aturannya milik Finance, menumpang service GA sudah tidak tepat. Pilihan dan preseden dibahas di [[GA - Form Pengadaan dan Pengajuan Dana]].
- Penomoran transaksi dan pengajuan.
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
