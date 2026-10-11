# ADR - 0171 Izin per Jam Dihitung Ulang dari Semua Pengajuan dan Dipotong per Subtipe

## Untuk Manajemen

- **Yang berubah**: izin per jam (keluar sementara, pulang cepat) hanya memotong **jam izinnya**, bukan sehari penuh, tak peduli izin itu disetujui sebelum atau sesudah karyawan tap. Bila dalam satu hari ada beberapa izin, semuanya terhitung dan terlihat. Jam izin "urusan kantor" tetap dibayar walau di hari yang sama ada izin pribadi.
- **Kenapa sekarang**: run payroll **2026-08 (masih draft)** memotong **31 hari penuh pada 27 karyawan** untuk izin yang hanya beberapa jam (diukur 2026-10-12). Bila perbaikan naik sebelum run itu difinalisasi lalu dihitung ulang, slipnya benar tanpa koreksi apa pun.
- **Siapa terdampak**: karyawan yang mengajukan izin per jam. Sejak 2026-08-20 tercatat 51 hari "dipotong penuh" pada 40-an karyawan, dan 25 hari dengan izin ganda (16 karyawan) yang jamnya sebagian tak tercatat.
- **Tidak dijanjikan**: slip yang sudah terbit tidak dikoreksi otomatis (keputusan koreksi di tangan HR/Finance); entri presensi lama tidak dihitung ulang; belum ada fitur membatalkan izin yang sudah disetujui.
- **Besaran kerja**: dua PR backend berurutan di `bip-erp` (attendance), lalu tampilan Web ERP dan MyBharata.

## Deskripsi

*Satu entri presensi per hari tidak lagi menyimpan "izin terakhir yang disetujui", melainkan hasil hitung ulang dari **semua** pengajuan cuti/izin yang disetujui untuk hari itu. Hari yang sudah tap tetap hadir; izin per jam di hari itu hanya mengurangi jam. Payroll memotong per subtipe sesuai master perlakuan yang sudah ada.*

