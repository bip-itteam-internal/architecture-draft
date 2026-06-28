## ADR 0006 — Tukar Jadwal Kerja: rekan swap harus se-departemen + se-site

- **Status**: ✅ Accepted (keputusan 2026-06-28; asumsi coverage per-brand menunggu konfirmasi final HRD)
- **Tanggal**: 2026-06-28
- **Konteks dok**: [[HRIS - Tukar Jadwal Kerja]] · [[Microservices - Attendance Service]]

## Context

Fitur **Tukar Jadwal Kerja** (Tukar Shift & Tukar Hari) hanya untuk karyawan ber-shift (Security, Production, Host Live). Validasi rekan saat ini (`validateSwapPartner`, `services/attendance/func.go` ~704) hanya memeriksa **same shift-role** via `IsSameShiftRole(GroupID)` — **tidak** memeriksa departemen maupun site. Endpoint `partners` juga memfilter `group_id` saja.

Temuan dari data **produksi** (cek read-only 2026-06-28): posisi **"Host Live" tersebar di 2 departemen** — **Kyura (8 orang)** & **Beauty Hacks (3 orang)** — dan **grup rotasi sengaja mencampur keduanya**: tiap grup `HOSTLIVE-…-THU-OFF-P3` berisi **1 Beauty Hacks + 1 Kyura**, sehingga **setiap shift selalu terisi 1 host per brand** (invariant "1 per brand per shift").

Konsekuensinya, walau **Tukar Shift netral secara headcount** (barter 1:1), swap **lintas-departemen mengubah brand mana yang terisi** per shift — bisa membuat satu brand **kosong** di satu shift. Contoh: *Khilda* (BH, pagi) ⟷ *Helga* (Kyura, malam) → pagi jadi 0 BH, malam jadi 0 Kyura. Selain itu, Security punya site terpisah (`*-TINGGARJAYA`) yang coverage-nya per-lokasi.

## Decision

Rekan swap (`partner_employee_id`) untuk **Tukar Shift maupun Tukar Hari** wajib:

1. **Se-departemen** dengan pemohon (`requesterDepartment == partnerDepartment`), dan
2. **Se-site/lokasi** (mis. `*-TINGGARJAYA` tidak boleh dicampur dengan site utama).

Di samping syarat lama: bukan diri sendiri, sama-sama ber-shift, dan **same shift-role**. Guard diterapkan **di tingkat rekan** (bukan di tingkat grup rotasi — grup memang boleh campur departemen) pada `validateSwapPartner` dan filter endpoint `partners`.

## Consequences

- ➕ Menjaga invariant coverage **"1 host per brand per shift"** (Host Live BH vs Kyura) dan coverage per-site (Security Tinggarjaya).
- ➕ Approval konsisten — `review_1` = supervisor departemen pemohon; tak ada swap lintas-dept yang hanya di-review satu pihak.
- ➖ Mempersempit kandidat rekan: Host Live **Beauty Hacks (hanya 3 orang)** jadi sangat terbatas pilihan rekannya.
- 🔴 **Belum diimplementasi** — `validateSwapPartner` + `partners` masih meloloskan lintas-departemen (gap; terverifikasi). TODO: tambah cek departemen + site. Lihat Known limitation di [[HRIS - Tukar Jadwal Kerja]].
- ⚠️ **Asumsi yang perlu dikonfirmasi HRD**: tiap shift host live wajib 1 BH + 1 Kyura (bukan satu pool interchangeable). Bila HRD menyatakan "satu pool", ADR ini ditinjau ulang (kemungkinan **Superseded**).
- 🔗 Terkait coverage minimum staffing per role/slot/site (masih TBD di [[HRIS - Tukar Jadwal Kerja]]).

## Dokumen Terkait

- [[HRIS - Tukar Jadwal Kerja]] · [[Microservices - Attendance Service]]
