# Payroll — Persona & Alur

> Menggambarkan **siapa** yang memakai alur **Payroll Run** (penggajian bulanan & **THR**) dan **bagaimana** alurnya. Sisi konsep: [[HRIS - Payroll]]; implementasi: [[Microservices - Payroll Service]]. Status: ⚠️ **Implemented (BE + FE)** — lifecycle run + slip self-service + THR di kode BE; **FE THR** (buat run THR, badge Jenis, detail masa kerja/proporsi, slip THR) di [[APP - Web ERP]].

## Aktor (ringkas)

| Persona | Peran & Divisi | Akses / RBAC | Device | Muncul di |
|---|---|---|---|---|
| **HR Supervisor (Personalia)** | Supervisor/Admin HR | `isHRSupervisor` (`system_roles["hris"]` = supervisor/admin) | Web ERP | Buat/recalc run (bulanan & THR); **impor & hapus run impor** (🔜 belum merged) |
| **Approver (Direktur / HR Admin)** | Admin HR / Direktur | `isApprover` = `isHRAdmin` (`system_roles["hris"]` = admin) | Web ERP | Approve → Publish run |
| **Karyawan** | Semua karyawan tetap/kontrak | Terautentikasi (identitas dari header gateway) | Web ERP (MyBharata menyusul) | Lihat slip sendiri (self-service) |

## Persona detail

### HR Supervisor (Personalia) — pembuat run
- **Peran & Divisi**: Supervisor/Admin di divisi HR/Personalia.
- **Akses / RBAC**: `isHRSupervisor` — `POST /payroll-runs` (bulanan) & `POST /thr-runs` (THR); `POST /payroll-runs/:id/recalculate` (draft).
- **Device**: Web ERP (grup menu Payroll).
- **Tujuan**: menjalankan penggajian bulanan (prorata Tunjangan Kehadiran dari attendance) dan **THR** (× proporsi masa kerja) untuk semua karyawan sekaligus, lalu review slip per orang sebelum diajukan.
- **Pain point**: hitung manual gaji/THR + pajak rawan salah & lambat; tak ada jejak lifecycle.
- **Aksi utama**: buat run → sistem hitung semua karyawan (snapshot slip) → cek line (incl. line ber-`error` bila attendance/masa kerja tak tersedia) → recalc bila perlu → serahkan ke Approver.
- 🔜 **Impor riwayat** (branch `feat/payroll-impor-run`, belum merged): `POST /payroll-runs/import` — unggah spreadsheet gaji yang **sudah dibayar**, petakan kolomnya, lalu impor sebagai run `type=import`. Angkanya **disalin, tidak dihitung**. Bila salah unggah, `DELETE /payroll-runs/:id` membatalkannya selagi `draft`; gerbangnya sengaja `payroll.work` juga, supaya yang mengimpor bisa membatalkan sendiri tanpa menunggu Approver. ⛔ Run impor **tidak bisa di-recalc** — koreksinya hapus lalu impor ulang. Rincian: [[ADR - 0070 Impor Payroll Run dari Spreadsheet HRD untuk Backfill Riwayat Gaji]].

### Approver (Direktur / HR Admin) — persetujuan & terbit
- **Peran & Divisi**: Admin HR / Direktur (persetujuan final).
- **Akses / RBAC**: `isApprover` (= HR admin) — `POST /payroll-runs/:id/approve` (draft→approved) & `/publish` (approved→published).
- **Device**: Web ERP.
- **Tujuan**: memastikan angka benar sebelum slip dibuka ke karyawan; menjaga kontrol dua-tahap.
- **Pain point**: tanpa pemisahan buat vs setujui, tak ada kontrol; slip bisa bocor sebelum final.
- **Aksi utama**: tinjau run draft → **Approve** → **Publish** (setelah published, karyawan bisa lihat slip).

