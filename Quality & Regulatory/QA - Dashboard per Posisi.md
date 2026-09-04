## Deskripsi

*Rancangan isi dashboard per posisi untuk divisi **Quality**, empat posisi. Diturunkan mengikuti [[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]].*

- **Status**: 🟡 **Rancangan**. Tak satu pun posisi di divisi ini punya lembar dashboard.
- **Angka KPI diukur 2026-08-28** (sumber: [[HRIS - Matriks KPI per Departemen]]). **Ukur ulang sebelum dipakai mengambil keputusan.**

## Temuan utama: dua penghambat mengunci 10 dari 18 metrik

| Penghambat | Metrik | Posisi |
|---|---:|---|
| **Batch Record & Production Log ada di kode tapi KOSONG di prod (0 dokumen)** | 6 | keempatnya |
| Tidak ada tracker audit internal / CAPA / izin BPOM | 4 | keempatnya |
| Belum dipetakan sama sekali | 4 | keempatnya |
| Punya sumber | 4 | QC Assistant, QC Production, Quality Supervisor, QA Leader |

⚠️ **Batch Record adalah kasus "fitur ada, data nol", bukan "fitur belum dibangun".** Koleksinya sudah ada di kode dan `batch_record` bahkan sudah punya `TglSelesaiOlah`, `DiajukanAt`, dan `DisetujuiAt`, yaitu persis tiga stempel waktu yang dibutuhkan menghitung QA release time. Yang tidak ada adalah isinya.

Bedanya menentukan urutan kerja: ini bukan permintaan fitur ke tim pengembang melainkan pertanyaan ke tim produksi tentang kenapa modulnya tidak dipakai. Kelas yang sama sudah dicatat untuk modul Training di [[HRIS - Dashboard per Posisi]] dan onboarding di divisi Recruitment.

## Quality Supervisor

**Dinilai dari** (template `KPI Quality Supervisor`, 5 metrik):

| Bobot | Metrik | Sumber | Keadaan |
|---:|---|---|---|
| 0,3 | Performance Monitoring Team, skor min. 70 | `skor_tim`, `rata_rata`, scope `department` | ✅ mesin siap |
| 0,25 | Zero complain, maks 15/bulan | belum dipetakan | ❌ |
| 0,15 | QA release time ≤ 24 jam | `batch_record`, koleksi kosong | ❌ |
| 0,15 | Defect rate maks 2% | batch record, koleksi kosong | ❌ |
| 0,15 | Zero major finding audit BPOM | tidak ada tracker | ❌ |

**Bisa ditampilkan sekarang.** Satu metrik, berbobot 0,3, dan itu yang tertinggi di posisi ini.

- **Visual utama**: sebaran skor KPI anggota divisi Quality terhadap ambang 70.
- Tidak ada kandidat kedua. Jangan mengisi sisanya dengan panel menunggu berjajar; satu kartu bermakna lebih baik daripada satu kartu bermakna ditemani empat kotak kosong.

## QA Leader

**Dinilai dari** (template `KPI QA Staff`, 4 metrik):

| Bobot | Metrik | Sumber | Keadaan |
|---:|---|---|---|
| 0,4 | QA release time < 20 jam sejak dokumen diterima | batch record, koleksi kosong | ❌ |
| 0,25 | Audit area QC, produksi, penyimpanan 2x/bulan | tidak ada tracker | ❌ |
| 0,2 | Review kesesuaian SOP & WI, 5 produk/bulan | butuh sumber baru | ❌ |
| 0,15 | Testing alat ukur bulanan sesuai jadwal | belum dipetakan | ❌ |

⛔ **Nol dari empat metrik punya sumber.** Tidak direkomendasikan dibuatkan dashboard sekarang.

⚠️ **Metrik berbobot 0,2 bernama `Kaizen dan Growth` TIDAK dilayani sumber Kaizen**, meski namanya menyebutnya. Yang diukur adalah jumlah review SOP dan WI per bulan, bukan ide perbaikan. Menyambungkannya ke `kaizen_ide_diajukan` akan menghitung hal yang sama sekali lain, dan namanya membuat kekeliruan itu terasa benar. Kelas yang sama dengan salah petak yang tercatat di [[GA - Dashboard per Posisi]].

