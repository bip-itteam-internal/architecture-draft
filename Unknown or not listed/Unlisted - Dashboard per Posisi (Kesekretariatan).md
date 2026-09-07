## Deskripsi

*Rancangan isi dashboard per posisi untuk divisi **Kesekretariatan**, tujuh posisi. Diturunkan mengikuti [[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]]. Ditaruh di `Unknown or not listed` karena divisi ini tidak punya padanan domain di vault: isinya bercampur sekretariat, branding, desain, audit internal, dan R&D regulatory.*

- **Status**: 🟡 **Rancangan**. Tak satu pun posisi di divisi ini punya lembar dashboard.
- **Angka KPI diukur 2026-08-28** (sumber: [[HRIS - Matriks KPI per Departemen]]). **Ukur ulang sebelum dipakai mengambil keputusan.**

## Temuan utama: divisi paling tidak terukur di perusahaan

**Dua dari 28 metrik punya sumber. Lima dari tujuh posisi punya NOL.**

| Posisi | Metrik | Bersumber | Rancangan |
|---|---:|---:|---|
| QA RND | 4 | 1 | 🟡 terbatas |
| Internal Audit | 5 | 1 | 🟡 terbatas |
| Company Branding | 4 | 0 | ⛔ tidak direkomendasikan |
| Corporate Secretary | 4 | 0 | ⛔ tidak direkomendasikan |
| Graphic Design | 3 | 0 | ⛔ tidak direkomendasikan |
| Personal Assistant | 4 | 0 | ⛔ tidak direkomendasikan |
| Video Editor | 4 | 0 | ⛔ tidak direkomendasikan |

Ini bukan kelalaian dokumentasi. Pekerjaan divisi ini sebagian besar **tidak melewati sistem sama sekali**: menyiapkan bahan untuk Direktur, menggarap desain, mengunggah konten ke akun organik perusahaan, menyusun izin BPOM. Tidak ada jejaknya untuk dibaca, dan menambahkan dashboard tidak akan menciptakannya.

## Yang punya sumber

### QA RND

**Dinilai dari** (template `R&D REGULATORY`, 4 metrik):

| Bobot | Metrik | Sumber | Keadaan |
|---:|---|---|---|
| 0,4 | Product Development Support | Accurate proxy (`/accounting/profit-loss`, `/balance-sheet`) | ⚠️ |
| 0,25 | Inovasi & efisiensi produk | butuh sumber baru | ❌ |
| 0,25 | Izin BPOM & Halal sebelum deadline launching | tidak ada tracker | ❌ |
| 0,1 | Zero major finding audit BPOM | tidak ada tracker | ❌ |

**Bisa ditampilkan sekarang.** Satu metrik berbobot 0,4, tetapi dengan keberatan yang harus disebut: sumbernya laba rugi **perusahaan**, sementara metriknya menilai dukungan pengembangan produk. Hubungannya jauh, dan angka yang keluar akan bergerak karena sebab yang tak ada kaitannya dengan pekerjaan posisi ini.

⚠️ **Metrik `Inovation & Improvement` bukan dilayani sumber Kaizen** meski redaksinya menyebut inovasi. Sama dengan `Kaizen dan Growth` di QA Leader ([[QA - Dashboard per Posisi]]): namanya membuat pemetaan yang keliru terasa benar.

**Rekomendasi**: tunda sampai tracker izin BPOM berdiri. Dua metriknya (total 0,35) menunggu hal yang sama, dan bersama-sama itu lebih berarti daripada satu metrik keuangan yang hubungannya renggang.

### Internal Audit

**Dinilai dari** (template `INTERNAL AUDIT`, 5 metrik):

| Bobot | Metrik | Sumber | Keadaan |
|---:|---|---|---|
| 0,25 | Ketepatan monitoring & follow up (closing finding rate) | sebagian tak terdefinisi tanpa modul | ❌ |
| 0,25 | Kelengkapan laporan & kejelasan rekomendasi | `GET /attendance/report`, 24.163 entri | ⚠️ salah petak |
| 0,2 | Akurasi & validitas data laporan lintas divisi, error ≤ 2% | belum dipetakan | ❌ |
| 0,15 | Kepatuhan implementasi kebijakan Direktur | belum dipetakan | ❌ |
| 0,15 | Efektivitas kontrol & deteksi issue | belum dipetakan | ❌ |

⚠️ **Satu-satunya metrik bersumber di posisi ini dipetakan ke data ABSENSI.** Metriknya menilai kelengkapan laporan audit dan kejelasan rekomendasi; sumbernya kehadiran dan keterlambatan. Keduanya tidak berhubungan. Ini salah petak, bukan sumber yang tersedia.

🟡 **Yang berubah dalam waktu dekat.** Modul Audit Internal sedang dipisah jadi service dan aplikasi sendiri ([[ADR - 0074 Audit Internal Dipisah jadi Service dan Aplikasi Sendiri]], [[ADR - 0073 Modul Audit Internal di finance-service dan Kertas Kerja yang Dipegang Sendiri]]). Begitu ia berjalan, **temuan dan penutupannya akan tercatat**, dan metrik closing finding rate berbobot 0,25 punya sumber alaminya. Posisi ini karena itu satu-satunya di divisi ini yang **jaraknya memendek sendiri** tanpa pekerjaan tambahan.

**Rekomendasi**: rancang lembarnya bersamaan dengan modul Audit Internal, bukan sekarang dan bukan terpisah.

