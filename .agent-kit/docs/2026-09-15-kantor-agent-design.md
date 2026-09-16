# Desain: Kantor Agent, denah isometrik sesi Claude Code yang hidup (v1.20.0)

- **Status**: ✅ Implemented, agent-kit 1.20.0 (2026-09-15). Desain disetujui pemilik per bagian pada hari yang sama; yang berubah saat implementasi dan review dicatat di § Perubahan dari desain awal
- **Tanggal**: 2026-09-15
- **Versi kit**: 1.20.0 (dari 1.19.0)
- **Keputusan arsitektur**: `Decisions/ADR - 0077 Otonomi Merge Agent Digerbang Mekanisme yang Bisa Menolak` (baris Kantor Agent di tabel Revisi)
- **Cara kerja untuk pembaca non-kit**: `IT/IT - Gerbang Repo dan Papan Sesi Agent` (bagian Kantor Agent)
- **Mockup**: lokal di `.task-plans/mockup/` pada mesin perancang. Sengaja tidak disalin ke vault karena memuat judul sesi nyata, dan repo vault PUBLIC

## Konteks

Pemilik ingin melihat bagaimana agent bekerja di mesin lokal: tiap sesi yang aktif tampil sebagai
robot yang masuk ke ruang sesuai pekerjaannya. Rujukan visualnya denah kantor isometrik berisi
agent sesuai perannya, bukan kotak-kotak ruang terpisah.

Yang sudah ada tidak menjawabnya. Diukur 2026-09-15:

- **`/papan-sesi` dan panel SESI `/dashboard` tak tahu aktivitas saat ini.** `tahap` hanya berubah
  saat slash command diketik; 61 dari 72 berkas sesi berstatus aktif masih di `mulai`.
- **Status `aktif` di berkas sesi tak bisa dipakai sebagai "hidup".** 72 dari 99 berkas berstatus
  aktif, tetapi hanya 7 transkripnya ditulis dalam 10 menit terakhir. Tiga berkas aktif yang
  diperiksa tak punya transkrip di mana pun (sesi dibuka tanpa prompt). Sesi yang ditutup tanpa
  `SessionEnd` tercatat aktif selamanya.
- **Transkrip sudah memuat yang dibutuhkan.** Tiap `tool_use`, `tool_result`, dan `end_turn`
  tercatat bertanda waktu. Subagent tercatat terpisah di `<sesi>/subagents/agent-<id>.jsonl`
  dengan `.meta.json` berisi `agentType` dan `description`. Judul sesi ada di kejadian `ai-title`,
  PR di `pr-link`.

## Tujuan dan bukan tujuan

**Tujuan**: satu halaman lokal yang menampilkan tiap sesi hidup sebagai robot **Lead** dan tiap
subagent hidup sebagai robot kecil **berperan**, berpindah antar-area kantor sesuai alat yang sedang
dipakai, diperbarui tiap 2 detik, tanpa layanan dan tanpa hook baru.

**Bukan tujuan** (sengaja tidak dibangun):

- lintas mesin (mewarisi TBD dok domain);
- riwayat, replay, atau statistik; feed hanya 30 perpindahan terakhir di memori halaman;
- mengendalikan sesi dari halaman; halaman read-only;
- biaya atau token per sesi;
- membedakan "menunggu izin" dari "tool berjalan" (tak ada sumbernya, lihat § Batas);
- mode terang, kamera yang bisa diputar atau di-zoom.

## Keputusan dan yang ditolak

| # | Keputusan | Dipilih | Ditolak, dan kenapa |
|---|---|---|---|
| 1 | Arti ruang | **aktivitas saat ini** | tahap flow: 61/72 sesi di `mulai`, robot menumpuk di lobi. Repo: menjawab "di mana", bukan "sedang apa" |
| 2 | Pemakai | **tim, lewat agent-kit** | mesin ini saja: tak ikut dirawat saat kit berubah |
| 3 | Subagent | **robot kecil sendiri** | lencana angka di Lead: isi kerjanya tak terlihat. Tidak ditampilkan sama sekali |
| 4 | Penyajian | **penulis Python + HTML statis `file://`** | HTML + File System Access API: Chromium saja, izin folder diminta ulang, belum terbukti di `file://`. Server + SSE: layanan, melanggar ADR 0077 §5 |
| 5 | Gaya | **denah kantor isometrik** | kotak ruang (piksel, blueprint, isometrik): dibandingkan di mockup, ditolak pemilik karena tak seperti kantor sungguhan |
| 6 | Peran | **Lead + `agentType`** | tahap flow: mayoritas jatuh ke satu peran. Repo: ambigu untuk sesi lintas repo |
| 7 | Render | **SVG isometrik tanpa library** | Three.js: vendor ratusan KB atau CDN yang mati saat offline, render loop WebGL di mesin yang sering sesak. Canvas + sprite: aset harus dibuat dan dirawat, label digambar manual |
| 8 | Label saat ramai | **area berisi ≥ 4 robot: nama saja**, alat di hover dan panel | gelembung alat untuk semua: di mockup membentuk kolom label setinggi enam baris |

