Dashboard ini sepadan dengan Omnichannel dashboard pada umumnya. Omnichannel adalah dashboard yang menggabungkan beberapa data platform (Tiktok, shopee, lazada) menjadi satu. tantangan dashboard hanya get API dari banyak platform tersebut. 

Tantangan selanjutnya adalah integrasi ads dengan toko yang saling berkaitan. Hal ini perlu dilakukan untuk mendapatkan informasi omset pertoko.

Berikut rincian **Full Tech Spec, audit masalah teknis utama, solusi, scope kesulitan development dari nol, serta estimasi waktu untuk proyek dashboard backend campaign manager multi-akun/multi-platform (Node.js/Express atau Golang):

---

![[WhatsApp Image 2025-12-02 at 10.38.30 AM.jpeg]]
![[WhatsApp Image 2025-12-02 at 10.38.30 AM(1).jpeg]]
![[WhatsApp Image 2025-12-02 at 10.38.30 AM(2).jpeg]]
![[WhatsApp Image 2025-12-02 at 10.38.30 AM(3).jpeg]]
![[WhatsApp Image 2025-12-02 at 10.38.31 AM.jpeg]]

## 1. ** Tech Spec (Backend Dashboard Multi-Ads Manager)**

## **A. Stack & Arsitektur**

- **Backend:** Node.js (Express/NestJS) atau Golang (Gin/Fiber)
- **Database:** PostgreSQL, Redis (cache/scheduler opsional)
- **API Integration:** TikTok Ads API (upload, report), Shopee Partner API (report, upload jika support), Meta Ads, Google Ads (expandable)
- **Auth:** JWT user session, OAuth2 multi-account API integration
- **Storage:** Local server/S3/MinIO (creative images/video)
- **Scheduler/Worker:** Bull Queue/node-cron (Node), goroutine/robfig-cron (Go)
- **Frontend:** React.js/Next.js SPA dashboard, UI admin/operator
- **Deployment:** Docker, VPS internal (min 4 vCPU/8GB RAM), CI/CD pipeline (GitHub Actions)
- **Security:** Password bcrypt/argon2, RBAC middleware, encrypted token, HTTPS mandatory

## **B. Tabel Feature & Entity**

- CRUD user, ad account, campaign, creative asset
- Bulk/single campaign upload ke multi-account/platform
- Fetch/report metrics: spend, ratings, CTR, conversion, sales, status, export report
- Audit trail per activity/error
- RBAC role granuler (admin, head, manager, marketer)
- Scheduler/worker untuk job batch, retry, alert
- Backup/restore DB & assets, monitoring job/slowness/fail
- File validation, asset storage integrity

---

## 2. **Masalah Teknis Besar yang Pasti Muncul & Solusi**

## **A. Integrasi API Platform**

**Masalah:**

- **Rate-limit API:** Terlalu banyak request upload/fetch, blokir sementara.
- **Token/OAuth Error:** Banyak akun → token expired, revoke, batch job gagal.
- **API Platform berubah:** Endpoint, format, deprecation mendadak.

**Solusi:**

- Scheduling batch dengan throttling, status/retry otomatis, alert/rollback jika kena rate-limit.
- Refresh OAuth/token dijalankan background, alert kadaluarsa, fallback draft jika gagal.
- Modular adapter API client, patch/update cepat, test sandbox/prod environment.

## **Kesulitan:**

- Test & debug job bulk upload/report antar platform.
- Membaca dokumentasi API yang sering versi/akses berubah.
- Mengkoordinasi test case sandbox vs production.

---

## **B. Multi-Account, Token, Credential**

**Masalah:**

- Credential/token bocor = risiko seluruh akun terkena hack/fraud.
- Typo/manual input → campaign masuk akun salah.
- Mapping token-akun user harus tepat.

**Solusi:**

- Simpan token field encrypted DB + rotasi berkala.
- Validasi token setiap submit, audit log, preview campaign sebelum upload.
- RBAC permission granular (prevent privilege escalation).

**Kesulitan:**

- Membuat flow secure multi-token, multi-user tanpa bocor.
- Restore jika token expired/batch revoke.

---

## **C. Bulk Upload, Asset Handling, Scheduler**

**Masalah:**

- File tidak sesuai standar API (format, size, corrupt) → gagal upload.
- Worker stuck, job deadlock; bulk upload ratusan task sekaligus.
- Disk full saat upload asset massal.

**Solusi:**

- Validator file sebelum upload, compress otomatis.
- Task queue, retry/fallback job-worker, reschedule jika fail.
- Monitor disk usage; alert dan auto-clean/rollback asset gagal.

**Kesulitan:**

