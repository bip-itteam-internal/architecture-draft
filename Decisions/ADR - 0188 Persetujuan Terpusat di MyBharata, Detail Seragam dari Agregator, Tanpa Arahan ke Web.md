# ADR - 0188 Persetujuan Terpusat di MyBharata, Detail Seragam dari Agregator, Tanpa Arahan ke Web

> **Status**: 🟢 Diterima, 2026-10-20, oleh irfanarfianto. Pemutus: irfanarfianto. Kode belum ada. Melanjutkan [[ADR - 0181 Portal Persetujuan Memuat Keputusan dan Tindakan Operasional]] (yang mengatur isi baris dan kode `aksi`) ke MyBharata, dan menambah bentuk keluar langkah persetujuan yang seragam. **Tidak mengubah** butir 12 ADR 0181 (tanpa penanda SLA). Pecahan kerja: [[ANALISA - Persetujuan Terpusat di MyBharata]].

## Untuk Manajemen

**Apa yang berubah di layar.**
- Di MyBharata, kartu ungu di Beranda berganti nama dari "Perlu Review" menjadi **"Perlu Tindakan"** dan menghitung **semua** yang menunggu Anda, bukan hanya cuti, izin, sakit, dinas, koreksi, tukar jadwal, dan booking ruang. Pengajuan Barang, Permintaan Pembelian, Permintaan Barang GA, Tiket, Live Support, Pelatihan, Payroll, Requisition, dan Offer ikut terhitung.
- Kartu itu membuka halaman **Persetujuan** di HP: tab Menunggu (yang paling lama di atas) dan Riwayat. Tiap dokumen bisa dibuka sampai rinciannya dan diputus dari HP. **Tidak ada lagi yang menyuruh membuka web.** Data yang besar, seperti rincian gaji seluruh karyawan sebuah payroll, mendapat halaman tabel sendiri di HP.
- Di web, halaman Persetujuan dirapikan: tiap jenis dokumen punya warna dan ikon yang sama dengan di HP, barisnya lebih padat, dan semua jenis dibuka di panel samping dengan urutan langkah persetujuan yang tampil sama di web dan HP.
- Label "Permintaan ERP" berganti menjadi **"Permintaan Pembelian"**.

**Siapa yang terdampak.** Semua penyetuju dan pelaksana tahap: atasan, HRD, GA, Finance, Accounting, pemilah tiket, dan Direktur. Pemohon tidak terdampak.

**Yang tidak dijanjikan.**
- Tidak ada perubahan siapa berwenang memutus apa. Tombol di HP memanggil jalur yang sama dengan web.
- Tidak ada penanda "terlambat" atau batas waktu. Batas resminya belum ada (ADR 0181 butir 12 tetap berlaku).
- Rincian gaji di HP **tidak** dikunci PIN tambahan; aksesnya sama dengan di web (izin melihat payroll).
- Cara tiap modul menyimpan riwayat persetujuannya tidak diubah; yang diseragamkan hanya cara menampilkannya. Model persetujuan tunggal lintas modul tetap menunggu [[ADR - 0137 Model Persetujuan Tunggal dan Pemisahan Tugas Lintas Modul]].
- Jenis yang di produksi belum pernah punya dokumen menunggu dikerjakan belakangan, setelah datanya terbukti ada.

**Perkiraan besaran kerja** (kasar, belum melewati `/plan`). Backend tiga bagian, sekitar enam sampai sepuluh hari. MyBharata tiga bagian, sekitar delapan sampai dua belas hari. Web dua bagian, sekitar lima sampai delapan hari. Urutan: backend, lalu MyBharata, lalu web. Pecahan kerjanya di [[ANALISA - Persetujuan Terpusat di MyBharata]].

## Deskripsi

*MyBharata mendapat halaman Persetujuan yang memuat seluruh antrean lintas modul dari agregator employee-service yang sama dengan web, dengan detail dan aksi di dalam aplikasi untuk semua jenis. Agregator menambah field `jenis`, bentuk keluar `langkah[]` yang seragam, dan endpoint detail; penyetuju boleh membaca detail dokumen yang ada di antrean atau riwayatnya. Web memakai bentuk yang sama.*

