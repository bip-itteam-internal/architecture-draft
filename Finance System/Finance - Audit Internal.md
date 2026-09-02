# Finance - Audit Internal

## Deskripsi

*Pengujian bulanan atas pembukuan PT Bharata Internasional Pharmaceutical, dijalankan sebagai modul di dalam finance-service yang menarik kedua sisi pembanding lewat pembaca yang sudah ada lalu menyajikan selisihnya sebagai kertas kerja. Sistem membandingkan; auditor menilai, menelusuri, dan menandatangani. Sumbernya BUKAN selalu Accurate — dari 36 pengujian, sisi bersumber Accurate justru minoritas.*

- **Status**: ⚠️ **Implemented (ada catatan)** — backend fase 1 selesai & ber-test di branch `feat/finance-audit-internal`; **belum di-deploy, belum ada layar, belum pernah dijalankan lewat gateway**
- **Implementasi**: [[Microservices - Procurement Service]] dan [[Microservices - Integration Service]] sebagai sumber; modulnya sendiri di `bip-erp/services/finance/audit_*.go`
- **Keputusan**: [[ADR - 0073 Modul Audit Internal di finance-service dan Kertas Kerja yang Dipegang Sendiri]]

## Latar Belakang

Auditnya sudah berjalan manual dan prosedurnya sudah terbukti sekali dipakai, dengan kertas kerja posisi **6 Agustus 2026** sebagai baseline. Yang membakar waktu bukan pengujiannya melainkan perakitan kertas kerjanya: menarik data, mencocokkan, dan menyusun ulang dari nol tiap bulan.

Baseline itu memunculkan angka yang jadi contoh uji yang berbunyi: selisih buku besar terhadap buku pembantu piutang Rp 954,7 juta, saldo barang dalam proses minus Rp 164 juta, harga pokok penjualan 13,4% dari pendapatan, PPN keluaran Rp 295 juta atas pendapatan Rp 70,6 miliar, 13 akun tanpa 2FA, dan proses akhir bulan tertinggal dua bulan.

**Independensi justru menguat.** Dokumen prosedurnya menulis bahwa otomasi tidak memperbaiki independensi karena datanya tetap diekspor manusia. Itu benar untuk ekspor Excel, tidak berlaku di sini: ERP menarik lewat kredensial sistem, sehingga angka yang diperiksa tidak pernah melewati tangan divisi yang diaudit.

## Ruang Lingkup / Cakupan

### 36 uji, tiga kelompok menurut asal sisi pembandingnya

Pengelompokan ini yang menentukan kekuatan tiap uji, bukan kecanggihannya.

| Kelompok | Sisi pembandingnya | Jumlah | Kekuatannya |
|---|---|---|---|
| 1 | Dari luar perusahaan: rekening koran, jawaban pelanggan, hitung fisik, akta | 12 (8 campuran, 4 manual) | **Paling kuat.** Tak seorang pun di dalam Bharata bisa mengarangnya |
| 2 | Dokumen internal di luar Accurate: surat jalan, berita acara, perintah kerja, PO dari CV | 8 (7 campuran, 1 manual) | Bisa dipalsukan, tapi menuntut usaha dan meninggalkan jejak fisik |
| 3 | Pembandingnya **aturan**, bukan data: logika akuntansi, ambang batas, standar konfigurasi Direksi | 16 (12 sistem, 4 campuran) | Bertahan menghadapi pembukuan yang dirapikan utuh |

⛔ **Tiga belas uji yang membandingkan neraca dengan laporan pendukungnya sudah DIKELUARKAN** — piutang terhadap umur piutang, persediaan terhadap kartu stok, aset tetap terhadap register, dan seterusnya. Kedua sisinya sama-sama tarikan dari basis data yang sama, sehingga pihak yang mampu mengubah pembukuan secara utuh tidak tertangkap di sana. Hasilnya cepat dan rapi, tapi keyakinan yang diberikannya semu.

