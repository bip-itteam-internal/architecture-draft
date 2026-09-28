# ADR - 0132 Asisten AI Tanya-Jawab Lintas Modul, Lapisan Data Bisnis per Service Bukan Terpusat

> **Status**: 🟡 **Diusulkan**, 2026-09-28, kode belum ada. Diusulkan tim IT/Tech Development — **belum ada konfirmasi eksplisit ini sudah dibicarakan ke Direktur**. Berdiri di atas grounding vault + kode langsung pada tanggal yang sama (lihat § Context untuk koreksi atas klaim vault yang ternyata tidak cocok dengan kode).

%% Status ditulis di blockquote atas, bukan bullet di ## Deskripsi, alasan sama dengan ADR 0120/0127:
## Untuk Manajemen mendorong Deskripsi melewati baris ke-15 sehingga status tak terbaca VAULT-INDEX.json. %%

## Untuk Manajemen

**Apa yang berubah di layar.** Supervisor (departemen mana pun), Direktur, dan tim IT mendapat satu
panel tanya-jawab baru di Web ERP. Mereka mengetik pertanyaan bahasa biasa tentang data operasional
— misalnya "toko mana yang belanja iklannya boros bulan ini" atau "siapa yang paling sering telat
bulan ini" — dan mendapat jawaban dalam hitungan detik, berbentuk teks, tabel, atau grafik sesuai
jenis datanya, tanpa perlu tahu dulu menu mana yang menyimpan angkanya.

**Siapa yang terdampak.** Supervisor semua departemen, Direktur, dan tim IT. Karyawan lain tidak
melihat menu ini sama sekali. Apakah Corporate Secretary ikut termasuk (ia setara Direktur untuk
persetujuan, tapi tidak otomatis dapat hak akses IT) **belum ditegaskan** — lihat §3.

**Apa yang TIDAK dijanjikan.**
- Asisten **tidak menghitung sendiri**. Ia hanya membaca angka yang sudah dihitung benar oleh
  service pemiliknya masing-masing.
- Jawaban yang sifatnya penilaian/perkiraan ditandai jelas "perlu diperiksa manusia" — tidak
  pernah disajikan seolah pasti.
- Cakupan awal **beberapa modul percontohan saja**, bukan seluruh ERP sejak hari pertama. Modul
  lain menyusul satu per satu, setelah endpoint barunya dibangun dan diverifikasi.
- **Tidak ada aksi tulis apa pun** (approve, ubah data, jalankan sesuatu) — murni baca.
- Pertanyaan yang menyentuh banyak modul sekaligus bisa gagal dijawab kalau makan waktu terlalu
  lama — ada batas teknis dari infrastruktur gateway yang sudah ada (§6), belum diperbaiki.
- Asisten mewarisi lubang keamanan endpoint yang diteruskannya apa adanya (§9) — ia tidak menutup
  celah yang sudah ada, dan beberapa celah seperti itu **sudah terbukti ada** hari ini.
- Model AI-nya dipanggil lewat relay internal yang diteruskan ke penyedia DI LUAR perusahaan.
  **Belum boleh memproses data asli sampai ada persetujuan tertulis Direksi** (§ Context) — baru
  boleh dipakai dengan data uji sintetis sampai persetujuan itu ada.

**Perkiraan besaran kerja.** Ini pekerjaan baru sama sekali — tidak ada satu baris kode pun yang
bisa dipakai ulang (klien AI, service, gate RBAC gabungan: semuanya belum ada, lihat § Context).
Realistis dihitung minggu, bukan hari, per modul percontohan: service baru + klien AI dari nol +
minimal satu endpoint baca baru per modul + panel chat di frontend + gate akses baru.

## Deskripsi

*Asisten AI di Web ERP menjawab pertanyaan bahasa natural tentang data ERP lintas modul dengan
memanggil, untuk tiap modul yang relevan, satu endpoint baca BARU yang dibangun di dalam service
pemilik datanya masing-masing — bukan satu lapisan data terpusat yang membaca banyak database
sekaligus. Panggilan mewarisi hak akses lewat JWT milik si penanya sendiri via gateway yang sudah
ada, dibatasi ke Supervisor/Direktur/IT, dan tidak pernah menghitung ulang dari data mentah.*

