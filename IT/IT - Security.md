## Deskripsi

*Pandangan **keamanan IT terpusat** untuk ekosistem bip-erp — mengonsolidasi kontrol keamanan yang saat ini tersebar di beberapa dok (auth, RBAC, jaringan, deploy, backup) menjadi satu gambaran utuh, sekaligus **memetakan gap** yang belum tergarap. Dok ini bersifat **overview + pointer**: detail tiap kontrol tetap di dok sumbernya.*

- **Status**: ⚠️ Parsial — sebagian kontrol sudah berjalan (✅), program keamanan terpusat (policy, incident response, dll) masih 🟡 konsep
- **Cakupan perlindungan**: seluruh aplikasi & service ERP bergantung pada kontrol auth/RBAC di sini; aset yang dilindungi mencakup **PII** (karyawan; kandidat — dari desain [[HRIS - Recruitment]]) & **kredensial pihak ketiga** (token Desty, OAuth marketplace, HMAC Accurate)

## Latar Belakang

- Kontrol keamanan **tersebar** di banyak dok → tidak ada gambaran menyeluruh maupun pemilik tunggal; gap (mis. incident response, patch) sulit terlihat.
- Permukaan serangan nyata: **portal publik** (guestbook, rencana lamaran publik recruitment), **webhook `/ext`** (akses tanpa JWT), **SSO** lintas-aplikasi, dan **kredensial pihak ketiga tersimpan**.

## Ruang Lingkup / Kontrol Keamanan

*Status per-item: ✅ sudah berjalan · 🟡 belum ada / konsep.*

- **Autentikasi & SSO** ✅ — JWT di gateway + **SSO one-time-code** (`/auth/sso/ticket` & `/auth/sso/redeem`) antar aplikasi internal. Detail: [[CORE - SSO Flow]], [[CORE - API Master Gateway]].
- **Otorisasi / RBAC** ✅ — `system_roles` (peta `module → role`: admin/supervisor/staff/security, dll) dipakai gateway untuk otorisasi; manajemen akun (aktif/nonaktif, reset, set role). Detail: [[IT - Employee System]].
- **Keamanan jaringan** ✅ — firewall & kebijakan akses jaringan (LAN/WiFi/perangkat). Detail: [[IT - Network Management]].
- **Keamanan deploy & secret** ✅ — secret deploy via GitHub Secret (tak disimpan di runner), deploy key read-only, secret mobile (Firebase/keystore) Base64 di Codemagic env. Detail: [[IT - CI-CD]].
- **Backup & enkripsi** ✅ — enkripsi backup + monitoring keberhasilan (alert bila gagal). Detail: [[IT - Backup & DR]].
- **Proteksi data & kredensial** 🟡 — klasifikasi data & kebijakan proteksi **PII** (karyawan/kandidat) dan **kredensial pihak ketiga** (Desty/marketplace/Accurate) belum terdokumentasi sebagai kebijakan.
- **Incident response** 🟡 — proses penanganan insiden keamanan belum ada.
- **Patch / vulnerability management** 🟡 — proses pemantauan kerentanan & cadence patch belum ada.
- **Keamanan endpoint / perangkat** 🟡 — kebijakan perangkat kerja/endpoint belum ada.
- **Audit keamanan IT** 🟡 — audit khusus security IT belum ada *(catatan: [[GA - Audit Internal System]] = audit kepatuhan GA, berbeda)*.

## Kendala

- Kontrol tersebar lintas dok tanpa **pemilik/pandangan tunggal** → gap mudah terlewat.
- Permukaan **publik** (`/public`) & **eksternal** (`/ext`, webhook tanpa JWT) butuh perhatian khusus — lihat [[CORE - API Master Gateway]].

## Belum Diputuskan (TBD)

- Pemilik proses keamanan & kebijakan (security owner) — IT sepenuhnya, atau lintas-fungsi?
- Skema **klasifikasi data** (publik/internal/rahasia) + aturan proteksi PII & kredensial.
- Proses **incident response** (deteksi → eskalasi → pemulihan → post-mortem).
- **Patch/vulnerability mgmt**: sumber info kerentanan & cadence patch.
- Keamanan **endpoint/perangkat** (mis. disk encryption, MDM) — perlu atau tidak?
- Apakah mengadopsi **framework/standar** formal (mis. ISO 27001/CIS) atau cukup baseline internal.

## Dokumen Terkait

- [[CORE - SSO Flow]] · [[CORE - API Master Gateway]] — autentikasi & gateway
- [[IT - Employee System]] — RBAC & manajemen akun
- [[IT - Network Management]] — firewall & jaringan
- [[IT - CI-CD]] — secret & keamanan deploy
- [[IT - Backup & DR]] — enkripsi & keandalan backup
- [[DB - Overview and Notes]] — penyimpanan data per service
- [[IT - Big Pictures]] — peta domain IT
