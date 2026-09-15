# Finance - Audit Internal

## Deskripsi

*Pemeriksaan bulanan atas pekerjaan Accounting dan Tax PT Bharata Internasional Pharmaceutical lewat 38 item uji petik dua arah. Tiap item diperiksa auditor dengan menelusuri sampel ke dokumen, lalu disimpulkan Wajar atau Temuan beserta sampel dan catatannya. Sistem menyiapkan kertas kerja, memaksa bukti pemeriksaan tertulis, dan menjaga jejaknya; ia tidak menyimpulkan apa pun sendiri. Modulnya hidup di finance-service, layarnya di [[APP - Audit Internal]].*

- **Status**: ⚠️ **Implemented (ada catatan)**. Yang LIVE di prod sejak 2026-09-03 masih **matriks 36 uji** (bip-erp [#1676](https://github.com/bip-itteam-internal/bip-erp/pull/1676) + [#1679](https://github.com/bip-itteam-internal/bip-erp/pull/1679)). Registry **38 item uji petik** ([[ADR - 0098 Audit Internal Beralih ke Uji Petik Dua Arah Manual]]) dikerjakan di branch bip-erp `feat/finance-audit-uji-petik` dan audit-bharata `feat/uji-petik-manual`, **belum merge** per 2026-09-15; merge bip-erp menunggu pemeriksaan data prod (lihat TBD). Paket izin `Audit: *` per pengukuran 2026-09-04 belum ditempel ke posisi mana pun.
- **Implementasi**: modul di `bip-erp/services/finance/audit_*.go`, registry item di `audit_item_petik.go`; layar di repo `audit-bharata` ([[APP - Audit Internal]]). Layar lama di `erp-frontend` dicabut di branch `feat/cabut-audit-internal-erp`, dan alamatnya dialihkan ke aplikasi audit.
- **Keputusan**: [[ADR - 0073 Modul Audit Internal di finance-service dan Kertas Kerja yang Dipegang Sendiri]] (diamandemen [[ADR - 0074 Audit Internal Dipisah jadi Service dan Aplikasi Sendiri]]; §8 diganti ADR 0098) · [[ADR - 0075 Bukti Sisi Lawan Dilampirkan dan Angkanya Dicatat, Pembacaan Otomatis Menyusul]] (§3 diganti ADR 0098) · [[ADR - 0098 Audit Internal Beralih ke Uji Petik Dua Arah Manual]]
- ⛔ **Modul ini AKAN PINDAH** keluar `finance-service` jadi service + database sendiri. Dok ini tetap memegang domainnya, apa pun rumahnya. Papan kerjanya [[ANALISA - Audit Internal Terpisah]].

## Latar Belakang

Auditnya sudah berjalan manual dan prosedurnya sudah terbukti sekali dipakai, dengan kertas kerja posisi **6 Agustus 2026** sebagai baseline. Yang membakar waktu bukan pengujiannya melainkan perakitan kertas kerjanya: menarik data, mencocokkan, dan menyusun ulang dari nol tiap bulan.

Baseline itu memunculkan angka yang jadi contoh uji yang berbunyi: selisih buku besar terhadap buku pembantu piutang Rp 954,7 juta, saldo barang dalam proses minus Rp 164 juta, harga pokok penjualan 13,4% dari pendapatan, PPN keluaran Rp 295 juta atas pendapatan Rp 70,6 miliar, 13 akun tanpa 2FA, dan proses akhir bulan tertinggal dua bulan.

**Sejak 2026-09-15 daftarnya diganti.** Manajemen menyerahkan dokumen "Item Pengecekan Accounting dan Tax": 38 item uji petik yang ditelusuri auditor ke dokumen. Matriks 36 uji sebelumnya hanya punya 6 penjalan otomatis, dan di prod periode 2026-08 hasilnya 32 `belum_diimplementasi` dan 4 `gagal_tarik` (diukur 2026-09-03). Pondasi yang dipilih sengaja manual: vonis Wajar atau Temuan dengan sampel dan catatan wajib, tanpa AI ([[ADR - 0098 Audit Internal Beralih ke Uji Petik Dua Arah Manual]]). Matriks lama beserta aturannya dipindah ke bagian **Arsip** di bawah, tidak dibuang.

**Independensi bergeser tempat.** Matriks lama menarik angka lewat kredensial sistem, sehingga angka yang diperiksa tidak melewati tangan divisi yang diaudit. Item uji petik menaruh independensi di **pembandingnya**: rekening koran, hitung fisik, dashboard platform, dokumen dari kantor pajak, dan untuk gaji, aturan Peraturan Perusahaan serta daftar karyawan HRIS, bukan data yang dipegang Finance.

## Ruang Lingkup / Cakupan

### 38 item uji petik dua arah

| Bagian | Tahap 2: dari sistem ke kenyataan | Tahap 3: dari kenyataan ke sistem | Jumlah |
|---|---|---|---|
| Accounting | 15 | 13 | 28 |
| Tax | 7 | 3 | 10 |

- **Tahap 2** menelusuri catatan ke kenyataannya: apakah yang tercatat itu nyata (saldo ke rekening koran, register aset ke barangnya).
- **Tahap 3** berangkat dari kenyataan ke catatan: apakah yang nyata sudah tercatat (mutasi bank ke jurnal, barang di gudang ke daftar persediaan).
- Tiap item membawa pos, nama, **titik awal**, **pembanding**, **kriteria cocok** ("Dinyatakan cocok bila"), tujuan, sampel yang dituntut, dan metode pemilihan.

⛔ **Daftar lengkapnya hidup di kode, tidak disalin ke dok ini.** Sumbernya `audit_item_petik.go`, dan layar membacanya dari `GET /audit/uji`. Tiga salinan kalimat kriteria (dok, layar, backend) akan menyimpang, padahal kriteria itulah yang disalin ke temuan saat terbit.

### Isi yang disesuaikan dari dokumen sumber

- **Metode per item, bukan satu aturan "semua acak"**: terarah untuk Accounting 18, 19, 20 (barang yang ditunjuk atau dilihat auditor, dan uji pisah batas); populasi penuh untuk Accounting 6, 12, 13, 15 dan Tax 1, 2, 3, 4, 5, 6, 8, 9; acak untuk 23 item sisanya.
- **Tanggal dan nama akun digeneralisasi** ("akhir periode", "bulan sesudah periode", "setiap dashboard iklan"), karena teks item dipakai tiap bulan.
- **Pembanding yang independen dari yang diperiksa**: Accounting 8 menghitung ulang gaji memakai Peraturan Perusahaan, bukan hasil payroll; Accounting 21 membandingkan transfer gaji dengan daftar karyawan HRIS ERP, bukan daftar yang dipegang Finance.
- **Nama pemegang jabatan dan bobot KPI tidak disimpan.**
- ⚠️ **Tax 2 memakai "batas lapor SPT Masa PPh yang berlaku"**, karena tanggalnya belum dikonfirmasi Tax Officer (TBD).

### Lima area di luar lingkup

Dikirim di respons kertas kerja (`di_luar_lingkup`) dan tampil di layar, supaya "tidak diperiksa" tidak terbaca "bersih": **penyusutan**, **utang kepada kreditur**, **ekuitas dan investasi**, **beban dan harga pokok**, dan **arsip transaksi Accounting**. Tiap area membawa kalimat akibatnya; angka laporan satu periode dari dokumen sumber tidak disalin.

### Yang TIDAK dicakup

- **Pembukuan 40 CV.** Terkunci [[ADR - 0068 Buku Besar Konsolidasi 40 CV di Luar Accurate]]; sistemnya di [[APP - Buku Besar Konsolidasi CV FINCON]].
- **Kesimpulan kecurangan.** Modul mencatat kesimpulan auditor per item, bukan kesimpulan atas perusahaan.
- **Deteksi otomatis.** Tak satu item pun punya penjalan; kode penjalan matriks lama disimpan tanpa dipanggil.

## Cara Memeriksa Satu Item

1. Kertas kerja periode disiapkan, oleh penjadwal tanggal 6 atau tombol **Siapkan kertas kerja**. Seluruh baris lahir `belum_diperiksa`.
2. Auditor membuka item dan membaca titik awal, pembanding, kriteria, dan sampel yang dituntut.
3. ⛔ **Penelusuran terjadi di luar sistem**: rekening koran, gudang, dashboard platform, arsip pajak.
4. Auditor kembali ke item, menulis **sampel yang diperiksa beserta cara memilihnya** dan **catatan**, lalu memilih:
   - **Tandai wajar**: tersimpan sebagai tinjauan (`ditinjau_wajar`).
   - **Jadikan temuan**: lewat konfirmasi yang menyebut item dan periodenya, terbit ke register temuan (`jadi_temuan`).
5. Lampiran bukti opsional per item.

Aturannya:

- ⛔ **Sampel dan catatan wajib**, ditegakkan backend (400) dan layar. Vonis tanpa sampel tak bisa diulang siapa pun; vonis tanpa catatan berubah jadi stempel.
- ⛔ **Kriteria temuan disalin dari registry**, bukan dari kiriman klien. Temuan tidak boleh dinilai terhadap aturan yang dikarang penerbitnya.
- ⛔ **Temuan tidak punya jalan hapus.** Menerbitkan ulang item yang sama merevisinya (id `<periode>-<kode>`), dan isi sebelumnya disimpan di jejak beraksi `revisi`.
- ⛔ **Item bertemuan tidak bisa ditandai wajar** (409). Penjaganya ikut di filter tulis, supaya temuan yang terbit di sela pembacaan dan penulisan tidak tertimpa.
- ⛔ **Menjadikan temuan hanya lewat rute temuan** (izin `audit.temuan.terbitkan`). Badan tinjauan yang membawa `jadi_temuan` ditolak.
- ⚠️ **Aturan sampel dokumen sumber hanya petunjuk**: pilih acak bukan yang terbesar, catat cara memilih, catat persen nilai bila sampel jatuh di transaksi kecil, dan **bila satu sampel meleset perluas jadi 10 di pos itu**. Pengingat perluasan tampil di konfirmasi temuan untuk item acak saja; sistem tidak menghentikan auditor yang tidak memperluasnya.

### Keadaan baris

```
belum_diperiksa --(tandai wajar)--> ditinjau_wajar --(jadikan temuan)--> jadi_temuan
belum_diperiksa --(jadikan temuan)-----------------------------------> jadi_temuan
jadi_temuan --(tandai wajar)--> DITOLAK 409, koreksinya lewat revisi temuan
```

Keadaan mesin lain (`menunggu_data`, `gagal_tarik`, `bersih`, `berbunyi`, `belum_diimplementasi`, `tidak_berlaku`) tetap ada di tipe untuk penjalan matriks lama, dan tidak dihasilkan item uji petik.

### Periode yang dibuka sebelum registry diganti

Periode yang sudah dibuka dengan matriks lama menyimpan 36 baris berkode lama. Kertas kerja **hanya menampilkan baris berkode terdaftar**; cacah yang disaring dikirim sebagai `baris_di_luar_daftar`, dan layar menawarkan **Siapkan kertas kerja** untuk menyemai 38 baris baru.

⛔ **Saringan itu senyap di layar**, jadi aman hanya bila baris lama tak memuat tinjauan, temuan, atau bukti. Itu wajib dibuktikan pemeriksaan data prod sebelum merge bip-erp. Register temuan tidak disaring: temuan berkode lama tetap tampil, bertanda item daftar lama.

## ⛔ Taruhannya: temuan modul ini bisa jadi dasar sanksi miliaran

Peraturan Perusahaan Pasal 54 menetapkan denda **Rp 2 miliar** untuk pelanggaran informasi rahasia dan **Rp 5 miliar** untuk penyalahgunaan wewenang, dan menyatakan sanksi itu *"harus tercatat dalam sistem audit"*. Karena itu **angka hasil pembacaan mesin yang tak pernah dikonfirmasi manusia tidak boleh menjadi dasar tunggal sebuah temuan** — berlaku juga untuk pengurai deterministik, bukan cuma untuk model. Sumbernya `mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md`, dan ia menang atas perilaku sistem ([[ADR - 0071 Peta Kepatuhan Peraturan Perusahaan dan Kewajiban ADR untuk Penyimpangan]]).

Taruhan yang sama menjelaskan kenapa vonis manual wajib bersampel dan bercatatan: temuan yang kelak jadi dasar sanksi harus bisa diulang pemeriksaannya oleh orang lain.

## Bukti Sisi Lawan (opsional)

Tempat menaruh bukti sudah ada sejak 2026-09-03 (bip-erp [#1699](https://github.com/bip-itteam-internal/bip-erp/pull/1699) + [#1700](https://github.com/bip-itteam-internal/bip-erp/pull/1700)): prefix MinIO `audit/`, koleksi `audit_bukti`, dan empat rute (unggah, daftar, baca berkas lewat proxy berizin, hapus). Keputusannya di [[ADR - 0075 Bukti Sisi Lawan Dilampirkan dan Angkanya Dicatat, Pembacaan Otomatis Menyusul]].

- Untuk item uji petik lampiran **opsional**; yang wajib tetap sampel dan catatan.
- ⚠️ **Prefix MinIO-nya wajib `audit/` sendiri, jangan menumpang `pajak/`.** Peta akses file-service berbasis prefix, jadi menumpang berarti siapa pun yang boleh membaca arsip pajak ikut boleh membaca rekening koran. Rinciannya: [[Microservices - File Service]].
- Pola unggahnya meniru `services/finance/pajak_arsip.go`: batas 4 MB yang mencerminkan `services/file/main.go`, daftar-izin ekstensi, hex acak pada nama objek.
- Rincian bukti per item terpilih untuk penjalan matriks lama ada di Arsip.

## Sampling

- **Ukuran sampel bagian kalimat item** (mis. "3 rekening dipilih acak", "20 item dipilih acak"), bukan master data. Setelan ukuran sampel milik Direksi berlantai 5 (ADR 0073 §8) **diganti** ADR 0098: rute `PUT /audit/setelan-sampel/:kode` masih ada tetapi menolak item tanpa penjalan, yaitu seluruh 38 item, dan halaman setelannya dicabut.
- **Acak dan terarah menjawab pertanyaan yang berbeda.** Acak dipakai bila kesimpulannya diekstrapolasi ke populasi dan yang diperiksa tak boleh bisa menebak; terarah dipakai bila yang dicari memang barang yang dilihat auditor atau batas periode. Sampel acak untuk "5 surat jalan terakhir sebelum tutup buku" akan melewatkan pisah batasnya.
- ⛔ **Pemilihan sampel tidak tercatat mesin.** Yang tersimpan hanya kalimat sampel dari auditor di tinjauan atau temuan. Benih, ukuran populasi, dan daftar item terpilih tidak disimpan, jadi klaim "sampelnya tidak dipilih yang mudah" bergantung pada kejujuran kalimat itu. `PenarikanSampel` (`audit_sampling.go`) dan koleksi `audit_sampel` dideklarasikan tetapi nol penulis dan nol pembaca (diverifikasi `git grep` 2026-09-03).

## Alur Bulanan

- **Sebelum memeriksa**: pastikan periodenya sudah ditutup. Selama pembatasan tanggal transaksi terbuka dan hak hapus melekat, dokumen yang ditelusuri masih bisa berubah di tengah pemeriksaan.
- **Tanggal 6, 01:00 WIB**: penjadwal membuka kertas kerja bulan sebelumnya. Dibuka tanggal 6, bukan 1: pemeriksaan berjalan atas bulan yang **sudah** ditutup.
- **Hari-hari berikutnya**: auditor memeriksa item satu per satu, lalu klarifikasi ke auditee.
- **Akhir siklus**: laporan diserahkan ke Direktur.

Pengisian berlangsung berhari-hari, sehingga kertas kerja **wajib bisa disimpan sebagian**: tiap item disimpulkan sendiri-sendiri. Ini salah satu alasan form-builder tidak dipakai.

## Layar dan Izin

Layarnya di [[APP - Audit Internal]]: kertas kerja (`/`) dan register temuan (`/temuan`). Halaman setelan sampel dicabut. Menu di [[APP - Web ERP]] dicabut di branch `feat/cabut-audit-internal-erp`, dan alamat lama `/audit*` dialihkan ke aplikasi audit.

### Pemetaan aksi layar → izin

⛔ Aturan ini dulu hanya hidup sebagai gerbang rute di `audit_handler.go`, dan layar pertama yang dirancang dari dokumentasi melewatkannya seluruhnya.

| Aksi di layar | Endpoint | Izin | Auditor | Direksi | Pembaca |
|---|---|---|---|---|---|
| Membaca kertas kerja, register temuan, bukti | `GET /audit/*` | `audit.view` | ✅ | ✅ | ✅ |
| Siapkan kertas kerja | `POST /periode/:periode/tarik` | `audit.tinjau` | ✅ | — | — |
| Tandai wajar (+ sampel, catatan) | `PATCH /periode/:periode/baris/:kode/tinjau` | `audit.tinjau` | ✅ | — | — |
| Jadikan atau revisi temuan (+ sampel, catatan) | `POST /periode/:periode/baris/:kode/temuan` | `audit.temuan.terbitkan` | ✅ | — | — |
| Lampirkan atau hapus bukti | `POST /periode/:periode/baris/:kode/bukti`, `DELETE /bukti/:id` | `audit.tinjau` | ✅ | — | — |

- ⛔ **`audit.tinjau` dan `audit.temuan.terbitkan` BUKAN satu izin.** Paket bisa disusun sendiri: pemegang tinjau saja tidak melihat tombol temuan, dan pada item bertemuan ia melihat kalimat keterangan, bukan isian tanpa tombol.
- ⚠️ **`audit.master.save` tak lagi punya aksi di layar.** Paket `Audit: Direksi` masih memegangnya, tetapi rutenya menolak seluruh item uji petik. Katalog izin sengaja tidak disentuh.
- ⚠️ **Direksi dan Pembaca rutin membuka kertas kerja tanpa izin tulis**, jadi panel mereka hanya-baca. Tombol yang pasti dijawab 403 membuat pemakainya menyimpulkan sistemnya rusak.

Penjaga sebenarnya tetap backend: menyembunyikan menu maupun tombol **bukan keamanan** ([[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]], ditegaskan ulang [[ADR - 0031 Prefix internal Bukan Batas Keamanan]]). Gerbang layar hanya mencegah **alur terputus**.

### Keadaan baris dihitung backend, tidak di layar

Layar membaca `keadaan_efektif` dari respons dan **tidak** menghitung ulang urutan menang antara vonis manusia dan keadaan mesin. Itu satu fakta; dua salinannya pasti menyimpang tanpa satu pun galat.

- ⛔ **Item yang belum diperiksa tidak disembunyikan.** Item yang hilang dari layar terbaca sebagai item yang lolos. Urutannya mengikuti dokumen sumber: bagian, tahap, lalu nomor, bukan menurut keadaan.
- ⛔ **Kalimat cakupan dihitung dari `jumlah_item`, bukan dari jumlah baris yang ada.** Item tanpa baris dihitung belum diperiksa, supaya kertas kerja yang barisnya belum lengkap tak pernah terbaca "seluruhnya wajar".

### Urutan deploy

- Kontraknya berubah (bentuk `GET /audit/uji`, isi `baris`, badan tinjauan dan temuan). Urutannya, dijalankan manusia: **finance-service**, lalu **aplikasi Audit Internal**, lalu **erp-frontend** dengan `NEXT_PUBLIC_AUDIT_URL` terisi sebelum build.
- **Layar baru di atas backend lama**: respons tanpa `jumlah_item` membuat layar menyatakan server belum diperbarui, bukan merender baris matriks.
- **Layar lama di atas backend baru**: tinjauan tanpa sampel ditolak 400. Jeda ini diterima karena pemakai aktif belum ada.

## Persona / Pengguna

| Persona | Peran & Divisi | Akses / RBAC | Device |
|---|---|---|---|
| Auditor internal | Posisinya **belum ada**; direncanakan | `audit_auditor` (view, tinjau, terbitkan) | Web ([[APP - Audit Internal]]) |
| Reviewer silang | Staf dari divisi di luar yang diaudit | `audit_auditor` | Web |
| Direktur | Penerima laporan | `audit_direksi` (view; `master.save` tanpa aksi sejak ADR 0098) | Web |

- **Tujuan**: memastikan ketepatan angka, mendeteksi indikasi kecurangan, dan menutup peluangnya.
- **Pain point**: kertas kerja dirakit ulang dari nol tiap bulan, dan datanya diminta dari divisi yang sedang diperiksa.
- **Aksi utama**: menelusuri sampel tiap item ke dokumen, lalu menyimpulkan Wajar atau Temuan dengan sampel dan catatan.

⛔ **Finance bukan pemakai modul ini**, melainkan pihak yang dimintai klarifikasi.
⛔ **Direktur tidak meninjau.** Yang membaca laporan bukan yang mengerjakan pemeriksaannya.

## Aturan yang Wajib Dibaca Sebelum Merancang Layar

- ⛔ **"Nol temuan" bukan "bulan ini aman".** Kertas kerja yang baru disiapkan berisi 38 item belum diperiksa dan nol temuan. Kalimat pembuka layar mendahulukan temuan, lalu gangguan, lalu belum diperiksa, dan hanya berbunyi wajar bila seluruh item terdaftar sudah dinilai wajar.
- ⛔ **Vonis manusia (`keadaan_tinjauan`) hidup DI LUAR hasil mesin**, dan yang dibaca layar `keadaan_efektif`. Menyiapkan ulang kertas kerja tidak menulis `keadaan_tinjauan`, `tinjauan`, maupun `temuan_id`.
- ⛔ **Frontend WAJIB membaca daftar item dari `GET /audit/uji`**, jangan menyalinnya.
- ⛔ **Area di luar lingkup wajib tampil** di kertas kerja.
- Semantik kolom Accurate untuk penjalan matriks lama ada di Arsip; ia berlaku lagi bila penjalan itu dipasang ulang.

## Konsumen Data

- [[APP - Audit Internal]]: kertas kerja dan register temuan.
- [[APP - Web ERP]]: layar lama (live di prod sejak 2026-09-03), dicabut di branch `feat/cabut-audit-internal-erp`; alamatnya dialihkan ke aplikasi audit.
- Direktur: laporan bulanan; penerimanya orang, bukan sistem.

## Kendala

- ⚠️ **`finance-service` tidak ada di `docker-compose.dev.yml`**, jadi modul ini **tak dapat dicoba di dev sama sekali**. Yang hidup justru PRODUKSI, sehingga percobaan menulis (tandai wajar, terbitkan temuan) tidak punya tempat latihan yang aman.
- **Pemakai utamanya belum ada.**
- Untuk penjalan matriks lama (disimpan, tak dipanggil): master pemasok tidak menyimpan nomor rekening; schema resmi Accurate tidak lengkap; limiter Accurate 6 permintaan per detik dibagi lintas service; `INTEGRATION_SERVICE_KEY` kosong di dev, terisi di prod.

## Belum Diputuskan (TBD)

- ⛔ **Gerbang data prod sebelum merge bip-erp**: apakah baris berkode lama memuat tinjauan, temuan, atau bukti. Skrip baca-saja disiapkan, belum dijalankan per 2026-09-15. Bila tidak nol, tampilan hanya-baca untuk uji lama masuk lingkup sebelum merge.
- **Tanggal batas lapor SPT Masa PPh untuk Tax 2**, dikonfirmasi ke Tax Officer. Kriterianya ditulis umum sampai itu.
- ⛔ **Kapan pemilihan sampel tercatat mesin.** Tanpa ukuran populasi, metode, dan benih yang tersimpan, pemeriksaan bulan lalu tak bisa direproduksi bulan depan. Task tersendiri.
- Apakah **pembacaan otomatis dokumen** dikerjakan, dan dengan model apa. Mengirim rekening koran ke API di luar perusahaan menuntut **persetujuan tertulis Direksi**; persetujuannya belum ada. Lihat [[ADR - 0075 Bukti Sisi Lawan Dilampirkan dan Angkanya Dicatat, Pembacaan Otomatis Menyusul]] §4.
- Apakah **batas 4 MB file-service** cukup untuk rekening koran pindaian. Belum diukur terhadap berkas sungguhan.
- **Retensi berkas bukti.** Disimpan selamanya untuk sekarang; kebijakan pemusnahan keputusan Finance.
- Kapan cakupan diperluas ke pembukuan 40 CV.
- Matriks lama, bila penjalannya dipasang lagi: apakah Accurate mengirim jejak pelaku; apakah `access-privilege/list.do` dapat ditarik; apakah dokumen Bayar Uang membawa rekening penerima; apakah tiga belas uji konsistensi internal dihidupkan kembali; angka kapasitas produksi normal PSAK 14; ambang tiap uji berpembanding aturan.

## Arsip: Matriks 36 Uji (dilepas 2026-09-15)

Dilepas dari registry oleh [[ADR - 0098 Audit Internal Beralih ke Uji Petik Dua Arah Manual]]. Kode penjalannya disimpan tanpa dipanggil. Bagian ini dipertahankan karena aturannya berlaku lagi bila penjalan itu dipasang ulang, dan karena beberapa pelajarannya berlaku untuk modul mana pun yang membaca Accurate.

### 36 uji, tiga kelompok menurut asal sisi pembandingnya

| Kelompok | Sisi pembandingnya | Jumlah | Kekuatannya |
|---|---|---|---|
| 1 | Dari luar perusahaan: rekening koran, jawaban pelanggan, hitung fisik, akta | 12 (8 campuran, 4 manual) | **Paling kuat.** Tak seorang pun di dalam Bharata bisa mengarangnya |
| 2 | Dokumen internal di luar Accurate: surat jalan, berita acara, perintah kerja, PO dari CV | 8 (7 campuran, 1 manual) | Bisa dipalsukan, tapi menuntut usaha dan meninggalkan jejak fisik |
| 3 | Pembandingnya **aturan**, bukan data: logika akuntansi, ambang batas, standar konfigurasi Direksi | 16 (12 sistem, 4 campuran) | Bertahan menghadapi pembukuan yang dirapikan utuh |

⛔ **Tiga belas uji yang membandingkan neraca dengan laporan pendukungnya sudah DIKELUARKAN** — piutang terhadap umur piutang, persediaan terhadap kartu stok, aset tetap terhadap register, dan seterusnya. Kedua sisinya sama-sama tarikan dari basis data yang sama, sehingga pihak yang mampu mengubah pembukuan secara utuh tidak tertangkap di sana.

⚠️ Dua dari empat temuan utama kertas kerja 6 Agustus lahir dari uji yang dikeluarkan itu (selisih piutang Rp 954,7 juta dan PPN keluaran 0,42%). Kriteria "bertahan menghadapi pembukuan yang dirapikan utuh" tepat untuk menilai kekuatannya sebagai **deteksi**, tetapi ikut membuang kemampuannya sebagai **akurasi**.

Tiap uji punya kolom **tujuan** (akurasi, deteksi, mitigasi) dan **kondisi ideal** (hasil yang dianggap bersih). Matriks ini juga tidak mencakup sembilan prosedur yang menuntut kehadiran fisik, korespondensi resmi, atau tanda tangan; item uji petik justru menaruh sebagian prosedur itu di tangan auditor.

### Enam uji punya penjalan otomatis

| Uji | Sisi A | Sisi B | Keadaan |
|---|---|---|---|
| Silang pemasok terhadap karyawan | ERP procurement | ERP employee | Menunggu dua endpoint dibangun |
| Saldo kas berjalan tidak negatif | Accurate, buku besar per akun | aturan | Jalan, menunggu setelan akun |
| Barang dalam proses tidak negatif | Accurate, saldo akun | aturan | Jalan, menunggu setelan akun |
| Hitung ulang penyusutan | Accurate, register aset | aturan | Jalan |
| Deskripsi jurnal | Accurate, jurnal umum | standar kelengkapan | Jalan |
| Jurnal manual besar | Accurate, jurnal umum | dokumen sumber | Pemilihan jalan; pembandingnya menunggu manusia |

Tiga puluh sisanya terdaftar dan terbit di kertas kerja berkeadaan `belum_diimplementasi`.

### Bukti per item terpilih, dan dua bentuk yang registry tidak membedakannya

- `ujiJurnalManualBesar` memilih sampel terarah, mengisi `HasilUji.Terpilih`, lalu berhenti di `menunggu_data` sampai tiap item terpilih berdokumen; begitu seluruhnya terjawab, `bersih`. ⚠️ Klaim `bersih`-nya SEMPIT: "dokumennya sudah ditunjukkan", bukan "jurnalnya wajar".
- ⛔ **Bukti tingkat baris (`Item` kosong) TIDAK menjawab item mana pun.** Tiap jurnal menuntut dokumen sumbernya sendiri.
- ⛔ **Mengunggah bukti menyegarkan barisnya SEKETIKA tanpa menarik ulang sumbernya**, sebab penarikan ulang memilih ulang sampel terarah dan bisa melepas bukti yang baru dilampirkan dari sampelnya.

| Bentuk | Uji | Yang dikerjakan manusia | Guna pembacaan otomatis |
|---|---|---|---|
| **A. Bukti per item terpilih** | jurnal manual besar, penyesuaian persediaan, kapitalisasi vs beban, retur penjualan, pisah batas penjualan, penjualan PT ke CV | melampirkan dokumen **per item** dan menilai apakah ia mendukung entrinya | **hampir nihil** |
| **B. Angka dari satu dokumen** | rekonsiliasi bank, rekonsiliasi pajak, kas rekening CV, piutang iklan ke CV | membaca saldo/mutasi dari satu dokumen | **hanya di sini** |

Diukur di prod 2026-09-03 pada periode 2026-08: **32 `belum diimplementasi`, 4 `gagal ditarik`, 0 `menunggu data`.** Sebelas dari dua belas uji ber-`SumberUnggahan` belum punya penjalan sama sekali.

### Sampling sepuluh uji

Dari 36 uji, sepuluh menuntut pemilihan sampel. Lima menuntut acak (konfirmasi saldo pelanggan, stock opname, cek fisik aset, retur penjualan, penyesuaian persediaan); lima harus terarah (jurnal manual besar, kapitalisasi versus beban, pisah batas penjualan, varian produksi, penjualan PT ke CV). Cash opname butuh **waktu** yang acak, bukan item yang acak. Ukuran sampelnya master data Direksi berlantai 5 untuk acak, berbenih `crypto/rand` (diganti ADR 0098 untuk item uji petik).

### Kategori sidebar `audit` di Web ERP (dicabut)

- ⛔ Kategori sidebarnya `audit`, berdiri sendiri, bukan menumpang FAT: frontend memotong tiap izin di titik pertama, jadi izin ber-prefiks `finance` akan memunculkan seluruh menu keuangan bagi auditor.
- ⚠️ Kategori ini lahir hanya dari paket izin; tidak ada `system_roles.audit`, dan `AuditTierDefault` mengembalikan kosong untuk tier apa pun.
- ⚠️ Super-akses sidebar (IT supervisor atau jabatan Direktur) meloloskan tiap item sebelum `perm` dinilai, kecuali izin di `TANPA_BYPASS_SEMUA_MENU`. Izin audit tak pernah didaftarkan di sana (ADR 0074 §5 tak dikerjakan), dan gugur bersama menunya.

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
- ⛔ **Hasil kelompok 3 tidak boleh jadi ringkasan teratas.** Layar yang membuka dengan uji hijau memproduksi rasa aman yang tidak dijamin ujinya.

## Dokumen Terkait

- [[ADR - 0098 Audit Internal Beralih ke Uji Petik Dua Arah Manual]] · [[ADR - 0073 Modul Audit Internal di finance-service dan Kertas Kerja yang Dipegang Sendiri]] · [[ADR - 0074 Audit Internal Dipisah jadi Service dan Aplikasi Sendiri]]
- [[ADR - 0075 Bukti Sisi Lawan Dilampirkan dan Angkanya Dicatat, Pembacaan Otomatis Menyusul]] · [[Microservices - File Service]]
- [[ADR - 0001 Akuntansi via Accurate]] · [[ADR - 0068 Buku Besar Konsolidasi 40 CV di Luar Accurate]]
- [[API - Finance Service]] · [[API - Integration Service]] · [[Microservices - Integration Service]] · [[External - Accurate]]
- [[Finance - Big Pictures]] · [[Finance - Rancangan Finance Service]] · [[Finance - Dashboard per Posisi (FAT)]]
- [[APP - Buku Besar Konsolidasi CV FINCON]] · [[CORE - RBAC dan Permission Set]]
