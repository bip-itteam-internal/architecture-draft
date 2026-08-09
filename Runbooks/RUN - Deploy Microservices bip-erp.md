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

## 3a. Perubahan `shared-library` → SERVICE PEMBACA WAJIB IKUT NAIK

Kopling ini **berbeda dari §3** dan lebih mudah terlewat: bukan soal urutan panggilan API, melainkan daftar yang **ikut terkompilasi ke dalam biner** tiap service.

`shared-library` dipakai lewat `replace` ke path lokal (`go.mod` tiap service), jadi tak ada versi yang perlu dinaikkan — tapi **service yang tidak di-rebuild tetap memegang salinan lama**.

**Kasus nyata, sudah menggigit DUA KALI**: `notification.InboxCategories` adalah daftar-izin kategori inbox. `notification-service` menolak kategori di luar daftar itu dengan **`400`**, dan pengiriman di service pengirim bersifat **best-effort** — kegagalannya hanya masuk log.

Hasilnya fitur yang **tampak jalan sepenuhnya** sementara tak satu pun notifikasinya sampai:

- Saat kategori `form-published` lahir (2026-08-02).
- Saat `kaizen-reminder` dan `kaizen-decided` lahir (terdeteksi 2026-08-06, diperbaiki PR [#1044](https://github.com/bip-itteam-internal/bip-erp/pull/1044)).

**Aturannya**: menambah kategori inbox berarti deploy **dua** container, `<service-pengirim>` DAN `notification-service`. Untuk program Kaizen:

```bash
docker compose up -d --build form-builder-service --no-deps
docker compose up -d --build notification-service --no-deps
```

Urutannya tak kritis di sini — yang kritis keduanya naik. Selama hanya satu yang naik, gejalanya **senyap**: tak ada galat di layar, tak ada alert, cuma notifikasi yang tak pernah tiba.

**Verifikasi setelah deploy**, bukan sekadar melihat health: picu satu notifikasi sungguhan lalu pastikan ia muncul di kotak masuk penerimanya. Di dev 2026-08-06 hal ini terbukti membedakan "sudah naik" dari "belum": percobaan 4 menit setelah merge gagal total, percobaan ulang setelah deploy mendarat berhasil.

Penjaganya di sisi kode ada di `services/form-builder/notify_category_test.go` — menambah kategori tanpa mendaftarkannya di `shared-library` menggagalkan test. Penjaga itu tidak bisa tahu container mana yang sudah naik, jadi langkah deploy ini tetap manual.

**Kasus yang sama, gejala yang jauh lebih besar (dev, ditemukan 2026-08-09):** dua container memegang biner yang mendahului perubahan `shared-library`, dan keduanya menyesatkan pelacakan berjam-jam.

| Container | Umur image | Akibat |
|---|---|---|
| `api-gateway` | 12 Juli | `common.PayloadJWT` versi lama tak punya field `Permissions`/`SupervisedDepartments`, jadi gateway mem-parse balasan employee-service, **membuang kedua klaim**, lalu menandatangani token tanpanya. **SELURUH permission-set tak pernah aktif di dev** — payroll, finance, procurement, monitoring, hris — dan `reach: division` tak pernah punya cakupan untuk dinilai. |
| `it-orchestrator` | 12 Juli | Memanggil `getCurrentRoles(employeeID)` tanpa `ctx`, sehingga header `BIP-System-Roles` tak ikut terkirim ke rute `/internal/*` employee-service yang baru digerbang. Ubah-role membalas **502** selama sepuluh hari. Rinciannya di [[CORE - IT Orchestrator]]. |

Yang membuat keduanya mahal: **gejalanya menunjuk ke arah yang keliru**. Menu tetap hilang meski paket sudah dipasang dan sudah login ulang berkali-kali; tuduhan pertama jatuh ke logika RBAC. Dan gateway tak bisa dibangun ulang sama sekali — ia memanggil `ValidateInternalURL` untuk SELURUH `InternalURL` saat start, dan tujuh modul yang belum jalan di dev tak punya entri `*_MODULE_URL`, jadi tiap percobaan build berakhir restart-loop. Port ketujuhnya ada di `.env.example` tapi tak pernah tersalin ke `.env` lokal. Karena itulah tak ada yang pernah merebuild-nya.

**Cara memeriksa cepat** — bandingkan umur image dengan tanggal perubahan `shared-library` yang relevan:

```bash
docker inspect <Container> --format '{{.State.StartedAt}}'
docker image inspect <image> --format '{{.Created}}'
```

Kalau image lebih tua daripada commit yang menambah field/klaim yang sedang dicari, biner itu tak mengenalnya. Untuk klaim JWT, `strings /service | grep permissions` di dalam container menjawabnya langsung.

> **Aturan yang lebih luas:** membaca kode di repo tidak cukup untuk menyimpulkan perilaku sebuah lingkungan. Sebelum menuduh logika, pastikan biner yang berjalan memang memuat logika itu. Per 2026-08-09 **tujuh service dev masih memakai image 12 Juli** (attendance, hris-orchestrator, insentive, inventory, notification, task-management, tiktok-shop).

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
| Fitur jalan normal tapi **notifikasinya tak pernah tiba**, tanpa galat di layar | kategori inbox baru; `notification-service` masih memegang `InboxCategories` lama dan menolak `400`, sementara pengiriman best-effort hanya nge-log | rebuild `notification-service` juga (§3a), lalu picu satu notifikasi sungguhan untuk memastikan |

## Dokumen Terkait

- [[Microservices - Warehouse Service]] · [[Microservices - Integration Service]] — implementasi service
- [[Microservices - Form Builder Service]] · [[Microservices - Notification Service]] — pasangan yang wajib naik bersama saat kategori inbox bertambah (§3a)
- [[HRIS - Kaizen (Ide Perbaikan)]] — fitur yang kegagalan senyapnya jadi contoh di §3a
- [[IT - Background Jobs & Schedulers]] — poller in-process (reconciler + sweep) yang restart otomatis
- [[RUN - Deploy Task Management Service]] — runbook deploy service lain (dengan migrasi data)
- [[CORE - API Master Gateway]] — health via gateway
