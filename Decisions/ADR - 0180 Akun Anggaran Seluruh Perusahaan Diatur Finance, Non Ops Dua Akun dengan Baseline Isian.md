# ADR - 0180 Akun Anggaran Seluruh Perusahaan Diatur Finance, Non Ops Dua Akun dengan Baseline Isian

> **Status**: 🟢 Diterima, 2026-10-15, oleh Azzerith. Keputusan diambil dalam sesi lewat pilihan ganda atas permintaan Cost Control 2026-10-15 (chat). **Direvisi 2026-10-15 (siang)** atas jawaban Finance: butir 5–6 diubah, butir 8 ditambah. Kode: bip-erp#3162, #3166, erp-frontend#2484, #2485 (PR terbuka), dengan revisi menyusul.

## Untuk Manajemen

**Apa yang berubah di layar.**
- **Akun Seluruh perusahaan.** Sejumlah akun beban, seperti pelatihan, maintenance, perizinan, uji lab, dan semua penyusutan, dianggarkan **untuk seluruh perusahaan**, bukan per divisi. Untuk akun-akun ini, tabel Serapan menampilkan realisasi **total perusahaan** dalam satu baris "Seluruh perusahaan", tidak dipecah per divisi. Daftar akunnya **diatur Finance sendiri** dari layar Anggaran.
- **Laporan Non Ops.** Laporan "Admin & Non-Ops" berganti nama menjadi **"Non Ops"** dan tinggal dua akun: Beban Iuran & Sumbangan, dan Beban Entertainment Adum. **Beban Bank pindah ke OPEX.**
  - Kolom Realisasi di kiri, Baseline di kanan.
  - Baseline **diisi Finance**. Kalau belum diisi, laporan dan KPI bulan itu berbunyi "baseline belum diisi". Angka tahun lalu × 1,25 hanya ditampilkan sebagai acuan.
  - Persentase dihitung (Realisasi − Baseline) ÷ Baseline, sehingga **minus berarti turun**, di layar dan di KPI.
- **Rekomendasi untuk anggaran gabungan.** Anggaran gabungan yang lewat bisa diberi satu rekomendasi untuk seluruh pagunya, tidak hanya per akun anggota.

**Siapa yang terdampak.** Cost Control (mengisi daftar akun, anggaran seluruh perusahaan, dan baseline Non Ops) dan pemegang KPI Cost Control.

**Apa yang TIDAK dijanjikan.**
- KPI Cost Control #2 baru memakai rumus baru setelah HRD mengganti template KPI-nya ke metrik bertanda baru. Sebelum itu, skor tetap memakai metrik lama, dan skor yang sudah dibekukan tidak dihitung ulang.
- Angka KPI #2 **berubah isinya**, karena Beban Bank tidak lagi dihitung.
- Akun seluruh perusahaan tidak bisa sekaligus dianggarkan per divisi, dan tidak bisa menjadi anggota anggaran gabungan.

**Perkiraan besaran kerja.** Empat PR, BE lebih dulu: (1) akun seluruh perusahaan di backend, (2) layarnya, (3) Non Ops di backend, (4) layarnya. Ditambah revisi Non Ops (baseline tanpa angka otomatis, metrik KPI bertanda) di PR yang sama, dan PR baru untuk rekomendasi anggaran gabungan.

## Deskripsi

*Merevisi sebagian [[ADR - 0178 Serapan Anggaran per Departemen Jurnal, Seluruh Perusahaan Dihapus, Pagu Gabungan per Departemen]] butir 1–2: departemen kosong ("Seluruh perusahaan") kembali sah, tetapi **hanya** untuk akun yang Finance masukkan ke daftar akun seluruh perusahaan. Menetapkan populasi laporan Non Ops (dua akun), baseline isian Finance yang menggantikan baseline otomatis, dan tanda persentase di layar.*