- Debug error asset di berbagai platform (dokumen API kadang ambigu).
- Mengelola worker-resume agar tidak duplikat atau partial fail.

---

## **D. Reporting & Data Sync**

**Masalah:**

- Fetch data report massal (multi-akun), time out, mismatch data dashboard asli.
- Long job = crash worker/server overload.

**Solusi:**

- Batch fetch & caching, raw response DB untuk audit.
- Worker monitoring, auto-restart scheduler jika stuck.

**Kesulitan:**

- Sinkronisasi data lintas banyak account, volume besar, limitasi resource.
- Komparasi metrik real vs dashboard platform, debug perbedaan data.

---

## **E. DB, Server, Reliability**

**Masalah:**

- Bulk process = DB lock, query lambat, upload/report hilang.
- Backup snapshot gagal/corrupt, risk loss data.
- Asset storage terselip/korup.

**Solusi:**

- Job resource monitoring, batch insert/update, auto rollback error.
- Automated daily & weekly backup, restore rapid on fail.
- Asset structure/checksum, folder integrity audit.

**Kesulitan:**

- Recovery dari backup pada traffic tinggi, test failover rutin.
- File recovery/scan corruption di storage

---

## **F. Keamanan & RBAC**

**Masalah:**

- RBAC error: user biasa ubah/upload/edit campaign semua akun.
- Logging aktivitas kurang detail, susah audit.
- Login brute-force attack, credential reuse

**Solusi:**
- Middleware RBAC per endpoint, logging semua perubahan penting.
- Password hash aman, rate limit login, alert lockout/bruteforce.

**Kesulitan:**
- Mendesain log/audit yang granular, mudah di-review/filter.
- Mapping edge-case role permission di multi-owner asset/campaign.

---

## 3. **Scope Kesusahan Development**
- Integrasi multi-platform workflow/testing sandbox-produk real.
- Membuat scheduler resilient (retry, rollback, job status, batch fail/fix)
- Secure credential/token multi-akun, audit okuRasi
- Asset/file error handling, mapping campaign-product-business logic
- Approval/preview proses sebelum upload massal (mitigasi human error)
- Test coverage dan failover scenario wajib untuk semua feature critical
- Backup, restore, monitoring job dan storage integritas, disaster recovery
- Logging, debugging, forensik audit semua action/error

---

## 4. **Mitigasi Kesulitan**
- Mulai MVP pada satu platform dulu, rilis bertahap.
- Sering review flow API, patch modular adapter.
- Automasi job only on tested batch, manual/rollback option on fail.
- Backup/snapshot before mass batch/critical job.
- Unit, integration test pada modul token, upload, RBAC, scheduler.
- Dokumentasi build, error, recovery flow.

---

## 5. **Estimasi Waktu Development Realistis**

| Tahap                                    | Estimasi Waktu  |
| ---------------------------------------- | --------------- |
| Planning/Database Design                 | 5–7 hari        |
| Setup Infra, Scaffolding Project         | 3–4 hari        |
| Backend Core CRUD & Auth/RBAC            | 2–3 minggu      |
| API Integrasi TikTok/Shopee/Meta         | 2 minggu        |
| Bulk Upload/Scheduler/Worker             | 1–1.5 minggu    |
| Frontend Dashboard MVP                   | 2 minggu        |
| Reporting/Monitoring, Audit Trail        | 1 minggu        |
| Backup, Restore, Log, Failover           | 4–6 hari        |
| Testing & QA (unit/integration/failover) | 1–1.5 minggu    |
| Documentation & Final Deploy             | 4–5 hari        |
| **Total Realistis (from zero)**          | **8–10 minggu** |

- **Tim efektif:** Minimal 2–3 dev (backend, frontend, devops/server)
- **Jika ingin enterprise quality atau advanced features:** Bisa mencapai 12–14 minggu

---

**Kesimpulan:**  
Proyek ini sangat menantang dari sisi teknis, workflow, security & audit. Estimasi waktu realistis: **8–10 minggu** (2–2.5 bulan), bahkan bisa lebih, mengikuti scope final dan business process internal.  
Kunci sukses: schedule bertahap, full modular, patching API cepat, backup/logging granular, robust failover.

Berikut adalah **template flowchart, contoh ERD, dan skema worker/scheduler untuk backend dashboard campaign manager** beserta **audit checklist utama** untuk pengembangan dari nol.

---

## 1. **ERD (Entity Relationship Diagram) Simplified**

- users: id, name, email, password_hash, role
- ad_accounts: id, platform, account_name, api_token, user_id, status
- campaigns: id, ad_account_id, name, asset_id, platform, start_date, end_date, status
- creative_assets: id, file_url, type, owner_user_id
- logs: id, user_id, campaign_id, action, message, timestamp
- reports: id, campaign_id, platform, metrics_json, fetched_at

