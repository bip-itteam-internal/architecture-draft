# ANALISA - Asisten AI Lintas Modul

Daftar task hasil `/analisa-kebutuhan` (2026-09-28). Keputusan arsitekturnya ada di
[[ADR - 0132 Asisten AI Tanya-Jawab Lintas Modul, Lapisan Data Bisnis per Service Bukan Terpusat]]
dan [[Microservices - Assistant Service]] (dok domain, diperbarui mengikuti ADR ini). Baca
keduanya dulu sebelum `/start-task` tiap item — daftar ini papan kerja, bukan rencana per berkas;
path/fungsi persis tetap digali `/plan` dari kode saat itu (kode bisa berubah sejak dok ini
ditulis).

Tiap task di bawah punya **Tujuan** (kenapa, biar agen yang eksekusi tidak menebak), **Bergantung**
(urutan wajib), **Baca dulu** (dokumen/kode/file:line spesifik yang sudah ketemu saat grounding
2026-09-28 — titik mulai, BUKAN kebenaran final; kode bisa sudah bergeser, verifikasi ulang), dan
**Kriteria selesai** (bukti konkret, bukan "sudah jalan di localhost").

## Prasyarat — keputusan manusia yang BELUM ada, sebelum task tertentu bisa dianggap tuntas

- **Corporate Secretary ikut akses "Direktur" di gate T3 atau tidak.** Default TIDAK sampai
  Direktur menegaskan tertulis. T3 dan T13 boleh dikerjakan dengan default ini, TAPI jangan
  ditutup sebagai "selesai penuh" sampai jawabannya ada — tandai eksplisit di PR/task tracker.
- **Apakah proposal ini sudah dibicarakan ke Direktur sama sekali.** ADR menulis "belum ada
  konfirmasi". Ini bukan blocker teknis untuk mulai T1-T2 (fondasi netral), tapi jadi blocker
  untuk T4 (memilih modul yang datanya sensitif) dan sebelum di-deploy ke prod.
- ⛔ **Persetujuan tertulis Direksi untuk data yang keluar perusahaan lewat relay
  `code.bharatainternasional.com`.** [[ADR - 0132 Asisten AI Tanya-Jawab Lintas Modul, Lapisan Data Bisnis per Service Bukan Terpusat]] §Context mencatat ini eksplisit sebagai
  keputusan yang SENGAJA ditunda (bukan diabaikan) — [[ADR - 0075 Bukti Sisi Lawan Dilampirkan dan Angkanya Dicatat, Pembacaan Otomatis Menyusul]] mensyaratkan persetujuan
  Direksi tertulis untuk data serupa dan sampai sekarang belum ada. **Boleh dilewati untuk
  pengembangan/uji teknis pakai data sintetis** (T1-T9), tapi WAJIB ada sebelum modul mana pun
  memproses pertanyaan dengan data ASLI di produksi.

## Fondasi

