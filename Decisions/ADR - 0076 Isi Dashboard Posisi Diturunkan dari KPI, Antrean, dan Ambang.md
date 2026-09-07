## Deskripsi

*Menetapkan dari mana isi dashboard sebuah POSISI diturunkan, dan kapan sebuah posisi sebaiknya **tidak** dibuatkan dashboard sama sekali. Keputusan ini lahir karena isi dashboard selama ini ditentukan per modul oleh siapa pun yang kebetulan membangunnya, tanpa aturan yang bisa dirujuk, sehingga dua divisi menghasilkan bentuk yang berbeda untuk pertanyaan yang sama.*

- **Status**: 🟡 **Berlaku sebagai rancangan** sejak 2026-09-04. Belum ditegakkan test. Dua divisi yang sudah punya dashboard (FAT dan HRGA) dibangun sebelum ADR ini dan sebagian sudah selaras dengannya; penyelarasan sisanya keputusan tersendiri.
- **Path di repo**: `erp-frontend/src/features/finance/posisi/` · `erp-frontend/src/features/hris/dashboard/`
- **Tanggal**: 2026-09-04

## Context

Per 2026-09-04, **54 posisi unik di 10 divisi** memiliki template KPI produksi (`HRIS - Matriks KPI per Departemen`, 311 baris metrik). Yang punya dashboard hanya **17 posisi**: FAT 9 dan HRGA 8. Empat divisi belum tersentuh sama sekali (Kesekretariatan, Manufaktur, Procurement, Quality).

Sebaran sumber metriknya menentukan seluruh keputusan di bawah:

| Divisi | Metrik | Otomatis | Bercatatan | Manual |
|---|---:|---:|---:|---:|
| Tech Development | 30 | 9 | 3 | 18 |
| Finance | 61 | 1 | 14 | 46 |
| Human Resource | 31 | 0 | 5 | 26 |
| Manufaktur | 52 | 0 | 3 | 49 |
| Beauty Hacks | 30 | 0 | 1 | 29 |
| Kyura | 27 | 0 | 1 | 26 |
| Kesekretariatan | 28 | 0 | 1 | 27 |
| General Affair | 24 | 0 | 0 | 24 |
| Quality | 18 | 0 | 1 | 17 |
| Procurement | 10 | 0 | 0 | 10 |
| **TOTAL** | **311** | **10** | **29** | **272** |

**272 dari 311 metrik (87,5%) dinilai manual**, artinya tidak ada angka di sistem yang bisa digambar. Konsekuensinya keras: dashboard yang diturunkan lurus dari KPI akan berisi mayoritas panel kosong untuk hampir semua divisi.

Tiga hal yang sudah terjadi karena tak ada aturannya:

1. **Bentuknya menyimpang antar-divisi.** FAT merender panel "menunggu penyambungan data" bernama hook-nya; HRGA tidak punya padanan itu. Pertanyaan yang sama ("kenapa kotak ini kosong") karena itu dijawab berbeda tergantung layar mana yang sedang dibuka.
2. **Angka nol dibaca sebagai fakta.** Elemen yang datanya belum tersambung, bila dirender sebagai `0`, terbaca "tidak ada transaksi" alih-alih "belum diukur". Ini sudah dicatat sebagai prinsip di [[Finance - Dashboard per Posisi (FAT)]] tetapi berlaku hanya di satu modul.
3. **Tak ada yang menjawab kapan sebuah posisi TIDAK perlu dashboard.** Karena pertanyaannya tak pernah diajukan, jawaban bawaannya jadi "semua posisi perlu", dan itu menghasilkan rencana kerja yang mustahil diselesaikan.

## Decision

### 1. Isi dashboard posisi diturunkan dari TIGA sumbu, bukan dari selera perancang

| Sumbu | Menjawab | Sumbernya |
|---|---|---|
| **KPI yang dinilai** | "saya diukur dari apa" | `kpi_template` posisi itu, sebagaimana tercatat di [[HRIS - Matriks KPI per Departemen]] |
| **Pekerjaan yang menunggu** | "apa yang harus saya kerjakan hari ini" | antrean, tenggat, dan persetujuan dari modul yang sudah berjalan |
| **Ambang yang tak boleh dilewati** | "kapan saya harus bertindak" | target yang benar-benar tertulis di `kpi_template` atau di master data |

Yang **tidak** boleh jadi sumbu: demografi, rekap yang tak menuntut tindakan, dan angka yang menarik tetapi bukan tanggung jawab posisi itu. Halaman Analisis SDM sudah pernah dicabut dari HRGA justru karena isinya demografi yang tak menjawab pertanyaan yang bisa ditindaklanjuti.

