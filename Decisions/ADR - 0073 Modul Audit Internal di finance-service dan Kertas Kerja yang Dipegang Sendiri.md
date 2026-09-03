## Untuk Manajemen

- **Yang berubah di layar**: modul baru berisi kertas kerja audit bulanan, satu baris per pengujian, dan register temuan yang menuliskan kondisi, kriteria, akar penyebab, dampak, dan rekomendasi. Angka kedua sisi pembanding sudah berdampingan beserta selisihnya, sehingga auditor **menilai**, bukan menghitung ulang. **Layarnya kini sudah dibuat** (tiga halaman, menu tersendiri bernama AUDIT INTERNAL), tetapi belum bisa dicoba siapa pun sampai service-nya di-deploy.
- **Siapa terdampak**: auditor internal sebagai pemakai utama. Posisi itu **belum ada**, dan sampai terisi modulnya dipakai review silang antar-divisi. Direktur sebagai penerima laporan sekaligus satu-satunya yang boleh menyetel ukuran sampel. Finance sebagai pihak yang dimintai klarifikasi, bukan sebagai pemakai.
- **Tidak dijanjikan**: modul ini **tidak menyimpulkan kecurangan**, ia menunjukkan selisih lalu berhenti. Ia **tidak menggantikan** hitung fisik kas dan gudang, konfirmasi saldo ke pelanggan, maupun pengambilan rekening koran dari bank. Ia **tidak mencakup pembukuan 40 CV**. Dari 36 pengujian, baru **enam** yang punya penjalan otomatis; sisanya terbit di kertas kerja sebagai baris yang jelas-jelas belum dikerjakan, bukan hilang dari daftar.
- **Besaran kerja**: mesin dan layarnya selesai. Yang tersisa: menaikkan service-nya ke lingkungan uji, menugaskan paket izinnya, dua endpoint di modul lain, dan tiga pembuktian ke produksi.

## Deskripsi

*Audit internal atas pembukuan dibangun sebagai **modul di dalam finance-service**, bukan service tersendiri, dan sebagai **konsumen pembaca yang sudah ada**, bukan klien Accurate keempat. Ia memegang sendiri kertas kerja beserta jejak tinjauannya alih-alih menumpang form-builder. Ketiga sisi keputusan ini berangkat dari alasan yang sama: yang menentukan kelayakan pakai-ulang bukan kemiripan bentuk, melainkan kontrak yang harus dipenuhi.*

