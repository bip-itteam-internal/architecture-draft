# ANALISA - KPI Tax Officer

Papan kerja hasil `/analisa-kebutuhan` atas matriks KPI posisi Tax yang datang dari manajemen, 2026-08-31. Bukan arsitektur; keputusan dan cara kerjanya tinggal di [[Finance - Rancangan Finance Service]].

## Kebutuhan sebenarnya, dipisah dari yang diminta

**Yang diminta**: "saran fitur untuk posisi Tax", disertai matriks 7 KPI berbobot 90 dengan kolom dokumen pendukung yang hampir seluruhnya berbunyi *laporan* atau *upload document*.

**Yang sebenarnya dibutuhkan**: delapan metrik KPI Tax yang hari ini **seluruhnya diisi tangan** perlu punya dasar yang dapat diperiksa. Itu dua kebutuhan berbeda yang matriksnya campur jadi satu:

1. **Tempat pekerjaan Tax tercatat.** SPT Masa, temuan kepatuhan, dan rekonsiliasi bulanan hari ini hidup di Excel pribadi, DJP Online, dan e-Faktur. Tak satu pun terjangkau sistem, sehingga tak ada yang bisa dihitung maupun diaudit.
2. **Angka KPI yang terisi sendiri.** Ini akibat dari yang pertama, bukan sesuatu yang bisa dikerjakan mendahuluinya, kecuali untuk satu metrik yang sumbernya memang sudah ada.

⛔ **Fiturnya bukan barang yang belum dipikirkan.** [[Finance - Rancangan Finance Service]] sudah merancang modul Tax lengkap (master jenis kewajiban, kewajiban per masa, register SPT, register temuan, klasifikasi akun deductible) beserta mesin status, rute FE tiga tab, notifikasi H-7/H-3, dan feed kalender. Yang menahannya **dua keputusan pemilik metrik**, bukan pekerjaan teknis.

## Dua keputusan yang menghentikan, dan pemiliknya bukan IT

Disalin dari bab "Menghentikan modul Tax (bobot 0,45)" di [[Finance - Rancangan Finance Service]]. Selama keduanya belum dijawab, membangun berarti menebak.

| # | Keputusan | Pemilik |
|---|---|---|
| 5 | **Input berstruktur menggantikan unggah dokumen sebagai dasar penilaian?** Kolom `SISTEM ERP` di Excel KPI meminta `FITUR UP DOKUMEN` untuk 7 dari 9 metrik Tax | SPV FAT + Tax Officer |
| 6 | **Pola tenggat per jenis pajak** — jatuh tempo setor, jatuh tempo lapor, dan urutannya untuk PPh 21/23/25, PPh 4 ayat 2, PPN Masa | Tax Officer |

**Kenapa #5 menentukan besar-kecilnya seluruh pekerjaan**: bila jawabannya *unggah dokumen*, jalurnya sudah tersedia penuh (file-service, tipe field `file` form-builder, preseden Register Perizinan) dan pekerjaannya kecil, tetapi KPI-nya **tetap dinilai manusia** karena berkas tidak bisa dihitung mesin. Bila jawabannya *input berstruktur*, KPI-nya bisa dihitung tetapi modulnya belum punya satu pun endpoint. Menebaknya berarti membangun hal yang salah dengan rapi.

⚠️ Rancangan yang ada **sudah memilih input berstruktur** dan menyatakan penyimpangannya sendiri dari permintaan Finance. Penyimpangan itu belum pernah disetujui pemiliknya. Itu yang perlu ditutup lebih dulu.

## Keadaan terukur, 2026-08-31

Diukur langsung ke produksi, bukan diperkirakan.

**Template `KPI Tax Officer`** (posisi `Tax Staff`, dept Finance, status aktif): 8 metrik, bobot total 1,00, **kedelapannya `auto: MANUAL`**. Dua karyawan memakainya. Matriks dari manajemen memuat 7 KPI berbobot 90; selisih 10 adalah metrik ide inovasi yang ada di template tetapi tidak ada di matriks.

