> **Status**: ⚠️ Implemented (tool sudah live di prod sejak deploy 2026-09-01; **eksekusi write belum dijalankan** — dry run wajib lebih dulu). Grounded ke [[Microservices - Integration Service]] (§*Atribusi order Shopee: afiliasi vs organik*).

## Tujuan

Mengisi `transaction_orders.shopee_attribution` untuk order Shopee **historis**, supaya layar Order Management bisa memisahkan order afiliasi dari organik. Tanpa backfill, order lama tetap berlabel **"Belum diketahui"** — benar secara fail-safe, tapi tak berguna.

Worker harian `sync-shopee-affiliate-conversion` (05:00 WIB) hanya melabeli **30 hari ke belakang**. Order yang lebih tua dari itu tak akan pernah tersentuh worker, jadi hanya backfill yang bisa mengisinya.

## Kapan dipakai

- Sekali setelah fitur atribusi di-deploy (PR [#1617](https://github.com/bip-itteam-internal/bip-erp/pull/1617)).
- Bila ledger AMS baru di-backfill mundur untuk suatu toko, sehingga order yang tadinya di luar jangkauan ledger kini tercakup.

## ⛔ Yang TIDAK dilakukan tool ini

**Backfill ini TIDAK bisa memicu pencatatan apa pun ke Accurate.** Diverifikasi ke kode 2026-09-01, tiga lapis:

1. `SetAttribution` hanya `$set` **dua field**: `shopee_attribution` dan `shopee_attribution_at`. Tak menyentuh `shipped_at`, `status`, `income_status`, `income.paid_at`, `items`, maupun `return` — dan justru itulah field yang dibaca mesin auto-sync.
2. Snapshot faktur/receipt Accurate dipicu **jendela tanggal** (`FilterByShippedAt` / `FilterByIncomePaidAt`), bukan oleh perubahan dokumen. Menulis field baru tak mengubah satu pun jawaban query itu.
3. **Nol change stream / watcher** di seluruh `services/integration` — tak ada yang bereaksi terhadap tulisan ke `transaction_orders`.

Sekelas dengan [[RUN - Deploy Microservices bip-erp]] §backfill sub-total TikTok, yang aman dengan syarat identik.

## Prasyarat

- Build yang memuat atribusi sudah ter-deploy. Bukti: `docker exec Integration-Service sh -c "strings /service | grep -c shopee_attribution"` mengembalikan **> 0**. ⚠️ `docker ps` dan `/health` **bukan** bukti.
- Env: `MONGO_URI` (+ `MONGO_DB`, `MONGO_INITDB_ROOT_USERNAME`, `MONGO_INITDB_ROOT_PASSWORD` bila dipakai) menunjuk Mongo **prod**. ⚠️ `MONGO_URI_ERP` di `.env` repo **BUKAN prod** — konfirmasi host sebelum menyambung.
- Dijalankan dengan `go run` dari mesin yang bisa menjangkau Mongo prod. ⚠️ Binernya **sengaja TIDAK dikapalkan ke image** — sama seperti 100 perintah `cmd/` lain di service ini; jangan menambahkannya ke Dockerfile.

---

## 1. Baseline

```
mongosh "$MONGO_URI" --eval 'db.transaction_orders.aggregate([{$match:{channel:"SHOPEE"}},{$group:{_id:"$shopee_attribution",n:{$sum:1}}}])'
```

Catat sebarannya. Sebelum backfill pertama, seluruhnya `null`.

## 2. DRY RUN — wajib, jangan dilewati

```
go run ./cmd/attributionbackfill/ -dari 20250601 -sampai 20260901
```

Tanpa `-tulis` ia **tidak menyentuh satu dokumen pun**; repo tulisnya diganti pembungkus no-op.

**Bandingkan cacahnya dengan angka yang sudah diukur di prod 2026-09-01:**

| Golongan | Harus keluar |
|---|---|
| `direct` | 14.704 |
| `indirect` | 22.253 |
| `organic` | 58.145 |
| `unknown` | 1.976 |
| **jumlah** | **97.078** |

⛔ **Bila melenceng jauh, BERHENTI — jangan lanjut `-tulis`.** Selisih besar berarti jangkauan ledger atau watermark berubah sejak pengukuran, dan labelnya belum tentu benar.

⚠️ Angka totalnya akan naik seiring waktu (order baru masuk). Yang harus stabil adalah **`direct` per bulan** untuk bulan yang sudah matang: 3.393 (Mei) / 3.555 (Jun) / 3.732 (Jul) / 3.988 (Agt) 2026.

## 3. Eksekusi

```
go run ./cmd/attributionbackfill/ -dari 20250601 -sampai 20260901 -tulis
```

Idempoten — aman diulang. Bisa dipersempit per toko dengan `-shop <shop_id>`.

## 4. Verifikasi

```
mongosh "$MONGO_URI" --eval 'db.transaction_orders.aggregate([{$match:{channel:"SHOPEE"}},{$group:{_id:"$shopee_attribution",n:{$sum:1}}}])'
```

Gerbangnya:

- Jumlah keempat golongan **= total order Shopee**. Tak boleh ada order yang jatuh ke luar klasifikasi.
- `unknown` **terkonsentrasi di dua tepi**, bukan tersebar acak: order paling lama (di bawah jangkauan ledger) dan order beberapa hari terakhir (di atas watermark). Bulan matang di tengah harus mendekati **nol** `unknown`.
- Order H-1 berlabel `unknown`, **bukan** `organic`. Bila `organic`, watermark tak tersimpan — periksa `db.shopee_attribution_states.find()`.

Lalu buka layar: **Order Management** (`/integration/transactions/list`), pilih platform **Shopee**, terapkan filter *Sumber order*. ⚠️ Membandingkan angka lewat `curl` **tidak menggantikan** langkah ini.

## Kalau hasilnya nol / semua `unknown`

- `db.shopee_attribution_states.countDocuments()` **= 0** → watermark belum pernah tersimpan. Watermark hanya ditulis worker 05:00 WIB; sebelum worker pertama menyala, seluruh order **memang** `unknown`. Tunggu, atau picu worker manual.
- Watermark ada tapi order tetap `unknown` → periksa jangkauan ledger toko itu: `db.shopee_affiliate_conversion.find({shop_id:"<id>"}).sort({place_order_date:1}).limit(1)`. Order di bawah tanggal itu memang **permanen** `unknown` (Shopee menolak permintaan Day di luar tiga bulan kalender).

## Dokumen Terkait

- [[Microservices - Integration Service]] — §Atribusi order Shopee
- [[API - Integration Service]] — param `shopee_attribution`
- [[APP - Web ERP]] — filter & kartu rekap di Order Management
- [[RUN - Deploy Microservices bip-erp]]
