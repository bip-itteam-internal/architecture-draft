# ADR - 0153 KPI Bulan Lampau yang Belum Dinilai Tampil sebagai Pratinjau di MyBharata, Bukan Layar Kosong

> **Status**: 🟢 **Diterima**, 2026-10-04, oleh pengguna Tech Development dalam sesi kerja, nol kode. Nomor 0153 diklaim saat push; bila sudah terpakai, geser ke nomor bebas berikutnya.

%% Vault ini PUBLIK. Nama orang dan employee_id tidak ditulis; yang disebut hanya angka agregat, departemen, dan posisi. %%

## Untuk Manajemen

**Masalahnya.** Karyawan yang membuka KPI bulan lalu di MyBharata melihat layar kosong bertuliskan "Skor KPI Belum Tersedia" selama atasannya atau otomasi belum menyimpan skor bulan itu. Diukur di produksi 2026-10-04 untuk Agustus 2026: dari 184 akun aktif, 62 orang tidak bisa melihat KPI Agustus, dan 52 di antaranya seharusnya punya nilai. Angka yang sebenarnya sudah dihitung sistem tidak terlihat oleh orang yang dinilai.

**Yang diputuskan.** Bulan lampau yang belum punya skor tersimpan ditampilkan sebagai **pratinjau berpenanda "belum dinilai"**, sama seperti bulan berjalan. Skor final tetap hanya lahir dari penilai atau finalisasi otomatis; pratinjau tidak menggantikannya.

## Deskripsi

*MyBharata memakai jalur pratinjau yang sudah ada (`GET /me/kpi-score?preview=true`) juga untuk bulan lampau yang belum dinilai, bukan hanya bulan berjalan. Backend tidak berubah.*

- **Tanggal**: 2026-10-04
- **Diukur ke**: bip-erp `origin/main` (`services/employee/kpi_me_pratinjau.go`), mybharata-app `origin/dev` (`lib/src/features/kpi/`), data PROD baca-saja 2026-10-04.
- **Hubungan dengan dok lain**:
  - [[ADR - 0048 Skor KPI Otomatis Penuh Dibekukan Sistem]]: skor final tetap lahir dari finalisasi atau penilai; ADR ini hanya soal yang ditampilkan sebelum itu.
  - [[HRIS - Otomasi Skor KPI]] · [[APP - MyBharata]]

## Context

**Mekanisme yang ada (terverifikasi di kode).**

- `GET /me/kpi-score?period=` (`HandlerKPISaya`) mengirim snapshot `kpi_score` bila ada. Bila tidak ada, ia membalas **404**, kecuali `preview=true`, yang menghitung pratinjau dari template posisi orang itu (`pratinjauKPISaya`) dan membalas `dinilai: false` beserta `metrik[]` dan `menunggu[]`. Pratinjau menerima **periode apa pun**, bukan hanya bulan berjalan.
- Pratinjau sengaja **opt-in** lewat parameter: aplikasi lama mengurai respons tanpa `preview` sebagai `KpiModel`, yang mewajibkan field `template`. Mengirim pratinjau tanpa diminta akan membuat aplikasi yang sudah terpasang gagal mengurai. Karena itu perubahannya di aplikasi, bukan di backend.
- MyBharata (`kpi_page.dart`): bulan berjalan memanggil pratinjau (`LoadKpiProgres`), bulan lampau memanggil skor (`LoadKpiScore`). Balasan 404 dipetakan ke `NoRecordFailure(errorKpiNotFound)` dan layar menampilkan "Skor KPI Belum Tersedia".
- Finalisasi otomatis hanya membekukan karyawan yang **seluruh** metriknya otomatis, dan hanya untuk bulan sebelumnya; selebihnya menunggu penilai menekan Simpan.

**Keadaan PROD Agustus 2026 (diukur 2026-10-04).** 62 orang tanpa skor Agustus: 26 metriknya otomatis penuh tapi belum dibekukan, 13 punya metrik manual yang belum dinilai, 13 posisinya belum punya template KPI, 10 wajar (masuk setelah Agustus, atau posisi tanpa KPI).

## Decision

1. **Bulan lampau tanpa skor tersimpan → pratinjau.** Bila `GET /me/kpi-score?period=<bulan lampau>` membalas 404, MyBharata meminta ulang dengan `preview=true` dan menampilkan hasilnya dengan tampilan dan penanda "belum dinilai" yang sudah dipakai bulan berjalan. Metrik manual tampil sebagai menunggu penilaian.
2. **Posisi tanpa template KPI** (pratinjau juga 404) menampilkan pesan yang menyebut sebabnya, bukan pesan generik "Skor KPI Belum Tersedia".
3. **Skor final tidak berubah sumbernya.** Begitu skor tersimpan, bulan itu kembali menampilkan skor final seperti sekarang.
4. **Backend tidak diubah**, demi aplikasi lama yang sudah terpasang.

## Consequences

- Karyawan dapat melihat angka bulan lalu yang belum final, yang bisa berubah saat penilai menyimpan. Penanda "belum dinilai" yang sudah dikenal dari bulan berjalan menjadi pembedanya.
- Perlu rilis aplikasi lewat store; karyawan melihatnya setelah memperbarui.
- Tidak mengurangi pekerjaan penilai dan HR: skor Agustus tetap perlu difinalisasi atau dinilai, dan posisi tanpa template tetap butuh template.

## Dokumen Terkait

- [[ADR - 0048 Skor KPI Otomatis Penuh Dibekukan Sistem]]
- [[HRIS - Otomasi Skor KPI]]
- [[APP - MyBharata]]
