# ADR - 0205 Izin Jam yang Menutup Keterlambatan Dihitung Sekali, Telat Dikurangi Irisan Jendela Izin

## Untuk Manajemen

- **Yang berubah**: karyawan yang datang terlambat **tetapi sudah mengajukan izin** untuk jam itu tidak lagi dipotong dua kali (sekali sebagai telat, sekali sebagai izin). Hanya keterlambatan **di luar** jam izin yang dihitung sebagai telat. Jam izinnya sendiri tetap dipotong seperti biasa (proporsional per jam).
- **Kenapa sekarang**: diukur di produksi 2026-10-24, pola ini menimpa **16 karyawan (21 hari)** sejak sistem rincian harian hidup, 7 di antaranya di periode gaji berjalan. Potongannya bisa membengkak sampai lebih dari satu hari tunjangan untuk izin yang sebenarnya cuma beberapa jam.
- **Siapa terdampak**: karyawan yang izin per jamnya menutupi keterlambatan masuk. Tidak menyentuh karyawan lain.
- **Tidak dijanjikan**: slip yang sudah terbit tidak dikoreksi otomatis (keputusan HR/Finance, task terpisah); entri presensi lama tidak dihitung ulang; kasus izin per jam **tanpa kehadiran sama sekali** (tidak tap) di luar cakupan ADR ini dan tetap dihitung sehari.
- **Besaran kerja**: satu perubahan backend di layanan presensi `bip-erp`. Tampilan Web/Mobile tidak berubah (hanya angkanya).

## Deskripsi

*Jam telat dan jam izin untuk jam yang sama tidak lagi dijumlahkan. Jam telat yang dikirim ke payroll dikurangi irisannya dengan jendela waktu izin berformat jam yang disetujui pada hari itu, sehingga setiap jam ketidakhadiran dihitung tepat sekali.*

- **Status**: 🟡 **Diusulkan**, 2026-10-24. Pemutus: irfanarfianto. Kodenya belum ada.
- **Issue**: _(diisi setelah issue dibuat)_
- **Path di repo**: `bip-erp/services/attendance/payroll_treatment.go` (`computePayoutBreakdown`, saat menyusun `DayBasis.LateHours` untuk hari ter-clock ber-izin jam) · `bip-erp/shared-library/models/attendance/models.go` (`LeavePart` — tambah jendela `from`/`to` agar irisan bisa dihitung) · penulis hitung-ulang yang mengisi `leave_parts`: `bip-erp/services/attendance/main.go`, `cron.go`, `roster.go` **(baru)**
- **Tanggal**: 2026-10-24

## Context

[[ADR - 0171 Izin per Jam Dihitung Ulang dari Semua Pengajuan dan Dipotong per Subtipe]] (🟢 Diterima 2026-10-12, ter-deploy) memperbaiki dua hal: hari yang sudah tap dihitung hadir apa pun statusnya, dan izin per jam dipotong proporsional per subtipe. Tetapi ia **sengaja menunda** satu kasus — kutipan dari bagian "Alternatif yang ditolak": *"Menggabung interval jam yang tumpang tindih: lebih adil, tapi pembagian jam per subtipe jadi ambigu; ditunda sampai ada kasus nyata."*

Kasus nyata itu sekarang ada. Di kode yang sudah ter-deploy, `computePayoutBreakdown` melaporkan untuk hari ter-clock ber-izin jam: `DayBasis.LateHours` = jam telat **penuh** (dihitung dari jam mulai shift ke clock-in) **dan** `DayBasis.LeaveHours` = jam izin. Payroll (`services/payroll/attendance_deduction_calc.go`, `nilaiHariKehadiran`) menjumlahkan `JamTelat` (tarif /173) dan `HariIzin` (/26) sebagai dua baris terpisah. Ketika jendela izin beririsan dengan jendela keterlambatan, irisan itu terhitung **dua kali**.

Contoh terukur (prod, Aris Romadhoni, 2026-10-23): jadwal 08:00–16:00, izin "meninggalkan pekerjaan sementara" 08:00–13:00 (5 jam), clock-in 14:38 → `late_hour` 7 (08:00→14:38) + `leave_hour` 5 (08:00→13:00). Irisan 08:00–13:00 (5 jam) terhitung sebagai telat **dan** izin. Potongan kehadiran ≈ Rp 130.939, padahal ketidakhadiran sesungguhnya ~6,6 jam (telat 1,6 jam di luar izin + izin 5 jam).

