> **Papan kerja**, bukan dokumen arsitektur. Berubah tiap item selesai. Keputusan yang matang naik jadi ADR atau dok domain; yang selesai dicoret dari sini.
>
> ⚠️ Berkas ini ada di `Workspace/`, jadi **dok yang terbit ke wiki DILARANG menautkannya**. Menunjuk ke sini dari `GA - Dashboard per Posisi` atau `HRIS - Dashboard per Posisi` akan menghasilkan tautan rusak di wiki.

# Kesenjangan Alat Kerja dan Penilaian KPI HRGA

**Diukur 2026-09-21** ke `origin/main` `bip-erp` commit `6ef719e3`, dengan kontrol positif pada tiap pencarian. Mencakup Human Resource, General Affair, dan Procurement (dua posisi, tinggal di folder GA).

**Diukur ulang 2026-09-24** ke `origin/main` `7b767ec9` **dan ke database produksi**. Pengukuran pertama seluruhnya dari kode; yang kedua menambahkan `employee_db` dan `learning_db`, dan itu membalik **enam** baris di bawah. Golongan A (belum ada kodenya) bertahan utuh 10 dari 10; yang meleset justru golongan B dan C, yaitu persis bagian yang dokumen ini sendiri peringatkan agar diukur ulang sebelum dipakai. Ringkasannya di bab **Cakupan otomatis terukur**; baris yang sudah tidak berlaku dicoret di tempatnya.

Dipisah menurut **siapa yang mengerjakan**, bukan menurut besarnya, karena itu yang paling sering salah diasumsikan.

## Cara memakai papan ini

- Golongan **A** pekerjaan dev. **B** pekerjaan HR dan GA (kodenya sudah ada, isinya yang kosong). **C** keputusan pemilik KPI, nol baris kode.
- Sebelum mengambil item dari **B**, **ukur ulang ke database**. Angkanya berasal dari dok vault bertanggal 2026-08-26 sampai 2026-09-18 dan tidak diverifikasi ulang saat papan ini dibuat.
- Sebelum mengambil item dari **A**, ulangi pencariannya. Beberapa klaim "belum ada" di dok lama sudah terbukti usang dalam satu sesi ini (lihat bab terakhir).

## Cakupan otomatis terukur (prod, 2026-09-24)

Diambil dari template yang **benar-benar menghasilkan skor** periode 2026-08, lewat `kpi_score.template.name`. ⚠️ **Bukan** dari `kpi_template_assignment`: koleksi itu berisi hasil semai migrasi (`metadata.created_by = migrasi:semai-dari-kpi_score`) dan sudah basi, sehingga membacanya menyimpulkan generasi template yang salah.

**2,80 dari 11,00 bobot otomatis di 11 posisi, sekitar 25%.** Sisanya diketik penilai.

| Posisi | Auto | Sumber yang terpasang |
|---|---|---|
| Recruitment & Onboarding | **0,75** | `rekrutmen` ×4 |
| Training & Perfomance Officer | **0,65** | `pelatihan` ×2, `rencana_pelatihan` |
| HRD Supervisor | 0,35 | `skor_tim`, `turnover_karyawan`, `indeks_layanan_tim` |
| GA Staff (Building and Maintenance Staff) | 0,35 | `kinerja_tiket` |
| Security · Office Boy | 0,30 | `nilai_layanan_pribadi` |
| Personalia | 0,10 | `kedisiplinan_absensi` |
| Leader Procurement | 0,10 | `skor_tim` |
| Admin GA · Staff Inventory · GA Staff (Asset) · Culture & Industrial | 0,00 | nihil |

⛔ **Terpasang tidak berarti berbunyi, dan inilah temuan terpentingnya.** Seluruh **0,65** milik Training & Perfomance Officer sudah tersambung ke sumber yang benar, tetapi koleksi pemberi makannya kosong di produksi: `quiz_attempt` **0** (mematikan `peningkatan_post_test_persen`, bobot **0,35**, metrik otomatis tunggal terbesar di seluruh HRGA), `training_plan_item` **0** (`rencana_pelatihan` 0,2), dan `training_participant` cuma **4** untuk 13 pelatihan (`kehadiran_peserta_persen` 0,1). Pekerjaan dev-nya sudah selesai; yang tersisa mengisi data.

⚠️ **Dua generasi template masih berdiri berdampingan** untuk tujuh posisi (Culture & Industrial, GA Staff, HRD Supervisor, Office Boy, Recruitment & Onboarding, Security, Training & Perfomance Officer). Generasi baru mulai menilai di **2026-08** dan generasi lama berhenti di **2026-07**, jadi peralihannya sudah terjadi. Yang membuktikan hanya periode di `kpi_score`, karena kedua generasi sama-sama `is_active` kosong.