## Bukti yang mendasari

**Spike `file://`** (Chrome headless lewat CDP, 2026-09-15). Percobaan pertama berbasis waktu
tidak membuktikan apa pun, karena Chrome butuh sekitar 30 detik untuk menyala sehingga berkas
sudah berganti sebelum halaman sempat membaca; hasil itu dibuang. Percobaan deterministik:

1. halaman terbukti membaca `A` (5 kali muat);
2. berkas ditulis langsung ke `B`; dalam 1,5 detik halaman membaca `B`;
3. 20 kali penggantian atomik (tulis `.tmp` lalu ganti nama) tiap 100 md: 0 gagal ganti nama,
   halaman menampilkan versi terakhir.

Kesimpulan: `<script src="data.js?t=...">` yang disuntik ulang membaca isi terbaru di `file://`,
dan Chrome tidak mengunci berkasnya.

**Membaca transkrip.** Ekor 5 kejadian dari 13 transkrip hidup: **0,045 detik** dengan Python 3.14.
Profil serupa dengan `ConvertFrom-Json` PowerShell 5.1 tidak selesai dalam 180 detik. Karena itu
penulis data tidak ditulis dalam PowerShell.

**Konkurensi 30 hari** (163 transkrip utama + 673 subagent, 1,3 GB; jeda ≤ 10 menit dianggap hidup):

| | Median | p90 | p99 | Maks |
|---|---|---|---|---|
| Sesi utama bersamaan | 2 | 4 | 6 | 8 |
| Subagent bersamaan | 1 | 3 | 7 | 13 |
| Total robot | 2 | 5 | 10 | 19 |

**Jenis subagent 30 hari** (673): `general-purpose` 488, `Explore` 134, `loop-docs` 14,
`loop-judge` 13, `loop-fix` 10, `claude-code-guide` 7, `Plan` 4, `loop-refactor` 3. `loop-test`
tidak pernah dipakai.

**Format transkrip internal.** Dok resmi (`code.claude.com/docs/en/sessions.md`) menyatakan format
entri internal, dan skrip yang membacanya "can break on any release". Sejalan dengan komentar di
`hooks/transkrip-ringkas.ps1`.

## Alur pengguna

1. Ketik `/kantor-agent`. Launcher menyalakan penulis data dan membuka halaman.
2. Halaman menampilkan denah; robot masuk dari pintu dan berjalan ke area sesuai keadaan sesinya.
3. Klik tab nama Lead: robot Lead dan subagentnya disorot, panel menggulir ke kartunya.
4. Halaman boleh ditutup. Penulis tetap jalan sampai sepi 60 menit atau dihentikan dengan
   `/kantor-agent --berhenti`; perintah berhenti dicetak saat menyala.
5. `/kantor-agent` lagi saat penulis masih hidup: tidak menyalakan penulis kedua, cukup membuka
   halaman.

Titik putus yang ditangani: Python tak ditemukan (pesan menyebut tiga lokasi yang dicari), penulis
mati atau berhenti (banner menyebut sejak kapan dan perintah untuk menyalakannya lagi).

## 1. Arsitektur dan komponen

```
<proyek-dir>/*/<sesi>.jsonl ─────────────────┐
<sesi>/subagents/agent-*.jsonl + .meta.json ─┼─> kantor-agent.py --loop 2
.task-plans/sesi/<sesi>.json ────────────────┘        │ tulis atomik tiap 2 dtk
                                                       v
                                     .task-plans/kantor-agent-data.js
                                                       │ <script> disuntik ulang tiap 2 dtk
                                                       v
                                     .task-plans/kantor-agent.html (file://)
```

