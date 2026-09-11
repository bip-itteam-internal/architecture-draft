## ADR 0019 — Kontrak Kerja Elektronik: service internal + lapisan tersertifikasi (PSrE + e-Meterai) via API berlisensi

- **Status**: ⛔ **Superseded** oleh [[ADR - 0089 Tanda Tangan Kontrak Kerja di Sistem Sendiri, Didampingi HRD, e-Meterai Dibubuhkan HR]] (2026-09-11). Tak pernah diratifikasi. Pemilik proses memilih tanda tangan tidak tersertifikasi dengan PIN dan e-Meterai yang dibubuhkan HR, tanpa PSrE, e-KYC, maupun `contract-service`. Isi di bawah dipertahankan sebagai rekaman usulan.
- **Tanggal**: 2026-07-18 (revisi 2026-09-11)
- **Konteks dok**: [[HRIS - Kontrak Kerja Elektronik (e-Signing & e-Meterai)]] · [[HRIS - Personalia]] · [[HRIS - Recruitment]] · [[Microservices - Employee Service]] · [[API - Employee Service]] · [[REF - Kepemilikan Data]] · [[CORE - HRIS Orchestrator]] · [[ADR - 0002 Database-per-Service]] · [[ADR - 0013 HRD Documents]]

> Catatan penomoran: penomoran ADR vault saat ini **tidak unik global** (ada tabrakan 0007/0013/0015/… antara seri HR-Core dan seri Retur/Sales-Finance). ADR ini memakai **0019** = nomor bebas global berikutnya untuk menghindari tabrakan baru.

## Revisi 2026-09-11: pondasi kontrak dibangun di employee-service, bukan di service baru

Bagian Context, Decision, dan Consequences di bawah dipertahankan apa adanya sebagai rekaman usulan 2026-07-18. Kodenya sudah bergerak, dan beberapa premisnya tak berlaku lagi (diverifikasi ke `bip-erp` `origin/main` `915ca2f8`, 2026-09-11).

**Yang sudah dibangun**: modul riwayat kontrak di [[Microservices - Employee Service]], koleksi `employee_contract` (rute di [[API - Employee Service]] §Kontrak Kerja). Penandatanganannya sendiri tetap terjadi **di luar sistem**: field `EmployeeContract.File` didefinisikan sebagai lampiran PDF yang *sudah* bertanda tangan digital (`shared-library/models/employee/models.go`).

**Selisih terhadap Decision**:

| Decision (usulan 2026-07-18) | Kenyataan di kode |
|---|---|
| §1 service baru `contract-service` memegang template, approval, arsip, dan audit | `contract-service` belum ada. Record kontrak dan arsip PDF ada di employee-service. Template, approval, dan jejak audit tanda tangan belum ada di mana pun |
| §3 `new_hire` dipicu orkestrator setelah create-employee commit | kontrak pertama sudah dibentuk **di dalam** transaksi create-employee (`kontrakPertama`, `services/employee/func.go`). Pemicu tanda tangan belum ada |
| §3 pengingat otomatis TBD karena tak ada cron | employee-service sudah menjalankan `robfig/cron` (`services/employee/cron.go`). Yang belum ada adalah pengingat kontraknya |
| §5 arsip di MinIO prefix `contract/` + referensi di `work_document` | arsip di field `employee_contract.file`, object key `employee/<employee_id>/contract/<contract_id>/`. `work_document` tidak dipakai |
| Context: "hanya view monitoring `GET /contract`" | ada riwayat per karyawan, nomor otomatis, lampiran PDF, dan ringkasan |

**Konsekuensi yang mengikat keputusan berikutnya**: [[REF - Kepemilikan Data]] menetapkan `employee_contract` sebagai pemilik fakta "kontrak kerja dan riwayatnya", dan `work_data.employment_type`/`contract_ending` hanya boleh ditulis modul kontrak. Bila e-signing kelak dibangun di service terpisah, service itu **tidak boleh** menjadi pemilik kedua record kontrak, jadi §1 dan §5 wajib diputuskan ulang saat ADR ini diratifikasi. Celah pondasi yang harus ditutup lebih dulu (nomor kontrak tak unik, lampiran bisa diganti, karyawan tanpa akses ke kontraknya) dicatat di [[HRIS - Kontrak Kerja Elektronik (e-Signing & e-Meterai)]] §Pondasi yang Sudah Ada.

## Context

Penerbitan kontrak kerja (PKWT/PKWTT) masih **berbasis kertas**: cetak (~10 lembar), materai fisik, tanda tangan basah dua pihak, serah-terima fisik saat onboarding, arsip di berkas kepegawaian. Akibatnya onboarding lambat (kontrak sering menyusul setelah karyawan bekerja), berkas mudah hilang, dan masa berlaku PKWT sulit dipantau otomatis (risiko uang kompensasi & kepatuhan PP 35/2021).

Yang **sudah ada** di kode (grounded): hanya **view monitoring** `GET /contract` di [[Microservices - Employee Service]] (`contract_status` dari `work_data.employment_type` + `contract_ending`) dan slot FE `Contract.file_object?`. **Tidak ada** e-signing / tanda tangan digital / e-Meterai di seluruh `bip-erp`. Administrasi kontrak/PKWT dikelola di [[HRIS - Personalia]].

