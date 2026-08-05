## Deskripsi

*Kajian awal pemindahan **dua form kertas GA** ke ERP: Form Permintaan Barang dan Form Pengajuan Dana, beserta rekap bulanannya yang kini dikerjakan di spreadsheet. Dokumen ini memuat isi form apa adanya, keadaan sistem yang sudah ada, dan pertanyaan yang menunggu jawaban SPV HRGA. Rencana lama yang lebih umum ada di [[GA - Procurement System]]; dokumen ini menggantikannya sebagai acuan kerja karena bertumpu pada form yang benar-benar dipakai.*

- **Status**: 🟡 Konsep / kajian awal. Belum ada kode. Tiga keputusan sudah turun (lihat bab Sudah Diputuskan), sisanya menunggu jawaban SPV HRGA.
- **Sumber**: dua form kertas resmi (kop PT Bharata Internasional Pharmaceutical) + spreadsheet rekap PR + arahan tim GA, dikumpulkan 4 Agustus 2026.
- **Keadaan sistem**: diperiksa langsung di produksi 4 Agustus 2026 (lihat bab Keadaan Sistem Hari Ini).

## Dua alur, bukan dua form yang mirip

Perbedaan pokoknya bukan pada isi form, melainkan pada **siapa yang membelanjakan**.

| | Form Permintaan Barang | Form Pengajuan Dana |
|---|---|---|
| Dikirim ke | Admin GA | Finance (di form tertulis **Payroll**) |
| Yang membeli | GA | Pemohon sendiri |
| Uang | Tidak disebut sama sekali | Keluar lebih dulu, baru dibelanjakan |
| Tanda tangan di kertas | 4: Diajukan, Mengetahui atasan, Diterima, Disetujui | 3: Diajukan, Disetujui atasan, Diserahkan |
| Lembar arsip | (tidak disebut) | Lembar 1 Payroll, Lembar 2 user pengaju |

Dua ketentuan di Form Pengajuan Dana menjadi masuk akal hanya bila dibaca dengan cara ini:

- **"Pengaju dan penerima dana harus user yang sama"** ada karena pemohonlah yang berbelanja.
- **"Sisa dana: ADA / TIDAK ADA"** dan **"Diterima kembali oleh"** ada karena uang tunai keluar lebih dulu, sehingga kembaliannya wajib dipertanggungjawabkan.

Keduanya tidak relevan pada Permintaan Barang. Karena itu **kedua alur tetap dipisah**, bukan digabung jadi satu form dengan pilihan jenis.

## Isi form kertas, disalin apa adanya

### Form Permintaan Barang

Kepala: `Nama`, `Divisi`, `Tanggal Pengajuan`, `Keperluan`, `No Permintaan`.
Tabel baris barang: `No.`, `Nama Barang`, `Qty`, `Keterangan` (4 baris tercetak).
Kaki: empat tanda tangan (`Diajukan oleh`, `Mengetahui atasan`, `Diterima oleh`, `Disetujui oleh`).

### Form Pengajuan Dana

Kepala: `No.`, `Tanggal`.
Isi: `Dana sebesar (Rp)`, `Diterima oleh / Tanggal`, `Digunakan untuk`, `Nama Barang / Deskripsi`, `Qty x Harga = Jumlah`, `Spesifikasi`.
Penutup: `Sisa dana: ADA / TIDAK ADA (Rp ...)`, `Diterima kembali oleh`.
Kaki: tiga tanda tangan (`Diajukan oleh`, `Disetujui oleh atasan`, `Diserahkan oleh` / Bagian Payroll).

**Empat ketentuan tercetak di form:**

1. Digunakan untuk permintaan pembelian maupun pengeluaran kas **selain** pembelian bahan baku dan bahan kemas.
2. Diajukan oleh user dan disetujui oleh atasan langsung.
3. Payroll berhak **menolak** pengajuan bila nama barang, spesifikasi, qty, dan estimasi harga tidak diisi.
4. Pengaju dan penerima dana harus user yang sama.

## Dua menu yang diminta

Arahan tim GA (4 Agustus 2026) menetapkan **dua menu**, bukan satu.

### Menu 1: Kas Kecil HRGA

Hanya untuk **admin GA**. Isinya dua hal: **pengajuan dana** dan **pelaporan penggunaan dana ke Finance**.

Ini keputusan besar dan menjawab pertanyaan yang sebelumnya menggantung: sumber uang **bukan sekadar label**. Kas Kecil HRGA menjadi **buku kas sungguhan di ERP** yang punya menu input tersendiri, saldo yang berkurang saat dipakai, dan laporan pertanggungjawaban ke Finance. Sistem hari ini belum punya pencatatan kas sama sekali (lihat bab Keadaan Sistem Hari Ini), jadi bagian ini **dibangun dari nol**.

Polanya adalah kas imprest yang lazim: GA mengajukan dana ke Finance, menerima, membelanjakannya untuk permintaan divisi, lalu melaporkan penggunaannya untuk diisi ulang.

