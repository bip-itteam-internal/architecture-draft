## Deskripsi

*Endpoint **recruitment-service** (ATS Fase 1-3 + adopsi struktur ERPGo Fase A–E + portal karir publik). Gateway: `/api/recruitment/*` (auth) & `/public/recruitment/*` (publik, tanpa JWT). RBAC `system_roles["hris"]`. Grounded ke `services/recruitment/routes.go` (branch `main`).*

- **Implementasi**: [[Microservices - Recruitment Service]] · **Status**: ⚠️ BE Fase 1-3 + master ERPGo (A–F) + portal publik (browse/apply/track) + requisition se-departemen — increment 2026-07-16 deployed & terverifikasi live di dev. **Custom Questions dihapus** (#486/#342). **hire→karyawan** (endpoint `link-employee`, PR #490) **merged, belum deploy**. **Link Form Feedback Interview** (`GET /interviews`, panel/location, feedback hardening — PR #536/#381) **merged & dilaporkan ter-deploy dev** (2026-07-18).
- **Konsumen publik**: [[APP - Portal Karir Bharata]]
- ⚠️ **Cakupan verifikasi 2026-09-10**: yang diperiksa ulang ke `routes.go` pada pass ini **hanya** blok **Stages** (tahap/tes/background check) dan **Interview Rounds**. Blok lain (Candidate `PUT /advance`, Offer `/candidates/:id/offer*`) **belum** diperiksa dan sudah terlihat menyimpang dari `routes.go` — jangan diperlakukan sebagai grounded sampai di-sync tersendiri.
- **Indeks**: [[API - Index]] · Role: `isSupervisor` (ajukan), `isHR`/`isHRSupervisor` (kelola/review **+ persetujuan final requisition** sejak 2026-07-22), `isApprover` (HR admin/Secretary — **tidak lagi dipakai di requisition**, masih dipakai untuk hire kandidat).

## Sistem
| Method | Path | Fungsi |
|---|---|---|
| GET | `/health` · `/me` | Health / identitas (+`is_hr`) |

## Job Requisition
| Method | Path | Fungsi | Role |
|---|---|---|---|
| POST | `/requisitions` | Ajukan permintaan posisi. **`department` diambil dari identitas pengaju, bukan body** (anti-spoof, PR #478). **PENGECUALIAN: jabatan berJENJANG direktur** (`position_items[].level_key` = `direktur`) boleh mengajukan untuk posisi di departemen **mana pun** — departemen diambil dari body. Jenjang ditanyakan ke employee-service `GET /master/departments` **hanya bila** departemen yang diminta berbeda dari departemen pengaju; gagal memastikan → **503**, bukan diam-diam memakai departemen pengaju. ⚠️ Corporate Secretary **TIDAK** termasuk (`common.SetaraDirektur` sempat dipakai sebagai sumbu tapi diganti — [[ADR - 0062 Jenjang Jabatan Menggerbangi Pengajuan Requisition Lintas-Departemen]]) | supervisor |
| GET | `/requisitions` · `/requisitions/:id` | List (HR semua / pengaju sendiri) / detail. **`?scope=department`** → SPV lihat requisition **se-departemen** (departemen dari identitas gateway; detail juga izinkan SPV se-departemen) — PR #470. Filter kini `$or[{department∈cakupan},{requested_by=pengaju}]`: pengaju SELALU melihat pengajuannya sendiri, termasuk yang dibuat Direktur untuk departemen LAIN (tanpa ini requisition lintas-departemen lenyap dari daftar portalnya) | auth |
| PUT | `/requisitions/:id` | Edit (saat Submitted/Revision). Departemen **dipertahankan** (edit tak memindahkan requisition) | pengaju |
| POST | `/requisitions/:id/resubmit` | Kirim ulang setelah revisi | pengaju |
| POST | `/requisitions/:id/hr-review` | Review kualifikasi. `action=approve` → **langsung `Approved`** (persetujuan final); `action=revision` → `Revision`. Menerima status sumber `Submitted` **maupun** `HR Reviewed` (agar requisition lama yang menggantung bisa diselesaikan) — PR #609 | HR supervisor |
| POST | `/requisitions/:id/reject` | Tolak. Alasan disimpan di `hr_note` (dulu `director_note`) | HR supervisor |

> **`POST /requisitions/:id/director-approve` DIHAPUS** (PR #609, 2026-07-22) bersama tahap persetujuan Direktur. Respons juga **tidak lagi memuat `can_director_approve`**; `can_hr_review` kini bernilai `true` untuk status `Submitted` maupun `HR Reviewed`.

## Job Posting
| Method | Path | Fungsi | Role |
|---|---|---|---|
| POST | `/postings` | Buka lowongan dari requisition Approved (+ generate `slug` unik dari title/posisi, untuk URL portal publik) | HR |
| GET | `/postings` · `/postings/:id` | List (`?status=&requisition_id=`) / detail | auth |
| PUT/POST | `/postings/:id` · `/postings/:id/close` | Edit / tutup lowongan | HR |

## Candidate
| Method | Path | Fungsi | Role |
|---|---|---|---|
| POST/GET | `/candidates` · `/candidates/:id` | Input/list (`?posting_id=&progress=&status=`)/detail | HR |
| PUT | `/candidates/:id` · `/advance` · `/reject` · `/withdraw` | Edit / gerak tahap (maju) / tolak / undur | HR |
| PUT | `/candidates/:id/link-employee` | Tautkan kandidat **Hired** ke karyawan yang dibuat di HRIS (wajib Hired & belum tertaut → set `employee_id`, `progress`→Onboarding, audit; cegah konversi ganda) — PR #490 | HR |
| POST/GET | `/candidates/:id/cv` · `/cv/preview` | Upload/preview CV (MinIO) | HR |
| POST/GET | `/candidates/:id/profile-image[/preview]` · `/cover-letter[/preview]` | Upload/preview foto profil & cover letter (MinIO) | HR |

## Stages & Offer
| Method | Path | Fungsi | Role |
|---|---|---|---|
| POST | `/candidates/:id/interviews` | Jadwalkan sesi interview (satu-satunya tahap yang **dijadwalkan**) | HR |
| GET | `/candidates/:id/stages` | Timeline tahap kandidat (kini hanya berisi `interviews`) | HR |
| PUT/DELETE | `/stages/:kind/:id` | Ubah / hapus record tahap (`:kind` yang dikenal saat ini hanya `interviews`) | HR |
| POST | `/candidates/:id/test-result` | **Rekam hasil babak bertipe tes** (Psikotest / Technical Test). Body: `round_id` (wajib, harus babak ber-`form_type: "test"`, kalau bukan → `400`), `result` (**Pass/Fail/Pending**, wajib), `score` (opsional), `notes`. **Upsert** per (`candidate_id`, `round_id`). Menggerakkan `progress` ke babak itu + status (Pass→`Pending`, Fail/Pending→`Hold`). Baris babak **Psikotest** juga ditulis **otomatis** saat sesi psikotes ditutup (langsung ke koleksi, bukan lewat endpoint ini, jadi progress/status tidak ikut bergerak): `result: Pending`, dan **(T0, bip-erp #1828)** `score` hanya untuk sesi `tuntas`; sesi terputus menulis baris **tanpa** `score`. ⚠️ `score` yang **tidak dikirim** ditulis `null` (`$set` apa adanya), jadi menyimpan Pass/Fail dengan isian Skor kosong menimpa skor otomatis psikotes (perbaikannya task T0b) | HR |
| GET | `/candidates/:id/test-results` | Daftar hasil tes kandidat, diperkaya `round_name` | HR |
| POST/GET | `/candidates/:id/background-check` | Rekam / baca Background Check (`verifications[]`, `reference`, `slik`, `decision`, `hr_note`) | HR |

### Psikotes online (sisi HR)

Rincian fitur: **[[HRIS - Psikotes Kraepelin]]**.

| Method | Path | Fungsi | Role |
|---|---|---|---|
| POST | `/candidates/:id/psikotes` | Terbitkan sesi psikotes + kirim magic link ke email kandidat (best-effort). **(2026-09-11, belum merged)** Body `{paket_id}` untuk tes berpaket atau `{config}` untuk Kraepelin lama; bagian yang belum siap atau soal yang jumlah kuncinya tak sesuai menggagalkan terbit dengan pesan. Balasan `{session_id, status, link}` (tanpa alamat email). Kandidat yang **sudah punya sesi → `409`** (sarankan Terbitkan Ulang). Babak `"Psikotest"` belum ada di master → `400` | HR |
| POST | `/candidates/:id/psikotes/reissue` | Terbitkan ulang. **`alasan` wajib** (kosong → `400`), body lain sama dengan terbit; sesi baru disiapkan dulu baru sesi lama dihapus, sehingga token lama mati | HR |
| GET | `/candidates/:id/psikotes/report` | Laporan individual (metrik 4 kategori + skor keseluruhan + `selesai_karena`; **(T0, bip-erp #1828)** + `col_index` = jumlah kolom yang sempat dikirim). **(2026-09-11)** Sesi paket + `paket_nama` dan `bagian[]` (`nama`, `jenis_jawaban`, `status`, `selesai_karena`, waktu, dan salah satu `kraepelin`/`pilihan_ganda`/`disc`; hanya hitungan). **Tidak memuat soal/kunci jawaban**. Kandidat tanpa sesi → `404 {"error": ...}` | HR |
| GET | `/candidates/psikotes/status` | Status **massal** untuk polling tabel (banyak id sekaligus, satu kueri `$in`). Tiap baris: `candidate_id`, `status`, `col_index`, `total_kolom`, `issued_at`, `last_seen_at?`; **(T0)** + `selesai_karena?` (omitempty, hanya sesi `finished`); **(2026-09-11)** sesi paket + `paket_nama`, `total_bagian`, `bagian_index`, `bagian_nama` (omitempty). **Tanpa** skor/kategori, dikunci test allowlist | HR |

> ⚠️ **`/candidates/psikotes/status` WAJIB terdaftar sebelum `GET /candidates/:id`**, kalau tidak ia tertelan sebagai permintaan kandidat ber-id `"psikotes"` dan membalas 200 berisi data yang salah, bukan 404. Di kode ada test yang mengunci urutannya.

> ⚠️ **Cache gateway 3 menit.** `GET /api/recruitment/*` di-cache api-gateway (modul `recruitment` tidak ada di `noCacheModules`), dan penutupan sesi oleh kandidat atau sweep tidak mengosongkannya. ✅ **(T0a, bip-erp #1832, merged 2026-09-11 `4ef28e21`)** Status massal, laporan psikotes, dan `/candidates/:id/test-results` dikecualikan lewat `noCacheRoutes`; di dev terverifikasi hari itu (tak pernah `X-Cache: HIT`, 0 kunci Redis). Naik di prod 2026-09-11 (biner memuat `psikotes/report`); periksa header `X-Cache` saat verifikasi. Path ketiganya tertulis juga di `api-gateway/redis.go` dan dijaga test `TestRuteYangDisalinKeNoCacheGatewayTetapTerdaftar`, jadi rename salah satunya wajib menyunting gateway juga. Rute recruitment lain tetap di-cache.

> ⚠️ **Endpoint per-tahap lama SUDAH TIDAK ADA** (diverifikasi ke `routes.go` 2026-09-10): `POST /candidates/:id/screening`, `/technical-test`, `/psychotest`. Screening jadi keputusan manual tanpa endpoint sendiri; tes dan psikotes menyatu jadi **satu jalur `/test-result` berbasis babak**. Contoh `curl` ke `/psychotest` yang masih beredar di `docs/recruitment-api.curl.md` (repo `erp`) ikut usang.
| POST | `/candidates/:id/offer` | Terbitkan offer (→ Offering) | HR supervisor |
| POST | `/candidates/:id/offer/letter` | Unggah surat penawaran PDF (MinIO) + email kandidat | HR supervisor |
| POST | `/candidates/:id/offer/accept` · `/offer/decline` | Respon offer | HR |
| POST | `/candidates/:id/hire` | Hire (butuh offer Accepted) → set `Hired` + onboarding handoff `/onboarding/register` (aktivasi akun). Pembuatan **data karyawan** dilakukan terpisah di HRIS "Tambah Karyawan" (dari kandidat) → `link-employee` | approver |
| GET | `/audits` | Audit log keputusan | HR admin |

### Katalog psikotes (sisi HR)

**(2026-09-11, bip-erp `feat/recruitment-psikotes-multi-jenis`, belum merged.)** Rincian aturan dan alur: [[HRIS - Bank Soal dan Paket Psikotes]]. "lihat" = `PermRecruitmentView` + `isHR`; "tulis" = `PermRecruitmentWork` + `isHR`.

| Method | Path | Fungsi | Role |
|---|---|---|---|
| GET | `/psikotes/tipe` (`?active=true`) · `/psikotes/tipe/:id` | Daftar/detail tipe + `total_durasi_detik`, `jumlah_soal` per kode subtes, `kesiapan`, `subtes_kurang`, `dipakai_paket` | lihat |
| POST/PUT/DELETE | `/psikotes/tipe` · `/psikotes/tipe/:id` | Buat/ubah/hapus tipe; `kode` dibuat server. `jenis_jawaban` di luar tiga nilai → `400`. Tipe bersoal: ganti jenis, buang subtes bersoal, atau ganti `jumlah_jawaban` subtes bersoal → `409`. Hapus tipe bersoal atau dipakai paket → `409` | tulis |
| GET | `/psikotes/item?tipe_id=` | Daftar soal satu tipe, **termasuk kunci dan dimensi DISC**; karena itu digerbang setara tulis, bukan lihat | tulis |
| POST/PUT/DELETE | `/psikotes/item` · `/psikotes/item/:id` | Buat/ubah/hapus soal, divalidasi terhadap tipenya (opsi 2 sampai 6, kunci sebanyak `jumlah_jawaban`, DISC tepat 4 kata berdimensi sah, gambar berpola kunci) | tulis |
| PUT | `/psikotes/item-urutan` | `{tipe_id, subtes_kode, ids}`: urutan baru satu subtes (tombol naik/turun) | tulis |
| POST | `/psikotes/impor-item` | `{tipe_id, dry_run, expected_hash, baris[]}`, maks 500 baris, divalidasi per baris. `dry_run` membalas `{baris[], valid, ditolak, hash}`; simpan wajib membawa hash yang sama, beda → `409` | tulis |
| POST | `/psikotes/gambar` | Multipart `file`, maks 2 MB (`413`); PNG/JPG/GIF/WEBP ditentukan dari isi berkas (lainnya `415`). Balasan `{gambar: <kunci>}` | tulis |
| GET | `/psikotes/gambar/:nama` | Pratinjau gambar untuk HR | lihat |
| GET · POST/PUT/DELETE | `/psikotes/paket` · `/psikotes/paket/:id` | Paket berurutan + `siap`, `total_durasi_detik`, kesiapan per bagian | lihat · tulis |

> `item-urutan` dan `impor-item` sengaja **satu segmen**, bukan `/psikotes/item/urutan`, supaya tak bersaudara dengan `/psikotes/item/:id` dan urutan pendaftaran rute tak menentukan kebenarannya. Semua perubahan tercatat di audit: `psikotes_tipe.*`, `psikotes_paket.*`, `psikotes_item.created|updated|deleted|reordered|imported` (ubah soal membawa penanda "kunci diubah" **tanpa nilai kuncinya**), `psikotes_gambar.uploaded`.

## Interview Rounds & Feedback (Fase F — adopsi ERPGo)
| Method | Path | Fungsi | Role |
|---|---|---|---|
| POST/GET | `/masters/interview-rounds` | **Katalog babak GLOBAL** (bukan lagi per lowongan). Field: `name`, `sequence_number`, `status` (`active`/`inactive`), `sends_feedback_link`, **`form_type`**. Di-seed 7 babak baku saat startup, idempoten (`$setOnInsert`) sehingga perubahan HR tak ketimpa | HR |
| PUT/DELETE | `/masters/interview-rounds/:id` | Ubah / hapus babak | HR |

> **`form_type` (5 nilai):** `generic` · `hrd_interview` · `user_interview` · `background_check` · `test`. Kosong dianggap `generic` (fallback babak lama). Nilai di luar itu ditolak `400`. Babak ber-`form_type` `test` atau `background_check` **tidak dijadwalkan** lewat Proses Seleksi, hasilnya direkam lewat endpoint hasil di atas. Babak baku ber-`test`: **Psikotest** (urutan 3) dan **Technical Test** (urutan 5).
>
> ⚠️ Rute lama **`/postings/:id/rounds`** dan **`/rounds/:id`** sudah tidak ada. Lowongan kini hanya **memilih** babak dari katalog lewat `round_ids[]`.
| GET | `/interviews` | **Semua** sesi interview (terbaru dulu), diperkaya nama/posisi kandidat + status feedback `feedback_submitted`/`feedback_total` — sisi HR (menu **Interviews**) — PR #536 | HR |
| GET | `/interviews/assigned` | Sesi interview yang menugaskan saya sebagai pewawancara (+ nama/posisi kandidat + jawaban saya). Dipakai halaman link `/interview-feedback/:id`; menu "Interview Saya" sendiri sudah dihapus dari navigasi (dormant) | auth |
| POST | `/interviews/:id/feedback` | Kirim/**ubah** penilaian (rating 1-5 + recommendation). **Upsert** per (interview, pewawancara) → tak dobel. Boleh **pewawancara sesi ATAU HR**. **`interviewer_id`** di body hanya dipakai bila pengirim **HR** (rekap atas nama pewawancara lain) — non-HR **selalu** JWT sendiri (PR #536) | auth |
| GET | `/interviews/:id/feedback` | Lihat semua feedback (rekap panel) | HR |

> **Interview orchestration (#498/#356, 2026-07-17):** `POST /candidates/:id/interviews` menerima **`round_id`** (tautkan sesi ke babak per-lowongan) & mengirim **notifikasi inbox** ke tiap pewawancara (`interviewers[]` + `interviewer` tunggal, dedup). Feedback **`requireAuth`** (pewawancara mengisi sendiri) + **upsert** (satu feedback/pewawancara, editable). FE menampilkan **rekap panel** (rata-rata per dimensi + tally rekomendasi).
>
> **Link Form Feedback Interview (#536/#381, 2026-07-18 — merged):** body juga menerima **`panel[]`** (snapshot pewawancara `employee_id`/`name`/`email`, untuk alamat email) & **`location`** (teks bebas, terpisah dari `meeting_link`). Untuk stage **User/Final**, tiap pewawancara di `panel[]` yang punya email dapat **email undangan** (jadwal + tombol **"Buka Form Feedback"** → halaman login-gated `/interview-feedback/:id`) — **menggantikan** menu "Interview Saya" sebagai jalur pengisian. Stage **HR**: tanpa email (HR isi dari detail kandidat). Kandidat menerima email jadwal terpisah (**semua stage**, tanpa link form). Detail: [[Microservices - Recruitment Service]].

## Master & Form Builder (adopsi ERPGo)
| Method | Path | Fungsi | Role |
|---|---|---|---|
| CRUD | `/masters/job-types` · `/masters/candidate-sources` · `/masters/interview-types` | Lookup (list/get/create/update/delete) | HR |
| CRUD | `/locations` | Master lokasi kerja (list/get/create/update/delete) | HR |

> **Custom Questions dihapus** (BE #486 / FE #342, 2026-07-16): endpoint `/questions` (form builder) + field `application_questions`/`custom_answers` **tak ada lagi** — portal karir memakai field native `candidate`. BSON lama diabaikan saat decode (tanpa migrasi).

> **Onboarding checklist (versi lama) dihapus** (2026-07-18): endpoint `/checklists` · `/checklists/:id/items` (template) **dan** `/candidates/:id/onboarding*` (instance per-kandidat) **tak ada lagi** — komponen FE-nya yatim/tak pernah dirender (dead code). **DIBANGUN ULANG 2026-07-26** dengan endpoint & model baru (`/onboarding-templates*`, `/onboarding-instances*`, `/onboarding-tasks/assigned`) — lihat section **Onboarding Checklist** di bawah. Performance Review Onboarding tetap terpisah.

## Performance Review Onboarding (⚠️ PR #493/#349 — belum merged/deploy)
> Digitalisasi Form Review Performance Masa Evaluasi (dulu Google Form). Peserta = **karyawan masa evaluasi** (`employment_type` "PKWT (Evaluasi)"); penilai = karyawan mana pun (identitas SSO). Peserta tak boleh menilai dirinya sendiri. Kriteria 7+3 **konstanta** (purpose-built, bukan form builder).

| Method | Path | Fungsi | Role |
|---|---|---|---|
| POST | `/onboarding-reviews` | HR buat sesi `{employee_id, peserta_name, peserta_position, peserta_department, scheduled_at, location, reviewers[]}` (peserta = karyawan masa evaluasi; peserta di-skip bila ikut `reviewers[]`) → undang penilai (inbox + email best-effort) | HR |
| GET | `/onboarding-reviews` | Daftar sesi (`?status=&employee_id=`) | HR |
| GET | `/onboarding-reviews/:id` | Detail + **rekap** (semua jawaban penilai) | HR |
| PUT | `/onboarding-reviews/:id/decide` | Keputusan `{outcome, note}` — outcome `Lulus`/`Diperpanjang`/`Tidak Lulus` → status `Decided` | HR |
| GET | `/onboarding-reviews/assigned` | Sesi yang ditugaskan ke saya (+ jawaban saya) | auth (penilai) |
| POST | `/onboarding-reviews/:id/response` | Submit/ubah jawaban `{ratings(7×1-5), strengths, improvements, recommendations}` — boleh edit sampai sesi `Decided` | auth (penilai) |

## Onboarding Checklist (rebuild 2026-07-26 — ✅ BE live dev, PR #692/#524)
> Template tugas onboarding karyawan baru + instansiasi per orang + penugasan **PIC lintas-tim** + notif inbox + pelacakan progres. **≠ Performance Review Onboarding** (yang itu penilaian masa evaluasi). Detail: [[Microservices - Recruitment Service]].

| Method | Path | Fungsi | Role |
|---|---|---|---|
| POST/GET | `/onboarding-templates` | Buat/daftar template (item: task/category/assigned_role/is_required/due_day) | HR |
| GET/PUT/DELETE | `/onboarding-templates/:id` | Detail / edit (full-replace items) / hapus | HR |
| POST | `/onboarding-instances` | Mulai onboarding: snapshot karyawan + template + `tasks[]` (item + PIC pilihan HR); BE hitung `due_date` (start+due_day), notif inbox tiap PIC | HR |
| GET | `/onboarding-instances` | Daftar (`?status=&employee_id=`) | HR |
| GET | `/onboarding-instances/:id` | Detail progres | HR |
| PUT | `/onboarding-instances/:id/complete` | Tutup manual (override) | HR |
| GET | `/onboarding-tasks/assigned` | Tugas onboarding yang ditugaskan ke saya, lintas instance | auth (PIC) |
| PUT | `/onboarding-instances/:id/tasks/:taskId` | Tandai status (Pending/In Progress/Done) + catatan; **auto-complete** instance saat semua item `is_required` = Done | auth (PIC/HR) |

> **Notif** = inbox best-effort; **email PIC ditahan** (menyusul, event `onboarding_task_assigned`). RBAC: kelola = isHR; PIC ditetapkan HR **manual** + guard assignee/HR pada update tugas.

## Publik (tanpa JWT — via gateway `/public/recruitment/*`)
| Method | Path (gateway) | Fungsi |
|---|---|---|
| GET | `/public/recruitment/postings` | Daftar lowongan Open (featured dulu) — tiap item memuat **`slug`** |
| GET | `/public/recruitment/postings/:id` | Detail lowongan. **`:id` menerima `slug` ATAU ObjectID** (dicoba ObjectID dulu; gagal parse → lookup by `slug`). Respons + `slug` & **`job_type`** (nama, hasil resolve `job_type_id` → master `job_types`) |
| POST | `/public/recruitment/apply` | Pelamar mendaftar sendiri (email + `posisi_dilamar` wajib). Respons **`201`** berisi **hanya** `{"message": "Lamaran terkirim. Konfirmasi telah dikirim ke email Anda."}` — **tanpa** `tracking_token`/`track_url` (fitur tracking dihapus, lihat di bawah). Kandidat lahir `progress: "CV Screening"`, `status: Pending`. **Dua bentuk body**: (a) JSON, atau (b) **`multipart/form-data`**: field `data` = JSON kandidat + file **`berkas`** = PDF **maks 10 MB** → MinIO `recruitment/cv/<candidate_id>/berkas.pdf` → set `cv_object` (HR buka via `GET /candidates/:id/cv/preview`) |

| Method | Path (gateway) | Fungsi |
|---|---|---|
| GET | `/public/recruitment/psikotes/:token` | Kandidat membuka sesi psikotes lewat magic link. **Tidak memuat digit soal**; sesi paket + `paket` (bagian, `bagian_index`, tanpa soal) |
| POST | `/public/recruitment/psikotes/:token/start` | Mulai mengerjakan. **Idempoten**: soal tidak digenerate ulang, lanjut dari kolom tersimpan |
| POST | `/public/recruitment/psikotes/:token/columns/:index` | Submit satu kolom. Index sama **menimpa**; index lama tidak menarik balik progres; panjang jawaban ditentukan **server** |
| POST | `/public/recruitment/psikotes/:token/finish` | Selesai + dinilai. Panggilan kedua tidak menghitung ulang |
| POST | `/public/recruitment/psikotes/:token/abandon` | Dipanggil browser lewat `navigator.sendBeacon`. Balasan **selalu** `{ok:true}` tanpa skor. **(2026-09-11)** Sesi paket hanya ditutup bila bagian Kraepelin sedang berjalan; di bagian lain no-op |
| POST | `.../:token/bagian/:b/mulai` | **(Tes berpaket, 2026-09-11, belum merged.)** Mulai bagian ke-b sesuai giliran. Bagian Kraepelin membalas config + kolom seperti `/start` lama |
| POST | `.../:token/bagian/:b/kolom/:index` · `.../bagian/:b/selesai` | Kirim kolom dan tutup bagian Kraepelin di dalam paket |
| POST | `.../:token/bagian/:b/subtes/:s/mulai` | Mulai subtes; server menulis deadline. Balasan soal **tanpa kunci/dimensi**, `soal_index`, `sisa_detik` (`null` bila tanpa timer) |
| POST | `.../:token/bagian/:b/subtes/:s/jawab` | `{nomor, pilihan}` (pilihan ganda) atau `{nomor, most, least}` (DISC, keduanya beda). Maju saja; lewat deadline plus 5 detik → `409 waktu_habis` |
| POST | `.../:token/bagian/:b/subtes/:s/selesai` | Tutup subtes; subtes terakhir menutup bagian, bagian terakhir menutup sesi |
| GET | `.../:token/gambar/:nama` | Gambar soal/opsi, **hanya** yang ada di snapshot sesi token itu (lainnya 404) |

> **Psikotes publik dijaga token, bukan sesi login.** Token 32 byte `crypto/rand` base64url, unik di level index. Tidak ada endpoint publik yang mengembalikan kunci jawaban, dimensi DISC, atau skor; soal CFIT/DISC dikirim **tanpa kunci** saat subtesnya dimulai. DTO-nya eksplisit dan ada test allowlist kunci JSON yang menggigit bila field internal bocor. Rincian: [[HRIS - Psikotes Kraepelin]] dan [[HRIS - Bank Soal dan Paket Psikotes]].

> **Galat mesin tes berpaket** berbentuk `{"error": <kalimat>, "kode": <kode>}` dengan kode `bukan_giliran`, `belum_mulai`, `waktu_habis`, `soal_terlewati`, `subtes_selesai` (409); career portal membaca `kode`. `POST .../columns/:index` dan `.../finish` menolak sesi paket (400). Gateway meneruskan semua rute ini lewat **satu rute umum berpenyaring** dengan limiter per token ([[CORE - API Master Gateway]]).

> **Galat publik yang dibaca halaman kandidat** (`psikotes_public_handlers.go`): token tak dikenal → `404 {"error": "sesi tes tidak ditemukan"}`; sesi sudah `finished` → `410 {"error": "sesi tes sudah selesai"}`. Kuncinya **`error`**, bukan `message`. **(T0, career-bharata #9)** Portal karir memetakan 404 ke layar "tautan tidak berlaku" tanpa Coba Lagi dan 410 ke layar "tes sudah selesai"; mengubah status kode ini di BE mengubah layar yang dilihat kandidat.

> ⛔ **`GET /public/recruitment/track/:token` SUDAH TIDAK BERFUNGSI** (diverifikasi 2026-09-10). Fitur lacak lamaran **dihapus** dari recruitment-service di `a298ba70` (2026-07-24, sudah di `origin/main`): `tracking_token`, `track_url`, dan handler `/public/track/:token` **nol hit** di seluruh `services/recruitment/*.go`, dan test template email menguncinya (`"applied: tombol tracking harus sudah dihapus"`).
>
> ✅ **Rute yatimnya sudah dibuang dari gateway** di bip-erp #1824 (merged 2026-09-10, `a0260e4d`). Biner API-Gateway **dev** yang naik sesudah merge tak lagi memuat string `recruitment/track` (0; kontrol positif `recruitment/psikotes` = 4, diukur 2026-09-10). **Prod ikut bersih sejak api-gateway prod di-deploy ulang 2026-09-11** (`recruitment/track` = 0, diukur hari itu). Sisi portal karir sudah bersih sejak awal: `career-bharata` **tidak punya** rute `/status` sama sekali.

> **Catatan kontrak `/apply`:** `posisi_dilamar` **wajib** dan **tidak** diisi server dari posting — divalidasi lebih dulu, jadi klien harus mengirimnya walau sudah kirim `posting_id`. `tanggal_lahir` = **RFC3339** (samakan dengan model employee agar mapping saat hire tidak perlu isi ulang — lihat [[HRIS - Recruitment]]). Upload berkas **backward-compatible**: body JSON tanpa file tetap diterima; berkas non-PDF / >10 MB → 400.

> **Catatan deploy (per 2026-07-16):** `slug`, `job_type` (resolve master), dan upload `berkas` **semua sudah live & terverifikasi** di dev (E2E multipart+berkas → `cv_object` → HR preview PDF valid). Deploy bip-erp **manual** (lihat [[Microservices - Recruitment Service]]).

## Dokumen Terkait
- [[Microservices - Recruitment Service]] · [[HRIS - Recruitment]] · [[Microservices - Employee Service]] · [[CORE - API Master Gateway]] · [[API - Index]]