---

## 2. **Flowchart (Proses Disederhanakan)**

**A. Campaign Upload**
1. User login (auth, RBAC)
2. User pilih ad accounts + upload campaign detail (+ asset)
3. Backend validate (format, size, permission)
4. Worker queue job upload (bulk/single) ➜ scheduler
5. Job worker upload campaign ke API |  
    └─ success: store campaign ID/result  
    └─ fail: retry/rollback & log
6. Notifikasi status + save activity ke [logs]

**B. Campaign Reporting**
1. Scheduler auto-fetch report dari platform per interval/batch
2. API call ke setiap ad_account, pull metrics
3. Store raw & processed metrics di [reports]
4. Email/notif jika error/mismatch > threshold
5. Update dashboard + logging

---

## 3. **Skema Worker/Scheduler**

- **Upload Job Queue (Bull/Go channel):**
    - Status: pending/processing/success/fail
    - Retry logic (max 3x, exponential delay)
    - Batch by platform/account, auto-adapt to API rate limit
    - On fail: log & fallback manual queue/review
        
- **Report Scheduler:**
    - Interval batch (misal per 2 jam, per akun)
    - Separate queue dari upload, bisa overlap parallel
    - On error: reschedule+alert admin

---

## 4. **Checklist Audit & Error**

- Semua API key/token dienkripsi, tidak pernah keluar di log/error
- Setiap aksi (upload, edit, delete) tercatat di [logs], dengan user ID, timestamp, IP
- RBAC: semua permission dicek sebelum tiap action critical
- Unit test: upload campaign, retry job worker, RBAC, reporting scheduler
- Data fetch mismacth >5% (dashboard vs platform) di-alert otomatis
- Daily backup: DB & asset file, success/fail dilaporkan ke admin
- Monitoring job stuck >1 jam = auto notifikasi dan restart worker
- Manual upload/retry minimal satu jalur (fallback SOP)
- Endpoint/integration API patch minimal 1 bulan sekali atau setelah ada update
- Penanganan error batch: partial fail tidak block seluruh queue, bisa resume

---

## 1. **ERD (Entity Relationship Diagram) Detail (Markdown)**


users  
- id (PK)  
- name  
- email  
- password_hash  
- role (ENUM: admin, manager, marketer)  
- status  
- created_at  
  
ad_accounts  
- id (PK)  
- platform (ENUM: tiktok, shopee, meta, google)  
- account_name  
- api_key  
- api_secret  
- access_token  
- refresh_token  
- token_expiry  
- user_id (FK → users.id)  
- status  
- created_at  
  
creative_assets  
- id (PK)  
- file_url  
- file_type (ENUM: image, video, text)  
- meta_json (resolution, size, checksum, etc)  
- owner_user_id (FK → users.id)  
- created_at  
  
campaigns  
- id (PK)  
- name  
- ad_account_id (FK → ad_accounts.id)  
- asset_id (FK → creative_assets.id)  
- objective  
- target (audience/region)  
- budget  
- start_date  
- end_date  
- platform (redundant, optional for fast query)  
- status (draft, pending, uploaded, failed, active, stopped)  
- api_campaign_id (campaign id dari platform)  
- created_by (FK → users.id)  
- created_at  
  
logs  
- id (PK)  
- user_id (FK → users.id)  
- campaign_id (FK → campaigns.id, optional)  
- ad_account_id (FK → ad_accounts.id, optional)  
- action (ENUM: upload, edit, report, fetch, delete, error)  
- message  
- status (success, failed)  
- timestamp  
  
reports  
- id (PK)  
- campaign_id (FK → campaigns.id)  
- fetched_at  
- metrics_json (meliputi: spend, ctr, cpc, sales, impressions, clicks, dsb)  
  
job_scheduler  
- id  
- type (campaign_upload, report_fetch, asset_upload)  
- params_json  
- status (pending, running, completed, failed)  
- retry_count  
- last_run_at  
- next_run_at  
- log
---

## 2. **UML Activity/Sequence Diagram (Detail Flow)**

## **Flow: Upload Campaign dari Dashboard**

## **Flow: Periodic Fetch Campaign Report**

---

## 3. **Workflow Gambar/Diagram (pseudo-Mermaid)**

## 4. **UML Sequence (kode-mockup)**

---

## Dokumen Terkait

- [[Sales - Big Pictures]] — peta domain Sales/Marketing
- [[Sales - Marketplace Integration]] — integrasi marketplace (sumber data ads/order)
- [[Sales - GMV Creative]] · [[Sales - TikTok Sentiment Pipeline]]
- [[Microservices - Integration Service]] — backend data GMS/GMV/ads

