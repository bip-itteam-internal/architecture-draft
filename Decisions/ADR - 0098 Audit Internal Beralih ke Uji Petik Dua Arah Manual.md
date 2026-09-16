# ADR - 0098 Audit Internal Beralih ke Uji Petik Dua Arah Manual

## Untuk Manajemen

Daftar pemeriksaan audit internal diganti dengan **38 item uji petik** dari dokumen "Item Pengecekan Accounting dan Tax": 28 item Accounting dan 10 item Tax. Tiap item diperiksa auditor dengan menelusuri sampel ke dokumen, lalu disimpulkan **Wajar** atau **Temuan**. Kesimpulan wajib menyertakan sampel yang diperiksa beserta cara memilihnya, dan catatan. Tanpa AI dan tanpa pemeriksaan otomatis. **Yang berubah di layar**: aplikasi Audit Internal menampilkan 38 item dikelompokkan per bagian dan tahap; register temuan cukup berisi catatan, kriteria, dan sampel; halaman pengaturan ukuran sampel dicabut. Menu Audit Internal di ERP dicabut, dan alamat lamanya mengantar ke aplikasi audit.

**Terdampak**: auditor internal (pemakai), Direktur (pembaca laporan), Accounting dan Tax (pihak yang diperiksa). **Yang TIDAK dijanjikan**: sistem tidak menyimpulkan apa pun sendiri, tidak memaksa perluasan sampel dari 3 ke 10, dan tidak memeriksa lima area yang dinyatakan di luar lingkup (penyusutan, utang kepada kreditur, ekuitas dan investasi, beban dan harga pokok, arsip transaksi Accounting). **Besaran kerja**: sedang, tiga repo, sudah dikerjakan di branch; merge menunggu pemeriksaan data prod.

## Deskripsi

*Mengganti registry 36 uji matriks pembanding milik [[Finance - Audit Internal]] dengan 38 item uji petik dua arah yang diperiksa manusia. Membalik [[ADR - 0075 Bukti Sisi Lawan Dilampirkan dan Angkanya Dicatat, Pembacaan Otomatis Menyusul]] §3 (penjalan uji yang menyimpulkan) dan [[ADR - 0073 Modul Audit Internal di finance-service dan Kertas Kerja yang Dipegang Sendiri]] §8 (ukuran sampel master data Direksi berlantai 5). Menuntaskan pencabutan layar audit dari [[APP - Web ERP]] yang dijadwalkan [[ADR - 0074 Audit Internal Dipisah jadi Service dan Aplikasi Sendiri]].*

- **Status**: ⚠️ **Implemented di branch, belum merge** (2026-09-15): bip-erp `feat/finance-audit-uji-petik`, audit-bharata `feat/uji-petik-manual`, erp-frontend `feat/cabut-audit-internal-erp`. Yang live di prod masih matriks 36 uji. Merge bip-erp menunggu pemeriksaan data prod (lihat Consequences).
- **Path di repo**:
  - `bip-erp/services/finance/audit_item_petik.go` (baru: 38 item + 5 area) · `audit_registry.go` · `audit_kertas_kerja.go` · `audit_tindakan.go` · `audit_handler.go` · `audit_uji.go`
  - `audit-bharata/src/app/page.tsx` · `src/app/temuan/page.tsx` · `src/features/audit/components/detail-uji-panel.tsx` · `konfirmasi-temuan-dialog.tsx` · `src/features/audit/lib/tampilan.ts` · `ringkasan-keadaan.ts`
  - `erp-frontend/next.config.js` (redirect) · `src/components/layout/sidebar-menus.tsx` · `src/app/(main)/audit/` dan `src/features/audit/` (dihapus)
- **Tanggal**: 2026-09-15

## Context

1. **Daftar yang diserahkan.** Manajemen menyerahkan dokumen "Item Pengecekan Accounting dan Tax" (diterima 2026-09-15): 38 item uji petik dua arah, Accounting 28 (Tahap 2: 15, Tahap 3: 13) dan Tax 10 (Tahap 2: 7, Tahap 3: 3), aturan pengambilan sampel, dan lima area yang sengaja tidak diperiksa. Tahap 2 menelusuri dari sistem ke kenyataan (apakah yang tercatat itu nyata); Tahap 3 dari kenyataan ke sistem (apakah yang nyata sudah tercatat).
2. **Registry yang digantikan.** Modul mendaftarkan 36 uji matriks pembanding dua sisi, dan hanya 6 yang punya penjalan otomatis. Di prod periode 2026-08 hasilnya 32 `belum_diimplementasi`, 4 `gagal_tarik`, 0 `menunggu_data` (diukur 2026-09-03). Paket izin `Audit: *` per pengukuran 2026-09-04 belum ditempel ke posisi mana pun, jadi belum ada pemakai sungguhan.
3. **Permintaan pemilik pekerjaan (2026-09-15).** Pondasi dulu: tiap item cukup ditandai wajar atau dijadikan temuan beserta catatan, tanpa AI, sesederhana mungkin tanpa meninggalkan esensi audit internal.
4. **Isi dokumen sumber yang tidak bisa disalin apa adanya.** Ada satu aturan "semua acak", padahal tiga item memilih barang yang dilihat auditor dan dua belas memeriksa seluruh populasi. Tanggal dan nama akun terikat satu periode ("31 Juli", nama dashboard iklan). Item gaji dan transfer gaji membandingkan dengan data yang dipegang Finance sendiri. Kriteria Tax item 2 menyebut tanggal lapor yang belum dikonfirmasi Tax Officer.

