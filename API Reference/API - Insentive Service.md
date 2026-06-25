## Deskripsi

*Endpoint **insentive-service** (engine skor KPI → insentif 9 role marketing + workflow approval). Gateway: `/api/insentive/*`. Semua butuh gateway key; `/health` bebas. Grounded ke `services/insentive/main.go`.*

- **Implementasi**: [[Microservices - Insentive Service]] · **Status**: ✅
- **Indeks**: [[API - Index]]

## Engine & Master KPI
| Method | Path | Fungsi |
|---|---|---|
| POST | `/calculate` | Engine perhitungan insentif universal (per-role) |
| POST | `/calculate/auto` | Trigger manual cron auto-calculate |
| GET/POST/PUT/DELETE | `/master-kpi` · `/master-kpi/:id` | CRUD master KPI (bobot total 100) |

## Mappings & Audit
| Method | Path | Fungsi |
|---|---|---|
| GET/POST/PATCH/DELETE | `/mappings` · `/mappings/:id` | Mapping performa employee (PATCH wajib reason) |
| GET | `/audit-logs` | Audit log (filter target_collection/target_id) |

## Results & Workflow
| Method | Path | Fungsi |
|---|---|---|
| GET | `/results` · `/results/summary` | List hasil insentif (paginated) |
| GET | `/results/export` | Export Excel (single/pivot/history) |
| GET | `/results/me` · `/results/team` · `/results/:id` | Hasil sendiri / tim / detail |
| POST | `/results/bulk-approve` · `/results/bulk-unapprove` | Approve/unapprove massal (DRAFT↔APPROVED) |
| POST | `/results/:id/approve` · `/results/:id/unapprove` | Approve/unapprove per-hasil |
| PATCH | `/results/:id/override` · `/results/:id/daily-override` | Override (wajib reason; trigger recalc) |
| DELETE | `/results/:id` | Hapus hasil (ditolak bila APPROVED) |

## Stats · Config · Proxy
| Method | Path | Fungsi |
|---|---|---|
| GET | `/stats` | Dashboard total + tren bulanan |
| GET/PUT | `/configs/ppn` | Persentase PPN (shopee/tiktok/meta) |
| GET | `/accurate/summary` · `/accurate/income` · `/accurate/invoices` | Proxy data Accurate |
| GET | `/integration/shopee/item-performance` | Ambil GMS Shopee dari integration |
| GET | `/health` | Health check |

> Cron harian 00:00 WIB (lock `cron_locks`) — lihat [[IT - Background Jobs & Schedulers]].

## Dokumen Terkait
- [[Microservices - Insentive Service]] · [[HRIS - Key Performance Index]] · [[Finance - Incentive]] · [[API - Index]]