Kendala legal yang membentuk keputusan:
- **TTE tersertifikasi** hanya sah dari **PSrE** berlisensi Komdigi (UU ITE / PP 71/2019). **e-Meterai** hanya sah dari **Perum Peruri** (UU 10/2020 / PP 86/2021). Keduanya **tidak dapat dibangun sendiri** secara legal.
- Perjanjian kerja adalah **objek bea meterai**, **tetapi materai bukan syarat sah** perjanjian (fungsinya = alat bukti). → e-Meterai bersifat **kebijakan**, bukan keharusan teknis semua dokumen.
- Penandatangan **karyawan (individu)** umumnya **belum bersertifikat** → butuh penerbitan sertifikat **on-demand via e-KYC** (NIK/Dukcapil + liveness) saat tanda tangan — pembeda utama vs kontrak B2B.

Konteks platform (grounded): `bip-erp` **database-per-service** ([[ADR - 0002 Database-per-Service]]), **tanpa event bus/message queue** (Redis hanya cache/queue), komunikasi bisnis = **HTTP internal** `/internal/...` (`routes.InternalRequest`, header `GatewayID`).

## Decision

1. **Bangun sendiri semua yang jadi kendali penuh** dalam **service baru `contract-service`** (pola [[Microservices - HRD Document Service]]: Go+Fiber+MongoDB, DB sendiri per [[ADR - 0002 Database-per-Service]], gateway `/api/contract/*`, auth SSO): template kontrak per jenis kepegawaian, alur persetujuan, arsip, jejak audit, konektor integrasi.
2. **Integrasikan HANYA dua fungsi tersertifikasi** — TTE (PSrE) & e-Meterai (Peruri) — **lewat API penyedia berlisensi**; jangan membangun sendiri (ilegal). Provider **TBD** (Tilaka/Privy/Mekari); kriteria utama: penerbitan sertifikat on-demand + e-KYC, harga per transaksi, kuota e-Meterai via API, opsi on-premise (kedaulatan data / UU PDP), SLA.
3. **Pemicu = pemanggilan HTTP** (tanpa event bus): `new_hire` disisipkan di [[CORE - HRIS Orchestrator]] **setelah `create-employee` commit** (best-effort, pola goroutine WA notif); `renewal`/`addendum` dari monitoring `GET /contract` via **aksi HR manual** (scheduler otomatis **TBD** — belum ada infra cron).
4. **Urutan e-Meterai → tanda tangan** agar TTE **mengunci dokumen ber-meterai** (integritas); dapat *bundled* tergantung provider. e-Meterai **diterapkan per kebijakan jenis kontrak**, bukan wajib semua.
5. **Arsip PDF final di MinIO** ([[Microservices - File Service]], prefix baru `contract/`) + referensi di employee `work_document` (`common.Document`). [[Microservices - HRD Document Service]] **tidak dipakai** untuk arsip (menyimpan Markdown `body_md`, bukan file binary) — hanya *pola* versioning/ack yang jadi acuan.
6. **Signing asinkron & human-in-the-loop** → `contract-service` memegang **state machine** + **penerima webhook** (pola gateway `/ext/webhook/:service` milik [[Microservices - Integration Service]]); callback **wajib idempoten**.
7. **RBAC**: role sistem modul baru (mis. `contract`) untuk approver, konvensi `system_roles` key = **modul** (bukan departemen).

## Consequences

- ➕ **Kendali penuh** atas proses bisnis + integrasi HRIS, sekaligus **patuh hukum** (fungsi tersertifikasi tetap lewat penyedia berlisensi).
- ➕ Onboarding cepat (karyawan tanda tangan jarak jauh sebelum/hari pertama), arsip tak tercecer, **masa PKWT terpantau otomatis**, jejak audit lengkap.
- ➕ Selaras arsitektur eksisting (pola service baru, HTTP internal, MinIO, Resend) — tanpa infra baru selain konektor eksternal.
- ➖ **Ketergantungan penyedia eksternal**: biaya per transaksi TTD, kuota & biaya e-Meterai, SLA di luar kendali.
- ➖ **e-KYC karyawan** menambah friksi & biaya (verifikasi identitas per orang, volume tinggi).
- ➖ Butuh **company/legal-entity master** (data & penandatangan pihak perusahaan) yang **belum ada** di `bip-erp`.
- ⚠️ **Pengingat perpanjangan otomatis** belum bisa event-driven (tak ada cron/bus) → sementara manual/poll.
- ⚠️ **Provider & urutan stamp/sign (bundled vs terpisah)** belum diputuskan → mempengaruhi detail alur.
- 🔗 [[Microservices - Employee Service]] perlu **endpoint internal baru** untuk write-back referensi PDF ke `work_document` + update `contract_ending`/`employment_type`.

## Dokumen Terkait

- [[HRIS - Kontrak Kerja Elektronik (e-Signing & e-Meterai)]] (desain lengkap: pemicu, pemetaan field, alur PSrE/e-Meterai, write-back) · [[HRIS - Personalia]] · [[HRIS - Recruitment]]
- [[Microservices - Employee Service]] · [[CORE - HRIS Orchestrator]] · [[Microservices - File Service]] · [[Microservices - Notification Service]] · [[Microservices - Integration Service]] · [[CORE - API Master Gateway]]
- [[ADR - 0002 Database-per-Service]] · [[ADR - 0013 HRD Documents]]