## Yang tidak direkomendasikan dibuatkan dashboard

### Company Branding

⛔ Tiga dari empat metriknya, bobot 0,85, menunggu satu hal: **akun Instagram dan TikTok organik perusahaan tidak terintegrasi.** Yang tersambung hanya TikTok Business/Shop, Shopee, Lazada, dan Accurate, yaitu kanal jualan, bukan akun korporat.

⚠️ **Jangan menambalnya dengan data TikTok Shop yang tebal itu.** Engagement rate akun korporat dan performa iklan marketplace adalah dua hal berbeda; angkanya akan mulus dan menjawab pertanyaan lain. Kelas yang sama sudah dicatat untuk Video Editor di [[Sales - Dashboard per Posisi (Beauty Hacks & Kyura)]].

### Graphic Design dan Video Editor

⛔ **Nol dari tujuh metrik** di kedua posisi, semuanya menunggu satu hal yang sama: **tidak ada tracker garapan desain dan video** (pengajuan, persetujuan, tenggat).

Perlu ditegaskan karena godaannya besar: metrik kedua posisi ini menilai **mutu dan ketepatan garapan**, bukan performa hasilnya di marketplace. Targetnya berbunyi "disetujui pengaju dan diserahkan 1 hari setelah form pengajuan ditandatangani". Yang dibutuhkan alur pengajuan bertenggat, bukan angka tayangan.

⚠️ Posisi Video Editor ada **dua kali di perusahaan** dengan template berbeda: `VIDEOGRAPHER & EDITOR COMPANY` di sini dan `VIDEO EDITOR` di Beauty Hacks. Keduanya terkunci pada tracker yang sama, jadi satu modul melayani keduanya.

### Corporate Secretary dan Personal Assistant

⛔ **Nol dari delapan metrik** di kedua posisi. Keduanya berpusat pada hal yang sama: agenda Direktur, penyelesaian instruksi Direktur, dan penyiapan bahan untuk Direktur.

🟡 **Ada kandidat yang layak diperiksa, dan sengaja ditulis sebagai kandidat, bukan sebagai temuan.** Dua modul yang sudah berjalan menyentuh wilayah ini: [[Microservices - Calendar Service]] menyimpan agenda mandiri di koleksi `calendar_events`, dan [[Microservices - Task Management Service]] mencatat penugasan bertenggat. Metrik "agenda berjalan tanpa bentrok" dan "tugas Direktur selesai tepat waktu" **mungkin** bisa diturunkan dari keduanya.

Kenapa tetap tidak direkomendasikan sekarang: matriks KPI menyatakan kedelapan metrik itu **belum dipetakan**, dan memetakannya adalah keputusan pemilik KPI yang menuntut memeriksa apakah agenda Direktur benar-benar dicatat di kalender dan instruksinya benar-benar dibuat sebagai task. Bila ternyata tidak, sumbernya ada tetapi kosong, dan itu keadaan yang sama dengan Batch Record di [[QA - Dashboard per Posisi]].

⚠️ Satu metrik Personal Assistant (`Responsivitas & Kerahasiaan`, 0,15) dipetakan ke **data percakapan CS marketplace**. Itu salah petak yang jelas: kecepatan respon asisten kepada Direktur tak ada hubungannya dengan chat pembeli.

## Kebutuhan backend, terurut

1. **Tracker garapan desain dan video** (pengajuan, persetujuan, tenggat). Membuka 7 metrik di 2 posisi di divisi ini, plus 3 metrik Video Editor Beauty Hacks. Total 10 metrik lintas divisi, daya ungkit tertinggi di dokumen ini.
2. **Selesaikan modul Audit Internal** yang sudah diputuskan dua ADR. Memberi Internal Audit metrik terbesarnya tanpa pekerjaan tambahan.
3. **Periksa kelayakan Calendar Service dan Task Management** sebagai sumber untuk Corporate Secretary dan Personal Assistant. Pemeriksaan dulu, bukan implementasi: yang harus dijawab apakah agenda dan instruksi Direktur benar-benar tercatat di sana.
4. **Tracker izin BPOM & Halal** untuk QA RND, dipakai bersama [[QA - Dashboard per Posisi]].
5. **Perbaiki tiga salah petak**: Internal Audit ke data absensi, Personal Assistant ke chat marketplace, QA RND `Inovation` ke Kaizen.
6. **Integrasi akun organik Instagram dan TikTok perusahaan** untuk Company Branding. Pekerjaan terbesar, cakupan satu posisi.

## Dokumen Terkait

- [[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]] — prinsip penurunannya
- [[REF - Layout Dashboard erp-frontend]] — cara menyusunnya di layar
- [[HRIS - Matriks KPI per Departemen]] — sumber angka di dokumen ini
- [[ADR - 0074 Audit Internal Dipisah jadi Service dan Aplikasi Sendiri]] · [[ADR - 0073 Modul Audit Internal di finance-service dan Kertas Kerja yang Dipegang Sendiri]] — modul yang memendekkan jarak Internal Audit
- [[Finance - Audit Internal]] · [[APP - Audit Internal]] — modul Audit Internal
- [[Microservices - Calendar Service]] · [[Microservices - Task Management Service]] — kandidat sumber agenda dan instruksi Direktur
- [[QA - Dashboard per Posisi]] — berbagi kebutuhan tracker BPOM
- [[Sales - Dashboard per Posisi (Beauty Hacks & Kyura)]] — berbagi kebutuhan tracker garapan video
