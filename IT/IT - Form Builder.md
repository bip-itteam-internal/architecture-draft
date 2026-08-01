## Deskripsi

*Konsep **Form Builder** — pembuat form dinamis tanpa coding untuk kasus internal baru/ad-hoc. Bharata banyak memakai "form request" yang kini di-hardcode per kasus; Form Builder jadi fondasi reusable (buat form baru tanpa rilis kode). Rencana yang dulu ditunda **sudah dieksekusi**: backend lengkap ada di branch `feat/form-builder`, dengan scope yang **lebih luas** dari rencana asli.*

- **Status**: ⚠️ **Backend + FE kelola selesai di branch `feat/form-builder` (belum merge, belum deploy).** FE web berupa alat **kelola** saja (daftar + builder); **halaman analisa/export belum**, dan **pengisian di MyBharata belum ada**
- **Penempatan**: tooling platform (Tech Development), dipakai bersama HRGA
- **Implementasi**: [[Microservices - Form Builder Service]] · **FE web**: [[APP - Web ERP]] · **API**: [[API - Form Builder Service]]

## Latar Belakang

- Form yang ada hardcoded per kasus: [[HRIS - Employee Request & Approval]], [[HRIS - Leave Request]], [[HRIS - Overtime]], [[HRIS - Attendance Correction]], Form Permintaan Karyawan ([[HRIS - Recruitment]]), guestbook ([[GA - Guestbook System (Complete)]]). [[GA - Checklist Management]] mendekati tapi bukan form umum.
- Cocok untuk survei internal, deklarasi, pendataan mendadak, pendaftaran event — **tanpa** mengganggu form approval bisnis yang sudah matang.

## Perubahan Scope dari Rencana Asli

Rencana yang terkunci di dokumen ini sebelumnya (RBAC `it` saja, tanpa FE, tanpa analitik, tanpa mobile, dan menjanjikan "nol dampak ke service berjalan") **sudah tidak berlaku**. Yang dieksekusi:

| Aspek | Rencana asli | Yang dibangun |
|---|---|---|
| RBAC | `system_roles["it"]` saja | `it` **dan** `ga` (HRGA) |
| Hasil jawaban | export CSV saja | analisa per pertanyaan + tren harian + tingkat pengisian, **plus** CSV |
| Sasaran form | (tak ada) | semua / per departemen / per karyawan |
| Dampak ke service lain | "nol dampak" | **menyentuh [[Microservices - Attendance Service]]**: clock-in mobile bisa ditahan bila ada form wajib belum diisi |
| Multi-perusahaan | (tak dibahas) | `company_id` sejak awal ([[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]]) |

Yang **tetap** ditunda sesuai rencana asli: **upload file** dan **logika percabangan** (lompat seksi berdasarkan jawaban).

## Intersep Presensi

Kebutuhan yang memicu perluasan scope: HRGA ingin memastikan form tertentu (mis. deklarasi kesehatan) benar-benar diisi sebelum karyawan mulai bekerja. Keputusan yang diambil:

- **Per form** bisa diatur `block` (tahan clock-in) atau `warn` (hanya ingatkan). Default `warn`.
- **Hanya jalur mobile** yang ditahan. Mesin fingerprint tak punya layar untuk mengisi form dan tak membawa identitas JWT, jadi menahan di sana hanya menghasilkan karyawan yang tertahan tanpa cara menyelesaikannya. Clock-**out** juga tak ditahan — menahan orang pulang bukan tujuan fitur ini.
- **Gagal-terbuka.** Form Builder yang mati, lambat, atau membalas rusak **tidak** boleh berubah jadi pemadaman presensi; clock-in diteruskan.
- **Jendela tanggal wajib**, supaya gerbang yang dilupakan tidak menahan presensi selamanya.

Rinciannya di [[Microservices - Form Builder Service]] dan [[Microservices - Attendance Service]].

## Urutan Rilis yang Mengikat

**Mode `block` sebaiknya belum dinyalakan di produksi sampai MyBharata siap.** Keputusan menaruh pengisian sepenuhnya di mobile berarti karyawan yang tertahan gerbang belum punya jalan mengisi lewat web. Mode `warn` aman dipakai lebih dulu. FE web sudah memasang peringatan ini di layar pengaturan gerbang, tapi itu peringatan, bukan pencegah.

Deploy tetap **backend lebih dulu, FE menyusul**.

## Belum Diputuskan (TBD)

- Kapan di-merge & deploy (BE harus naik lebih dulu dari FE — lihat catatan urutan deploy di [[Microservices - Form Builder Service]]).
- Halaman **analisa & export** di [[APP - Web ERP]]: endpoint backend sudah siap tapi belum ada layarnya.
- Renderer pengisian di [[APP - MyBharata]] — belum dikerjakan sama sekali.
- Pencarian karyawan untuk sasaran per-orang (sementara diketik sebagai Employee ID per baris).
- Apakah form publik (tanpa login) akan didukung — belum dikerjakan.
- Apakah RBAC akan dinaikkan ke permission-set [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]].

## Dokumen Terkait

- [[Microservices - Form Builder Service]] · [[API - Form Builder Service]]
- [[HRIS - Employee Request & Approval]] · [[GA - Checklist Management]] · [[GA - Guestbook System (Complete)]]
- [[Microservices - Attendance Service]] · [[Microservices - File Service]] · [[CORE - SSO Flow]] · [[CORE - API Master Gateway]] · [[DB - Overview and Notes]] · [[ROADMAP]]
