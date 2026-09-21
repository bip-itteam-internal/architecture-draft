## Deskripsi

*Peta 25 sheet Dashboard People & Development 2026 ke keadaan ERP hari ini: mana yang sudah ada dan dipakai, mana yang sudah ada tetapi kosong, mana yang belum ada sama sekali, dan mana yang sudah dilampaui ERP. Dibuat supaya penundaan di [[ADR - 0115 Spreadsheet People and Development Belum Dipindah ke ERP, KPI Ganda Diselesaikan Lebih Dulu]] tidak perlu dianalisis ulang dari nol saat dibuka kembali.*

- **Status**: ⚠️ **Salinan bertanggal 2026-09-21**, diukur ke `origin/main` dan prod. Bukan rancangan dan bukan usulan; ini keadaan yang benar-benar ada saat diukur. **Ukur ulang sebelum dipakai mengambil keputusan**, karena isi koleksi berubah tanpa memberi tahu siapa pun.
- **Sumber**: sheet-nya dari analisis mandiri pemilik dokumen (25 sheet, ±170 karyawan, tahun 2026); keadaan ERP dari `git grep` ke `origin/main` dan pembacaan prod baca-saja.
- **Terkait**: [[ADR - 0115 Spreadsheet People and Development Belum Dipindah ke ERP, KPI Ganda Diselesaikan Lebih Dulu]] · [[HRIS - Training Program]] · [[HRIS - Work Review]] · [[HRIS - Career & Promotion]] · [[Microservices - Learning Service]] · [[Microservices - Employee Service]]

## Cara membaca

Empat kategori, dan bedanya penting karena menentukan pekerjaan yang lahir darinya:

| Kategori | Artinya | Pekerjaan yang lahir |
|---|---|---|
| ✅ **Ada dan dipakai** | Koleksinya ada dan terisi di prod | Tidak ada, kecuali menghentikan sumber gandanya |
| ⚠️ **Ada tetapi kosong** | Kodenya lengkap, datanya hampir nol | Pengisian data, bukan kode |
| 🔜 **Belum ada** | Nol berkas di backend | Modul baru, dan butuh keputusan lebih dulu |
| ✅➕ **Dilampaui ERP** | ERP sudah punya bentuk yang lebih baik | Sheet-nya tidak perlu dipindah |

## Peta per sheet

### KPI & Kinerja

| Sheet | Keadaan ERP | Catatan |
|---|---|---|
| TRACKING KPI ALL DIVISI | ✅ Ada dan dipakai | `kpi_score` prod **679 skor**, **108 sampai 165 karyawan per bulan** (April sampai Agustus 2026), `kpi_template` 119, `kpi_template_assignment` 207. ⛔ **Inilah sumber gandanya**: fakta yang sama juga dipelihara di sheet ini |
| AVG KPI DEPARTEMEN | ✅ Ada dan dipakai | Tidak perlu tabel; sudah jadi rekap per departemen di employee-service |
| RESUME KPI ALL DIVISI | ✅ Ada dan dipakai | Sama, rekap hasil hitung |
| KPK | 🔜 Belum ada | `improvement_plan` nol berkas. Yang ada hanya ujungnya, layar `/hris/surat-peringatan`. ⛔ Jalur KPI menuju SP **tidak punya dasar** di Peraturan Perusahaan, lihat ADR 0115 keputusan 3 |

⚠️ **Cakupan kedua sumber KPI berbeda, bukan cuma tempatnya**: ERP tidak punya skor Januari dan Februari 2026, dan Maret hanya 1 orang, sementara sheet memuat Januari sampai Desember.

### Talent Management

| Sheet | Keadaan ERP | Catatan |
|---|---|---|
| Performance & Potential Skor (PE1-5, PO1-5) | 🔜 Belum ada | `talent_assessment` nol |
| Talent Assessment-Mapping (9-box) | 🔜 Belum ada | `nine_box` dan `9-box` nol. [[HRIS - Career & Promotion]] menyatakan kaderisasi **baru desain** |
| TALENT POOL | 🔜 Belum ada | `talent_pool` nol. Bobotnya (KPI 70, training 15, disiplin 15) disimpulkan dari judul kolom, **belum dikonfirmasi**. Skor training butuh modul Training yang hari ini hampir kosong |

Bila kelak dibangun: **kategori 9-box hanya terlihat HR** (keputusan pemilik proses 2026-09-21). Atasan boleh mengisi penilaian tanpa melihat kategori akhirnya.

### Training

