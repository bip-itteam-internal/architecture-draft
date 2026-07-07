## Deskripsi

*`hris-dashboard` ("One Bharata") adalah portal web internal ERP/HRIS terpadu Bharata Group — dashboard berbasis role untuk mengelola HR, attendance, finance/insentif, integrasi marketplace, IT, dan GA. Selain itu, web ini juga berperan sebagai **SSO Identity Provider** untuk aplikasi lain (mis. Task Manager).*

- **Stack**: Next.js 16 (App Router) + React 19 + TypeScript; shadcn/ui + Radix + Tailwind v4; TanStack Query + axios; react-hook-form + zod; recharts (grafik); leaflet (peta lokasi absensi); `@uiw/react-md-editor` (article); **react-i18next** (i18n dua bahasa → [[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]])
- **Path**: `erp-frontend` (repo `erp-frontend`), branch `feature/sso-task-manager-menu`
- **Status**: ✅ Implemented (aktif dikembangkan)

## Autentikasi & Role

- Login `employee_id` + password → `POST /auth/login` (gateway); `token`, `system_roles`, dll disimpan sebagai cookie. Bearer token auto-attach; proactive refresh via `/auth/refresh` (<60 detik sebelum expiry); interceptor 401 retry sekali lalu redirect `/login`.
- **SSO Identity Provider** (mint one-time code via `POST /auth/sso/ticket`):
	- *Inbound handoff*: jika login dengan query `?redirect_url=...`, setelah login di-redirect balik ke app tujuan dengan `?code=...`
	- *Outbound launch*: tombol/menu "Task Management" memanggil `/auth/sso/ticket` lalu menuju `${TASK_MANAGER_APP_URL}/auth/callback?code=...`
- Role dari cookie `system_roles` (map `module → role | role[]`). Module: `erp, finance, insentive, hris, kpi, it, ga, secretary, beauty_hacks, kyura, manufacture, quality, procurement, integration`. Role: `admin, supervisor, security`, dan khusus insentif `adv_leader, adv_marketplace, adv_meta`.
- **Role gating**: sidebar menampilkan module sesuai key `system_roles` (`erp` publik); menu KPI butuh `supervisor`; Guestbook butuh `ga:security`; create Article + seluruh card Splash butuh `admin`; sub-item Incentive di-gate per role.

## Modul / Fitur (Sudah Diimplementasikan)

**ERP (publik)**
- Dashboard: ringkasan kehadiran pribadi (clock in/out, overtime/telat/cuti), ringkasan karyawan, jadwal shift, widget helpdesk (`POST /feedback`)
- Article + Splash (admin): kelola artikel (md-editor) & gambar splash
- Guestbook view (role security), Task Management (tombol SSO ke app eksternal)

**HRIS** (module paling lengkap)
- Employee: CRUD penuh, filter/search, summary, export Excel, status registrasi myBharata, halaman detail
- Attendance: tabel clock in/out + ikon metode + preview geolokasi (Leaflet), update manual, summary
- Contract, Schedule (kalender + holiday CRUD), Vacation (kuota/terpakai/sisa), Report (bulanan + export Excel), Fingerprint (device management), Dashboard analitik, KPI

**KPI (shared)** — scoring per departemen + template CRUD + filter periode/status; HR lihat semua, supervisor hanya divisinya

**Finance**
- Piutang (TikTok/Shopee): tabel accounts-receivable + filter overdue/in-transit
- Incentive: Dashboard (stats/tren + bulk approve), detail, My Incentive, Master KPI CRUD, Master Integration (mapping employee ↔ platform/campaign)

**IT** — Employee (aktivasi akun, reset password), Network (WiFi SSID/MAC CRUD)
**GA** — Inventory (QR, repair history, assignment)
**Integration (marketplace ↔ Accurate)** — Ads Analytics (Shopee/TikTok), Ads Management, Auto-Approve log, Marketplace log, Master Data (Product, Config Accurate), Shipment Setting, OAuth; `integration-accurate`: Sales / Income / Return Shopee & TikTok-Shop
- **Transactions** — sub-navigasi dua halaman:
  - *Dashboard* (`/integration/transactions`): 4 kartu status live (Pesanan Baru/Belum Di Proses/Siap Dikirim/Pesanan Selesai), filter Platform + Shop + rentang tanggal kustom, grafik perbandingan 4 tab (Potensi Penjualan, Produk Terjual, Penjualan Selesai, Pesanan Selesai) dengan granularity hourly/daily otomatis.
  - *Order Management* (`/integration/transactions/list`): tabel order terpadu + filter (platform, shop, status, date range, Canceled By — tampil hanya saat status = CANCELLED) + 4 kartu ringkasan (Total Revenue, Total Orders, Total Cancel, Total Return) + search global order ID + tombol Accurate Integration. Detail order: Payment Method + Due Date ditampilkan di seksi Shipping Information.