**Yang membalikkan keputusan ini**: batch record terisi. Satu hal itu langsung memberi posisi ini metrik terbesarnya (0,4).

## QC Assistant

**Dinilai dari** (template `KPI QC Assistant`, 4 metrik):

| Bobot | Metrik | Sumber | Keadaan |
|---:|---|---|---|
| 0,3 | Pengecekan bahan kemas selesai sebelum tenggat retur supplier, maks 3 hari | `accurate_daily_returns` (3.351) + `shopee_returns` (271) + `GET /daily-returns/stats` | ✅ |
| 0,3 | Persentase bahan kemas diluluskan QC | batch record, koleksi kosong | ❌ |
| 0,3 | Zero major finding audit BPOM | tidak ada tracker | ❌ |
| 0,1 | Kemampuan multi-tasking | belum dipetakan | ❌ |

**Bisa ditampilkan sekarang.** Satu metrik berbobot 0,3, dan datanya tebal.

- **Visual utama**: umur retur yang belum tuntas terhadap tenggat 3 hari, bukan cacahnya. Metriknya mengukur ketepatan waktu, jadi yang harus terbaca sekali lihat adalah **mana yang hampir lewat**, bukan berapa banyak.
- Daftar retur yang mendekati tenggat, diurutkan sisa hari. Ini sumbu "pekerjaan yang menunggu" yang benar untuk posisi ini.

## QC Production

**Dinilai dari** (template `KPI Quality Staff - Production`, 5 metrik):

| Bobot | Metrik | Sumber | Keadaan |
|---:|---|---|---|
| 0,25 | Dokumen catatan pengujian maks 12 jam setelah CPPB | batch record, koleksi kosong | ❌ |
| 0,25 | In-Process Control tiap tahap, 100% berhasil | batch record, koleksi kosong | ❌ |
| 0,2 | Zero major finding audit BPOM | tidak ada tracker | ❌ |
| 0,15 | Komplain kualitas dari Marketing maks 12/bulan | belum dipetakan | ❌ |
| 0,15 | Incoming inspection raw material, laporan maks 3 hari | `inventory_db.inventory` 134 item | ⚠️ |

⛔ **Praktis tidak dapat dirancang sekarang.** Satu-satunya yang punya sumber bertumpu pada `inventory_db` yang riwayat perbaikannya kosong dan stok opnamenya belum ada, jadi ia pun setengah tersedia.

**Yang membalikkan keputusan ini**: batch record terisi, membuka bobot 0,5 sekaligus.

## Kebutuhan backend, terurut

1. **Isi Batch Record & Production Log di produksi.** Satu pekerjaan yang membuka 6 metrik di keempat posisi, termasuk metrik terbesar QA Leader (0,4) dan separuh bobot QC Production. Daya ungkit tertinggi di divisi ini, dan **kemungkinan besar bukan pekerjaan kode**: koleksinya sudah ada beserta stempel waktunya, yang kurang pemakaiannya.
2. **Tracker audit internal / CAPA / izin BPOM.** Mengunci 4 metrik, satu di tiap posisi. Bersinggungan dengan [[QA - Quality Operasional (CAPA, Incoming, Batch Release)]] dan [[QA - Register Perizinan & Sertifikasi]] yang sudah punya konsepnya di vault.
3. **Sumber untuk review SOP & WI** milik QA Leader. Jangan dipetakan ke Kaizen meski namanya menyebutnya.
4. **Pemetaan metrik komplain** (Quality Supervisor 0,25, QC Production 0,15). Keduanya soal komplain tetapi belum dipetakan sama sekali, dan bobot gabungannya 0,4.
5. **Riwayat dan stok opname aset** di `inventory_db`, dipakai bersama dengan [[GA - Dashboard per Posisi]].

## Dokumen Terkait

- [[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]] — prinsip penurunannya
- [[REF - Layout Dashboard erp-frontend]] — cara menyusunnya di layar
- [[HRIS - Matriks KPI per Departemen]] — sumber angka di dokumen ini
- [[QA - Quality Operasional (CAPA, Incoming, Batch Release)]] — modul untuk metrik audit dan release
- [[QA - Register Perizinan & Sertifikasi]] — konteks izin BPOM
- [[QA - CPOB (GMP)]] — standar yang mendasari metrik audit
- [[Manufacture - Dashboard per Posisi]] — divisi yang berbagi sumber batch record
