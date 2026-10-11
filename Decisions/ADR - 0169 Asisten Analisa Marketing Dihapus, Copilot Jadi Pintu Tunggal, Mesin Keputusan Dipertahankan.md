# ADR - 0169 Asisten Analisa Marketing Dihapus, Copilot Jadi Pintu Tunggal, Mesin Keputusan Dipertahankan

> **Status**: 🟢 **Diterima**, 2026-10-11, oleh irfanarfianto (diputuskan di sesi analisa 2026-10-11). ⚠️ **Implementasi**: belum dimulai. Pemutus: irfanarfianto. Mencabut [[ADR - 0120 Asisten Analisa Marketing Jadi Menu ERP, Template dan Jadwal Lebih Dulu Tanpa AI]], [[ADR - 0127 Laporan Asisten Analisa Membawa Keputusan AI, Orang Menjalankan atau Menolak]] (kecuali mesin keputusan, lihat §3), [[ADR - 0134 Sajian Laporan Asisten Analisa Berupa Blok Terstruktur, AI Memilih Bentuk, Angka dari Backend]], dan [[ADR - 0139 Penjelasan Tiap Tabel dan Diagram Laporan Ditulis AI, Angkanya Rujukan ke Fakta Backend]].

## Untuk Manajemen

**Yang berubah di layar.** Menu **Asisten Analisis** di Marketing Analytics (`/marketing-analytics/jadwal-laporan`, beserta halaman laporan dan halaman Keputusan AI) dihapus. Laporan mingguan otomatis yang selama ini dikirim ke leader marketing berhenti. Pertanyaan analisa marketing sesudah ini lewat **Copilot**. Kalau ingin diingatkan rutin, pakai jadwal tugas Copilot, yang mengirim pengingat lalu pemakainya bertanya sendiri.

**Siapa yang terdampak.** Penerima laporan terjadwal saat ini: Aris Romadhoni, Maftuhissaiin, Wirawan Widi Atmoko (penerima), serta Irfan Arfianto dan Kukuh Adafi Septya Rizki (penerima bayangan). Mereka perlu diberi tahu **sebelum** pengiriman berhenti.

**Yang tetap ada.** Seluruh halaman analitik Marketing (Ringkasan, Profit, Video, Live, dan lainnya), lencana keputusan per baris (Tambah / Pantau / Cek HPP / Kurangi), blok keputusan per toko, rantai keputusan di Ringkasan, dan blok "Perlu tindakan".

**Yang tidak dijanjikan.** Copilot **tidak** mengirim laporan utuh tanpa pemakainya hadir ([[ADR - 0135 Jadwal Tugas Copilot Mengirim Pengingat, Bukan Menjalankan Tanpa Kehadiran Pemakai]] tidak diubah). Keputusan jalankan/tolak tidak dipindahkan ke Copilot.

**Besaran kerja.** Sedang: dua repo (backend ±60 berkas dihapus, frontend ±59 berkas dihapus), satu pembersihan izin di data produksi yang dijalankan manusia, dan penyesuaian dok vault.

## Deskripsi

*Fitur Asisten Analisa Marketing (jadwal laporan, hasil analisa, sajian blok, lapisan AI, kiriman keputusan + jawaban jalankan/tolak) dihapus dari marketing-analytics dan erp-frontend. Copilot (assistant-service) jadi satu-satunya pintu analisa percakapan. Mesin keputusan berbasis aturan (katalog, kelayakan, jendela matang, orkestrator) dipertahankan tanpa pemakai untuk [[ADR - 0145 Agen Pengelola Toko Tumbuh dari Mesin Keputusan yang Ada, Dampak Diukur Sebelum Eksekusi]]. Koleksi prod diarsip, tidak di-drop.*