**Data yang tersedia di `integration_db` produksi:**

| Koleksi | Dokumen | Periode terisi |
|---|---:|---|
| `anggaran_opex` | 233 | 2026-07 s/d 2026-12, 40 akun, **hanya 3 departemen** (`""`, `MARKETING - BEAUTYHACKS`, `MARKETING - KY + GB`) |
| `realisasi_opex` | 250 | 2026-07, 2026-08 |
| `accurate_ppn_masukan` | 167 | 2026-07, 2026-08 |
| `catatan_beban_manual` | 57 | 2026-08 |
| `accurate_jurnal_kas` | **0** | belum pernah terisi |

**Riwayat efektifnya dua bulan.** Metrik apa pun yang menuntut tren atau pembanding tahun lalu belum punya dasar.

⛔ **Tidak ada satu pun penanda deductible / non-deductible di data mana pun.** Diperiksa pada `accurate_ppn_masukan`, `catatan_beban_manual`, `realisasi_opex`, `anggaran_opex`, dan `incentive_opex_accurate`. Field `taxable` pada PPN masukan adalah DPP yang kena pajak, **bukan** klasifikasi fiskal. Klasifikasi deductible adalah keputusan Tax Officer yang hari ini tidak pernah tercatat di mana pun, dan itulah sebabnya ia masuk lingkup modul Tax sebagai master tersendiri.

## Tiga koreksi terhadap vonis yang beredar

**1. "Budget TIDAK tersimpan di ERP mana pun" sudah kedaluwarsa.** Vonis itu di [[HRIS - Matriks KPI per Departemen]] untuk metrik `Varians antara budget vs realisasi OPEX ≤ ±5%` (bobot 0,15). Master anggaran OPEX kini terisi, dan metriknya **sudah bisa dinyalakan hari ini tanpa satu baris kode**. Pratinjau produksi untuk Tax Staff `BIP-0155-05-25`, periode 2026-07:

```
varians_anggaran / varians_persen   →   source: semi   auto_value: 12,8
  basis  : varians 39,06%; anggaran Rp 5.118.934.685, realisasi Rp 3.119.359.028
  cakupan: 28,06%  "39 dari 139 pos terhitung, sisanya belum dianggarkan atau belum disinkron"
```

Statusnya `semi`, bukan `otomatis`, dan itu jujur: anggaran baru terisi untuk sebagian kecil pos. Menaikkan cakupan adalah pekerjaan **pengisian master data**, bukan pekerjaan dev.

**2. Dua baris yang divonis "bisa otomatis sekarang" keliru, bobot gabungan 0,30.** `Kepatuhan pajak 100% setiap bulan 3` diukur dari *"100% temuan ditindaklanjuti dalam ≤ 10 hari kerja"*, dengan sumber tertulis `/accounting/profit-loss` dan `/balance-sheet`. Laba rugi Accurate tidak menyimpan temuan maupun tanggal tindak lanjutnya. Ini kelas yang sudah dinamai dok rancangan sendiri: **sumber datanya ada, tetapi bukan sumber untuk hal yang diukur**. Berlaku sama untuk `Kepatuhan pajak 100% setiap bulan 1` (rekonsiliasi bulanan).

**3. Rekonsiliasi pajak per nomor faktur mustahil hari ini.** Penjualan digunggung dan `taxNumber` kosong pada 22 dari 22 sampel probe Accurate. KPI #2 menuntut *discrepancy = 0%*; bentuk rekonsiliasi yang dapat dijanjikan bukan per faktur, dan definisinya harus disepakati lebih dulu.

## Masalah pada templatenya sendiri, terpisah dari fitur

Tiga metrik berlabel **`Kepatuhan pajak 100% setiap bulan 1`, `… 2`, `… 3`**. Yang dinilai tidak bisa tahu apa yang diukur darinya, dan ketiganya tak terbedakan di daftar. Sebabnya terbaca jelas: yang masuk kolom `label` adalah **AREA KINERJA**, sementara KPI-nya turun ke `description` — terbalik dari template lain.

