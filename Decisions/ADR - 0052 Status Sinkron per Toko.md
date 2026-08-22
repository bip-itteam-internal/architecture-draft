**Status**: 🟡 Implemented di branch `feat/oauth-shop-status-history` (bip-erp + erp-frontend, 2026-08-22) — **belum merge/deploy**. Test hijau (BE 11 handler + 4 filter + 1 task; FE 6 panel, total suite oauth 46 lulus).

## Context

Beberapa toko di-banned marketplace, tetapi tidak ada konsep status per-toko di mana pun: `ListAllShops` (`shopee_repo.go`) mengembalikan semua toko tanpa filter dan memberi makan 6+ cron, dan refresh token dicoba ulang tiap 4 jam selamanya tanpa counter. Panggilan API ke toko banned **pasti gagal** — membakar kuota harian dan menyeret success rate seluruh partner app. Ini pola akar yang sama dengan insiden pembatasan akun Shopee (dok `docs/Final Shopee API Limit Analysis Root Cause.md`: success rate 58,1%, `refresh_access_token` 40,3%, akun dibatasi karena 7-day avg < 90%).

`shopee_shop_infos.status` (NORMAL/BANNED/FROZEN dari `get_shop_info`) ada tapi **beku sejak connect** (sengaja tak di-refresh demi kuota Ads) dan tak pernah dibaca worker — bukan sumber keputusan yang layak.

## Decision

1. **Status sinkron LOKAL per toko** di koleksi **terpisah** `shop_sync_states` (unique `channel+shop_id`; `ACTIVE`/`DISABLED` + alasan + actor), BUKAN field di dokumen toko — nalar yang sama dengan [[ADR - 0027 Status Sinkron Resi Terpisah dari Update_Time Marketplace]]: dokumen toko ditulis ulang saat re-sync/re-auth sehingga field lokal bisa hilang senyap. Toko tanpa dokumen = ACTIVE.
2. **Semua jalur sync melewati toko DISABLED lewat satu pintu**: `ListSyncableShops` (Shopee & TikTok) / `ListSyncableAuthorizedShops` (TikTok per-credential) — dipasang di 6 cron Shopee, `RefreshAllCredentials`, tracking sync, wallet-sync (sisi Shopee), review-sync (dua channel), ICC video, order sync + reconcile TikTok, affiliate orders, stale-toship guardian. **Worker/jalur sync baru WAJIB memakai `ListSyncable*`, bukan `ListAllShop`.**
3. **Fail-open**: repo state nil (cmd/ tools) atau koleksi tak terbaca → set disabled kosong + warn, semua toko diproses. Lebih baik sync kelebihan daripada seluruh sync mati karena satu koleksi baru.
4. **Skip selalu bersinyal**: ringkasan run (Telegram/log) memuat "N toko nonaktif dilewati" — mengikuti aturan yang lahir dari kasus `toko-tanpa-config-alert` di [[Microservices - Integration Service]]: toko yang dilewati tidak boleh lenyap senyap.
5. **Toggle manual + riwayat**: endpoint `/shops/*` (lihat [[API - Integration Service]]) — disable admin-only dengan **alasan wajib**, transisi atomik (filter status lama; race → no-op idempoten), riwayat append-only di `shop_status_histories`. FE: panel "Shop Sync Status" di tab Shopee & TikTok Shop halaman `/integration/oauth` ([[APP - Web ERP]]), default hanya menampilkan toko butuh-perhatian (DISABLED / marketplace BANNED-FROZEN).
6. **Disable ≠ Revoke**: kredensial & data historis tetap utuh; toko yang menang banding tinggal di-enable.

## Consequences

- Toko banned berhenti membakar kuota begitu di-disable; success rate naik karena panggilan pasti-gagal (terutama refresh 4-jam-an) hilang dari penyebut.
- Toko DISABLED berhenti disinkron **sepenuhnya** (order/retur/escrow/wallet/review) — kesalahan disable menghentikan data masuk; mitigasinya sinyal di tiga tempat (badge FE, baris "skip N" per run, riwayat ber-actor).
- Order TO_SHIP toko disabled sengaja TIDAK di-touch guardian — begitu toko enable lagi, kandidat langsung tersapu run berikutnya.
- Yang sengaja TIDAK difilter (dampak kuota kecil): wallet-sync sisi TikTok, `tt_shop_master_data` (satu call per credential; menjaga daftar toko segar supaya re-enable mudah), jalur webhook.
- **Tahap 2 (belum dibuat)**: auto-disable setelah ≥5 kegagalan auth beruntun (classifier `isShopeeAuthError` / dead-check refresh TikTok) + notifikasi Telegram ber-damper persisten meniru `MetaCredential.DeadNotifiedAt`.
- Riwayat tanpa TTL (volume rendah — hanya aksi manual); bila Tahap 2 menambah event otomatis, beri `expires_at` + TTL index parsial.

## Dokumen Terkait

[[API - Integration Service]] · [[Microservices - Integration Service]] · [[APP - Web ERP]] · [[ADR - 0027 Status Sinkron Resi Terpisah dari Update_Time Marketplace]] · [[ADR - 0031 Prefix internal Bukan Batas Keamanan]] · [[ADR - 0011 Integration Read Cache + Singleflight (Fase 1 Perf)]] · [[Sales - Marketplace Integration]]