- **Status**: 🟢 Diterima, kode belum ada (lihat baris status di atas)
- **Path di repo** (akan disentuh):
  - `bip-erp/services/employee/antrean_pengajuan.go` · `bip-erp/services/employee/antrean_kontrak.go` · `bip-erp/services/employee/antrean_detail.go` (baru) · `bip-erp/services/employee/antrean_langkah.go` (baru)
  - rute detail/akses baca di service sumber: `bip-erp/services/procurement/permintaan_erp_handler.go` · `bip-erp/services/inventory/permintaan_gate.go` · `bip-erp/services/recruitment/` · `bip-erp/services/learning/request.go` · `bip-erp/services/marketing-analytics/karya_live_support_handler.go`
  - `mybharata-app/lib/src/features/home/presentation/widgets/my_activity/pending_approval_card.dart` · `mybharata-app/lib/src/features/persetujuan/` (baru) · `mybharata-app/lib/l10n/app_{id,en}.arb`
  - `erp-frontend/src/features/persetujuan/` · `erp-frontend/src/i18n/locales/{id,en}.ts`
- **Tanggal**: 2026-10-20
- **Rujukan visual**: Figma `BUV8afcBrNSbkmm0qI8EYz`, halaman "Persetujuan Terpusat", bagian "MyBharata: Persetujuan Terpusat versi compact" (kartu daftar, layar Menunggu/Riwayat, detail D1-D6, Rincian Payroll R1-R2, kartu Beranda) serta bagian tabel dan Sheet web. Rancangan adalah salinan bertanggal, bukan sumber kebenaran.

## Context

**Masalahnya.** Penyetuju tidak punya satu tempat di HP untuk melihat dan menuntaskan semua yang menunggu dia.
- Kartu "Perlu Review" MyBharata menghitung `GET /hr/requests?as=reviewer&include=booking` (`pending_approval_card.dart:25-26`), yang hanya mencakup enam jenis pengajuan karyawan plus booking ruang. Kartu membuka `ReviewerSubmissionPage` dengan cakupan yang sama.
- MyBharata **belum memanggil** agregator `GET /pengajuan/antrean` maupun `/pengajuan/ringkasan` (git grep `origin/dev`, 2026-10-19). Komentar `core/api/url.dart:271` menyatakan antrean peninjau "dikerjakan di web".
- Layar peninjau mobile hanya ada untuk enam jenis karyawan, booking ruang, dan triase tiket. Pelatihan, Pengajuan Barang, Permintaan, Permintaan Barang GA, Payroll, Live Support, dan rekrutmen tidak punya layar peninjau di mobile.
- [[ANALISA - Antrean Persetujuan Terpusat di Web]] butir T12 mencatat 119 pengajuan absensi "Diabaikan oleh sistem" karena lewat 24 jam tanpa diputus, padahal pintunya ada di MyBharata; sebabnya belum diukur.
- *Asumsi eksplisit (belum diukur)*: sebagian besar penyetuju lebih sering memegang HP daripada membuka web.

**Yang sudah ada dan dipakai ulang.**
- Agregator `GET /pengajuan/antrean` (`antrean_pengajuan.go:1888`) dengan 10 sumber di `registriAntrean` (`:384-681`), sumbu `?as=reviewer|reviewed`, `aksi`, `boleh_putus` tiga nilai, `nilai`, `degraded`. Isi baris dan kode `aksi` sudah diputuskan [[ADR - 0181 Portal Persetujuan Memuat Keputusan dan Tindakan Operasional]] butir 3-4 dan 13.
- Kartu dan detail peninjau asli MyBharata: `ReviewerLeaveCard`, `ReviewerSubmissionDetailPage`, `ReviewStepper`, `PayslipDetailBody`. Rancangan memakai bentuk asli ini (dirender lewat golden test), bukan komponen baru.
- Paket izin "Tanda Tangan" payroll (Cost Control, HRD, Finance, Direksi) sudah membawa `payroll.view` (`shared-library/common/catalog_payroll.go:190,198,206,214`), sehingga penyetuju run sudah boleh membaca rincian per karyawan (`GET /payroll-runs/:id` mengembalikan seluruh baris, `run_handlers.go:366-387`).

