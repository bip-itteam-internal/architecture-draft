**Status**: ✅ Implemented. Diputuskan dan dijalankan 2026-07-30, **live di dev dan produksi** (PR bip-erp [#780](https://github.com/bip-itteam-internal/bip-erp/pull/780) dan [#781](https://github.com/bip-itteam-internal/bip-erp/pull/781)), dengan uji penjaga di `services/employee/internal_routes_guard_test.go`. Cakupan yang sudah dibereskan baru **employee-service**; service lain menyusul (lihat Consequences).

## Context

Prefix `/internal/...` pada rute service bip-erp selama ini dibaca seperti jaminan jaringan, seolah hanya bisa dipanggil service lain. **Itu tidak benar**, dan dua mekanisme berikut adalah sebabnya:

- `api-gateway/main.go` mendaftarkan **satu catch-all** `api.All("/:module/*")` yang meneruskan **seluruh** sub-path `/api/<module>/*` apa adanya ke service tujuan. Tidak ada daftar rute yang diizinkan, dan tidak ada penyaringan path.
- `routes.Reroute` (`shared-library/routes/gateway_request.go`) **mengisi sendiri** header `BIP-Gateway-ID` dari env, sehingga `validation.ValidateGateway` di service tujuan **selalu** lolos untuk request yang datang lewat gateway.

Gabungan keduanya berarti satu-satunya syarat menjangkau rute `/internal/...` dari internet adalah **token login valid, peran apa pun**, termasuk karyawan biasa tanpa peran modul apa pun. Tidak ada pembeda antara request service-ke-service dan request dari internet, karena keduanya membawa gateway key yang sama.

Audit 2026-07-30 di employee-service menemukan akibatnya:

- **16 rute tulis data karyawan** (personal, work, schedule, dokumen, system-auth) tanpa gerbang apa pun, baik di middleware maupun di dalam handler. Terbukti dengan token supervisor manufaktur yang lolos sampai lapis validasi.
- Kedua handler system-auth menulis map kiriman klien apa adanya, sehingga pemegang hak tulis non-IT bisa **menyelipkan `system_roles`** ke payload, termasuk mengangkat dirinya jadi admin pusat.
- **Tiga rute tulis `/internal/auth/*`** tanpa gerbang dan **tanpa satu pun pemanggil** di seluruh repo (orchestrator, gateway, `erp-frontend`, `mybharata-app`):
    - `PUT /internal/auth/roles/:username` menulis `system_roles` apa pun termasuk `group=admin` (admin pusat lintas perusahaan), yaitu **eskalasi hak penuh**;
    - `PUT /internal/auth/disable/:employee_id` menonaktifkan akun siapa pun, termasuk seluruh direksi;
    - `PUT /internal/auth/change-password/:username` memverifikasi password lama (jadi bukan pengambilalihan), tapi menjadi **orakel pengecekan password** yang melewati `strictLimiter` di `/auth/login`.
- Enam rute baca membuka data orang lain ke siapa pun yang bisa login: peran dan daftar device per akun, serta **seluruh dokumen pribadi** (KTP, NPWP, kontrak) beserta URL berkasnya.

Pembuktian di produksi dilakukan tanpa mengubah data, memakai username yang sengaja tidak ada sehingga `MatchedCount` nol: `PUT /api/employee/internal/auth/roles/<fiktif>` dijawab `404 {"error":"User not found"}`, yang berarti request **menembus seluruh otorisasi** dan hanya gagal mencocokkan dokumen.

Konteks ini melengkapi [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]], yang sudah mencatat 557 rute user-facing tanpa middleware (230 di antaranya operasi tulis) tapi memperlakukannya sebagai pekerjaan per-modul. Temuan ini menunjukkan sebagian dari rute itu **lebih terbuka dari yang diduga**, karena prefix `/internal/` tidak mempersempit apa pun.

## Decision

**`/internal/` adalah konvensi penamaan, bukan batas keamanan. Setiap rute wajib menggerbangi dirinya sendiri.**

Aturan turunannya:

1. **Tidak ada rute tanpa gerbang, apa pun prefiksnya.** Rute baru wajib memasang `common.Require*` sendiri. Asumsi "ini kan internal" tidak diterima sebagai alasan.
2. **Kode mati dihapus, bukan digerbangi.** Tiga rute `/internal/auth/*` di atas dihapus karena jalur sahnya sudah ada dan bergerbang (IT Orchestrator `PUT /roles/set` dengan `RequireITStaff`, yang menulis via `PUT /update/:employee_id/system-auth`). Memberi gerbang pada kode mati hanya menyisakan permukaan serang yang tak pernah dipakai.
3. **Memberi peran dipisah dari membuat akun.** Membuat/mengubah akun boleh HR (dipakai alur Buat Karyawan), tapi menulis `system_roles` hanya boleh peran `it`. Ditegakkan `saringPeranNonIT` yang **membuang** field `system_roles` dari payload (bukan menolak request utuh, karena alur Buat Karyawan mengirim satu payload gabungan) lalu mencatat percobaannya ke log.
4. **Pengecualian harus tertulis beserta alasannya.** Rute yang sengaja tanpa gerbang didaftarkan di `rutePolos` pada uji penjaga, dan **rute TULIS tidak pernah boleh masuk daftar itu**.
5. **Penjaganya berupa uji, bukan sekadar konvensi.** `internal_routes_guard_test.go` memaksa setiap rute `/internal/` bergerbang atau terdaftar, menjaga tiga rute yang dihapus tidak didaftarkan kembali, membuang entri pengecualian yang rutenya sudah tak ada, dan **menguji logika penjaganya sendiri dengan sumber palsu** supaya tidak menjadi uji yang tak pernah bisa gagal.

## Consequences

**Konsekuensi yang diterima:**

- **Gerbangnya `RequireHRISOrITStaff`, tingkat staf ke atas, bukan supervisor.** Itu tingkat yang dipakai pemanggil sahnya: IT Orchestrator bergerbang global `RequireITStaff`, HRIS Orchestrator menggerbangi per rute. Menaikkannya ke supervisor akan mematikan reset password dan pengelolaan akun yang memang dikerjakan staf IT.
- **`routes.InternalRequest(nil, ...)` tidak meneruskan `BIP-System-Roles`.** Rute yang dipanggil dengan ctx nil (mis. `callCekEndpoint` di HRIS Orchestrator untuk validasi duplikat saat membuat karyawan) akan **mati** kalau digerbangi. Karena itu `GET /internal/cek/:data` sengaja dibiarkan tanpa gerbang (responsnya hanya boolean duplikat) dan tercatat di `rutePolos`. Perbaikan yang benar: teruskan ctx dari pemanggil lebih dulu, baru gerbangi.
- **Penyembunyian di FE tetap bukan keamanan.** Konsisten dengan [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]: menu rapi tidak berarti endpoint aman.

**Yang belum dikerjakan (menyusul):**

- **Gateway belum menolak `/internal/` dari luar.** Itu pertahanan di tepi yang akan menutup kelas bug ini untuk **semua** service sekaligus, dan menurut audit ini lebih berbobot daripada menambal per service. Prasyaratnya perubahan FE: `erp-frontend` memanggil `/api/attendance/internal/fingerprint/{list,add,delete}` (ketiganya sudah bergerbang `RequireITStaff` di [[Microservices - Attendance Service]]), jadi endpoint itu perlu dipindah keluar namespace `/internal/` lebih dulu.
- **Service lain belum disapu** dengan pola yang sama: integration (241 rute telanjang), manufacture (95, seluruh WMS), attendance (45), insentive (32).
- **`/api/employee/auth/login` melewati `strictLimiter`.** Limiter hanya menempel di `/auth/login` milik gateway, sementara rute yang sama bisa dicapai lewat catch-all `/api/employee/*` dengan token valid.
- **`GET /list` memproyeksikan `system_roles`** ke setiap pemanggil ber-token bila query `role_system`/`role_value` diisi. Perbaikan yang aman: tetap izinkan **filternya**, tapi proyeksikan `system_roles` hanya untuk peran HRIS/IT. `erp-frontend` hanya memakai filternya (`use-employee-lookup.ts` untuk insentif) dan tidak membaca field perannya, jadi tidak ada yang pecah.
- **`system_authentication` tanpa jejak audit.** Tidak ada `updated_at`/`updated_by` dan tidak ada koleksi riwayat, sehingga "siapa mengubah peran ini, kapan" tidak bisa dijawab dari datanya sendiri. Ini yang membuat pemeriksaan insiden harus bersandar pada access log; lihat [[LOG - 2026-07-30 Audit Otorisasi Employee Service]].

**Yang belum diputuskan (TBD):**

- Apakah `/internal/` tetap dipakai sebagai penanda "rute service-ke-service" setelah gateway memblokirnya, atau namanya dipensiunkan supaya tidak lagi menyiratkan jaminan keamanan.
- Bagaimana membedakan request service-ke-service dari request lewat gateway secara teknis (mis. kunci terpisah per asal, bukan satu `INTERNAL_GATEWAY_KEY` yang dipakai keduanya).

## Terkait

- [[LOG - 2026-07-30 Audit Otorisasi Employee Service]] (catatan point-in-time: pembuktian, forensik access log, sensus peran)
- [[CORE - API Master Gateway]] (catch-all `/api/:module/*` dan `Reroute` yang mengisi gateway key)
- [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] · [[CORE - RBAC dan Permission Set]]
- [[Microservices - Employee Service]] (rute yang dihapus & digerbangi) · [[CORE - IT Orchestrator]] (jalur sah pemberian peran) · [[CORE - HRIS Orchestrator]] (pemanggil ctx nil)
- [[Microservices - Attendance Service]] (endpoint fingerprint yang menahan blokir gateway)
- [[ADR - 0003 SSO-only Gateway]] · [[APP - Web ERP]]