- **Path di repo**: `bip-erp/services/assistant/` **(baru)** — orkestrator saja, tidak menyimpan
  data bisnis apa pun; endpoint baca baru per modul percontohan di service masing-masing (path
  persis ditentukan saat `/plan` per modul); `erp-frontend/src/features/assistant/` **(baru)** —
  panel chat + render tabel/chart
- **Tanggal**: 2026-09-28

## Context

**Kebutuhan.** Supervisor, Direktur, dan IT butuh jawaban cepat atas pertanyaan data lintas modul
tanpa harus tahu dulu layar mana yang menyimpannya, dan tanpa menunggu orang lain menyusun laporan
manual — dengan syarat jawabannya tidak boleh salah dengan cara yang meyakinkan. Cara kerja hari
ini: manual, gonta-ganti layar per modul, seperti yang dicatat [[Microservices - Assistant Service]]
§Latar Belakang.

**Prior art yang hampir identik sudah ada, tapi beda cakupan.** [[Microservices - Assistant
Service]] (🟡 Konsep, 2026-08-29, 0 kode) sudah merancang pola yang sama persis — asisten yang
MERUTEKAN pertanyaan ke endpoint yang sudah menghitung, memanggil pakai JWT si penanya, dilarang
menghitung sendiri, jawaban selalu bertaut ke layar aslinya. Bedanya: dokumen itu mengarahkan
irisan pertama HANYA ke marketing-analytics, dan mencatat kunci RBAC-nya sebagai TBD. ADR ini
mengambil pola yang sama tapi dengan **cakupan lintas modul sejak awal** dan **RBAC yang
ditegaskan** (§3) — perbedaan yang disengaja, dicatat di sini sebagai keputusan baru, bukan
penerus otomatis dari dokumen itu.

⚠️ **Koreksi penting atas klaim vault, diverifikasi langsung ke kode 2026-09-28.** [[ADR - 0082
Integrasi AI lewat Klien Tipis di Shared-Library]] dan [[ADR - 0127 Laporan Asisten Analisa
Membawa Keputusan AI, Orang Menjalankan atau Menolak]] mencatat klien AI `shared-library/ai`
(`GenerateJSON`) sebagai **sudah ada dan sudah dipakai recruitment**. `git grep` menyeluruh atas
`origin/main` (HEAD `60c240fc`, dicek juga 60+ worktree lain) untuk `GenerateJSON`, `shared-library/ai`,
maupun env `AI_*` — **nol hasil di luar false-positive kata Indonesia**. Direktori `services/assistant/`
juga masih **0 kode**, konsisten dengan catatan vault. Kesimpulannya: **ini genuinely greenfield**,
bukan "pemakai ketiga" dari fondasi yang sudah berdiri — retry, kuota, cache, dan pembuatan prompt
untuk panggilan AI semuanya harus dirancang dari nol.

**Ketegangan dengan [[ADR - 0058 Kapabilitas AI Digerbang Kelayakan Data, Bukan Kelayakan
Teknologi]] §2 tidak bisa diwarisi dari ADR-0120.** §2 melarang service AI terpisah, dengan alasan
model tidak boleh terpisah dari data yang dibacanya. [[ADR - 0120 Asisten Analisa Marketing Jadi
Menu ERP, Template dan Jadwal Lebih Dulu Tanpa AI]] §Consequences menjawab ketegangan itu **untuk
kasus satu domain** (Marketing) dengan cara **tidak membuat service baru sama sekali** — model
menumpang di dalam marketing-analytics lewat klien tipis. Pola itu tidak bisa dipakai apa adanya
di sini: asisten lintas modul **secara struktural** harus memanggil banyak service pemilik data
berbeda, sehingga ia sendiri tetap harus berdiri sebagai service terpisah. Ini penyimpangan sadar
dari arah ADR-0120 untuk kasus lintas-modul, dicatat di sini sebagai keputusan ADR ini sendiri
(§2), bukan tafsir diam-diam.

