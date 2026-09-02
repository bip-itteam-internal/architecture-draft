# Finance - Audit Pembukuan Accurate

## Deskripsi

*Pengujian bulanan atas pembukuan PT Bharata Internasional Pharmaceutical di Accurate Online, dijalankan sebagai modul ERP yang menarik kedua sisi pembanding lewat pembaca yang sudah ada lalu menyajikan selisihnya sebagai kertas kerja. Sistem membandingkan; auditor menilai, menelusuri, dan menandatangani. Keputusan arsitekturnya di [[ADR - 0073 Modul Audit Memakai Pembaca Accurate yang Ada dan Memegang Kertas Kerjanya Sendiri]].*

- **Status**: 🟡 Konsep — kode belum ada; tiga gerbang kelayakan belum dijalankan
- **Implementasi**: TBD (`bip-erp/services/audit/`, belum dibuat)

## Latar Belakang

Auditnya sudah berjalan manual dan prosedurnya sudah terbukti sekali dipakai, dengan kertas kerja posisi **6 Agustus 2026** sebagai baseline. Yang membakar waktu bukan pengujiannya melainkan perakitan kertas kerjanya: menarik data dari Accurate, mencocokkan, dan menyusun ulang dari nol tiap bulan.

Baseline itu memunculkan beberapa angka yang jadi contoh uji yang berbunyi: selisih buku besar terhadap buku pembantu piutang Rp 954,7 juta, saldo barang dalam proses minus Rp 164 juta, harga pokok penjualan 13,4% dari pendapatan, PPN keluaran Rp 295 juta atas pendapatan Rp 70,6 miliar, 13 akun tanpa 2FA, dan proses akhir bulan tertinggal dua bulan.

**Independensi justru menguat, bukan melemah.** Dokumen prosedurnya menulis bahwa otomasi tidak memperbaiki independensi karena datanya tetap diekspor manusia. Itu benar untuk ekspor Excel, tidak berlaku di sini: ERP menarik lewat kredensial sistem, sehingga angka yang diperiksa tidak pernah melewati tangan divisi yang diaudit.

## Ruang Lingkup / Cakupan (business view)

### Sembilan modul pengujian

| Modul | Cakupan | Keadaan sumber data |
|---|---|---|
| A | Kas & Bank | Sebagian. Saldo akun kas/bank per tanggal dan buku besar kas kecil ada. **Rekonsiliasi rekening koran terhadap buku besar belum ada rencananya sama sekali.** |
| B | Piutang & Penjualan | Sebagian. Umur piutang B2B + DSO tersedia; posisi per akhir bulan historis tersedia terpisah. |
| C | Persediaan & Produksi | Sebagian tipis. Saldo stok tersalin tiap 30 menit; kartu stok **mutasi** belum pernah ditarik. |
| D | Pembelian & Utang | Sebagian. Umur utang tayang, 139 pemasok tercermin, rantai Pesanan → Penerimaan tersambung. **Penerimaan → Faktur tidak tersambung.** |
| E | Aset Tetap | Paling siap. 371 aset tersalin harian, rekonsiliasi ERP↔Accurate bertoleransi 1%. |
| F | Jurnal & Integritas | Sebagian. Sekitar 96 ribu jurnal berhalaman + buku besar per akun. Jejak pelaku belum terbukti ada. |
| G | Hak Akses & Konfigurasi | Kosong. Endpoint matriks hak akses terdaftar di schema tetapi belum pernah dipanggil. |
| H | Pajak | Sebagian. PPN masukan tersalin harian; PPN keluaran dan rekonsiliasi SPT belum ada. |
| I | Transaksi Antar-Entitas | Terkunci [[ADR - 0068 Buku Besar Konsolidasi 40 CV di Luar Accurate]]. |

### 48 uji menurut asal sisi pembandingnya

Pengelompokan ini yang menentukan kekuatan tiap uji, bukan kecanggihannya.

| Kelompok | Sisi pembandingnya | Jumlah | Catatan |
|---|---|---|---|
| 1 | Dari luar perusahaan (rekening koran, jawaban pelanggan, hitung fisik, akta) | 12 | 8 campuran, 4 manual. **Paling kuat**, tak seorang pun di dalam bisa mengarangnya. |
| 2 | Dokumen internal di luar Accurate (surat jalan, berita acara, perintah kerja) | 8 | 7 campuran, 1 manual. Bisa dipalsukan tapi meninggalkan jejak fisik. |
| 3 | Kedua sisi dari dalam Accurate | 13 | 12 sistem, 1 campuran. **Paling cepat, paling lemah.** |
| 4 | Pembandingnya aturan, bukan dokumen | 15 | 12 sistem, 3 campuran. Bergantung ambang yang disepakati lebih dulu. |

