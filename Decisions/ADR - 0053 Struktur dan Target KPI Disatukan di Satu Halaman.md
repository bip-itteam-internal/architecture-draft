## Deskripsi

*Membuat template KPI dan menetapkan targetnya dikerjakan di **satu layar**, bukan dua. Pemisahannya sebelumnya adalah keputusan sadar yang ditulis sebagai komentar di kode, jadi pembalikannya ditulis sebagai ADR supaya tidak dibalik lagi diam-diam.*

- **Status**: ⚠️ **Diputuskan 2026-08-25, kode selesai tetapi BELUM merge dan BELUM deploy.** Branch `feat/kpi-katalog-scope-sumber` (bip-erp) dan `feat/kpi-template-satu-halaman` (erp-frontend).
- **Ruang lingkup**: `kpi_template` di [[Microservices - Employee Service]], halaman `/hris/kpi/templates` dan tab Atur Target di `/hris/kpi` pada [[APP - Web ERP]]. Tidak menyentuh `kpi_score` maupun aturan penilaian.

## Context

Sebuah template KPI punya dua sisi: **strukturnya** (metrik apa saja yang dinilai dan berapa porsi bobot masing-masing) dan **cara menilainya** (sumber data, rumus, cakupan, arah, dan target). Keduanya tersimpan di dokumen yang sama, `kpi_template`, dan disimpan lewat endpoint yang sama, `POST /kpi/templates`.

Di antarmuka keduanya dipisah:

| Sisi | Tempat | Bentuk |
|---|---|---|
| Struktur | `/hris/kpi/templates` | modal `template-form.tsx` |
| Cara menilai | `/hris/kpi` tab Atur Target | `atur-target-inline.tsx` |

Pemisahan itu disengaja dan tertulis di kodenya sendiri (`template-form.tsx`, komentar di kaki kartu metrik): *"Konfigurasi otomasi (sumber/target) kini di TAB ATUR TARGET, bukan di form template — form ini hanya matriks (metrik/porsi)."*

Tiga hal membuatnya tidak bertahan:

1. **Membuat satu template menuntut dua halaman.** Admin mengisi metrik dan porsi di satu layar, lalu harus berpindah untuk mengisi sumber dan target. Tidak ada apa pun di layar pertama yang mengantar ke sana.

2. **Layar kedua menuntut memilih seorang karyawan lebih dulu**, sedangkan template yang baru saja dibuat belum dipegang siapa pun. Langkah berikutnya justru paling sulit dijangkau tepat setelah langkah sebelumnya selesai.

3. **Bobot hidup di dua tempat.** Keduanya menyunting `weight` dan menyimpannya lewat endpoint yang sama, sehingga yang belakangan disimpan menang tanpa ada yang tahu.

Sebuah cacat yang ditemukan saat mengerjakan ini memperkuat keputusannya. `Auto` di `KPIMetric` adalah **pointer** (`nil` berarti metrik manual), dan `ValidateKPIAutoConfig` menolak blok yang ada tetapi tak lengkap. Tab Atur Target selalu mengirim blok `auto` untuk **setiap** metrik, sehingga metrik manual murni memicu tiga penolakan sekaligus (`formula` kosong, `scope` kosong, `target` nol) dan menggagalkan penyimpanan **seluruh** template. Produksi memuat **144 dari 311 metrik** yang manual, jadi ini menyentuh hampir semua template campuran.

## Decision

**1. `/hris/kpi/templates` menjadi satu-satunya tempat menyunting template.** Editornya memuat struktur dan cara menilai dalam satu kartu per metrik, beserta pintu ke target per karyawan dan ke penetapan template.

**2. Editornya inline, bukan modal.** Target per karyawan membuka dialognya sendiri, dan dialog di atas dialog adalah bentuk yang sudah dihindari di tempat lain. Karena alasan yang sama, dialog "Kelola Template" yang dulu dibuka dari Atur Target diganti tautan halaman.

