# ANALISA - Agen Pengelola Toko

Daftar task hasil `/analisa-kebutuhan` (2026-09-30 sampai 2026-10-01). Keputusan arsitekturnya di
[[ADR - 0145 Agen Pengelola Toko Tumbuh dari Mesin Keputusan yang Ada, Dampak Diukur Sebelum Eksekusi]],
cara kerjanya di [[Sales - Agen Pengelola Toko]]. Baca keduanya dulu sebelum `/start-task` tiap item.
Daftar ini papan kerja, bukan rencana per berkas: path dan fungsi persis tetap digali `/plan` dari kode
saat itu.

Tiap task punya **Tujuan**, **Bergantung**, **Baca dulu** (titik mulai dari grounding 2026-09-30, BUKAN
kebenaran final; verifikasi ulang ke `origin/main`), dan **Kriteria selesai** (bukti konkret).

## Prasyarat: keputusan manusia yang belum ada

- **P1. Manajemen marketing tahu dan setuju pilot, lalu memilih toko pilot (3 sampai 5) dan penyetuju per
  toko.** ADR 0145 mencatat belum ada konfirmasi. T2 boleh dikerjakan dengan data uji, tetapi tidak boleh
  dinyalakan di prod sebelum P1 ada.
- **P2. Aturan insentif dan KPI toko tanpa pemegang manusia** (manajemen marketing + Finance, mengikuti
  [[ADR - 0138 Penugasan Toko Marketplace Bertanggal Berlaku untuk KPI dan Insentif]]). **Bukan** blocker
  tahap 1 (pemetaan pemegang tidak diubah, ADR 0145 §7), tetapi blocker mutlak untuk melepas toko pilot.

## Tahap 1: penasihat toko pilot dengan penilaian dampak