**Yang belum ada** (dibuktikan `git grep` atas `origin/main` bip-erp, 2026-10-19):
- Field jenis untuk kategori `karyawan`: jenisnya hanya hidup di `perihal` (`RequestType + " - " + Subtype`, `antrean_pengajuan.go:837-840`) dan di `tautan`.
- Bentuk langkah seragam: tiap modul menyimpan riwayatnya berbeda (`ReviewStep` attendance, `ReviewSlot` learning, `RiwayatBarang`, `RiwayatRun`, `RiwayatPermintaan`, `RiwayatKarya`; Permintaan ERP hanya `DisetujuiOleh/Pada`; tiket hanya timestamp). `langkah_ke/langkah_total` hanya terisi untuk Pengajuan Barang dan Permintaan Barang GA (`antrean_kontrak.go:156-160`). Di web, tiga stepper terpisah dirakit tiap modul (`linimasa-pengajuan.tsx`, `stepper-tahap-payroll.tsx`, inline di `request-detail.tsx`).
- Endpoint detail di agregator (hanya `/pengajuan/antrean` dan `/pengajuan/ringkasan`).
- Rute detail per id untuk Live Support, Pelatihan, dan Offer.
- Akses baca penyetuju: `GET /permintaan-erp/:id` digerbang `procurement.view` (`procurement/main.go:873`); `GET /permintaan/:nomor` (Permintaan Barang GA) 403 sesudah status `DIAJUKAN` kecuali staf GA (`inventory/permintaan_gate.go:46-54`); daftar Offer digerbang `recruitment.view`.

**Data nyata.** Per 2026-10-15, [[ADR - 0181 Portal Persetujuan Memuat Keputusan dan Tindakan Operasional]] mencatat **0 dokumen menunggu** di prod untuk Permintaan ERP, Pelatihan, Payroll, Permintaan Barang GA, dan Requisition. Belum diukur ulang untuk ADR ini (lihat "Perlu ukur prod" di ANALISA). Karena itu urutan kerja per jenis mengikuti data, bukan daftar.

**Status dok yang dijadikan dasar.** [[ADR - 0137 Model Persetujuan Tunggal dan Pemisahan Tugas Lintas Modul]] masih 🟡 Diusulkan dengan pengambil keputusan TBD. Keputusan butir 4 di bawah sengaja hanya menyentuh **bentuk keluar**, searah opsi 2 butir 4 ADR itu, supaya tidak mendahului keputusan model persetujuannya.

## Decision

### 1. Kartu Beranda MyBharata: "Perlu Tindakan"
- Judul **"Perlu Tindakan"**, subjudul **"{n} menunggu Anda"** (kalimat sama dengan subjudul halaman Persetujuan web), ikon inbox. Ikon lama clipboard-check dilepas karena kini menjadi ikon jenis Permintaan Pembelian.
- Angka = jumlah baris `GET /pengajuan/antrean?as=reviewer` yang `aksi`-nya bukan `pantau`. Baris Pantau tidak dihitung.
- Kartu tersembunyi hanya bila angkanya **benar-benar 0**. Galat pemuatan tampil sebagai keadaan galat yang bisa dicoba lagi, **tidak** dilipat ke 0 seperti hari ini (`pending_approval_card.dart:26`). `degraded` tak kosong ditandai di halaman tujuan.
- **Tanpa** penanda "lewat N hari" (ADR 0181 butir 12).
- Kartu membuka halaman Persetujuan MyBharata dengan pil "Perlu tindakan" aktif.

### 2. Halaman Persetujuan MyBharata
- Tab **Menunggu** (bawaan urut terlama) dan **Riwayat** (bawaan terbaru), sumber agregator `?as=reviewer|reviewed`. Pencarian, pil per `aksi`, dan penyaring kategori mengikuti web.
- Kartu memakai bentuk **asli `ReviewerLeaveCard`**: kepala = nama pemohon + posisi • departemen; tiket = ikon jenis berwarna + nama jenis + perihal (maks 2 baris) + tanggal/nomor; pemisah; `ReviewStepper` dua langkah (selesai terakhir + yang menunggu). Tambahan untuk data lintas modul, sengaja minimal: lama menunggu di slot trailing kepala (hari ini kosong), nominal di kanan tiket bila `nilai` tidak null, dan pil berisi label `aksi` pada langkah yang menunggu pemanggil.
- Kategori `karyawan` **dipecah per jenis** memakai field `jenis` (butir 4).
- 16 jenis: Cuti, Izin, Sakit, Dinas, Koreksi Presensi, Tukar Jadwal, Booking Ruang, Pelatihan, Pengajuan Barang, Permintaan Pembelian, Permintaan Barang GA, Tiket, Live Support, Payroll, Requisition, Offer. Warna dan ikon tujuh jenis pertama dan Pelatihan diambil dari `RequestTypeUIHelper` yang ada; delapan lainnya ditambahkan di tempat yang sama (satu peta, dipakai juga web).