**Marketing Insight** (`/marketing-insight`, feature `src/features/marketing-insight/`) — landing card + sidebar submenu; submodul: Customer Demography, GMV Max Monitoring, Product Performance, dan **Affiliate Performance** (`/marketing-insight/affiliate`): KPI cards (GMV, komisi dibayar/estimasi, order·creator) + kartu Validasi Komisi (cross-check finance statement: tervalidasi/selisih/belum-ada-bukti/menunggu); satu tabel ber-tab (Order | Top Creator | Top Produk) dengan nama+gambar produk (enrich \$lookup `tt_business_store_products` via item_group_id); klik baris order → modal Detail Transaksi Affiliate (produk, creator, konten, model/rate komisi, est/actual, status, verdict validasi finance); filter status validasi; date range picker tanpa default (max 3 bulan); section Update Otomatis (jadwal pipeline bahasa awam + tarikan/validasi terakhir + riwayat 10 batch); fetch react-query → `/api/integration/affiliate/*` ([[API - Integration Service]])

- **Gross Profit / Laba Sejati** (`/integration/gross-profit`, feature `src/features/integration/gross-profit/`) — ⚠️ *working branch `feat/gross-profit` (sudah di-push ke origin), belum merge*: laba kontribusi per produk/SKU TikTok mengikuti blueprint dashboard marketing (`GMV − biaya MP − promo = net settlement − HPP − iklan = laba`; retur kolom informasi). 3 tab: **Profit** (kartu **Arus Dana**: Sudah Cair actual vs Uang Gantung ± estimasi + baris akurasi rumus 30 hari + collapsible rincian per toko×bulan — `cash-flow-cards.tsx`, endpoint `/profit/cash-flow`; kartu ringkasan alur GMV→Net→Laba; toggle mode data **Cair saja (default) | Semua order (±)** — mode cair = murni settlement actual tanpa estimasi, iklan prorata porsi cair; toggle Produk|Bundle — kedua tabel **identik struktur** via komponen bersama `profit-table-shared.tsx` (grup kolom berwarna, legend, sort, footer TOTAL, badge Aksi SCALE/JAGA/PERBAIKI/HENTIKAN; tanda estimasi ± hanya di sel BIAYA settlement — GMV/HPP/Iklan selalu pasti, GMV dari seluruh penjualan bukan dari settlement); tabel Bundle: kolom pertama SKU bundle + subteks komposisi, caption anti-dobel-hitung lintas tab; klik baris → panel samping waterfall Rincian Biaya + tabel per-SKU qty/GMV/Net/Laba, porsi bundle expandable), **HPP** (upload xlsx finance format `SKU|Produk|HPP/Pcs` + tambah/edit/hapus HPP manual per baris + filter nama/periode + badge Aktif/riwayat; HPP bundle terhitung read-only), **Mapping** (generate 2 fase dari master+nama finance, tabel Single|Bundle grouped per SKU, edit nama inline, panel approve saran dengan status simpan Menyimpan…/Tersimpan ✓ + guard klik ganda). Mutasi hanya role `supervisor|admin` modul `integration` ATAU `finance`. Backend: [[API - Integration Service]] rute `/profit/*`.

**Lain** — Secretary / Manufacture / Quality / Procurement (KPI saja), Beauty_hacks / Kyura (link eksternal Ideamiils + KPI)

**Internasionalisasi (i18n)** — dukungan dua bahasa **Indonesia (default) / English** via `react-i18next` (`src/i18n/`); switcher di header (samping tema), pilihan disimpan cookie `lang` (dibaca SSR). Rollout **bertahap**; sudah: HRIS Ulang Tahun, KPI, Announcements. Aturan lengkap: [[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]]

## Belum Diimplementasikan / Catatan

- **`/integration/inventories` = STUB** (data `MOCK_INVENTORIES` hardcoded; inventory asli ada di module GA)
- **`/integration/shipment-setting`** create modal — `// TODO: wire up mutation` (tabel tampil, create belum di-wire)
- **Accurate transaction detail** — panel "Summary Coming Soon"
- **User dropdown**: item Account, Notifications, Settings *disabled*; belum ada route Settings
- **Payroll Calculator**: route ada tapi dihapus dari menu
- **Firebase/FCM push**: kode di-comment, env Firebase masih placeholder
- **Login**: "Forgot your password?" / "Contact admin" link mati; belum ada flow reset password / registrasi

## Dependencies & Integrasi

- **API Gateway bip-erp** (`NEXT_PUBLIC_BASE_URL`; dev `http://localhost:6969`) — semua request lewat sini → [[CORE - API Master Gateway]]
- Konsumsi module via gateway: [[Microservices - Employee Service]], [[Microservices - Attendance Service]], [[Microservices - Notification Service]], [[Microservices - Insentive Service]], [[Microservices - Integration Service]], [[Microservices - Inventory Service]], serta operasi IT via [[CORE - IT Orchestrator]] & HR via [[CORE - HRIS Orchestrator]]
- SSO target: app Task Manager (`tasks.bharatainternasional.com`) → memicu sesi ke [[Microservices - Task Management Service]]
- CDN dokumen (`NEXT_PUBLIC_DOC_URL`), MinIO read-key per domain (employee/attendance/task/notification)

## Dokumen Terkait

- [[BASE - Enterance Point]]
- [[APP - MyBharata]]
- [[HRIS - Key Performance Index]]
- [[Finance - Incentive]]
- [[Finance - Bridging App]]
- [[GA - Inventory Management]]
- [[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]]