## Decision

### 1. Registry berisi 38 item uji petik, diperiksa manusia

Registry di kode (`audit_item_petik.go`) memuat 38 item. Tiap item menyimpan bagian (`accounting` | `tax`), tahap (2 | 3), nomor dalam bagiannya, pos, nama, titik awal, pembanding, kriteria cocok ("Dinyatakan cocok bila"), tujuan, sampel yang dituntut, dan metode pemilihan. Nama pemegang jabatan dan bobot KPI dari dokumen sumber **tidak** disimpan. Tak satu item pun punya penjalan otomatis. Registry tidak lagi mendeklarasikan sumber per sisi, sehingga pembagian sumber di ADR 0073 §3 tidak tercermin di item uji petik. Layar membaca daftarnya dari `GET /audit/uji`, tidak menyalinnya.

### 2. Vonis manusia: Wajar atau Temuan, dengan sampel dan catatan wajib

- Baris lahir `belum_diperiksa` saat kertas kerja disiapkan.
- **Wajar**: catatan dan sampel wajib (400 bila kosong).
- **Temuan**: catatan (`kondisi`) dan sampel wajib. **Kriteria disalin dari registry**; kiriman klien diabaikan. Klasifikasi mayor/moderat/minor opsional; akar penyebab, dampak, dan rekomendasi tidak lagi diminta.
- Temuan tidak punya jalan hapus. Menerbitkan ulang item yang sama merevisinya, dan isi sebelumnya disimpan di jejak beraksi `revisi`.
- Item bertemuan tidak bisa ditandai wajar (409). Penjaganya ikut di filter tulis, supaya temuan yang terbit di sela pembacaan dan penulisan tidak tertimpa.
- Menjadikan temuan hanya lewat rute temuan yang digerbang `audit.temuan.terbitkan`. Badan tinjauan yang membawa `jadi_temuan` ditolak 400, bukan diabaikan: klien lama yang mengirimnya tidak boleh diam-diam tercatat Wajar.

### 3. Metode sampel per item, ukuran sampel bagian kalimat item

- Metode per item: **terarah** untuk Accounting 18, 19, 20; **populasi penuh** untuk Accounting 6, 12, 13, 15 dan Tax 1, 2, 3, 4, 5, 6, 8, 9; **acak** untuk 23 item sisanya.
- Ukuran sampel tertulis di kolom sampel item (mis. "3 rekening dipilih acak"), bukan master data terpisah. Rute `PUT /audit/setelan-sampel/:kode` tetap ada tetapi menolak item tanpa penjalan, yaitu seluruh 38 item.
- Aturan "bila satu sampel meleset, perluas jadi 10 di pos itu" tampil sebagai **pengingat** di konfirmasi temuan untuk item acak, dan **tidak ditegakkan** sistem.

### 4. Isi item disesuaikan dari dokumen sumber

- Tanggal dan nama akun digeneralisasi ("akhir periode", "bulan sesudah periode", "setiap dashboard iklan").
- Pembanding yang independen dari pihak yang diperiksa: Accounting 8 menghitung ulang gaji memakai Peraturan Perusahaan, bukan hasil payroll; Accounting 21 memakai daftar karyawan HRIS ERP, bukan daftar yang dipegang Finance.
- Tax 2 memakai "batas lapor SPT Masa PPh yang berlaku", karena tanggalnya belum dikonfirmasi Tax Officer.

### 5. Lima area di luar lingkup ikut terbit di kertas kerja

Penyusutan, utang kepada kreditur, ekuitas dan investasi, beban dan harga pokok, serta arsip transaksi Accounting dikirim sebagai `di_luar_lingkup` di respons kertas kerja dan tampil di layar, supaya "tidak diperiksa" tidak terbaca "bersih". Angka laporan satu periode dari dokumen sumber tidak disalin.

### 6. Registry lama dilepas, kodenya disimpan