- **Path di repo**: `bip-erp/services/marketing-analytics/{jadwal_laporan*,jadwal_jatuh_tempo,penjalan_jadwal,template_analisa*,hasil_analisa*,lingkup_hasil,blok_keputusan,catatan_perkiraan_ringkas,sajian,sajian_fakta,keputusan_ai_*,keputusan_kiriman_*,keputusan_kirim_bayangan,keputusan_riwayat}.go` · `bip-erp/services/marketing-analytics/{routes,main,index}.go` · `bip-erp/shared-library/common/{roles,catalog_marketing}.go` · `bip-erp/shared-library/models/notification/models.go` · `bip-erp/services/notification/webpush.go` · `erp-frontend/src/app/(main)/marketing-analytics/{jadwal-laporan,keputusan}/` · `erp-frontend/src/features/marketing-analytics/components/{hasil-analisa,jadwal-laporan,keputusan}/` · `erp-frontend/src/features/marketing-analytics/components/penanda-keputusan.tsx` · `erp-frontend/src/components/layout/sidebar-menus.tsx`
- **Tanggal**: 2026-10-11

## Context

**Dua fitur menjawab kebutuhan yang tumpang tindih.** Asisten Analisa (ADR 0120/0127/0134) mengirim laporan marketing terjadwal berisi keputusan AI. Copilot ([[ADR - 0132 Asisten AI Tanya-Jawab Lintas Modul, Lapisan Data Bisnis per Service Bukan Terpusat]], ADR 0135) menjawab pertanyaan lintas modul dan punya jadwal tugas sendiri. Tumpang tindihnya ada di dua tempat: dua mekanisme jadwal untuk permintaan yang sama, dan dua pembuat laporan laba (template `ringkasan_laba` di sini, `laba_toko`/`laba_produk` di `services/assistant/internal/alat/laporan_laba.go`), masing-masing dengan aturan sajian sendiri (ADR 0134 vs [[REF - Penyajian Laporan Copilot]]). Lapisan data tidak tumpang tindih: alat marketing Copilot membaca endpoint marketing-analytics.

**Pemakaian terukur nol.** Diukur di prod 2026-10-11 (`marketing_analytics_db`): 4 jadwal aktif (dibuat sejak 2026-09-28), 15 `hasil_analisa`, 5 `keputusan_kiriman` berisi **417** keputusan, **0** jawaban jalankan/tolak. Penjawab keputusan hanya penerima bayangan (IT). Satu kiriman memuat sampai 134 keputusan, 89 di antaranya `hentikan_iklan`, termasuk yang bernilai belasan ribu rupiah. Contoh kiriman 2026-10-05 memakai jendela data 2026-08-18..24.

**Ketergantungan silang diperiksa** (inventaris `origin/main` 2026-10-11). Backend fitur tertutup ke dalam: ia memakai `statusVonis`, `pilihPenggerus`, `rakitLabaHarian`, dan `IndeksPenanggungJawab` milik Beranda, tetapi tidak ada berkas lain yang memanggil balik ke berkas fitur. Copilot tidak memanggil endpoint fitur. Satu-satunya jejaknya komentar di `laporan_laba.go:83` yang merujuk `keputusan_jendela_matang.go:283`, dan nilai ambangnya sudah disalin di sana. Di FE, `PenandaKeputusan` (dipasang di `halaman-beranda.tsx`) **termasuk** fitur, karena memanggil `GET /keputusan-kiriman`. Yang **bukan** fitur dan tetap: `kolom-keputusan.tsx`, `keputusan-toko.ts`, `blok-keputusan-toko.tsx`, `rantai-keputusan.tsx`, `rantai-drill.tsx`, `segmentasi-rugi.ts`.

**Mesin keputusan punya pemakai yang direncanakan.** [[ADR - 0145 Agen Pengelola Toko Tumbuh dari Mesin Keputusan yang Ada, Dampak Diukur Sebelum Eksekusi]] (Agen Pengelola Toko, 🟡 Diusulkan 2026-10-01) dirancang tumbuh dari katalog tindakan, kelayakan, dan orkestrator ADR 0127.

## Decision