| Berkas di `.agent-kit/` | Tugas |
|---|---|
| `hooks/kantor-agent.py` | **Satu-satunya penulis data**: memilih sesi hidup, menurunkan area, keadaan, dan peran, menulis `kantor-agent-data.js` secara atomik |
| `hooks/kantor-agent.template.html` | **Satu-satunya penulis UI**: denah SVG isometrik, robot, label, tab, panel, feed |
| `hooks/kantor-agent.ps1` | Launcher Windows: mencari Python, mencegah penulis ganda, menyalin template, menjalankan penulis terlepas, membuka halaman, `-Berhenti` |
| `hooks/kantor-agent.sh` | Launcher mac/linux dengan `python3`, pola `dashboard.sh` |
| `commands/kantor-agent.md` | `/kantor-agent [--berhenti] [--sekali]` |
| `tests/test_kantor_agent.py`, `tests/fixtures/kantor-agent/` | Unit test fungsi murni penulis atas potongan transkrip sungguhan |
| `tests/kantor-agent-browser.ps1` | Verifikasi manual halaman di Chrome sungguhan lewat CDP |

Keluaran di `.task-plans/` (bukan repo git): `kantor-agent.html` (salinan template, ditimpa tiap
launcher jalan), `kantor-agent-data.js`, `kantor-agent.pid`, `kantor-agent.log`.

Antarmuka:

```
kantor-agent.py  --workspace WS [--proyek-dir DIR] (--sekali | --loop DETIK) [--sepi-menit 60] [--keluaran DIR] [--log BERKAS]
kantor-agent.ps1 [-Workspace WS] [-ProyekDir DIR] [-Sekali] [-Interval 2] [-SepiMenit 60] [-TanpaBuka] [-Berhenti] [-Python EXE]
```

`--proyek-dir` bawaannya `~/.claude/projects`; hanya test yang menggantinya.

**Tiga prinsip**

1. **Satu penulis data, satu penulis UI.** Peta tool ke area dan `agentType` ke peran hanya hidup
   di `kantor-agent.py`. Sengaja berbeda dari `/dashboard`, yang punya dua pengumpul
   (`dashboard.ps1` dan `dashboard.py`) yang harus dijaga identik dengan tangan.
2. **Tanpa hook baru.** Data diambil dari transkrip yang memang ditulis Claude Code, jadi tak ada
   spawn proses tambahan di tiap panggilan tool.
3. **Berkas, bukan layanan** (ADR 0077 §5). Penulis yang mati terlihat sebagai data basi, bukan
   robot beku yang tampak masih bekerja.

**Launcher**

- Mencari Python berurutan: `architecture-draft/Tools/.venv/Scripts/python.exe`, `py -3`,
  `python3`. Urutan ini mengikuti `commands/index-vault.md`: `python` global di banyak mesin tim
  menunjuk ke venv proyek lain. Tak ada satu pun: exit 2 dengan pesan.
- `kantor-agent.pid` berisi PID yang masih hidup **dan** command line proses itu memuat
  `kantor-agent.py`: tidak menyalakan penulis kedua, cukup mencetak PID-nya. PID basi yang sudah
  dipakai proses lain tidak terbaca sebagai penulis. Penjagaan ini ada di launcher, bukan kunci di
  penulis, jadi dua launcher pada detik yang sama masih bisa menyalakan dua penulis.
- Menyalin template ke `.task-plans/kantor-agent.html`, menjalankan penulis terlepas dengan
  `--loop 2 --log .task-plans/kantor-agent.log` (penulis mencatat sendiri, jadi tak ada handle yang
  diwariskan ke proses lepas), menunggu penulis hidup paling lama 30 detik (exit 3 bila tidak), lalu
  membuka halaman kecuali `-TanpaBuka`. Penulis terbukti tetap hidup setelah panggilan tool yang
  menjalankan launcher selesai.

**Pemilihan sesi tiap tick**

- Kandidat: `<proyek-dir>/*/*.jsonl` dengan mtime ≤ 30 menit. Daftar direktori (`os.scandir`)
  dipakai sebagai prasaring longgar (6 jam), baru kandidatnya di-`stat` tepat: `os.stat` per berkas
  di Windows terukur 77 ms untuk 167 transkrip per tick.
