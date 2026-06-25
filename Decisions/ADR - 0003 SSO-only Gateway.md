## ADR 0003 — Autentikasi terpusat: SSO + JWT via API Gateway

- **Status**: ✅ Accepted (mencerminkan kondisi kode)
- **Tanggal**: TBD (keputusan historis; dikodifikasi 2026-06-24)
- **Konteks dok**: [[CORE - SSO Flow]] · [[CORE - API Master Gateway]] · [[BASE - Enterance Point]]

## Context

Banyak aplikasi internal (web ERP, mobile, Task Manager, dll) butuh autentikasi. Membuat akun terpisah per aplikasi = buruk untuk UX & keamanan. Lihat [[CORE - SSO Flow]].

## Decision

Autentikasi **terpusat di [[CORE - API Master Gateway]]**: login memanggil employee-service di balik layar, lalu gateway menerbitkan **JWT**. Aplikasi internal lain memakai akun karyawan yang sama via **SSO one-time-code handoff** (`/auth/sso/ticket` → `/auth/sso/redeem`). Service di belakang gateway hanya membaca identitas dari header `BIP-*` + RBAC ringan berbasis `system_roles` (key per-modul). Aplikasi eksternal/prototype pun memakai SSO ERP ini, bukan auth sendiri.

## Consequences

- ➕ Satu identitas karyawan untuk semua aplikasi; revoke terpusat.
- ➕ Service tidak mengurus login — cukup percaya header gateway + cek role modulnya.
- ➖ Gateway = komponen kritis (single entry); harus selalu sehat (lihat [[IT - Monitoring System]]).
- ⚠️ Role per modul diambil dari `system_roles["<modul>"]`; menambah key role baru menyentuh employee-service/JWT (lihat keputusan RBAC [[IT - Form Builder]] yang sengaja reuse key `it` agar tak mengubah employee-service).
- 🔗 Cut-over Task Manager ke SSO-only sudah dilakukan (lihat catatan proyek terkait).

## Dokumen Terkait

- [[CORE - SSO Flow]] · [[CORE - API Master Gateway]] · [[BASE - Enterance Point]] · [[IT - Monitoring System]]
