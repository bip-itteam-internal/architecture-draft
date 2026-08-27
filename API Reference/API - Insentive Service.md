## Deskripsi

*Endpoint **insentive-service**. Sejak 2026-07-30 skemanya **profit-based untuk seluruh jabatan** (SK 010 & 011/DIR/SK6/VII/2026); rute `/profit*` di bawah adalah yang berlaku. Rute warisan skema KPI-multiplier masih terdaftar tetapi sebagian **menolak** — lihat catatannya. Gateway: `/api/insentive/*`. Semua butuh gateway key; `/health` bebas. Grounded ke `services/insentive/main.go` + `func.go`.*

- **Implementasi**: [[Microservices - Insentive Service]] · **Status**: ⚠️ Implemented (ada catatan)
- **Indeks**: [[API - Index]]

## Profit-based (skema berlaku)
| Method | Path | Fungsi |
|---|---|---|
| GET | `/profit-dashboard` | Dashboard insentif per periode & level (`periode=YYYY-MM`, `level=icc\|leader\|supervisor`, `refresh=1` tarik ulang beban non-gaji). Tiap baris membawa `toko_tanpa_penjualan` — berapa dari `shop_ids` yang terpetakan ke orang itu tetapi nol order di periode berjalan, dipakai layar untuk menulis "9 dari 15 toko" alih-alih menyembunyikan yang belum berjualan (2026-08-26, PR #1455) |
| GET/POST | `/profit/org` | Struktur tim (ICC ↔ Leader ↔ Supervisor) |
| PATCH | `/profit/org/:id/tutup` | Tutup masa berlaku satu baris struktur |
| GET/POST | `/profit/targets` | Target profit per entitas/periode (ubah saat berjalan wajib beralasan ≥10 karakter) |
| GET/POST | `/profit/opex` | Biaya operasional manual — kini **cadangan** (gaji dari payroll, non-gaji dari Accurate) |
| POST | `/profit/opex/distribusi` | Bagi satu angka divisi ke tiap entitas (pro-rata, metode sisa-terbesar) |
| GET/POST/DELETE | `/profit/internal-affiliates` · `/:username` | Daftar putih akun affiliate milik sendiri |

> Sumber angka: komponen profit & beban non-gaji dari [[API - Integration Service]] (`/profit/incentive/summary`, `/profit/incentive/opex`), beban karyawan dari payroll-service `GET /employer-cost`.

## Engine lama & Master KPI (warisan)
| Method | Path | Fungsi |
|---|---|---|
| POST | `/calculate` | ⚠️ **Menolak seluruh role** — skema KPI-multiplier & ICC per-video dicabut; balasannya menyebut SK pencabutnya |
| POST | `/calculate/auto` | ⚠️ Sama; cron harian sudah dihapus |
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

> ⚠️ **Cron harian sudah DIHAPUS** bersama skema KPI-multiplier (`cron_worker.go`, 2026-07-30). Tidak ada lagi job terjadwal di service ini — lihat [[IT - Background Jobs & Schedulers]].

## Dokumen Terkait
- [[Microservices - Insentive Service]] · [[HRIS - Key Performance Index]] · [[Finance - Incentive]] · [[API - Index]]
- [[ADR - 0033 Beban Operasional Insentif dari Proyek Accurate]] · [[API - Integration Service]]
