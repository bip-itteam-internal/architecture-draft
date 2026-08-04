## Deskripsi

*Pengelolaan **jenjang karier, promosi, dan mutasi** karyawan — perubahan posisi/golongan dan perpindahan departemen/lokasi. **Tangga jenjangnya sudah ada** (2026-08-03, lihat [[HRIS - Organization Structure]]); promosi, mutasi, dan riwayatnya belum ada subsistem khusus.*

- **Status**: 🟡 Konsep / Draft — **tangga jenjang sudah di kode**, tapi promosi/mutasi/riwayat belum

## Ruang Lingkup

- **Jenjang karier** — ✅ **tangganya sudah ada** sejak 2026-08-03: lima tingkat (Pelaksana · Senior/Officer · Leader · Supervisor · Direktur) di koleksi `master_job_level`, menempel ke jabatan lewat `position_items[].level_key`. Dikelola di tab **Jenjang Jabatan** pada `/hris/master-data`. Detail desain (rank renggang, larangan jadi sumbu hak akses) di [[HRIS - Organization Structure]]
	- ⚠️ **Baru tangganya, belum isinya**: nol dari 79 jabatan terisi per 2026-08-03
	- **Matriks kompetensi belum ada** dan tetap TBD; jenjang saat ini murni penanda tingkat, tanpa syarat apa pun yang menempel padanya
- **Promosi** — 🟡 belum ada. Kenaikan jenjang saat ini berarti mengubah `level_key` jabatan atau memindahkan orangnya ke jabatan lain, **tanpa** tanggal efektif, alasan, maupun jejak
- **Mutasi** — perpindahan departemen/lokasi/posisi (mis. *Bootcamp Content Creator* yang pindah HR → GA)
- Riwayat perubahan posisi per karyawan (work history)

## Keterkaitan

- Masukan keputusan: [[HRIS - Work Review]] & [[HRIS - Key Performance Index]]
- Eksekusi perubahan data: `work_data` (departemen/posisi/supervisor) di [[Microservices - Employee Service]]
- Berkaitan dengan [[HRIS - Compensation & Benefits]] (dampak gaji) & [[HRIS - Organization Structure]]

## Belum Diputuskan (TBD)

- ~~Definisi jenjang/golongan~~ — **selesai 2026-08-03** (lima tingkat). **Matriks kompetensi masih TBD**
- **Penempatan 79 jabatan ke tingkatnya** — nol terisi; berkas usulan menunggu koreksi HR
- Aturan & syarat promosi; alur **approval** promosi/mutasi
- Dampak ke payroll/komponen gaji — **rentang gaji per jenjang** adalah salah satu alasan utama jenjang dibuat, tapi belum ada apa pun yang menghubungkan keduanya
- Pencatatan riwayat (efektif tanggal, alasan) — sengaja **di luar lingkup** pekerjaan jenjang 2026-08-03 supaya task-nya tak membengkak

## Dependensi / Dokumen Terkait

- [[HRIS - Big Pictures]] · [[HRIS - Analysis]]
- [[HRIS - Work Review]] · [[HRIS - Key Performance Index]] · [[HRIS - Personalia]]
- [[Microservices - Employee Service]]
