## Deskripsi

*Endpoint **manufacture-service** (WMS manufaktur: master bahan/produk, stok, transaksi, formula, produksi, PO, proposal, resi retur ekspedisi). Gateway: `/api/manufacture/*`. Grounded ke `services/manufacture/main.go`.*

- **Implementasi**: [[Microservices - Manufacture Service]] · **Status**: ✅ (di kode)
- **Indeks**: [[API - Index]] · RBAC: di-handle di gateway (tak eksplisit di rute).

## Master & stok
| Method | Path | Fungsi |
|---|---|---|
| GET | `/master-bahan` · `/master-bahan/:kode` | List/detail master bahan |
| POST/PUT/DELETE | `/master-bahan` · `/master-bahan/:kode` | Create/update/delete master bahan manual (tandai `source:"manual"` → kebal stale-marking saat sync Sheet) |
| POST/PATCH | `/master-bahan/sync` · `/master-bahan/:kode/status` | Sync (Sheets) / ubah status (audit) |
| GET | `/master-product` · `/master-product/:kode` | List/detail master produk |
| POST/PUT/DELETE | `/master-product` · `/master-product/:kode` | Create/update/delete master produk manual (tandai `source:"manual"` → kebal stale-marking saat sync Sheet) |
| POST | `/master-product/sync` | Sync master produk dari Google Sheet (opsional, transisi) |
| GET/POST | `/stok` · `/stok/:kode` · `/stok/reconcile` | Stok + rekonsiliasi |
| GET | `/stok/sektor` | Stok riil per gudang untuk card Status Sektor (utama = kode master bahan, tinggar = kode master barang, sadewa = net transaksi bergudang-simpan "sadewa"); breakdown `jenis` → satuan → qty. Terdaftar **sebelum** `/stok/:kode` agar tidak tertangkap param |
| GET/POST | `/saldo-awal` (`?bulan=YYYY-MM`) · `/saldo-awal/snapshot` | Saldo awal bulanan (snapshot stok tiap awal bulan, terpisah dari master); snapshot idempoten — dipicu otomatis (boot + ticker 6 jam) atau manual |

## Transaksi · Formula · Produksi
| Method | Path | Fungsi |
|---|---|---|
| GET/POST | `/transaksi` | List/buat transaksi stok (INBOUND/OUTBOUND); kode boleh master bahan **atau** produk jadi (`master_product`); OUTBOUND ditolak 422 bila stok tidak cukup; field UI tambahan (QC, PIC, dll) disimpan apa adanya di `detail` |
| PATCH | `/transaksi/:id/status` | Ubah status UI transaksi (`detail.status`) — dipakai alur terima SJ Kirim Produk (IN TRANSIT → DELIVERED) |
| GET/POST/PUT/DELETE | `/formula` · `/formula/:id` | Formula/BOM (resep produksi) — CRUD penuh (create/update/delete) |
| POST | `/formula/sync` | Sync formula dari Google Sheet (service account, opsional) |
| GET/POST | `/production` | Order produksi (konsumsi stok) |
| GET/POST/DELETE | `/production-log` · `/production-log/:id` | Catatan produksi (tanpa konsumsi stok) |
| GET/POST/DELETE | `/material-order` · `/material-order/:id` | Order material internal |

## Resi — Master Retur Ekspedisi
| Method | Path | Fungsi |
|---|---|---|
| GET | `/resi` · `/resi/lookup/:resi` | List semua resi · lookup 1 resi by `no_resi` (auto-fill scan form Return & Keluar FG). Tiap resi bawa `status_pesanan`, `tanggal_rts`, `shift` (Pagi/Siang/Sore/Luar Jam — diturunkan dari waktu ready-to-ship) |
| POST/PUT/DELETE | `/resi` · `/resi/:id` | CRUD resi (mayoritas terisi otomatis; tombol input manual sudah dihapus dari UI, endpoint tetap ada) |
| POST | `/resi/sync-tiktok` | **Pull** resi order TikTok dari integration `/tiktok/shop/orders/resi-feed`, upsert by `no_resi` (index unik) |
| POST | `/resi/sync-shopee` | **Pull** resi order Shopee dari integration `/shopee/orders/resi-feed`, upsert by `no_resi` |
| POST | `/resi/sync-batch` | **Push endpoint**: menerima batch resi-feed dari scheduler integration `sync-resi-wms` (lihat [[IT - Background Jobs & Schedulers]]) |

## PO · Proposal · Audit
| Method | Path | Fungsi |
|---|---|---|
| GET/POST/PATCH/DELETE | `/marketing-po` · `/marketing-po/:id[/status]` | PO marketing (audit) |
| GET/POST/PATCH/DELETE | `/procurement-po` · `/procurement-po/:id[/status]` | PO procurement (audit) |
| GET/POST | `/proposal` · `/proposal/:id/approve` · `/reject` | Proposal koreksi/deviasi pemakaian fisik (PENDING_PPIC → PENDING_SPV → APPLIED, audit). Saat APPLIED, pemotongan stok memakai filter kondisional `stok_sekarang >= qty` — ditolak 409 bila akan membuat stok minus |
| GET | `/audit-log` (`?user=&aksi=`) · `/audit-log/rekap` (`?bulan=YYYY-MM`) · `/health` | Audit log (list) · rekap aktivitas CRUD per user/bulan untuk **KPI otomatis** (agregasi batas hari/bulan pakai **WIB**, respons ber-flag `truncated` bila >20k entri) · health |

## Dokumen Terkait
- [[Microservices - Manufacture Service]] · [[Manufacture - Stock & Material Management]] · [[GA - Procurement System]] · [[API - Integration Service]] (resi-feed) · [[IT - Background Jobs & Schedulers]] (`sync-resi-wms`) · [[API - Index]]