- Yang dibaca hanya ekor: 64 KB untuk transkrip utama, 32 KB untuk subagent (desain awal 256/128 KB
  terukur median 320 ms per tick); baris pertama yang terpotong dan baris terakhir yang sedang
  ditulis dibuang. Hasil urai di-cache per `(ukuran, mtime)`, jadi hanya transkrip yang berubah yang
  diurai ulang; judul dan PR yang jatuh di luar ekor dipertahankan dari urai sebelumnya.
- Sesi masuk bila `cwd` terakhir di transkrip berada di dalam workspace (dibandingkan setelah
  `normcase`).
- `.task-plans/sesi/<id>.json` hanya pelengkap: `tahap`, `task`, dan `status=selesai` (membuat
  robot pulang tanpa menunggu 30 menit).

**Halaman**

- Menyuntik ulang `<script src="kantor-agent-data.js?t=<ms>">` tiap 2 detik. Data sah terakhir
  dipertahankan bila muatan gagal atau berkasnya terbaca terpotong.
- Basi bila `sekarang − dibuat > 10 detik`. Data dari `--sekali` (`penulis.interval_detik = 0`)
  tampil sebagai snapshot sekali, bukan penulis mati.

## 2. Model keadaan

### Robot dan peran

- **Lead**: satu per sesi hidup. Label dari `ai-title` terakhir, lalu `task` berkas sesi, lalu
  8 karakter id. Chip tahap hanya bila tahapnya bukan `mulai`; lencana PR dari `pr-link`.
- **Subagent**: satu per subagent hidup, warna induknya. Peran dari `agentType`:

| agentType | Peran | agentType | Peran |
|---|---|---|---|
| `general-purpose` | Generalis | `loop-test` | QA |
| `Explore` | Peneliti | `loop-refactor` | Refactor |
| `Plan` | Arsitek | `loop-judge` | Juri |
| `loop-fix` | Engineer | `loop-docs` | Penulis |
| `claude-code-guide` | Pemandu | lainnya | nama asli `agentType` |

### Aturan area

Diturunkan dari kejadian terakhir yang bermakna. `attachment`, `queue-operation`, `ai-title`,
`pr-link`, dan tipe lain di luar `user`/`assistant` tidak mengubah keadaan. `tool_use` tertunda
dihapus oleh `tool_result`-nya, oleh `end_turn`, dan oleh prompt baru dari user (kejadian `user`
tanpa `tool_result` dan bukan `isMeta`).

Dalam satu batch tool paralel, hasil tool singkat (Read, Edit) sering baru tertulis setelah tool
lambat di batch yang sama selesai. Diukur 2026-09-15 atas 25 transkrip: pada 125 batch yang tool
lambatnya lebih dulu, hasil tool singkatnya ikut tertahan, sehingga aturan "tool tertunda terakhir"
menaruh robot di Perpustakaan selama PowerShell berjalan. Karena itu yang menentukan area adalah tool
tertunda paling awal di luar Perpustakaan/Meja, dan bila tak ada, yang paling awal.

| Urutan | Kondisi | Area | Keadaan |
|---|---|---|---|
| 1 | Ada `tool_use` tertunda | menurut tool tertunda paling awal di luar Perpustakaan/Meja (bila tak ada: paling awal) | `alat` (atau `menunggu_anda` untuk tool Lounge) |
| 2 | `end_turn` dan masih ada subagent hidup | Ruang rapat | `menunggu_subagent` |
| 3 | `end_turn` tanpa subagent hidup | Lounge | `menunggu_anda` |
| 4 | Selain itu (sesudah hasil tool, prompt baru, thinking) | Meja sendiri | `berpikir` |

| Tool | Area |
|---|---|
| Read, Grep, Glob, WebFetch, WebSearch, Skill, ToolSearch | Perpustakaan |
| Edit, Write, NotebookEdit | Meja sendiri |
| PowerShell, Bash, Monitor, TaskOutput, TaskStop | Ruang server |
| Agent, Workflow, SendMessage | Ruang rapat |
| AskUserQuestion, ExitPlanMode | Lounge |
| Tool MCP dan tool tak dikenal | Ruang server, dengan nama aslinya (tidak ditebak dari namanya) |

**Hidup dan pulang**

- Sesi hidup: transkrip ditulis ≤ 30 menit dan belum ada `SessionEnd` yang lebih baru dari
  kejadian terakhirnya.
- Subagent hidup: transkripnya ditulis ≤ 10 menit dan kejadian terakhirnya bukan `end_turn`.
  Subagent pulang begitu `end_turn`.

