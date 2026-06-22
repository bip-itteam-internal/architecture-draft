## Deskripsi

*Pengelolaan **jenjang karier, promosi, dan mutasi** karyawan — perubahan posisi/golongan dan perpindahan departemen/lokasi. Saat ini belum ada subsistem khusus; data posisi/departemen tersimpan di [[Microservices - Employee Service]].*

- **Status**: 🟡 Konsep / Draft (belum ada subsistem khusus di kode)

## Ruang Lingkup

- **Jenjang karier** — peta posisi/golongan per departemen (referensi: `PositionTitle*` per departemen di employee-service)
- **Promosi** — kenaikan posisi/golongan (dengan dasar penilaian)
- **Mutasi** — perpindahan departemen/lokasi/posisi (mis. *Bootcamp Content Creator* yang pindah HR → GA)
- Riwayat perubahan posisi per karyawan (work history)

## Keterkaitan

- Masukan keputusan: [[HRIS - Work Review]] & [[HRIS - Key Performance Index]]
- Eksekusi perubahan data: `work_data` (departemen/posisi/supervisor) di [[Microservices - Employee Service]]
- Berkaitan dengan [[HRIS - Compensation & Benefits]] (dampak gaji) & [[HRIS - Organization Structure]]

## Belum Diputuskan (TBD)

- Definisi jenjang/golongan & matriks kompetensi
- Aturan & syarat promosi; alur **approval** promosi/mutasi
- Dampak ke payroll/komponen gaji
- Pencatatan riwayat (efektif tanggal, alasan)

## Dependensi / Dokumen Terkait

- [[HRIS - Big Pictures]] · [[HRIS - Analysis]]
- [[HRIS - Work Review]] · [[HRIS - Key Performance Index]] · [[HRIS - Personalia]]
- [[Microservices - Employee Service]]
