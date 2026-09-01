# `/orders/get` — daftar order

| | |
|---|---|
| **Path** | `/orders/get` |
| **Method** | `GET` |
| **Auth** | `app_key` + `timestamp` (unix **ms**) + `sign_method=sha256` + `access_token` + `sign` |
| **Dipakai di kode** | `LazadaClient.GetOrders`, `LazadaClient.GetOrdersRange` (`internal/infrastructure/clients/lazada_client.go`) |
| **Confidence** | `created_*` **verified-by-usage** · `update_*` **verified-live 2026-09-01** |

## Dua sumbu window: BUAT vs UBAH

Endpoint ini menerima **dua pasang** filter waktu yang berdiri sendiri. Perbedaannya menentukan
apakah sebuah penyapu berkala bisa menangkap perubahan status atau tidak.

| Param | Arti | Status |
|---|---|---|
| `created_after` / `created_before` | window **waktu order dibuat** | verified-by-usage (dipakai `GetOrders`/`GetOrdersRange`) |
| `update_after` / `update_before` | window **waktu order terakhir berubah** | **verified-live 2026-09-01** |
| `limit` | maks 100 | verified-by-usage |
| `offset` | paging | verified-by-usage |
| `sort_by` / `sort_direction` | `created_at`, `ASC`/`DESC` | verified-by-usage |

### Bukti live (probe read-only, toko 401556928228, 2026-09-01)

Rancangan probe memakai panggilan **kontrol** lebih dulu supaya hasilnya tak ambigu: bila kontrol
sukses, sign & kredensial terbukti benar, sehingga kegagalan pada uji pasti soal parameternya.
Pembedanya order `2783465852040104` — **dibuat 21 Agu, diperbarui 27 Agu**.

| Panggilan | `count` | memuat order pembeda |
|---|---|---|
| kontrol `created_after=2026-08-26` | 11 | **tidak** (benar: dibuat sebelum window) |
| `update_after=2026-08-26` | **24** | **ya** |
| `update_after=2026-08-26` + `update_before=2026-08-28` | 7 | ya |

Semua `HTTP 200`, `code="0"`.

## Kenapa ini penting

Order Lazada masuk ERP **hanya lewat webhook LPM** — tak ada penarik berkala seperti Shopee
(`sync-shopee-orders`) atau TikTok. Lihat [[IT - Background Jobs & Schedulers]].

Penyapu berbasis `created_after` **tidak cukup** sebagai jaring pengaman: order yang dibuat
sebelum window lalu berubah status di dalam window tak akan tersentuh. Itu persis kelas
kegagalan insiden 2026-09-01 — order 13–21 Agustus yang dikirim & sampai selama webhook mati,
dan statusnya beku di ERP. Angka di atas mengukurnya: 24 berbanding 11 pada window yang sama,
jadi sapuan waktu-buat melewatkan lebih dari separuh.

**Untuk guardian, pakai `update_after`/`update_before`.**

## Respons (field yang dipakai)

```
data.count                 int
data.orders[].order_id     int64
data.orders[].created_at   string
data.orders[].updated_at   string
data.orders[].statuses[]   []string  → mapLazadaStatus (lazada_transform.go)
```

> **Jebakan**: `statuses` order-level bisa TERTINGGAL dari kenyataan. Terukur 2026-09-01 pada
> `2783465852040104`: item `status="confirmed"` padahal `/logistic/order/trace` sudah
> `detail_type="delivered"`. Penyembuhnya jalur tracking (`sync-tracking` → promote status),
> bukan status order. Lihat [[order.order-items-get]] bila kelak dibuatkan.