⚠️ **Konsekuensi yang harus disadari:** dua dari empat temuan utama kertas kerja 6 Agustus lahir dari uji yang dikeluarkan itu (selisih piutang Rp 954,7 juta dan PPN keluaran 0,42%). Kriteria "bertahan menghadapi pembukuan yang dirapikan utuh" tepat untuk menilai kekuatannya sebagai **deteksi**, tetapi ikut membuang kemampuannya sebagai **akurasi** — dan selisih piutang jauh lebih mungkin lahir dari kesalahan pembukuan daripada kecurangan. **Belum diputuskan** apakah kelompok itu dihidupkan kembali sebagai kelompok "konsistensi internal" berlabel jujur; lihat TBD.

### Tiap uji punya kolom tujuan dan kondisi ideal

- **Tujuan** mengacu tiga sasaran yang ditetapkan: **akurasi** (ketepatan angka), **deteksi** (indikasi kecurangan), **mitigasi** (menutup peluang). Yang pertama disebut adalah sasaran utamanya.
- **Kondisi ideal** menyatakan hasil yang dianggap bersih. Tanpanya, tiap uji butuh penafsir untuk memutuskan apa yang dianggap bersih, dan penafsirnya berganti tiap bulan. Setiap penyimpangan dari kondisi ideal jadi calon temuan.

### Enam uji sudah punya penjalan otomatis

| Uji | Sisi A | Sisi B | Keadaan |
|---|---|---|---|
| Silang pemasok terhadap karyawan | ERP procurement | ERP employee | Menunggu dua endpoint dibangun |
| Saldo kas berjalan tidak negatif | Accurate, buku besar per akun | aturan | Jalan, menunggu setelan akun |
| Barang dalam proses tidak negatif | Accurate, saldo akun | aturan | Jalan, menunggu setelan akun |
| Hitung ulang penyusutan | Accurate, register aset | aturan | Jalan |
| Deskripsi jurnal | Accurate, jurnal umum | standar kelengkapan | Jalan |
| Jurnal manual besar | Accurate, jurnal umum | dokumen sumber | Pemilihan jalan; pembandingnya menunggu manusia |

Tiga puluh sisanya **terdaftar dan terbit di kertas kerja** berkeadaan `belum_diimplementasi`. Uji yang hilang dari daftar akan terbaca sebagai uji yang lolos, dan itu kelas kesalahan paling mahal di modul ini.

### Yang TIDAK dicakup

- **Pembukuan 40 CV.** Terkunci [[ADR - 0068 Buku Besar Konsolidasi 40 CV di Luar Accurate]]; sistemnya di [[APP - Buku Besar Konsolidasi CV FINCON]].
- **Kesimpulan kecurangan.** Modul menunjukkan selisih lalu berhenti.
- **Sembilan prosedur yang menuntut kehadiran fisik, korespondensi resmi, atau tanda tangan.**

## Sampling: sepuluh uji, dan separuhnya justru tidak boleh acak

Dari 36 uji, **sepuluh menuntut pemilihan sampel**; 26 sisanya atas populasi penuh. Nol dari 16 uji kelompok 3 butuh sampling, dan itu imbalan terbesar otomasi: sampling ada karena manusia tak sanggup memeriksa semuanya, bukan karena memeriksa sebagian lebih baik.

⚠️ **Acak dan terarah menjawab pertanyaan yang BERBEDA.** Lima menuntut acak (konfirmasi saldo pelanggan, stock opname, cek fisik aset, retur penjualan, penyesuaian persediaan) karena kesimpulannya diekstrapolasi ke populasi dan karena yang diperiksa tak boleh bisa menebak. Lima lagi justru harus terarah (jurnal manual besar, kapitalisasi versus beban, pisah batas penjualan, varian produksi, penjualan PT ke CV) karena yang dicari memang yang bernilai besar atau berisiko. Sampel acak untuk "20 jurnal terbesar" akan melewatkan jurnal terbesar.

**Cash opname butuh waktu yang acak, bukan item yang acak.** Ia menghitung seluruh kas; yang harus tak terduga adalah harinya, dan keacakan itu gampang hilang begitu jadwalnya tersimpan di kalender yang bisa dilihat orang.

