## Deskripsi

*Pengelolaan **jenjang karier, kaderisasi, promosi, dan mutasi** karyawan — perubahan posisi/golongan dan perpindahan departemen/lokasi. **Tangga jenjangnya sudah ada** (2026-08-03, lihat [[HRIS - Organization Structure]]); promosi, mutasi, dan riwayatnya belum ada subsistem khusus. **Kaderisasi (Talent Pool) sudah punya desain lengkap**, tapi belum ada kodenya.*

- **Status**: ⚠️ Implemented (ada catatan) — **tangga jenjang** dan **modul promosi/mutasi** sudah di kode (yang kedua merged 2026-08-10, belum diverifikasi lewat gateway & belum punya frontend); **kaderisasi** baru desain

## Ruang Lingkup

- **Jenjang karier** — ✅ **tangganya sudah ada** sejak 2026-08-03: lima tingkat (Pelaksana · Senior/Officer · Leader · Supervisor · Direktur) di koleksi `master_job_level`, menempel ke jabatan lewat `position_items[].level_key`. Dikelola di tab **Jenjang Jabatan** pada `/hris/master-data`. Detail desain (rank renggang, larangan jadi sumbu hak akses) di [[HRIS - Organization Structure]]
	- ⚠️ **Baru tangganya, belum isinya**: nol dari 79 jabatan terisi per 2026-08-03
	- **Matriks kompetensi belum ada** dan tetap TBD; jenjang saat ini murni penanda tingkat, tanpa syarat apa pun yang menempel padanya
- **Promosi & Mutasi** — ⚠️ **sudah ada** sejak 2026-08-10, satu modul dan satu koleksi `employee_movement` dibedakan `type` (`Promosi` · `Mutasi` · `Mutasi Antar-Perusahaan`). Menutup kekosongan lama: perpindahan kini punya tanggal efektif, alasan, dokumen SK, dan jejak yang bisa dibatalkan. Keputusannya di [[ADR - 0044 Mutasi Antar-Tenant Mempertahankan employee_id]], rincian teknis di [[Microservices - Employee Service]]
	- **Termasuk perpindahan ANTAR-PERUSAHAAN** (BIP ↔ ELT), dan `employee_id` sengaja **tidak** diterbitkan ulang supaya riwayat presensi/KPI/cuti/payroll tak terputus. Konsekuensinya prefix ID berhenti menandakan perusahaan
	- **Jenis dipilih HR, tidak disimpulkan dari jenjang** — nol dari 79 jabatan berjenjang, jadi menyimpulkannya berarti menyimpulkan dari data kosong
	- **Layar**: menu HRIS → Personalia → **Promosi & Mutasi** (`/hris/mutasi`), lengkap dengan panel detail bergambar sebelum → sesudah dan lampiran SK
	- **Pemberitahuan** dikirim saat perpindahan benar-benar diterapkan: ke karyawannya, dan untuk perpindahan lintas tenant juga ke supervisor HR perusahaan tujuan
	- ⚠️ **Approval sengaja DITUNDA** (2026-08-10), sehingga perusahaan tujuan tidak punya suara atas karyawan yang didorong masuk. Lingkupnya sudah ditetapkan untuk kelak: hanya perpindahan antar-perusahaan yang akan digerbang. Sampai itu ada, notifikasi ke HR tujuan adalah **penambal**, bukan pelengkap
	- **Masa kerja, kuota cuti, dan BPJS IKUT PINDAH apa adanya** saat ganti badan usaha (keputusan HR 2026-08-10, **sementara**). Modul ini karena itu tak menyentuh ketiganya, dikunci uji
	- **Kontrak kerja baru wajib tapi tidak dibuat sistem**: nomor, jenis, dan dokumen bertanda tangan tak bisa diturunkan dari data perpindahan. HR tujuan diingatkan lewat pemberitahuan yang sama
	- ⚠️ **Belum diverifikasi lewat gateway hidup**, prod belum di-deploy
- **Kaderisasi / Talent Pool** — 🟡 desainnya lengkap, kodenya belum ada. Pencatatan calon penerus jabatan beserta kesiapannya, dirancang sebagai Fase 2 LMS di [[Microservices - Learning Service]]. Rinciannya di bagian **Kaderisasi & Talent Pool** di bawah
- **Mutasi** — perpindahan departemen/lokasi/posisi (mis. *Bootcamp Content Creator* yang pindah HR → GA)
- Riwayat perubahan posisi per karyawan (work history)

## Kaderisasi & Talent Pool (desain, belum ada kode)

Kaderisasi di ERP dirancang **bukan** sebagai modul berdiri sendiri, melainkan sebagai lensa baca di atas data belajar: karyawan yang disiapkan naik jabatan mengerjakan kurikulum **jabatan tujuan**, dan nilainya jadi bahan pertimbangan. Desain lengkapnya ada di `erp/docs/superpowers/specs/2026-08-05-lms-people-development-design.md` bagian *Talent Pool (Fase 2)*; yang dirangkum di sini adalah keputusan yang mengikat modul karier.