**Kendala gateway, terukur langsung ke kode `shared-library/routes/gateway_request.go`
(2026-09-28).** Timeout HTTP eksplisit **30 detik** (baris 118). Tidak ada dukungan
`text/event-stream`: hanya `Content-Type` berawalan `image/`, `video/`, `audio/`, `application/pdf`,
`application/octet-stream` yang benar-benar di-stream (`io.Copy`); selain itu — **termasuk SSE** —
dibaca penuh ke memori dulu (`io.ReadAll`, baris 157) baru dikirim sekali jadi (baris 158). Jawaban
tidak bisa mengalir token-per-token lewat gateway yang sama, dan giliran yang memanggil banyak tool
berisiko lewat 30 detik lalu dibalas **502**, bukan pesan yang bisa dibaca.

**`InternalRequest` BUKAN pengganti `Reroute` untuk panggilan asisten ke service lain.**
`shared-library/routes/internal_request.go` meneruskan identitas (`EmployeeID`, `SystemRoles`,
`Department`, `SupervisedDepartments`, `CompanyID`) tapi **tidak meneruskan `BIP-Permissions`**.
Endpoint tujuan yang menggerbang pakai permission-set RBAC baru (ADR-0030), bukan `system_roles`
lama, bisa menerima hak yang lebih sempit dari hak asli si penanya bila dipanggil lewat jalur ini.

**Tidak ada gate RBAC siap pakai untuk "Supervisor departemen mana pun ATAU Direktur ATAU IT".**
`work_data.is_supervisor` dipakai untuk rantai persetujuan (routing atasan), bukan gerbang
menu/API. Tidak ada fungsi backend `IsAnySupervisor` (yang disebut di komentar `catalog_hris.go`
ternyata hidup di erp-frontend, bukan Go). Proksi terdekat yang sudah ada:
`common.SupervisedDepartmentsStrict(c)) > 0` — belum pernah dipakai sebagai gerbang tunggal.
Direktur mendapat `it:supervisor` otomatis lewat derivasi jabatan (`peran_dari_jabatan.go`), TAPI
Corporate Secretary (setara Direktur untuk persetujuan lain) **tidak** ikut derivasi itu. Pola
komposisi gate OR (`validateRole`) sudah mapan dan dipakai luas — jadi ini bukan arsitektur RBAC
baru, hanya satu predikat baru yang perlu ditulis plus satu keputusan eksplisit soal Corp Sec.

**Sebagian endpoint yang akan diteruskan asisten TERBUKTI tidak bergerbang peran hari ini.**
`LOG - 2026-09-17 Audit Checklist Marketing dan Integration` mencatat **kritis, belum
diperbaiki**: sejumlah endpoint Integration cuma butuh login, tanpa gerbang peran apa pun —
mencakup kredensial marketplace, kontrol job sinkron, data order/laba/ulasan. [[ADR - 0120]]
§Realisasi mencatat pola serupa di sebagian endpoint marketing-analytics: menu dipersempit tapi
endpoint datanya tetap balas 200 untuk siapa pun bertoken. Prinsip "asisten mewarisi RBAC lewat
JWT jadi otomatis aman" **hanya sekuat gerbang endpoint aslinya** — dan sudah ada bukti sebagian
gerbang itu belum ada.

**Klien AI: bukan Anthropic SDK/Tool Runner, tapi klien tipis OpenAI-compatible — divalidasi
langsung 2026-09-28.** [[ADR - 0082 Integrasi AI lewat Klien Tipis di Shared-Library]] dan
[[ADR - 0075 Bukti Sisi Lawan Dilampirkan dan Angkanya Dicatat, Pembacaan Otomatis Menyusul]]
sudah memprobe endpoint internal `https://code.bharatainternasional.com/v1` ("9router", menawarkan
9 model) dan menemukan bentuknya **OpenAI-compatible** (Chat Completions), BUKAN format native
Anthropic — sehingga rencana awal memakai Anthropic Go SDK/Tool Runner **tidak cocok dipakai
langsung**. Probe ulang sesi ini (2026-09-28, dari container prod — kredensial `AI_BASE_URL`/
`AI_API_KEY` ternyata sudah tersedia di SEMUA container prod lewat blok/anchor compose bersama,
termasuk container MongoDB; ini layak ditinjau terpisah, di luar cakupan ADR ini) **membuktikan
tool/function-calling DIDUKUNG**: satu panggilan uji dengan skema tool sederhana menghasilkan
`tool_calls` + `finish_reason:"tool_calls"` yang benar. Overhead terukur **2.332 prompt token**
untuk satu pesan + satu skema tool (dekat baseline ~2.030 token tanpa tools di ADR-0082). Router
sempat membalas 401 *"OAuth access token has expired... (reset after 2m)"* pada percobaan pertama
lalu pulih sendiri di percobaan kedua — **transien**, klien wajib retry sekali untuk kelas galat
ini, bukan menyerah permanen. ⛔ **Wajib memakai id model eksplisit `cc/claude-*`** (mis.
`cc/claude-sonnet-4-6`), **jangan pernah** `Claude` polos atau apa pun di bawah `token-router/` —
router bisa mendarat di penyedia lain (mis. MiniMax) tanpa peringatan bila id-nya generik
([[ADR - 0075]]).