### 3. Detail dan aksi di MyBharata, tanpa arahan ke web
- Detail memakai bentuk **asli `ReviewerSubmissionDetailPage`**: app bar "Review Pengajuan"; kartu jenis + perihal **utuh** + nominal + stepper; "Detail Pengajuan" berisi baris label-nilai (Nama Pemohon, Posisi, Departemen, lalu isi khas jenis, lalu Alasan); bilah bawah tombol aksi. Halaman detail jenis karyawan yang sudah ada dipakai ulang.
- Stepper detail ringkas dua langkah dengan tautan **"Lihat semua langkah (N)"** bila langkahnya lebih dari dua.
- Baris `pantau` atau `boleh_putus` false: tanpa tombol, bilah bawah berisi pesan status (pola `_buildStatusMessage` yang ada).
- **Tidak ada tombol atau alur yang membuka ERP web.** Data yang terlalu besar untuk satu layar diberi halaman MyBharata sendiri. Untuk Payroll: halaman **Rincian Payroll** (tabel compact: Karyawan · Pokok · Potongan · Bersih, pencarian, penyaring, baris total menempel) dan **Rincian Gaji per karyawan** berbentuk `PayslipDetailBody` dengan navigasi sebelumnya/berikutnya; tombol Unduh PDF disembunyikan selama run belum terbit.
- Rincian Payroll **tanpa PIN tambahan** (keputusan Pemutus 2026-10-19). Aksesnya `payroll.view` seperti web.

### 4. Agregator: `jenis`, `langkah[]`, dan detail seragam
- `BarisAntrean` mendapat field **`jenis`** (kode stabil, mis. `cuti`, `izin`, `sakit`, `dinas`, `koreksi`, `tukar`, `booking`; untuk kategori non-karyawan sama dengan kategorinya). `perihal` tidak lagi diawali nama jenis.
- **Bentuk keluar langkah seragam** `langkah[]`, diterjemahkan **sekali** di agregator dari bentuk simpan tiap modul (pola `petakan*` yang ada). Tiap langkah: `kunci`, `label`, `peran` (`pengaju` | `penyetuju` | `sistem`), `status` (`selesai` | `menunggu` | `ditolak` | `dikembalikan` | `diabaikan` | `belum`), `anda` (bool), `aktor` {id, nama, posisi} atau null, `calon` (daftar nama bila belum ada aktor), `waktu`, `catatan`, `putaran`. Field opsional ditulis tanpa `omitempty` agar null terbaca sebagai "tidak ada", bukan "kunci hilang". `langkah_ke`, `langkah_total`, dan `posisi_sekarang` diturunkan dari `langkah[]`, bukan dihitung terpisah.
- Baris antrean membawa `langkah[]` **ringkas** (langkah selesai terakhir + langkah menunggu). Endpoint detail baru `GET /pengajuan/antrean/:kategori/:id` membawa `langkah[]` lengkap dan rincian label-nilai per jenis.
- Penyimpanan riwayat di tiap modul **tidak diubah**.

### 5. Akses baca penyetuju dikerjakan di service sumber
- Penyetuju atau pelaksana tahap **boleh membaca detail dokumen yang ada di antrean atau riwayatnya**, tanpa diberi izin modul penuh. Polanya `BolehMelihatPengajuan` (`procurement/pengajuan_barang_cakupan_baca.go:76-100`): pemohon, siapa pun di riwayat, dan siapa pun yang sedang boleh menindak.
- Gerbangnya di service sumber, bukan di agregator (ADR 0181 dan aturan Portal Persetujuan). Rute detail per id dibuat untuk Live Support, Pelatihan, dan Offer; `GET /permintaan-erp/:id` dan `GET /permintaan/:nomor` diberi jalur baca untuk penyetuju dengan aturan yang sama.

### 6. Label "Permintaan ERP" menjadi "Permintaan Pembelian"
- Di semua permukaan (portal web, MyBharata). Di sistem, istilah ini berarti entitas `permintaan_erp` milik procurement.
- ⚠️ Di [[GA - SOP Posisi Procurement]] dan [[GA - Form Pengadaan dan Pengajuan Dana]] istilah "Permintaan Pembelian" dipakai untuk dokumen SOP/form GA. Pembaca yang mencocokkan dok SOP dengan layar harus tahu keduanya berbeda; kalimat ini sengaja ditulis di sini supaya tidak hanya hidup di kepala orang.

