# WH - Kelola Pesanan (Order Management)

## Deskripsi

*Rencana penyatuan alur fulfillment gudang yang kini tersebar di beberapa menu
(Perlu Diproses, Antrian Pesanan, Pengambilan, Pengemasan, Riwayat Cetak Resi,
Serah Terima) menjadi **satu layar omnichannel ala Desty**: "Kelola Pesanan".
Backend tidak berubah — ini pekerjaan frontend + rollout di atas endpoint
[[Microservices - Warehouse Service]] & [[Microservices - Integration Service]]
yang sudah live.*

- **Stack**: Next.js (`erp-frontend`), react-query, di atas endpoint `services/warehouse` + `services/integration` (tak berubah).
- **Path di repo**: `erp-frontend/src/features/warehouse/components/kelola-pesanan/*` (pratinjau Beta) · `app/(main)/warehouse/kelola-pesanan/page.tsx` · item sidebar "Kelola Pesanan (Beta)".
- **Status**: 🟡 Konsep / Direncanakan — pratinjau **FE-only "Kelola Pesanan (Beta)"** sudah ada di kode (data **dummy**, aksi **mati**); gate RBAC badge count sudah live (lihat [[CORE - RBAC dan Permission Set]]); **penyambungan ke data/endpoint nyata + cutover dari menu lama BELUM dikerjakan**.
- **Acuan alur target**: [[WH - Fulfillment Flow & WMS Tinggarjaya]].

## Latar Belakang

Alur gudang Tinggarjaya sudah berjalan penuh, tetapi UI-nya terpecah per-tahap
(satu menu per langkah). Admin gudang di lapangan sebagian masih memakai aplikasi
Desty yang menyajikan **satu layar omnichannel** dengan tab bertahap. "Kelola
Pesanan" meniru pola itu — satu tempat untuk memantau semua pesanan lintas
channel (Shopee/TikTok/Lazada) dan memprosesnya dari tahap "Perlu diproses"
sampai "Serah kurir" — tanpa mengubah backend atau state machine yang sudah
terbukti (100+ resi/hari). Konteks lepas-Desty: [[External - Desty]].

## Kondisi Saat Ini

**Pratinjau Beta (FE-only, dummy):** komponen `KelolaPesananBeta` (shell + switcher),
`KelolaPesananView`, `OrderTabs`/`SubTabs`, `OrderCard`, `SelectionBar` (TeamPicker
T1/T2 + paginasi, aksi **disabled**), filter Toko/Kurir/Tanggal+jam/Urutkan,
`RiwayatCetakResiView`. Data dari `dummy.ts` (`ORDERS`, `TABS`, `SUBS`) — **tanpa hook
backend apa pun**. Dibungkus `WarehouseGuard`; item sidebar berlabel "(Beta)" di
paling bawah. Konstanta `CAP = 100` menandai batas batch backend.

**Produksi (sudah wired & live):** menu lama memakai endpoint nyata — `PendingArrangeView`
(`GET /fulfillment/pending-arrange` + `POST /fulfillment/arrange`), `QueueView`
(`GET /fulfillment/queue` + `queue/counts`), plus aksi approve/hold/pick/pack/rts/labels/
labels-merged/handover, gerbang rekon `queue/export` (cap `exported_at`), dan
`labels/history` (Riwayat Cetak Resi). Semua role-guarded `system_roles["warehouse"]`.

Kesenjangan inti: **Beta punya tata letak & UX; produksi punya pipa data & aksi.**
Mutasi = mengawinkan keduanya lewat **reuse hook/komponen yang sudah ada** — bukan
menulis ulang (mencegah lahirnya sumber kebenaran kedua).

## Persona / Pengguna

| Persona | Peran & Divisi | Akses/RBAC | Device |
|---|---|---|---|
| Admin Gudang | staf gudang Tinggarjaya | `system_roles["warehouse"]` = `admin_gudang` (proses penuh) | Web ERP (desktop gudang) |
| Leader / SPV | pengawas gudang | `warehouse` = `leader`/`spv`, atau pengawas WMS (PPIC/SPV manufaktur) | Web ERP |
| Admin QC | pemeriksa | `warehouse` = `admin_qc` (read-only: antrian + dashboard) | Web ERP |

- **Tujuan**: memproses pesanan lintas channel dari satu layar (arrange → cetak resi → serah kurir) tanpa pindah-pindah menu.
- **Pain point**: alur lama terpecah per-tahap; sebagian admin masih bersandar ke Desty.
- **Aksi utama**: Atur Pengiriman (arrange) · Cetak Resi (rts+labels, pilih Tim T1/T2) · pantau status per tab.

> Mitra **gudang Sadewa** (`admin_gudang_sadewa`) sengaja **di luar lingkup awal** — aksinya lewat lapisan approval Sadewa→Tinggar dan harus disebut eksplisit per-rute. Lihat [[WH - Warehouse Sadewa]].

## Peta Tab → Sumber Data (grounded ke endpoint nyata)

Tab (dari `dummy.ts` `TABS[].anno`) → sumber data saat disambungkan:

| Tab | Cakupan status | Sumber saat wired | Catatan |
|---|---|---|---|
| Semua Pesanan | union semua status | gabungan sumber di bawah (FE) | — |
| Belum Dibayar | `TO_PROCESS` & `raw_status=UNPAID` | integration transactions (filter `raw_status`) | **butuh dukungan BE kecil** (TBD) |
| Pesanan Baru | `TO_PROCESS` & `raw_status ∈ ArrangeReady` | `GET /fulfillment/pending-arrange` | endpoint **sudah ada** |
| Siap Dikirim | `TO_SHIP` / pipeline `status_wms` | `GET /fulfillment/queue` + `queue/counts` | inti kerja gudang (3 sub-tab) |
| Dikirim | `SHIPPED` / `HANDED_OVER` | `queue?status=HANDED_OVER` / integration | — |
| Selesai | `COMPLETED` | integration transactions | — |
| Pembatalan | `CANCELLED` | integration transactions | — |
| Pengembalian | `RETURNED` | integration transactions (read-only) | modul retur WMS = fase berikut |

**Sub-tab "Siap Dikirim"** (paling penting):

| Sub-tab | `status_wms` | Endpoint | Aksi |
|---|---|---|---|
| Perlu diproses | `NEW` (`arrange_status≠arranged`) | `pending-arrange` / `queue?status=NEW` | **Atur Pengiriman** → `POST /arrange` (terbit AWB) |
| Diproses | APPROVED/PICKING/PACKED/RTS_OK/RTS_FAILED/LABEL_PRINTED | `queue?status=<multi>` | approve / rts / **cetak resi** |
| Telah diproses | `HANDED_OVER` | `queue?status=HANDED_OVER` | Cetak Ulang / audit |

> Penamaan tab Beta berbeda dari tab produksi `QueueView` (Pesanan Baru/Disetujui/…). Saat mutasi, **satukan taksonomi status** — jangan biarkan dua peta status hidup paralel (angka bisa menyimpang diam-diam). Reconcile yang sahih = `TO_SHIP ↔ TO_SHIP`, bukan angka mentah antar-tab.

## Rencana Mutasi (bertahap, tiap fase teruji sendiri)

| Fase | Isi | Status |
|---|---|---|
| 0 | Gate badge count sidebar by akses (`bolehLihatMenuWarehouseTinggar`/`bolehAksesSadewa`) — fondasi RBAC menu baru | ✅ selesai |
| 1 | Wiring **baca** (read-only): dummy → hook nyata (`useWarehouseQueue`, `useQueueCounts`, `usePendingArrange`); aksi tetap mati | 🟡 |
| 2 | Aksi **Atur Pengiriman** (`POST /arrange`, batch ≤100); adopsi guard TikTok `package_id` kosong → "Menunggu sinkronisasi" | 🟡 |
| 3 | Aksi **Cetak Resi** (`rts`→`labels`+`labels/merged`, TeamPicker `packer_code` T1/T2) **dengan gerbang rekon** + penanganan gagal cetak | 🟡 |
| 4 | Tab non-WMS (Belum Dibayar/Selesai/Batal/Retur) dari integration + Riwayat nyata (`labels/history`) | 🟡 |
| 5 | Cutover: feature-flag, jalan **paralel** dgn menu lama sampai paritas terbukti, lalu pensiunkan menu lama; hapus label "(Beta)" | 🟡 |

## Gerbang & Nuansa yang Wajib Dipertahankan

Diangkat dari [[WH - Fulfillment Flow & WMS Tinggarjaya]] — paling gampang hilang saat "cuma ganti UI":

1. **Gerbang rekon `exported_at`** sebelum RTS (`only_new=true` per batch); RTS order belum ditarik → 422.
2. **Kode packer T1/T2** (`packer_code`) — dicap saat unduh rekon & batch label, tidak menimpa.
3. **Guard TikTok `package_id` kosong** → label "Menunggu sinkronisasi", baris disable (**bukan** seluruh TikTok).
4. **Batch cap 100** (arrange & labels/merged) — Beta sudah sadar (`CAP=100`).
5. **Order tahap-2 (Perlu Diproses) BUKAN record WMS** — hanya proxy dari integration; record lahir saat `TO_SHIP`. Jangan menambah aksi tulis di tab ini selain `arrange`.

## Belum Diputuskan (TBD)

- **Tab "Belum Dibayar"** butuh dukungan BE kecil (filter `raw_status=UNPAID` di integration) — perlu dikonfirmasi apakah tab ini benar dibutuhkan sebelum menambah endpoint.
- **Cakupan Sadewa**: apakah Kelola Pesanan kelak melayani mitra Sadewa (dengan lapisan approval-nya) atau tetap Tinggar-saja. Awalnya **Tinggar-saja**.
- **Nasib menu lama** setelah cutover: disembunyikan dari sidebar (route tetap via URL, pola `rts`/`labels`) atau dihapus.

## Dependensi & Integrasi

- [[Microservices - Warehouse Service]] — endpoint fulfillment (queue, arrange, rts, labels, history) + role guard; **sumber utama aksi**.
- [[Microservices - Integration Service]] — proxy API marketplace (`ship-batch`, `labels`) + sumber transaction untuk tab non-WMS.
- [[CORE - RBAC dan Permission Set]] — lapisan gating frontend (`WarehouseGuard`, gate badge count).
- [[WH - Warehouse Sadewa]] — gudang kedua yang berbagi antrian (di luar lingkup awal).
- [[External - Desty]] — konteks omnichannel lepas-Desty yang ditiru layar ini.

## Dokumen Terkait

- [[WH - Fulfillment Flow & WMS Tinggarjaya]] — alur end-to-end target (sumber gerbang & state machine).
- [[Microservices - Warehouse Service]] · [[API - Warehouse Service]] — implementasi & daftar endpoint.
- [[APP - Web ERP]] — modul frontend induk.
