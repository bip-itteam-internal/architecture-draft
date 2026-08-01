## Deskripsi

*Endpoint **form-builder-service** (form dinamis + analisa jawaban + kepatuhan presensi). Gateway: `/api/form-builder/*`. RBAC dari map `system_roles`: kelola form butuh key `it` atau `ga` (staff/supervisor/admin); mengisi cukup terautentikasi. Grounded ke `services/form-builder/routes.go` + handler terkait (branch `feat/form-builder`).*

- **Implementasi**: [[Microservices - Form Builder Service]] · **Status**: ⚠️ (branch belum merge, belum deploy)
- **Indeks**: [[API - Index]]
- **Konsumen**: rute `/forms*` sudah dipakai FE kelola di [[APP - Web ERP]]. Rute **analitik/export** dan seluruh rute **`/me/*`** belum punya pemanggil — lihat catatan di [[Microservices - Form Builder Service]].

## Sistem
| Method | Path | Fungsi |
|---|---|---|
| GET | `/health` | Health check (di belakang gateway key) |

## Kelola Form (RBAC `it` / `ga`)
| Method | Path | Fungsi |
|---|---|---|
| POST | `/forms` | Buat form (lahir `draft`; `owner_module` wajib `it`/`ga` dan harus dikelola pemanggil) |
| GET | `/forms` | Daftar form modul yang boleh dikelola pemanggil (`?status=`, `?search=`, `?page=`, `?limit=` maks 100) |
| GET | `/forms/:id` | Detail + `response_count` |
| PATCH | `/forms/:id` | Sunting. `409` bila susunan field diubah padahal sudah ada jawaban. `owner_module` tak bisa dipindah |
| PATCH | `/forms/:id/status` | `draft`→`published`→`closed`. `409` bila mencoba mundur dari `published` ke `draft` |
| DELETE | `/forms/:id` | Hapus lunak (`deleted_at` + status `closed`) |

## Analisa & Export (RBAC `it` / `ga`)
| Method | Path | Fungsi |
|---|---|---|
| GET | `/forms/:id/analytics` | Rekap per pertanyaan + tren harian + tingkat pengisian (lihat bentuk respons di bawah) |
| GET | `/forms/:id/responses` | Daftar jawaban berhalaman (`?page=`, `?limit=` maks 200), terbaru dulu |
| GET | `/forms/:id/export` | CSV (`text/csv`). Header `X-Export-Truncated` muncul bila menyentuh batas 20.000 baris |

## Pengisian (karyawan terautentikasi)
| Method | Path | Fungsi |
|---|---|---|
| GET | `/me/forms` | Form terbit yang ditujukan ke pemanggil (+`submitted`, `blocks_attendance`, `gate_end_date`) |
| POST | `/me/forms/:id/responses` | Kirim jawaban. `403` bila bukan sasaran, `409` bila form tak `published` atau `single_response` sudah terpakai |
| GET | `/me/responses` | Riwayat jawaban sendiri |

> **Idempoten**: pengiriman identik dalam 2 menit dibalas `200 {"duplicate": true}` tanpa insert baru (sidik jawaban di-hash setelah kunci diurutkan, jadi payload yang disusun ulang saat retry tetap terdeteksi).

## Internal (dipanggil service lain)
| Method | Path | Fungsi |
|---|---|---|
| GET | `/internal/compliance` | Form wajib yang belum diisi: `{blocking:[{id,title}], warning:[...]}`. Dipakai [[Microservices - Attendance Service]] saat clock-in |

> **Identitas terkunci ke header.** Query `?employee_id=&department=&company_id=` HANYA dihormati bila request tak membawa `BIP-Employee-ID` sama sekali (ciri panggilan service-to-service). Request pemakai lewat gateway selalu terkunci ke dirinya sendiri — tanpa aturan ini rute ini jadi jalan mengintip form tertunda orang lain lintas perusahaan. Lihat [[ADR - 0031 Prefix internal Bukan Batas Keamanan]].

## Bentuk data penting

**Tipe field** (`fields[].type`): `short_text` · `long_text` · `number` · `date` (`YYYY-MM-DD`) · `time` (`HH:MM`) · `dropdown` · `radio` · `checkbox` (jawaban berupa array) · `scale` (rentang maks 10 langkah).

**Sasaran** (`audience.type`): `all` · `departments` (+`departments[]`) · `employees` (+`employee_ids[]`). `estimated_size` diisi manual sebagai penyebut tingkat pengisian; bila 0, `response_rate` tidak dikirim.

**Gerbang presensi** (`attendance_gate`): `{enabled, mode: "warn"|"block", start_date, end_date}`. Tanggal wajib **RFC3339** (`2026-08-01T00:00:00Z`); `"2026-08-01"` akan ditolak.

**Respons analytics**: `total_responses`, `unique_respondents`, `audience_size`, `sample_size`, `truncated`, `response_rate` (opsional), `daily[{date,count}]`, `fields[{key,label,type,answered,skipped,options[{option,count}],average,min,max,sample_text[]}]`. Saat `truncated=true`, `response_rate` sengaja tidak dikirim karena tak bisa dihitung jujur dari sebagian data.

## Dokumen Terkait

- [[Microservices - Form Builder Service]] · [[IT - Form Builder]]
- [[API - Index]] · [[API - Attendance Service]] · [[CORE - API Master Gateway]]