⛔ **Kelompok 3 tidak boleh jadi ringkasan teratas layar.** Kedua sisinya satu sumber, jadi pembukuan yang dirapikan secara utuh lolos seluruhnya tanpa memunculkan apa pun. Layar yang membuka dengan dua belas uji hijau memproduksi rasa aman yang tidak dijamin ujinya.

### Dari 24 uji bertanda Sistem, lima belum terbukti mungkin

- **15** sumbernya sudah ditarik ERP hari ini.
- **4** endpointnya ada tetapi belum pernah dipanggil: kartu stok mutasi, kecocokan tiga dokumen, waktu pembuatan transaksi, konfigurasi sistem (yang terbukti tersedia baru matriks hak akses; lock period dan 2FA belum ditemukan di schema).
- **5** bergantung Log Aktivitas yang belum terbukti terekspos: penghapusan bukti kas keluar, penghapusan jurnal, perubahan harga beli, pembuat lawan penyetuju, dan sebaran aktivitas pengguna.

### Yang TIDAK dicakup

- **Pembukuan 40 CV.** Penjualan ke konsumen akhir, sebagian besar beban iklan, dan payroll advertiser ada di sana. Lihat [[APP - Buku Besar Konsolidasi CV FINCON]].
- **Kesimpulan kecurangan.** Modul menunjukkan selisih lalu berhenti; membedakan kelalaian dari kesengajaan menuntut bukti niat.
- **Sembilan prosedur yang menuntut kehadiran fisik, korespondensi resmi, atau tanda tangan.**

## Alur Bulanan

- **H+1** — verifikasi Modul G lebih dulu. Selama pembatasan tanggal transaksi terbuka dan hak hapus melekat, bukti yang dikejar modul lain masih bisa berubah di tengah pengujian.
- **H+2** — penarikan otomatis lewat kredensial sistem.
- **H+3** — uji berjalan; yang berbunyi naik ke atas.
- **H+4 sampai H+7** — penelusuran manusia ke dokumen sumber, lalu klarifikasi ke auditee.
- **H+8** — laporan ditandatangani dan diserahkan ke Direktur.

Pengisian berlangsung berhari-hari, sehingga kertas kerja **wajib bisa disimpan sebagian**. Ini salah satu alasan form-builder tidak dipakai (ADR-0073 §2).

## Persona / Pengguna

| Persona | Peran & Divisi | Akses / RBAC | Device |
|---|---|---|---|
| Auditor internal | Posisinya **belum ada**; direncanakan | modul `audit` (baru) | Web ERP |
| Reviewer silang | Staf dari divisi di luar yang diaudit, sementara auditor belum ada | modul `audit` (baru) | Web ERP |
| Direktur | Penerima laporan | modul `audit` (baru) | Web ERP |

- **Tujuan**: memastikan ketepatan angka, mendeteksi indikasi kecurangan, dan menutup peluangnya.
- **Pain point**: kertas kerja dirakit ulang dari nol tiap bulan, dan datanya diminta dari divisi yang sedang diperiksa.
- **Aksi utama**: meninjau baris yang berbunyi, menelusuri ke dokumen sumber, menandai wajar dengan alasan tertulis, atau menaikkannya jadi temuan.

⛔ **Finance bukan pemakai modul ini**, melainkan pihak yang dimintai klarifikasi. Pelaksana audit tidak boleh berasal dari divisi yang diaudit.

## Aturan Kolom yang Wajib Dibaca Sebelum Merancang Layar

Aturan berikut selama ini hanya hidup sebagai komentar Go, sehingga siapa pun yang merancang layar dari dokumentasi tidak punya cara mengetahuinya. Salah memakainya menghasilkan **angka salah yang masuk akal**, tanpa galat dan tanpa test merah.