⚠️ **Keputusan yang SENGAJA ditunda, dicatat eksplisit supaya tidak jadi asumsi diam-diam seperti
yang sudah terjadi di ADR-0127.** Endpoint ini relay ke Anthropic **di luar perusahaan** — data
yang dikirim untuk dianalisis (angka HRIS/Marketing/dll) ikut keluar gedung. [[ADR - 0075]]
mensyaratkan **persetujuan tertulis Direksi** untuk data serupa (rekening koran) dan menahan
fiturnya sampai ada; [[ADR - 0127]] mengasumsikan boleh tanpa keputusan eksplisit, dengan alasan
precedent CV pelamar. Dua ADR yang sudah ada mengambil sikap **berlawanan** soal hal yang sama.
Pemilik proposal ini (2026-09-28) memutuskan: **jalankan dulu pengembangan & probe teknis (data
uji sintetis, seperti probe di atas, tidak menyentuh isu ini), tapi persetujuan Direksi WAJIB ada
sebelum modul mana pun mengirim DATA ASLI (bukan data uji) lewat endpoint ini ke produksi.** Ini
bukan penghalang untuk T1-T9 (pengembangan/uji teknis), tapi penghalang keras untuk deploy prod
yang memproses pertanyaan sungguhan.

**Kolom yang aman dijumlah beda-beda per modul, dan baru terdokumentasi untuk Marketing.**
[[CORE - Kapabilitas AI dan Machine Learning]] §Aturan pemakaian kolom cuma memuat jebakan kolom
marketing-analytics (`iklan_sia_sia`, `spend_vsa` vs `spend_gmv_max`, retur yang sudah terpotong,
dst). Modul lain (HRIS, Finance, dll) **belum punya daftar serupa** — tiap modul baru yang
di-onboard wajib digali ulang jebakannya sendiri, tidak boleh diasumsikan aman.

## Decision

### §1 Cakupan awal: beberapa modul percontohan, bukan seluruh ERP

Mulai dari 2-3 modul percontohan (kandidat kuat: attendance dan marketing-analytics, karena
jebakan datanya sudah paling banyak terdokumentasi — daftar final diputuskan saat `/plan`). Modul
baru ditambah satu per satu setelah endpoint §2 dan RBAC §3 modul sebelumnya terbukti benar,
bukan dibangun serentak.

### §2 Lapisan Data Bisnis hidup DI DALAM service pemilik data, bukan lapisan terpusat

`services/assistant` **hanya orkestrator**: menerjemahkan prompt, memutuskan modul mana yang
relevan, memanggil endpoint modul itu, menggabungkan hasil, memformat jawaban. Ia **tidak
menyimpan aturan bisnis maupun membaca database service lain**. Tiap modul percontohan mendapat
satu endpoint baca BARU yang ditulis pakai struct/fungsi bisnis yang **sudah ada** di service itu
— realisasi "Lapisan Data Bisnis" adalah kode di service pemiliknya, bukan penulisan ulang aturan
di tempat baru. Ini konsisten dengan [[REF - Kepemilikan Data]]: "konsumsi lewat pemilik, bukan
lewat database-nya."

Panggilan assistant-service ke service lain **wajib** lewat jalur setara `Reroute` gateway (bukan
`InternalRequest`) supaya `BIP-Permissions` ikut terbawa utuh — lihat § Context soal
`InternalRequest` yang tidak meneruskannya.

### §2a Klien AI: tipis, hand-roll, OpenAI-compatible — bukan SDK Anthropic

