# Finance - Proses Gaji dan Iuran BPJS

## Deskripsi

*Proses P7, gaji dan iuran BPJS, dari [[Finance - Proses Bisnis dan Kebutuhan Sistem]]. Dok ini memuat tujuan, cara dikerjakan hari ini, yang sudah ada di ERP, alur target di sistem, celah yang harus ditutup, kontrol yang wajib dijaga, dan ukuran untuk membuktikan efisiensinya. Penilaian cakupan dan kesesuaiannya ada di dok induk.*

- **Status**: ⚠️ **Implemented (ada catatan)**. Perhitungan payroll per badan usaha ada; daftar transfer bank, rekap iuran BPJS, dan jurnal gaji 🟡 direncanakan (T7).
- **Sumber**: survei alur kerja Finance (isian mandiri 14 sampai 16 September 2026, butir bertanda *survei 2026-09*), kode `bip-erp` dan `erp-frontend` di `origin/main` 2026-09-17. Keadaan prod bertanggal di tiap butir; ukur ulang sebelum dipakai memutuskan.
- **Kelompok celah**: **A** sudah ada, tinggal dipakai · **B** sudah ada, perlu diperbaiki · **C** belum ada, perlu dibangun (definisi di dok induk).

## Tujuan

Gaji dan iuran dihitung sekali dari data kehadiran, dibayar per badan usaha tanpa diketik ulang, dan dijurnal otomatis.

## Hari ini (*survei 2026-09*)

Rekap gaji dan data BPJS datang dari HR lewat WhatsApp, Excel, dan email per CV (satu sampai tiga hari, lampiran kadang tidak ada, nominal bisa beda); rekap diperiksa per orang terhadap lampiran izin, SKS, dan jam absen, lalu diperiksa lagi dari sisi rekening dan PPh; pembayaran diketik ulang ke bank.

## Sudah ada di ERP

Payroll per badan usaha (41 entitas), dua dasar upah BPJS, potongan kehadiran dari attendance-service, dan beban perusahaan per karyawan ([[Microservices - Payroll Service]]). Prod 2026-09-17 (jumlah dokumen per koleksi, baca-saja): 1 run payroll, dibuat 2026-09-03, berisi 174 baris; 180 data gaji karyawan; 23 komponen gaji; 41 badan usaha. Dua run draft yang tercatat akhir Agustus (dibuat Juli dan Agustus) tidak ada lagi. Status run itu (draft, disetujui, atau terbit) belum diukur. Aturan potongan dan sanksi mengikuti [[HRIS - Kepatuhan Peraturan Perusahaan]].

## Alur target

HR menjalankan payroll di ERP → pengecekan Finance memakai data kehadiran dan izin yang sudah di sistem → sistem menghasilkan daftar transfer per badan usaha dan rekap iuran BPJS → pembayaran lewat P2 → jurnal gaji otomatis ke buku entitasnya.

## Celah

- **A** HR memakai payroll ERP sebagai sumber gaji.
- **C** Daftar transfer bank, rekap iuran BPJS per badan usaha, dan jurnal gaji (T7). `git grep` 2026-09-17 atas `services/payroll` tidak menemukan ekspor transfer bank, rekap BPJS, maupun pemanggilan Accurate atau jurnal (kontrol positif: kata `bpjs` ada di 33 berkas).
- **TBD** Apakah pemeriksaan rekap gaji dari dua sudut (kehadiran dan potongan; rekening dan PPh) tetap dua langkah sesudah payroll ERP dipakai.

## Kontrol wajib

Yang menghitung gaji bukan yang menyetujui dan membayarnya.

## Ukuran efisiensi

Lama dari rekap gaji tersedia sampai dibayar; jumlah selisih nominal BPJS antara tagihan dan data peserta.

Sumber data baseline: Tanggal kirim rekap gaji dan tanggal transfer; tagihan BPJS dan data peserta.

## Proses terkait

- P2: [[Finance - Proses Pembayaran Keluar]]

## Dokumen Terkait

- [[Finance - Proses Bisnis dan Kebutuhan Sistem]] · [[Finance - Kalender dan Rantai Tenggat]] · [[Finance - Sambungan dan Permintaan Data Lintas Departemen]] · [[Finance - FAT Persona]]
- [[Microservices - Payroll Service]] · [[HRIS - Kepatuhan Peraturan Perusahaan]]