36 uji lama dilepas dari registry. Kode penjalannya disimpan tanpa dipanggil, beserta test-nya. Kertas kerja hanya menampilkan baris yang kodenya terdaftar. Baris lama periode yang sudah dibuka tetap tersimpan di database, dan cacahnya dikirim sebagai `baris_di_luar_daftar` tetapi tidak ditampilkan layar.

### 7. Layar hanya di aplikasi Audit Internal; menu ERP dicabut, alamat lamanya dialihkan

Rute `/audit*` dan kategori sidebar `audit` di erp-frontend dicabut. Alamat lama dialihkan (307) ke `NEXT_PUBLIC_AUDIT_URL` lewat `next.config.js`: `/audit` ke beranda, `/audit/temuan` ke register, sisanya ke beranda. Env kosong berarti tanpa redirect. Halaman setelan sampel di [[APP - Audit Internal]] ikut dicabut. Empat entri `audit.*: tolak` di `menu-permission.ts` dipertahankan, sebab `bolehMenu` meloloskan izin tanpa entri.

## Consequences

### Yang membaik

- Daftar pemeriksaan sama dengan dokumen yang dipegang auditor; tak ada lagi 30 baris `belum_diimplementasi` yang mengisi kertas kerja.
- Tiap kesimpulan membawa sampel dan cara memilihnya, sehingga pemeriksaannya bisa diulang orang lain.
- Kriteria temuan tidak bisa dikarang penerbitnya.

### Yang memburuk atau tetap terbuka

- ⚠️ **Tidak ada lagi deteksi otomatis.** Seluruh keyakinan bergantung pada auditor yang benar-benar menelusuri sampel. Sistem memaksa adanya catatan dan sampel, bukan bahwa penelusurannya terjadi.
- ⚠️ **Pemilihan sampel tidak tercatat mesin.** Benih, ukuran populasi, dan item terpilih tidak disimpan; yang ada hanya kalimat sampel dari auditor. Lubang `audit_sampel` yang dicatat di [[Finance - Audit Internal]] tetap terbuka.
- ⚠️ **Aturan perluasan 3 ke 10 hanya pengingat.** Auditor yang tidak memperluas sampel tidak dihentikan sistem.
- ⚠️ **Baris lama disembunyikan tanpa tanda di layar.** Aman hanya bila baris lama tak memuat tinjauan, temuan, atau bukti. Itu wajib dibuktikan pemeriksaan data prod **sebelum merge bip-erp**; bila tidak nol, tampilan hanya-baca untuk uji lama masuk lingkup lebih dulu.
- **`audit.master.save` dan paket `Audit: Direksi` kehilangan aksi tulis** di layar. Katalog izin di shared-library sengaja tidak disentuh, sebab menyentuhnya membangun ulang seluruh service.
- **Env baru erp-frontend** `NEXT_PUBLIC_AUDIT_URL` wajib diisi di `.env` prod **sebelum build**; redirect dibekukan saat build, jadi restart saja tidak cukup. Tanpa env, `/audit*` membalas 404.
- **Urutan deploy** (dijalankan manusia): finance-service, lalu aplikasi Audit Internal, lalu erp-frontend. Selama jeda finance-service ke aplikasi audit, layar audit versi lama tidak cocok dengan respons baru, dan tinjauannya ditolak karena tidak mengirim sampel. Jeda itu diterima karena pemakai aktif belum ada.

### Yang sengaja tidak dilakukan

- Tidak ada AI, pembacaan dokumen otomatis, maupun penjalan otomatis untuk item uji petik.
- Tidak menegakkan perluasan sampel dan tidak mengunci ukuran sampel.
- Tidak menghapus kode penjalan lama, rute setelan sampel, maupun izin `audit.master.save` dari katalog.
- Tidak mengarsipkan atau menghapus baris matriks lama di prod; saringannya terjadi saat baca.
- Tidak mengaitkan item ke bobot KPI.

## Dokumen Terkait

- [[Finance - Audit Internal]]: cara kerja modul dan registry
- [[APP - Audit Internal]]: layar · [[APP - Web ERP]]: pencabutan menu dan redirect · [[API - Finance Service]]: kontrak rute
- [[ADR - 0073 Modul Audit Internal di finance-service dan Kertas Kerja yang Dipegang Sendiri]] (§8 diganti, §3 tak tercermin di item uji petik) · [[ADR - 0075 Bukti Sisi Lawan Dilampirkan dan Angkanya Dicatat, Pembacaan Otomatis Menyusul]] (§3 diganti) · [[ADR - 0074 Audit Internal Dipisah jadi Service dan Aplikasi Sendiri]] (§5 gugur karena menu dicabut)
- [[GA - Audit Internal System]] · [[CORE - RBAC dan Permission Set]] · [[RUN - Deploy Microservices bip-erp]]
