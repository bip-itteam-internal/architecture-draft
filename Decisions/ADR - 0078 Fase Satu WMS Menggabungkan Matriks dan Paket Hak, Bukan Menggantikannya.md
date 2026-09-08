## Deskripsi

*Menetapkan bagaimana katalog izin modul `manufacture` (WMS) hidup berdampingan dengan `MATRIKS_TAB_WMS` selama fase satu: keduanya **dijumlahkan** (union), bukan "klaim menang lalu tier diabaikan" seperti modul berkatalog lainnya. Keputusan ini lahir karena tier WMS bukan `staff/supervisor/admin` yang kasar melainkan matriks enam peran yang dipakai belasan orang setiap hari — sehingga pola baku akan membuat pemberian paket sempit MENCABUT hak tulis seorang admin gudang, senyap, dan persis kebalikan dari maksud pemberiannya.*

- **Status**: 🟡 **Diputuskan, menunggu merge** — bip-erp PR [#1723](https://github.com/bip-itteam-internal/bip-erp/pull/1723) + erp-frontend PR [#1463](https://github.com/bip-itteam-internal/erp-frontend/pull/1463), keduanya **belum merge**. Fase dua (`MANUFACTURE_TIER_FALLBACK=off`) belum dijadwalkan dan menuntut sensus lebih dulu.
- **Path di repo**: `bip-erp/shared-library/common/catalog_manufacture.go` · `bip-erp/services/manufacture/rbac.go` · `bip-erp/services/employee/permission_catalogs.go` · `bip-erp/shared-library/models/employee/permission_set.go` · `erp-frontend/src/features/manufacture/akses.ts` · `erp-frontend/src/utils/access.ts`
- **Tanggal**: 2026-09-05

## Context

[[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] menetapkan hak menempel pada posisi lewat permission-set, dan [[ADR - 0043 Peran Sistem Diturunkan dari Jabatan]] sengaja **menunda** katalog untuk `manufacture` dengan alasan yang benar: matriks WMS sudah punya cerminan backend yang wajib sinkron, dan menambah katalog berarti melahirkan bentuk ketiga yang harus dijaga sama selamanya.

Yang memaksa keputusan ini diambil sekarang adalah kebutuhan yang **tak bisa dinyatakan sama sekali** dengan mekanisme yang ada: memberi seseorang — Finance, Internal Audit, atasan — pandangan penuh atas WMS **tanpa** hak tulis. Satu-satunya jalan hari ini adalah `manufacture: ppic|supervisor`, yang sekaligus membuka seluruh tombol simpan, Sync Master, push Accurate, dan seluruh persetujuan. Halaman Hak Akses (`/it/hak-akses`) tak punya pengaruh apa pun terhadap WMS karena modulnya tak berkatalog.

Tiga fakta kode yang membentuk rancangannya:

- **Tier WMS bukan tingkatan, melainkan matriks.** Enam peran granular (`admin_gudang_rm`, `admin_gudang_fg`, `admin_produksi`, `ppic`, `qc`, `rnd`) × 28 tab, ditambah pengecualian lintas-modul untuk `finance`, `wms_viewer`, `quality`, `rnd`, `procurement`, dan posisi Security. Bandingkan dengan `ga` yang tiernya `staff|supervisor|admin` dan ketiganya mendapat izin yang sama rata.
- **Pola baku modul lain adalah penggantian.** `KlaimMemuatIzinModul` (dipakai `catalog_ga.go`, `catalog_secretary.go`, `catalog_hris.go`) berbunyi: bila klaim memuat izin modul ini, klaim yang berlaku dan tier **diabaikan sepenuhnya**.
- **Prefiks izin menentukan kategori sidebar.** `kunciModulAktif` (`erp-frontend/src/components/layout/modul-aktif.ts`) menurunkan kategori dari segmen sebelum titik pertama, dan key kategori WMS di `sidebar-menus.tsx` adalah `manufacture`.

## Decision

**1. Modulnya dinamai `manufacture`, bukan `wms`.** ADR 0030 menyebutnya `wms` dan nama itu lebih tepat menggambarkan isinya, tetapi modul bernama `wms` menghasilkan paket yang tersimpan rapi, tervalidasi, dan ter-assign — sementara kategori WMS-nya **tak pernah muncul** di sidebar pemegangnya, tanpa satu pun galat.

**2. Fase satu MENGGABUNG.** Yang berhak menurut izin **atau** menurut matriks lolos. Ini menyimpang sadar dari `KlaimMemuatIzinModul`.

Sebabnya bukan selera. Dengan pola baku, memberi seorang `admin_gudang_fg` paket `wms_pemantau` (baca semua tab) akan **mencabut** hak tulisnya atas Gudang FG, Analisa Stok, dan Master Data — sebab sejak klaimnya memuat izin `manufacture`, matriksnya berhenti dibaca. Tidak ada galat, tidak ada pesan; pengelola yang bermaksud **menambah** pemantauan justru melumpuhkan operator. Union membuat fase satu hanya bisa menambah, dan itu yang membuat penggelarannya benar-benar nol perubahan akses.

**3. Matriks pindah ke `shared-library/common`.** Inilah yang menjawab keberatan ADR 0043. Matriks, katalog izin, dan paket bawaan kini diturunkan dari **satu peta** di `catalog_manufacture.go`, sehingga sisi Go tak bisa menyimpang dari dirinya sendiri. Frontend masih memegang salinannya sampai fase dua: dua sumber, sama seperti sebelum ADR ini, bukan tiga.

**4. `.work` hanya untuk tab yang punya gerbang tulis.** Sepuluh dari 28 tab. Izin tanpa titik penegakan bisa dicentang pengelola, tersimpan di paket, ikut ke klaim, dan tak pernah diperiksa satu pun titik kode — ia menjanjikan kewenangan yang tak ada penegaknya. Aturan yang sama membuat `catalog_ga.go` menahan `ga.approve`.

**5. `input` dan `approve` tetap izin terpisah.** `requireK3Input` dan `requireGudangInput` hari ini menolak PPIC/SPV supaya approval tetap berarti sebagai bukti dua pasang mata. Melebur keduanya ke satu izin "tulis" akan membatalkan pemisahan itu lewat pintu belakang; karena itu paket `wms_ppic` sengaja **tidak** memuat `k3.input` maupun `gudang.input`.

**6. Penyempitan adalah urusan fase dua.** `MANUFACTURE_TIER_FALLBACK=off` mematikan matriks; sejak itu hanya pemegang paket yang boleh. Sakelarnya **sengaja tidak ditulis di compose sama sekali** (pola `SECRETARY_TIER_FALLBACK`) supaya tak bisa menyala tak sengaja seperti `KPI_TIER_FALLBACK` dulu.

## Consequences

- **Fase satu tak bisa mencabut apa pun.** Paket hanya menambah. Pengelola yang ingin mempersempit akses seseorang harus tetap mengubah `system_roles`-nya di Akun Karyawan sampai fase dua menyala. Ini harga yang dibayar untuk penggelaran tanpa risiko.
- **Fase dua mematikan super-akses IT.** `wmsSuperAccess` meloloskan `it: supervisor|admin`, dan cabang itu ada di dalam fallback. IT yang perlu masuk WMS untuk dukungan harus dipasangi paket `wms_ppic` di posisinya sebelum sakelar dinyalakan.
- **Fase dua menuntut tiga langkah bersamaan**, bukan satu env: matikan sakelar, **hapus** matriks di `erp-frontend/src/features/manufacture/akses.ts`, dan cabut baris `manufacture` di `services/employee/peran_dari_jabatan.go` (ADR 0043 memang menuntutnya begitu modul ini berkatalog). Membiarkan matriks FE hidup sesudah backend berhenti mempercayainya menghasilkan menu yang tampil lalu dijawab 403.
- **Delapan belas tab punya `.view` tanpa penegak backend** (`dashboard`, `history`, `reports`, `kpi`, `raw_materials`, `k3_gmp`, `cycle_count`, `stok_accurate`, dan seterusnya). Penegaknya hari ini hanya gerbang tab frontend, dan menu bukan keamanan ([[ADR - 0031 Prefix internal Bukan Batas Keamanan]]). Dicatat di dalam berkas katalog, bukan disembunyikan.
- **Paket rakitan tangan bisa tak sinkron.** Paket yang memuat `manufacture.k3.input` tanpa `manufacture.k3_gmp.view` membuat frontend menyembunyikan menunya sementara backend meloloskan endpoint-nya. Tak satu pun dari sepuluh paket bawaan menghasilkan kombinasi itu; ini konsekuensi kebebasan meracik, bukan cacat.
- **Klaim JWT membesar.** Katalog sistem tumbuh 83 → 128 izin; kasus terburuk ±11,4 KB gabungan cookie + Authorization. Masih jauh di bawah `ReadBufferSize` 32 KB yang sudah terpasang di gateway dan seluruh service.
- **Katalog sistem jadi 16 modul**, dan `manufacture` yang di ADR 0030 tercatat sebagai `wms` "belum berkatalog" kini terhapus dari daftar itu.

## Dokumen Terkait

- [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] — fondasi yang dijalankan ADR ini untuk modul WMS
- [[ADR - 0043 Peran Sistem Diturunkan dari Jabatan]] — jembatan yang mulai dibongkar oleh ADR ini
- [[ADR - 0039 Menu Terbatas Default Terbuka sampai Di-assign]] — mekanisme yang arahnya berlawanan (menutup, bukan membuka)
- [[ADR - 0031 Prefix internal Bukan Batas Keamanan]] — kenapa gerbang frontend bukan pengaman
- [[CORE - RBAC dan Permission Set]] — katalog acuan seluruh modul
- [[Microservices - Manufacture Service]] — matriks WMS yang dicerminkan
