## Deskripsi

*Endpoint service `learning` (modul gateway **`/api/learning/*`**, port internal 6987). Isinya modul pelatihan karyawan yang dipindah utuh dari [[Microservices - Employee Service]] pada LMS Fase 0. Implementasi & catatan: [[Microservices - Learning Service]] · konsep: [[HRIS - Training Program]].*

- **Status**: ✅ Grounded ke kode, live di dev + produksi 2026-08-06
- **RBAC**: tulis = `RequireHRISStaff`; GET terbuka di belakang gateway
- **Catatan pemindahan**: path internalnya **tidak berubah** dari versi lama, hanya prefix modulnya. `/api/employee/training/...` menjadi `/api/learning/training/...`

## Master — Jenis Pelatihan & Trainer

| Method | Path | Fungsi |
|---|---|---|
| GET · POST | `/training/types` | List / buat jenis pelatihan |
| GET · PUT · DELETE | `/training/types/:id` | Detail / ubah / hapus (by ObjectID) |
| GET · POST | `/training/trainers` | List / buat trainer, internal (`employee_id`) atau eksternal |
| GET · PUT · DELETE | `/training/trainers/:id` | Detail / ubah / hapus (by ObjectID) |

> ⚠️ Rute statik (`/types`, `/trainers`) **wajib** didaftarkan sebelum rute param `/training/:id`. Fiber mencocokkan per urutan registrasi; terbalik berarti `/training/trainers` ter-match sebagai `:id` bernilai `"trainers"`.

## Transaksi — Event Pelatihan

| Method | Path | Fungsi |
|---|---|---|
| GET · POST | `/training` (`?department_key=&status=`) | List / buat event pelatihan |
| GET · PUT · DELETE | `/training/:id` | Detail / ubah (guard transisi status) / hapus (cascade peserta) |

- **Department opsional** (peran penyelenggara, tidak membatasi peserta). Bila diisi, diverifikasi ke employee-service — lihat di bawah.
- Transisi status sah: `Scheduled → Ongoing → Completed`, dan `Scheduled|Ongoing → Cancelled`. `Completed` serta `Cancelled` terminal.
- `PUT` bersifat **full-replace**, jadi pemanggil wajib mengirim objek lengkap.

### Kode status verifikasi `department_key`

Verifikasi memanggil `GET {EMPLOYEE_MODULE_URL}/master/departments/{key}` di [[Microservices - Employee Service]]. Pemetaannya dipisah tegas supaya gangguan server tidak terbaca sebagai kesalahan input:

| Kondisi | Balasan |
|---|---|
| Departemen ditemukan (2xx) | Lolos |
| Departemen tidak ada (404) | **400** `department "<key>" not found` |
| employee-service membalas 5xx / status lain | **502**, pesan menyebut status, bukan "not found" |
| Tak terjangkau, atau `EMPLOYEE_MODULE_URL` kosong | **502**, pesan menyebut tak terjangkau / belum dikonfigurasi |

`department_key` kosong melewati pemeriksaan sepenuhnya.

## Peserta & Kehadiran

| Method | Path | Fungsi |
|---|---|---|
| GET · POST | `/training/:id/participants` | List / enroll peserta. Unique index `{training_id, employee_id}` menutup pendaftaran ganda secara atomik; **tanpa cap kapasitas** (kapasitas = jumlah peserta yang di-assign) |
| PATCH · DELETE | `/training/:id/participants/:employeeId` | Tandai kehadiran (boolean) / batalkan peserta |
| GET | `/training/history/:employeeId` | Riwayat pelatihan per karyawan |

## Lain-lain

| Method | Path | Fungsi |
|---|---|---|
| GET | `/health` | Health check, di belakang kunci gateway `BIP-Gateway-ID` |

## Belum Ada

Seluruh endpoint LMS (course, materi, bank soal, pre/post test, skoring, kurikulum jabatan, Talent Pool, penilaian trainer) **belum ada** — Fase 1 ke atas. Desainnya di [[HRIS - Training Program]].

## Dokumen Terkait

- [[Microservices - Learning Service]] · [[HRIS - Training Program]]
- [[API - Employee Service]] — rumah lama endpoint ini · [[API - Index]]
- [[CORE - API Master Gateway]]