**Ukuran sampel adalah master data Direksi**, berlantai 5 untuk metode acak, berbenih tak tertebak, dan berjejak. Yang tersimpan bukan hanya yang terpilih melainkan juga ukuran populasi, metode, dan benihnya — tanpa ketiganya sampel tak bisa direproduksi dan auditor tak punya cara membuktikan ia tidak memilih yang mudah.

## Alur Bulanan

- **H+1** — verifikasi Modul G lebih dulu. Selama pembatasan tanggal transaksi terbuka dan hak hapus melekat, bukti yang dikejar modul lain masih bisa berubah di tengah pengujian.
- **H+2** — penarikan otomatis lewat kredensial sistem. Kertas kerja dibuka tanggal 6, bukan 1: pemeriksaan berjalan atas bulan yang **sudah** ditutup.
- **H+3** — uji berjalan.
- **H+4 sampai H+7** — penelusuran manusia ke dokumen sumber, lalu klarifikasi ke auditee.
- **H+8** — laporan ditandatangani dan diserahkan ke Direktur. Periode yang sudah diterbitkan **menolak ditarik ulang**.

Pengisian berlangsung berhari-hari, sehingga kertas kerja **wajib bisa disimpan sebagian**. Ini salah satu alasan form-builder tidak dipakai.

## Persona / Pengguna

| Persona | Peran & Divisi | Akses / RBAC | Device |
|---|---|---|---|
| Auditor internal | Posisinya **belum ada**; direncanakan | `audit_auditor` (view, tinjau, terbitkan) | Web ERP |
| Reviewer silang | Staf dari divisi di luar yang diaudit | `audit_auditor` | Web ERP |
| Direktur | Penerima laporan, penyetel ukuran sampel | `audit_direksi` (view, master.save) | Web ERP |

- **Tujuan**: memastikan ketepatan angka, mendeteksi indikasi kecurangan, dan menutup peluangnya.
- **Pain point**: kertas kerja dirakit ulang dari nol tiap bulan, dan datanya diminta dari divisi yang sedang diperiksa.
- **Aksi utama**: meninjau baris yang berbunyi, menelusuri ke dokumen sumber, menandai wajar dengan alasan tertulis, atau menaikkannya jadi temuan.

⛔ **Finance bukan pemakai modul ini**, melainkan pihak yang dimintai klarifikasi.
⛔ **Direktur tidak meninjau, auditor tidak menyetel ukuran sampel.** Yang menetapkan beban pemeriksaan bukan yang mengerjakannya.

## Aturan yang Wajib Dibaca Sebelum Merancang Layar

Aturan berikut selama ini hanya hidup sebagai komentar Go, sehingga siapa pun yang merancang layar dari dokumentasi tidak punya cara mengetahuinya. Salah memakainya menghasilkan **angka salah yang masuk akal**, tanpa galat dan tanpa test merah.

### Semantik kolom

- ⛔ **Aset tetap: `kuantitas` adalah `quantityAvailable`** (sisa, sudah dikurangi pelepasan), **bukan** `quantity` (perolehan awal). `biaya_perolehan` juga basis current. **Mencampur biaya current dengan kuantitas perolehan salah dua kali.**
- ⛔ **`BelumDidepresiasi` HIMPUNAN BAGIAN dari `TotalAset`.** Aset draft dikecualikan; penyusutannya selalu nol.
- ⛔ **Piutang historis: `lebih14` ⊇ `lebih60` ⊇ `lebih90` BERSARANG. Jangan dijumlahkan.**
- ✅ Umur piutang B2B: ember `0-30`, `31-60`, `61+` **partisi saling lepas**. Boleh dijumlahkan.
- ⛔ **Umur utang: `TanpaJatuhTempo` wajib dipisah**, dan **`TotalUangMuka` berpopulasi SAMA tetapi berdimensi BERBEDA** — bukan subset, bukan komponen.
- ⛔ **PPN: `TotalDPP` dan `TotalPPN` HANYA dari subset `Taxable`.**
- ⛔ **Jurnal: `Amount` + `AmountType` adalah SATU nilai bertanda implisit**, bukan dua kolom sejajar.
- ⛔ **Buku besar per akun: `Nominal` turunan bertanda `Debit − Kredit`.** Akun beban sesekali menerima kredit.
- ⛔ **Realisasi per departemen wajib `glaccount/get-balance.do`**, bukan `get-pl-account-amount.do` yang mengabaikan `departmentName` diam-diam.

