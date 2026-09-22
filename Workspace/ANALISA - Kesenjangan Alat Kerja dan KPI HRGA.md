> **Papan kerja**, bukan dokumen arsitektur. Berubah tiap item selesai. Keputusan yang matang naik jadi ADR atau dok domain; yang selesai dicoret dari sini.
>
> ⚠️ Berkas ini ada di `Workspace/`, jadi **dok yang terbit ke wiki DILARANG menautkannya**. Menunjuk ke sini dari `GA - Dashboard per Posisi` atau `HRIS - Dashboard per Posisi` akan menghasilkan tautan rusak di wiki.

# Kesenjangan Alat Kerja dan Penilaian KPI HRGA

**Diukur 2026-09-21** ke `origin/main` `bip-erp` commit `6ef719e3`, dengan kontrol positif pada tiap pencarian. Mencakup Human Resource, General Affair, dan Procurement (dua posisi, tinggal di folder GA).

Dipisah menurut **siapa yang mengerjakan**, bukan menurut besarnya, karena itu yang paling sering salah diasumsikan.

## Cara memakai papan ini

- Golongan **A** pekerjaan dev. **B** pekerjaan HR dan GA (kodenya sudah ada, isinya yang kosong). **C** keputusan pemilik KPI, nol baris kode.
- Sebelum mengambil item dari **B**, **ukur ulang ke database**. Angkanya berasal dari dok vault bertanggal 2026-08-26 sampai 2026-09-18 dan tidak diverifikasi ulang saat papan ini dibuat.
- Sebelum mengambil item dari **A**, ulangi pencariannya. Beberapa klaim "belum ada" di dok lama sudah terbukti usang dalam satu sesi ini (lihat bab terakhir).

## Rencana dan urutan pengerjaan

Disepakati 2026-09-21. Diurutkan menurut **bobot metrik yang dibuka per satuan usaha**, bukan menurut besar pekerjaannya. Hasilnya: **dua tingkat teratas tidak butuh satu baris kode pun.**

**Urutan yang dipilih: Tingkat 0 dan Tingkat 1 dikerjakan lebih dulu, serentak.** Keduanya tidak memakai waktu dev sama sekali, jadi tidak saling menunggu. Dev baru masuk di Tingkat 2.

### Tingkat 0 — nol baris kode (pemilik KPI)

Lembar keputusan untuk dibawa ke rapat. Tiap baris adalah satu keputusan, bukan satu tugas dev.

| ☐ | Metrik | Keadaan sekarang | Yang perlu diputuskan |
|---|---|---|---|
| ☐ | Staff Inventory, 2 metrik bobot **0,6** | menunjuk `tt_business_gmv_max_performance_reports` (data iklan TikTok) | sumber benarnya apa. Kandidat kuat data penerimaan dan PO di procurement, tetapi **menetapkannya hak pemilik KPI**, bukan tebakan dari papan ini |
| ☐ | Recruitment & Onboarding, **0 dari 5** | sumber `rekrutmen` sudah merged tapi belum dipasang ke template mana pun | metrik mana dipasang ke baris mana. Yang tersedia: `pemenuhan_tepat_waktu`, `pemenuhan_tepat_waktu_kritikal`, `buffer_mpp_persen`, `buffer_mpp_kritikal_persen`, `review_evaluasi_tepat_waktu`, `retensi_masa_probation` |
| ☐ | Turnover probation | sumber terdaftar mengukur resign sukarela seluruh perusahaan | ⚠️ **periksa `retensi_masa_probation`** dari sumber `rekrutmen` di atas. Ia mungkin sudah menjawab persis pertanyaan ini, sehingga perbaikannya tinggal memasang, bukan membangun. Perlu dikonfirmasi semantiknya lebih dulu |
| ☐ | Procurement Leader, metrik rebate 0,1 | menunjuk kontrak **karyawan** (`work_data.contract_ending`) | sumber kontrak **vendor** yang benar |
| ☐ | HRD Supervisor, metrik aset | sumbernya data retur, deskripsinya monitoring aset | apa yang sebenarnya diukur |
| ☐ | Security, rating pelayanan **0,3** | belum dipetakan sama sekali | diukur dari apa |
| ☐ | Security, kepatuhan SOP **0,2** | belum dipetakan | apakah cukup lewat `ceklis_kpi` dengan penilai SPV. Bila ya, **nol modul baru** |

⛔ **Baris pertama paling mendesak dan bukan karena bobotnya.** Metrik kosong terlihat kosong; metrik salah petak terlihat berfungsi. Sumbernya ratusan ribu baris sehingga angkanya mulus, stabil, dan sepenuhnya keliru, dan ia **sedang menilai orang sekarang**.

