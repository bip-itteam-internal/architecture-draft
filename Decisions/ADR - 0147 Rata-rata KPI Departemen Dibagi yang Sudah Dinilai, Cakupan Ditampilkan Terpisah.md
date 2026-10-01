# ADR - 0147 Rata-rata KPI Departemen Dibagi yang Sudah Dinilai, Cakupan Ditampilkan Terpisah

## Deskripsi

*Rata-rata KPI sebuah departemen (kartu departemen `/portal/kpi`, garis trennya, dan grafik "Rata-rata KPI per bulan") dihitung atas orang yang **sudah punya skor** saja, bukan atas seluruh karyawan aktif. Cakupan penilaian ("X orang · Y dinilai · Z belum dinilai") tetap tampil, sebagai angka terpisah. Membalik keputusan product owner 2026-08-28 yang tercatat di [[HRIS - Key Performance Index]] § aturan kartu ringkasan nomor 1.*

- **Status**: 🟡 Diusulkan (2026-10-01). Belum ada kode.
- **Path di repo**:
  - bip-erp `services/employee/kpi_ringkasan_departemen.go` (`ringkasDepartemen`, pembagi `RataRata`), `kpi_ringkasan_departemen_test.go`
  - erp-frontend `src/features/hris/kpi/lib/tren-kpi.ts` (`rataRataAtasTotal`), pemakainya (`dashboard/lib/kpi-hrga/deret-skor.ts`, tile rata-rata di `blueprint/kpi-blueprint-view.tsx`, `rata-rata-perusahaan-section.tsx`), teks `statRataBasis` dan `sectionCatatan` di `src/i18n/locales/id.ts` + `en.ts`
- **Tanggal**: 2026-10-01
- **Terkait**: [[HRIS - Key Performance Index]] · [[HRIS - Otomasi Skor KPI]] · [[API - Employee Service]] · [[APP - Web ERP]]

## Untuk Manajemen

**Apa yang berubah di layar.** Angka besar di kartu tiap departemen menjadi rata-rata skor orang yang **sudah dinilai**. Contoh Agustus 2026: Procurement (3 orang, baru 1 dinilai dengan skor sekitar 96) selama ini tampil **31,4 merah**; sesudah perubahan tampil **sekitar 96**, dengan keterangan "1 dinilai · 2 belum dinilai" tetap di bawahnya. Garis tren di kartu dan grafik "Rata-rata KPI per bulan" memakai aturan yang sama, sehingga angkanya cocok dengan rekap per departemen yang dihitung langsung dari skor tersimpan.

**Siapa yang terdampak.** Semua pembaca halaman KPI (HR, supervisor, direksi). Skor perorangan tidak berubah sama sekali.

**Yang tidak dijanjikan.**
- Dorongan untuk menyelesaikan penilaian kini datang dari keterangan cakupan, bukan dari angka rata-rata yang anjlok. Departemen yang baru menilai sedikit orang bisa tampil tinggi; pembacanya wajib melihat baris "belum dinilai".
- Skor tiap orang di bulan berjalan tetap **mentah** (metrik yang belum terisi dihitung 0, aturan nomor 2), tidak diubah oleh ADR ini.
- Lambatnya pemuatan kartu untuk bulan lampau adalah masalah terpisah, tidak diselesaikan di sini.

**Perkiraan besaran kerja.** Kecil: satu baris aturan di backend, satu fungsi dan beberapa teks di web, beserta test-nya. Sekitar satu hari kerja termasuk verifikasi.

## Context

Pemicu 2026-10-01: rekap rata-rata KPI per departemen enam bulan (April sampai September 2026) yang dihitung langsung dari `employee_db.kpi_score` prod, dengan pembagi = jumlah skor tersimpan, berbeda jauh dari kartu `/portal/kpi`. Contoh: Procurement Agustus 96,0 lawan 31,4; Beauty Hacks September sekitar 45 lawan 21,4 (42 orang, 18 terhitung). Sesudah membandingkan kedua rumus, user (panpan) meminta rumus rekap itu dipakai di halaman, dan menyatakan product owner sudah menyetujuinya (2026-10-01).

Diukur di kode (`origin/main` 2026-10-01):

1. **Backend** `ringkasDepartemen` menghitung `rata := a.jumlahSkor / float64(a.total)` (`kpi_ringkasan_departemen.go`), dengan komentar "KEPUTUSAN DIBALIK 2026-08-28 ... Product owner menolaknya ... pembaginya wajib TOTAL AKTIF". `KelengkapanPct` sudah dibagi `a.dinilai`.
2. **Frontend** mengulang aturan yang sama secara terpisah: `rataRataAtasTotal` (`tren-kpi.ts`) mengalikan `average_score` milik `GET /kpi` (yang sudah dibagi yang dinilai) dengan `scored / total`, dipakai grafik "Rata-rata KPI per bulan" dan dashboard KPI HRGA.
3. **Bulan lampau di garis tren** dihitung `denganOtomasi=false`, sehingga hanya pemilik `kpi_score` yang berskor ([[HRIS - Key Performance Index]] aturan nomor 3). Dengan pembagi total, titik itu tergantung berapa yang kebetulan sudah dibekukan; dengan pembagi yang dinilai, titik itu menjadi rata-rata skor tersimpan, sama dengan rekap langsung dari DB.

## Decision

1. **Pembagi rata-rata departemen = jumlah orang yang punya skor** (`a.dinilai` di backend, `scored` di frontend). Orang yang belum dinilai tidak ikut pembilang maupun pembagi.
2. **Cakupan tetap tampil sebagai angka terpisah** dari payload yang sudah ada (`total_karyawan`, `dinilai`, `belum_dinilai`, `kelengkapan_pct`). Tidak ada field baru.
3. **Satu aturan untuk semua permukaan rata-rata departemen**: kartu departemen, garis trennya, grafik "Rata-rata KPI per bulan", dan dashboard KPI HRGA. Bila ada satu permukaan yang tetap memakai pembagi total, satu bulan akan punya dua angka di dua layar, yaitu kegagalan yang hendak dihilangkan ADR ini.
4. **Teks layar yang menyebut pembagi ikut dikoreksi** di `id.ts` dan `en.ts` (mis. `statRataBasis` "dibagi {{n}} anggota", `sectionCatatan` "Departemen yang belum ada nilainya dihitung 0"), supaya keterangan tidak berbohong tentang rumusnya.
5. **Bulan tanpa satu pun skor tetap `null`** (jeda di grafik), bukan 0.

## Consequences

- ✅ Angka kartu bisa dibaca sebagai kinerja, dan cocok dengan rekap yang dihitung dari `kpi_score`.
- ✅ Titik tren bulan lampau tidak lagi turun-naik hanya karena berapa orang yang sudah dibekukan.
- ⚠️ Departemen dengan cakupan rendah bisa tampil tinggi berdasarkan segelintir orang. Itu ongkos yang diterima; cakupan dibaca dari keterangan di bawah angka.
- ⚠️ Komentar kode dan dok vault yang menjelaskan keputusan 2026-08-28 wajib diperbarui bersama, kalau tidak pembaca berikutnya akan "memperbaiki" kodenya kembali ke pembagi total.

## Alternatives Considered

- **Tetap pembagi total aktif** (keputusan 2026-08-28): ditolak karena satu angka memuat kinerja dan cakupan sekaligus, dan terbaca sebagai kinerja buruk (Procurement 31,4 merah untuk kinerja sekitar 96).
- **Dua angka besar (kinerja dan "rata-rata atas seluruh anggota")**: tidak dipilih; cakupan sudah tampil sebagai hitungan orang, angka kedua hanya menambah beban baca.
