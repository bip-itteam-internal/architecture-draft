## Deskripsi

*Endpoint **insentive-service**. Sejak 2026-07-30 skemanya **profit-based untuk seluruh jabatan** (SK 010 & 011/DIR/SK6/VII/2026); rute `/profit*` di bawah adalah yang berlaku. Rute warisan skema KPI-multiplier masih terdaftar tetapi sebagian **menolak** — lihat catatannya. Gateway: `/api/insentive/*`. Semua butuh gateway key; `/health` bebas. Grounded ke `services/insentive/main.go` + `func.go`.*

- **Implementasi**: [[Microservices - Insentive Service]] · **Status**: ⚠️ Implemented (ada catatan)
- **Indeks**: [[API - Index]]

## Profit-based (skema berlaku)
| Method | Path | Fungsi |
|---|---|---|
| GET | `/profit-dashboard` | Dashboard insentif per periode & level (`periode=YYYY-MM`, `level=icc\|leader\|supervisor`, `refresh=1` tarik ulang beban non-gaji). Tiap baris membawa `toko_tanpa_penjualan` — berapa dari `shop_ids` yang terpetakan ke orang itu tetapi nol order di periode berjalan, dipakai layar untuk menulis "9 dari 15 toko" alih-alih menyembunyikan yang belum berjualan (2026-08-26, PR #1455), dan `retur_gagal_booking` — order retur yang belum/gagal masuk pembukuan sehingga tak ikut rasio (2026-08-27, PR #1462). Jawabannya juga membawa, sekali per respons, `tarif_tiers` (tangga tarif SK siap tampil), `batas_retur_persen` (7), dan `batas_pencapaian_bebas_retur` (100) — dikirim backend, TIDAK disalin ke layar, karena tabel tarif pernah salah satu poin persen di produksi (2026-08-27, PR #1463). Parameter `mode=bergeser` mengaktifkan jendela KPI (lihat catatan di bawah) |
| GET/POST | `/profit/org` | Struktur tim (ICC ↔ Leader ↔ Supervisor) |
| PATCH | `/profit/org/:id/tutup` | Tutup masa berlaku satu baris struktur |
| GET/POST | `/profit/targets` | Target profit per entitas/periode (ubah saat berjalan wajib beralasan ≥10 karakter) |
| GET/POST | `/profit/opex` | Biaya operasional manual — kini **cadangan** (gaji dari payroll, non-gaji dari Accurate) |
| POST | `/profit/opex/distribusi` | Bagi satu angka divisi ke tiap entitas (pro-rata, metode sisa-terbesar) |

> Sumber angka: komponen profit & beban non-gaji dari [[API - Integration Service]] (`/profit/incentive/summary`, `/profit/incentive/opex`), beban karyawan dari payroll-service `GET /employer-cost`.

> ⚠️ **`mode=bergeser` — dua angka profit yang sah berbeda.** Bawaan (tanpa parameter) memakai aturan insentif: order yang uangnya cair setelah tanggal 25 bulan berikutnya HANGUS. `mode=bergeser` memasukkannya ke periode berikutnya, dan itulah yang diminta adaptor KPI `insentif_profit` — insentif membayar periode yang sudah tertutup, KPI menilai kerja yang hasilnya baru cair terlambat. Terukur prod 2026-08-27: selisihnya +0,151% (Juli) dan +0,093% (Agustus). **Mode ikut kunci cache**; dua mode berbagi kunci akan membuat dashboard insentif menampilkan angka bergeser. Pre-warm menghangatkan KEDUA mode — tanpa itu panggilan KPI pertama memicu komputasi dingin ~2 menit lalu habis waktu di gateway. PR #1503 (belum merge).

> 🗑️ **Rute `/profit/internal-affiliates` DIHAPUS** (2026-08-27, PR #1474). Daftar putih affiliate kosong di produksi sepanjang umurnya sehingga penyaringan tak pernah menyala; premisnya juga tak ada di SK, dan komisi affiliate sudah terpotong di uang cair. Lihat [[Microservices - Insentive Service]].

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