### Menu 2: Permintaan Pembelian Kebutuhan Operasional

Dari **seluruh divisi** ke **admin HRGA**.

**Dua klasifikasi menurut besar nominal yang diajukan**, dan klasifikasi itu menentukan sumber dananya:

| Klasifikasi | Sumber dana |
|---|---|
| Nominal kecil | Kas Kecil HRGA |
| Nominal besar | Budget perusahaan |

Ambang pemisahnya belum ditentukan (lihat pertanyaan 2).

**Tahap pengajuan**: No PR, nama pengaju, divisi, tanggal pengajuan, alasan pengajuan, nama barang, qty, estimasi harga, keterangan, persetujuan SPV.

**Tahap realisasi**: status persetujuan atasan GA (Acc / Reject / Pending, dengan Pending berarti masuk bulan depan atau belum dapat persetujuan), nama barang dan qty yang benar-benar dibeli, vendor, sumber dana, total harga realisasi, lampiran nota atau bukti pembelian.

**Rekap bulanan**: jumlah pengadaan masuk, selesai, pending atau masuk bulan berikutnya, dan ditolak.

### Catatan atas daftar sumber dana

Arahan awal menyebut **tiga** sumber (Kas Kecil GA, Finance, Kas Kardus). Arahan terbaru menyebut **dua** (Kas Kecil HRGA, budget perusahaan). Kemungkinan "Finance" dan "budget perusahaan" adalah hal yang sama, tetapi **"Kas Kardus" hilang dari daftar** dan perlu dipastikan apakah memang tidak dipakai lagi.

## Keadaan Sistem Hari Ini

Diperiksa langsung di produksi, bukan dari dokumen.

**Sudah ada dan berjalan.** `procurement-service` hidup di produksi dengan master **139 pemasok** dan **955 barang** (tersinkron ke Accurate), serta cermin baca-saja dari Accurate: **1.038 pesanan**, **1.841 penerimaan**, **2.055 faktur pembelian**, **235 permintaan barang**. Lihat [[Microservices - Procurement Service]].

**Belum ada sama sekali.**

- **Buku kas.** Modul finance di ERP seluruhnya dashboard **baca-saja** atas data Accurate dan marketplace (piutang, utang, laba, pencairan, kas toko). Tidak ada pencatatan kas kecil. **"Kas Kecil GA" dan "Kas Kardus" karena itu tidak punya rumah di sistem mana pun.**
- **Alur persetujuan bertingkat untuk pengadaan.** Koleksi `purchase_order` (PO buatan ERP) berisi **0 dokumen** di produksi; jalur itu tidak pernah dipakai.

**Ada tapi bukan wadah yang cocok.** [[Microservices - Form Builder Service]] hanya mesin form survei dan kepatuhan: mengumpulkan jawaban, tanpa persetujuan bertingkat, tanpa baris item, tanpa lampiran, tanpa transisi status. Memaksakan PR ke sana berarti menulis ulang separuh mesinnya.

**Sudah ada di Accurate.** Menu Permintaan Pembelian Accurate berisi 235 dokumen yang sudah dicerminkan ke ERP secara baca-saja. Perlu diputuskan apakah pengadaan GA nanti ikut tercatat di sana atau berhenti di ERP.

## Sudah Diputuskan

| Pertanyaan | Jawaban | Tanggal |
|---|---|---|
| Satu form gabungan atau dua alur? | **Dua alur.** Bedanya bukan isi form melainkan siapa yang membelanjakan | 4 Agt 2026 |
| Sumber dana cukup dicatat, atau saldonya berkurang? | **Saldo sungguhan.** Kas Kecil HRGA jadi buku kas dengan menu input tersendiri, plus pelaporan ke Finance | 4 Agt 2026 |
| Bagaimana sumber dana ditentukan? | **Otomatis dari besar nominal.** Nominal kecil memakai Kas Kecil HRGA, nominal besar memakai budget perusahaan | 4 Agt 2026 |

## Pertanyaan untuk SPV HRGA

Disusun agar dapat dijawab tanpa perlu tahu isi sistem. Dua yang bertanda **(besar)** menentukan ukuran pekerjaan.

### 1. Apakah kedua alur bisa saling menyambung?

Contohnya: divisi minta barang ke GA, kas kecil GA sedang tidak cukup, lalu GA mengajukan dana ke Finance untuk membelinya.

- **a.** Ya, satu Permintaan Pembelian bisa melahirkan Pengajuan Dana, dan keduanya perlu saling tertaut.
- **b.** Tidak, keduanya berdiri sendiri.

Kalau **a**, keduanya wajib tertaut supaya tidak terhitung dua kali di rekap bulanan.

### 2. Berapa ambang nominal pemisah kedua klasifikasi? (besar)

Sudah diputuskan bahwa besar nominal menentukan sumber dana. Yang belum: **angkanya berapa**, dan tiga hal turunannya.