⚠️ Periode terakhir yang berskor adalah **2026-08**; September belum ditutup saat diukur.

## Rencana dan urutan pengerjaan

Disepakati 2026-09-21. Diurutkan menurut **bobot metrik yang dibuka per satuan usaha**, bukan menurut besar pekerjaannya. Hasilnya: **dua tingkat teratas tidak butuh satu baris kode pun.**

**Urutan yang dipilih: Tingkat 0 dan Tingkat 1 dikerjakan lebih dulu, serentak.** Keduanya tidak memakai waktu dev sama sekali, jadi tidak saling menunggu. Dev baru masuk di Tingkat 2.

### Tingkat 0 — nol baris kode (pemilik KPI)

Lembar keputusan untuk dibawa ke rapat. Tiap baris adalah satu keputusan, bukan satu tugas dev.

| ☐ | Metrik | Keadaan sekarang (diukur prod 2026-09-24) | Yang perlu diputuskan |
|---|---|---|---|
| ☐ | Staff Inventory, 2 metrik bobot **0,6** | **manual**, tanpa blok `auto`. `key`-nya warisan salin-tempel: `revenue-240m` dan `revenue-240-m` | sumber benarnya apa. Kandidat kuat data penerimaan dan PO di procurement, tetapi **menetapkannya hak pemilik KPI**, bukan tebakan dari papan ini |
| ☐ | Procurement Leader, metrik rebate 0,1 | **manual**, `key` warisan `penurunan-hpp-5` | sumber kontrak **vendor** yang benar |
| ☐ | HRD Supervisor, metrik aset | **manual** ("Monitoring Asset" 0,25) | apa yang sebenarnya diukur |
| ☐ | Security, kepatuhan SOP **0,2** | belum dipetakan | apakah cukup lewat `ceklis_kpi` dengan penilai SPV. Bila ya, **nol modul baru** |
| ✅ | ~~Recruitment & Onboarding, 0 dari 5~~ | **SELESAI.** 4 dari 5 sudah otomatis, bobot 0,75 | sisa manual cuma Jobdesk 0,25, dan itu terhalang penyimpanan (golongan A) |
| ✅ | ~~Turnover probation~~ | **SELESAI.** `retensi_masa_probation` terpasang 0,1 | — |
| ✅ | ~~Security, rating pelayanan 0,3~~ | **SUDAH DIPETAKAN** ke `nilai_layanan_pribadi` | — |

⛔ **Koreksi penting atas versi 2026-09-21 papan ini: tidak ada metrik HRGA yang "salah petak" ke sumber lain.** Versi sebelumnya menyebut Staff Inventory menunjuk `tt_business_gmv_max_performance_reports`, Procurement Leader menunjuk `work_data.contract_ending`, dan HRD Supervisor menunjuk data retur. Diukur di `kpi_template` produksi, ketiganya **tidak punya blok `auto` sama sekali** — semuanya diketik penilai. Yang nyata ada dan memang membingungkan adalah **slug `key` warisan**: `revenue-240m` dipakai bersama **12 template**, sisa salin-tempel saat template dibuat, dan slug itulah yang terbaca seperti tautan ke metrik revenue.

⚠️ Konsekuensinya **urutan prioritas berubah**. Metrik manual yang labelnya benar tidak menghasilkan angka salah, ia cuma tidak otomatis, jadi baris Staff Inventory **turun dari "paling mendesak"**. Yang masih layak diperiksa cepat: memastikan tak ada lapisan lain (mis. pemetaan di dashboard per posisi) yang me-resolusi metrik lewat `key`, karena satu slug dipakai 12 template.

### Tingkat 1 — isi data ke modul yang sudah berdiri (HR)

⛔ **Koreksi 2026-09-24: modul Training BUKAN kosong, dan itu mengubah cara mengerjakannya.** `learning_db` produksi sudah berisi **13 pelatihan, 25 jenis pelatihan, dan 7 trainer**. Yang kosong justru koleksi di hilirnya, dan justru itulah yang dibaca metrik KPI. Jadi ini bukan "isi modul dari nol" melainkan "tutup tiga koleksi hilir".

**Daya ungkitnya tetap yang terbesar di seluruh HRGA**, sekarang dengan angka pasti: **0,65 bobot Training & Perfomance Officer sudah tersambung ke sumber yang benar dan tidak menghasilkan apa pun** karena kekurangan data ini.