Metrik pertama lebih tajam lagi: labelnya `Varians antara budget vs realisasi OPEX ≤ ±5%` (bisa otomatis), deskripsinya bicara **deductible vs non-deductible** (mustahil otomatis). Dua hal berbeda dalam satu baris berbobot 0,15. Ini melanggar aturan di [[REF - Penamaan Metrik & Sumber KPI]] dan wajib diselesaikan pemilik metrik sebelum otomasi apa pun, sebab yang mengikat adalah **hal yang benar-benar dihitung sumbernya**, bukan labelnya.

## Yang bisa dipakai ulang, dan seberapa jauh

Ditelusuri ke kode, bukan ke dokumentasi. Ini yang membuat modul Tax jauh lebih kecil daripada kelihatannya.

| Kebutuhan Tax | Yang sudah ada di kode | Seberapa jauh |
|---|---|---|
| **Kewajiban berkala + tenggat + status penuntasan** | **Modul obligation `calendar-service`**: `obligation_templates`, `obligation_periods`, `obligation_fulfillments`, `GraceDays`, dan empat status `pending/scheduled/fulfilled/missed` | Mesinnya **hampir persis** kebutuhan kewajiban pajak. `missed` sengaja **ditulis cron, bukan dihitung saat dibaca**, dengan alasan yang berlaku sama untuk pajak: *"belum" dan "telat" adalah dua hal berbeda dan yang kedua tak boleh bisa berubah lagi hanya karena seseorang membuka laporannya di hari yang berbeda*. Yang belum ada: satu pun template pajak |
| **Unggah laporan + persetujuan SPV** | **Modul Laporan `form-builder`**: unggah, keputusan **per butir**, unggah ulang butir yang ditolak, antrean penyetuju, pratinjau bergerbang | Rantainya sudah utuh dan jalan di produksi. Wewenang menyetujui sudah dipersempit ke penyetuju **departemen pengirim**, bukan pemilik form. Validasi terhadap **snapshot periode**, bukan definisi form terkini, persis yang dibutuhkan laporan berkala yang formatnya berubah antar tahun pajak |
| **Temuan + tindak lanjut bertenggat** | **Mesin SLA `task-management`**: dua dimensi (response & resolution), enam state, `on_hold` membekukan SLA jadi `held`, laporan breach, eskalasi menganggur | `on_hold` penting untuk temuan yang menunggu jawaban KPP: ia tak pernah tampil `breached` selama ditahan. ⛔ Tapi lihat celah hari kerja di bawah |
| **Metrik KPI tampil sebagai skor** | Registri sumber KPI `employee-service` + seluruh UI otomasi | Metrik Tax cukup jadi **entri baru di katalog**, tanpa satu baris frontend |
| **Penyimpanan berkas** | `file-service`, cap 4 MB | ⚠️ Otorisasinya **per prefix direktori lewat env**. Modul baru wajib mendaftarkan kunci + prefix, kalau tidak seluruh unggah ditolak `invalid access key`. Sudah pernah menggigit procurement. Bila lewat modul Laporan form-builder, prefiksnya sudah terdaftar |

⛔ **Kerangka modul Tax sudah mendarat TANPA isi, dan tak ada yang berbunyi.** `services/finance/db.go:16-19` mendeklarasikan empat nama koleksi — `pajak_kewajiban`, `pajak_spt`, `pajak_temuan`, `pajak_klasifikasi_akun` — dan `git grep` atas keempatnya di seluruh `services/` **hanya mengembalikan baris deklarasinya sendiri**. Nol pemanggil. Kontrol positifnya `rekomendasiCollection` yang muncul 5 kali di `rekomendasi.go`. Konstanta paket di Go tidak memicu galat "declared but not used", sehingga kerangka semacam ini bisa hidup berbulan-bulan tanpa satu pun tanda. `services/finance/routes.go:53-55` menyatakan sebabnya harfiah: *"Modul Tax menyusul; ia menunggu keputusan pemilik metrik."*

