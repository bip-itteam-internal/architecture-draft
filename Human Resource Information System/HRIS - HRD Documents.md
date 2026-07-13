# HRIS - HRD Documents

## Deskripsi

*Sistematisasi dokumen HRD (SOP, Syarat & Ketentuan, Kebijakan, dll.) dari Google Drive manual menjadi satu model **reusable**: `title + body` + **penyasaran (targets) polimorfik** (semua/posisi/departemen/jenis-pengajuan/karyawan) + acknowledgment + versioning. SOP disasar per posisi; S&K per jenis pengajuan; kebijakan sekantor.*

- **Status**: ⚠️ **Fase 1 BE di kode** (keputusan: [[ADR - 0013 HRD Documents]]) — service [[Microservices - HRD Document Service]]; **FE & soft-validate target belum**.
- **Implementasi**: [[Microservices - HRD Document Service]] (Fase 1 BE).

## Latar Belakang

Dokumen HRD kini manual di **Google Drive** ([[HRIS - Big Pictures]] §Dokumen): tak tersistem, tak bisa disasar per-konteks, tak ada jejak persetujuan. Acknowledgment HR **"masih dalam diskusi"** — bila dokumen butuh persetujuan HR, wait 2×24 jam per request dianggap buruk (diselesaikan dengan **ack di titik submit**, bukan menunggu HR — lihat ADR).

## Ruang Lingkup / Cakupan (business view)

- Jenis dokumen: **SOP**, **Syarat & Ketentuan**, **Kebijakan** (+ jenis lain via registry `type`).
- **Penyasaran**: `targets[]` (OR) lintas dimensi — `all | position | department | request_type | employee`.
- **Acknowledgment** opsional (`ack_required`); S&K terkait pengajuan → wajib setuju sebelum submit, tercatat per-versi.
- **Versioning** immutable (riwayat versi), body **rich-text**.

## Persona / Pengguna

| Persona | Peran & Divisi | Akses / RBAC | Device |
|---|---|---|---|
| **HR Admin (Personalia)** | Admin HR | `isHRAdmin` (`system_roles["hris"]`) | Web ERP |
| **Karyawan** | Semua karyawan | terautentikasi (identitas gateway) | Web ERP (MyBharata menyusul) |

- **HR Admin** — **Tujuan**: kelola dokumen HRD tersistem & tersasar. **Aksi**: buat/edit → set `type`, `targets`, `ack_required`, tulis body (rich-text) → **publish** (versi baru).
- **Karyawan** — **Tujuan**: baca dokumen yang berlaku untuknya + setuju S&K saat mengajukan. **Aksi**: "Dokumen Saya" (dokumen yang menyasar dirinya); saat pengajuan (mis. Cuti) → tampil S&K → **setuju** → submit.

## Bentuk Form Author (FE, acuan)

Satu form untuk **semua jenis** dokumen — yang berubah hanya *Jenis* & nilai *target*.

```
Jenis *      [ Syarat & Ketentuan ▼ ]        ← registry type
Judul *      [ .................................. ]

Berlaku untuk (targets) *                     ← OR: cocok salah satu
  • Jenis Pengajuan: Cuti      [x]
  • Jenis Pengajuan: Dinas     [x]
  [ + Tambah target ]  Dimensi:[Semua│Posisi│Departemen│
       Jenis Pengajuan│Karyawan]  Nilai:[dropdown sumber ▼]  ← cascade + soft-validate

[✓] Wajib persetujuan (acknowledgment)

Isi dokumen *  ┌ Rich-text editor (B I • 1. link H2 …) ┐
               └ tulis isi SOP / S&K / kebijakan ……… ┘

Status: Draft · Versi aktif: v2 · [Lihat riwayat]
              [ Simpan Draft ]   [ Publish → v3 ]
```

- **Targets builder** = inti reusable: tiap baris `{dimensi → nilai}`. *Semua* = tanpa nilai; dimensi lain → nilai dari dropdown sumber (posisi/dept dari employee, request_type dari registry attendance).
- **Publish** → versi immutable baru. Karyawan sisi baca: "Dokumen Saya" (baca) / centang setuju (S&K saat pengajuan) — tanpa builder.

## Konsumen Data

- [[Microservices - Employee Service]] — sumber posisi/departemen (validasi & resolusi target).
- [[Microservices - Attendance Service]] — `HRRequestTypes` (nilai target `request_type`) + titik integrasi S&K pada alur `/request/*`.

## Belum Diputuskan (TBD)

- **Fase 2**: enforcement ack di BE saat submit request (kini gate di FE); tanda tangan security **QR** untuk status cuti (§Dokumen); analitik kepatuhan (siapa belum ack).
- `scope_type: employee` (dokumen per-individu) — disediakan tapi opsional di Fase 1.

## Dokumen Terkait

- [[ADR - 0013 HRD Documents]] (keputusan desain) · [[HRIS - Big Pictures]] (§Dokumen) · [[HRIS - Leave Request]] · [[HRIS - Employee Request & Approval]] · [[Microservices - Employee Service]] · [[Microservices - Attendance Service]]
