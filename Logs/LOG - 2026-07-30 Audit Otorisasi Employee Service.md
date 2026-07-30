Catatan **point-in-time** hasil audit otorisasi employee-service pada **2026-07-30**, termasuk pembuktian di produksi, forensik access log, dan sensus peran. Keputusan arsitektur yang lahir dari audit ini ada di [[ADR - 0031 Prefix internal Bukan Batas Keamanan]]; ini rekaman buktinya, bukan dokumentasi arsitektur.

## Ringkas

Dua lubang otorisasi ditemukan, ditambal, dan ter-deploy ke produksi pada hari yang sama. Forensik access log **tidak menemukan tanda keduanya pernah dipakai**. Rekomendasi yang diambil: perlakukan sebagai **kerentanan kritis yang ditangani**, bukan insiden kebocoran data, sehingga **tidak dilakukan reset password massal**.

## Temuan

| # | Temuan | Tingkat | Penutup |
|---|---|---|---|
| 1 | 16 rute tulis data karyawan tanpa gerbang apa pun (personal, work, schedule, dokumen, system-auth) | Kritis | PR bip-erp #780 |
| 2 | Payload system-auth menerima `system_roles` kiriman klien, sehingga penulis non-IT bisa mengangkat dirinya jadi admin pusat | Kritis | PR #780 (`saringPeranNonIT`) |
| 3 | `PUT /internal/auth/roles/:username` tanpa gerbang: menulis `system_roles` apa pun termasuk `group=admin` | Kritis | PR #781 (dihapus) |
| 4 | `PUT /internal/auth/disable/:employee_id` tanpa gerbang: menonaktifkan akun siapa pun | Tinggi | PR #781 (dihapus) |
| 5 | `PUT /internal/auth/change-password/:username` tanpa gerbang: orakel pengecekan password yang melewati limiter login | Sedang | PR #781 (dihapus) |
| 6 | `PUT /internal/schedule/factory-update` tanpa gerbang: memindahkan jadwal kerja siapa pun | Tinggi | PR #781 (digerbangi) |
| 7 | Lima rute baca membuka peran, device, dan seluruh dokumen pribadi (KTP, NPWP, kontrak) milik siapa pun | Sedang | PR #781 (digerbangi) |

Sebabnya satu: prefix `/internal/` bukan batas keamanan. Mekanismenya diuraikan di [[ADR - 0031 Prefix internal Bukan Batas Keamanan]].

## Pembuktian di produksi (tanpa mengubah data)

Memakai username yang sengaja tidak ada, sehingga `MatchedCount` nol dan tidak ada dokumen tersentuh:

```
SEBELUM tambalan
PUT /api/employee/internal/auth/roles/zzz-tidak-ada-probe-audit  -> 404 {"error":"User not found"}
GET /api/employee/internal/check/<id>/system-auth                -> 200 (peran orang lain terbaca)

SESUDAH tambalan (rute lenyap dari tabel rute, 404 bawaan Fiber)
PUT /api/employee/internal/auth/roles/zzz-fiktif            -> 404 Cannot PUT /internal/auth/roles/zzz-fiktif
PUT /api/employee/internal/auth/disable/zzz-fiktif          -> 404 Cannot PUT /internal/auth/disable/zzz-fiktif
PUT /api/employee/internal/auth/change-password/zzz-fiktif   -> 404 Cannot PUT /internal/auth/change-password/zzz-fiktif
```

`404 {"error":"User not found"}` adalah 404 **dari handler**, artinya request menembus seluruh otorisasi. `404 Cannot PUT ...` adalah 404 **bawaan Fiber** untuk rute yang tidak ada di tabel rute. Perbedaan itulah buktinya.

Verifikasi bahwa tambalan tidak mematikan alur sah (token `it:supervisor` + `hris:staff`): rute tulis karyawan tetap sampai ke validasi (400, bukan 403), `internal/check/../system-auth` 200, `internal/documents/..` 200, `attendance internal/fingerprint/list` 200, direktori `employee/list` 200, login normal, log service tanpa panic.