### Penanda di atas robot

- **Durasi tool** tampil setelah 60 detik, bersama tanda "?" dan keterangan "prompt izin tidak
  tercatat di transkrip" (`PowerShell · 2m14s ?`). Di bawah itu gelembung hanya memuat alat dan
  detailnya.
- **Diam**: kejadian terakhir lebih dari `ambang.diam_menit` (10) menit lalu. Robot diredupkan dan
  diberi label `diam 14m`. Ambang diam dan hidup dibaca halaman dari data, tidak ditulis ulang.

### Kontrak data

`kantor-agent-data.js` adalah satu-satunya jembatan penulis ke UI.

```js
window.__KANTOR__ = {
  versi: 1,
  dibuat: "<ISO UTC>",
  penulis: { pid: 1234, interval_detik: 2, berhenti: null, tick_ms: { p50, p95, n } },   // berhenti "sepi" pada tulisan terakhir; interval 0 = --sekali
  ambang: { hidup_menit: 30, diam_menit: 10 },
  skema: { baris_diurai: 812, baris_rusak: 0, dikenali: true, dilewati_luar_workspace: 0 },
  sesi: [{
    id, judul, tahap, pr,
    area,        // "perpustakaan" | "meja" | "server" | "rapat" | "lounge"
    keadaan,     // "alat" | "berpikir" | "menunggu_anda" | "menunggu_subagent"
    alat, detail, sejak, durasi_detik, diam_detik,
    subagent: [{ id, jenis, peran, deskripsi, area, keadaan, alat, detail, sejak, durasi_detik, diam_detik }]
  }]
}
```

- `detail` dipotong 56 karakter: `description` untuk PowerShell/Bash/Monitor, **nama berkas (bukan
  path)** untuk Read/Edit/Write, pola untuk Grep/Glob, `description` untuk Agent, header pertanyaan
  untuk AskUserQuestion, kosong untuk yang lain.
- Data hanya ditulis ke disk lokal dan tidak dikirim ke mana pun. Ini berbeda dari `loop-kirim`,
  yang sengaja tanpa judul karena mengirim ke papan tim.
- `skema.dikenali = false` bila lebih dari separuh baris gagal diurai, atau ada transkrip hidup
  sepanjang ≥ 20 baris tanpa satu pun kejadian `user`/`assistant` di ekornya (yang lebih pendek
  dianggap sesi yang baru lahir). Ambang separuh sama dengan penolakan di `transkrip-ringkas.ps1`.
  Sebelum menyimpulkan yang kedua, ekor diperluas ×4 sampai 2 MB: satu hasil tool bisa lebih besar
  dari ekornya, dan ekor yang cuma berisi potongan baris itu tak boleh terbaca sebagai format berubah.

## 3. Denah dan perilaku robot

### Denah

Satu lantai 26 × 20 unit, proyeksi isometrik 2:1: `layar_x = (x − y) · 20`,
`layar_y = (x + y) · 10 − z · 22`. Dinding belakang (utara dan barat) setinggi 3,2 unit, dinding
depan dipotong 0,55 unit. Sekat antar-ruang berupa kaca tembus pandang setinggi 2,3 unit, supaya
isi ruang di belakangnya tetap terlihat.

| Area | Lantai (x, y, lebar, dalam) | Isi | Titik robot |
|---|---|---|---|
| Perpustakaan | 0, 0, 12, 6 | 4 rak buku di dinding utara, 2 meja baca | 10 |
| Ruang server | 12, 0, 14, 6 | 8 rak berlampu, meja konsol dengan 2 monitor | 9 |
| Koridor | 0, 6, 26, 2 | jalur antar-area, antrean luapan | 16 |
| Area meja | 0, 8, 17, 8,9 | 8 pod (meja, kursi Lead, 2 bangku subagent), meja panjang cadangan 6 kursi, papan tulis | 8 Lead, 16 subagent, 6 cadangan |
| Ruang rapat | 18, 8, 8, 7 | meja bundar, 8 kursi | 8 |
| Lounge | 17, 16,3, 8,6, 3,5 | sofa dan kursi santai menghadap penonton, 2 beanbag, pantry, kulkas | 8 |
| Pintu masuk | 0, 16,9, 9, 3,1 | pintu di dinding barat, meja resepsionis, keset | titik masuk dan keluar |