- **Status**: 🟢 Diterima 2026-10-15 (Azzerith), kode belum ada
- **Path di repo** (rencana):
  - `bip-erp/services/integration/internal/domain/entity/anggaran.go`, `usecase/anggaran_varians.go`, `interface/http/anggaran_handler.go`, `usecase/anggaran_xlsx.go`, `usecase/anggaran_pagu.go`
  - `bip-erp/services/integration/internal/usecase/admin_nonops_daftar.go`, `usecase/opex_daftar.go`, `domain/entity/admin_nonops.go`, `interface/http/admin_nonops_handler.go`
  - `bip-erp/services/employee/kpi_sumber_admin_nonops.go` (teks catatan saja)
  - `erp-frontend/src/features/finance/anggaran/` (Serapan, Anggaran Bulanan, panel Non Ops)
- **Tanggal**: 2026-10-15

## Context

**Permintaan Cost Control 2026-10-15** (chat):
1. Realisasi sudah dibedakan per tag divisi, tetapi ada beban yang di laba-rugi dibebankan ke masing-masing divisi, sedangkan di laporan anggaran nyatanya untuk seluruh perusahaan. Untuk beban ini, realisasi cukup ditampilkan sebagai total seluruh perusahaan. Daftarnya 13 akun:
   - 6206 Beban Pelatihan Karyawan
   - 6214 Beban Maintenance & Instalasi Adum
   - 6219 Beban Registrasi, Administrasi, & Perizinan
   - 6220 Biaya Uji Lab
   - 7109 Beban Penyusutan Aset Lainnya
   - 7110 Beban Penyusutan Gd Kantor Baru 2 Lt
   - 7107 Beban Penyusutan Gd Kantor Lt Ke-3
   - 7101 Beban Penyusutan Gedung Kantor
   - 7106 Beban Penyusutan Gerbang Utama
   - 7104 Beban Penyusutan Kendaraan Kantor
   - 7103 Beban Penyusutan Mesin Kantor
   - 7105 Beban Penyusutan Peralatan Gudang
   - 7102 Beban Penyusutan Peralatan Kantor
2. Laporan Admin & Non-Ops diganti menjadi "Non Ops". Beban Bank dipindah ke komponen OPEX (bukan non-ops, berdasarkan rekomendasi Pak Endri), sehingga non-ops tinggal 2 akun. Revisi yang diminta:
   - Realisasi di kiri, Baseline di kanan.
   - Baseline bisa diedit.
   - Rumus penurunan = (Realisasi − Baseline) ÷ Baseline.

**Keputusan dalam sesi 2026-10-15 (Azzerith):**
- Daftar akun seluruh perusahaan **diatur Finance di layar**, bukan ditulis di kode.
- Dua hal lain dibiarkan "tanpa preferensi", sehingga diambil usulan bawaan:
  - baseline kosong jatuh ke YoY × 1,25;
  - tanda rumus dibalik di layar saja.