- **Status**: 🟢 **Diterima**, 2026-10-12, oleh irfanarfianto (perintah "kerjakan sekarang" atas bip-erp#2977; empat keputusan dipilih lewat pertanyaan pilihan ganda di sesi). Koreksi slip lampau **didelegasikan ke HR/Finance**, tidak diputuskan di sini.
- **Issue**: bip-erp#2977
- **Path di repo**: `bip-erp/services/attendance/payroll_treatment.go` (`computePayoutBreakdown`) · `bip-erp/services/attendance/main.go` (persetujuan izin `applyApprovedLeaveToPrevAttendanceEntries`, PATCH manual HR `/:id/update`) · `bip-erp/services/attendance/cron.go` (`approvedLeaveByEmployee`, `terapkanCutiDanDinas`) · `bip-erp/services/attendance/roster.go` (`cutiDanDinasHariIni`) · `bip-erp/shared-library/models/attendance/models.go` (`AttendanceEntries`)
- **Tanggal**: 2026-10-12

## Context

Entri `attendance_entries` hanya punya satu `status`, satu `leave_subtype`, dan satu `leave_hour` per hari. Penulisnya **menimpa**, tidak menggabungkan:

1. **Persetujuan izin** (`main.go`, `applyApprovedLeaveToPrevAttendanceEntries`, sekitar `setFields["leave_subtype"]`) melakukan `UpdateMany $set` `status`, `leave_subtype`, dan `leave_hour` milik pengajuan **itu saja**, tanpa memeriksa `clock_in`.
2. **Cron pra-alokasi** (`cron.go`, `approvedLeaveByEmployee`) dan **roster** (`roster.go`, `FindOne`) memakai satu pengajuan per karyawan, dari query tanpa urutan.
3. **Clock-in** (`handleClockIn`) menimpa `status` jadi Tepat Waktu/Terlambat dan membiarkan `leave_hour`/`leave_subtype`.

Akibatnya hasil payroll bergantung pada **urutan** kejadian. `computePayoutBreakdown` (`payroll_treatment.go`) hanya memperlakukan hari sebagai "hadir dengan jam izin" bila statusnya Tepat Waktu/Terlambat. Hari berstatus Izin dengan subtipe yang dipotong masuk cabang `default`, yang memasang `UnpaidFullDay = true`, dan payroll (`services/payroll/attendance_deduction_calc.go`, `nilaiHariKehadiran`) lalu memotong satu hari izin penuh plus uang makan.

Diukur di prod 2026-10-12 (baca saja):

| Ukuran | Nilai |
|---|---|
| Entri berstatus **Izin padahal sudah tap**, subtipe per jam yang dipotong, sejak 2026-08-20 | "Meninggalkan perkerjaan sementara" 30 hari (22 karyawan), "Pulang cepat" 21 hari (18 karyawan) |
| … subtipe "urusan kantor" (dibayar) | 133 hari (41 karyawan), dibayar penuh, sudah benar |
| Slip yang memuat hari itu sebagai **tidak dibayar** | **run 2026-08, status `draft`: 31 hari, 27 karyawan**; tidak ada run lain (rincian harian baru disimpan sejak 2026-08-20) |
| Hari dengan ≥ 2 izin per jam disetujui (2026-04-16 s.d. 2026-10-23) | 25 hari, 16 karyawan; 95 jam diajukan, 40 tersimpan; 6 jam sejak 2026-08-20 |
| Hari dengan ≥ 2 pengajuan apa pun | 47 hari, 29 karyawan; 5 dengan subtipe berbeda |
| Urusan kantor di hari ter-clock (ikut dipotong) | 1 hari |
| Dinas berformat jam | 0 |

Rincian pengukuran ada di bip-erp#2977 dan komentarnya.

**Peraturan Perusahaan** (`mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md` §2.D, Pasal 19-20): "Izin Jam Kerja: Memotong Tunjangan Kehadiran & Uang Makan." Yang dipotong adalah **izin jam kerja**, bukan sehari kerja. Memotong sehari penuh untuk izin beberapa jam adalah penyimpangan yang tidak pernah diputuskan. Pengecualian "urusan kantor dibayar" sudah hidup di master `payroll_subtype_treatment` (prod: `Izin | Meninggalkan perkerjaan sementara (urusan kantor)` → `paid: true`). Itu penyimpangan dari teks pasal yang **sengaja**, dan ADR ini yang mencatatnya sesuai [[ADR - 0071 Peta Kepatuhan Peraturan Perusahaan dan Kewajiban ADR untuk Penyimpangan]].

## Keputusan

1. **Hari yang sudah tap tetap hadir.** Izin per jam yang disetujui sesudah tap tidak mengubah `status` jadi Izin; ia hanya menambah jam izin. Payroll memperlakukan hari ber-`clock_in` sebagai hari hadir **apa pun statusnya**, sehingga entri lama yang sudah terlanjur berstatus Izin ikut benar tanpa migrasi.
2. **Dipotong per subtipe.** Jam izin dikelompokkan per subtipe dan diklasifikasikan lewat master `payroll_subtype_treatment` (kunci: status hasil resolve dari `leave_type` + subtipe). Hanya jam yang perlakuannya dipotong yang dikirim sebagai `leave_hours` ke payroll. Jam berbayar dikirim di field baru yang aditif.
3. **Hitung ulang, bukan menimpa.** Setiap persetujuan, dan setiap pra-alokasi cron/roster, menghitung ulang entri hari itu dari **semua** pengajuan `Disetujui` yang menutupi hari itu (idempoten, tak bergantung urutan):
   - `leave_hour` = jumlah jam izin berformat jam, dibatasi jam jadwal hari itu;
   - field baru `leave_parts[]` = satu baris per pengajuan (`request_id`, `leave_type`, `leave_subtype`, `format`, `hours`), dipakai layar dan payroll;
   - `leave_subtype` tetap ada sebagai subtipe pemenang, untuk konsumen lama.
4. **Aturan menang deterministik untuk `status`:**
   - Ada pengajuan berformat **hari**: status dari pengajuan harian. Bila lebih dari satu, yang disetujui paling akhir menang (tie-break `_id` terbesar). `leave_hour = 0` di hari itu.
   - Hanya pengajuan berformat **jam**: sudah tap berarti status tidak disentuh; belum tap berarti status dari pengajuan (Izin/Dinas) seperti sekarang. `leave_subtype` = subtipe dengan jam terbanyak (tie: `from_date` paling awal).
5. **Koreksi manual HR dikunci.** PATCH manual yang benar-benar mengubah `status` atau `leave_hour` menandai entri (`leave_manual: true`). Hitung ulang otomatis melewati entri bertanda dan mencatat log.
6. **Pembulatan jam seperti sekarang.** Per pengajuan `max(round(jam), 1)`; Pulang cepat/Datang terlambat dihitung dari `work_time` entri. Jumlahnya dibatasi jam jadwal. Interval yang tumpang tindih tidak digabung.
7. **Slip yang sudah terbit tidak diubah kode.** Basisnya sudah disnapshot di slip. Koreksi slip lampau, bila ada, adalah keputusan HR/Finance dan dikerjakan sebagai task terpisah. Entri presensi lama tidak dihitung ulang.

## Rencana kerja

| Urutan | Repo | Isi | Syarat |
|---|---|---|---|
| **PR-A** (mendesak) | bip-erp (attendance) | Keputusan 1 dan 2 di `computePayoutBreakdown`: hari ber-`clock_in` dihitung hadir, jam per subtipe dari `leave_parts` (fallback `leave_subtype` + `leave_hour` untuk entri lama), field `leave_hours_paid` aditif di `days[]`. Payroll tidak berubah. | Deploy **sebelum** run 2026-08 difinalisasi; lalu run itu dihitung ulang |
| **PR-B** | bip-erp (shared-library + attendance) | Keputusan 3-6: `leave_parts`, `leave_manual`, fungsi murni hitung ulang dipakai persetujuan, cron, dan roster | Sesudah PR-A |
| FE / Mobile | erp-frontend, my-bharata | Menampilkan semua izin hari itu dari `leave_parts` (usulan tampilan di pratinjau sesi 2026-10-12) | Sesudah PR-B ter-deploy |

Belum ada fitur membatalkan izin yang sudah disetujui. PR-B menyediakan titik masuk hitung ulang per karyawan per hari supaya fitur itu kelak cukup memanggilnya.

## Konsekuensi

- Rekap yang membaca `status` (KPI disiplin, ringkasan kehadiran, laporan "Izin Kantor" di Web ERP) akan melihat lebih sedikit hari Izin dan lebih banyak hari hadir untuk hari yang sudah tap. Perlu dicek sebelum PR-B merge.
- Run payroll draft yang dihitung ulang sesudah PR-A berubah angkanya. Itu memang tujuannya.
- Dua persetujuan yang berjalan bersamaan bisa membaca himpunan pengajuan yang berbeda (persetujuan berjalan sebagai goroutine). PR-B wajib menangani balapan ini, minimal dengan membaca ulang lalu mengulang bila himpunannya berubah.

## Alternatif yang ditolak

- **Menambah jam (`$inc`) saat disetujui**: sederhana, tapi pembatalan harus mengurangi sendiri, dan cron tetap perlu diubah terpisah.
- **Semua jam izin dipotong**: bertentangan dengan perlakuan "urusan kantor dibayar" yang sudah dikonfigurasi HR.
- **Izin sesudah tap tetap mengubah status jadi Izin**: mempertahankan potongan sehari penuh untuk izin beberapa jam.
- **Menggabung interval jam yang tumpang tindih**: lebih adil, tapi pembagian jam per subtipe jadi ambigu; ditunda sampai ada kasus nyata.