**3. Porsi bobot hanya disunting di editor.** Tab Atur Target tetap menampilkannya supaya penyetel target tahu bobotnya, tetapi tidak lagi bisa mengubahnya. Satu angka, satu tempat.

**4. Tab Atur Target tetap ada**, menyempit ke perannya yang sebenarnya: menyetel target **karyawan tertentu**. Konteks "orang ini" memang milik halaman itu, dan menghapusnya akan memutus alur supervisor yang menyesuaikan target satu orang.

**5. Aturan penyusunan blok `auto` dipusatkan** di satu fungsi murni yang dipakai kedua layar. Metrik tanpa sumber tidak mengirim blok sama sekali, sehingga metrik manual tetap manual bagi backend.

**6. Rumus dan cakupan dijawab BACKEND lewat `GET /kpi/sumber-katalog`, bukan disalin ke frontend.** Katalog bertambah `scope_didukung`, `scope_baku`, `formula_baku`, dan `formula_metrik`. Alasannya sama dengan yang sudah tertulis di `kpi_katalog.go`: daftar yang ditulis ulang di frontend membuat tiap sumber baru menuntut perubahan di dua tempat, dan yang tampak hanyalah pilihan yang hilang.

**7. Nilai rumus yang didaftarkan grounded ke pemakaian nyata**, dari sensus `kpi_template` produksi 2026-08-25 atas 34 metrik ber-`auto`. Sumber yang belum punya bukti pemakaian **dibiarkan kosong**, dan frontend meminta pengisi memilih. Menebak rumus lebih berbahaya daripada mengakui belum tahu: rumus yang salah tidak menimbulkan galat, hanya angka salah yang tampak wajar.

## Consequences

**Yang membaik**

- Membuat template lengkap selesai tanpa berpindah halaman.
- Bobot berhenti punya dua sumber kebenaran.
- Penyimpanan template yang punya metrik manual berhenti gagal 400. Ini perbaikan bug, bukan sekadar penataan ulang.
- Cakupan tak lagi bisa tertinggal kosong: katalog selalu menjawab nilai yang lolos validator, termasuk untuk sumber yang mengabaikan cakupan.

**Yang diterima sebagai konsekuensi**

- **Layar editor jadi padat.** Satu kartu metrik memuat tujuh kendali. Itu harga dari tidak memecahnya ke dua halaman, dan dinilai lebih murah daripada perpindahan halaman yang dulu.
- **Rumus belum lengkap untuk semua sumber.** Sumber tanpa bukti pemakaian menjawab kosong, sehingga di layar Atur Target (yang sengaja tak punya pemilih rumus) sumber semacam itu belum bisa dikonfigurasi. Editor template tidak terdampak karena punya dropdown rumus.
- **Urutan deploy mengikat.** Employee-service wajib naik sebelum frontend, karena kontrak katalog bertambah field. Frontend jatuh ke perilaku lama bila field itu belum ada, dan itu dikunci test.
- **`template-form.tsx` dan `template-mapper.ts` dihapus.** Membiarkannya berarti menyisakan jalan kedua, yang justru hendak dihilangkan.

**Yang sengaja TIDAK diputuskan di sini**

- Apakah `ValidateKPIAutoConfig` sebaiknya melonggarkan `scope` untuk 13 sumber yang tak pernah membacanya. Katalog kini menyatakan mana yang berpengaruh, tetapi validator masih menuntutnya terisi untuk semua.

## Dokumen Terkait

- [[HRIS - Key Performance Index]] — mekanisme template & scoring
- [[HRIS - Otomasi Skor KPI]] — katalog sumber dan konfigurasi otomasi
- [[API - Employee Service]] — kontrak `GET /kpi/sumber-katalog`
- [[ADR - 0048 Skor KPI Otomatis Penuh Dibekukan Sistem]] — pembekuan skor otomatis penuh
- [[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]] — teks editor di dua locale
- [[RUN - Menambah Metrik KPI Otomatis]] — prosedur menambah sumber baru