**Keadaan kode** (`bip-erp` origin/main 2026-10-15, sesudah bip-erp#3108 dan #3123 merged):
- **Anggaran.** Departemen kosong ditolak di form dan upload (ADR 0178, bip-erp#3108). `/anggaran/varians` tidak mengeluarkan baris `""`; realisasi tanpa tag keluar sebagai "Tanpa departemen".
- **Pagu gabungan.** Ada per departemen (bip-erp#3123), dan satu akun hanya boleh berada di satu pagu atau punya anggaran per akun.
- **Populasi Non Ops.** `usecase/admin_nonops_daftar.go:33` `DaftarAkunAdminNonOps` = Beban Iuran & Sumbangan, Beban Bank, Beban Entertainment Adum. Ada test `TestAkunAdminNonOpsTidakAdaDiDaftarOpex` yang menjaga agar daftar ini tidak beririsan dengan daftar OPEX (`usecase/opex_daftar.go`).
- **Rumus penurunan.** `entity/admin_nonops.go:61` `PenurunanYoY` = (baseline − realisasi) ÷ baseline, dan nilai negatif dipotong ke 0. Komentar `:75-82` mencatat bahwa sheet Finance tidak konsisten antara baris akun dan baris total, lalu memilih konvensi baris TOTAL (positif = turun).
- **Pemakai KPI.** `services/employee/kpi_sumber_admin_nonops.go` memasok KPI Cost Control #2 (`penurunan_yoy_persen`) dan sebuah metrik rasio. Teks catatannya menyebut "×1,25".

**Jawaban Finance 2026-10-15 (siang), atas pertanyaan dalam sesi:**
1. Baseline Non Ops: kosong sampai diisi (butir 5 direvisi).
2. KPI juga disesuaikan; Finance sudah berkoordinasi dengan HRD untuk mengubah penilaian KPI-nya (butir 6 direvisi).
3. Anggaran Beban Bank masuk Seluruh perusahaan. Ini data, cukup lewat daftar akun Seluruh perusahaan, tanpa kode.
4. Urutan 15 baris awal Serapan menurut nomor COA sudah sesuai.
5. Perlu satu rekomendasi untuk anggaran gabungan secara keseluruhan (butir 8).
6. Anggaran akan di-input ulang semua (termasuk memindahkan Rp45 juta dari akun 6111 ke anggaran gabungan).
- Data acuan yang sedang diubah Finance adalah **September 2026**, bulan yang pengeluarannya sudah lengkap. Verifikasi memakai periode itu.
## Decision

1. **Daftar akun seluruh perusahaan** (entitas baru di integration-service, diatur Finance).
   - Isinya nomor akun beserta namanya dari katalog Accurate, dan bersifat global (tidak per bulan).
   - Rute tulis memakai gerbang kelola anggaran; rute baca memakai gerbang akuntansi.
   - Daftar awal diisi Finance lewat layar dengan 13 akun di Context. Daftarnya **tidak ditanam** di kode maupun seed.
2. **Anggaran akun seluruh perusahaan.**
   - Untuk akun di daftar, anggaran diisi dengan departemen kosong ("Seluruh perusahaan"), dan **hanya** itu. Anggaran per departemen untuk akun tersebut ditolak, dan form/upload menyebut alasannya.
   - Untuk akun di luar daftar, ADR 0178 butir 1 tetap berlaku: departemen wajib.
   - Akun di daftar tidak boleh menjadi anggota pagu gabungan, ke arah mana pun.
   - Baris anggaran yang tidak sesuai dengan status akunnya saat dibaca, misalnya akun dikeluarkan dari daftar padahal masih punya anggaran `""`, **bukan pos**. Baris itu dilaporkan terpisah, tidak dibuang diam-diam (pola `anggaran_bentrok_pagu`).
3. **Varians akun seluruh perusahaan.**
   - Akun di daftar keluar sebagai **satu** baris berdepartemen `""` (`seluruh_perusahaan: true`), dengan realisasi = total perusahaan akun itu: semua departemen ditambah yang tanpa tag.
   - Pecahan per departemen dan "Tanpa departemen" untuk akun itu **tidak** keluar, sehingga realisasinya terhitung tepat sekali di `ringkas` dan KPI.
   - Akun di luar daftar tidak berubah.
4. **Populasi Non Ops = dua akun:** Beban Iuran & Sumbangan dan Beban Entertainment Adum. Beban Bank pindah ke daftar OPEX. Pagar "tidak beririsan" tetap berlaku.
5. **Baseline Non Ops diisi Finance**, per akun per bulan. *(Direvisi 2026-10-15 atas jawaban Finance: "kosong sampai diisi".)*
   - **Hanya angka isian yang menjadi baseline.** Bila kosong, baris itu berstatus "baseline belum diisi", dan total serta KPI bulan itu tidak terdefinisi. Hasilnya **bukan** 0% dan bukan galat diam.
   - Baseline otomatis (bulan yang sama tahun lalu × 1,25) **tidak** lagi dipakai untuk menghitung apa pun. Angkanya boleh tetap dikirim sebagai **acuan** untuk membantu Finance mengisi.
   - KPI #2 memakai baseline isian yang sama, dari satu sumber, yaitu respons integration.
6. **Tanda persentase = (Realisasi − Baseline) ÷ Baseline × 100, di layar DAN di KPI.** *(Direvisi 2026-10-15: Finance meminta KPI ikut disesuaikan, dan HRD sudah berkoordinasi untuk mengubah penilaian KPI-nya.)*
   - Di layar Non Ops, hitungannya ada di **satu** fungsi FE, sama seperti Varians Serapan (ADR 0178 butir 4). Negatif berarti turun.
   - Untuk KPI, sumber KPI menyediakan metrik **bertanda baru**, `perubahan_yoy_persen` = (Realisasi − Baseline) ÷ Baseline × 100, dengan arah "lebih kecil lebih baik". HRD mengganti template KPI Cost Control #2 ke metrik ini, dengan ambang "≤ −2%".
   - Metrik lama `penurunan_yoy_persen` (positif = turun) **tidak dihapus dan tidak dibalik**. Skor yang sudah dibekukan tetap bisa dibaca, dan template yang belum diganti tidak tiba-tiba terbalik. Selama template belum diganti HRD, skor KPI tetap memakai metrik lama.
   - Field backend `penurunan_persen` tidak dibalik. Sebagai gantinya ditambahkan field bertanda `perubahan_persen`.
7. **Nama laporan** di layar menjadi "Non Ops". Kontrak endpoint `admin-nonops` tidak diganti nama.
8. **Rekomendasi untuk anggaran gabungan.** *(Ditambah 2026-10-15 atas jawaban Finance.)* Cost Control bisa membuat **satu** rekomendasi untuk pagu gabungan secara keseluruhan, dari baris pagu di Serapan, dari peringatan pos lewat anggaran, dan dari kartu tindak lanjut Cost Control. Rekomendasi per akun anggota tetap bisa dibuat. Rekomendasi pagu merujuk `pagu_id` (id hulu), bukan menyalin nama pagu saja.

## Consequences

- **KPI Cost Control #2** berubah isinya, karena populasinya tinggal dua akun, tetapi tidak berubah arah. Skor bulan yang belum dibekukan (dibekukan tanggal 5 bulan berikutnya) akan dihitung dengan populasi baru.
- **Beban Bank kini butuh anggaran OPEX.** Finance perlu memasukkannya ke RAPB. Selama belum, barisnya berbunyi "anggaran belum diisi" di Serapan.
- **Satu konsep, dua tanda** (`penurunan_persen` backend positif = turun, layar negatif = turun). Penjaganya: tanda layar dihitung di satu fungsi, dan dok [[Finance - Serapan Anggaran dan Cost Control]] menyebut keduanya.
- **Daftar akun seluruh perusahaan adalah data.** Kalau Finance lupa mengisinya sesudah deploy, akun-akun itu kembali diperlakukan per divisi, dan anggaran `""`-nya ditolak. Urutan deploy: BE naik, Finance mengisi daftar, baru unggah anggaran.
- **Akun penyusutan (71xx)** belum diperiksa: apakah ada di katalog OPEX dan apakah ikut populasi refresh realisasi. Task BE wajib memastikan realisasi total perusahaan akun di daftar memang ditarik.

## Dokumen Terkait

- [[ADR - 0178 Serapan Anggaran per Departemen Jurnal, Seluruh Perusahaan Dihapus, Pagu Gabungan per Departemen]]
- [[Finance - Serapan Anggaran dan Cost Control]]
- [[HRIS - Otomasi Skor KPI]]
- [[API - Integration Service]]
