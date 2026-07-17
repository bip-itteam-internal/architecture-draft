> **Status:** ✅ Implemented (17 Juli 2026) — **kill switch default MATI** (`ACCURATE_WMS_PUSH`); belum pernah dinyalakan di environment mana pun. Menyalakannya butuh koordinasi finance.

## Context

Sejak master & stok WMS manufaktur read-sync dari [[External - Accurate]], pergerakan **internal gudang** (konsumsi bahan produksi, hasil produksi, masuk-kembali sisa, koreksi proposal) tidak pernah sampai ke Accurate — sync berikutnya membuat pergerakan itu tampak "dibatalkan" di snapshot stok, dan validasi "stok cukup" bisa dibohongi (keluar 100, sync, angka kembali, keluar 100 lagi padahal fisik kosong).

Sebagian pergerakan **sudah** menggerakkan Accurate lewat jalur lain — diverifikasi terhadap kode integration:
- Keluar FG marketplace → **Sales Invoice** otomatis (`OnOrderToShip`/`OnOrderCompleted` → `sales-invoice/save.do`).
- Return/cancel marketplace → **Sales Return** otomatis (`OnOrderCancelledOrReturned` → `sales-return/save.do`).
- Order sampel TikTok → **Penyesuaian Persediaan** harian (`OnSampleShipped`).

## Decision

Pergerakan WMS didorong ke Accurate sebagai **dokumen Penyesuaian Persediaan harian per arah** (maks. 2 dokumen/hari: `WMS Manufaktur Keluar/Masuk <tanggal>`), **kecuali** yang sudah tercakup jalur lain:

| Pergerakan | Penanda (`detail` transaksi) | Didorong? |
|---|---|---|
| Keluar FG marketplace (F4) | `marketplaceSalesDetection` | ❌ — tercakup Sales Invoice |
| Return ekspedisi (F3) | `namaMarket` | ❌ — tercakup Sales Return |
| Kirim Produk (transfer keluar) | `driver` | ❌ — net antar gudang nol |
| Input Gudang FG (transfer masuk) | `gudangSimpan` | ❌ — pasangan di atas |
| Saldo OPENING era import | `ref: OPENING` | ❌ — baseline |
| Konsumsi bahan produksi, hasil produksi, masuk-kembali, koreksi proposal, transaksi manual | (sisanya) | ✅ |

Mekanisme (`services/manufacture/accurate_push.go` + integration `POST /accurate/wms-adjustment`):
- **Pemindai watermark** atas ledger `manufacture_transaksi` — bukan hook per-form (kebal rollback transaksi Mongo, otomatis mencakup jalur tulis baru). Watermark perdana = saat pertama dipindai → **sejarah lama tak pernah ikut terdorong**.
- **Outbox** `manufacture_accurate_push` (`_id` = id transaksi → dedupe alami; baris SKIP selalu menyimpan alasan, bisa diaudit `GET /accurate/push/outbox`).
- **Konversi satuan = kebalikan sync stok**: WMS gram → Accurate kg (÷1000), `faktor_stok_accurate` per-item (÷faktor), PCS/FG apa adanya.
- **Idempoten**: protokol edit resmi Accurate (header id + baris lama `_status: delete`) — push ulang di hari yang sama meng-edit dokumen; hash isi untuk skip-unchanged. State harian (accurate_id/number/hash) di `manufacture_accurate_push_day`; integration stateless.
- **Kill switch** `ACCURATE_WMS_PUSH=true` (compose, default `false`) — kredensial Accurate dev/prod menunjuk **pembukuan sungguhan**. Loop otomatis (10 mnt) hanya jalan bila aktif; `POST /accurate/push?dry_run=true` untuk pratinjau kapan pun.

## Consequences

- Setelah dinyalakan, sync stok tidak lagi "membatalkan" pergerakan internal — kedua buku bergerak bersama; jendela selisih tinggal jeda push (≤10 menit) + jeda sync.
- Finance akan melihat maksimal 2 dokumen Penyesuaian Persediaan per hari berlabel "WMS Manufaktur …" — perlu sosialisasi supaya tidak dianggap anomali; angka di dalamnya dalam **satuan Accurate** (kg dsb.).
- **Prasyarat menyalakan**: kode barang dua sisi sudah selaras (sudah — trio align), finance tahu & setuju, dan diverifikasi dengan satu pergerakan kecil dulu sambil melihat dokumennya muncul di Accurate. Penyalaan perdana disarankan di jam tenang: dokumen pertama hari itu = create, sisanya edit.
- Batas pengujian: kredensial Accurate localhost sengaja mati → jalur "berhasil menulis ke Accurate" belum pernah tereksekusi; yang terverifikasi adalah klasifikasi, konversi, idempotensi lokal, dan gagal-aman (outbox tetap PENDING saat Accurate tak terjangkau).
- Pergerakan yang keliru penanda (mis. form baru tanpa marker) akan ikut terdorong — mitigasi: outbox auditable + dry-run; tambah marker/aturan klasifikasi bila form baru lahir.

## Dokumen Terkait

- [[Microservices - Manufacture Service]] · [[Microservices - Integration Service]] · [[API - Manufacture Service]] · [[API - Integration Service]]
- [[ADR - 0001 Akuntansi via Accurate]] (Accurate = pemegang saldo) · [[RUN - Selaraskan Kode Bahan WMS ke Accurate]] (prasyarat kode selaras)
