## Deskripsi

*Asisten tanya-jawab di dalam Web ERP yang menjawab pertanyaan tentang angka bisnis dengan cara MERUTEKAN pertanyaan ke endpoint yang sudah menghitungnya, bukan dengan menghitung sendiri. Ia memanggil endpoint memakai JWT orang yang bertanya, sehingga hak aksesnya identik dengan hak akses orang itu di layar. ~~Irisan pertama diarahkan ke data marketing analytics.~~ **Diputuskan berbeda 2026-09-28** ([[ADR - 0132 Asisten AI Tanya-Jawab Lintas Modul, Lapisan Data Bisnis per Service Bukan Terpusat]]): cakupan lintas modul sejak awal, dimulai beberapa modul percontohan sekaligus, dibatasi ke Supervisor/Direktur/IT.*

- **Status**: 🟡 **Konsep**, 2026-08-29. ~~0 kode, dikonfirmasi ulang lewat `git grep` langsung ke
  kode 2026-09-28.~~ **T1 sekarang punya kode nyata, 2026-09-28**: `bip-erp/services/assistant/`
  ada — `internal/aiclient/` (klien tipis OpenAI-compatible, `client.go`+`types.go`+11 test) dan
  `cmd/probe/main.go` (CLI verifikasi manual), 536 baris. Baru klien AI dasar (T1 di papan kerja
  `ANALISA - Asisten AI Lintas Modul`); **belum ada Fiber/gateway route, RBAC, maupun endpoint
  modul apa pun** (T2 dst). Merged 2026-09-29
  ([bip-erp#2150](https://github.com/bip-itteam-internal/bip-erp/pull/2150)) — status
  keseluruhan tetap 🟡 Konsep sampai lebih banyak T-task selesai.
  **T2 kerangka service ditulis 2026-09-29** (branch `feat/assistant-skeleton`): Fiber +
  `ValidateGateway`, hanya `GET /` dan `GET /health` (`{"message":"ok"}`), tanpa database dan
  tanpa rute AI. Merged (bip-erp #2151) dan **terbukti di DEV 2026-09-29** lewat gateway dengan
  JWT sungguhan (`/api/assistant/health` → 200). PROD dinaikkan manusia 2026-09-29 (healthy,
  env gateway benar; panggilan ber-JWT lewat gateway prod belum dicoba).
  **Frontend: banner pengumuman "Copilot" + halaman placeholder `/copilot`** — murni pengumuman
  "Segera Hadir", **tidak memanggil backend apa pun**. Nama fitur yang diputuskan: **Copilot**.
  Sempat berupa menu di puncak sidebar
  ([erp-frontend#1788](https://github.com/bip-itteam-internal/erp-frontend/pull/1788)), lalu
  2026-09-28 diganti strip pengumuman di atas header yang sementara hanya terlihat Tech
  Development (erp-frontend#1790, lalu dipindah dari dalam konten ke atas header). Lihat § Persona.
  **Jadwal Tugas** diputuskan sebagai pengingat, bukan eksekusi otomatis — lihat § Jadwal Tugas.
  ⚠️ **SEBAGIAN DIGANTIKAN 2026-09-22** oleh [[ADR - 0120 Asisten Analisa Marketing Jadi Menu ERP, Template dan Jadwal Lebih Dulu Tanpa AI]]
  **untuk kasus laporan Marketing terjadwal saja**: asisten analisa marketing diputuskan berdiri
  **di dalam service pemilik data lewat klien tipis `shared-library/ai`**, bukan sebagai service
  tersendiri. ⚠️ **Klien `shared-library/ai` yang disebut di sana TERNYATA BELUM ADA sama sekali
  di kode** — diverifikasi `git grep` menyeluruh 2026-09-28, nol hasil di luar false-positive.
  Ketegangan dengan ADR 0058 §2 yang dicatat dokumen ini (§ Dua ketegangan terbuka) **sudah
  dijawab** di sana, tapi HANYA untuk kasus satu domain (Marketing) — untuk kasus tanya-jawab
  bebas **lintas modul**, ketegangan itu **dijawab beda** oleh
  [[ADR - 0132 Asisten AI Tanya-Jawab Lintas Modul, Lapisan Data Bisnis per Service Bukan Terpusat]]
  (2026-09-28): asisten lintas
  modul secara struktural **tetap jadi service terpisah** (`services/assistant/`, sesuai rencana
  di dokumen ini), karena tidak ada satu service pemilik untuk semua modul sekaligus.
  ⚠️ **"Tanya-jawab bebas ditunda sampai template terbukti dipakai" (2026-09-22) DIPUTUSKAN TIDAK
  BERLAKU LAGI oleh ADR-0132** (2026-09-28) — keputusan sadar untuk mulai cakupan lintas modul
  sekarang, bukan menunggu. Kunci RBAC yang dicatat TBD di dokumen ini (§ Belum Diputuskan)
  **sudah ditegaskan** ADR-0132 §3: Supervisor departemen mana pun ATAU Direktur ATAU IT (Corp
  Sec belum ditegaskan). Yang TETAP berlaku dari dokumen ini: empat keputusan rancangannya
  (asisten dilarang berhitung, tool memanggil lewat gateway dengan JWT pemakai, jawaban adalah
  pintu), empat penjaga anti angka karangan, dan § Temuan gateway soal batas 30 detik — semuanya
  jadi dasar ADR-0132.
- **Stack**: Go, `net/http` langsung (klien tipis hand-roll, BUKAN SDK Anthropic — divalidasi
  2026-09-28, lihat
  [[ADR - 0132 Asisten AI Tanya-Jawab Lintas Modul, Lapisan Data Bisnis per Service Bukan Terpusat]]
  §Context & §2a) ke `https://code.bharatainternasional.com/v1`
  (OpenAI-compatible, bukan format native Anthropic), model dipatok literal `cc/claude-*` +
  MongoDB untuk riwayat percakapan.
  ✅ **Tool/function-calling terbukti didukung** endpoint ini (probe 2026-09-28: `tool_calls` +
  `finish_reason:"tool_calls"` kembali benar untuk skema tool sederhana). Overhead terukur ~2.332
  prompt token per giliran dengan satu tool. Router bisa membalas 401 OAuth-expired transien
  (pulih ~2 menit) — klien wajib retry sekali untuk kelas galat ini.
- **Path di repo**: `bip-erp/services/assistant/` — `internal/aiclient/` dan `cmd/probe/` (T1);
  `main.go` + `main_test.go` + `Dockerfile` (T2, mengikuti pola `services/.template` tanpa Mongo).
- **Port & deploy**: `ASSISTANT_SERVICE_PORT=6991`, container `Assistant-Service`
  (`docker-compose.yml`), healthcheck ber-header `BIP-Gateway-ID`. Tidak ada di `deploy.yml`,
  tetapi **DEV tetap ter-deploy otomatis oleh Harness `bip_erp_deploy_dev`** saat merge (terjadi
  2026-09-29); PROD manual. ⚠️ `.env` server wajib memuat `ASSISTANT_SERVICE_PORT`
  **sebelum** `api-gateway` di-`--force-recreate`: tanpanya `ASSISTANT_MODULE_URL` menjadi
  `http://assistant-service:` (tak kosong, jadi gateway tidak panic) dan `/api/assistant/*`
  membalas 502 tanpa petunjuk.
- **Rute**: lewat [[CORE - API Master Gateway]] seperti service lain; modul `assistant`, tanpa cache
  gateway (`noCacheRoutes`) karena jawaban berbeda per pertanyaan. Kini baru `/api/assistant/` dan
  `/api/assistant/health`. ⚠️ Cara mengantar jawabannya BELUM diputuskan karena gateway tidak meneruskan stream (lihat § Temuan gateway).
- **Keputusan yang mengikat**: [[ADR - 0058 Kapabilitas AI Digerbang Kelayakan Data, Bukan Kelayakan Teknologi]]

## Latar Belakang

Angka bisnis sudah tersedia lengkap di [[Microservices - Marketing Analytics Service]], tetapi tersebar di belasan layar. Orang yang ingin tahu satu angka harus tahu lebih dulu layar mana yang memuatnya. Asisten ini memperpendek jarak itu, dan **hanya** itu.

Yang membuatnya berbeda dari kapabilitas AI lain yang sudah ada di [[CORE - Kapabilitas AI dan Machine Learning]]: ini kapabilitas pertama yang **membaca data ERP atas nama seorang pemakai**. [[APP - Ideamills]] dan [[Sales - TikTok Sentiment Pipeline]] tidak menyentuh data ERP, dan [[Microservices - Vault MCP Service]] membaca dokumentasi, bukan angka. Karena itu pertanyaan hak akses di sini baru, dan dijawab di § Keputusan 2.

## Keputusan yang diambil saat perancangan

Empat keputusan di bawah punya alasan yang lebih dalam daripada preferensi.

### 1. Bukan LangGraph, melainkan Tool Runner

[[Sales - Veo (Gemini) Automation Layer]] memakai LangGraph, dan di sana ia tepat: alurnya bercabang, berjalan lama, dan berhenti menunggu persetujuan manusia. Terverifikasi di `ideamiils/package.json` (`@langchain/langgraph` 1.4.4, `@langchain/langgraph-checkpoint-mongodb`) dengan graf nyata di `ideamiils/automation/graph/`.

Asisten ini tidak punya satu pun sifat itu. Ia satu putaran tanya, panggil beberapa tool, jawab. Tool Runner di SDK resmi sudah menjalankan loop itu. Memakai LangGraph berarti membawa checkpointer, state machine, dan node graph yang tak satu pun fiturnya terpakai.

### 2. Tool memanggil endpoint LEWAT GATEWAY dengan JWT pemakai, bukan lewat jalur internal

Ini keputusan terpenting di dokumen ini. Ongkosnya satu lompatan HTTP ekstra. Imbalannya hak akses asisten **identik** dengan hak akses orang itu di layar, bukan mirip, karena melewati kode gerbang yang sama persis.

Terverifikasi di `shared-library/routes/gateway_request.go`: gateway **membuang seluruh namespace header `BIP-*` kiriman klien** lalu mengisinya ulang dari klaim JWT (`BIP-Employee-ID`, `BIP-System-Roles`, `BIP-Department`, `BIP-Supervised-Departments`, `BIP-Company-ID`, `BIP-Permissions`). Jadi service ini tidak bisa memperluas aksesnya sendiri sekalipun mencoba.

Alternatif memanggil `/internal/` ditolak. Vault sudah mencatat dua kali bahwa `/internal/` bukan berarti privat dan bahwa penyaringan hak akses wajib dikerjakan di service sumber ([[Microservices - Calendar Service]]). Menulis ulang aturan izin di sini akan melahirkan sumber kebenaran kedua yang pasti menyimpang.

### 3. Asisten DILARANG berhitung

Angka hanya boleh berasal dari yang sudah dihitung endpoint. Aturan pemakaian kolom yang berbahaya tetap tinggal di Go, tidak disalin ke prompt.

Alasannya spesifik dan sudah terdokumentasi di [[CORE - Kapabilitas AI dan Machine Learning]] § Aturan pemakaian kolom: `iklan_sia_sia` adalah himpunan bagian dari `ads_cost` dan tidak boleh dijumlahkan ke laba, `spend_vsa` dan `spend_gmv_max` dua basis atribusi berbeda yang tidak boleh digabung, dan pendapatan nol di tingkat video bisa berarti tidak ada datanya. Model bahasa yang diberi angka mentah akan menjumlahkannya dengan percaya diri, kegagalannya bukan galat melainkan **angka salah yang masuk akal**, dan tak ada test yang menangkapnya.

### 4. Jawaban adalah pintu, bukan tujuan

Tiap jawaban wajib membawa tautan ke layar yang menampilkan angka yang sama. Layar tetap sumber kebenaran dan tiap angka bisa diperiksa dalam satu klik. Prinsip ini disalin sadar dari [[Microservices - Calendar Service]], yang sudah memakainya untuk `deep_link`.

## Alur

```mermaid
flowchart LR
    FE["erp-frontend<br/>panel chat"]
    GW["API Gateway<br/>isi ulang header BIP-* dari JWT"]
    AS["assistant-service<br/>Tool Runner"]
    CL["Claude API"]
    MA["marketing-analytics"]

    FE -->|"POST /api/assistant/chat + JWT"| GW
    GW --> AS
    AS <-->|"tool_use / tool_result"| CL
    AS -->|"GET /api/marketing-analytics/... + JWT yang SAMA"| GW
    GW --> MA
```

⚠️ Rute akar modul didaftarkan di `app.Get("/")`, **bukan** `/assistant`, karena gateway memotong prefix `/api/<module>` sebelum meneruskan. Unit test tetap hijau bila keliru karena memanggil path lokal langsung ke Fiber.

## Permukaan tool

Satu tool per endpoint baca, sekitar delapan sampai dua belas untuk irisan pertama. Kandidatnya dari rute yang sudah ada di `services/marketing-analytics/handler_mart.go` dan tetangganya: `/beranda`, `/summary`, `/profit/shops`, `/profit/products`, `/profit/skus`, `/profit/campaigns`, `/profit/ads`, `/videos`, `/lives`, `/returns/breakdown`. Daftar finalnya **TBD**.

Semua tool `strict: true` supaya argumennya dijamin valid.

Yang sengaja **TIDAK** ada, dan alasannya bukan kehati-hatian umum:

| Tidak dibuat | Alasan |
|---|---|
| Tool bash atau perintah bebas | Harness hanya menerima string buram, sehingga tak bisa menggerbang, mengaudit, atau merender per aksi |
| Tool query bebas ke MongoDB | Membuka jalan bagi asisten menghitung sendiri, yang justru dilarang Keputusan 3 |
| Tool tulis apa pun | Irisan pertama baca-saja. Aksi menulis menuntut gerbang konfirmasi tersendiri yang belum dirancang |

## Penjaga supaya tidak lahir angka karangan

Empat-empatnya wajib, dan ketiadaannya tidak akan terlihat sebagai test merah.

1. **Tidak berhitung.** Lihat Keputusan 3.
2. **Tautan ke layar** di tiap jawaban. Lihat Keputusan 4.
3. **Umur data ikut dijawab.** [[ADR - 0058 Kapabilitas AI Digerbang Kelayakan Data, Bukan Kelayakan Teknologi]] mencatat bahwa pada 2026-08-28 job `sync-shop-performance` terakhir sukses 2026-08-20 dan `sync-live-sessions` 2026-08-19, dan kegagalannya **tidak berbunyi di layar mana pun**. Asisten yang menjawab di atas data berhenti empat hari akan terdengar sama meyakinkannya dengan yang benar. Karena itu tiap hasil tool membawa keterangan periode dan kesegaran sumbernya, dan asisten menyebutkannya.
4. **Tidak tahu adalah jawaban yang sah.** Bila tak ada tool yang memegang angkanya, asisten menjawab tidak tahu dan menunjuk layarnya, bukan menaksir.

## Gerbang ADR 0058

[[ADR - 0058 Kapabilitas AI Digerbang Kelayakan Data, Bukan Kelayakan Teknologi]] § 1 memasang tiga syarat. Dua yang pertama mengikat keras kapabilitas **prediktif** karena hanya yang prediktif menuntut label historis; asisten ini **generatif** dan tidak menaksir apa pun.

Yang tetap mengikat penuh adalah syarat ketiga: **ada keputusan yang benar-benar berubah, dan ada orang yang mengambilnya.** Belum dijawab dengan angka. Sampai terjawab, dokumen ini konsep.

⚠️ § 2 ADR yang sama menyatakan model menumpang service pemilik data dan tidak ada service AI terpisah. Asisten ini **service terpisah**, dan itu perlu dicatat terus terang. Alasan mengapa tidak dianggap melanggar: § 2 mengatur tempat **model** supaya tidak terpisah dari data yang dibacanya, sedangkan service ini tidak memuat model dan tidak membaca database mana pun. Ia pemanggil endpoint HTTP dan sifatnya memang lintas modul. **Menyelesaikan ketegangan ini menuntut ADR baru, bukan tafsir di dokumen ini.**

## Temuan gateway yang mengikat rancangan

Diukur langsung dari `shared-library/routes/gateway_request.go` pada 2026-08-29, dan keduanya membatalkan bentuk pengantaran jawaban yang paling wajar.

| Temuan | Baris | Akibat |
|---|---|---|
| Respons non-biner dibaca penuh ke memori (`io.ReadAll` lalu `c.Send`) | 157-158 | `text/event-stream` **tidak** ada di daftar biner, jadi SSE ditahan sampai selesai. Jawaban tidak mengalir, layar diam lalu tiba-tiba penuh |
| `http.Client{Timeout: 30 * time.Second}` | 118 | Giliran yang memanggil beberapa tool bisa melewati 30 detik, dan gateway membalas **502**, bukan pesan yang bisa dibaca |

Empat jalan keluar yang terbuka, belum dipilih:

1. Tambah `text/event-stream` ke cabang streaming dan buat timeout dapat diatur per-rute. Tempatnya benar, tetapi berkas itu **dipakai SELURUH service**, jadi ongkos salahnya jatuh ke semua orang. ⚠️ Perlu diverifikasi juga apakah cabang biner yang ada (`io.Copy` ke `BodyWriter`) benar-benar mengalir, atau fasthttp tetap menahannya sampai handler selesai; bila yang kedua, cabang itu pun bukan streaming sungguhan.
2. Tanpa stream, satu jawaban utuh sekali kirim, dengan tiap giliran dipaksa selesai di bawah 30 detik.
3. Tidak lewat gateway, berdiri sebagai host sendiri seperti [[Microservices - Vault MCP Service]]. Preseden ada, tetapi ongkosnya persis yang paling ingin dipertahankan Keputusan 2, yaitu pewarisan hak akses lewat gateway.
4. FE menarik berkala: POST memulai giliran dan membalas id, FE mengambil potongan jawabannya menyusul.

## Persona / Pengguna

| Persona | Peran & Divisi | Akses / RBAC | Device |
|---|---|---|---|
| Supervisor departemen mana pun | Tim mana pun, ber-`is_supervisor` | Mewarisi gerbang endpoint yang dipanggil; DAN gate baru "Supervisor apa pun ATAU Direktur ATAU IT" ([[ADR - 0132 Asisten AI Tanya-Jawab Lintas Modul, Lapisan Data Bisnis per Service Bukan Terpusat]] §3) | Web ERP |
| Direktur | Kesekretariatan | Sama seperti di atas; otomatis lolos lewat derivasi `it:supervisor` dari jabatan. Corporate Secretary belum ditegaskan ikut atau tidak | Web ERP |
| Tim IT | IT | Sama seperti di atas, lewat `common.IsITMember`/`IsITSupervisor` | Web ERP |

⚠️ **Pengumuman INTERIM jauh lebih sempit dari tabel di atas** (erp-frontend 2026-09-28): belum
ada menu Copilot sama sekali. Yang ada strip pengumuman tipis DI ATAS HEADER seluruh halaman,
selebar kolom konten (`components/layout/banner-copilot.tsx`, dirender `Container` sebelum
`<Header/>`; tak sticky sehingga tergulir hilang, sidebar tak digeser), hanya untuk
**departemen Tech Development** — dibandingkan dengan konstanta `DIVISI_IT`, **bukan**
`system_roles.it` (peran itu juga dipegang orang HR, Kesekretariatan, dan Finance). Selalu tampil
tanpa tombol tutup, tombol "Pelajari" menuju `/copilot`, dan disembunyikan di `/copilot` sendiri.
Izin `assistant.view` tetap `tolak` di `FALLBACK` (`utils/menu-permission.ts`) sebagai penjaga,
walau tak ada menu yang memakainya: izin tak-terdaftar diloloskan untuk semua orang. Halaman
`/copilot` sendiri tidak menggerbangi apa pun karena tak memuat data (ADR 0031).
⚠️ Belum diverifikasi: `KonteksPortal.supervisedDepartments` di `components/layout/portal-menu.ts`
didokumentasikan sebagai sinyal supervisor yang benar — relevan saat menu sungguhan dibuka ke
supervisor (T3).

- **Tujuan**: mendapatkan satu angka tanpa harus tahu lebih dulu layar mana yang memuatnya.
- **Pain point**: angkanya ada, tetapi tersebar di belasan layar.
- **Aksi utama**: bertanya, membaca jawabannya, lalu mengklik tautannya untuk memeriksa sendiri di layar aslinya.

## Jadwal Tugas (🟡 diusulkan)

Keputusan dan alasannya di [[ADR - 0135 Jadwal Tugas Copilot Mengirim Pengingat, Bukan Menjalankan Tanpa Kehadiran Pemakai]]. Bagian ini menjelaskan cara kerjanya. Kode belum ada, dan **tidak bisa dikerjakan sebelum Tanya Jawab bisa menjawab**, karena tautan pengingat menunjuk ke sana.

```
buat jadwal (nama + instruksi/template + frekuensi + jam)      @ Copilot > Jadwal Tugas
        │
cron assistant-service (Asia/Jakarta) ── slot jatuh tempo? ── klaim atomik (tugas, slot) unik
        │
kirim pengingat: inbox + push, kategori baru, tautan pre-fill  ── TANPA panggilan AI / data
        │
pemakai klik ── Tanya Jawab terbuka berisi instruksi ── jalan dengan JWT HIDUP miliknya
        │                                                     (gate ADR-0132 §3 dinilai ulang)
riwayat: kapan terkirim, kapan dibuka
```

- **Tidak ada eksekusi tanpa kehadiran pemakai.** Itu satu-satunya alasan fitur ini tak butuh mekanisme identitas baru: cron di kode hari ini memanggil lewat `InternalRequest(nil, …)` tanpa header RBAC apa pun, dan perhitungan izin efektif cuma hidup privat di titik penerbitan JWT employee-service (rincian di ADR-0135 § Context).
- **Isi tugas**: nama, instruksi atau template Copilot, frekuensi (harian, hari kerja, mingguan+hari, bulanan+tanggal) + jam. Tanpa mode izin, pilihan model, atau project.
- **Biaya AI nol sampai pemakai membuka tautan**; jadwal yang diabaikan tak memakan token.
- ⚠️ **Deploy**: kategori inbox baru → `notification-service` naik LEBIH DULU, baru `assistant-service` (lihat [[Microservices - Notification Service]]).
- **TBD**: nama kategori inbox, batas jumlah tugas per orang dan interval minimum (angka PRD claude.ai tak dipakai), serta apakah pengingat berikutnya ditahan bila yang sebelumnya belum dibuka.

## Di luar lingkup

- **Menghitung, menaksir, dan meramal.** Seluruhnya. Yang prediktif tunduk pada gerbang [[ADR - 0058 Kapabilitas AI Digerbang Kelayakan Data, Bukan Kelayakan Teknologi]] dan bukan pekerjaan service ini.
- **Aksi menulis.** Irisan pertama baca-saja.
- **Otomasi komentar di media sosial (buzzer).** Dibahas 2026-08-29 dan **ditolak**, dicatat di sini supaya tidak diusulkan berulang. Komentar otomatis yang dirancang agar terbaca seperti datang dari orang sungguhan menipu pembacanya, dan melanggar aturan platform. Taruhannya bukan kecil: omzet Rp 40,44 miliar dalam 146 hari yang diukur ADR 0058 mengalir lewat toko-toko yang akan kena sanksinya. **Yang sah dan tetap terbuka**: triase komentar masuk, draf balasan yang dikirim setelah ditinjau orang, dan balasan otomatis sebagai akun brand secara terbuka untuk pertanyaan berulang. Pembedanya satu, yaitu apakah identitas yang bicara disamarkan.
- ~~**Modul selain marketing analytics.** Irisan pertama saja; perluasan diputuskan setelah irisan pertama terbukti hidup.~~ **Diputuskan berbeda 2026-09-28** oleh [[ADR - 0132 Asisten AI Tanya-Jawab Lintas Modul, Lapisan Data Bisnis per Service Bukan Terpusat]]: cakupan lintas modul sejak awal (beberapa modul percontohan sekaligus, bukan satu-satu bergantian menunggu bukti).

## Belum Diputuskan (TBD)

- **Cara mengantar jawaban.** Empat pilihan di § Temuan gateway, belum dipilih. Ini penghalang pertama, bukan detail.
- **Daftar tool final** beserta bentuk argumen dan bentuk hasilnya.
- ~~**Kunci RBAC** yang menentukan siapa boleh membuka asistennya.~~ **Ditegaskan 2026-09-28** oleh [[ADR - 0132 Asisten AI Tanya-Jawab Lintas Modul, Lapisan Data Bisnis per Service Bukan Terpusat]] §3: Supervisor departemen mana pun ATAU Direktur ATAU IT. Yang masih TBD: apakah Corporate Secretary ikut termasuk.
- **Penyimpanan riwayat percakapan**: koleksi, masa simpan, dan apakah isinya boleh dibaca siapa pun selain penanyanya.
- **Model dan ongkos.** Probe 2026-09-28 memakai `cc/claude-sonnet-4-6` (bukan opus) — terbukti mendukung tool-calling, 2.332 prompt token untuk satu tool sederhana. Biaya rupiah per pertanyaan lintas modul sungguhan (lebih banyak tool) **masih belum diukur** — lihat T12 di [[ANALISA - Asisten AI Lintas Modul]]. Batas pemakaian per orang per hari juga belum ada.
- **Prompt caching**: daftar tool dan system prompt yang tetap seharusnya di-cache, penempatan breakpoint-nya belum dirancang.
- ~~**Penyimpanan kunci API Anthropic** dan siapa yang memegangnya.~~ **Sebagian terjawab 2026-09-28**: `AI_BASE_URL`/`AI_API_KEY` sudah ada sebagai env var di SEMUA container prod (termasuk container MongoDB — kemungkinan dari blok/anchor compose bersama yang terlalu luas, layak ditinjau terpisah, di luar cakupan dok ini) lewat `~/apps/bip-erp/.env` di server. Siapa yang mengelola rotasi/akses kunci ini masih belum jelas.
- ~~**Seluruh sisi frontend**~~ **Sebagian terjawab 2026-09-28**: pengumuman lewat banner
  (bukan menu) dengan kilau beranimasi (keyframe `copilot-kilau`, garis putih transparan supaya
  tak jadi bayangan di tema gelap, mati untuk `prefers-reduced-motion`); halaman placeholder
  `/copilot` + kunci i18n `copilot.*` dan `copilot.banner.*` di `id`/`en`
  ([[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]]). Yang masih TBD: letak menu Copilot
  sungguhan saat fiturnya hidup, panel chat, render tabel/chart jawaban, dan sub-menu (Tanya
  Jawab, Jadwal Tugas).
- **Irisan dan gerbang verifikasinya.** Belum disusun.
- ~~**ADR** yang menyelesaikan ketegangan dengan ADR 0058 § 2.~~ **Ditulis 2026-09-28**: [[ADR - 0132 Asisten AI Tanya-Jawab Lintas Modul, Lapisan Data Bisnis per Service Bukan Terpusat]] §2 — asisten lintas modul tetap jadi service terpisah, karena tidak ada satu service pemilik untuk semua modul.

## Dependensi & Integrasi

| Bergantung pada | Untuk apa | Bila mati |
|---|---|---|
| [[CORE - API Master Gateway]] | Jalur masuk, dan jalur keluar tool ke endpoint data | Asisten tak bisa dipanggil maupun memanggil |
| [[Microservices - Marketing Analytics Service]] | Seluruh angka yang dijawab | Asisten wajib menjawab tidak tahu, bukan menaksir |
| Claude API (Anthropic) | Model bahasa | Fitur padam; kegagalannya wajib berbunyi, bukan diam |
| [[CORE - SSO Flow]] | JWT yang diwarisi tool | Tak ada identitas, tak ada jawaban |

**Tidak** bergantung pada: notification-service, calendar-service, dan database mana pun milik service lain.

## Dokumen Terkait

- [[ADR - 0132 Asisten AI Tanya-Jawab Lintas Modul, Lapisan Data Bisnis per Service Bukan Terpusat]], keputusan yang menggantikan cakupan & RBAC dokumen ini
- [[CORE - Kapabilitas AI dan Machine Learning]], peta seluruh kapabilitas AI dan aturan pemakaian kolomnya
- [[ADR - 0058 Kapabilitas AI Digerbang Kelayakan Data, Bukan Kelayakan Teknologi]], gerbang yang mengikat
- [[Microservices - Marketing Analytics Service]], pemilik seluruh angka yang dijawab
- [[API - Marketing Analytics Service]], endpoint yang jadi tool
- [[Microservices - Vault MCP Service]], preseden akses Claude ke data internal, dan preseden tidak lewat gateway
- [[Sales - Veo (Gemini) Automation Layer]], kapabilitas yang memakai LangGraph dan kenapa di sini tidak
- [[APP - Web ERP]], tempat panel chat berdiri
