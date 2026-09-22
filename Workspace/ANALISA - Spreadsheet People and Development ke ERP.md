---
publish: false
---
# ANALISA — Spreadsheet People & Development ke ERP

Daftar task hasil `/analisa-kebutuhan` (2026-09-21) atas permintaan memindahkan 25 sheet Dashboard People & Development ke ERP. Keputusan: [[ADR - 0115 Spreadsheet People and Development Belum Dipindah ke ERP, KPI Ganda Diselesaikan Lebih Dulu]]. Peta keadaannya: [[REF - Peta Spreadsheet People and Development ke ERP]]. Papan kerja, berubah tiap item selesai; bukan arsitektur, bukan rencana per berkas.

⛔ **Daftar ini SENGAJA pendek.** Empat modul yang diminta (KPK, talent 9-box beserta talent pool, TNA, program pengembangan) **tidak** ada di sini karena diputuskan ditunda, bukan karena terlewat. Yang tersisa hanya satu pekerjaan nyata dan beberapa pengisian data, sebab itulah yang benar-benar memburuk bila didiamkan.

## Fase 0 — Menghentikan KPI ganda

- [ ] **T1. Bandingkan nilai KPI spreadsheet dengan ERP untuk periode yang sama.** Ambil April sampai Agustus 2026, yang dimiliki KEDUA sumber, lalu cocokkan per karyawan memakai `employee_id`. Keluarannya satu tabel selisih: berapa orang cocok, berapa berbeda, berapa yang hanya ada di satu sisi. ⛔ **Jangan berhenti di jumlah baris.** Dua sumber bisa sama-sama berisi 150 orang dan tetap berbeda isinya; yang dicari selisih NILAI per orang per bulan. ⚠️ Cakupan sudah diketahui berbeda sebelum dibandingkan: ERP tak punya Januari dan Februari, dan Maret hanya 1 orang. Dependensi: tidak ada. **Ini task pertama.**
- [ ] **T2. Pemilik proses memutuskan sumber tunggal KPI.** Sesudah selisih T1 terlihat. Yang diputuskan: sisi mana yang menang, apa yang dilakukan pada periode yang hanya dimiliki satu sisi, dan sejak kapan sisi yang kalah berhenti diisi. Keputusannya masuk ke ADR 0115 sebagai pembaruan, bukan jadi ADR baru. Dependensi: T1.
- [ ] **T3. Bila ERP yang menang: lengkapi periode yang belum ada di ERP.** Januari sampai Maret 2026. Ini pengisian data oleh HR, bukan kode. Dependensi: T2.

## Fase 1 — Mengisi modul yang sudah terpasang

- [ ] **T4. Isi peserta dan kehadiran kelas pelatihan yang sudah tercatat.** Prod 2026-09-21: 13 kelas dengan **4 baris peserta**. Alatnya sudah live termasuk penugasan beberapa orang sekaligus. ⚠️ Ini task yang sama dengan T19 di [[ANALISA - Penyelenggara dan Bank Sertifikat Pelatihan]]; jangan dikerjakan dua kali, rujuk ke sana. Dependensi: tidak ada.
- [ ] **T5. Ukur ulang sesudah T4.** Sertifikat dan evaluasi trainer harus bergerak dari nol untuk kelas tanpa materi yang kehadirannya ditandai. Kalau tidak bergerak, barulah curigai rantainya putus. Dependensi: T4.

## Fase 2 — Menutup pertanyaan terbuka, tanpa membangun apa pun

- [ ] **T6. Konfirmasi sumber skor kedisiplinan dan bobot talent pool.** Bobot 70/15/15 baru disimpulkan dari judul kolom, dan sumber skor disiplin baru diasumsikan dari kehadiran ERP. Keduanya cukup satu percakapan dengan pemilik proses, dan hasilnya ditulis ke [[REF - Peta Spreadsheet People and Development ke ERP]]. Tanpa ini, talent pool kelak dibangun di atas tebakan. Dependensi: tidak ada.
- [ ] **T7. Catat jalur KPI menuju surat peringatan sebagai selisih yang diketahui.** Peraturan Perusahaan memicu SP dari kehadiran dan tidak menyebut KPI sama sekali, sementara spreadsheet memakai jalur KPI rendah menuju KPK menuju SP 1. Tambahkan ke [[HRIS - Kepatuhan Peraturan Perusahaan]] sebagai selisih, **bukan** sebagai fitur, mengikuti [[ADR - 0071 Peta Kepatuhan Peraturan Perusahaan dan Kewajiban ADR untuk Penyimpangan]]. Dependensi: tidak ada.

## Yang sengaja TIDAK ada di daftar ini

| Yang ditunda | Kenapa |
|---|---|
| KPK sebagai modul | Tidak ada keputusan yang menunggu, dan jalur menuju SP belum punya dasar tertulis (ADR 0115 keputusan 3) |
| Talent Assessment 9-box dan Talent Pool | Butuh skor training yang hari ini hampir nol; dibangun sekarang berarti layar berwibawa tanpa isi |
| TNA | Sama, dan `training_plan_item` sudah menutupi sisi penjadwalannya |
| Development Program, Bootcamp, PKL/Magang | Belum ada keputusan yang bergantung padanya |
| Kamus Kompetensi dan Silabus | Matriks kompetensi masih TBD di dok HRIS; membangun wadahnya lebih dulu tidak menjawab apa pun |
| Vendor pelatihan | Sudah punya rumahnya sendiri, T2 di [[ANALISA - Penyelenggara dan Bank Sertifikat Pelatihan]] |

Syarat membuka kembali seluruh daftar tunda ini ada di ADR 0115 keputusan 6.

## Catatan

- **Nol yang mencurigakan bukan kabar baik**: bila sesudah T4 sertifikat dan evaluasi tetap nol, itu pertanyaan, bukan kabar baik.
- **Angka di daftar ini bertanggal 2026-09-21**; ukur ulang sebelum dipakai mengambil keputusan.