### Karyawan — self-service slip
- **Peran & Divisi**: karyawan yang punya baris di sebuah run `published`. ⚠️ Untuk run engine itu berarti ia punya `employee_salary`; untuk **run impor tidak**, karena backfill riwayat justru mencakup orang yang struktur gajinya belum pernah dimasukkan ke sistem (kop slipnya jatuh ke badan usaha default dan barisnya ditandai `import_company_default`).
- **Akses / RBAC**: cukup terautentikasi; identitas dari header gateway (`BIP-Employee-ID`). Hanya slip **sendiri**, hanya dari run **published**; field internal HR (`notes`, pembuat/penyetuju/penerbit) di-**redact**.
- **Device**: Web ERP (integrasi [[APP - MyBharata]] menyusul).
- **Tujuan**: melihat rincian gaji bulanan & slip **THR** sendiri (pendapatan, BPJS, PPh21, net).
- **Pain point**: dulu slip manual/tak transparan; sulit cek potongan.
- **Aksi utama**: buka "Slip Gaji Saya" → `GET /payroll-runs/my` (daftar) / `/my/:id` (detail). Slip THR dibedakan dari bulanan via `run.type`.

## Alur

```
HR Supervisor  ── buat run (bulanan: POST /payroll-runs · THR: POST /thr-runs) ──▶ DRAFT (hitung semua karyawan)
     │ recalc (opsional, draft)
     │
     └─ 🔜 impor (POST /payroll-runs/import) ──▶ DRAFT (angka DISALIN dari spreadsheet)
              │ TIDAK bisa recalc; koreksi = DELETE lalu impor ulang (selagi draft)
     ▼
Approver  ── /approve ──▶ APPROVED  ── /publish ──▶ PUBLISHED
                                                        │
                                                        ▼
                                              Karyawan lihat slip (/payroll-runs/my)
```

**THR (spesifik)**: `POST /thr-runs` → masa kerja tiap karyawan diambil dari [[Microservices - Employee Service]] (`join_date`) → **proporsi** (≥12 bln=1; 1–11=bln/12; <1=tak dapat) → THR = `basic_salary × proporsi`; PPh21 = TER atas bruto THR (standalone, di-true-up saat Rekonsiliasi Desember). Lifecycle approve/publish & slip self-service **reuse** rute `/payroll-runs/*`.

## Skenario Gagal

- **Masa kerja tak diketahui** (join_date kosong) → line THR karyawan itu ditandai `error`, THR = 0 (tak salah bayar). HR lengkapi data lalu recalc.
- **employee-service tak tersedia** saat buat run THR → run draft ter-buat tapi 0 line (error); pulihkan via `recalculate` setelah service kembali.
- **Approve/Publish di status salah** → ditolak (approve hanya dari `draft`; publish hanya dari `approved`).
- **Karyawan akses run belum published / bukan miliknya** → tak terlihat (self-service hanya published + line miliknya).
- 🔜 **Impor: baris tak menjumlah ke TOTAL TERIMA** → SELURUH permintaan ditolak 400 berikut selisih tiap baris dalam rupiah; **nol dokumen tersimpan**. Bukan sebagian terimpor, karena satu run yang berdiri dengan sebagian baris adalah payroll yang salah, bukan payroll yang belum selesai.
- 🔜 **Impor: `employee_id` tak ada di master karyawan** → baris ditolak, dan layar menautkan ke Data Karyawan karena tempat membetulkannya ada di modul lain.
- 🔜 **Impor: nama komponen tak ada di master** → ditolak 400 dengan nama yang bersangkutan disebut; HR menambahkannya dulu di Pengaturan > Komponen Gaji.
- 🔜 **Impor: tombol Hitung Ulang ditekan pada run impor** → 400. Layar juga menyembunyikan tombolnya, tapi penjaga yang sesungguhnya ada di server.

## Dokumen Terkait

- [[HRIS - Payroll]] · [[Microservices - Payroll Service]] · [[Microservices - Employee Service]] · [[Microservices - Attendance Service]] (`payroll-supplement`)
- [[ADR - 0070 Impor Payroll Run dari Spreadsheet HRD untuk Backfill Riwayat Gaji]]
