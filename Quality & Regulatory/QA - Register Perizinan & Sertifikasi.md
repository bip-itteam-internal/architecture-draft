## Deskripsi

*Register Perizinan & Sertifikasi adalah workspace ERP pertama untuk posisi **Staf Legal**: satu daftar terpusat izin & sertifikat perusahaan (izin edar BPOM, sertifikat Halal, izin usaha, sertifikasi lain) berikut masa berlakunya, dengan penanda **alert H-90** sebelum kedaluwarsa. Dibangun sebagai bagian dari inisiatif "satu workspace per posisi" (branch `feature/workspace-position`) — memberi jejak kerja di ERP bagi posisi yang sebelumnya bekerja di luar sistem, sehingga KPI-nya kelak bisa dihitung otomatis. Fitur unggah PDF sertifikat dan register Kontrak/Dispute menyusul.*

- **Stack**: Go (Fiber, di-host di employee-service) + MongoDB (`legal_license`) + JWT/`system_roles` sebagai pembawa peran; frontend Next.js (App Router, TanStack Query).
- **Path di repo**:
  - Backend: `bip-erp/services/employee/{legal_perizinan.go,legal_kontrak.go,legal_dispute.go}` (routes+handler CRUD) · model `LegalLicense`/`LegalContract`/`LegalDispute` di `bip-erp/shared-library/models/employee/models.go` · collection `legal_license`/`legal_contract`/`legal_dispute` · RBAC `RequireLegalStaff`/`RequireLegalSupervisor` di `bip-erp/shared-library/common/roles.go` · seed department `legal` di `.../master_data.go` (`DefaultDepartments`). Unggah PDF memakai endpoint generik `POST /upload` yang sudah ada (`minio.UploadSingleHandler`).
  - Frontend: `erp-frontend/src/app/(main)/legal/{perizinan,kontrak,dispute}/page.tsx` · `erp-frontend/src/features/legal/{perizinan,kontrak,dispute}/*` (types, hooks fetch/upsert/delete, form modal) · helper unggah `features/legal/shared/upload.ts` · tiga entri menu `legal` di `src/components/layout/sidebar.tsx` · gating rute di `src/proxy.ts`.
- **Status**: ⚠️ Implemented (ada catatan). Ketiga register (Perizinan, Kontrak & SLA, Dispute & Advis) + **unggah PDF** **live di kode** (Go build + FE typecheck/eslint lolos), **belum diverifikasi runtime** di stack dev (butuh redeploy container + akun ber-role `legal`). Pemisahan ke service `legal` tersendiri **belum**.

## Persona / Pengguna

| Persona | Peran & Divisi | Akses/RBAC | Device |
|---|---|---|---|
| Staf Legal | posisi `Staf Legal` / department `legal` | role `legal:staff` — buat/edit/lihat izin | Web ERP |
| Legal Supervisor | department `legal` | role `legal:supervisor` — termasuk hapus izin | Web ERP |

- **Tujuan**: satu layar yang menjawab "izin apa yang segera habis" tanpa menyusuri folder/berkas fisik.
- **Pain point**: pemantauan masa berlaku izin hari ini manual (spreadsheet), sehingga perpanjangan sering baru disadari mepet tenggat.
- **Aksi utama**: catat izin baru, perbarui status perpanjangan, pantau alert H-90.

## Fitur (Sudah Diimplementasikan)

**Register Perizinan & Sertifikasi** — di-host di employee-service, dipanggil FE lewat prefix gateway `/api/employee/legal/...`:
- `GET /legal/licenses` — daftar izin (filter opsional `?license_type=` & `?status=`). Gate `RequireLegalStaff`.
- `GET /legal/licenses/:id` — detail satu izin (`_id` ObjectID). Gate `RequireLegalStaff`.
- `POST /legal/licenses` — buat izin (`name` + `license_type` wajib). Gate `RequireLegalStaff`.
- `PUT /legal/licenses/:id` — perbarui izin (metadata `created_*` dipertahankan). Gate `RequireLegalStaff`.
- `DELETE /legal/licenses/:id` — hapus izin. Gate `RequireLegalSupervisor`.
- Model `LegalLicense`: `name`, `license_type` (BPOM/Halal/Izin Usaha/Sertifikasi/Lainnya), `number`, `issuer`, `pic`, `status` (Aktif/Dalam Perpanjangan/Kedaluwarsa/Tidak Perlu), `issued_at` & `expires_at` (ISO `YYYY-MM-DD`, string agar bebas dari friksi parse `time.Time`), `notes`, `file_object`+`file_name` (PDF sertifikat), `metadata`.
- **Alert H-90 dihitung di sisi UI** dari `expires_at`: badge `H-{n}` (≤90 hari) / `Kedaluwarsa` (lewat tenggat) di halaman `/legal/perizinan`.