Diukur prod 2026-10-24 (baca saja): **16 karyawan / 21 entri** sepanjang waktu berstatus Terlambat dengan `leave_hour > 0`; 7 di periode gaji 2026-09 (26 Sep–25 Okt). Tujuh entri periode berjalan telah ditambal data sementara (`late_hour` dikurangi `leave_hour`) agar run bulan ini benar; ADR ini untuk perbaikan **permanen**.

**Peraturan Perusahaan** (`mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md` §2.D, Pasal 19–20): "Izin Jam Kerja: Memotong Tunjangan Kehadiran & Uang Makan" — dipotong **sekali**, sebesar jam izinnya. Memotong jam yang sama sebagai telat *dan* izin adalah penyimpangan yang belum pernah diputuskan, sesuai kewajiban ADR di [[ADR - 0071 Peta Kepatuhan Peraturan Perusahaan dan Kewajiban ADR untuk Penyimpangan]].

## Decision

1. **Setiap jam ketidakhadiran dihitung tepat sekali.** Jam telat yang dikirim ke payroll untuk hari ter-clock ber-izin jam = durasi `[jam mulai shift → clock-in]` **dikurangi irisannya** dengan jendela izin berformat jam yang disetujui pada hari itu. Jam izin tetap utuh (proporsional per subtipe, sesuai ADR 0171).
2. **Irisan dihitung dari JENDELA WAKTU izin, bukan sekadar mengurangi angka jam.** Izin di tengah hari yang **tidak** beririsan dengan keterlambatan (mis. clock-in tepat waktu lalu izin siang) tidak boleh mengurangi jam telat. Pengurangan jam buta (`telat − jam_izin`) ditolak karena salah untuk kasus ini — itu sebabnya ADR 0171 menyebutnya "ambigu".
3. **Jendela waktu izin harus tersedia di titik hitung.** `LeavePart` diperluas dengan `from`/`to`, diisi oleh jalur hitung-ulang (persetujuan, cron, roster) dari `leave_request`. Entri lama tanpa jendela jatuh ke perilaku aman (lihat Konsekuensi). Bentuk persisnya diputuskan di `/plan`.
4. **Hanya menyentuh Tunjangan Kehadiran & Uang Makan.** Gaji pokok tidak terpengaruh. Tidak ada tarif/ambang/pembagi baru; hanya jam telat yang dilaporkan yang berubah.
5. **Slip yang sudah terbit tidak diubah kode** (sama dengan ADR 0171 Keputusan 7). Koreksi slip lampau adalah keputusan HR/Finance.

## Consequences

- Potongan kehadiran **turun** untuk ~16 karyawan yang izinnya menutupi keterlambatan. Run draft yang dihitung ulang sesudah perbaikan berubah angkanya — memang tujuannya.
- Entri lama yang `leave_parts`-nya belum punya jendela waktu: fallback aman = perilaku ADR 0171 saat ini (telat penuh, tidak dikurangi) atau pengurangan jam-buta terbatas; dipilih di `/plan` dengan test regresi. Degradasinya tidak boleh menghukum lebih dari keadaan sekarang.
- **Kasus izin per jam TANPA clock-in** (karyawan tidak hadir sama sekali, mis. prod 2026-10-20 Afiana) **di luar cakupan** — tetap dihitung sehari karena tak ada kehadiran. Bila kelak diputuskan proporsional juga, itu ADR tersendiri.
- Membuka kembali alternatif yang ditunda ADR 0171; ADR ini menggantikan status "ditunda" itu dengan keputusan.

## Alternatif yang ditolak

- **`telat efektif = max(0, telat − jam_izin)`** (pengurangan jam buta): sederhana dan benar untuk izin yang menempel di awal shift, tetapi salah untuk izin di tengah hari yang tidak beririsan dengan keterlambatan — persis keambiguan yang membuat ADR 0171 menundanya. Dipakai hanya sebagai tambalan data sementara periode berjalan, bukan perbaikan permanen.
- **Perbaiki `late_hour` di sumber (`handleClockIn`)**: mengubah `late_hour` tersimpan sehingga memengaruhi tampilan dan rekap disiplin yang membacanya; keputusan "sekali" ini soal potongan payroll, jadi irisan dihitung di jalur payout, bukan menimpa fakta telat.