### 2. Ambang hanya dipasang bila targetnya memang tertulis

Indikator lulus/gagal dipasang di ambang yang ada di `kpi_template` atau master data. Ambang yang masih parameter manusia tanpa master **tidak** dijadikan lampu lulus/gagal. Aturan ini sudah dijalankan FAT dan di sini diangkat jadi lintas divisi.

Alasannya bukan kerapian: lampu merah yang ambangnya ditebak akan diperlakukan sebagai fakta oleh yang membacanya, dan yang membaca tidak punya cara tahu ambang itu berasal dari mana.

### 3. Metrik tanpa sumber dirender sebagai panel jujur, BUKAN angka nol

Elemen yang hook-nya belum ada dirender sebagai panel bertuliskan apa yang ditunggu, dengan nama hook atau endpoint yang dibutuhkan **terlihat di layar**. Tiap helper grafik mengembalikan keadaan kosong saat datanya `undefined`.

Nama hook sengaja ditampilkan, bukan disembunyikan di komentar kode: ia yang mengubah panel kosong dari keluhan jadi tiket kerja yang bisa langsung dieksekusi.

### 4. Posisi yang seluruh KPI-nya manual DAN tak punya jejak pekerjaan di sistem tidak dibuatkan dashboard

Bukan ditunda, melainkan dinyatakan tidak direkomendasikan, beserta alasannya, sampai sumbernya ada. Dok divisi wajib menuliskannya eksplisit per posisi.

Membuatkan layar untuk posisi seperti ini menghasilkan halaman yang seluruhnya panel menunggu, dan halaman semacam itu mengajari pemakainya bahwa dashboard memang tidak berisi apa-apa. Kerusakan itu menular ke layar lain yang sebenarnya berguna.

**Yang membalikkan keputusan ini untuk sebuah posisi**: munculnya satu sumber angka nyata, atau adanya modul yang mencatat pekerjaan posisi itu (antrean, tenggat, persetujuan). Salah satunya cukup.

### 5. Tata letaknya tunduk pada pedoman layout

Susunan, ukuran, jarak, dan urutan baca mengikuti [[REF - Layout Dashboard erp-frontend]]. ADR ini menentukan **apa** yang tampil; dokumen itu menentukan **bagaimana** menyusunnya. Keduanya tidak boleh saling menyalin.

## Consequences

**Yang didapat.** Isi tiap dashboard bisa ditelusuri ke template KPI yang benar-benar dipakai menilai orangnya, jadi pertanyaan "kenapa angka ini ada di layar saya" punya jawaban yang tidak bergantung pada ingatan perancangnya. Panel jujur mengubah kekurangan backend jadi daftar kerja yang terurut sendiri. Dan pertanyaan "posisi mana yang belum perlu dashboard" akhirnya punya jawaban yang boleh berbunyi "tidak perlu".

**Yang harus diterima.** Dengan 87,5% metrik manual, dok rancangan untuk sebagian besar divisi akan didominasi bagian "menunggu backend". Itu bukan kegagalan rancangan melainkan potret keadaan; yang keliru justru bila doknya terlihat penuh padahal datanya tidak ada.

**Ketergantungan pada satu dokumen.** Seluruh sumbu pertama bersandar pada [[HRIS - Matriks KPI per Departemen]], yang merupakan **salinan** data produksi bertanggal, bukan sumber kebenaran hidup. Bila `kpi_template` berubah, dok rancangan ikut basi tanpa ada yang berbunyi. Karena itu tiap dok divisi wajib mencantumkan tanggal ukur, dan klaim apa pun tentang metrik posisi wajib diukur ulang sebelum dipakai mengambil keputusan.

**Yang tidak diputuskan di sini.** Urutan pembangunan antar-divisi, siapa pemilik tiap layar, dan apakah 17 dashboard yang sudah ada akan diselaraskan mundur ke ADR ini. Ketiganya keputusan tersendiri.

## Dokumen Terkait

- [[REF - Layout Dashboard erp-frontend]] — cara menyusunnya di layar
- [[HRIS - Matriks KPI per Departemen]] — sumber sumbu "KPI yang dinilai"
- [[Finance - Dashboard per Posisi (FAT)]] — pendahulu, tempat prinsip panel jujur lahir
- [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] — model hak akses per posisi
- [[HRIS - Alur KPI Otomatis]] — bagaimana metrik jadi angka
- [[ADR - 0048 Skor KPI Otomatis Penuh Dibekukan Sistem]] — batas kewenangan atas skor otomatis