- Apakah ambangnya tetap, atau bisa diubah admin tanpa minta bantuan IT?
- Apakah klasifikasi dihitung per **satu pengajuan** (total semua barang) atau per **baris barang**?
- Apa yang terjadi bila nominalnya kecil tetapi **saldo kas kecil sedang tidak cukup**? Otomatis pindah ke budget perusahaan, atau ditahan sampai kas diisi ulang?

### 3. Kas Kardus masih dipakai?

Arahan awal menyebut tiga sumber dana (Kas Kecil GA, Finance, Kas Kardus); arahan terbaru hanya dua (Kas Kecil HRGA, budget perusahaan). Apakah Kas Kardus sudah tidak dipakai, atau terlewat disebut?

### 4. Siapa yang mengisi ulang kas kecil, dan atas dasar apa?

Menu Kas Kecil HRGA memuat pengajuan dana dan pelaporan penggunaan ke Finance. Yang perlu dipastikan: apakah pengisian ulang dilakukan **setelah laporan penggunaan disetujui Finance**, atau bisa diajukan kapan saja? Dan apakah ada batas atas saldo kas kecil?

### 5. Rekap bulanan menghitung form atau barang? (besar)

Di rekap Juni tertulis: Form Masuk **31**, Total Permintaan **55**, Selesai **42**, Reject **4**, Pending **11**. Penjumlahan tiga status terakhir memberi **57**, sedangkan Total Permintaan **55** dan Form Masuk **31**.

Satu pengadaan berisi 5 barang dihitung sebagai **1** atau **5**? Dan angka Selesai, Reject, Pending menghitung form atau barang?

### 6. Payroll atau Finance?

Di form kertas, yang menyerahkan uang tertulis **Bagian Payroll**, dan lembar arsip pertama juga untuk Payroll. Arahan lisan menyebut **Finance**. Apakah Payroll di sini bagian dari Finance, atau dua pihak berbeda? Ini menentukan siapa yang mendapat tombol persetujuan.

### 7. Sisa dana masih dicatat?

Bagian "Sisa dana ADA / TIDAK ADA" dan "Diterima kembali oleh" tidak muncul di daftar kolom yang diminta. Masih dipakai, atau sudah ditinggalkan?

### 8. Rantai persetujuan yang mana yang berlaku?

Empat versi berbeda ditemukan:

| Sumber | Urutan |
|---|---|
| Form Pengajuan Dana | Pengaju, Atasan langsung, Diserahkan (Payroll) |
| Form Permintaan Barang | Pengaju, Mengetahui atasan, Diterima, Disetujui |
| [[GA - Procurement System]] (rencana lama) | SPV divisi, GA, Finance, Direktur |
| Arahan lisan tim GA | SPV, Atasan GA |

Apakah urutannya sama untuk semua nominal, atau di atas jumlah tertentu perlu tanda tangan tambahan?

### 9. Ketentuan tercetak ditegakkan otomatis?

Dari empat ketentuan di Form Pengajuan Dana, mana yang harus membuat pengajuan **tidak bisa disimpan** bila dilanggar? Terutama: pengecualian bahan baku dan bahan kemas, kelengkapan spesifikasi/qty/estimasi harga, dan pengaju sama dengan penerima.

## Pertanyaan untuk Finance (bukan HRGA)

**Apakah pengadaan GA harus tercatat juga di Accurate sebagai Permintaan Pembelian, atau cukup berhenti di ERP?** Bila harus, ERP perlu menulis ke API Accurate yang belum pernah dicoba: sejauh ini `procurement-service` hanya pernah menulis data pemasok dan barang, tidak pernah dokumen transaksi.

## Belum Diputuskan (TBD)

- Service mana yang memuat fitur ini: menumpang `procurement-service` (sudah punya master barang dan pemasok) atau service GA tersendiri.
- Penomoran PR: format, per tahun atau berjalan, siapa yang menentukan.
- Siapa yang boleh mengajukan: semua karyawan, atau hanya lewat SPV divisi.
- Lampiran nota memakai [[Microservices - File Service]] (batas 4 MB per berkas).

## Dependensi & Integrasi

- [[Microservices - Procurement Service]] — master pemasok dan barang, kandidat wadah fitur ini
- [[Microservices - File Service]] — penyimpanan lampiran nota
- [[Microservices - Employee Service]] — data karyawan, divisi, dan atasan untuk rantai persetujuan
- [[CORE - RBAC dan Permission Set]] — hak akses pengaju, admin GA, atasan GA, Finance
- [[ADR - 0001 Akuntansi via Accurate]] — batas antara ERP dan pembukuan

## Dokumen Terkait

- [[GA - Procurement System]] — rencana lama yang lebih umum, memuat peringatan tim sendiri agar fitur ini tidak dijadikan fitur pertama GA dan Finance
- [[GA - Inventory Management]] — tujuan akhir barang yang diterima GA
- [[GA - Big Pictures]] — peta domain General Affairs