⛔ **Tidak ada aritmetika HARI KERJA di seluruh repo.** Dikonfirmasi `git grep` atas `hariKerja|workingDay|businessDay|hari_kerja`: satu-satunya hit adalah `HariKerja` di attendance, yang berarti **penyebut kehadiran** ("hari yang menuntut kehadiran"), bukan "N hari kerja setelah tanggal X". Seluruh SLA yang ada berbasis **jam kalender**. KPI #4 menuntut *"ditindaklanjuti dalam ≤ 10 hari kerja"*, jadi helper baru harus dibangun di atas koleksi `holidays` yang sudah ada (`IsHoliday`). Kecil, tapi jangan sampai luput dari perkiraan.

⚠️ **Tiga akun PPh berasal dari jurnal penyesuaian sehingga tak pernah punya anggaran bulanan** (PPh Final UMKM, PPh Badan 31E, PPh 23). Keanggotaannya di daftar OPEX sudah pasti, tetapi **perlakuannya dalam perhitungan varians masih menunggu keputusan Finance**. Ini menyentuh langsung metrik #1 yang hendak dinyalakan di task 1.

## Yang TIDAK perlu dibangun

- **Metrik ide inovasi (0,10).** Kaizen sudah live dan dua sumber KPI-nya terdaftar, tetapi [[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]] memutuskan Kaizen tidak dipakai untuk otomasi. Manual karena keputusan, bukan karena sistemnya belum ada.
- **Halaman kalender pajak sendiri.** Dilarang; wajib jadi feed [[Microservices - Calendar Service]].
- **Service baru.** `finance-service` sudah berdiri dan live; modul Tax mengisi rumah yang sudah ada.
- **Tandingan PPh 21.** `GET/PUT /config/tax` di payroll-service sudah memegang PPh 21 beserta tabel TER.

## Daftar task

Berurutan. Yang bertanda ⛔ memblokir yang di bawahnya.

### Tanpa menunggu keputusan apa pun

1. **Nyalakan metrik varians OPEX untuk template `KPI Tax Officer`.** Konfigurasi `varians_anggaran` / `varians_persen`, arah `turun`. Tak ada kode; isian HR di Atur Target. Sepakati targetnya lebih dulu, sebab realisasi Juli 39,06% jauh di atas ±5% yang tertulis di matriks. **Prasyarat**: selesaikan lebih dulu tabrakan label-vs-deskripsi pada metrik itu (lihat § Masalah pada templatenya).
2. **Betulkan label tiga metrik `Kepatuhan pajak … 1/2/3`** jadi menyebut yang diukur. Aman dilakukan: `IsiKunciMetrik` mempertahankan `key`, jadi konfigurasi otomatis tidak lepas saat label diganti.
3. **Isi master anggaran OPEX untuk departemen selain Marketing.** Ini yang menaikkan cakupan metrik varians dari 28% menuju penuh, dan ia pekerjaan pengisian data, bukan dev.
4. **Koreksi vonis Tax di [[HRIS - Matriks KPI per Departemen]]** (dua baris "bisa otomatis sekarang" dan satu vonis budget kedaluwarsa). Sudah dikerjakan bersamaan dengan analisa ini.

### ⛔ Menunggu keputusan #5 dan #6

5. **Ajukan keputusan #5 dan #6 ke SPV FAT + Tax Officer.** Bawa konsekuensinya, bukan pertanyaan telanjang: unggah dokumen berarti KPI tetap dinilai manusia; input berstruktur berarti KPI dapat dihitung tetapi menuntut modul baru. Sertakan pola tenggat per jenis pajak sebagai lampiran yang harus mereka isi.
6. **Bila #5 = input berstruktur**: bangun modul Tax mengikuti cetakan **Cost Control Fase 1a** di service yang sama (satu handler + satu berkas sumber KPI). Empat konstanta koleksinya sudah menunggu di `finance/db.go`. Pecah per register, berurutan menurut bobot yang dibuka:
	- **6a. Kewajiban per masa** — daftarkan sebagai **template obligation di calendar-service**, jangan bikin mesin tenggat sendiri. Butuh jawaban #6 (pola tenggat per jenis pajak). Menghidupkan metrik SPT tepat waktu (0,10).
	- **6b. Register temuan** — pakai mesin SLA task-management, plus **helper hari kerja baru** di atas koleksi `holidays`. Menghidupkan metrik tindak lanjut (0,15).
	- **6c. Klasifikasi akun deductible** — master tersendiri; ini satu-satunya yang datanya tidak ada di mana pun hari ini. Menghidupkan sisi deductible metrik #1.