| Sheet | Keadaan ERP | Catatan |
|---|---|---|
| TNA & CALENDER | 🔜 Belum ada | `tna` sebagai kata nol. Yang mirip tetapi **bukan**: `training_plan_item` (menu Rencana Pelatihan) hanya berisi bulan, judul, jenis, dan departemen sasaran, tanpa permasalahan, kondisi saat ini versus harapan, gap kompetensi, maupun intervensi |
| CALENDER | ⚠️ Ada tetapi kosong | Tertutup `training` beserta tanggalnya |
| VENDOR TRAINING | 🔜 Belum ada, **sudah diputuskan** | `training_vendor` nol. Sudah jadi T2 di [[ADR - 0109 Penyelenggara Pelatihan Internal atau Eksternal dengan Master Vendor Milik HR dan Bank Sertifikat Dua Sumber]], berstatus 🟡 |
| KEGIATAN INTERNAL | ⚠️ Ada tetapi kosong | `training` + `training_participant`. Prod 13 kelas, 4 baris peserta |
| KEGIATAN EXTERNAL TRAINING | ⚠️ Ada sebagian | Kelas dan peserta ada; kolom "tingkat implementasi pasca training" dan "masa kerja" **tidak ada** |
| REALISASI TRAINING | ⚠️ Ada tetapi kosong | Status kelas dan kehadiran sudah menutupinya |
| RAPORT PENILAIAN PESERTA (pre/post-test) | ⚠️ Ada tetapi kosong | `course`, `quiz`, `quiz_attempt`. Prod `quiz_attempt` **0** |
| SKOR PENILAIAN TRAINING | ⚠️ Ada tetapi kosong | `trainer_evaluation` (empat aspek) plus kesesuaian materi. Prod **1** evaluasi |
| REPORT PERFORMANCE TRAINING VS KPI | ✅➕ Dilampaui ERP | Sudah jadi metrik KPI otomatis `kenaikan_kpi_peserta_persen` ([[ADR - 0102 Kesesuaian Materi Dinilai Peserta dan Dampak Pelatihan dari Kenaikan Skor KPI]]), bukan rekap manual. Sheet ini tidak perlu dipindah |
| BUDGET vs REALISASI TRAINING | ⚠️ Ada sebagian | Kelas punya field `cost`; **tidak ada** anggaran per bulan maupun laporan budget versus realisasi |
| OWNERSHIP LIST | ⚠️ Ada tetapi kosong | Presensi satu kelas, tertutup `training_participant` |
| Pivot Table 7 | ✅➕ Dilampaui ERP | Rata-rata nilai per tema jadi query, bukan tabel |

ERP juga punya yang **tidak ada di spreadsheet**: sertifikat pelatihan terbit otomatis dengan nomor urut per perusahaan per tahun, pengajuan pelatihan beserta persetujuannya, dan penugasan peserta beberapa orang sekaligus berlaporan per orang.

### Program Pengembangan & Referensi

| Sheet | Keadaan ERP | Catatan |
|---|---|---|
| DEVELOPMENT PROGRAM | 🔜 Belum ada | `development_program` nol |
| Bootcamp | 🔜 Belum ada | Kata `bootcamp` memang muncul di kode, tetapi soal **pengecualian KPI**, bukan program rotasi |
| PKL/Magang | 🔜 Belum ada | Kata `magang` muncul sebagai **jenis kontrak PKWT**, bukan modul magang. Sheet-nya sendiri kosong |
| Kamus Kompetensi | 🔜 Belum ada | `kompetensi` dan `competency` nol. Matriks kompetensi masih TBD di dok HRIS |
| SILABUS | 🔜 Belum ada | `silabus` nol |
| RESUME (dashboard) | ⚠️ Ada sebagian | Ada dashboard `/hris` dan KPI, tetapi bukan filter divisi, kegiatan, dan tema seperti di sheet |

## Yang sudah terjawab ERP tanpa perlu dibangun

Analisis aslinya menyebut masalah terbesar spreadsheet adalah **tidak ada kunci karyawan yang konsisten**, sehingga sheet hanya bisa dihubungkan lewat nama. Itu sudah selesai di ERP sejak lama: `employee_id` berformat `BIP-xxxx-mm-yy` adalah kunci di seluruh modul, departemen dan jabatan sudah master data, dan pencocokan lewat nama tidak dipakai di mana pun. Ini alasan terkuat memindahkan sisanya ke ERP kelak, dan sekaligus jawaban atas pertanyaan terbuka "stack apa yang dipakai" di dokumen aslinya.

## Pertanyaan yang masih terbuka

1. **Apakah nilai KPI di spreadsheet dan di ERP cocok?** Belum diketahui. Yang terbukti hanya keduanya terisi. Ini task pertama di [[ANALISA - Spreadsheet People and Development ke ERP]].
2. **Skor kedisiplinan talent pool diambil dari mana?** Diasumsikan dari data kehadiran ERP, belum dikonfirmasi. Pertanyaan ini sudah ditulis pemilik dokumen sendiri.
3. **Bobot talent pool 70/15/15** disimpulkan dari judul kolom, belum dikonfirmasi.
4. **Siapa pengguna dan hak aksesnya** selain HR. Yang sudah diputuskan baru visibilitas 9-box, yaitu hanya HR.