- [ ] **T1. Pastikan mesin keputusan benar-benar mengalir di prod.**
  - **Tujuan**: seluruh tahap 1 berdiri di atas kiriman keputusan; per 2026-09-30 prod baru punya 1 kiriman
    dan 0 jawaban. Tanpa aliran, tak ada yang bisa dinilai.
  - **Bergantung**: tidak ada.
  - **Baca dulu**: [[ADR - 0127 Laporan Asisten Analisa Membawa Keputusan AI, Orang Menjalankan atau Menolak]]
    § Realisasi (butir o: anggaran waktu model, bip-erp #2149); koleksi `keputusan_kiriman`,
    `jadwal_laporan` di `marketing_analytics_db`; saklar `MARKETING_ANALYTICS_AI_KEPUTUSAN_ENABLED`.
  - **Kriteria selesai**: ukuran prod bertanggal: jumlah kiriman per pekan, porsi `status_model=siap`,
    jumlah jawaban. Penyebab bila kiriman tidak bertambah sesuai jadwal ditemukan dan dicatat.

- [ ] **T2. Toko pilot dan penyetuju eksplisit per toko.**
  - **Tujuan**: keputusan untuk toko pilot sampai ke Leader/SPV yang ditunjuk, dan jawabannya tercatat di
    jalur yang sudah ada.
  - **Bergantung**: T1 (aliran kiriman). P1 untuk menyalakan di prod.
  - **Baca dulu**: pola `penerima_bayangan` per jadwal (ADR 0127 § Realisasi butir i); jawaban
    `POST /keputusan-kiriman/:id/jawaban` (`keputusan_kiriman_handler.go`), aturan TOLAK MENANG
    (`statusKeputusanTerakhir`). ⛔ Jangan menurunkan penyetuju dari `RequireMarketingLeader` (meloloskan
    supervisor integration dan staf IT).
  - **Kriteria selesai**: penyetuju yang bukan penyetuju toko itu ditolak menjawab (test HTTP lewat
    `app.Test`); satu keputusan toko pilot dijawab penyetujunya lewat gateway DEV.

- [ ] **T3. Layar penyetuju toko pilot.**
  - **Tujuan**: Leader/SPV menjawab keputusan toko pilotnya tanpa membuka layar lain.
  - **Bergantung**: T2 (kontrak backend). Deploy BE sebelum FE.
  - **Baca dulu**: tab Hasil analisa (erp-frontend #1776/#1778/#1784), `rules/ui-checklist.md`, i18n dua
    bahasa (ADR 0010). Pakai komponen yang ada; jangan merakit tabel sendiri.
  - **Kriteria selesai**: satu perjalanan utuh sebagai penyetuju (buka, baca alasan, jalankan/tolak, lihat
    statusnya berubah), lima keadaan layar, `pnpm tsc/lint/test/build` lokal.

- [ ] **T4. Verifikasi "dijalankan" dari data untuk tindakan iklan.**
  - **Tujuan**: jawaban `jalankan` yang tidak dilakukan di Seller Center tidak terhitung sebagai bukti.
  - **Bergantung**: T2.
  - **Baca dulu**: ADR 0145 §4; kolom `ads_cost` harian per level di mart; `hentikan_iklan`,
    `kurangi_belanja`, `naikkan_belanja` di `keputusan_katalog.go`. ROAS per video tidak andal.
  - **Kriteria selesai**: fungsi murni penentu `terverifikasi` / `tidak_terverifikasi` /
    `tak_bisa_diverifikasi` dengan test kasus tepi (hari tanpa data, belanja nol, arah salah) dan kontrol
    negatif; tindakan di luar tiga itu selalu `tak_bisa_diverifikasi`.

- [ ] **T5. Penilaian dampak keputusan.**
  - **Tujuan**: jantung tahap 1. Tiap keputusan `jalankan` dinilai selisih `laba_matang` 30 hari
    sesudah vs sebelum, dikurangi perubahan toko pembanding.
  - **Bergantung**: T2, T4.
  - **Baca dulu**: ADR 0145 §3; [[Sales - Agen Pengelola Toko]] § Aturan pemakaian angka;
    `keputusan_jendela_matang.go`; `analisis_penanggung_jawab.go` (laba_matang). Definisi toko pembanding
    diputuskan di `/plan` dan ditulis balik ke dok domain.
  - **Kriteria selesai**: status `belum_matang` dan `tak_bisa_dinilai` terbukti bukan nol (test); hasil
    disimpan append-only terpisah dari `keputusan_kiriman`; tidak ada angka proyeksi; job terjadwal
    idempoten; satu penilaian dihitung atas data DEV dan dicocokkan manual ke mart.

- [ ] **T6. Laporan hasil dan hitungan gerbang tahap 2.**
  - **Tujuan**: pemilik produk dan Direktur melihat jenis keputusan mana yang menambah laba, dan sistem
    menghitung sendiri apakah gerbang ADR 0145 §5 (30 keputusan terverifikasi dan matang, 2 jenis
    tindakan, jumlah selisih tidak negatif) sudah terpenuhi.
  - **Bergantung**: T5.
  - **Baca dulu**: daftar penerima eksplisit ([[ADR - 0120 Asisten Analisa Marketing Jadi Menu ERP, Template dan Jadwal Lebih Dulu Tanpa AI]]);
    konvensi bagan (`BaganSkorBulanan`, `ChartContainer`, `--fb-seri-*`) di team-memory.
  - **Kriteria selesai**: angka gerbang ditampilkan apa adanya termasuk yang belum matang; ambang gerbang
    tinggal di satu tempat (bukan disalin ke FE).

- [ ] **T7. Hasil dampak masuk loop belajar langkah 2.**
  - **Tujuan**: keyakinan keputusan berikutnya menyesuaikan dari hasil nyata, bukan hanya frekuensi tolak.
  - **Bergantung**: T5, dan minimal sejumlah penilaian matang (ambangnya diputuskan di `/plan`; di bawah
    ambang tidak mengubah apa pun).
  - **Baca dulu**: `keputusan_riwayat.go` (langkah 1), `keputusan_ai_masukan.go`.
  - **Kriteria selesai**: di bawah ambang, keluaran identik dengan sebelum perubahan (test); di atas ambang,
    perubahan keyakinan tercatat di jejak model.

- [ ] **T8. Verifikasi ujung ke ujung.**
  - **Tujuan**: tahap 1 terbukti bisa dipakai, bukan cuma merged.
  - **Bergantung**: T1 sampai T6.
  - **Kriteria selesai**: di DEV lewat gateway: kiriman toko pilot terbit, penyetuju menjawab, verifikasi
    dan penilaian terhitung (dengan tanggal buatan), laporan menampilkan hasil dan gerbang.

## Paralel, boleh mulai sekarang

- [ ] **T9. Cek izin scope API tulis TikTok Shop dan Shopee.** Tujuan: lead time izin marketplace tidak
  menahan tahap 2. Kriteria: daftar scope yang dibutuhkan per tindakan (balas ulasan, promo, budget iklan),
  status aplikasi kita, dan perkiraan waktu persetujuan, bertanggal.
- [ ] **T10. Ukur pekerjaan Account Specialist.** Tujuan: tahu apa yang sebenarnya akan diganti. Kriteria:
  survei atau wawancara minimal 5 orang, porsi waktu per jenis pekerjaan termasuk pembuatan video AI.

## Tahap 2 (hanya sesudah gerbang ADR 0145 §5 terpenuhi)

- [ ] **T11. ADR eksekusi tindakan pertama** (usulan: balas ulasan), menggantikan ADR 0127 §2 khusus
  tindakan itu, dengan eksekusi saat disetujui memakai identitas penyetuju. Bergantung: T6 (gerbang), T9.

## Terpisah, diputuskan saat dibutuhkan

- [ ] **T12. Keputusan ADR 0138 dan aturan insentif toko pilot** (P2). Pemilik: manajemen marketing +
  Finance; IT menyiapkan dampak angka per opsi.
- [ ] **T13. Jalur baca pengetahuan kurasi manusia (vault privat) dari server.**
- [ ] **T14. Ideamills menyimpan id video marketplace hasil unggahan**, supaya pembuatan video bisa
  disambung ke `tt_shop_video_performances`.