- ⛔ **Aset tetap: `kuantitas` adalah `quantityAvailable`** (sisa, sudah dikurangi pelepasan), **bukan** `quantity` (perolehan awal, tidak pernah turun saat disposal). `biaya_perolehan` juga basis current. **Mencampur biaya current dengan kuantitas perolehan salah dua kali.**
- ⛔ **`BelumDidepresiasi` adalah HIMPUNAN BAGIAN dari `TotalAset`**, bukan kolom sejajar. Aset draft dikecualikan karena penyusutannya selalu nol; memasukkannya membesarkan angka ini secara palsu.
- ⛔ **Piutang historis: `lebih14` ⊇ `lebih60` ⊇ `lebih90` BERSARANG. Jangan dijumlahkan.**
- ✅ Umur piutang B2B: ember `0-30`, `31-60`, `61+` adalah **partisi saling lepas** yang menjumlah ke total. Boleh dijumlahkan.
- ⛔ **Umur utang: `TanpaJatuhTempo` wajib dipisah, jangan dilebur.** Menebaknya ke "belum jatuh tempo" menyembunyikan utang yang mungkin sudah lewat; membuangnya membuat jumlah ember tak lagi sama dengan total.
- ⛔ **Umur utang: `TotalUangMuka` berpopulasi SAMA dengan `TotalNominal` tetapi berdimensi BERBEDA.** Ia bukan subset dan bukan komponen; menjumlahkannya ke ember mana pun menghitung rupiah yang sama dua kali.
- ⛔ **PPN: `TotalDPP` dan `TotalPPN` dihitung HANYA dari subset `Taxable`.** `JumlahFaktur` adalah induk = `Taxable` + `NonTaxable`. Faktur non-taxable dicacah supaya cakupannya terlihat, tetapi nilainya bukan objek pajak.
- ⛔ **Jurnal: `Amount` + `AmountType` adalah SATU nilai bertanda implisit**, bukan dua kolom debit dan kredit yang sejajar.
- ⛔ **Buku besar per akun: `Nominal` adalah turunan bertanda `Debit − Kredit`.** Akun beban sesekali menerima kredit — pengembalian uang — dan memakai sisi debit saja membuat beban tampak lebih besar tanpa satu pun galat.
- ⛔ **Realisasi per departemen wajib `glaccount/get-balance.do`, BUKAN `get-pl-account-amount.do`.** Yang kedua **mengabaikan `departmentName` diam-diam**: kontrol negatif dengan nama departemen ngawur tetap mengembalikan angka penuh, sehingga tiap departemen menampilkan total seluruh perusahaan dan variansnya tampak wajar padahal palsu.
- ⚠️ **`salinan_kosong: true` berarti belum pernah disinkron, BUKAN nilai nol.** Berlaku untuk aset tetap dan PPN masukan.

## Konsumen Data

- [[APP - Web ERP]] — layar kertas kerja dan register temuan (baru)
- Direktur — laporan bulanan; penerimanya orang, bukan sistem

## Kendala

- **Master pemasok tidak menyimpan nomor rekening sama sekali.** Dua pengujian bersandar padanya sebagai sumbu silang dan karena itu tidak dapat dijalankan dengan data yang ada. Sumbu yang tetap bisa dipakai: NPWP, NIK, nama, alamat, telepon, email.
- **Schema resmi Accurate tidak lengkap**, jadi ketiadaan di sana bukan bukti. Tiga endpoint yang dipanggil produksi hari ini tidak terdaftar di sana.
- **Limiter Accurate 6 permintaan per detik dibagi lintas service**, dan sudah ada tiga klien terpisah. Ini alasan modul audit tidak memegang kredensial Accurate sendiri.
- **Pemakai utamanya belum ada.** Rancangan layar harus tetap masuk akal untuk review silang antar-divisi sampai posisi auditor terisi.

## Belum Diputuskan (TBD)

- Apakah Accurate mengirim jejak pelaku pada dokumennya. **Lima uji berdiri di atas jawabannya.** Probe `cmd/incaudit` sudah ada, hasilnya belum pernah dicatat.
- Apakah `access-privilege/list.do` benar-benar dapat ditarik. Seluruh Modul G berdiri di atasnya.
- Apakah dokumen Bayar Uang di Accurate membawa rekening penerima.
- Ambang tiap uji yang pembandingnya aturan (batas nilai persetujuan, umur uang muka, kebijakan diskon) — dan sebagiannya menuntut kebijakan tertulis yang belum ada.
- Kapan cakupan diperluas ke pembukuan 40 CV, yang menunggu [[ADR - 0068 Buku Besar Konsolidasi 40 CV di Luar Accurate]] diputuskan.

## Dokumen Terkait

- [[ADR - 0073 Modul Audit Memakai Pembaca Accurate yang Ada dan Memegang Kertas Kerjanya Sendiri]]
- [[ADR - 0001 Akuntansi via Accurate]] · [[ADR - 0068 Buku Besar Konsolidasi 40 CV di Luar Accurate]]
- [[API - Integration Service]] · [[Microservices - Integration Service]] · [[External - Accurate]]
- [[Finance - Big Pictures]] · [[Finance - Rancangan Finance Service]] · [[Finance - Dashboard per Posisi (FAT)]]
- [[APP - Buku Besar Konsolidasi CV FINCON]] · [[CORE - RBAC dan Permission Set]]