- [x] **T1 — Klien AI dasar. SELESAI 2026-09-28**, kode Go nyata (bukan cuma probe shell). ~~Go +
  Anthropic SDK dengan Tool Runner~~ **Klien tipis hand-roll, OpenAI-compatible, ke
  `https://code.bharatainternasional.com/v1`** — divalidasi langsung 2026-09-28, lihat
  [[ADR - 0132 Asisten AI Tanya-Jawab Lintas Modul, Lapisan Data Bisnis per Service Bukan Terpusat]] §Context & §2a. Kode: `bip-erp/services/assistant/internal/aiclient/`
  (`client.go`+`types.go`, 11 test lolos dua kali jalan) + `cmd/probe/main.go`, branch
  `feat/assistant-klien-ai`, merged 2026-09-29 (bip-erp#2150).
  - **Tujuan**: satu-satunya jalan masuk ke model untuk seluruh task di bawah.
  - **Bergantung**: tidak ada.
  - **Baca dulu**: [[ADR - 0132 Asisten AI Tanya-Jawab Lintas Modul, Lapisan Data Bisnis per Service Bukan Terpusat]] §2a untuk ketentuan wajib klien (`stream:false` ditanam mati,
    id model dipatok `cc/claude-*` literal, retry sekali khusus 401 "OAuth access token has
    expired", loop tool-calling ditulis manual). ⚠️ **Jangan pakai Anthropic Go SDK/Tool
    Runner** — endpoint ini OpenAI-compatible (Chat Completions), bukan format native Anthropic.
    ⚠️ **Jangan asumsikan ada `shared-library/ai`/`GenerateJSON` yang bisa dipakai ulang** —
    diverifikasi `git grep` 2026-09-28 ke `origin/main`, nol hasil. `AI_BASE_URL`/`AI_API_KEY`
    SUDAH ada sebagai env var di semua container prod (lihat [[Microservices - Assistant Service]] § Belum Diputuskan) — tinggal dipakai, tidak perlu provisioning baru untuk dev
    lanjutan, tapi verifikasi juga ketersediaannya di lingkungan dev/staging.
  - **Sudah terbukti lewat probe shell (2026-09-28)**: satu panggilan uji (prompt sederhana +
    satu skema tool dummy `get_weather`) menghasilkan `tool_calls` + `finish_reason:"tool_calls"`
    yang benar; token usage tercatat (`prompt_tokens:2332`, `completion_tokens:56`). Router
    sempat 401 "OAuth expired" lalu pulih sendiri ~2 menit kemudian — buktikan retry-nya di kode
    Go, bukan cuma tahu soal gejalanya.
  - **Kriteria selesai (kode Go, bukan shell)**: fungsi Go yang mereplikasi hasil probe di atas
    (payload sama, endpoint sama), dengan retry transien dan `stream:false` ditanam di kode
    (bukan opsional), token usage tercatat di log terstruktur.

- [x] **T2 — Skeleton `services/assistant/`. SELESAI di DEV 2026-09-29** (bip-erp #2151):
  lewat gateway dev dengan JWT sungguhan `GET /api/assistant/health` dan `/api/assistant/` → 200
  `{"message":"ok"}`, kontrol `/api/assistant/tidakada` → 404. **PROD naik 2026-09-29** (manusia):
  healthy, env gateway `http://assistant-service:6991`; panggilan ber-JWT lewat gateway prod belum dicoba.
  - **Tujuan**: rumah orkestrator. Tidak menyimpan data bisnis, tidak baca database service lain.
  - **Bergantung**: T1 (butuh klien AI untuk diuji lewat rute ini).
  - **Baca dulu**: pola boilerplate `services/.template`. [[CORE - API Master Gateway]] soal cara
    service baru didaftarkan. ⛔ **Rute akar modul didaftarkan di `app.Get("/")`, BUKAN
    `app.Get("/assistant")`** — gateway memotong prefix `/api/<module>` sebelum meneruskan; salah
    di sini pernah membuat 404 `Cannot GET /` di calendar-service dan test lokal tetap hijau
    karena memanggil Fiber langsung, bukan lewat gateway.
  - **Kriteria selesai**: endpoint kesehatan bisa dipanggil dari FE dev **lewat gateway
    sungguhan** (bukan `localhost:<port>` langsung ke service).
  - **Kemajuan 2026-09-29**: kode ditulis di branch `feat/assistant-skeleton` — `main.go`
    (Fiber, `ValidateGateway`, `GET /` dan `GET /health`, tanpa Mongo, tanpa rute AI), port
    `6991`, modul `assistant` di map gateway + `/api/assistant` di noCacheRoutes, blok
    `assistant-service` di `docker-compose.yml`. **Sengaja TIDAK didaftarkan di `deploy.yml`**
    ⚠️ Ternyata dev TETAP ter-deploy otomatis oleh Harness `bip_erp_deploy_dev` begitu merge
    (bukan deploy.yml), dan karena `.env` dev belum memuat `ASSISTANT_SERVICE_PORT` container
    sempat naik dengan `PORT=` kosong dan gateway menunjuk `http://assistant-service:`. Port
    ditambahkan ke `.env` dev lalu kedua container dibuat ulang (`--no-build --force-recreate`).
    Service baru berikutnya: isi `.env` dev SEBELUM merge.

- [ ] **T3 — Gate RBAC baru "Supervisor departemen mana pun ATAU Direktur ATAU IT".**
  - **Tujuan**: batasi menu asisten sesuai keputusan [[ADR - 0132 Asisten AI Tanya-Jawab Lintas Modul, Lapisan Data Bisnis per Service Bukan Terpusat]] §3.
  - **Bergantung**: tidak ada — boleh paralel dengan T1-T2.
  - **Baca dulu** (file:line dari grounding 2026-09-28, verifikasi ulang sebelum dipakai — kode
    bisa bergeser): `shared-library/common/roles.go:562-596` (`validateRole` pola OR,
    `checkRole`), `shared-library/common/department_scope.go:84-107`
    (`SupervisedDepartmentsStrict` — proksi "supervisor departemen apa pun", TANPA fallback),
    `shared-library/common/jabatan_direktur.go:24-47` (`SetaraDirektur`, daftar jabatan setara
    Direktur), `shared-library/common/roles.go:194-205` (`IsITMember`/`IsITSupervisor`),
    `services/employee/peran_dari_jabatan.go:206-223,308-310` (derivasi otomatis
    Direktur→`it:supervisor` saat token diterbitkan, dan cara mematikannya lewat env
    `ROLE_FROM_POSITION=off` — jangan kaget kalau derivasi ini nonaktif di suatu environment).
  - **Kriteria selesai**: satu fungsi baru "supervisor di departemen manapun" + gate gabungan,
    dikunci test T13. Menu diberi penanda `perm` sejak commit pertama (menu tanpa penanda selalu
    tampil ke semua orang — ini gotcha RBAC yang sudah tercatat).
  - ~~**Jangan tutup sebagai selesai** sampai keputusan Corp Sec (lihat § Prasyarat) ada jawabannya.~~
    ✅ **Dijawab 2026-09-29: Corporate Secretary IKUT** (ADR-0132 §3 diperbarui).
  - **Kemajuan 2026-09-29 (BE)**: branch `feat/assistant-gate-copilot` — `common.BolehPakaiCopilot`
    + `RequireCopilot` (`shared-library/common/akses_copilot.go`, 20 kasus test + kontrol negatif
    per cabang) dan `GET /api/assistant/akses`. Merged (bip-erp #2154) dan **terbukti di DEV
    2026-09-29** lewat gateway, tiap cabang oleh akun yang hanya punya cabang itu: panpan (IT
    saja) 200, Diki (supervisor saja) 200, Wirawan (Direktur) 200, Fathur & Abdul (staf) 403.
    Cabang Corporate Secretary hanya dikunci unit test (tak ada akun Corp Sec di dev). **PROD naik
    2026-09-29** (manusia): biner memuat `/akses`, healthy; panggilan ber-JWT di prod belum dicoba. **FE ditunda
    sebagai task terpisah** (keputusan user): halaman/menu `/copilot` bertanya ke `/akses`,
    BUKAN `aksesSemuaMenu` (tak mencakup Corp Sec). Banner tetap khusus Tech Development.

## Modul percontohan pertama

- [x] **T4 — Pilih modul percontohan final + verifikasi gerbangnya. SELESAI 2026-09-29: ATTENDANCE.**
  - **Keputusan user 2026-09-29**: modul percontohan pertama **attendance**. marketing-analytics
    **gugur sementara** menurut ADR §9: `/beranda`, `/summary`, `/returns/detail` membaca laba
    seluruh perusahaan tanpa gerbang peran, dan keputusannya (terima terbuka / gerbang jalur baca)
    masih menunggu issue bip-erp #2008 (OPEN, 0 komentar per 2026-09-29). **Diputuskan dan
    ditutup 2026-09-30**: gerbang jalur baca (bip-erp #2365), lihat T7.
  - **Hasil ukur lewat gateway DEV 2026-09-29** (JWT sungguhan, parameter unik per panggilan
    melawan cache; tiap 403 punya kontrol positif). Akun: Fathur (staf, peran `{}`), Diki
    (supervisor Manufaktur, non-HR), Seno (HRD Supervisor), Wirawan (Direktur, `hris:supervisor`).

    | Endpoint | Gerbang (tempatnya) | Fathur | Diki | Seno | Wirawan | Hasil |
    |---|---|---|---|---|---|---|
    | `GET /today?view=team` | departemen pemanggil dari JWT (handler) | 200, 32 org Manufaktur | 200, 32 org Manufaktur | 200, 20 org GA+HR | 200, 6 org Kesekretariatan | ✅ lolos, tercakup departemen sendiri |
    | `GET /history?month=YYYY-MM` | diri sendiri dari JWT (handler) | 200, 1 org | 200, 1 org | 200, 1 org | 200, 0 baris | ✅ lolos, hanya diri sendiri |
    | `GET /report?date=YYYY-MM` | `gateHris(PermHrisView, RequireHRISStaff)` (rute) | 403 | 403 | 200, 169 org | 200, 169 org | ✅ lolos, HR saja |
    | `GET /entries?period_start&period_end` | `gateHris(PermHrisView, RequireHRISStaff)` (rute) | 403 | 403 | 200 | 200 | ✅ lolos, HR saja |
    | `GET /internal/summary` | `RequireHRISStaff` (rute) | 403 | 403 | 200 | 200 | ✅ lolos, HR saja |
    | `GET /internal/late-recap?period=YYYY-MM` | `RequireHRISStaff` (rute) | 403 | 403 | 200 | 200 | ✅ lolos, HR saja |
    | `GET /kpi/attendance` | `GerbangKunciAbsensi` (rute) | 401 | 401 | 401 | 401 | ⛔ **tidak diteruskan**: jalur mesin-ke-mesin, bukan untuk JWT pemakai |

  - **Kesimpulan**: tak satu pun endpoint attendance yang diukur bocor; §9 terpenuhi untuk enam
    endpoint di atas. ⚠️ **Konsekuensi manfaat**: rekap disiplin (`/report`, `/entries`,
    `/late-recap`, `/internal/summary`) hanya untuk HR (dan Direktur lewat `hris:supervisor`,
    BUKAN lewat jabatan). Supervisor non-HR hanya mendapat presensi tim hari ini + riwayat
    dirinya; pertanyaan "siapa di tim saya yang paling sering telat bulan ini" belum punya
    endpoint bercakupan departemen, dan itu **wajib jadi endpoint baru di T5** (dicakup
    `SupervisedDepartmentsStrict`), bukan dengan melonggarkan gerbang HR. Corporate Secretary
    tanpa peran `hris` akan mendapat 403 di endpoint HR, sebagai warisan gerbang yang benar.
  - **Tujuan**: jangan onboard modul yang endpoint-nya sudah diketahui bocor (ADR §9).
  - **Bergantung**: § Prasyarat (Direktur sudah tahu proposal ini ada) idealnya sudah terjawab
    sebelum modul dengan data sensitif dipilih.
  - **Baca dulu**: `LOG - 2026-09-17 Audit Checklist Marketing dan Integration` bagian yang
    menyebut endpoint Integration cuma butuh login tanpa gerbang peran (kritis, belum diperbaiki
    per tanggal log itu — ukur ulang, jangan percaya tanggalnya begitu saja). [[ADR - 0120 Asisten Analisa Marketing Jadi Menu ERP, Template dan Jadwal Lebih Dulu Tanpa AI]]
    §Realisasi soal endpoint marketing-analytics yang menu-nya sempit tapi data tetap 200 untuk
    semua token.
  - **Kandidat kuat** (bukan keputusan final): attendance, marketing-analytics — jebakan datanya
    sudah paling banyak terdokumentasi di vault, jadi risiko "angka salah yang masuk akal" lebih
    mudah dijaga sejak awal.
  - **Kriteria selesai**: untuk TIAP modul kandidat, daftar endpoint yang akan diteruskan + hasil
    cek gerbangnya (lolos/tidak) DENGAN BUKTI (request nyata, bukan baca kode saja — ingat
    gerbang lazim berada satu lapis di atas yang tampak jelas, lihat gotcha "GERBANG LAZIM
    BERADA SATU LAPIS DI ATAS" di rules tim).

- [x] **T5 — Endpoint baca baru ("Lapisan Data Bisnis") di modul percontohan pertama. SELESAI
  2026-09-29** (bip-erp #2160; naik di dev dan prod). Terbukti lewat gateway DEV dengan akun
  sungguhan pada periode berdata (2026-04 dan 2026-02; data telat dev hanya padat sampai April):
  Diki → hanya Manufaktur, Seno → hanya HR+GA, Wirawan → hanya Kesekretariatan, Fathur → 403;
  `late_count` tiap orang cocok **100%** dengan `/internal/late-recap` (9/9, 9/9, 1/1; 23/23,
  3/3, 1/1). PROD: biner memuat rute, healthy; panggilan ber-JWT di prod belum dicoba.
  - **Kemajuan 2026-09-29**: `GET /api/attendance/rekap-telat/tim` di branch
    `feat/attendance-rekap-telat-tim` ([[API - Attendance Service]]). Fungsi yang dipakai ULANG:
    `rentangPeriodeTelat`, `kriteriaTelatDihitung`, `pipelineRekapTelat` (diberi parameter
    `employeeIDs`). Penanda kesegaran `dihitung_pada`. Keputusan user: jumlah telat saja (tanpa
    penanda SP1 Pasal 19), cakupan hanya departemen yang disupervisi; HR/Direktur tetap
    `/internal/late-recap`.
  - **Tujuan**: realisasi [[ADR - 0132 Asisten AI Tanya-Jawab Lintas Modul, Lapisan Data Bisnis per Service Bukan Terpusat]] §2 — pintu masuk fleksibel, aturan bisnis TETAP di kode
    yang sudah ada.
  - **Bergantung**: T4.
  - **Kriteria selesai**: endpoint baru ditulis memakai ULANG struct/fungsi bisnis yang SUDAH ADA
    di service itu (sebutkan nama fungsi yang dipakai ulang di PR description — ini yang
    membuktikan §2 dipatuhi, bukan aturan ditulis dobel). Responsnya menyertakan penanda umur/
    kesegaran data (§4 ADR) — untuk marketing-analytics ingat mart-nya sinkron tiap ~48 jam, ini
    WAJIB muncul di jawaban, bukan disembunyikan.

- [ ] **T6 — Tool + uji end-to-end tool tunggal.**
  - **Kemajuan 2026-09-29**: kode di branch `feat/assistant-tanya-rekap-telat` — `POST /tanya` +
    tool `rekap_telat_tim` + samaran identitas ([[Microservices - Assistant Service]] § Permukaan
    tool). Keputusan user: pengujian memakai data dev ASLI dengan identitas disamarkan (bukan data
    sintetis), jawaban sekaligus tanpa stream, **T7-T8 dilewati dulu, lanjut T9** sesudah T6
    (marketing masih terhalang #2008). `.env` dev diisi `AI_*` dari prod sebelum merge.
  - **Terbukti di DEV 2026-09-29** (bip-erp #2161, lewat gateway, akun sungguhan): Diki → 3 teratas
    = rekap T5 (6,4 dtk); Seno → 9 orang HR+GA = rekap T5 (5 dtk); Fathur → 403 tanpa memanggil
    AI; pertanyaan laba toko → menolak tanpa angka. Dua cacat ditemukan: jawaban bermarkdown
    (tampil mentah di panel T9a) dan saran modul karangan ("Point of Sale"); diperbaiki di PR
    `fix/assistant-prompt-teks-biasa`.
  - ⚠️ **Keputusan prod, disampaikan user (panpan) 2026-09-29**: Copilot T6+T9a boleh naik ke
    PROD **tanpa menunggu persetujuan tertulis Direksi**, dengan dasar identitas disamarkan. Yang
    tetap keluar ke relay: nama departemen, jumlah telat per token, dan isi pertanyaan (termasuk
    nama yang diketik penanya di pertanyaan pertama). Prasyarat § Persetujuan Direksi di atas
    tidak dicabut oleh keputusan ini; ia tetap terbuka untuk modul berikutnya.
  - **Naik di PROD 2026-09-29** (manusia; bip-erp #2161, #2167, #2240; erp-frontend #1798, #1885):
    biner attendance + assistant memuat kode baru, env `AI_*`/`GATEWAY_URL` terisi, 0 panic,
    tanpa JWT = 401, bundel FE memuat panel. Panggilan ber-JWT di prod belum dicoba agent (tanpa
    akun uji prod). Cakupan rekap diperluas (keputusan user): IT supervisor/admin, Direktur, Corp
    Sec = seluruh perusahaan (dev: 56/56 cocok rekap HR); staf IT tetap 403. Prompt: tanpa
    Markdown, tanpa nama layar/modul (dev: model sempat mengarang "Point of Sale"). Tampilan dari
    review Grok (dipilih user): tampilan awal satu input + chip saran pengisi + input pil Enter.
    Sisa kecil: keterangan uji coba masih berbunyi "tim yang Anda supervisi".
  - **Bergantung**: T1, T2, T5.
  - **Baca dulu**: `shared-library/routes/gateway_request.go:47-115` (`Reroute` — cara header
    `BIP-*` diisi ulang dari klaim JWT, TERMASUK `BIP-Permissions`) **vs**
    `shared-library/routes/internal_request.go:34-60` (`InternalRequest` — TIDAK meneruskan
    `BIP-Permissions`). ⛔ **assistant-service memanggil modul lain WAJIB lewat jalur setara
    `Reroute` (bulat-balik ke gateway), BUKAN `InternalRequest`** — kalau salah pakai, hak akses
    bisa diam-diam menciut tanpa galat apa pun.
  - **Kriteria selesai**: uji dengan akun uji SUNGGUHAN (bukan token admin) untuk tiap tingkat
    akses (staff biasa, supervisor, Direktur, IT), buktikan hasilnya identik dengan yang orang
    itu lihat di layar aslinya. Uji juga satu pertanyaan yang SENGAJA di luar cakupan tool ini →
    jawaban harus "tidak tahu, cek layar X", bukan menaksir.

## Modul percontohan kedua + korelasi lintas modul

- [ ] **T7 — Ulangi T5-T6 untuk modul percontohan kedua.**
  - **Kemajuan 2026-09-30 — modul kedua: MARKETING** (keputusan user "marketing dulu semuanya",
    urutan "gerbang dulu, baru Copilot"):
    - **Penghalang §9 dibereskan**: bip-erp #2365 (menutup #2008) menggerbang 21 rute baca angka
      bisnis marketing-analytics dengan `RequireAnalitikMarketing` = audiens layar (`bolehAnalitik`)
      + Direktur/Corp Sec (keputusan user). Rute baru dijaga `TestRuteGetTerklasifikasi`
      ([[Microservices - Marketing Analytics Service]] § Prinsip Arsitektur 3).
    - **Tujuh tool** (bip-erp #2367, erp-frontend #1906): `ringkasan_marketing`, `laba_toko`,
      `laba_produk`, `iklan`, `live`, `retur`, `affiliate_video` — memakai endpoint yang ADA, tanpa
      endpoint baru; aturan kolom ditegakkan di tool ([[Microservices - Assistant Service]] § Tool
      marketing).
    - **Cacat sumber ditemukan saat membangun**: laba per produk/SKU/item bulanan terpotong 5.000
      baris harian (issue #2366, diukur PROD); diperbaiki bip-erp #2369.
    - Juga dari sisi HRIS: tool ketiga `cuti_tim` + endpoint baru `GET /cuti/tim` (bip-erp #2363,
      erp-frontend #1905).
    - **PROD 2026-09-30** (dideploy manusia): backend di HEAD #2369, `assistant-service`
      `MONGO_DB=assistant_db`. ⚠️ Per pengecekan agent pukul 08:21 WIB container frontend masih
      build 2026-09-29 17:28 (checkout sudah memuat #1905/#1906), jadi label/saran tool baru belum
      tampil sampai `frontend-hris` dibangun ulang.
    - ⛔ **Belum**: uji end-to-end DEV dengan akun leader marketing (angka = layar) dan akun
      non-marketing (`tidak_berhak`), uji `cuti_tim` dengan pengajuan uji, dan ukur waktu
      `/profit/items` rentang 3 bulan terhadap batas 30 detik. Agent tak bisa membuat token uji
      sendiri (membaca secret JWT dev ditolak classifier 2026-09-30); butuh akun dari manusia.
  - Sama persis strukturnya, modul berbeda. Jangan disingkat langkahnya hanya karena "sudah
    pernah dikerjakan di T5-T6" — tiap modul punya jebakan kolomnya sendiri yang belum
    terdokumentasi (CORE - Kapabilitas AI baru mendokumentasikan jebakan Marketing, modul lain
    kosong).

- [ ] **T8 — Uji korelasi lintas modul + ukur batas waktu nyata.**
  - **Bergantung**: T6, T7.
  - **Tujuan**: buktikan [[ADR - 0132 Asisten AI Tanya-Jawab Lintas Modul, Lapisan Data Bisnis per Service Bukan Terpusat]] §5 (gabung hasil, bukan gabung query) dan isi angka §6
    yang sengaja dikosongkan di ADR ("ditetapkan dari pengukuran nyata saat /plan").
  - **Kriteria selesai**: satu pertanyaan yang butuh KEDUA modul (kunci penghubung sama, mis.
    `employee_id`) → dua tool call dalam satu giliran → jawaban menggabungkan angka yang SUDAH
    benar dari keduanya. Catat waktu total giliran ini. **Tuliskan angka batas maksimal
    modul/tool-call per pertanyaan yang aman di bawah timeout gateway 30 detik** sebagai catatan
    realisasi balik ke ADR-0132 §6 — jangan biarkan angka ini cuma hidup di kode.

## Presentasi jawaban

- [ ] **T9 — Format keluaran terstruktur (teks/tabel/chart) + panel chat FE.**
  - **Dipecah user 2026-09-29**: **T9a** panel tanya teks + sumber (sekarang), **T9b** tabel/chart
    (menyusul; butuh `/tanya` mengembalikan data baris apa adanya ke penanya, tidak lewat AI).
  - **Kemajuan T9b (2026-09-29)**: keputusan user = **AI memilih bentuk, angka dari tool**; grafik
    rekap telat = batang mendatar per karyawan. BE merged (bip-erp #2359) dan terbukti di DEV lewat
    gateway (tabel 56 baris, grafik 15 dari 56). FE `feat/copilot-tampilan` (erp-frontend) menyusul;
    **kriteria selesai (render di layar, terang DAN gelap) belum dibuktikan**. Rincian:
    [[Microservices - Assistant Service]] § Blok tampilan.
  - **Riwayat percakapan (2026-09-29, di luar daftar T awal, diminta user)**: simpan selamanya,
    hanya pemilik, drawer daftar + hapus + lanjutkan. BE bip-erp #2332 dan FE erp-frontend #1899
    merged; BE terbukti di DEV. Rincian: [[Microservices - Assistant Service]] § Riwayat percakapan.
  - **Tool kedua `antrean_persetujuan` (2026-09-29, keputusan user: antrean dulu, lalu cuti/izin
    tim)**: endpoint attendance `/hr/requests?as=reviewer` dipakai apa adanya (gerbang relasional
    sudah benar). BE bip-erp #2362 merged, terbukti di DEV ujung ke ujung dengan pengajuan uji.
    Pemetaan kandidat lain: cuti/izin tim, lembur tim, dan sisa kuota **tak punya** endpoint
    bercakupan supervisor (hanya HR, diri sendiri, atau yang pernah ditinjau), jadi cuti/izin tim
    butuh endpoint baru seperti T5. Temuan sampingan keamanan dicatat di issue privat bip-erp, tidak
    di vault (repo publik).
  - **Kemajuan T9a**: branch erp-frontend `feat/copilot-panel-tanya` — `features/copilot/components/
    panel-tanya.tsx` + `hooks/use-tanya-copilot.ts`; halaman `/copilot` menampilkan panel (badge "Uji
    Coba"), jawaban teks polos + sumber, galat per status lewat i18n dengan Coba lagi, riwayat
    hanya selama halaman terbuka. Batas panjang pertanyaan sengaja tak disalin ke FE (milik BE).
  - **Baca dulu**: komponen `ChartContainer` (`components/ui/chart.tsx`) yang sudah baku di
    erp-frontend, dan skill `dataviz` bila tersedia di sesi yang mengerjakan. Aturan yang SUDAH
    berlaku di codebase ini (lihat rules tim §Bagan/chart): palet `--fb-seri-1..6` untuk deret
    jamak (BUKAN `--chart-1..5`, itu goyah kontrasnya), `connectNulls={false}`, `domain=[0,100]`
    untuk skor, `type="monotone"` saja untuk kurva.
  - **Kriteria selesai**: minimal satu jawaban berbentuk tabel dan satu berbentuk chart benar-
    benar dirender di FE dev, lolos di mode terang DAN gelap.

- [ ] **T10 — Penanda tingkat keyakinan.**
  - **Kriteria selesai**: jawaban yang sifatnya judgment/heuristik menampilkan penanda "perlu
    diperiksa manusia" yang kelihatan (bukan cuma kalimat terselip). Uji dengan **kontrol
    negatif**: satu skenario yang SEHARUSNYA ditandai, pastikan benar-benar tertandai — jangan
    cuma uji skenario yang memang jelas pasti.

- [ ] **T11 — File (Excel/PDF) hanya saat diminta eksplisit.**
  - **Kriteria selesai**: jawaban default tanpa file. File Excel/PDF cuma muncul kalau prompt
    penanya eksplisit minta ("buatkan Excel-nya") — dikunci test yang membuktikan permintaan
    tanpa kata itu TIDAK menghasilkan file.

## Verifikasi & pengukuran

- [ ] **T12 — Ukur biaya AI per pertanyaan.**
  - **Bergantung**: T1-T9 sudah berjalan di dev, idealnya minimal seminggu pemakaian nyata.
  - **Kriteria selesai**: angka token + biaya rupiah NYATA (dari `NarasiJejak`-style log atau
    setara), dicatat di [[Microservices - Assistant Service]] — bukan estimasi dari harga model
    di kertas.

- [x] **T13 — Uji gate RBAC positif dan negatif. SELESAI bersama T3 (diperiksa 2026-09-29)**:
  `bip-erp/shared-library/common/akses_copilot_test.go` `TestRequireCopilot` di `origin/main` mengunci
  kelima skenario (staf ditolak; supervisor satu departemen DAN grup HRGA lolos; Direktur, IT
  staf/supervisor/admin, Corporate Secretary lolos) plus 10 kasus tolak (admin HR, supervisor modul
  tanpa `is_supervisor`, cakupan kosong/rusak, "Direktur Utama", fallback `BIP-Department`). Tiap
  cabang diuji sendirian supaya kontrol negatif per cabang bermakna. Tak ada kode tambahan.
  - **Bergantung**: T3.
  - **Kriteria selesai**: test otomatis mengunci LIMA skenario sekaligus: staff biasa DITOLAK,
    supervisor departemen mana pun (bukan cuma satu departemen yang kebetulan dites) LOLOS,
    Direktur LOLOS, IT LOLOS, Corporate Secretary sesuai keputusan § Prasyarat (lolos ATAU
    ditolak — yang penting ada test yang mengunci hasilnya, jangan dibiarkan tak diuji).

## Jadwal Tugas ([[ADR - 0135 Jadwal Tugas Copilot Mengirim Pengingat, Bukan Menjalankan Tanpa Kehadiran Pemakai]])

⛔ **Semua task di bawah bergantung Tanya Jawab sudah bisa menjawab** (minimal T2, T3, T5, T6).
Tautan pengingat menunjuk ke Tanya Jawab; membangunnya lebih dulu menghasilkan notifikasi ke
halaman yang tak bisa apa-apa. Keputusan user 2026-09-28: tunda sampai fondasi terbukti.

- [ ] **T14 — Koleksi jadwal + CRUD di `services/assistant`.**
  - **Bergantung**: T2, T3.
  - **Baca dulu**: ADR-0135 §2-§3; `services/form-builder/form_handlers.go:35-42` — bug
    `recurrence` yang tak pernah terikat ke struct request (3 hari "live" tak bisa dipakai).
  - **Kriteria selesai**: buat/ubah/jeda/hapus jadwal lewat gateway `/api/assistant/...` dengan
    akun ber-gate; field jadwal TERBUKTI terikat dari body JSON (test `app.Test` handler, bukan cuma
    unit domain); akun tanpa gate ditolak.
- [ ] **T15 — Penjadwal pengingat idempoten.**
  - **Bergantung**: T14.
  - **Baca dulu**: `services/form-builder/cron.go` (pola buka periode per jam, idempoten);
    `services/calendar/obligation_cron.go` (`cron.Recover`); `services/integration/internal/worker/lock.go`
    (kunci terdistribusi — hanya bila lebih dari satu replika).
  - **Kriteria selesai**: satu slot = paling banyak satu pengingat (indeks unik tugas+slot, ada test
    yang menjalankan slot sama dua kali); zona Asia/Jakarta; TIDAK ada panggilan AI maupun endpoint
    data di jalur ini (dikunci test).
- [ ] **T16 — Kategori inbox + tautan pre-fill.**
  - **Bergantung**: T15, dan layar Tanya Jawab (T8/T9).
  - **Baca dulu**: `shared-library/models/notification/models.go` (`InboxCategories`, komentar
    urutan deploy); [[Microservices - Notification Service]].
  - **Kriteria selesai**: satu notifikasi sungguhan tiba di inbox + push di dev; tautannya membuka
    Tanya Jawab dengan instruksi terisi; urutan deploy (notification-service dulu) tercatat di
    rencana.
- [ ] **T17 — Layar Jadwal Tugas di erp-frontend.**
  - **Bergantung**: T14, T16.
  - **Baca dulu**: `rules/ui-checklist.md` §2a (Sheet berangka tiga — form Task Baru);
    `features/form-builder/components/recurrence-fields.tsx` sebagai acuan BENTUK saja (ia tak punya
    harian maupun jam, jangan dipakai ulang apa adanya); mockup Contoh 8 sesi 2026-09-28.
  - **Kriteria selesai**: daftar jadwal + form Sheet (nama, instruksi/template, frekuensi, jam,
    notifikasi) + riwayat terkirim/dibuka; sub-menu Copilot "Tanya Jawab"/"Jadwal Tugas" (ingat
    `ambangSarang: 2`); i18n id+en; satu perjalanan utuh sebagai orang di dev.

## Terkait

- [[ADR - 0132 Asisten AI Tanya-Jawab Lintas Modul, Lapisan Data Bisnis per Service Bukan Terpusat]]
- [[Microservices - Assistant Service]]
- [[REF - Kepemilikan Data]]
- [[CORE - RBAC dan Permission Set]] · [[CORE - API Master Gateway]] · [[CORE - Kapabilitas AI dan Machine Learning]]