### 7. Web memakai bentuk yang sama
- Tabel **compact**: Menunggu · Tindakan (+ "x/y") · Dokumen (ubin warna/ikon jenis + perihal + jenis · nomor, nominal di ujung kanan bila ada) · Pemohon. Kolom Nilai digabung ke Dokumen. Riwayat: Diproses · Tindakan Anda (+ alasan satu baris) · Dokumen · Pemohon · Posisi sekarang.
- **Sheet untuk 16 jenis** dengan kerangka tiga bagian yang sudah berlaku: header = nama pemohon (perihal tidak dipotong di header), badan dimulai perihal utuh, lalu kotak tindakan, rincian, dan stepper ringkas dua langkah + "Lihat semua langkah"; footer aksi. Tombol ke halaman lengkap modul tetap ada di web.
- Satu komponen stepper bersama di web yang merender `langkah[]`, menggantikan tiga stepper terpisah untuk konteks persetujuan.

### 8. Urutan kerja dan deploy
- Backend lebih dulu, lalu MyBharata, lalu web. Semua field baru bersifat tambahan; konsumen lama tetap jalan selama field baru belum ada.
- Jenis yang di prod masih 0 dokumen menunggu dikerjakan sesudah jenis yang berdata.

## Alternatif yang Ditolak

- **MyBharata memanggil detail tiap sumber langsung.** Tanpa endpoint agregator baru, tetapi logika langkah ditulis dua kali (Dart dan TypeScript) untuk sepuluh sumber: satu fakta di dua tempat, kelas kerusakan yang paling sering tercatat di vault ini.
- **Mobile hanya daftar, detail tetap di web.** Ditolak Pemutus: tidak boleh ada arahan ke web.
- **Penanda "lewat 3 hari".** Ditolak karena ADR 0181 butir 12 (Diterima) menolak penanda SLA sampai ada batas resmi.
- **Memberi penyetuju izin modul penuh** (mis. `procurement.view`). Ditolak: penyetuju akan melihat seluruh modul, bukan hanya dokumen yang ia tangani.
- **PIN tambahan untuk rincian gaji.** Ditolak Pemutus; akses mengikuti web.
- **Label "Permintaan Barang ERP".** Lebih dekat ke dok procurement, tetapi Pemutus memilih "Permintaan Pembelian".

## Consequences

- MyBharata menjadi konsumen kedua agregator. Perubahan kontrak agregator sejak itu harus menjaga dua klien; `jenis` dan `langkah[]` dikunci test kontrak di employee-service.
- Endpoint detail di agregator memanggil service sumber per permintaan (fan-out satu sumber), jadi galat sumber tampil sebagai detail tak termuat, bukan halaman kosong.
- Kategori yang belum punya riwayat di sumber (Tiket, Live Support, Permintaan Barang GA, rekrutmen; ADR 0181:135) tetap tak tampil di tab Riwayat sampai sumbernya membangun riwayat.
- Rilis MyBharata wajib menaikkan version name, bukan hanya versionCode.
- Bug kecil yang ikut diperbaiki di MyBharata: pil "Submitted" di `submission_card_stepper.dart:133` masih string Inggris tanpa l10n.
- Dok yang memakai label lama "Permintaan ERP" dan masih hidup disunting; ADR 0114 dan 0181 tidak disunting karena catatan keputusan bertanggal, ADR ini yang menyatakan penggantiannya.

## Terkait

- [[ADR - 0181 Portal Persetujuan Memuat Keputusan dan Tindakan Operasional]]
- [[ADR - 0114 Antrean Persetujuan Terpusat di Web, Satu Tabel Seragam dari Agregator Employee-Service]]
- [[ADR - 0137 Model Persetujuan Tunggal dan Pemisahan Tugas Lintas Modul]]
- [[ADR - 0129 Persetujuan Payroll Run Bertingkat dan Dibayar per Badan Usaha sebelum Terbit]]
- [[REF - Alur Persetujuan]] · [[APP - MyBharata]] · [[APP - Web ERP]]
- [[ANALISA - Persetujuan Terpusat di MyBharata]]