**Register Kontrak & SLA Legal** (`legal_kontrak.go`, collection `legal_contract`):
- `GET/POST /legal/contracts`, `GET/PUT /legal/contracts/:id` (gate `RequireLegalStaff`), `DELETE` (gate `RequireLegalSupervisor`). Filter `?contract_type=`&`?review_status=`.
- Model `LegalContract`: `name`, `counterparty` (pihak), `contract_type`, `value` (Rp), `review_status` (Draft/Review/Aktif/Selesai/Berakhir), `start_date`/`end_date`, `pic`, `notes`, `file_object`+`file_name`. **Alert jatuh tempo H-60** dari `end_date` di UI.

**Register Dispute & Advis Hukum** (`legal_dispute.go`, collection `legal_dispute`):
- `GET/POST /legal/disputes`, `GET/PUT /legal/disputes/:id` (gate `RequireLegalStaff`), `DELETE` (gate `RequireLegalSupervisor`). Filter `?dispute_type=`&`?status=`.
- Model `LegalDispute`: `title`, `dispute_type` (Vendor/Karyawan/Pajak/Regulasi/Lainnya), `counterparty`, `risk_value` (Rp), `status` (Terbuka/Proses/Advis/Selesai), `chronology`, `advice`, `notes`, `file_object`+`file_name`.

**Unggah PDF** — reuse endpoint generik `POST /api/employee/upload` (field multipart `file`, `minio.UploadSingleHandler`) yang sudah ada; FE (`features/legal/shared/upload.ts`) unggah lebih dulu, simpan `full_url`→`file_object` di payload. Tiap halaman menautkan `file_object` (buka PDF di tab baru).

- **Frontend**: tiga halaman list (Perizinan/Kontrak/Dispute) + modal create/edit (react-hook-form + zod) + hapus (ActionDialog) + unggah PDF. Tiga menu muncul di sidebar untuk pemegang role `legal`; rute `/legal/*` digating di `proxy.ts`.
- **RBAC & seed**: role key `legal` pada tier `system_roles` (`legal:staff|supervisor`), department `legal` di-seed di `DefaultDepartments` sehingga peran bisa di-assign lewat Master Data. Lihat [[CORE - RBAC dan Permission Set]].

## Belum Diimplementasikan / Catatan

- **Unggah PDF pakai bucket `uploads/` generik**: berkas disimpan lewat `POST /upload` (prefix `uploads/`, bukan `legal/...` khusus) dan `file_object` menyimpan `full_url` publik langsung — belum ada preview presigned/akses berbasis-peran. Cukup untuk sekarang; perlu ditinjau bila dokumen legal harus dibatasi.
- **Hosting sementara di employee-service** (TBD): dipilih agar tidak menambah modul gateway/URL baru (menghindari panic `ValidateInternalURL`) dan bisa langsung boot. Bila beban Legal tumbuh, ekstrak ke service `legal` tersendiri (env `LEGAL_MODULE_URL` + entri `InternalURL` di [[CORE - API Master Gateway]] + service data-owning meniru [[Microservices - Recruitment Service]]).
- **Verifikasi runtime**: build Go & typecheck FE lolos; smoke-test end-to-end (login akun `legal`, CRUD terhadap employee-service berjalan) belum dijalankan — perlu redeploy `docker-compose.dev.yml`.
- **Domain**: perizinan (BPOM/Halal/izin edar) masuk cakupan Quality & Regulatory; sebagian isi (izin usaha, kontrak) beririsan dengan fungsi Legal/GA. Posisi `Staf Legal` dulunya terdaftar di department `ga`/`secretary`; kini punya department key `legal` sendiri.

## Dependensi & Integrasi

- [[Microservices - Employee Service]] — host endpoint `/legal/*`, koneksi Mongo, seed department.
- [[CORE - API Master Gateway]] — meneruskan `/api/employee/legal/*` + header `BIP-*` (termasuk `BIP-System-Roles` yang dipakai `RequireLegal*`).
- [[CORE - RBAC dan Permission Set]] — role key `legal` pada tier `system_roles`.
- [[APP - Web ERP]] — modul frontend `legal` (sidebar, gating, halaman Perizinan/Kontrak/Dispute).

## Dokumen Terkait

- [[Microservices - Employee Service]]
- [[CORE - RBAC dan Permission Set]]
- [[APP - Web ERP]]