Divalidasi 2026-09-28 (lihat § Context). `services/assistant` memanggil
`https://code.bharatainternasional.com/v1/chat/completions` langsung lewat `net/http`, TANPA
menarik SDK vendor apa pun — konsisten dengan filosofi "klien tipis" [[ADR - 0082]]. Ketentuan
wajib:
- `stream:false` ditanam mati di payload, tidak pernah jadi parameter (endpoint ini default
  `true` bila tak dikirim, dan gagalnya tidak terbaca sebagai galat — pola sama dengan ADR-0082).
- Id model dipatok literal `cc/claude-*`, tidak pernah dibaca dari input bebas.
- Retry **sekali** khusus untuk 401 ber-pesan "OAuth access token has expired" (transien,
  terbukti pulih dalam ~2 menit pada probe sesi ini) — retry TIDAK berlaku untuk 401 lain.
- Loop tool-calling ditulis manual: kirim `tools`, terima `tool_calls` dari respons, eksekusi,
  kirim hasil balik sebagai pesan `role:"tool"` di giliran berikutnya.

### §3 RBAC: gate baru "Supervisor departemen mana pun ATAU Direktur ATAU IT"

Dibangun mengikuti pola `validateRole(...)` OR yang sudah mapan (bukan arsitektur RBAC baru):
- **IT**: `common.IsITMember` / `IsITSupervisor` yang sudah ada.
- **Direktur**: derivasi role otomatis (`it:supervisor` dari jabatan "direktur") sebagai jalur
  utama, `common.SetaraDirektur` (posisi) sebagai jaga-jaga bila derivasi mati atau Master Data
  jabatan salah ketik.
- **Supervisor departemen mana pun**: predikat BARU (belum ada di kode), dasarnya
  `len(common.SupervisedDepartmentsStrict(c)) > 0`.

⛔ **Corporate Secretary TIDAK termasuk** sampai ditegaskan eksplisit oleh Direktur, sekalipun ia
`SetaraDirektur` untuk alur persetujuan lain. Default fail-closed: tidak diikutkan sampai ada
keputusan tertulis.

Menu WAJIB diberi penanda `perm` sejak commit pertama — RBAC modul ini mencatat menu tanpa
penanda selalu tampil ke semua orang.

### §4 Tidak pernah menghitung dari data mentah; ketidaktahuan adalah jawaban sah

Masukan model hanya hasil hitung yang sudah dikeluarkan endpoint §2, lengkap dengan penanda umur
data dan status kesegarannya (beberapa mart, mis. marketing-analytics, hanya sinkron tiap 48 jam
— ini WAJIB ikut disebutkan di jawaban, bukan disembunyikan). Bila tidak ada endpoint yang
menjawab kombinasi yang ditanya, asisten menjawab **tidak tahu** dan menunjuk layar yang ada,
bukan menaksir atau turun membaca database mentah.

### §5 Korelasi lintas modul lewat banyak pemanggilan tool dalam satu giliran, bukan join database

Pertanyaan yang butuh lebih dari satu modul (mis. KPI + presensi) dijawab dengan memanggil
endpoint §2 tiap modul secara terpisah dalam satu giliran tanya, lalu model menggabungkan
angka-angka yang SUDAH benar itu di kalimat jawaban. Tidak ada query gabungan lintas database.
Pasangan modul yang digabung wajib punya kunci penghubung yang sama (mis. `employee_id`,
`shop_id`) — diperiksa per pasangan modul saat `/plan`, tidak diasumsikan berlaku umum.

### §6 Batas jumlah modul per pertanyaan mengikuti batas gateway, bukan diperbaiki dulu

Tanpa streaming di iterasi pertama — jawaban dikirim utuh sekali jadi, dan total waktu satu
giliran (seluruh pemanggilan tool + model) wajib dijaga di bawah timeout gateway 30 detik (§
Context). Batas maksimal modul/tool-call per pertanyaan ditetapkan dari pengukuran nyata saat
`/plan`, bukan ditulis tangan di sini. Memperbaiki `gateway_request.go` sendiri (menambah SSE,
timeout per-rute) **ditunda** — berkas itu dipakai SELURUH service lain, jadi bukan keputusan
untuk satu fitur ini sendirian.

### §7 Keluaran terstruktur: teks, tabel, atau chart — pakai komponen yang sudah ada