**Kenapa dicatat di sini, bukan di [[HRIS - Training Program]]**: pelatihan cuma alat ukurnya, sedangkan yang dikelola adalah perpindahan jenjang. Talent Pool memakai kurikulum sebagai bukti kesiapan, bukan sebaliknya.

**Lubang yang ditutupnya**: [[HRIS - Matriks KPI per Departemen]] memuat KPI HR *"Succession Planning Terimplementasi, menyusun Kaderisasi & Talent Pool"* dengan catatan apa adanya bahwa modulnya tidak ada dan calon penerus jabatan belum tercatat di mana pun.

### Prasyarat: dua dari tiga sudah terjawab

[[HRIS - Work Review]] menunda Succession Planning karena tiga prasyarat kosong, yaitu org chart, jenjang jabatan, dan matriks kompetensi.

- **Jenjang jabatan** — tangganya ada sejak 2026-08-03, tapi ⚠️ **isinya masih nol dari 79 jabatan** (masih nol saat desain LMS ditulis, 2026-08-05)
- **Matriks kompetensi** — desain LMS mengklaim menjawabnya: **kurikulum per jabatan adalah matriks kompetensi** dalam bentuk yang bisa dipakai
- **Org chart** — lihat [[HRIS - Organization Structure]]

Akibat jenjang yang belum terisi: sistem **tidak tahu** jabatan mana di atas jabatan mana, dan **tidak boleh menebaknya**. HR yang menunjuk kandidat beserta jabatan tujuannya. Saran kandidat otomatis berdasarkan jenjang baru mungkin setelah 79 jabatan itu terisi.

### Alur

1. **Atasan mengusulkan** bawahannya untuk jabatan tujuan tertentu, dengan catatan alasan. Status `diusulkan`
2. **HR menyetujui atau menolak.** Persetujuan HR menjaga kriteria seragam antar departemen; tanpa itu tiap atasan memakai standar sendiri dan talent pool jadi tak bisa dibandingkan
3. Setelah `disetujui`, kandidat mendapat kurikulum jabatan tujuan sebagai kurikulum pengembangan, **dan baru pada titik ini kandidat mengetahuinya**. Usulan berstatus `diusulkan` dan `ditolak` tak pernah terlihat kandidat, supaya penolakan tidak jadi kekecewaan yang diumumkan sistem
4. Sistem menghitung **syarat belajar terpenuhi**: seluruh course wajib kurikulum tujuan selesai dan rata-rata nilainya mencapai `talent_min_average` (usulan bawaan 75, lebih tinggi dari nilai kelulusan biasa)
5. **HR atau atasan menetapkan status `siap`.** Sistem tidak pernah menetapkannya sendiri
6. Bila promosi terjadi, status jadi `dipromosikan`

### Yang dihitung sistem dan yang tidak

Sistem menghitung yang objektif: persen penyelesaian kurikulum tujuan, nilai rata-rata, dan penanda syarat belajar terpenuhi. Sistem **tidak** menyimpulkan layak atau tidak layak.

Pemisahan ini disengaja. "Syarat belajar terpenuhi" bisa dihitung; "layak dipromosikan" melibatkan sikap, kesiapan memimpin, dan ada tidaknya kursi yang kosong, yang tak satu pun ada di data mana pun. Sistem yang mengeluarkan putusan layak akan membuat keputusan HR yang berbeda tampak seperti melawan sistem, padahal justru HR yang memegang informasi yang tidak dimiliki sistem.

### Model data (usulan, di service `learning`)

Koleksi baru **`talent_candidate`**: `{ company_id, employee_id, target_department_key, target_position_key, status, nominated_by, nominated_at, nomination_note, approved_by, approved_at, decided_by, decided_at, decision_note }`.

Status: `diusulkan | disetujui | siap | dipromosikan | ditolak | batal`. Transisinya divalidasi fungsi murni (`diusulkan` ke `disetujui`/`ditolak`; `disetujui` ke `siap`/`batal`; `siap` ke `dipromosikan`/`batal`; tiga terakhir terminal), mengikuti pola `IsValidStatusTransition` yang sudah ada di modul Training.

> **Nyaris tanpa model baru.** Progres melekat pada pasangan karyawan dan course, sedangkan kurikulum hanyalah lensa baca di atasnya. Memberi kandidat kurikulum jabatan tujuan karena itu tak mengubah satu baris pun data progres. Efek sampingnya menyenangkan: begitu kandidat benar-benar dipromosikan dan jabatannya berubah di `work_data`, kurikulum jabatan barunya langsung menjadi kurikulum wajibnya, dan course yang sudah dia selesaikan tetap terhitung selesai tanpa migrasi apa pun.

### Batas dengan Promosi

Talent Pool mencatat **persiapan**, bukan **perpindahan**. Status `dipromosikan` hanya menutup catatan kandidat: ia tidak mencatat posisi lama, posisi baru, tanggal efektif, maupun dokumen keputusan, dan **tidak menulis apa pun ke `work_data`**.

