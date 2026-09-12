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
cd <folder stack>
git fetch origin main && git reset --hard origin/main   # ← WAJIB, lihat §1a
docker compose up -d --build <service> --no-deps
docker image inspect bip-erp-<service> --format '{{.Created}}'   # ← gerbang, lihat §1b
```

`--build` rebuild image dari source; `-d` detached; **`--no-deps` = kunci utama** (lihat §2).

### 1a. Tarik kode dulu — `--build` membangun dari DISK, bukan dari `main`

Runbook ini semula langsung ke perintah compose, karena sesi yang melahirkannya kebetulan punya
checkout yang sudah mutakhir. Asumsi itu tak pernah terlihat sampai ia menggigit.

**2026-08-14, produksi**: PR sudah merge ke `main`, `docker compose up -d --build
integration-service --no-deps` dijalankan, dan **semuanya melaporkan berhasil** — build sukses,
container naik, healthcheck hijau. Tetapi checkout di VM masih commit lama, jadi tak satu pun
berkas berubah, build kena cache penuh, dan **image yang dihasilkan identik dengan yang lama**.
Perilaku service tidak berubah sedikit pun. Tidak ada satu pun pesan galat di mana pun.

### 1b. "Build sukses" BUKAN bukti — periksa umur image

Dua kegagalan senyap yang berlawanan arah, keduanya terjadi dalam dua hari ke tim yang sama:

| Yang basi | Gejalanya |
|---|---|
| **Container** (checkout benar) | Fitur tampak "sudah di prod" padahal biner lama yang melayani — `integration-service` tertinggal 10 jam setelah dua PR merge, 2026-08-14 |
| **Checkout** (container baru dibangun) | `build` dan `up -d` sama-sama sukses, image identik, timestamp tak bergerak |

Gerbangnya satu baris, dan ia yang membedakan keduanya:

```bash
docker image inspect bip-erp-<service> --format '{{.Created}}'
```

Harus **lebih baru dari waktu merge commit yang kamu harapkan hidup**. `docker ps`, `/health`,
`docker compose build` yang sukses, dan "checkout-nya sudah benar" — **tak satu pun dari itu
membuktikan biner mana yang sedang melayani permintaan**. Bukti terakhirnya tetap satu panggilan
lewat gateway yang menunjukkan perilaku barunya.

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

## 3a2. Service yang ada di compose PRODUKSI tapi tidak di compose DEV

`docker-compose.yml` dan `docker-compose.dev.yml` **bukan cerminan satu sama lain**. Beberapa service hanya didefinisikan di yang pertama, sementara `*_MODULE_URL`-nya tetap dipasang di gateway dev — memang harus, sebab gateway memanggil `ValidateInternalURL` untuk SELURUH `InternalURL` saat start dan akan restart-loop bila ada yang kosong (§3a).

Akibatnya URL-nya ADA tapi container-nya TIDAK. Panggilan mati di resolusi DNS dan kembali sebagai **502**, bukan 404 — jadi gejalanya terbaca seperti "service-nya rusak" atau "gerbangnya menolak", padahal service-nya memang tak pernah dijalankan. Layar yang bersangkutan hanya bisa diuji pada **jalur gagalnya**.

| Service | Status di compose dev |
|---|---|
| `procurement-service` (+ `procurement-mongo-db`) | **Ditambahkan 2026-08-10.** Panel Permintaan Barang & Pesanan Pembelian di Ruang Direktur ([[APP - Web ERP]]) baru bisa diuji dengan data sungguhan sejak saat itu. |
| `payroll-service` (+ `payroll-mongo-db`) | **Ditambahkan 2026-08-10.** Mongo-nya memakai host port **32795**, bukan 32792 seperti di compose produksi — di dev 32792 sudah dipakai `warehouse-mongo-db`. |

Setelah `payroll-service` hidup, `PAYROLL_PERMISSION_ENFORCEMENT` **sengaja tidak diset di compose dev**, jadi dev menegakkan izin di kedua permukaan payroll. Produksi tidak: nilainya `"off"` di sana, tapi **hanya di blok `attendance-service`** — sementara `payroll-service` membaca nama env yang sama justru supaya satu modul punya satu sakelar. Ketimpangannya dicatat, bukan ditiru ke dev; lihat [[CORE - RBAC dan Permission Set]].

> ⚠️ **`env_file: .env` memuat SELURUH `.env` ke container, termasuk yang tak disebut di blok `environment`.** Di dev itu berarti kredensial **Accurate produksi** ikut masuk ke setiap service — dibuktikan log boot procurement yang menyebut "mode token statis" walau blok `environment`-nya tak menyertakan satu pun `ACCURATE_*`. Berlaku untuk semua service dev, bukan satu. Konsekuensi praktisnya: **jangan pakai dev untuk mencoba sync/push dokumen ke Accurate.** Yang sengaja TIDAK diteruskan ke procurement dev hanyalah `INTEGRATION_MONGO_URI`, supaya dev tak ikut membaca/menyegarkan token OAuth milik integration-service.

## 3b. Fitur dorman di balik feature flag (aman deploy siapa pun)

Beberapa fitur landing **DORMANT** — kode ada di produksi tapi tidak jalan sampai env flag dinyalakan sengaja. **Deploy integration-service oleh siapa pun TIDAK mengaktifkannya** selama flag tidak di-set `true` di `.env`.

- **`AUTO_ARRANGE_ENABLED`** (integration-service, default **off**) — worker `auto-arrange` (pengganti auto-ship Desty) hanya didaftarkan bila `=true`. **JANGAN set `true` sampai cutover Desty→WMS** (WMS gudang mulai dipakai & arrange manual Desty dihentikan). Mengaktifkan = aksi kirim NYATA & irreversible ke marketplace. Lihat [[External - Desty]] & [[IT - Background Jobs & Schedulers]]. Verifikasi status di log boot: `auto-arrange scheduler DORMANT` (off) vs `... ENABLED` (on).

## 3c. TTL index: masa simpannya TIDAK bisa diubah lewat deploy

`attendance-service` membuat TTL index saat boot untuk koleksi `submission_attempt` (jejak percobaan pengajuan, [[ADR - 0046 Percobaan Pengajuan Dijejaki Middleware, Bukan Panggilan per Cabang]]), lewat `ensureSubmissionAttemptIndexes` dengan `SetExpireAfterSeconds(365 * 24 * 60 * 60)`.

**Mengubah angka itu di kode lalu men-deploy TIDAK mengubah apa pun.** `CreateOne` atas index yang sudah ada dengan spesifikasi berbeda bukan operasi yang menimpa: Mongo menolaknya, dan penjaganya di sini hanya `log.Printf` yang tidak memblokir start. Jadi gejalanya **senyap**: deploy sukses, container sehat, retensinya tetap yang lama, dan tak ada yang tahu sampai ada yang menghitung umur dokumen tertua.

Mengubah retensi menuntut langkah manual yang **bukan bagian dari deploy**:

```bash
# di container mongo koleksi yang bersangkutan
db.submission_attempt.dropIndex("at_1")
# lalu restart service-nya supaya ensure...Indexes() membuat ulang dengan nilai baru
```

Verifikasinya satu baris, dan jangan percaya deploy tanpa menjalankannya:

```bash
db.submission_attempt.getIndexes()   # cari expireAfterSeconds pada index `at_1`
```

Pola yang sama berlaku untuk TTL index mana pun yang lahir dari `ensure*Indexes()` di service lain. Aturan umumnya: **index yang sudah ada tidak pernah berubah karena deploy**, hanya index yang belum ada yang dibuat.

## 3d. Kunci layanan baru → pengirim DAN penerima naik bersama, dengan `--force-recreate`

Kopling ini berbeda lagi dari §3 dan §3a: bukan urutan panggilan, bukan isi biner, melainkan **nilai env yang harus sama di dua container**. Rute bahan penilaian KPI digerbang kunci layanan lewat query `key`, bukan header gateway, karena gateway memasang `BIP-Gateway-ID` pada setiap permintaan ber-JWT ([[ADR - 0031 Prefix internal Bukan Batas Keamanan]]). Cara menambah kunci semacam itu beserta rutenya ada di [[RUN - Menambah Metrik KPI Otomatis]]; bagian ini hanya soal men-deploy-nya. `.env.example` mencatat pasangan lain berpola sama (mis. `WAREHOUSE_SERVICE_KEY`, `ATTENDANCE_SERVICE_KEY`).

> ⚠️ **`FORM_BUILDER_SERVICE_KEY`** ([[ADR - 0090 Inspeksi Satgas 5R dan K3 di Form Builder dengan Nilai dari Cek Ulang Terakhir]] T3) ada di bip-erp branch `feat/satgas-nilai-kpi` per 2026-09-12: **belum PR, belum merge, belum deploy**. Isi `.env` DEV dan PROD untuk env ini **belum diukur**.

| Container | Perannya | Bila env-nya kosong |
|---|---|---|
| `form-builder-service` | penerima: `GET /internal/satgas/metrics` memeriksa `key` | rute menolak **semua** pemanggil dengan 401 (gagal tertutup) |
| `employee-service` | pengirim: sumber KPI `nilai_inspeksi_satgas` | sumbernya gagal hitung: `FORM_BUILDER_SERVICE_KEY belum diatur` |

Nilai yang berbeda di kedua blok berakibat sama dengan kosong di penerima, dan employee-service menuliskannya `form-builder menolak kunci layanan (401); periksa FORM_BUILDER_SERVICE_KEY di form-builder dan employee-service`. Kedua galat itu berkelas `gagal mengambil data`, bukan `belum dapat dihitung`, jadi selama metriknya belum diisi manual, **skor orang yang templatenya memakai sumber ini tidak ditampilkan** (`adaSumberGagalTanpaNilai`), bukan cuma satu metrik yang kosong.

Env dibaca saat container **DIBUAT**, jadi `restart` tidak cukup (baris `--force-recreate` di §5). Perintahnya §1 ditambah `--force-recreate`, penyedia rute lebih dulu sesuai §3:

```bash
docker compose up -d --build --force-recreate form-builder-service --no-deps
docker compose up -d --build --force-recreate employee-service --no-deps
```

Gerbang umur image §1b tetap berlaku untuk keduanya. `/health` hijau tak membuktikan apa pun di sini; yang membuktikan adalah tiga pemeriksaan ini, masing-masing menjawab satu kegagalan:

1. **Rutenya tertutup bagi karyawan.** Lewat gateway dengan JWT karyawan biasa, tanpa `key`: `GET /api/form-builder/internal/satgas/metrics?period=<YYYY-MM>` harus **401** berbadan `{"error":"Unauthorized gateway"}`. Badan `Invalid or expired token` berarti gateway yang menolak JWT-nya, jadi gerbang kuncinya belum teruji. **200 di sini adalah kebocoran nilai per orang.**
2. **Kuncinya sama di kedua container.** Dari dalam `Employee-Service`, memakai env container itu sendiri (kutip tunggal, supaya variabelnya diurai di dalam container, bukan di shell host). Rute ini baca-saja:

   ```bash
   docker exec Employee-Service sh -c 'wget -qO- --header="BIP-Gateway-ID: $INTERNAL_GATEWAY_KEY" "$FORM_BUILDER_MODULE_URL/internal/satgas/metrics?period=<YYYY-MM>&company_id=BIP&key=$FORM_BUILDER_SERVICE_KEY"'
   ```

   Harus 200 **berbentuk kontrak**, bukan sekadar 200: `has_form` dan `period_key` selalu ada; `orang[]` hanya bila `has_form` true, tiap butirnya `employee_id`, `forms_dinilai`, `forms_total`, `ada_kiriman`, `menunggu_cek_ulang` (plus `nilai`, `batas_cek_ulang`, `form_tanpa_skala` bila terisi), dan **tanpa** nama, departemen, atau jabatan. Header gateway wajib ikut karena form-builder memasang `ValidateGateway` untuk seluruh rutenya; tanpa header itu 401-nya datang dari gerbang tersebut dan tak mengatakan apa pun tentang kuncinya.
3. **Sumbernya membaca, bukan gagal.** Untuk metrik yang sudah dipasang HR dengan sumber `nilai_inspeksi_satgas`, `GET /api/employee/kpi/auto-values?employee_id=<id>&period=<YYYY-MM>&template_id=<id>` harus mengembalikan `auto_value` terisi atau `auto_basis` berawalan `belum dapat dihitung:`, dengan `auto_gagal_sumber: false`. Berawalan `gagal mengambil data:` berarti sumbernya tak berhasil membaca, dan kalimat sesudahnya menyebut sebabnya, termasuk env mana yang belum benar. (`POST /kpi/auto-values/pratinjau` sudah dicabut, jadi pemeriksaan ini butuh metrik yang sudah terpasang di template.)

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
| Endpoint balas **502** di dev padahal rute & gerbangnya benar | service-nya tak didefinisikan di `docker-compose.dev.yml` walau `*_MODULE_URL`-nya terpasang → mati di resolusi DNS | tambahkan service + mongo-nya ke compose dev (§3a2), bukan mengubah kode |
| Fitur jalan normal tapi **notifikasinya tak pernah tiba**, tanpa galat di layar | kategori inbox baru; `notification-service` masih memegang `InboxCategories` lama dan menolak `400`, sementara pengiriman best-effort hanya nge-log | rebuild `notification-service` juga (§3a), lalu picu satu notifikasi sungguhan untuk memastikan |
| Metrik KPI bersumber `nilai_inspeksi_satgas` berbasis `gagal mengambil data: FORM_BUILDER_SERVICE_KEY belum diatur` atau `gagal mengambil data: form-builder menolak kunci layanan (401)...`, dan skor orangnya tak tampil | `FORM_BUILDER_SERVICE_KEY` kosong di employee-service, kosong atau berbeda nilai di form-builder, atau `.env` sudah diisi tapi container belum dibuat ulang | isi nilai yang SAMA di kedua blok, `--force-recreate` keduanya, lalu tiga pemeriksaan §3d |

## Dokumen Terkait

- [[Microservices - Warehouse Service]] · [[Microservices - Integration Service]] — implementasi service
- [[Microservices - Form Builder Service]] · [[Microservices - Notification Service]] — pasangan yang wajib naik bersama saat kategori inbox bertambah (§3a)
- [[HRIS - Kaizen (Ide Perbaikan)]] — fitur yang kegagalan senyapnya jadi contoh di §3a
- [[ADR - 0090 Inspeksi Satgas 5R dan K3 di Form Builder dengan Nilai dari Cek Ulang Terakhir]] · [[Microservices - Employee Service]] (pasangan pengirim dan penerima `FORM_BUILDER_SERVICE_KEY`, §3d)
- [[RUN - Menambah Metrik KPI Otomatis]] (cara menambah kunci layanan beserta rutenya, §3d)
- [[IT - Background Jobs & Schedulers]] — poller in-process (reconciler + sweep) yang restart otomatis
- [[RUN - Deploy Task Management Service]] — runbook deploy service lain (dengan migrasi data)
- [[CORE - API Master Gateway]] — health via gateway