- Ukuran mengikuti pengukuran: 8 pod sama dengan puncak sesi bersamaan; kapasitas total di atas 19
  sama dengan puncak robot. Luapan area masuk antrean koridor; bila koridor pun penuh, label area
  menampilkan `+N`.
- Tempat duduk menghadap penonton (sofa, kursi santai), dan kursi Lead berada di sisi utara meja,
  supaya wajah robot terlihat di atas monitor. Perabot yang membelakangi penonton menutupi robotnya,
  dan itu terlihat di mockup pertama.

### Urutan kedalaman

- Urutan gambar menurut `x + y` pusat objek (painter's order).
- Objek panjang (dinding, sekat, sofa, meja panjang) dipecah per 1 unit, supaya urutannya benar
  terhadap robot di sebelahnya.
- Perabot dirender sekali ke kelompok per `floor(x + y)`. Robot yang berjalan dipindahkan ke
  kelompok yang sesuai posisinya setiap kali melintasi batas unit.

### Perilaku robot

- **Meja tetap**: Lead mendapat pod kosong pertama saat muncul dan memegangnya sampai pulang; Lead
  ke-9 dan seterusnya duduk di meja cadangan. Subagent memakai 2 bangku pod induknya, sisanya
  berdiri di sisi pod.
- **Warna identitas** diberikan halaman: slot palet kosong pertama saat Lead muncul, dilepas saat
  pulang. Memakai 6 slot palet `/dashboard` yang sudah divalidasi; Lead ke-7 dan seterusnya abu netral.
  Identitas tak pernah bergantung pada warna saja karena nama selalu tertulis.
- **Berjalan** lewat pintu area dan koridor, tidak menembus dinding. Kecepatannya tetap, tetapi satu
  perpindahan dibatasi paling lama 3 detik (perjalanan jauh dipercepat) supaya tampilan tak
  tertinggal dari data. Tujuan yang berganti di tengah jalan dilanjutkan dari posisi saat itu.
- **`berpikir` berarti diam di tempat dengan gelembung pikiran.** Robot kembali ke meja hanya bila
  berpikir lebih dari 20 detik, atau saat mulai Edit/Write. Alasannya: pola nyata Read, pikir, Read
  dengan interval data 2 detik membuat robot yang selalu kembali ke meja tak pernah tiba di mana pun.
- Muncul dari pintu masuk; pulang berjalan ke pintu lalu hilang.
- Animasi kerja hanya saat berhenti: membaca (perpustakaan), mengetik dengan lampu monitor berwarna
  Lead (meja), lampu rak berkedip (server), duduk (rapat, lounge). Dengan `prefers-reduced-motion`,
  robot berpindah tanpa berjalan dan tanpa animasi berulang.

### Label

- **Lead**: nama (judul ≤ 20 karakter, atau 8 karakter id) dengan batang warna, ditambah gelembung
  `PowerShell · <detail> · 2m14s`, `menunggu Anda`, `menunggu N subagent`, atau titik-titik berpikir.
- **Subagent**: peran; deskripsi dan alat di hover.
- **Area berisi ≥ 4 robot: nama saja**; alat di hover dan panel.
- **Penempatan tanpa tabrakan**: papan area menjadi rintangan. Tiap label mencoba bergeser ke atas
  (kelipatan 14 px) dan ke samping (±46 px) sampai tak menabrak, dengan garis penunjuk ke kepala
  robot. Lead didahulukan, lalu yang paling depan.

### Sekeliling denah

- **Header**: jumlah Lead dan subagent, status penulis (`live · 2 dtk lalu`).
- **Tab nama Lead**: klik menyorot robot Lead beserta subagentnya dan menggulir panel ke kartunya.
- **Panel kanan**: kartu per Lead (judul, tahap bila bukan `mulai`, PR, area, alat, durasi, daftar
  subagent) dan feed 30 perpindahan terakhir. Feed dihitung halaman dari selisih dua data
  berurutan, jadi penulis tak perlu tahu soal feed.
- **Lima keadaan layar**: memuat (denah kosong, "menunggu penulis"), kosong ("tak ada sesi hidup"),
  normal, basi (banner "data berhenti sejak HH:MM:SS", robot diredupkan), dan format berubah
  (banner "perbarui kit").
- Tema gelap saja, senada `/dashboard`. Teks berbahasa Indonesia; ini perkakas kit, bukan
  erp-frontend, jadi ADR 0010 tidak berlaku.

## 4. Galat, pengujian, distribusi, dokumen

### Galat: semua terlihat, tak ada yang senyap

| Kejadian | Penulis | Halaman |
|---|---|---|
| Python tak ditemukan | launcher exit 2: "butuh Python 3.8+. Dicari: <venv vault>, py -3, python3" | tidak dibuka |
| Penulis sudah jalan | tidak menyalakan yang kedua, mencetak PID lama | normal |
| Penulis tak menyala dalam 30 detik | launcher exit 3, menunjuk `kantor-agent.log` | tidak dibuka |
| Penulis mati | tidak ada | banner basi bila `dibuat` lebih dari 10 detik, robot diredupkan |
| Format transkrip berubah | tetap menulis, `skema.dikenali = false` | banner "perbarui kit" |
| Satu transkrip terkunci atau terhapus di tengah tick | berkas itu dilewati pada tick ini, tidak crash | sesinya hilang sementara |
| Menulis `data.js` gagal 5 kali berturut-turut | exit 3 dengan pesan di log; berkas sementara tiap percobaan dibuang | banner basi |
| Sepi 60 menit | menulis data terakhir berisi `penulis.berhenti: "sepi"`, lalu exit 0 | banner "penulis berhenti: tak ada sesi hidup cukup lama" |
| `--sekali` | menulis sekali, tanpa PID, `interval_detik: 0` | setelah 10 detik banner "snapshot sekali", bukan "penulis mati" |

### Pengujian: tiap lapis harus bisa merah

1. **Unit Python** di `tests/test_kantor_agent.py` (pytest, venv vault). Fixture-nya potongan JSONL
   transkrip sungguhan yang dipangkas, bukan objek rakitan tangan: test yang memalsukan sumbernya
   sudah terbukti buta di repo ini (`team-memory.md` § endpoint daftar). Kasus: tool tertunda ke
   area; `end_turn` dengan subagent ke rapat; `end_turn` tanpa subagent ke lounge; prompt baru
   membatalkan tool tertunda; subagent `end_turn` pulang; tool dan `agentType` tak dikenal; berkas
   kit `selesai` pulang; `cwd` di luar workspace dilewati; lebih dari separuh baris rusak membuat
   `dikenali = false`. Kasus penting dibuktikan tidak vakum dengan satu mutasi yang membuatnya merah.
2. **Integrasi** di `tests/test-init.ps1`, dengan pola cek `dashboard.ps1` yang sudah ada: folder
   proyek palsu lewat `-ProyekDir`, jalankan `kantor-agent.ps1 -Sekali -TanpaBuka`, lalu pastikan
   `kantor-agent-data.js` versi 1 memuat sesi uji di area yang benar dan HTML tersalin.
3. **Browser nyata**, gerbang sebelum `/wrap`: pola CDP dari spike (halaman membaca data A, penulis
   menulis B, halaman menampilkan B dalam ≤ 3 detik), ditambah screenshot kelima keadaan layar dan
   satu area berisi ≥ 4 robot. jsdom tak bisa membuktikan ini. Dibangun sebagai
   `tests/kantor-agent-browser.ps1` (manual, butuh Chrome): memuat, normal, data B tanpa reload
   dengan pod dan warna stabil, ambang dari data, ramai, format berubah, kosong, basi, snapshot
   `--sekali`, sepi, dan 0 galat JavaScript.
4. **Beban**: durasi tick penulis diukur dengan sesi hidup nyata; lolos bila p95 ≤ 200 ms.
   Pembanding terukur: membaca ekor 13 transkrip butuh 45 ms.

⚠️ Dok domain mencatat test kit **tidak dijalankan otomatis oleh apa pun** (butir "gerbang kit atas
dirinya sendiri belum berjalan"). Rencana implementasi wajib menjalankan keempatnya secara eksplisit
dan menempelkan keluarannya.

### Distribusi

- `VERSION` naik ke 1.20.0, dengan entri changelog di `README.md`.
- `init` tidak diubah: ia sudah menyalin `hooks/` dan `commands/` utuh.
- `templates/workspace-CLAUDE.md` menambahkan `/kantor-agent` di deretan perkakas loop otonom.
- mac/linux cukup `kantor-agent.sh`; tampilannya identik di semua OS karena hanya ada satu penulis
  dan satu template.

### Dokumen vault (lewat `/sync-docs`)

- **ADR 0077**: baris baru di tabel Revisi, di sebelah baris Dashboard. Cukup revisi, bukan ADR
  baru, karena §5 (berkas, bukan layanan) tetap dipatuhi.
- **IT - Gerbang Repo dan Papan Sesi Agent**: bagian baru "Kantor Agent". Daftar "sengaja tidak
  termasuk" diubah dari "dashboard web live" menjadi "layanan web live", dan batas yang disadari di
  bawah ikut dicatat.

## Batas yang disadari

- **Prompt izin tidak tercatat di transkrip.** Tool yang tertunda lebih dari 60 detik diberi tanda
  "?" dengan keterangan itu, bukan ditebak.
- **Format transkrip internal.** Bisa patah di rilis Claude Code mana pun; terdeteksi sebagai
  "format berubah", dan perbaikannya di kit.
- **Satu mesin, dan hanya sesi yang `cwd`-nya di dalam workspace.** Sesi yang dibuka dari folder di
  luar workspace (misalnya worktree `C:\wt\...`) tidak tampil.
- **Menunggu tugas shell latar (`run_in_background`) tidak dibedakan dari menunggu Anda**: Lead
  tampil di lounge. Subagent latar tertangani karena transkripnya sendiri hidup.
- **Tool yang sudah berjalan sebelum pesan asistennya selesai ditulis belum terlihat.** Claude Code
  menjalankan tool call pertama selagi model masih menulis tool call berikutnya di pesan yang sama,
  tetapi baris pesan baru masuk ke transkrip setelah pesannya lengkap. Selama itu robot tampil
  berpikir di Meja. Terukur 2026-09-15: Agent berjalan sejak 14:15:09, baris pesannya baru tertulis
  14:15:31 karena tool call kedua memuat perintah panjang.
- **Langkah model yang sangat panjang** tanpa tulisan transkrip bisa memicu tanda "diam" walau sesi
  masih bekerja.
- **Sesi yang ditutup tanpa `SessionEnd`** baru pulang setelah 30 menit tanpa tulisan transkrip.
- **Dua `/kantor-agent` pada detik yang sama** bisa menyalakan dua penulis yang menulis isi sama;
  `--berhenti` hanya menghentikan yang tercatat di berkas PID.
- **Launcher `.sh` belum pernah dijalankan** di mac/linux; galatnya terlihat oleh pemakai pertama.

## Belum diputuskan (TBD)

- **Transkrip agent milik tool `Workflow`**: tidak teramati. Diperiksa saat `/plan` (2026-09-15):
  0 pemanggilan `Workflow` nyata di 78 transkrip utama 14 hari, jadi lokasi dan bentuk transkripnya
  belum pernah terlihat, dan agent-agent itu tidak ditampilkan. Lead yang memanggil `Workflow` tetap
  tampil di ruang rapat.
- **Tautan dari panel SESI `/dashboard` ke Kantor Agent**: di luar lingkup rilis ini.

## Perubahan dari desain awal

Ditemukan saat implementasi, verifikasi data nyata, dan `/review` (2026-09-15). Faktanya sudah
diperbarui di bagian masing-masing; daftar ini hanya penunjuk.

- Ekor transkrip diperpendek, daftar direktori jadi prasaring, dan hasil urai di-cache (§ Pemilihan
  sesi tiap tick). Tick p95 93 ms saat diukur, 68,9 ms atas 6 sesi hidup nyata.
- Tool penentu area dalam batch paralel: paling awal di luar Perpustakaan/Meja, bukan yang terakhir
  (§ Aturan area). Ditemukan verifikasi data nyata: robot sesi yang menjalankan PowerShell dua
  menit tampil di Perpustakaan.
- Pecahan detik 7 digit yang ditulis PowerShell di berkas sesi dinormalkan, karena Python ≤ 3.10
  menolaknya.
- Transkrip pendek tanpa percakapan tidak lagi terbaca sebagai format berubah (§ Kontrak data).
- Penulis tunggal dijaga launcher lewat PID dan command line, penulis menerima `--log` (§ Launcher).
- Dari `/review`: ambang diam dan hidup dibaca halaman dari data (§ Penanda); data `--sekali` tampil
  sebagai snapshot (§ Halaman, § Galat); teks papan area dan angka 60 detik masing-masing hidup di
  satu konstanta template.