### Semantik keadaan baris

- ⛔ **Tidak ada keadaan "kosong".** Penarikan yang gagal berkeadaan `gagal_tarik` beserta sebabnya, bukan bersih bernilai nol.
- ⛔ **Vonis manusia (`keadaan_tinjauan`) hidup DI LUAR hasil mesin**, dan yang dibaca layar `KeadaanEfektif()` — vonis menang atas keadaan mesin. Menyalin urutan menang itu ke sisi layar melahirkan sumber kebenaran kedua.
- ⛔ **Frontend WAJIB membaca daftar 36 uji dari `GET /audit/uji`**, jangan menyalinnya. Salinan di layar menyimpang jadi baris yang tampil tanpa pernah dijalankan.
- ⚠️ **Hasil kelompok 3 tidak boleh jadi ringkasan teratas**, dan urutan daftar menaikkan kelompok 1. Layar yang membuka dengan uji hijau memproduksi rasa aman yang tidak dijamin ujinya.

## Konsumen Data

- [[APP - Web ERP]] — layar kertas kerja dan register temuan (**belum ada**, fase 2)
- Direktur — laporan bulanan; penerimanya orang, bukan sistem

## Kendala

- **Master pemasok tidak menyimpan nomor rekening sama sekali.** Sumbu silang yang dipakai: NPWP, NIK, nama, alamat, telepon, email. Kondisi ideal uji itu wajib menyebut batasnya, kalau tidak laporannya terbaca sebagai "rekening sudah diperiksa dan bersih".
- **Schema resmi Accurate tidak lengkap**; tiga endpoint yang dipanggil produksi tidak terdaftar di sana. Ketiadaan di schema bukan bukti.
- **Limiter Accurate 6 permintaan per detik dibagi lintas service**, dan sudah ada tiga klien terpisah.
- **`finance-service` tidak ada di `docker-compose.dev.yml`**, jadi modul ini belum bisa dicoba lewat gateway di mana pun.
- **Pemakai utamanya belum ada.**

## Belum Diputuskan (TBD)

- Apakah Accurate mengirim jejak pelaku pada dokumennya. **Menyandera dua uji** (waktu pembuatan transaksi, sebaran aktivitas pengguna).
- Apakah `access-privilege/list.do` benar-benar dapat ditarik. **Menyandera seluruh Modul G**; lock period, konfigurasi penyetuju, dan status 2FA belum ditemukan di schema mana pun.
- Apakah dokumen Bayar Uang membawa rekening penerima.
- Apakah tiga belas uji konsistensi internal dihidupkan kembali sebagai kelompok berlabel jujur, mengingat dua temuan utama baseline lahir dari sana.
- Angka kapasitas produksi normal PSAK 14 untuk uji alokasi biaya konversi — tidak ada di sistem mana pun, penetapannya keputusan Finance.
- Ambang tiap uji yang pembandingnya aturan (batas nilai persetujuan, kebijakan diskon), sebagiannya menuntut kebijakan tertulis yang belum ada.
- Kapan cakupan diperluas ke pembukuan 40 CV.

## Dokumen Terkait

- [[ADR - 0073 Modul Audit Internal di finance-service dan Kertas Kerja yang Dipegang Sendiri]]
- [[ADR - 0001 Akuntansi via Accurate]] · [[ADR - 0068 Buku Besar Konsolidasi 40 CV di Luar Accurate]]
- [[API - Integration Service]] · [[Microservices - Integration Service]] · [[External - Accurate]]
- [[Finance - Big Pictures]] · [[Finance - Rancangan Finance Service]] · [[Finance - Dashboard per Posisi (FAT)]]
- [[APP - Buku Besar Konsolidasi CV FINCON]] · [[CORE - RBAC dan Permission Set]]