| ☐ | Koleksi | Isi di prod | Metrik yang kelaparan |
|---|---|---|---|
| ☐ | `quiz_attempt` | **0** | `peningkatan_post_test_persen` — bobot **0,35**, metrik otomatis tunggal terbesar di HRGA |
| ☐ | `training_plan_item` | **0** | `rencana_pelatihan` 0,2 |
| ☐ | `training_participant` | **4** untuk 13 pelatihan | `kehadiran_peserta_persen` 0,1 |
| ☐ | `trainer_evaluation` | **1** | `kepuasan_trainer_skala10`, `kesesuaian_materi_skala10` (belum terpasang ke template) |

⚠️ Sumber `pelatihan` sudah live di produksi **dan sudah terpasang ke template `People and Development`**, jadi yang menahan memang cuma datanya. Sisi dev yang tersisa hanya layar post-test yang belum ada, dan itu pula yang menjelaskan kenapa `quiz_attempt` nol: ada 1 `quiz` terdefinisi tetapi tak ada cara mengerjakannya.

⚠️ Angka 1,30 bobot di tiga posisi pada versi 2026-09-21 adalah potensi, bukan keadaan. Yang **benar-benar tersambung** hari ini hanya 0,65 di Training & Perfomance Officer; bagian Culture & Industrial (template `HR Organizational Development`) masih 0,00 otomatis, dan di HRD Supervisor metrik pelatihan 0,1 masih manual.

### Tingkat 2 — penyimpanan kecil yang mengunci banyak (dev)

Jobdesk per posisi (0,25 Recruitment + 0,15 Training) · master anggaran departemen GA (3 metrik) · stok opname aset (0,15). Ketiganya penyimpanan sederhana, bukan modul besar, dan rasio dampak terhadap usahanya paling baik di antara pekerjaan dev.

### Tingkat 3 — modul baru (dev)

Inspeksi berjadwal lebih rapat dari mingguan. Irisan pertamanya sudah dirancang: `GA - Ronda Security` + ADR 0112. Selain membuka metrik patroli 0,3, ia memberi Office Boy dan Security **antrean pertamanya**, yang menurut ADR 0076 adalah syarat posisi itu layak punya dashboard sama sekali.

### Tingkat 4 — besar, sempit, terakhir

Modul MRP untuk Procurement Leader, bobot 0,2. Pekerjaan terbesar, cakupan tersempit di seluruh papan ini.

## A. Belum ada kodenya (dev)

| ☐ | Item | Mengunci | Catatan |
|---|---|---|---|
| ☐ | Inspeksi berjadwal lebih rapat dari mingguan | metrik patroli 0,3 | irisan pertama sudah dirancang: `GA - Ronda Security` + ADR 0112. Recurrence form-builder cuma `monthly` dan `weekly` |
| ☐ | **Jobdesk per posisi** | 0,25 Recruitment & Onboarding, 0,15 Training | tidak ada penyimpanan di sistem mana pun. Satu-satunya kecocokan `QJobdesk` adalah pertanyaan ke kandidat di recruitment. Juga yang membuat kelengkapan alat kerja tiap posisi mustahil dijawab sistem |
| ☐ | **Master anggaran departemen GA** | 3 metrik di Admin dan GA Staff | |
| ☐ | Stok opname aset | akurasi stok GA Staff 0,15 | beda dari `repair_history` yang sudah ada, lihat golongan B |
| ☐ | Kontrol SOP Procurement: RFQ 3 vendor, evaluasi vendor, AVL, matriks approval nominal | kepatuhan SOP pengadaan | keempatnya nol di `services/procurement` |
| ☐ | Modul MRP | Procurement Leader 0,2 | pekerjaan terbesar, cakupan tersempit |
| ☐ | LMS materi, kurikulum jabatan, Talent Pool | sisa bobot Training | post-test berskor sudah ada, layarnya belum |
| ☐ | Exit clearance off-boarding | Personalia | |
| ☐ | Overtime request dan approval workflow | HRIS | 💤 **sengaja ditunda PO**, bukan terlupa. Pencatatan lembur sudah ada |
| ☐ | e-Signing dan e-Meterai kontrak | Personalia | 116 berkas pada pencarian awal ternyata kata "design" |
| ☐ | HRD Documents sisi karyawan (Dokumen Saya, ack, S&K) | HRD | sisi author sudah ada |
| ✅ | ~~Metrik time to fill / fulfilment~~ | Recruitment | **SELESAI**, terpasang sebagai `pemenuhan_tepat_waktu` bobot 0,25. ⚠️ Mencarinya dengan `time_to_fill` membalas **nol** karena namanya Indonesia; itu yang membuatnya terdaftar sebagai "belum ada" |
| ☐ | Booking berulang dan pemilih ruang di modul lain (irisan 3 sampai 7) | GA | irisan 1, 1b, dan 2 sudah merged |
| ☐ | Serah terima shift, insiden keamanan, gate pass, kunci dan akses fisik, CCTV | Security | inventaris lengkap di `GA - Ronda Security` bab Inventaris Alat Kerja Security |

