## Deskripsi

*Kompensasi & benefit karyawan — komponen gaji, BPJS, pajak (PPh21), tunjangan, serta bonus/lembur/insentif. Melengkapi [[HRIS - Payroll]] (proses penggajian) dengan rincian komponen & benefit yang belum terdokumentasi.*

- **Status**: 🟡 Konsep / Draft

## Ruang Lingkup

- **Komponen gaji**: gaji pokok, tunjangan tetap/tidak tetap, potongan
- **BPJS**: Kesehatan & Ketenagakerjaan (data BPJS dikelola di [[HRIS - Personalia]] / [[Microservices - Employee Service]])
- **Pajak PPh21** — perhitungan & pelaporan (**belum** terdokumentasi)
- **Benefit** lain: THR, tunjangan kesehatan, dll
- **Variabel**: lembur ([[HRIS - Overtime]]), insentif ([[Sales - Incentive]] / [[Finance - Incentive]])

## Keterkaitan

- Diproses oleh [[HRIS - Payroll]] (yang menarik jam kerja/telat/lembur/cuti dari attendance `payroll-supplement`)
- Komponen dasar (kontrak/BPJS) dari [[HRIS - Personalia]]

## Belum Diputuskan (TBD)

- Struktur komponen gaji & golongan (kaitan [[HRIS - Career & Promotion]])
- Metode perhitungan **PPh21** (TER/PTKP) & pelaporan pajak
- Daftar tunjangan/benefit resmi + aturannya
- Slip gaji: komponen yang ditampilkan

## Dependensi / Dokumen Terkait

- [[HRIS - Payroll]] · [[HRIS - Personalia]] · [[HRIS - Overtime]]
- [[Sales - Incentive]] · [[Finance - Incentive]]
- [[Microservices - Employee Service]]