1. **Dihapus dari bip-erp (marketing-analytics):** jadwal laporan, penjalan jadwal (goroutine di `main.go`), template analisa, hasil analisa, lingkup hasil, sajian dan sajian fakta, seluruh `keputusan_ai_*`, `keputusan_kiriman_*`, `keputusan_kirim_bayangan`, `keputusan_riwayat`, beserta rute `/template-analisa`, `/jadwal-laporan*`, `/hasil-analisa`, `/keputusan-kiriman*` dan indeks `keputusan_kiriman` di `index.go`. Di shared-library: `RequireMarketingReportAdmin`/`IsMarketingReportAdmin`/`marketingReportAdminChecks`, izin `marketing.jadwal-laporan.manage`, kategori inbox `marketing-laporan-terjadwal`. Env `MARKETING_ANALYTICS_AI_KEPUTUSAN_ENABLED` dan blok `AI_*` di service marketing-analytics dicabut dari compose. Env `AI_*` global tetap (dipakai recruitment), begitu juga `shared-library/ai`.
2. **Dihapus dari erp-frontend:** halaman `/marketing-analytics/jadwal-laporan`, `/jadwal-laporan/laporan`, `/keputusan`; folder komponen `hasil-analisa/`, `jadwal-laporan/`, `keputusan/`; `penanda-keputusan`; hook, lib, dan tipe fitur; menu sidebar "Asisten Analisis"; izin `jadwalLaporan`; isi panduan `asistenAnalisis`; namespace i18n `marketing.jadwalLaporan`, `marketing.hasilAnalisa`, `marketing.keputusan` di **kedua** locale.
3. **Dipertahankan tanpa pemakai, untuk ADR 0145:** `keputusan_katalog.go`, `keputusan_kelayakan.go`, `keputusan_jendela_matang.go`, `keputusan_orkestrator.go` beserta test-nya. Ketiga yang pertama dan orkestrator saat ini merujuk tipe dari berkas kiriman yang dihapus, jadi tipe yang dibutuhkan **dipindahkan**, tidak disalin, ke berkas mesin. Perilaku mesin tidak berubah: test-nya hijau sebelum dan sesudah. Orkestrator tidak lagi memanggil lapisan AI. Bila ia tak bisa berdiri tanpa lapisan AI, orkestrator ikut dihapus dan kekurangannya dicatat di ADR 0145, bukan dipertahankan setengah.
4. **Data prod diarsip, tidak di-drop:** koleksi `jadwal_laporan`, `hasil_analisa`, `keputusan_kiriman` dibiarkan tanpa kode pembaca. Entri izin `marketing.jadwal-laporan.manage` di `position_items[].permission_sets` dibersihkan lewat skrip dry-run/apply yang dijalankan **manusia**.
5. **Urutan deploy, terbalik dari penambahan kontrak:** (1) erp-frontend, supaya layar berhenti memanggil endpoint; (2) marketing-analytics, sehingga pengiriman berhenti; (3) notification-service, untuk mencabut kategori sesudah tidak ada lagi pengirimnya. Pemberitahuan ke penerima laporan dilakukan sebelum langkah 2.
6. **Copilot jadi pintu tunggal analisa percakapan marketing.** Pengingat rutin lewat jadwal tugas Copilot apa adanya (ADR 0135 tetap). Laporan laba hanya punya satu pembuat, yaitu milik Copilot.

## Consequences

- **Leader tak lagi menerima laporan tanpa membuka Copilot.** Diterima sadar: laporan push terukur tidak dipakai, dan ADR 0135 sengaja tidak menjalankan laporan tanpa pemakai hadir.
- **Tak ada lagi jalur di ERP yang mendorong keputusan ke orang.** Lencana per baris tetap memberi vonis, tapi tak ada yang meminta jawaban. Bila kelak dibutuhkan, dirancang ulang di atas Copilot atau di ADR 0145, bukan dihidupkan dari arsip.
- **Kode tanpa pemakai hidup di marketing-analytics** sampai ADR 0145 dibangun atau dibatalkan. Ini utang yang diterima sadar. Bila ADR 0145 dibatalkan, mesin itu dihapus juga. Tiap pemeriksa kode mati (linter `unused`) yang menyala atas berkas mesin itu dibungkam per berkas dengan rujukan ke ADR ini, bukan dengan menghapus mesinnya diam-diam.
- **ADR 0120, 0127, 0134, 0139 berstatus dicabut** (0127 sebagian, untuk mesin keputusannya). Dok perujuk diperbarui lewat `/sync-docs` sesudah penghapusan mendarat di prod.
- **Komentar `laporan_laba.go:83`** di Copilot yang merujuk `keputusan_jendela_matang.go:283` tetap sah, karena berkas itu dipertahankan.
- **Arsip prod bisa di-drop belakangan** tanpa ADR baru, cukup dengan `mongodump` lebih dulu.