Batas itu disengaja. `work_data` milik [[Microservices - Employee Service]], dan menaruh penulisannya di `learning` melanggar [[ADR - 0002 Database-per-Service]] sekaligus menciptakan dua tempat yang bisa mengubah jabatan orang. Selama modul promosi belum ada, promosi kandidat tetap dikerjakan manual seperti sekarang, dan Talent Pool cuma menyimpan bahwa keputusannya sudah diambil.

Bila modul promosi dibangun nanti, polanya **tidak perlu meniru ERPGo**: ERP sudah punya pola yang lebih baik di rumah sendiri, yaitu modul Resign yang memisahkan `scheduled` dari `applied` lalu menerapkannya lewat cron harian yang idempoten. Dari ERPGo yang layak diambil cuma dua, yaitu snapshot posisi lama disimpan permanen (bukan diturunkan dari catatan sebelumnya) dan visualisasi sebelum-sesudah di layar detail.

### Antarmuka

Menu **Talent Pool** di `/hris/learning/talent` (baru, Fase 2): usulan kandidat dari atasan, persetujuan HR, dan kesiapan tiap kandidat terhadap kurikulum jabatan tujuannya.

## Keterkaitan

- Masukan keputusan: [[HRIS - Work Review]] & [[HRIS - Key Performance Index]]
- Bukti kesiapan kaderisasi (kurikulum & nilai): [[Microservices - Learning Service]] · [[HRIS - Training Program]]
- Eksekusi perubahan data: `work_data` (departemen/posisi/supervisor) di [[Microservices - Employee Service]]
- Berkaitan dengan [[HRIS - Compensation & Benefits]] (dampak gaji) & [[HRIS - Organization Structure]]

## Belum Diputuskan (TBD)

- ~~Definisi jenjang/golongan~~ — **selesai 2026-08-03** (lima tingkat). **Matriks kompetensi masih TBD**; usulan terkini menjadikan **kurikulum jabatan** sebagai bentuk pakainya (lihat Kaderisasi & Talent Pool), tapi belum diputuskan maupun dibangun
- **Penempatan 79 jabatan ke tingkatnya** — nol terisi; berkas usulan menunggu koreksi HR. Ini juga yang menghalangi saran kandidat otomatis di Talent Pool
- **Angka bawaan Talent Pool** — `talent_min_average` baru **usulan** 75, belum ditetapkan HR
- ~~**Modul Promosi** — ditunda sebagai spec terpisah~~ — **dibangun 2026-08-10**, lihat §Ruang Lingkup & [[ADR - 0044 Mutasi Antar-Tenant Mempertahankan employee_id]]
- **Prasyarat belajar perpindahan** — diputuskan 2026-08-10: naik jabatan/pindah posisi menuntut **lulus post-test seluruh course wajib kurikulum jabatan TUJUAN**. Yang diukur **course, bukan kehadiran kelas**; jalur belajarnya bebas (mandiri atau tatap muka), post-test yang menentukan. Pondasinya sudah terpasang di [[Microservices - Employee Service]] (`DaftarkanPrasyarat`); pemeriksanya menunggu LMS Fase 1 ([[Microservices - Learning Service]]).
	- ⚠️ **Belum diputuskan**: jabatan yang belum punya kurikulum — lolos (tak ada syarat) atau tertahan? Bukan kasus pinggiran: pada hari LMS menyala, mayoritas dari 79 jabatan belum punya kurikulum, jadi memilih "tertahan" akan membekukan seluruh pencatatan mutasi sekaligus
- Alur **approval** perpindahan — **ditunda sadar** 2026-08-10, bukan terlupa. Lingkupnya sudah ditetapkan (hanya antar-perusahaan); yang belum adalah siapa penyetujunya. Tetap yang paling mendesak, sebab modulnya sudah jalan tanpa persetujuan siapa pun
- ~~**Masa kerja, kuota cuti, dan BPJS saat pindah badan usaha**~~ — **diputuskan 2026-08-10**: ketiganya ikut pindah apa adanya, **sementara**. Perlu ditinjau ulang bila pesangon lintas-entitas jadi persoalan, sebab masa kerja yang berjalan terus berarti perhitungannya memakai tanggal masuk di perusahaan lama
- Aturan & syarat promosi (kapan seseorang layak naik) — masih terbuka, dan bergantung pada matriks kompetensi yang juga belum ada
- Dampak ke payroll/komponen gaji — **rentang gaji per jenjang** adalah salah satu alasan utama jenjang dibuat, tapi belum ada apa pun yang menghubungkan keduanya
- Pencatatan riwayat (efektif tanggal, alasan) — sengaja **di luar lingkup** pekerjaan jenjang 2026-08-03 supaya task-nya tak membengkak

## Dependensi / Dokumen Terkait

- [[HRIS - Big Pictures]] · [[HRIS - Analysis]]
- [[HRIS - Work Review]] · [[HRIS - Key Performance Index]] · [[HRIS - Personalia]]
- Kaderisasi: [[HRIS - Training Program]] · [[Microservices - Learning Service]] · [[HRIS - Matriks KPI per Departemen]] · [[ADR - 0002 Database-per-Service]]
- [[Microservices - Employee Service]]
