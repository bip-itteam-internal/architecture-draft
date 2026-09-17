> **Tipe:** Log operasional (audit point-in-time), bukan dokumentasi arsitektur.
> **Tanggal:** 2026-09-17 · **Konteks arsitektur:** [[Microservices - Marketing Analytics Service]] · [[Microservices - Integration Service]] · [[APP - Web ERP]]

# Audit Checklist ERP Marketing dan Integration

Catatan **point-in-time** hasil audit 19 item checklist ERP divisi Marketing (baris 124–133) dan Integration (baris 134–142) terhadap kode. Checklistnya spreadsheet manajemen "Checklist_ERP_Bharata_Internasional" (sheet "Checklist ERP", dibuat 2026-09-14). Kolom "Kondisi Saat Ini" di sana diisi dari **melihat menu**, belum dari logika dan data.

- **Basis kode:** `origin/main` erp-frontend `fa33d34` dan bip-erp `f5bf38f` (17 Sep 2026 pagi).
- **Diperiksa:** rute dan komponen FE, endpoint dan handler Go, sumber data, gerbang akses, riwayat git sejak 1 Agu 2026, dan rencana kerja yang berjalan.
- **Tidak diperiksa:** perilaku langsung di DEV/PROD dan status deploy.
- ⚠️ **Status di bawah bergerak.** Ukur ulang sebelum dipakai untuk rencana.

## Ringkas

| Divisi | Status di checklist | Usulan status hasil audit |
|---|---|---|
| Marketing (10) | 1 Dalam Proses, 9 Belum Mulai | 2 Selesai, 6 Dalam Proses, 1 Revisi, 1 Tidak Relevan |
| Integration (9) | 9 Belum Mulai | 1 Selesai, 1 Dalam Proses, 4 Revisi, 2 Belum Mulai, 1 Tidak Relevan |

Hampir semua item masih tertulis "Belum Mulai", padahal sebagian besar sudah dibangun. Masalah yang sebenarnya ada di kelengkapan:
- celah akses di Integration (lihat §Temuan keamanan);
- satu halaman berisi data contoh yang tampil seolah data asli;
- Kamus Metrik yang bertentangan dengan rumus dashboard;
- tiga requirement yang salah menafsirkan nama menu.

**Definisi status usulan:**

| Status | Arti |
|---|---|
| Selesai | Requirement tertulis terpenuhi di kode tanpa gap berarti |
| Dalam Proses | Sebagian terpenuhi, atau masih aktif dikerjakan |
| Revisi | Sudah jalan tapi ada cacat atau celah yang wajib diperbaiki |
| Belum Mulai | Belum ada implementasi nyata, termasuk halaman berisi data contoh |
| Tidak Relevan | Requirement salah menafsirkan menu, atau menunya sudah dicabut |

## Marketing (baris 124–133)