7. **Bila #5 = unggah dokumen**: pakai **modul Laporan form-builder** yang sudah punya unggah + tinjau per butir + tolak + unggah ulang + antrean penyetuju, bukan membangun alur unggah baru. Pekerjaannya tinggal mendefinisikan satu Form bertipe Laporan. **Catat eksplisit bahwa KPI-nya tetap dinilai manusia** supaya tak ada yang mengira otomasi akan menyusul sendiri.
8. **Sepakati definisi "discrepancy rekonsiliasi = 0%"** yang tidak bersandar pada nomor faktur, sebab `taxNumber` tidak tersedia.
9. **Putuskan perlakuan tiga akun PPh jurnal penyesuaian** dalam perhitungan varians (lihat § Yang bisa dipakai ulang). Menyentuh metrik #1 yang dinyalakan di task 1.

### Yang wajib diperiksa saat modulnya dibangun

10. **Modul finance belum punya satu pun izin TULIS**; `finance.pajak.kelola` akan jadi yang pertama, dan layar tulis `/finance/anggaran` yang ada hari ini dijaga izin BACA. Betulkan bersamaan, jangan diwariskan.
11. **`features/finance/` nol berkas memakai `useTranslation`**, sementara [[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]] mewajibkannya untuk teks baru. Halaman `/finance/pajak` akan jadi pulau i18n bila tidak diputuskan sejak awal.
12. **Metrik tanpa data wajib GALAT, bukan nol.** Pada metrik berarah `turun`, nol adalah nilai sempurna. Sudah tergigit sekali di produksi.
13. **Notifikasi H-7/H-3 membawa kategori inbox baru** → service pengirim dan `notification-service` wajib naik bersama, kalau tidak notifikasinya tak pernah tiba tanpa satu pun galat.
14. **Bila memakai file-service langsung**: daftarkan kunci + prefix direktori barunya, kalau tidak seluruh unggah ditolak `invalid access key`. Tidak berlaku bila lewat modul Laporan form-builder.
15. **Rute modul didaftarkan tanpa prefix `/finance`** — gateway sudah membuangnya. Salah taruh = 404 untuk semua permintaan lewat jalur normal sementara unit test tetap hijau.

## Asumsi eksplisit

- **Cakupan `semi` dapat diterima sebagai dasar penilaian.** Metrik varians akan berstatus `semi` selama anggaran belum lengkap. Bila pemilik metrik menolak menilai orang dengan angka bercakupan 28%, task 1 harus menunggu task 3.
- **Kedua Tax Staff dinilai dengan template dan angka yang sama.** Metrik berbasis OPEX dan pajak tidak punya dimensi per orang, persis seperti rumpun AR. Pembeda antar-orang harus datang dari metrik lain.
- **Matriks yang dikirim manajemen adalah yang berlaku**, dan selisih bobot 90 vs 100 dijelaskan oleh metrik Kaizen yang tetap manual.

## Dokumen Terkait

- [[Finance - Rancangan Finance Service]] — rancangan modul Tax, mesin status, dan bab keputusan yang menghentikannya
- [[HRIS - Matriks KPI per Departemen]] — vonis per metrik Tax Staff
- [[HRIS - Otomasi Skor KPI]] — katalog sumber KPI dan konfigurasinya
- [[RUN - Menambah Metrik KPI Otomatis]] — prosedur bila modulnya jadi dibangun
- [[REF - Penamaan Metrik & Sumber KPI]] — aturan label yang dilanggar tiga metrik Tax
- [[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]]