## B. Kode sudah ada, datanya yang kosong (HR dan GA)

⚠️ **Ukur ulang ke database sebelum dipakai memutuskan.** Ini jenis status yang bergerak. Baris bertanda 2026-09-24 sudah diukur; sisanya belum.

| ☐ | Item | Keadaan tercatat |
|---|---|---|
| ☐ | Isi `repair_history` aset | koleksi sudah ada di inventory lengkap dengan komponen biaya, isinya kosong. **Belum diukur ulang** |
| ☐ | Isi modul Training di produksi | **diukur 2026-09-24:** pelatihan, jenis, dan trainer sudah terisi; yang nol `quiz_attempt` dan `training_plan_item`, peserta baru 4. Rinciannya di Tingkat 1 |
| ☐ | Pakai Payroll untuk menggaji | lengkap sampai terbit slip, dua `payroll_run` masih `draft`, nol slip pernah terbit. **Belum diukur ulang** |
| ✅ | ~~Pasang sumber KPI `rekrutmen` ke template~~ | **SELESAI, diukur 2026-09-24.** Empat metrik terpasang di template `Recruitment` (`pemenuhan_tepat_waktu` 0,25 · `review_evaluasi_tepat_waktu` 0,2 · `buffer_mpp_kritikal_persen` 0,2 · `retensi_masa_probation` 0,1) dan sudah menilai di periode 2026-08 |

## C. Pemetaan belum diputuskan (pemilik KPI, nol baris kode)

Diperbarui 2026-09-24. Tiga baris dicoret karena sudah terjawab, dan tiga baris yang tersisa **berubah sifat**: bukan salah petak, melainkan belum dipetakan sama sekali (lihat koreksi di Tingkat 0).

| ☐ | Item | Kenapa mendesak |
|---|---|---|
| ☐ | Staff Inventory: dua metrik bobot total **0,6** | manual seluruhnya. Tidak menghasilkan angka salah, tapi 0,6 bobot bergantung penuh pada ketikan penilai. `key` warisan `revenue-240m` dipakai bersama 12 template dan layak dibereskan terpisah |
| ☐ | Security: kepatuhan SOP 0,2 | belum dipetakan. Berpeluang lewat `ceklis_kpi` tanpa modul baru |
| ☐ | Procurement Leader: metrik rebate | manual, `key` warisan `penurunan-hpp-5`. Perlu sumber kontrak **vendor** |
| ☐ | HRD Supervisor: metrik aset | manual ("Monitoring Asset" 0,25). Perlu ditetapkan apa yang diukur |
| ☐ | Apakah Guestbook layak masuk KPI Security | pekerjaan nyata yang tercatat rapi tapi tidak muncul di satu pun metrik |
| ☐ | Satu shift Security isinya apa saja | dijawab dengan bertanya ke SPV HRGA, bukan mencari di kode |
| ✅ | ~~Security: rating pelayanan 0,3~~ | **SUDAH DIPETAKAN** ke `nilai_layanan_pribadi`, dipakai 4 template HRGA |
| ✅ | ~~Turnover probation~~ | **SELESAI**, `retensi_masa_probation` terpasang 0,1 |

## Koreksi dok usang yang ditemukan saat mengukur

Dicatat supaya tidak dikerjakan ulang sebagai "fitur baru".