Jawaban model berbentuk data terstruktur (bukan cuma prosa), diklasifikasi jenis penyajiannya
(teks/tabel/chart) sebelum dikirim ke frontend. Chart WAJIB pakai `ChartContainer` + Recharts yang
sudah baku di erp-frontend (palet `--fb-seri-*`, `connectNulls={false}`, dst) — dilarang membangun
sistem chart baru untuk fitur ini.

### §8 File (Excel/PDF/dokumen) hanya dibuat saat diminta eksplisit

Jawaban default selalu di dalam chat (teks/tabel/chart). Menghasilkan file terpisah menunggu
permintaan eksplisit dari penanya, bukan otomatis untuk tiap jawaban.

### §9 Asisten mewarisi gerbang endpoint aslinya apa adanya

Ini bukan tanggung jawab fitur ini untuk menutup celah RBAC yang sudah ada di endpoint yang
diteruskannya. TAPI: modul percontohan yang endpoint-nya diketahui belum bergerbang peran (lihat
§ Context) **wajib diperbaiki gerbangnya lebih dulu** sebagai prasyarat sebelum modul itu
diikutkan ke asisten — bukan diikutkan dengan lubang itu dibiarkan.

## Consequences

### Yang membaik

- SPV/Direktur/IT dapat jawaban lintas modul dalam hitungan detik tanpa menunggu laporan manual.
- Aturan bisnis tetap hidup di satu tempat (service pemiliknya) walau pintu masuknya jadi lebih
  fleksibel — tidak melahirkan sumber kebenaran kedua.

### Yang memburuk atau tetap terbuka

- Cakupan sempit di awal (beberapa modul saja), tumbuh bertahap, bukan universal sejak hari
  pertama — ini pengorbanan sadar demi keamanan, bukan kelalaian.
- Biaya panggilan AI per pertanyaan **belum pernah diukur** karena klien AI belum ada sama sekali.
- Batas 30 detik gateway membatasi kompleksitas pertanyaan lintas-modul yang bisa dijawab dalam
  satu giliran.
- Endpoint yang diketahui belum bergerbang peran (Integration, sebagian marketing-analytics)
  menahan modul terkait sampai diperbaiki lebih dulu (§9) — menambah pekerjaan di luar fitur ini
  sendiri sebagai prasyarat.

### Yang sengaja tidak dilakukan

- **Tidak ada akses database langsung atau lintas-database** untuk fitur ini.
- **Tidak ada tool query bebas** (SQL/Mongo) yang bisa ditulis model sendiri.
- **Tidak streaming** di iterasi pertama; tidak memperbaiki infrastruktur gateway bersama sebagai
  bagian dari fitur ini.
- **Tidak eksekusi apa pun** — murni baca, sama seperti batas [[ADR - 0058]] §5 yang tetap berlaku
  penuh di sini (tidak ada pengecualian seperti ADR-0127 untuk laporan Marketing).

## Dokumen Terkait

- [[Microservices - Assistant Service]] — prior art terdekat, konsep yang sama untuk satu modul; diperbarui mengikuti ADR ini
- [[ADR - 0058 Kapabilitas AI Digerbang Kelayakan Data, Bukan Kelayakan Teknologi]] — gerbang yang mengikat, §2-nya disimpangi sadar di §2 ADR ini
- [[ADR - 0120 Asisten Analisa Marketing Jadi Menu ERP, Template dan Jadwal Lebih Dulu Tanpa AI]] · [[ADR - 0127 Laporan Asisten Analisa Membawa Keputusan AI, Orang Menjalankan atau Menolak]] — preseden pola berbeda (satu domain, di dalam service pemilik), bukan aturan yang mengikat ADR ini
- [[ADR - 0082 Integrasi AI lewat Klien Tipis di Shared-Library]] — klaim klien AI di sana ternyata belum terimplementasi (lihat § Context)
- [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] · [[CORE - RBAC dan Permission Set]] — dasar gate §3
- [[REF - Kepemilikan Data]] — prinsip "konsumsi lewat pemilik" yang mendasari §2
- [[CORE - Kapabilitas AI dan Machine Learning]] — peta kapabilitas AI, aturan kolom Marketing
- [[CORE - API Master Gateway]] — mekanisme `Reroute`, batas §6
