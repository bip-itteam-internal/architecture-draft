**Status**: ⚠️ **Implementasi (FE), diringkas 2026-09-26 — isi per posisi pindah ke modul kerjanya.** Dashboard `/finance` bukan lagi sebelas tab per posisi, tapi dua tab **Ringkasan Divisi** dan **Kamus & Catatan**; ruang kerja per posisi di portal (`/dashboard`) tetap ada tapi kini memuat komponen yang ASLI dari modul kerjanya. Lihat [[ADR - 0130 Dashboard FAT Diringkas, Isi Posisi Pindah ke Modul Kerjanya]]. ✅ **Layar Tim Accounting dirombak 2026-10-09** (erp-frontend #2240, merge `a53f3c359`): tiga tab Ringkasan, Jurnal, Histori, tanpa penanda "belum ada sumber data" (lihat § Tim Accounting). 🟡 Tab **Kas dan Bank** di layar itu **belum dibangun** ([[ADR - 0163 Salinan Saldo dan Arus Kas-Bank per Rekening Dimiliki Finance Service, Ditarik lewat Integration Service]]).

## Deskripsi

Menu **Finance** dulu menyediakan **dashboard per posisi** (Finance/Accounting/Tax — "FAT") lewat sebelas tab di `/finance`. Sejak diringkas (2026-09-26, erp-frontend #1750/#1751), `/finance` hanya dua tab — **Ringkasan Divisi** (angka divisi + bagian khusus Supervisor bagi yang berhak) dan **Kamus & Catatan** — dan isi tab lama pindah ke halaman modul kerja masing-masing:

| Bekas tab `/finance` | Pindah ke |
|---|---|
| Supervisor FAT | Dilebur ke Ringkasan Divisi; bagian khususnya (piutang B2B >60, utang lewat jatuh tempo, beban non-operasional, persetujuan menunggu, beban per kelompok, kotak masuk persetujuan) tampil hanya bila `lihatSemuaFinance` (supervisor mana pun atau anggota IT) |
| AR Leader, AR Staf | Tab **Penagihan · Retur · Uang Masuk** di [[APP - Web ERP]] `/finance/ar` (bergabung dengan tab kanal piutang yang sudah ada di sana) |
| Senior + Junior Accounting | Halaman baru `/finance/tim-accounting`, menu sidebar **"Tim Accounting"** (isinya dirombak 2026-10-09, lihat § Tim Accounting) |
| Tax Officer | Kartu unik ("Beban pajak efektif", "PPN Masukan") pindah ke `/finance/pajak` |
| Accounting Payable | Kartu unik ("Costing HPP Valid") pindah ke `/finance/ap` |
| Cost Control | Dihapus — isinya (varians OPEX) sudah ada di `/finance/anggaran` |
| Accounting CV | Dihapus — satu-satunya elemen hidupnya ("Penjualan per toko", `useFetchPenjualanToko`/endpoint `GET /transactions/orders/summary/shops`) **dibuang, bukan dipindah**: keputusan user 2026-09-26 saat review rencana. Endpoint itu kini tanpa konsumen FE. |
| Kamus | Tetap tab `/finance` |

Rute lama `/finance/posisi/<slug>/page.tsx` **tidak dihapus** — semuanya jadi `redirect()` ke tujuan barunya (peta tunggal `posisi/lib/tujuan-posisi-lama.ts`), supaya tautan dan penanda buku lama tak putus.

Kode: `erp-frontend/src/features/finance/posisi/`
- `lib/daftar-posisi.ts` (`KELOMPOK_POSISI`) — SATU sumber isi tab `/finance`: kini hanya Ringkasan + Kamus.
- `lib/tab-untuk-posisi.ts` (`PETA_POSISI`, `slugUntukPosisi`) — memetakan **nama posisi** (dari `work_data`) ke **slug ruang kerja** (`ringkasan` | `ar-leader` | `ar-staf` | `tim-accounting`). Dipakai portal `/dashboard` (via `RUANG_KERJA_FAT`) dan kartu Skor KPI (`skor-kpi-posisi.ts`) — **satu peta**, bukan dua, supaya "siapa pemegang posisi X" tak bisa menyimpang antara kedua pemakai.
- `components/isi-tab.tsx` — dua peta yang SENGAJA dipisah: `ISI_KHUSUS` (isi tab `/finance`, kini tinggal Ringkasan) dan `RUANG_KERJA_FAT` (isi ruang kerja portal per slug posisi, komponennya diimpor langsung dari modul kerja masing-masing — bukan salinan).
- `components/isi-ringkasan-divisi.tsx` — Ringkasan Divisi, menyerap bagian Supervisor lewat `components/bagian-supervisor.tsx` (dirender hanya bila `lib/lihat-semua.ts` `lihatSemuaFinance()` true).
- `components/halaman-posisi.tsx` — perender generik (kartu/bagan/tabel/peringatan) dari deskripsi statis, dipakai tab Kamus dan tab AR (`ar/components/tab-penagihan.tsx`, `tab-retur.tsx`, `tab-uang-masuk.tsx`). Sejak 2026-10-09 halaman Tim Accounting **tidak lagi** memakainya.
- `components/bagan/` — pustaka grafik lokal: `BaganBatang`, `BaganBatangHorizontal`, `BaganGaris`, `BaganPersen`, `BaganDonat`. Warna dari token tema `WARNA_SERI` (`var(--fat-*)`), bukan heksa.
- Rute aktif: `app/(main)/finance/page.tsx` (tab `?posisi=`), `app/(main)/finance/tim-accounting/page.tsx` (guard `finance.accounting.view`, tab lewat `?tab=`). Rute pengalih: `app/(main)/finance/posisi/*/page.tsx`.

Hak akses per posisi mengikuti model RBAC yang hak-nya menempel di posisi — lihat [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]].

Siapa pemegang tiap posisi di produksi, akses nyatanya, dan bagaimana pekerjaan mengalir antar posisi dicatat di [[Finance - FAT Persona]] (diukur prod 2026-09-12, **belum diukur ulang setelah peringkasan 2026-09-26** — path kode `posisi/data/<posisi>.ts` dan `posisi/components/isi-<posisi>.tsx` yang disebutnya sudah dihapus untuk posisi yang isinya pindah/dibuang; TBD naikkan dok itu). Temuan lama yang masih berlaku: Account Payable dan Tax Officer di prod belum memegang izin apa pun, sehingga halaman kerjanya belum bisa mereka buka.

## Prinsip data (penting)

- **Tidak ada angka palsu.** Elemen yang hook-nya belum dipanggil dirender sebagai panel **"menunggu penyambungan data"** dengan nama hook-nya terlihat — bukan angka nol yang terbaca "tidak ada transaksi". Tiap helper grafik mengembalikan keadaan **kosong** saat datanya `undefined`.
- **Pass/fail hanya untuk target yang sudah tertulis di kode.** Indikator target‑vs‑aktual dipasang di ambang yang memang ada (AR Staf: piutang >14 hari & retur >14 hari, "maks 5%"). Ambang yang masih parameter manusia tanpa master (mis. SPV "beban non‑operasional ≤2%") **sengaja tidak** dijadikan lampu lulus/gagal.
- ⚠️ Prinsip "panel menunggu penyambungan" di atas **tidak lagi berlaku untuk Tim Accounting** sejak 2026-10-09: layar itu membuang semua penandanya dan hanya menampilkan yang punya sumber; kebutuhan yang belum terpenuhi dicatat di § Tim Accounting di dok ini, bukan di layar.
- Sumber angka lintas modul; akuntansi via [[External - Accurate]] (laba rugi, saldo, varians anggaran).

## Grafik & indikator yang sudah hidup (per lokasi baru, diukur 2026-09-26)

Isi per posisi tidak hilang saat diringkas — dipindah utuh ke halaman modul kerjanya. Tabel di bawah menggantikan tabel lama "per posisi", yang lokasinya sudah usang:

| Elemen | Lokasi sekarang | Sumber |
|---|---|---|
| Aging piutang & Aging utang (donat); OPEX anggaran vs realisasi (batang) | Ringkasan Divisi (`/finance`) | `useFetchPiutangSummary`, `useAgingUtang`, `useFetchVariansEnamBulan` |
| Tren AR >60 hari (garis); Beban per kelompok (persen); Aging piutang (donat); kotak persetujuan — hanya tampil bagi supervisor/IT | Ringkasan Divisi, bagian Supervisor (`bagian-supervisor.tsx`) | agregator persetujuan, laba rugi & piutang Accurate |
| Status penyelesaian retur (batang); Belum dicocokkan per kanal (persen); indikator target **Piutang >14 hari** & **Retur >14 hari** (maks 5%) | `/finance/ar` tab Retur + Uang Masuk; kartu Piutang >14 Hari juga di ruang kerja portal AR Staff | `useFetchReturnStats`, `useFetchMissingAgregat` |
| Uang tertagih per minggu (batang); Komposisi piutang per umur (persen) | `/finance/ar` tab Penagihan | `useFetchReceiptMingguan`, `useFetchPiutangSummary` |
| Varians per pos biaya (batang‑horizontal); Anggaran vs Realisasi per pos (batang 2 seri) | `/finance/anggaran` (tab Master) | `useFetchVariansAnggaran` |
| Kartu, panel, dan tabel Tim Accounting (bagan "Transaksi hari ini vs rata‑rata" dan donat aset tetap **sudah diganti** kartu/panel batang 2026-10-09) | `/finance/tim-accounting`, rincian di § Tim Accounting | lihat § Tim Accounting |
| Aging utang (batang) | `/finance/ap` | `useAgingUtang` |
| Costing HPP Valid (persen SKU ber-HPP) | `/finance/ap` (`kartu-costing-hpp.tsx`) | `useFetchRasioHpp` |
| Beban pajak efektif, PPN Masukan | `/finance/pajak` (`kartu-pajak-lanjutan.tsx`) | `useFetchLabaRugi` (perhitungan lokal) |
| ~~Penjualan per toko (Accounting CV)~~ | **Dibuang**, tanpa pengganti (keputusan 2026-09-26) | ~~`useFetchPenjualanToko`~~ |

Komponen indikator: `components/kartu-indikator-target.tsx` (pil hijau/amber/merah + bar target), status dihitung `lib/status-ambang.ts` (`statusAmbang({nilai,target,arah})` → `sehat|waspada|kritis`). Transform data grafik ada di `lib/bagan-*.ts` (murni, ber‑unit test).

## TBD (menunggu backend)

Masih panel jujur "menunggu penyambungan" di lokasi barunya masing-masing (Tim Accounting **tidak termasuk**: kebutuhannya dicatat di § Tim Accounting): AR "hasil penagihan per cara hubung", Anggaran & Cost Control "forecast kas" & "penghematan terealisasi", Pajak "biaya non‑deductible per penyebab". Butuh endpoint/agregat backend baru sebelum bisa dijadikan grafik.

## Tim Accounting (`/finance/tim-accounting`)

*Diukur 2026-10-09 terhadap erp-frontend `origin/main` sesudah #2240 (merge `a53f3c359`). Semua path di bawah relatif ke `erp-frontend/`.*

Halaman gabungan bekas tab Senior + Junior Accounting. Guard halaman `finance.accounting.view` untuk SEMUA tab (`src/app/(main)/finance/tim-accounting/page.tsx:100`); menu sidebar di `src/components/layout/sidebar-menus.tsx:466`. Tab aktif dibaca dari `?tab=` (`src/features/finance/tim-accounting/lib/tab-tim-accounting.ts`); nilai asing, termasuk `?tab=pencatatan` yang dulu tab sendiri, jatuh ke Ringkasan (`page.tsx:51-53`, komentar `tab-tim-accounting.ts:11-12`).

| Tab | `?tab=` | Isi | Kode |
|---|---|---|---|
| **Ringkasan** (bawaan, tak ditulis di URL) | `ringkasan` | Delapan kartu, tiga panel batang, lalu tabel antrean Menunggu Dicatat. Dipakai juga sebagai ruang kerja Senior/Junior Accountant di `/dashboard` (`RUANG_KERJA_FAT`) | `components/isi-tim-accounting.tsx:40-80` |
| **Jurnal** | `jurnal` | Tiga kartu (Transaksi Hari Ini, Jurnal Terkirim, Jurnal Gagal); tabel Jurnal Pembayaran (yang gagal paling atas) berdampingan dengan Jurnal Umum bertanggal hari ini, berpaginasi server, baris membuka rincian debit-kredit | `components/tab-jurnal-tim-accounting.tsx:317-336` |
| **Histori** | `histori` | Dokumen yang **pernah** lewat tahap `pb_accounting_catat`, tak peduli tahap/status sekarang; komponen yang sama dengan histori `/finance/ap` | `page.tsx:84-90`, `src/features/pengajuan-barang/components/tabel-histori-pengajuan.tsx` |

**Kartu Ringkasan** (urutan di `isi-tim-accounting.tsx:58-67`): Menunggu Dicatat, Paling Lama, Dicatat (jendela `JENDELA_DICATAT_HARI` di `lib/antrean-accounting.ts:26`, hanya aksi `dicatat`), Jurnal Gagal (menaut ke tab Jurnal), Rekonsiliasi Bank (menaut ke tab Rekening Bank pada bulan kartunya), Transaksi Hari Ini vs rata-rata (jendela `HARI_RATA_RATA_JURNAL` di `lib/rentang-jurnal.ts:5`), Aset Belum Didepresiasi, Skor KPI. **Panel**: Lama Menunggu Dicatat (kelompok umur, batas di `BATAS_UMUR_HARI`, `antrean-accounting.ts:23`), Komposisi Aset Tetap (tombol Segarkan tetap ada), Menunggu Dicatat per Departemen (`components/panel-tim-accounting.tsx`). Kartu dan panel yang sumbernya gagal dimuat tampil berketerangan gagal, bukan angka 0.

### Izin yang menentukan apa yang terlihat

Satu fungsi, `aksesTimAccounting` (`src/features/finance/tim-accounting/lib/izin-tim-accounting.ts:29-36`), dengan fallback `false` untuk ketiganya (izin ini tak punya tier `system_roles` lama):

| Izin | Bagian yang bergantung padanya | Tanpa izin |
|---|---|---|
| `budget.accounting.pencatatan` (`izin-tim-accounting.ts:12`) | kartu Menunggu Dicatat dan Paling Lama, dua panel antrean, tabel antrean | Seluruh bagian itu **diganti satu keterangan** (`role="note"`, `isi-tim-accounting.tsx:49-56`). Alasannya: antrean memendek di server (tahap `pb_accounting_catat` hanya muncul bagi pemegang izin ini, lihat [[API - Procurement Service]]), jadi angkanya bukan nol sungguhan |
| `budget.jurnal.view` (`izin-tim-accounting.ts:13`) | kartu Jurnal Gagal dan Jurnal Terkirim, tabel Jurnal Pembayaran | Tidak dirender sama sekali, `GET /pengajuan-barang/pembukuan` tidak dipanggil (backend membalas 403 tanpa izin ini) |
| `rekonbank.view` atau `rekonbank.edit` (`izinBacaBank`, `src/features/integration/accurate/reconciliation/bank/lib/izin.ts:14-19`) | kartu Rekonsiliasi Bank | Tidak dirender, query tidak jalan |

Kartu yang tidak berhak tidak dirender (bukan dirender lalu disembunyikan). Jurnal Umum dan sisa kartu mengikuti guard halaman saja. Gerbang di backend tetap yang menentukan; daftar izin dan pemetaan tahapnya di [[API - Procurement Service]] dan [[CORE - RBAC dan Permission Set]].

⚠️ **Super-akses belum dikenali layar ini** (diketahui di badan #2240): hanya izin eksplisit yang dibaca. Bila backend juga membuka antrean pencatatan untuk `budget.superadmin` atau supervisor IT, pemegangnya tetap membaca keterangan "hanya tampil bagi pemegang izin pencatatan". TBD: apakah backend memang membukanya, belum dibaca di sesi ini.

### Tab Kas dan Bank: 🟡 BELUM DIBANGUN

Tab keempat **tidak ada di kode** (`DAFTAR_TAB_TIM_ACCOUNTING` hanya berisi tiga nilai, `tab-tim-accounting.ts:30-46`). Rencananya: sisa saldo, uang masuk, dan uang keluar per CV dan PT untuk satu bulan, salinan dari Accurate dengan jam data terakhir dan tombol Segarkan. Keputusannya [[ADR - 0163 Salinan Saldo dan Arus Kas-Bank per Rekening Dimiliki Finance Service, Ditarik lewat Integration Service]] (🟢 Diterima 2026-10-09). Pekerjaan: backend bip-erp#2880 (belum merged per 2026-10-09), layar erp-frontend#2235 (menyusul, sesudah backend). Sebelum keduanya merged, jangan menulis tab ini sebagai fitur yang berjalan. Ukur ulang statusnya sebelum dipakai.

### Kebutuhan yang BELUM terpenuhi (dulu tampil sebagai penanda di layar)

Sebelum #2240 layar memuat 12 kartu, 3 bagan, dan 2 tabel dari `data/tim-accounting.ts`, sebagian besar berstatus "belum" (berkas itu dihapus #2240; isinya dibaca dari `a53f3c359^1`). Keputusan induk (bip-erp#2879, Pemutus 2026-10-09) memindahkan daftar ini dari layar ke dok ini. Daftar di bawah **tetap berlaku** sebagai kebutuhan yang belum dibangun, kecuali yang diberi catatan:

| Elemen lama | Jenis | Yang dibutuhkan agar bisa hidup | Keadaan 2026-10-09 |
|---|---|---|---|
| Progres tutup buku; Target selesai; Ketepatan tutup (maks tgl 3); tabel Daftar langkah tutup buku | kartu ×3, tabel | Modul tutup buku / closing checklist: langkah, PIC, tenggat, status per langkah | Belum ada. Lihat juga [[Finance - Proses Tutup Buku, Stock Opname, dan Laporan]] |
| Selisih rekonsiliasi bank (nilai selisih dan jumlah rekening cocok) | kartu | Alur rekonsiliasi rekening koran terhadap GL (bukan `/wallet/reconciliation`, yang mencocokkan settlement marketplace) | **Sebagian**: kartu Rekonsiliasi Bank kini menampilkan rekening selesai dari jumlah rekening per bulan (`kartu-tim-accounting.tsx`, `KartuRekonBank`), **bukan nilai selisih**. Nilai selisih: TBD |
| Umur selisih rekonsiliasi | bagan | Tiap selisih tercatat dengan tanggal asalnya | Belum ada |
| Selisih rekonsiliasi persediaan | kartu | Angka hasil stock opname fisik beserta alur yang mempertemukannya dengan stok Accurate dan stok WMS | Belum ada |
| Koreksi jurnal bulan ini; Jumlah koreksi jurnal | kartu, bagan | Penanda mana jurnal yang merupakan **koreksi**; tanpanya yang terhitung seluruh jurnal | Belum ada penanda koreksi |
| Dikoreksi checker (maks 3%); Dokumen tidak lengkap; Koreksi per jenis transaksi | kartu ×2, bagan | Alur maker-checker pencatatan: peran checker, jejak koreksi, penanda kelengkapan dokumen | Belum ada |
| Menunggu dicatat; tabel Antrean pencatatan | kartu, tabel | Antrean transaksi sebelum dijurnal | **Sebagian terpenuhi**: kartu Menunggu Dicatat dan tabel antrean kini berjalan dari tahap `pb_accounting_catat`. Kolom **Penahan** dan **Status** yang diminta rancangan lama **tidak ada** (kolom antrean: nomor, pengaju, departemen, kategori, CV, nominal, menunggu; `antrean-pencatatan-accounting.tsx:69-127`) |

Aset belum didepresiasi dan Skor KPI sudah berjalan sejak sebelum #2240. Tiga catatan lama yang ikut dibuang dari layar tetap benar sebagai peringatan: rekonsiliasi di sini = rekening koran terhadap buku besar; dua aksi tutup buku dan rekonsiliasi masih dikerjakan di luar sistem sehingga jejaknya tak bisa diaudit dan KPI yang bergantung padanya tak bisa dihitung otomatis.

## Rancangan isi menurut ADR 0076

*Ditambahkan 2026-09-04, **path layar di bawah belum diperbarui** setelah peringkasan 2026-09-26 — tabel "Grafik & indikator yang sudah hidup" di atas memuat lokasi baru; bagian ini merekam analisis KPI apa adanya karena masih berlaku, terlepas dari layar mana yang merendernya. Analisisnya dinilai terhadap [[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]], sejajar dengan sembilan divisi lain. Angka KPI diukur 2026-08-28 dari [[HRIS - Matriks KPI per Departemen]]; ukur ulang sebelum dipakai mengambil keputusan.*

Divisi ini punya **61 metrik di 8 posisi**, jumlah terbanyak di perusahaan. Yang sudah menyala otomatis di produksi baru satu: `Performance Monitoring Team` milik Finance Supervisor.

### Dua penghambat memakan 30% metrik divisi ini

⛔ **Delapan belas dari 61 metrik (29,5%) adalah dua hal yang sama, berulang di hampir tiap template.**

| Penghambat | Metrik | Posisi |
|---|---:|---|
| **Tidak ada log 1-on-1** | 8 | semua kecuali Finance Supervisor dan AR Staff Piutang |
| **Ide inovasi / Kaizen** | 10 | tujuh dari delapan posisi |

Keduanya menuntut perlakuan yang **berbeda**, dan membedakannya menentukan apakah dashboardnya jujur:

- **Kaizen tidak boleh digambar sama sekali.** Ia manual **karena keputusan** ([[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]]), bukan karena sistemnya kurang. Panel "menunggu penyambungan" di sana akan berbohong tentang sebabnya, dan sepuluh panel berbohong yang tersebar di tujuh layar adalah cara tercepat membuat orang berhenti mempercayai panel jujur di tempat lain.
- **1-on-1 boleh digambar sebagai panel jujur**, sebab ia memang menunggu fitur yang belum ada. Satu fitur log 1-on-1 membuka delapan metrik sekaligus, dan itu bobot antara 0,05 sampai 0,15 di masing-masing dari tujuh posisi.

### Yang siap dijadikan visual utama

| Posisi | Kandidat visual utama | Sumber |
|---|---|---|
| AR Staff (Piutang) | umur piutang terhadap ambang 14 dan 60 hari, bobot gabungan 0,9 | `GET /accounting/receivables` |
| AR Staff (Retur) | pencatatan retur, bobot 0,5 | `accurate_daily_returns` 3.351 |
| AR Staff (Sales Admin) | pencatatan penjualan, bobot 0,5 | `kinerja_sales_admin` |
| AR Leader | piutang > 60 hari dan pengawasan ≤ 14 hari, bobot gabungan 0,6 | Accurate proxy |
| Finance Supervisor | sebaran skor KPI tim terhadap ambang | `skor_tim`, **sudah menyala** |
| Cost Control | varians OPEX terhadap ±5% | perlu master anggaran |

Empat posisi AR adalah kelompok paling siap, dan ketiganya sudah punya elemen hidup di layar sekarang (lihat tabel Grafik & indikator di atas).

### Yang harus diputuskan sebelum digambar

⚠️ **Metrik `Monitoring Team` di AR Leader (0,2) dan Senior Accountant (0,1) BUKAN skor tim murni.** Deskripsinya menggabungkan checker inputan dengan ketepatan tanggal, dua hal berbeda dalam satu metrik. Menggambarnya sebagai kartu skor tim akan menampilkan angka yang tidak menjawab separuh isi metriknya. Pisahkan lebih dulu di master data, atau jangan digambar.

⚠️ **Metrik `Pengelolaan Aset Tetap` Senior Accountant (0,15) dan `Pengelolaan asset/perlengkapan` Junior Accountant (0,15) dipetakan ke `manufacture_resi` dan `fulfillment_orders`**, yaitu data resi dan pemenuhan pesanan gudang. Aset tetap akuntansi tidak ada hubungannya dengan itu. Salah petak, sekelas dengan yang tercatat di [[GA - Dashboard per Posisi]] dan [[Manufacture - Dashboard per Posisi]].

⚠️ **Tax Staff punya tiga metrik bernama `Kepatuhan pajak 100% setiap bulan` 1, 2, dan 3** dengan sumber berbeda-beda, dua di antaranya menunggu tracker pajak yang tidak ada. Nama yang tak dapat dibedakan membuat layar detailnya mustahil dibaca; ini persoalan penamaan metrik ([[REF - Penamaan Metrik & Sumber KPI]]), bukan persoalan dashboard.

### Kebutuhan backend, terurut

1. **Fitur log 1-on-1.** Membuka 8 metrik di 7 posisi dalam satu pekerjaan. Daya ungkit tertinggi di divisi ini, dan **kemungkinan besar juga dibutuhkan Warehouse Leader** di [[Manufacture - Dashboard per Posisi]], jadi cakupannya lintas divisi.
2. **Master anggaran** untuk varians OPEX (Cost Control 0,2, Tax 0,15, Account Payable 0,25). Dipakai bersama [[GA - Dashboard per Posisi]] dan [[IT - Dashboard per Posisi]] yang membutuhkan hal yang sama untuk departemennya masing-masing.
3. **Pisahkan metrik `Monitoring Team`** di AR Leader dan Senior Accountant.
4. **Perbaiki pemetaan aset tetap** Senior dan Junior Accountant.
5. **Tracker pajak dan audit internal**, mengunci 5 metrik Tax Staff dan 1 Senior Accountant. Bersinggungan dengan modul Audit Internal yang sedang dipisah ([[ADR - 0074 Audit Internal Dipisah jadi Service dan Aplikasi Sendiri]]).
6. **Pemetaan metrik `Laporan keuangan`** yang muncul tanpa sumber di Junior Accountant (0,3), Senior Accountant (0,35 gabungan), dan Tax Staff (0,1).

## Dokumen Terkait

- [[ADR - 0130 Dashboard FAT Diringkas, Isi Posisi Pindah ke Modul Kerjanya]] — keputusan peringkasan 2026-09-26 dan peta pemindahan
- [[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]] — prinsip penurunan isi dashboard posisi
- [[REF - Layout Dashboard erp-frontend]] — cara menyusunnya di layar
- [[HRIS - Matriks KPI per Departemen]] — sumber angka bagian rancangan
- [[ADR - 0163 Salinan Saldo dan Arus Kas-Bank per Rekening Dimiliki Finance Service, Ditarik lewat Integration Service]] — tab Kas dan Bank Tim Accounting (belum dibangun)
- [[API - Procurement Service]] — gerbang tahap `pb_accounting_catat` dan pembukuan pengajuan
- [[CORE - RBAC dan Permission Set]] — katalog izin
- [[Finance - Proses Tutup Buku, Stock Opname, dan Laporan]] — proses tutup buku yang belum punya modul
- [[Finance - Big Pictures]] — peta domain Finance System
- [[Finance - FAT Persona]]: persona per posisi, akses nyata di prod, dan alur kerja antar posisi
- [[Finance - Incentive]] — dashboard insentif (menu Finance terkait)
- [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] — model hak akses per posisi
- [[External - Accurate]] — sumber angka akuntansi (laba rugi, varians anggaran)
