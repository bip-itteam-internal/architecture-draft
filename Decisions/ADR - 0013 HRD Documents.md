## ADR 0013 — HRD Documents: model dokumen reusable (title+body + targets polimorfik)

- **Status**: ✅ Accepted — **Fase 1 BE diimplementasi** ([[Microservices - HRD Document Service]]); FE & soft-validate target menyusul
- **Tanggal**: 2026-07-14
- **Konteks dok**: [[HRIS - HRD Documents]] · [[HRIS - Big Pictures]] · [[Microservices - Employee Service]] · [[Microservices - Attendance Service]] · [[ADR - 0002 Database-per-Service]]

## Context

Dokumen HRD (SOP, Syarat & Ketentuan, Kebijakan, dll.) saat ini disimpan manual di **Google Drive** ([[HRIS - Big Pictures]] §Dokumen) — tak tersistem, tak bisa disasar per-konteks, tak ada jejak persetujuan. Kebutuhan: **SOP** disasar **per posisi**, **S&K** **per jenis pengajuan** (Izin/Cuti/Dinas/Sakit/Koreksi Presensi/Tukar Jadwal), **kebijakan** sekantor. Struktur umum semuanya sama: **title + body**. Acknowledgment HR **"masih dalam diskusi"** (§Dokumen) karena bila dokumen butuh persetujuan HR, wait time 2×24 jam per request dianggap buruk.

Pola reusable sudah ada di ERP: registry `/data-type` (attendance) + master configurable (payroll `payroll-status-treatment`), alur leave-request (`/request/*`), RBAC `system_roles["hris"]`, rich-text-editor (branch `feat/rich-text-editor`). Nilai penyasaran nyata: posisi/departemen (`work_data`, [[Microservices - Employee Service]]) + jenis pengajuan (`HRRequestTypes`, [[Microservices - Attendance Service]]).

## Decision

Satu model **dokumen HRD reusable** di **service baru `hrd-document`** (DB sendiri, [[ADR - 0002 Database-per-Service]]), gateway `/api/hrd-document/*`, RBAC `isHR`/`isHRAdmin` (`system_roles["hris"]`). Tujuh keputusan:

1. **Penyasaran (`targets[]`)** — dokumen punya `targets: [{type, value, label}]`, berlaku bila karyawan cocok **salah satu** (OR); boleh campur dimensi. `type` target = **ENUM 5 dimensi**: `all | position | department | request_type | employee`.
2. **Acknowledgment opsional** — flag `ack_required` per dokumen. Bila true & S&K terkait pengajuan → karyawan **wajib setuju saat submit** (langsung, **tanpa** menunggu HR → menjawab kekhawatiran wait 2×24 jam). Ack dicatat **per-versi**.
3. **Versioning immutable** — tiap publish = versi baru (snapshot title+body); versi lama tersimpan (riwayat). Ack terikat versi.
4. **Body Markdown** — editor FE (TipTap + `tiptap-markdown`, `RichTextField`) menghasilkan & menampilkan **Markdown**; simpan `body_md` (kanonik) + turunan `body_text` (teks polos untuk search/preview, via `toPlainText`). *(Revisi pasca-implementasi FE: rencana awal `body_html`/`body_json` diganti Markdown agar selaras editor nyata di `erp-frontend`.)*
5. **Extensibility** — `type` dokumen (sop/terms/policy/…) = **registry** configurable (HR tambah tanpa deploy); `scope_type` = **enum kode** (tiap dimensi butuh resolver).
6. **Rumah** — service baru `hrd-document` (bukan menggemukkan employee service).
7. **Validasi target soft** — saat simpan, cek nilai target ada di sumber (posisi/dept → employee, request_type → registry attendance) + simpan `label` snapshot; **soft** (warning bila tak cocok, tak memblokir keras).

**Model data** (`hrd_document_db`): `hrd_document` (identitas+config: type, title, body_md/text, targets[], ack_required, status, current_version) · `hrd_document_version` (snapshot konten immutable: title, body_md/text, published_by/at) · `hrd_document_ack` (`{document_id, version, employee_id, agreed_at}`) · `hrd_document_type` (registry jenis).

**RBAC**: **author = HR staff (`isHR`)** — buat/edit/hapus-draft/**terbitkan** dokumen (bukan `isHRAdmin`; menulis dokumen bagian kerja staf HR). Registry `type` tulis = `isHRAdmin`. Baca+ack karyawan = terautentikasi.

**Resolusi "Dokumen Saya"** = union target vs posisi/dept/employee_id karyawan + `all`. **S&K saat pengajuan** = FE query dokumen `target{request_type:X}` + `ack_required` → tampil → wajib setuju → catat ack → submit boleh lanjut.

## Consequences

- ➕ Satu model + query untuk semua jenis dokumen (SOP/S&K/kebijakan) — reusable, hemat kode.
- ➕ Ack di titik **submit** (bukan approval HR) → **tanpa wait 2×24 jam** (menjawab §Dokumen).
- ➕ Jejak audit: versi immutable + ack per-versi (tahu siapa setuju versi berapa).
- ➖ Penyasaran lintas-service: `hrd-document` bergantung employee (posisi/dept) & attendance (request_type) → panggilan internal + risiko nilai basi (dimitigasi soft-validate + `label` snapshot).
- ➖ Body rich-text menambah kebergantungan ke rich-text-editor yang **masih dibangun**.
- ⚠️ **Fase 1 = gate ack di FE**; enforcement ack di BE saat submit request (attendance `/request/create` cek ack) = **Fase 2** (kopling lintas-service lebih dalam).
- ⚠️ **Belum diputuskan (Fase 2)**: tanda tangan security QR untuk status cuti (§Dokumen), analitik kepatuhan (siapa belum ack).
- 🔗 `scope_type: employee` (dokumen per-individu) jarang dipakai — disediakan tapi opsional di Fase 1.

## Dokumen Terkait

- [[HRIS - HRD Documents]] (konsep domain) · [[HRIS - Big Pictures]] (§Dokumen) · [[HRIS - Leave Request]] / [[HRIS - Employee Request & Approval]] (integrasi S&K) · [[Microservices - Employee Service]] · [[Microservices - Attendance Service]] · [[ADR - 0002 Database-per-Service]]