## Forensik: apakah lubangnya pernah dipakai

`system_authentication` tidak punya `updated_at`/`updated_by` dan tidak ada koleksi riwayat, jadi database **tidak bisa** menjawab. Sumber yang mencatat path lengkap adalah access log Nginx Proxy Manager (`npm-npm-1:/data/logs/*access.log*`, termasuk arsip `.gz`).

Cakupan yang diperiksa: **3 sampai 30 Juli 2026, 5.535.504 baris**. Seluruh baris yang memuat `internal/` berjumlah 144, dan semuanya terjelaskan:

| Path | Hit | Keterangan |
|---|---|---|
| `/internal/security/login` | 96 | pemindai internet acak (UA "InfraSec Scanner"), produk lain, semua 404 |
| `/api/attendance/internal/fingerprint/list` | 40 | pemakaian FE yang sah, sudah bergerbang `RequireITStaff` |
| `/internal/.env` | 5 | pemindai mencari file env, 404 |
| `/internal/v2/config/mps_secret/ADM_SESSIONID` | 1 | pemindai, 404 |
| `/api/employee/internal/check/<id>/system-auth` | 1 | probe audit hari ini |
| `/api/employee/internal/auth/roles/zzz-tidak-ada-probe-audit` | 1 | probe audit hari ini |

**Nol permintaan** ke rute rentan selain probe audit itu sendiri.

## Sensus peran istimewa (2026-07-30)

Pemegang `system_roles.group = admin` (admin pusat lintas perusahaan), **8 akun**: 5 anggota Tech Development (Fullstack/Frontend/Backend Developer), Tech Development Supervisor, Internal Audit, HRD Supervisor, dan Direktur.

Pemegang peran modul `it`: **10 akun**, 9 di antaranya `supervisor`.

Tidak ada nama tak terduga, yang justru paling mungkin muncul kalau ada yang mengangkat dirinya sendiri. Dua hal yang perlu ditinjau pemilik proses, bukan temuan teknis: apakah **Internal Audit** dan **HRD Supervisor** memang perlu wewenang lintas perusahaan, dan satu akun dengan nilai peran kosong (`it: ""`) yang perlu dirapikan (nilai kosong tidak dihitung sebagai punya peran, jadi tidak berbahaya).

## Kesimpulan & batasnya

Diperlakukan sebagai **kerentanan kritis yang ditangani**, bukan insiden kebocoran data. Dasarnya: nol bukti eksploitasi di jendela yang tersedia, keadaan peran saat ini bersih, dan rute password tetap memverifikasi password lama sehingga tidak ada jalur pengambilalihan akun. Konsekuensinya, **tidak perlu reset password massal**.

Dua batas yang harus dibaca bersama kesimpulan itu:

1. Access log hanya mundur **27 hari**, sementara lubangnya ada jauh lebih lama. Ini bukti "tidak ada jejak", **bukan** "terbukti tidak pernah terjadi".
2. Tanpa jejak audit di `system_authentication`, kesimpulan ini tidak bisa diverifikasi ulang secara independen dari datanya sendiri. Penambahan `updated_at`/`updated_by` tercatat sebagai tindak lanjut di [[ADR - 0031 Prefix internal Bukan Batas Keamanan]].

Selain itu, access log hanya membuktikan tidak ada akses **dari luar lewat proxy**. Panggilan dari dalam Docker network (mis. dari container lain atau seseorang yang sudah punya akses server) tidak akan tercatat di situ, meski itu mensyaratkan akses server yang jauh lebih tinggi.

## Terkait

- [[ADR - 0031 Prefix internal Bukan Batas Keamanan]] (keputusan arsitektur hasil audit ini)
- [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] · [[CORE - RBAC dan Permission Set]]
- [[Microservices - Employee Service]] · [[CORE - API Master Gateway]] · [[CORE - IT Orchestrator]]