- **Status**: ⚠️ **Implemented (ada catatan)** — seluruhnya **merged ke `main`** per 2026-09-03: backend fase 1 ([#1676](https://github.com/bip-itteam-internal/bip-erp/pull/1676)), `keadaan_efektif` ke JSON ([#1679](https://github.com/bip-itteam-internal/bip-erp/pull/1679)), layar fase 2 (erp-frontend [#1429](https://github.com/bip-itteam-internal/erp-frontend/pull/1429)). **Belum di-deploy dan belum pernah dijalankan lewat gateway.** Lihat "Belum selesai" di bawah.
- ⛔ **§1 DIAMANDEMEN [[ADR - 0074 Audit Internal Dipisah jadi Service dan Aplikasi Sendiri]]** (2026-09-03): audit dipisah jadi service dan database sendiri. Alasan penolakan di §1 tidak dibantah — ia kalah oleh dua tuntutan yang saat itu belum dinyatakan (bukti tak boleh diubah pihak yang diperiksa; wadahnya menampung seluruh audit internal termasuk kepatuhan GA). **Keputusan §2 sampai §11 tetap berlaku.**
- **Path di repo**: `bip-erp/services/finance/audit_*.go` · `bip-erp/shared-library/common/catalog_audit.go` · `bip-erp/services/employee/permission_catalogs.go` · `bip-erp/services/integration/internal/interface/http/riwayat_akun_handler.go` · `bip-erp/docker-compose.yml` · `erp-frontend/src/app/(main)/audit/*` · `erp-frontend/src/features/audit/*` · `erp-frontend/src/components/layout/sidebar-menus.tsx` · `erp-frontend/src/utils/menu-permission.ts`
- **Tanggal**: 2026-09-02 (diamandemen di hari yang sama, lihat §1 dan §8)

## Context

Kebutuhan datang sebagai solusi: sebuah dokumen prosedur berisi sembilan modul pengujian bulanan atas pembukuan Accurate, disusul matriks pengujian yang memetakan tiap uji ke asal sisi pembandingnya. Wawancara menyempitkannya jadi kebutuhan yang berbeda: **auditnya sudah berjalan manual dan prosedurnya sudah terbukti sekali dipakai; yang membakar waktu adalah menarik dan mencocokkan datanya.** Kertas kerja audit posisi 6 Agustus 2026 adalah buktinya.

Satu hal yang tidak disadari dokumen sumbernya perlu dicatat karena ia justru nilai terbesar modul ini. Dokumen itu menulis bahwa otomasi tidak memperbaiki independensi karena datanya tetap diekspor manusia. Itu benar untuk ekspor Excel, tetapi tidak berlaku bila ERP menarik lewat kredensial sistem: angka yang diperiksa tidak pernah melewati tangan divisi yang sedang diaudit.

**Yang sudah ada jauh lebih banyak dari yang diperkirakan dokumen itu.** [[Microservices - Integration Service]] sudah menjadi pembaca Accurate yang serius dan **nol tulis**, menyuplai dashboard FAT lewat grup `/accounting/*` ([[API - Integration Service]]): laporan keuangan, saldo per akun, jurnal umum berhalaman sekitar 96 ribu baris, umur piutang B2B beserta DSO, aset tetap dari salinan Mongo, dan PPN masukan.

[[ADR - 0001 Akuntansi via Accurate]] tidak menghalangi ini. Yang dilarangnya **membangun** general ledger sendiri dan **menulis balik sembarangan**; pembacaan read-only justru dicatat sebagai konsekuensi positif.

⚠️ **Yang tidak terlihat dari dokumentasi, dan baru ketahuan saat implementasi:** "data sudah ditarik ERP" TIDAK sama dengan "terjangkau service lain lewat HTTP". Buku besar per akun sudah lama hidup sebagai metode klien di integration-service tetapi tak pernah terekspos sebagai endpoint, dan daftar pemasok maupun daftar karyawan sama sekali belum punya rute. Perkiraan awal yang menyebut 15 uji siap jalan karena itu terlalu optimistis.

## Decision

### 1. Modul di dalam `finance-service`, BUKAN service tersendiri

**Diamandemen 2026-09-02.** Versi pertama ADR ini menetapkan `services/audit` baru dengan alasan RBAC: integration-service tak punya perkakas izin. Alasan itu **tidak bertahan diperiksa** — `RegisterCatalog` dan `RequirePermission` hidup di `shared-library` dan dapat dipakai service mana pun, dan `finance-service` pun belum memakainya.

Yang menggantikannya:

- **`services/finance` sudah ada, hidup, dan ter-deploy** dengan modul Pajak dan Cost Control, DB sendiri, dan identitas service yang memang menyebut dirinya menampung modul.
- **Container baru mahal di lingkungan ini.** VM dev sudah menjalankan puluhan container dan pernah kena OOM kernel.
- **Service baru punya riwayat lolos dari deploy**; `deploy.yml` berulang kali tidak mencakupnya, dan gagalnya senyap.
- **Jebakan urutan rute sudah dijinakkan di sana** beserta testnya.

Keberatan yang diterima sadar: modul audit menumpang di service yang mengelola domain yang diauditnya. Pemisahnya RBAC dan kredensial, bukan batas proses. Koleksinya berawalan `audit_` di database yang sama, sebab `koleksi()` di `db.go` terikat satu DB dan menembusnya berarti melewati penjaga yang menurunkan kegagalan "DB nil" dari panik senyap menjadi galat yang bisa dibaca.

⛔ **Izinnya ber-prefiks `audit`, BUKAN `finance`.** Prefiks izin menentukan kategori sidebar di frontend, dan menyatukannya membuat pemegang izin finance ikut membuka kertas kerja yang memeriksa pekerjaannya sendiri.

### 2. Konsumen pembaca yang ada, bukan klien Accurate keempat

Seluruh angka ditarik lewat `/accounting/*` dan saudara-saudaranya. Modul audit **tidak memegang kredensial Accurate**. Sudah ada tiga klien Accurate terpisah di repo dan seluruhnya berbagi limiter yang dijaga 6 permintaan per detik; yang keempat memakan jatah yang sama sekaligus melahirkan pembaca kedua atas angka yang sudah dibaca dashboard FAT.

Satu endpoint baru ditambahkan ke integration-service alih-alih dibuat sendiri: `GET /accounting/riwayat-akun`, membungkus metode klien yang sudah ada dan sudah ber-test.

### 3. Modul ini BUKAN modul Accurate

**Diamandemen 2026-09-02.** Dari 36 pengujian, sisi yang bersumber Accurate justru minoritas. Registry karena itu mendeklarasikan **sumber per sisi**, lima jenis: `accurate`, `erp` (modul ERP sendiri), `unggahan` (rekening koran, SPT, berita acara, akta), `input_manusia` (hitung fisik, jawaban konfirmasi), dan `aturan` (tak ada sisi lawan sama sekali).

Akibat yang menguntungkan: **silang daftar pemasok terhadap data karyawan dapat otomatis penuh.** Matriks menandainya campuran dengan alasan "data HRGA diminta manusia", dan itu tidak lagi benar — data karyawan ada di ERP sendiri.

### 4. Kertas kerja dan jejak tinjauan dipegang sendiri, BUKAN form-builder

Pemeriksaan `services/form-builder` menemukan empat dari lima sifat tidak terpenuhi, dua di antaranya fatal:

- ⛔ **Tidak bisa simpan sebagian.** `FormResponse` tidak punya field status maupun draft. Audit berjalan H+1 sampai H+8, jadi ini pembatalan alur kerjanya.
- ⛔ **Tidak ada jejak perubahan, bahkan `updated_by` pun tidak.** Lebih jauh, jejak keputusan lama justru dihapus saat sebuah butir diperbaiki.
- ⛔ **Baris tidak bisa membawa nilai terhitung**, dan batas 100 field per form dilampaui.
- ⛔ **`FormTypeChecklist` tidak memberi apa pun selain namanya** — komentarnya sendiri menyatakan tipe itu tak punya perilaku.

Argumen penutupnya datang dari peringatan form-builder sendiri: mengganti sebuah key membuat kiriman lama tersangkut permanen, dan menghapus key membuat kiriman yang menunggu terbaca "disetujui" lalu lenyap. Untuk kertas kerja yang harus dapat dibandingkan antar bulan, itu berarti temuan bulan lalu bisa hilang karena seseorang menyunting redaksi ujinya.

### 5. Register temuan terpisah dari `quality_capa`

`CAPA_AREAS` dikunci `["Produksi", "Gudang"]` dan nilainya mencerminkan backend serta dipakai metrik KPI `temuan_capa_produksi`. Menambahkan area finance mengotori metrik yang sudah berjalan demi satu pemanggil baru.

Register temuan **tanpa persetujuan berjenjang**: auditor menerbitkan, Direktur menerima. Akar penyebab lahir kosong dan diisi pemeriksa — sistem hanya menunjukkan selisihnya.

### 6. Gagal-TERTUTUP dan berisik, kebalikan dari gerbang presensi

Gerbang form di attendance-service sengaja **gagal-terbuka**, dan itu benar di sana. Untuk modul audit keputusannya **dibalik**: daftar uji yang kosong karena sumbernya tak terjangkau terbaca sebagai "tidak ada yang perlu diperiksa".

Dua celah dari kelas ini ditutup dan diuji saat implementasi:

- **Populasi nol bukan bersih.** Accurate membalas `s:false` untuk akun tak ditemukan dan client menerjemahkannya jadi daftar kosong tanpa galat. Tanpa penjaga, uji kas melaporkan "tidak ada saldo negatif" atas akun yang tak pernah ketemu. Penjaga transport tidak menangkapnya sebab `s:false` bukan kegagalan transport.
- **Sisi silang yang kosong bukan bersih.** Nol kecocokan adalah hasil yang diinginkan, sehingga sisi kosong menyamar jadi kabar baik.

### 7. Vonis manusia dipisah dari keadaan mesin

**Ditambahkan 2026-09-02 dari hasil review.**

Vonis peninjau (`keadaan_tinjauan`) hidup **di luar** subdokumen hasil mesin, dan penarikan ulang hanya menulis `hasil`. Sebelumnya keduanya menumpuk di satu field, sehingga tiap penarikan mengembalikan vonis auditor ke keadaan mesin sementara alasannya tetap tertinggal — baris menggendong "sudah saya periksa, wajar" sambil berstatus belum ditinjau.

Bukan kasus tepi: penjadwal menyala tiap sepuluh menit di dalam jendela, dan tombol tarik ulang terbuka bagi tiap pemegang `audit.tinjau`.

⛔ **Penjaganya STRUKTURAL, bukan pemeriksaan bersyarat.** Pemisahan field membuat pertentangannya mustahil, bukan sekadar dijaga; pemeriksaan bersyarat bisa lupa dipasang orang berikutnya. Urutan menangnya hidup di satu tempat, `KeadaanEfektif()`.

Menyertainya: periode yang **sudah diterbitkan menolak ditarik ulang**. Laporan yang sudah diserahkan tidak boleh berubah angkanya di bawah tanda tangan.

### 8. Ukuran sampel adalah master data Direksi, berlantai, dan berjejak

- Izin `audit.master.save` **terpisah** dari `audit.tinjau`. Yang menyetel ukuran sampel menentukan beban kerja peninjau; menyatukannya membuat peninjau menyetel sendiri berapa banyak yang harus ia periksa.
- **Lantai 5 untuk metode acak.** Ukuran sampel adalah tuas yang dapat mematikan kontrol **tanpa terlihat mematikannya**: disetel 1, ujinya tetap berjalan dan tetap hijau, dan dari layar "bersih dengan sampel 1" terbaca sama dengan "bersih dengan sampel 40".
- **Acak dan terarah menjawab pertanyaan berbeda.** Sampel acak untuk "20 jurnal terbesar" melewatkan jurnal terbesar; sampel terarah untuk konfirmasi pelanggan menghasilkan kesimpulan yang tak bisa digeneralisasi. Metodenya diambil dari registry, bukan dari permintaan — kalau tidak, sampel acak bisa lolos lantai dengan menyebut dirinya terarah.
- **Benih dari `crypto/rand`, bukan waktu.** Benih yang diturunkan dari waktu bisa dihitung ulang siapa pun yang tahu kira-kira kapan penarikannya terjadi, dan sampel yang bisa ditebak pihak yang diperiksa tidak bernilai sebagai pemeriksaan.
- Perubahan setelan **berjejak siapa, kapan, dari berapa ke berapa**.

### 9. Buku besar per akun digerbang kunci layanan, bukan gerbang menu

**Ditambahkan 2026-09-02 dari hasil review.**

`GET /accounting/riwayat-akun` memaparkan tiap transaksi, tanggal, nomor dokumen, keterangan, dan nominal untuk akun **apa pun**, rentang apa pun. Ia lebih luas daripada `/balance-sheet` yang sudah digembok: neraca memberi saldo, ini memberi jejak transaksinya.

- `BIP-Gateway-ID` **tidak cukup**: gateway memasangnya pada setiap permintaan yang lolos JWT ([[ADR - 0031 Prefix internal Bukan Batas Keamanan]]), jadi bersandar padanya berarti membuka buku besar bagi seluruh karyawan yang sudah login.
- Gerbang menu **juga tidak cukup**: ia sengaja gagal-terbuka saat header izin absen.

Yang dipakai gerbang kunci layanan `INTEGRATION_SERVICE_KEY`, dan **kunci kosong MENUTUP rutenya**. Konsekuensi yang diterima sadar: ia jadi rute mesin-ke-mesin, bukan rute layar.

### 10. Jejak adalah produknya, bukan catatan tambahan

Kegagalan menulis jejak **menggagalkan aksinya**. Ini pembalikan sadar dari kebiasaan best-effort di modul lain repo ini (manufacture, recruitment, template KPI) yang sengaja tidak menggagalkan aksi utama. Alasan pembedaannya: di sana jejak catatan tambahan, di sini jejak adalah produknya.

Menandai wajar **wajib beralasan**. Checklist yang bisa dicentang tanpa alasan berubah jadi stempel yang justru menghasilkan bukti tertulis bahwa seluruh uji sudah diperiksa.

Temuan yang direvisi menyimpan **nilai sebelumnya secara utuh**, lima unsur lengkap, dan aksinya ditandai `revisi` bukan `terbitkan`.

### 11. Cakupan berhenti di pembukuan PT

Penjualan ke konsumen akhir, sebagian besar beban iklan, dan payroll advertiser dibukukan di 40 CV lewat aplikasi di luar ERP maupun Accurate, yang berjalan tanpa jejak audit, tanpa kunci periode, dan dengan kredensial bersama di bundel klien ([[APP - Buku Besar Konsolidasi CV FINCON]]). Modul audit **tidak** menjangkaunya karena arahnya terkunci [[ADR - 0068 Buku Besar Konsolidasi 40 CV di Luar Accurate]].

Yang tidak boleh terjadi: cakupan ini hilang diam-diam. Modul yang memeriksa buku pertama dengan teliti sementara buku kedua tak punya satu pun kontrol akan terbaca sebagai jaminan yang tidak pernah diberikan.

## Belum selesai

- ⛔ **Belum pernah dijalankan lewat gateway.** `docker-compose.dev.yml` **tidak punya blok `finance-service` sama sekali**, jadi seluruh modul ini tak dapat dicoba di dev. Rutenya membalas 502 di sana, bukan 403 atau 200.
- ⛔ **Dua endpoint ERP belum ada**: `/internal/audit/pemasok` di procurement dan `/internal/audit/karyawan` di employee. Sampai keduanya dibangun, uji silang pemasok berkeadaan `gagal_tarik` dengan sebab terbaca — bukan bersih.
- ⚠️ **Utang kontrak `SetelanSampel.Akun`**: didokumentasikan sebagai NAMA akun tetapi dipakai sebagai NOMOR akun pada jalur buku besar. Gejalanya sudah jinak (berujung `gagal_tarik` berisi sebab yang menyebut obatnya), tetapi **wajib selesai sebelum Direksi menyetel akun untuk pertama kali** — sesudah itu menuntut migrasi setelan.
- ⚠️ **Tiga gerbang kelayakan belum dijalankan**, seluruhnya bacaan produksi oleh manusia: apakah Accurate mengirim jejak pelaku (menyandera 2 uji), apakah matriks hak akses dapat ditarik (menyandera Modul G), dan apakah dokumen Bayar Uang membawa rekening penerima.
- ⚠️ **Mesin pencatat reproduksibilitas sampel terpasang tetapi belum tersambung**: belum ada uji bermetode acak yang berjalan di fase ini.
- ⚠️ **Layar merged tetapi belum terverifikasi sama sekali.** Ketiga halaman lolos `tsc`, `lint`, `build`, dan 32 test lokal, tetapi **tak satu pun pernah memuat data sungguhan** — sebabnya sama dengan butir pertama: `finance-service` tak ada di dev. Merged bukan berarti tergerbang, dan test hijau bukan bukti fitur bisa dipakai.
- ⚠️ **Paket izin belum dipasang ke satu akun pun.** Sampai `Audit: Auditor Internal` / `Audit: Direksi` / `Audit: Pembaca` ditugaskan lewat layar Hak per Posisi, kategori sidebarnya tidak muncul untuk siapa pun kecuali pemegang super-akses menu (IT supervisor dan jabatan Direktur), yang melihat menunya lalu ditolak backend.

## Consequences

- ➕ Tidak ada integrasi Accurate baru untuk sebagian besar modul, dan tidak ada container baru.
- ➕ Independensi terjaga di lapisan penarikan: angka tidak pernah melewati tangan divisi yang diaudit. Manfaat ini bahkan tidak diklaim dokumen prosedurnya.
- ➕ Uji yang belum berimplementasi tetap terbit di kertas kerja sebagai baris berkeadaan `belum_diimplementasi`. Uji yang hilang dari daftar akan terbaca sebagai uji yang lolos.
- ➖ Modul terikat pada bentuk endpoint yang ada; uji yang menuntut field belum tersedia harus menunggu endpointnya diperluas.
- ➖ Modul audit menumpang di service yang mengelola domain yang diauditnya. Pemisahnya RBAC, bukan batas proses.
- ⚠️ **Izin wajib didaftarkan TIGA kali**: di service penegak, di `services/employee/permission_catalogs.go`, dan di setup test `shared-library`. Yang kedua menentukan apakah izinnya muncul di dropdown penyusun permission set; yang ketiga menentukan apakah paketnya lolos `ValidatePermissionSet`.
- ⚠️ **Env baru menuntut `--force-recreate`**, bukan `restart`: `PROCUREMENT_MODULE_URL`, `EMPLOYEE_MODULE_URL`, dan `INTEGRATION_SERVICE_KEY` di blok `finance-service`.
- ⚠️ **Urutan deploy**: integration-service lebih dulu (endpoint riwayat akun beserta gerbangnya), baru finance-service.
- ⚠️ Pemakai utamanya belum ada. Sampai posisi auditor internal terisi, modul dipakai review silang antar-divisi.
- ⚠️ **Tiga izin tulis yang berbeda menuntut tiga gerbang berbeda DI LAYAR, bukan satu.** Ini konsekuensi langsung §8 (yang menyetel ukuran sampel bukan yang mengerjakan pemeriksaan): dua dari tiga paket bawaan memegang `audit.view` sehingga rutin membuka kertas kerja tanpa satu pun izin tulisnya. Layar pertama yang dirancang dari dokumentasi melewatkannya seluruhnya, karena aturannya hanya hidup sebagai gerbang rute di `audit_handler.go`. Pemetaan lengkapnya kini ada di [[Finance - Audit Internal]].
- ⚠️ **Kategori sidebar `audit` lahir HANYA dari paket izin.** Tak ada `system_roles.audit` dan `AuditTierDefault` kosong, jadi modul ini satu-satunya yang sepenuhnya bergantung pada penugasan paket. Konsekuensi turunannya: menugaskan paket adalah langkah **deploy**, bukan langkah opsional.

## Dokumen Terkait

- [[Finance - Audit Internal]] — dok domain: cara kerjanya, 36 uji, dan batas tiap kelompok
- [[ADR - 0001 Akuntansi via Accurate]] · [[ADR - 0068 Buku Besar Konsolidasi 40 CV di Luar Accurate]]
- [[ADR - 0066 Salinan Dokumen Retur Accurate + Pemindai Drift]] — pola cermin dan pemindai drift
- [[ADR - 0037 Rekonsiliasi Aset GA dengan Accurate untuk KPI]] · [[ADR - 0067 Opname Perlengkapan GA via Rekonsiliasi Accurate]] — pola menyajikan dua angka berdampingan
- [[ADR - 0031 Prefix internal Bukan Batas Keamanan]] · [[CORE - RBAC dan Permission Set]]
- [[API - Integration Service]] · [[Microservices - Integration Service]] · [[External - Accurate]]
- [[APP - Buku Besar Konsolidasi CV FINCON]] · [[Finance - Big Pictures]] · [[Finance - Rancangan Finance Service]]
