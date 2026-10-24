# ANALISA - Izin Jam Menutup Keterlambatan Dihitung Sekali

> **Menunggu [[ADR - 0205 Izin Jam yang Menutup Keterlambatan Dihitung Sekali, Telat Dikurangi Irisan Jendela Izin]] Diterima: sebelum itu ANALISA ini BUKAN keputusan yang bisa ditunjuk `/brief`.**

- **ADR**: [[ADR - 0205 Izin Jam yang Menutup Keterlambatan Dihitung Sekali, Telat Dikurangi Irisan Jendela Izin]] (🟡 Diusulkan)
- **Dok domain**: [[Microservices - Attendance Service]] · [[HRIS - Payroll]]
- **Pemutus**: irfanarfianto
- **Ukuran**: **Kecil** — satu repo (`bip-erp`, layanan attendance). FE/mobile tidak berubah (mereka render angka potongan, bukan strukturnya). Bisa jadi 2 PR (perluas `leave_parts` dengan jendela waktu, lalu pakai di `computePayoutBreakdown`); bila begitu, pecah jadi issue sejajar, bukan sub-issue (satu repo).
- **Induk**: [[ADR - 0171 Izin per Jam Dihitung Ulang dari Semua Pengajuan dan Dipotong per Subtipe]] (🟢 Diterima, ter-deploy) — ADR 0205 membuka kasus yang 0171 tunda.

---

## Issue: Izin jam yang menutup keterlambatan dihitung sekali (telat dikurangi irisan jendela izin)

**Repo**: `bip-erp`
**Pemutus:** irfanarfianto
**PIC:** _(diisi saat ditugaskan)_
**Issue GitHub:** [bip-itteam-internal/bip-erp#3541](https://github.com/bip-itteam-internal/bip-erp/issues/3541)

### Masalah
Hari yang sudah tap dengan izin per jam yang menutupi keterlambatan dihitung dobel: `computePayoutBreakdown` melaporkan `DayBasis.LateHours` (telat penuh dari jam mulai shift) DAN `DayBasis.LeaveHours` (izin), lalu payroll menjumlah keduanya. Irisan jam telat dan jendela izin terpotong dua kali. Diukur prod 2026-10-24: 16 karyawan / 21 entri (status Terlambat dengan `leave_hour > 0`) sepanjang waktu, 7 di periode gaji 2026-09.

### Keputusan
Ikuti [[ADR - 0205 Izin Jam yang Menutup Keterlambatan Dihitung Sekali, Telat Dikurangi Irisan Jendela Izin]]. **Layak diberi label `Siap Agent` hanya setelah ADR 0205 berstatus Diterima** (sekarang 🟡 Diusulkan). Bentuk ringkas: jam telat yang dikirim ke payroll = `(jam mulai shift → clock-in)` − irisan dengan jendela izin berformat jam yang disetujui hari itu; jam izin tetap proporsional per subtipe; hanya Tunjangan Kehadiran + Uang Makan yang terpengaruh.

### Yang harus benar
- Hari ter-clock dengan izin jam beririsan keterlambatan: jam telat ke payroll = durasi keterlambatan **dikurangi irisan** dengan jendela izin disetujui. Contoh Aris (jadwal 08:00–16:00, izin 08:00–13:00, clock-in 14:38): telat efektif = 13:00→14:38 (~2 jam), bukan 7 jam; izin tetap 5 jam.
- Izin jam **di tengah hari** yang TIDAK beririsan dengan keterlambatan tidak mengurangi jam telat.
- Tanpa izin: jam telat penuh seperti sekarang (tidak ada regresi).
- Jam izin tetap proporsional per subtipe (tak berubah dari ADR 0171); gaji pokok tidak berubah.
- Entri lama yang `leave_parts`-nya belum punya jendela waktu: degradasi aman, tidak lebih buruk dari perilaku sekarang.
- Ada test fungsi murni untuk perhitungan irisan (kasus: beririsan penuh, sebagian, tanpa irisan, tanpa izin).

### Di luar cakupan
- Izin jam **tanpa clock-in** (karyawan tak hadir sama sekali) — tetap dihitung sehari; bila mau proporsional, ADR tersendiri.
- Koreksi slip yang sudah terbit (keputusan HR/Finance, task terpisah).
- Entri periode 2026-09 yang sudah ditambal data sementara (`late_hour` dikurangi `leave_hour`) — perbaikan kode ini menggantikan tambalan untuk periode berikutnya.

### Data / bukti pendukung
Diukur prod 2026-10-24 (baca saja): 16 karyawan / 21 entri status Terlambat dengan `leave_hour > 0` sepanjang waktu; 7 di periode 2026-09. Contoh Aris Romadhoni (BIP-0224-01-26) 2026-10-23: `late_hour` 7 + `leave_hour` 5 pada jadwal 8 jam, izin 08:00–13:00, clock-in 14:38. Config potongan (singleton `payroll_config`): hour_divisor 173, day_divisor 26.

### Prasyarat
- [[ADR - 0205 ...]] berstatus Diterima.
- Dibangun di atas [[ADR - 0171 ...]] (sudah ter-deploy): `leave_parts`, `computePayoutBreakdown` jalur hourLeaveSplit.