| No | Requirement | Checklist → Audit | Temuan utama |
|---|---|---|---|
| 124 | Dashboard penjualan (omzet, growth) | Dalam Proses → **Dalam Proses** | Omzet, GMV, dan laba ada di Ringkasan. Growth baru untuk laba. `/beranda` sudah mengirim `delta_revenue_persen` tapi FE belum membacanya. |
| 125 | Informasi iklan: ROI, budget terpakai, ROAS | Belum Mulai → **Dalam Proses** | Sudah merged 2026-09-15 (erp-frontend #1590, [[ADR - 0097 Anggaran Iklan Dashboard Marketing Dibaca dari Master Anggaran Finance]]). Anggaran baru untuk Beauty Hacks dan Kyura, bulan berjalan. Verifikasi PROD belum. |
| 126 | Performa konten & produk | Belum Mulai → **Selesai** | Profit per Produk/SKU, Video, Live, Affiliate. Konten terbatas TikTok karena Shopee/Lazada tak menyediakan data video. |
| 127 | Jadwal Host Live streaming | Belum Mulai → **Selesai** | Pola shift dan penugasan host bergerbang izin ([[ADR - 0072 Kewenangan Jadwal Host Live sebagai Izin yang Ditugaskan]]). Ceklis kesiapan siaran ([[ADR - 0101 Kesiapan Siaran Dicatat Host saat Mulai sebagai Dasar KPI Live Support]]) belum tuntas. Laporan Mingguan Live Support di-revert 2026-09-17 (erp-frontend #1623). |
| 128 | Laba per level (reseller/affiliate tier) | Belum Mulai → **Tidak Relevan** | Salah tafsir. Menunya penelusuran laba toko → produk → SKU → kampanye → iklan → video → live → affiliate. Tier reseller tidak ada di kode ("reseller" nol hit). |
| 129 | Engagement (interaksi customer/sosial media) | Belum Mulai → **Dalam Proses** | Isinya tiket boosting media sosial dari Account Specialist ke tim Engagement ([[ADR - 0058 Tiket Engagement Memakai Koleksi dan State Machine Sendiri]], [[Sales - Engagement Team (Modul)]]), fase B masih dikerjakan. Membalas ulasan atau chat customer belum ada. |
| 130 | ICC & Komplain ke QC | Belum Mulai → **Dalam Proses** | Usul dipecah: ICC Management = Selesai; Komplain ke QC = Revisi (daftar tak disaring per brand, putusan bisa ditimpa, hasil belum dipakai CAPA/KPI, teks belum dua bahasa). |
| 131 | Kamus Metrik | Belum Mulai → **Revisi** | Teks statis 12 entri, terakhir diubah 2026-08-09. Definisi ROAS, Revenue, dan Laba kotor bertentangan dengan backend. Mengikuti Kamus berarti retur terhitung dua kali. |
| 132 | PO Barang Jadi ke gudang/produksi | Belum Mulai → **Dalam Proses** | Kini "MO Barang Jadi", dari SPV Marketing ke PPIC, bukan ke gudang. Alurnya ada, tapi belum ada MO yang diajukan dari layar Marketing di PROD (per komentar kode 2026-09-16). |
| 133 | Semua halaman Marketing punya analisa otomatis | Belum Mulai → **Dalam Proses** | 13 dari 17 halaman analitik punya daftar "Perlu tindakan" berbasis aturan (bukan AI). Belum: Harga & Diskon, Pelanggan & Cohort. Iklan dan Video baru sebagian. |

## Integration (baris 134–142)

| No | Requirement | Checklist → Audit | Temuan utama |
|---|---|---|---|
| 134 | Dashboard integrasi transaksi & Gross Profit | Belum Mulai → **Revisi** | GP jalan untuk Shopee/TikTok/Lazada (HPP dari upload Finance). Tiga masalah: platform "All" di dashboard transaksi diam-diam memakai Shopee (`use-dashboard.ts`), kartu status hanya menghitung order hari ini, dan gerbang akses (§Temuan keamanan). Risiko: jalur laba produk mengelompokkan penjualan per SKU tanpa penjaga SKU kosong, kelas bug yang sama dengan HPP insentif; dampaknya belum diukur. |
| 135 | Order Management lintas marketplace | Belum Mulai → **Revisi** | Cari, filter, detail, ekspor order tiga channel (baca saja; proses order di WMS). Perlu gerbang akses; tanda sinkron Lazada belum ada. |
| 136 | Packet Tracking pengiriman | Belum Mulai → **Revisi** | Ekspor terpotong 10.000 baris tanpa peringatan, golongan masalah hanya mengenali kode TikTok, Lazada tersinkron tapi tak ada di filter. |
| 137 | Ulasan / review produk | Belum Mulai → **Selesai** | Shopee (teks) dan TikTok (sebaran bintang) tampil, dan bisa diteruskan jadi komplain gudang ([[ADR - 0099 Komplain dari Ulasan Marketplace Dirutekan per Departemen lewat Register Komplain yang Ada]]). Balas ulasan belum ada; Lazada belum tercakup. |
| 138 | Teams | Belum Mulai → **Tidak Relevan** | Menu dicabut 2026-09-15 ([[ADR - 0045 Identitas Tim Tunggal dan Peta Kepemilikan Marketing]]). Penggantinya Marketing › ICC Management, tab Kepemilikan Toko. |
| 139 | Inventories (stok lintas channel) | Belum Mulai → **Belum Mulai** | Halaman masih data contoh (`MOCK_INVENTORIES`) sejak Maret 2026, padahal checklist menulis "Sudah ada". Stok nyata (baca saja, dari Accurate) ada di Stok Accurate. Kirim stok ke marketplace belum ada. |
| 140 | Master Data (produk, kategori, listing) | Belum Mulai → **Dalam Proses** | Produk, bundle, harga jual, Mapping SKU, Config Accurate jalan. Master kategori dan manajemen listing marketplace belum ada. |
| 141 | OAuth / koneksi API | Belum Mulai → **Revisi** | Koneksi TikTok Shop/Business, Shopee, Lazada, Meta, Accurate jalan. Wajib perbaikan akses (§Temuan keamanan). Otorisasi app TikTok CS belum punya layar. |
| 142 | Dashboard KPI integrasi + analisa otomatis | Belum Mulai → **Belum Mulai** | Belum ada halaman kesehatan integrasi lintas channel; yang ada status sinkron TikTok dan peringatan Telegram. Data job, webhook, dan order macet sudah ada di backend tanpa layar. Marketplace Log masih data contoh. |

## Temuan keamanan

⛔ **Integration: sejumlah endpoint hanya mensyaratkan login, tanpa gerbang peran.** Cakupannya:
- kredensial koneksi marketplace;
- kendali job sinkron;
- data order, laba, dan ulasan.

**Tingkat:** kritis. **Status per 2026-09-17:** belum diperbaiki. Temuan ini dibuktikan dari penelusuran kode dan belum diuji ke sistem hidup.

Rincian teknis, asal-usul, dan usulan langkahnya ada di **issue privat bip-erp #1941**. Rincian itu sengaja tidak ditulis di sini karena repo vault ini publik. Pola penanganannya mengikuti [[LOG - 2026-07-30 Audit Otorisasi Employee Service]]: rincian baru dicatat di vault sesudah celahnya tertutup.

Sampai issue itu ditutup, **jangan mengandalkan anggapan bahwa seluruh API Integration digerbang peran.**

## Kualitas lintas item

- **Dua bahasa ([[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]]) belum dipenuhi di sebagian besar layar.** Marketing Analytics: 34 dari 104 komponen yang memakai terjemahan. Integration: enam halaman utama menulis teksnya langsung.
- **Definisi ROAS/ROI belum satu.** Dashboard memakai target ROAS 4,5, KPI Leader memakai ROI 3,2, dan basis revenue beda antar channel.

## Menu yang belum ada di checklist

**Marketing:**
- Submenu Analisis: Analisis Live, Analisis Account Specialist, Retur, Pembatalan, Harga & Diskon, Matriks SKU × Toko, Pelanggan & Cohort, Audiens & Wilayah.
- Komplain ke Gudang, Ulasan (entri Marketing), Team Performance, Performa Saya.

**Integration:**
- Harga Jual, Mapping SKU, Config Accurate, Department, Project.
- Kategori Accurate (12 menu).
- Halaman tanpa menu: Marketplace Log (data contoh), Shipment Setting, Auto Approve, Ads Analytics.

## Keputusan yang dibutuhkan dari manajemen

1. Definisi dan target ROAS/ROI.
2. Arti "analisa otomatis": berbasis aturan (sudah ada) atau narasi AI (pekerjaan baru).
3. Apakah tier reseller/affiliate memang dibutuhkan.
4. Balas ulasan dan kirim stok ke marketplace: masuk roadmap atau tetap lewat Seller Center.
5. Laporan Mingguan Live Support yang di-revert 2026-09-17: dilanjutkan atau dibatalkan.

## Dok vault yang tertinggal (untuk `/sync-docs`)

Diperiksa ke kode 2026-09-17:

| Dok | Yang tertulis | Yang ada di `origin/main` |
|---|---|---|
| [[ADR - 0097 Anggaran Iklan Dashboard Marketing Dibaca dari Master Anggaran Finance]] | "belum merge" | Sudah merged, erp-frontend #1590 |
| [[Microservices - Marketing Analytics Service]] §Analisis Account Specialist | "belum PR" | Sudah merged, bip-erp #1865 (2026-09-14) |
| [[Microservices - Integration Service]] §department-shops | `POST /department-shops` digerbang `RequireIntegrationAdmin`, `GET` digerbang `RequireIntegrationStaff` | `POST` = `RequireMarketingLeader`, `GET` = `RequireDepartmentShopsView` |
| [[Microservices - Integration Service]] §Packet Tracking | Menyebut ekspor cepat dan lengkap | Parameter `with_total` tidak ada di kode; ekspor masih terpotong 10.000 baris |
| [[QA - Quality Operasional (CAPA, Incoming, Batch Release)]] §komplain | Aturan "hanya pengaju yang boleh mengubah" tertulis "belum merge" | Sudah ada di `main` |

## Terkait

- [[Microservices - Marketing Analytics Service]] · [[API - Marketing Analytics Service]]
- [[Microservices - Integration Service]] · [[API - Integration Service]] · [[Sales - ICC Affiliate Mapping]]
- [[APP - Web ERP]] · [[IT - Security]] · [[CORE - API Master Gateway]]
- [[LOG - 2026-07-30 Audit Otorisasi Employee Service]] (pola audit keamanan sebelumnya)