### Tingkat 1 — isi data ke modul yang sudah berdiri (HR)

**Modul Training sudah ter-deploy dan kosong.** Mengisinya membuka **1,30 bobot di tiga posisi sekaligus**: 0,75 di Training & Performance Officer (0,55 langsung, 0,2 menunggu definisi "rencana"), 0,4 di Culture & Industrial, dan 0,15 di HRD Supervisor. **Tidak ada pekerjaan lain di seluruh HRGA yang mendekati daya ungkit ini.**

| ☐ | Yang diisi | Menyalakan metrik |
|---|---|---|
| ☐ | pelatihan, peserta, kehadiran | `kehadiran_peserta_persen` |
| ☐ | post-test berskor | `skor_post_test_persen`, `peningkatan_post_test_persen` |
| ☐ | evaluasi | `kenaikan_kpi_peserta_persen` |

⚠️ Sumber `pelatihan` sudah live di produksi, jadi yang menahan **memang cuma datanya**. Sisi dev yang tersisa hanya layar post-test yang belum ada.

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
| ☐ | Metrik time to fill / fulfilment | Recruitment | koleksi `candidate` **sudah ada**; yang nol metriknya |
| ☐ | Booking berulang dan pemilih ruang di modul lain (irisan 3 sampai 7) | GA | irisan 1, 1b, dan 2 sudah merged |
| ☐ | Serah terima shift, insiden keamanan, gate pass, kunci dan akses fisik, CCTV | Security | inventaris lengkap di `GA - Ronda Security` bab Inventaris Alat Kerja Security |

## B. Kode sudah ada, datanya yang kosong (HR dan GA)

⚠️ **Ukur ulang ke database sebelum dipakai memutuskan.** Ini jenis status yang bergerak, dan angkanya bukan hasil ukur hari ini.

| ☐ | Item | Keadaan tercatat |
|---|---|---|
| ☐ | Isi `repair_history` aset | koleksi sudah ada di inventory lengkap dengan komponen biaya, isinya kosong |
| ☐ | Isi modul Training di produksi | modul sudah ter-deploy; pelatihan, peserta, kehadiran, evaluasi, dan post-test belum diisi |
| ☐ | Pakai Payroll untuk menggaji | lengkap sampai terbit slip, dua `payroll_run` masih `draft`, nol slip pernah terbit |
| ☐ | Pasang sumber KPI `rekrutmen` ke template | sumbernya sudah merged, belum dipasang ke template mana pun |

## C. Pemetaan belum diputuskan (pemilik KPI, nol baris kode)

| ☐ | Item | Kenapa mendesak |
|---|---|---|
| ☐ | **Staff Inventory: dua metrik bobot total 0,6 menunjuk data iklan TikTok** | **paling mendesak.** Bukan belum tersambung melainkan tersambung ke tempat yang salah, sumbernya ratusan ribu baris sehingga menghasilkan angka mulus yang sepenuhnya keliru, dan itu sedang menilai orang sekarang |
| ☐ | Security: rating pelayanan 0,3 | belum dipetakan sama sekali |
| ☐ | Security: kepatuhan SOP 0,2 | belum dipetakan. Berpeluang lewat `ceklis_kpi` tanpa modul baru |
| ☐ | Procurement Leader: metrik rebate | menunjuk kontrak **karyawan**, padahal metriknya kontrak **vendor** |
| ☐ | HRD Supervisor: metrik aset | sumbernya data retur, deskripsinya monitoring aset |
| ☐ | Turnover probation | sumbernya mengukur resign sukarela seluruh perusahaan |
| ☐ | Apakah Guestbook layak masuk KPI Security | pekerjaan nyata yang tercatat rapi tapi tidak muncul di satu pun metrik |
| ☐ | Satu shift Security isinya apa saja | dijawab dengan bertanya ke SPV HRGA, bukan mencari di kode |

## Koreksi dok usang yang ditemukan saat mengukur

Dicatat supaya tidak dikerjakan ulang sebagai "fitur baru".

- ⛔ **Community of Interest SUDAH punya backend** di form-builder (`culture_clubs.go`, `culture_events.go`, `culture_notify.go`, `models_culture.go`, `culture_club_seed.go`, `db.go`), dan sumber KPI `program_culture` sudah terdaftar. Dok `HRIS - Pengembangan Organisasi (Community of Interest)` masih menyatakan seluruh data klub konstanta di frontend dan belum ada service maupun storage di backend. **Dok itu perlu disegarkan.**
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

## Sumber angka

`GA - Dashboard per Posisi` · `HRIS - Dashboard per Posisi` · `GA - Ronda Security` · `HRIS - Matriks KPI per Departemen` · registry 43 sumber KPI di `services/employee/kpi_sumber_*.go`.