- ✅ **Community of Interest SUDAH punya backend** di form-builder, dan sumber KPI `program_culture` sudah terdaftar. Diukur ulang 2026-09-24 ternyata jauh lebih besar dari catatan awal: **23 berkas `culture_*` dan 9 koleksi**, plus grup rute `/culture` di `routes.go`. Frontend-nya juga sudah pindah seluruhnya dari `/hris/community/*` ke `/hris/program-culture/*` (7 halaman) dan memanggil backend lewat `use-culture.ts`. **Ditindaklanjuti 2026-09-24:** dok `HRIS - Pengembangan Organisasi (Community of Interest)` ditandai **SUPERSEDED** dengan tiga klaimnya yang terbantah dicatat di kepalanya, menunjuk ke ADR 0066 / 0084 / 0093 dan `Microservices - Form Builder Service`. Tidak ditulis ulang, karena itu task tersendiri.
- `repair_history` **sudah** jadi koleksi di inventory. Yang kosong isinya, bukan kodenya.
- Koleksi `candidate` **sudah ada**; yang nol adalah metrik time to fill.
- Metrik Security "Kerapihan dan kebersihan pos jaga" **sudah punya sumber** (`nilai_inspeksi_satgas`), sudah dikoreksi di `GA - Dashboard per Posisi`.
- `ceklis_kpi` **sudah ada** sebagai mekanisme generik yang menautkan metrik KPI ke satu butir form-builder lewat UID butir. Metrik berbentuk "sudah atau belum" tidak butuh modul baru.

## Jebakan pencarian yang sudah terbukti di sini

Dicatat karena ketiganya hampir menerbitkan temuan palsu, dan ketiganya akan terulang.

- `incident` mengembalikan **93 berkas**, seluruhnya integration dan monitoring (insiden marketplace dan sistem), nol soal keamanan.
- `apar` mengembalikan **84 berkas**, mayoritas kata "pemadaman". APAR sungguhan cuma satu butir form Satgas.
- `esign` mengembalikan **116 berkas**, seluruhnya kata "design".
- `plat` mengena "GoogleCloudPlatform"; `checklist` mengena form-builder generik; `limbah` mengena metrik KPI produksi; `clearance` mengena bea cukai TikTok.

**Aturannya: pakai batas kata, periksa isi berkasnya, jangan menghitung jumlah berkas.** Dan `Grep` melewati berkas yang mengandung byte NUL, jadi klaim "tidak ada" wajib memakai `git grep` berkontrol positif.

### Arah sebaliknya, yang menggigit di pengukuran 2026-09-24

Keempat jebakan di atas menerbitkan temuan **palsu-positif**. Putaran kedua kena yang kebalikannya, dan itu lebih berbahaya karena hasilnya terbaca sebagai "sudah dicek, memang belum ada".

- ⛔ **Nama Indonesia menyembunyikan fitur yang sudah ada.** `time_to_fill` mengembalikan **nol**, dan itu benar secara harfiah; metriknya hidup dengan nama `pemenuhan_tepat_waktu`. Satu baris golongan A karena itu salah terdaftar selama tiga hari. **Cari konsepnya dalam dua bahasa sebelum menulis "belum ada".**
- ⛔ **Kode bukan sumber kebenaran untuk pemetaan KPI.** Terpasang atau tidaknya sebuah sumber ke sebuah metrik tinggal di **`kpi_template` di database**, bukan di repo. Seluruh enam koreksi putaran ini hanya terlihat setelah mengukur ke prod; pencarian kode sesempurna apa pun tak akan menemukannya.
- ⛔ **`kpi_score` tidak punya field `position` di akar.** Identitasnya ada di dalam snapshot `template` (`template.position`, `template.name`, `template.department`). Query `{position: /inventor/i}` membalas **0 tanpa galat** dan sempat terbaca sebagai "template ini tidak menilai siapa-siapa"; lewat `template.position` ternyata ada 4 skor sampai 2026-08. Sekelas dengan 200-berisi-nol-baris. **Sebelum menyimpulkan nol, buktikan fieldnya ada** dengan `countDocuments({<field>: {$exists: true}})`.
- ⚠️ **`kpi_template_assignment` basi dan menyesatkan.** Isinya hasil semai migrasi (`metadata.created_by = migrasi:semai-dari-kpi_score`) dan menunjuk generasi template lama, sementara yang benar-benar menilai sejak 2026-08 adalah generasi baru. Yang membuktikan generasi mana yang hidup hanya **periode di `kpi_score`**, karena kedua generasi sama-sama tanpa `is_active`.

## Sumber angka

`GA - Dashboard per Posisi` · `HRIS - Dashboard per Posisi` · `GA - Ronda Security` · `HRIS - Matriks KPI per Departemen` · registry sumber KPI di `services/employee/kpi_sumber_*.go`.

**Pengukuran 2026-09-24** (prod, baca saja): `employee_db.kpi_template` (119 dok) untuk pemetaan metrik ke sumber, `employee_db.kpi_score` (679 dok) untuk template mana yang benar-benar menilai dan di periode apa, `learning_db` untuk isi modul Training. Batas recurrence form-builder dari `services/form-builder/models_period.go` (`monthly`, `weekly`).
