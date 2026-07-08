## Deskripsi

*Sistem ini diposisikan sebagai **IT Helpdesk / ticketing**: desk dimiliki dan ditangani oleh **divisi IT**, sementara **semua divisi dapat membuat (submit) tiket** ke sana untuk meminta bantuan/penyelesaian dari IT. Dibangun sebagai task tracker dinamis berbasis Kanban yang terpusat agar konsisten dan dapat digunakan kembali.*

> [!note] Positioning vs implementasi
> Kode saat ini masih mendukung **multi-divisi** (Space per divisi + supervisor per divisi + admin/sekretaris lintas-divisi). Sesuai positioning baru sebagai IT Helpdesk, penanganan tiket difokuskan ke divisi IT dengan semua divisi sebagai requestor — pembatasan scope ke IT perlu dipertimbangkan di implementasi.

Saat ini sedang dikembangkan secara internal, repository-nya tercantum di bawah ini:
- [Repository frontend](https://github.com/bip-itteam-internal/bharata-task-manager-fe)
- [Repository backend](https://github.com/bip-itteam-internal/bharata-task-manager-be)

## Status Implementasi (Frontend — `bharata-task-manager-fe`)

- **Stack**: Next.js 16 (App Router) + React 19 + TypeScript; Kanban drag-drop `@dnd-kit`; `@tanstack/react-table`; axios + SWR; `react-hook-form` + zod; recharts; export Excel (`xlsx`)
- **Path**: `task-management/bharata-task-manager-fe` (repo terpisah), branch `feature/gateway-cutover`
- **Production**: `task.bharatainternasional.com`
- **Status**: ✅ Implemented (aktif dikembangkan)

**Autentikasi & Role**
- **SSO gateway-cutover SELESAI** — tidak ada login lokal. Tujuan login diarahkan ke ERP (`/auth/callback`), tukar one-time code via `POST /auth/sso/redeem` → ERP JWT (disimpan di localStorage, dikirim sebagai Bearer & token WebSocket). Tanpa refresh token (401 → re-SSO).
- Role: **staff / supervisor / admin** (dari `GET /api/task-management/me`). Route gating di middleware (`proxy.ts`): `/admin/*` admin+supervisor; divisi/settings/audit admin-only; approval/archive supervisor.

**Fitur (Sudah Diimplementasikan)**
- Member: dashboard (stat tugas masuk/keluar, refresh realtime), daftar tugas + detail, profile, report KPI, help
- Spaces & **Kanban**: board per divisi dengan drag-drop status (stage Request/Todo/Done dilindungi), CRUD stage/priority, edit prioritas/tenggat/archive per kartu; drag di-gate per role (staff hanya tugas yang ditugaskan ke dirinya, supervisor di divisinya, admin lintas divisi)
- Tugas: create/assign (multi-assignee), **approval** (approve dgn start_date + due_date + priority_id + assign_to / reject + alasan), comment, checklist, attachment (file + link, presigned preview), riwayat/aktivitas, badge **SLA** (response + resolution)
- **Notifikasi**: inbox (unread count, mark-read, delete) + **WebSocket realtime** (auto-reconnect)
- Admin/supervisor: executive/manager dashboard, team tasks per divisi, approval queue, archive, audit log, report SLA + export Excel
- Backend lewat bip-erp gateway `/api/task-management/*` → [[Microservices - Task Management Service]] (BE standalone lama `bharata-task-manager-be` ditinggalkan)

## Belum Diimplementasikan / Catatan

- `/admin/settings` (Pengaturan Sistem) = **Coming Soon** (placeholder, disembunyikan dari sidebar)
- **Members & Roles management** belum di-wire (komponen ada tapi orphan/dead code; tidak ada route `/admin/members`)
- `/admin/divisions` = **read-only** (CRUD divisi menunggu dukungan backend)
- **On-time rate**: backend kini menyuplai via `GET /report/sla` (`overall`/`by_division` response & resolution) — lihat [[Microservices - Task Management Service]]; verifikasi tampilan FE end-to-end **pending**. (Manpower on-time masih `null` di sisi FE.)
- **Role gating**: backend kini punya RBAC ringan (`requireRoles` `supervisor`/`staff`) di [[Microservices - Task Management Service]]; gating FE/middleware tetap dipertahankan sebagai lapis tambahan
- Catatan adopsi: tantangan utama adalah menjaga pengguna tetap memakai sistem dalam jangka panjang — butuh keterhubungan dengan pembuat/penerima tiket (fokus Notification Center)

## BUGS
* **User masih bisa melihat space dari divisi lain** — `SpacesPage` mengambil semua space; filter divisi hanya dropdown client-side yang bisa diubah ke "Semua divisi". Aksi Edit/Delete sudah benar di-gate ke supervisor divisi sendiri, tetapi isolasi tampilan yang sebenarnya perlu **scoping di backend**. **Masih terbuka**: paritas BE `feat/task-management-parity` menambah scoping pada `/tasks/filter` (flag kepemilikan) tetapi **belum** pada listing `GET /spaces`.

### Production
https://task.bharatainternasional.com

## Pertimbangan

- Integrasi ke sistem ini akan memakan waktu
- Konteks mungkin terasa terpisah dari tempat seharusnya (misalnya HRIS task tracker akan berada di sini alih-alih di HRIS itu sendiri)

## Integrasi ke Insentive
- Integrasi ke sistem insentive memiliki beberapa pertanyaan / masalah :
  1. Di Finance - Incentive ICC, leader/spv mengecek video menggunakan modul 
  2.

Integrasi ke Insentive
1. pada ICC : pengawas (disebut pengawas karena masih belum diketahui posisi yang melakukan tugas ini) melakukan pengecekan dan evaluasi video di modul khusus R&D. Apa modul khusus R&D tersebut ?
2. Bagaimana flow task management setelah diperbarui dan integrasi dengan insentive ?
3. Bagaimana rencana penggabungan task management dengan erp ?

Jawab :
1. 
2. Flow task management inegrasi dengan insentive :
   Untuk integrasi dengan insentive jelas perlu pembaruan flow ux , database dengan jadi patokan divisi marketing untuk intensive, fitur sprint untuk semua divisi:
    - flow :
	    tambahan field type pada form buat task/request. yang beda-beda tiap divisi. Khusus untuk marketing disesuaikan dengan insentive maka ada beberapa tambahan type beserta flownya : 
		- **`ADS_CAMPAIGN` (Untuk Tim ADV & ADV Meta)**
		    - **Aktivitas:** Menjalankan iklan di TikTok, Meta (FB/IG), dll.    
		    - **Saat digeser ke "Done" meminta:** _Campaign ID_ atau _Ad Group ID_.
		    - **Tujuan Metrik:** Menarik data Jumlah Konversi dan CPA dari API TikTok/Meta Ads.	        
		- **`VIDEO_CONTENT` (Untuk Tim ICC)**
		    - **Aktivitas:** Memproduksi dan mengunggah video ke TikTok sesuai standar R&D.  
		    - **Saat digeser ke "Done" meminta:** _Video URL_ atau _Video ID_.
		    - **Tujuan Metrik:** Menghitung Kuantitas Harian (5 video/hari), dan menarik data _Views_, CTR, _Watch Time_ untuk bonus kualitas video.
		- **`LIVE_STREAM` (Untuk Tim Host Live)**
		    - **Aktivitas:** Melakukan sesi siaran langsung (Live) di TikTok Shop/Marketplace.
		    - **Saat digeser ke "Done" meminta:** _Live Session ID_ atau sekadar _Screenshot GMV_ (jika API belum siap).
		    - **Tujuan Metrik:** Menarik data Konversi spesifik dari sesi Live tersebut.
		- **`AFFILIATE_PITCH` / `AFFILIATE_CAMPAIGN` (Untuk Tim Affiliator)**
		    - **Aktivitas:** Menghubungi kreator (Affiliate) untuk mempromosikan produk Bharata atau membuat _campaign_ komisi.
		    - **Saat digeser ke "Done" meminta:** _Affiliate Link ID_ atau _Creator Username_.
		    - **Tujuan Metrik:** Melacak jumlah _Affiliate_ yang aktif (syarat KPI Affiliator) dan Konversi dari _link_ afiliasi tersebut.
		- **`CRM_BROADCAST` / `CUSTOMER_CLOSING` (Untuk Tim CRM)**
		    
		    - **Aktivitas:** Melakukan _follow-up_ database pelanggan lama atau _broadcast promo_.
		        
		    - **Saat digeser ke "Done" meminta:** _Nomor Tiket Order / Customer ID_ (Bisa dikoneksikan ke ERP).
		        
		    - **Tujuan Metrik:** Menghitung jumlah konversi (pesanan) yang berhasil di-_closing_ oleh tim CRM.

	- Ekspektasi api dan response yang diharapkan 
	  Berikut ekpektasi api dan response dari pengambilan data dari be :
		- Data Keuangan (Dari Accurate) - Untuk Syarat SPV & Global
			Data ini ditarik setiap akhir bulan untuk mengecek Laba Bersih dan batas Retur 5%.
			- **Endpoint di Golang:** `POST /api/v1/webhook/finance/accurate-summary` 
			- **Authorization:** `x-api-key: [SECRET_KEY_INTERNAL]`		    
			- **Ekspektasi Payload (Dikirim oleh Analis Accurate):**
				```
				{
				  "period": "2026-02",
				  "division": "MARKETING",
				  "data": {
				    "net_profit": 85000000,          // Laba bersih dalam Rupiah
				    "total_sales_qty": 10000,        // Total Pcs terjual bulan ini
				    "total_return_qty": 350          // Total Pcs retur bulan ini
				  },
				  "fetched_at": "2026-02-28T23:59:00Z"
				}
				```
			Response dari Golang (Jika Sukses):
			```
			{
			  "status": "success",
			  "message": "Finance data for 2026-02 recorded. Return rate is 3.5% (Qualified).",
			  "reference_id": "fin_889900"
			}
			```
		- Data Advertiser / ADV (Dari TikTok/Meta Ads)
		
			Data ini dikirim harian/mingguan untuk memperbarui metrik tiket _Task_ milik ADV.
			- **Endpoint di Golang:** `POST /api/v1/webhook/marketing/ads-metrics`
			- **Ekspektasi Payload (Dikirim oleh Analis TikTok/Meta):**
			
			JSON
			
			```
			{
			  "platform": "TIKTOK_ADS",
			  "campaign_id": "1234567890",       // Harus match dengan ID di tiket ProjectFlow
			  "metrics": {
			    "conversions": 150,              // Jumlah Closing
			    "spend": 2250000,                // Total pengeluaran (Opsional)
			    "cpa": 15000                     // Cost Per Acquisition
			  },
			  "fetched_at": "2026-02-23T10:00:00Z"
			}
			```
			
			- **Response dari Golang (Jika ID Ditemukan):**
			JSON
			```
			{
			  "status": "success",
			  "message": "Metrics updated for Task ID: 64a7b...",
			  "updated_fields": ["conversions", "cpa"]
			}
			```
			
			- **Response dari Golang (Jika Error / Campaign ID tidak ada di database):**
			
			JSON
			
			```
			{
			  "status": "error",
			  "code": "CAMPAIGN_NOT_FOUND",
			  "message": "No active task found with campaign_id 1234567890"
			}
			```
		- Data Content Creator / ICC (Dari TikTok API)
		
			Data ini digunakan untuk mengecek apakah video memenuhi standar kualitas (CTR ≥ 2% & Watch ≥ 30%) dan GMV Max (ROI ≥ 3.2 & Order ≥ 15).
			
			- **Endpoint di Golang:** `POST /api/v1/webhook/marketing/video-metrics`
			    
			- **Ekspektasi Payload (Dikirim oleh Analis TikTok):**
			    
			
			JSON
			
			```
			{
			  "video_id": "9876543210123",       // Harus match dengan ID di tiket ProjectFlow
			  "metrics": {
			    "views": 50000,
			    "ctr_percentage": 2.5,           // CTR dalam persen
			    "watch_time_percentage": 35.0,   // Watch time dalam persen
			    "total_orders": 20,              // Jumlah order dari video ini
			    "roi_gmv": 4.1                   // ROI penjualan vs biaya
			  }
			}
			```
			
			- **Logic Tersembunyi di Golang:** Saat menerima JSON ini, Golang Anda akan otomatis mengecek: _"Oh, CTR > 2% dan Watch > 30%, berarti is_qualified = true. Oh, Order > 15 dan ROI > 3.2, berarti is_gmv_winner = true"_.
		- Data Host Live & Affiliator (Dari TikTok Shop)
		
			Data untuk tim _Live Stream_ dan _Affiliator_ berfokus pada volume konversi kelompok.
			
			- **Endpoint di Golang:** `POST /api/v1/webhook/marketing/shop-metrics`
			    
			- **Ekspektasi Payload:**
			    
			
			JSON
			
			```
			{
			  "source_type": "LIVE_STREAM",      // Bisa "LIVE_STREAM" atau "AFFILIATE_LINK"
			  "source_id": "live_session_999",   // ID Sesi Live atau ID Campaign Affiliate
			  "metrics": {
			    "conversions": 300,              // Jumlah pesanan terbayar (Paid)
			    "active_affiliates": 0           // Diisi jika type-nya AFFILIATE_LINK
			  }
			}
			```


3. 

Catatan :
1. Harapan memang untuk pengambilan data bisa langsung terintegrasi ke sumber data tapi apakah perlu fitur antisipasi jika pengambilan data itu salah ? misal dibuat input link bukti satau ss laman bukti
