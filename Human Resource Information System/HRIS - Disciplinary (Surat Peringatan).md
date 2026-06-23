## Deskripsi

*Penanganan kedisiplinan karyawan & **Surat Peringatan (SP)** — mis. dari keterlambatan/pelanggaran berulang. Saat ini masih **konsep** (disebut di [[HRIS - Big Pictures]] & [[BASE - Enterance Point]]), belum ada implementasi di kode.*

- **Status**: 🟡 Konsep / Direncanakan (belum di kode)

## Latar Belakang

- Karyawan dengan pelanggaran (mis. **telat** berulang, alpha) dapat dikenakan **Surat Peringatan**.
- Penanganan telat saat ini digambarkan di BPMN [[HRIS - Big Pictures]] (alur manual → usulan otomatis).
- Status SP karyawan ingin ditampilkan di landing ([[BASE - Enterance Point]]): jumlah SP aktif, dengan **masa berlaku 6 bulan** per SP sebelum hangus.

## Ruang Lingkup (Direncanakan)

- **Penerbitan SP** (tingkat: SP1/SP2/SP3 — *tingkat & aturan eskalasi TBD*) atas pelanggaran/akumulasi telat-alpha
- **Masa berlaku SP** (6 bulan) → otomatis kedaluwarsa/hangus
- Riwayat & status SP per karyawan (jumlah aktif)
- Tautan pemicu dari data kehadiran ([[HRIS - Attendance System]]) — mis. akumulasi telat/alpha

## Belum Diputuskan (TBD)

- Tingkatan SP & aturan eskalasi (berapa pelanggaran → SP berapa)
- Pemicu otomatis vs penerbitan manual oleh HR
- Dampak ke payroll/insentif (sanksi)
- Alur approval penerbitan SP

## Dependensi / Dokumen Terkait

- [[HRIS - Big Pictures]] (BPMN penanganan telat)
- [[BASE - Enterance Point]] (status SP)
- [[HRIS - Attendance System]] · [[HRIS - Personalia]] · [[Microservices - Employee Service]]
