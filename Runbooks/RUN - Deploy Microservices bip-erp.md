> **Status**: ⚠️ Implemented (prosedur diturunkan dari praktik deploy prod sesi 2026-07; nilai host/creds diisi saat eksekusi). Grounded ke `bip-erp/docker-compose.yml`.

## Tujuan

Men-deploy ulang **satu** microservice bip-erp ke produksi (rebuild image + recreate container) **tanpa menyentuh dependensinya** — khususnya database — agar aman dijalankan di **jam rawan (banyak order masuk)**.

## Kapan dipakai

- Rilis perubahan kode satu service (mis. `warehouse-service`, `integration-service`) ke prod.
- Hotfix cepat saat traffic sedang tinggi.

## Prasyarat

- Akses SSH VM prod + izin `docker compose` di folder stack (tempat `docker-compose.yml`).
- Dependensi service **sudah sehat & jalan** (mongo/redis/service lain). Bila ada yang mati, lihat catatan `--no-deps` di §2.

## 1. Perintah deploy per-service

```bash
docker compose up -d --build <service> --no-deps
```

`--build` rebuild image dari source; `-d` detached; **`--no-deps` = kunci utama** (lihat §2).

## 2. Kenapa `--no-deps` WAJIB di jam rawan

`docker compose up <service>` secara default **ikut menyalakan/recreate semua yang ada di `depends_on`** service tersebut. Di `docker-compose.yml`, `warehouse-service` **`depends_on: warehouse-mongo-db`** (`condition: service_healthy`). Tanpa `--no-deps`, deploy warehouse bisa **menyentuh MongoDB warehouse** → seluruh operasi gudang putus beberapa saat, bukan cuma service target.

`--no-deps` membatasi **blast radius ke container target saja**: service restart ~beberapa detik lalu reconnect ke mongo/redis yang tetap hidup. Job in-process (reconciler 60s, open-order sweep 5m) mulai lagi otomatis — lihat [[IT - Background Jobs & Schedulers]].

> **JANGAN pakai `--no-deps` bila dependensi sedang MATI.** `--no-deps` melewati health-gating; di kondisi itu Anda justru butuh compose menyalakan mongo/redis dulu (deploy tanpa `--no-deps`, atau nyalakan dependensi manual lebih dulu).

## 3. Urutan aman antar-service yang saling bergantung

Bila dua service dirilis bersama dan salah satu memanggil yang lain saat boot/runtime, **deploy penyedia API dulu**. Contoh (fitur open-order sweep):

1. `docker compose up -d --build integration-service --no-deps` (penyedia param `order_ids`)
2. `docker compose up -d --build warehouse-service --no-deps` (konsumen — sweep memanggil `?order_ids=`)

Urutan terbalik hanya berisiko sementara (warehouse memanggil endpoint yang belum paham param baru → filter diabaikan) sampai integration ter-update; bukan fatal, tapi hindari di jam rawan.

## 3b. Fitur dorman di balik feature flag (aman deploy siapa pun)

Beberapa fitur landing **DORMANT** — kode ada di produksi tapi tidak jalan sampai env flag dinyalakan sengaja. **Deploy integration-service oleh siapa pun TIDAK mengaktifkannya** selama flag tidak di-set `true` di `.env`.

- **`AUTO_ARRANGE_ENABLED`** (integration-service, default **off**) — worker `auto-arrange` (pengganti auto-ship Desty) hanya didaftarkan bila `=true`. **JANGAN set `true` sampai cutover Desty→WMS** (WMS gudang mulai dipakai & arrange manual Desty dihentikan). Mengaktifkan = aksi kirim NYATA & irreversible ke marketplace. Lihat [[External - Desty]] & [[IT - Background Jobs & Schedulers]]. Verifikasi status di log boot: `auto-arrange scheduler DORMANT` (off) vs `... ENABLED` (on).

## 4. Verifikasi pasca-deploy

```bash
docker logs <Container-Name> --tail 40
```
- `warehouse-service` (container `Warehouse-Service`): cari `Reconciler started` + `Open-order sweep started (5m interval)`; tidak ada panic MongoDB.
- `integration-service` (container `Integration-Service`): service listen + tidak ada error koneksi.
- Health: `GET /health` service (via gateway/internal) → `{"status":"ok"}`.

## 5. Troubleshooting (gejala → akar → fix)

| Gejala | Akar | Fix |
|---|---|---|
| Operasi gudang putus sesaat pasca-deploy | deploy **tanpa** `--no-deps` → mongo warehouse ikut di-recreate | selalu `--no-deps` di jam rawan (§2) |
| Service gagal start "connection refused" mongo/redis | dependensi mati + `--no-deps` melewati gating | nyalakan dependensi dulu / deploy tanpa `--no-deps` |
| Perubahan env/port tak terbaca | `up -d --build` saja kadang tak recreate | tambahkan `--force-recreate` (env berubah) |
| Sweep/reconciler tak jalan | `REDIS_URL` kosong | pastikan env redis terisi; log akan bilang "tidak diaktifkan" |

## Dokumen Terkait

- [[Microservices - Warehouse Service]] · [[Microservices - Integration Service]] — implementasi service
- [[IT - Background Jobs & Schedulers]] — poller in-process (reconciler + sweep) yang restart otomatis
- [[RUN - Deploy Task Management Service]] — runbook deploy service lain (dengan migrasi data)
- [[CORE - API Master Gateway]] — health via gateway
