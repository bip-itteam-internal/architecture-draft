# IT - Gerbang Repo dan Papan Sesi Agent

## Deskripsi

*AI Engineering Loop di agent-kit: **gerbang lokal** yang menolak commit di branch utama dan push yang gagal pemeriksaan dasar, **papan sesi** yang menunjukkan sesi kerja mana sedang mengerjakan apa, **Kantor Agent** yang menampilkan sesi yang sedang hidup sebagai robot di denah kantor sesuai alat yang sedang dipakai, dan **loop otonom** `/brief` → `/kerjakan` yang mengerjakan satu task kecil lewat agen domain, dinilai dua lapis (mesin dan penilai), lalu berhenti di PR. Semuanya hidup di mesin developer, tanpa layanan dan tanpa biaya berjalan di luar langganan Claude. Keputusan, substitusi dari dokumen rujukan, dan batasnya ada di [[ADR - 0077 Otonomi Merge Agent Digerbang Mekanisme yang Bisa Menolak]].*

- **Status**: ⚠️ **Implemented (ada catatan)**, agent-kit **1.15.0** (2026-09-06), terakhir berubah di **1.22.0** (2026-09-16, arah hadap robot Kantor Agent); bagian lain diperiksa ulang ke kit 1.19.0 pada 2026-09-15. Sumber: `architecture-draft/.agent-kit/` (`agents/`, `commands/`, `hooks/`, `baseline/`), disebar lewat `init` + restart sesi. Catatan: (1) gerbang lokal bisa dilewati `--no-verify`, disadari; (2) papan sesi berkas satu mesin; (3) baseline test diukur sekali 2026-09-06 dan wajib diukur ulang saat `main` bergerak jauh; (4) `/supervise` menulis draft, tidak pernah auto-apply; (5) agent berhenti di PR, merge tetap manusia; (6) **gerbang kit atas dirinya sendiri belum berjalan**, tak ada yang otomatis menjalankan `tests/test-init.ps1` maupun pytest `Tools/`; (7) **repo selain Node dan Go (mis. `mybharata-app`) tidak punya gerbang deterministik**, jadi lapis mesin `/judge` lolos tanpa memeriksa apa pun di sana; (8) **Kantor Agent membaca dua format internal Claude Code**, registri sesi `~/.claude/sessions` dan transkrip, jadi bisa patah di rilis mana pun; kerusakannya tampil sebagai banner (registri dicocokkan dengan `claude agents --json` yang terdokumentasi), bukan kantor kosong.

## Latar Belakang

Per 2026-09-06 tidak ada satu pun gerbang otomatis yang berjalan tanpa manusia di `erp-frontend` maupun `bip-erp`. Bukan lemah, melainkan nol:

- Seluruh workflow yang menggerbangi berstatus `disabled_manually`. Run terakhir `ci.yml` erp-frontend (2026-08-13) bahkan tidak sempat jalan karena kegagalan billing GitHub Actions.
- `pr-notification.yml` bip-erp tercatat `active` tetapi seluruh isinya dikomentari, sehingga tiap push memicu run gagal 0 detik yang tidak menggerbangi apa pun.
- `main` di kedua repo `protected: false`, dan rulesets ditolak 403 dengan tawaran upgrade paket.
- Nol hook git lokal aktif di kedua repo.

Di sisi agent-kit, kelima berkas `rules/` adalah prosa yang dibaca model, bukan skrip. Kedua hook yang terpasang selalu `exit 0`. Satu-satunya proses berexit-code di seluruh kit adalah `build-vault-index.py --check`, dan lingkupnya cuma kesegaran indeks dokumentasi.

Dua cacat kecil yang menjelaskan mengapa ini bisa bertahan lama tanpa terasa. Pertama, hook `PreToolUse` dipasang dengan matcher `Bash` sementara seluruh git di mesin dev Windows dijalankan lewat PowerShell, jadi pengingat pre-commit satu-satunya itu tidak pernah menyala di sana. Kedua, `tests/test-init.ps1` milik kit pernah merah beberapa rilis tanpa terdeteksi karena tidak ada CI yang menjalankannya.

Kebutuhan kedua datang dari pemilik proses: lebih dari empat sesi kerja berjalan bersamaan di satu mesin, dan jejaknya hilang.

## Ruang Lingkup / Cakupan (business view)

**Yang termasuk**

1. **Gerbang lapis satu, hook Claude Code** (`hooks/pre-commit-gate.ps1|.sh`, `PreToolUse`). Menolak lewat **exit 2** setiap `git commit` di branch default repo kode (dibaca dari `origin/HEAD`), bukan mencetak pengingat lalu lolos. Vault dikecualikan karena konvensinya push langsung ke `main`. **Gagal-tertutup**: bila perintahnya memuat commit tetapi repo-nya tak bisa ditentukan (mis. path dari ekspresi), commit ikut ditolak. Sejak kit **1.18.0** hook dipasang sebagai dua entri, matcher `Bash` dan `PowerShell`, masing-masing bersaring `if` (`Bash(*commit*)`, `PowerShell(*commit*)`), sehingga skripnya hanya di-spawn untuk perintah yang memuat kata commit. Sebelumnya skrip itu di-spawn untuk setiap panggilan tool: median 10× `Get-Location` 3,7 detik, lawan 0,27 detik sesudahnya (diukur di satu mesin dengan beban berbeda, rincian di changelog kit 1.18.0).
2. **Gerbang lapis dua, `pre-push` git hook** (`hooks/githooks/pre-push`, satu skrip `sh` untuk semua OS). `init` memasangnya lewat `core.hooksPath` absolut ke setiap repo sibling ber-`.git` selain vault; repo yang sudah punya `hooksPath` lain (mis. husky) dilewati, bukan ditimpa. Repo Node (`package.json` + `pnpm-lock.yaml`): `pnpm tsc`/`typecheck`/`lint` yang ada di scripts, lalu `pnpm build` (bisa dilewati sadar lewat `AGENTKIT_SKIP_BUILD=1`, dan itu dicetak). Repo Go multi-modul (bip-erp): `go build ./...` per `services/<x>` yang tersentuh, semua service bila `shared-library` tersentuh. **Repo jenis lain lolos tanpa pemeriksaan**, termasuk `mybharata-app`. Test sengaja tidak dijalankan di sini karena makan menit; itu urusan `/judge`. Dipilih `pre-push` dan bukan `pre-commit` karena gerbang yang berbunyi tiap beberapa menit akan dimatikan orang dalam sepekan.
3. **Gerbang kit atas dirinya sendiri** (ADR 0077 §4). ⚠️ **Belum berjalan** (diperiksa 2026-09-15): vault tidak punya `core.hooksPath`, `init` sengaja melewati `architecture-draft` saat memasang `pre-push`, dan tidak ada hook, githook, maupun skrip yang memanggil `tests/test-init.ps1` atau pytest `Tools/`. Keduanya masih dijalankan manual oleh yang mengubah kit, jadi kelas kegagalan yang melahirkan butir ini (test kit merah beberapa rilis tanpa terdeteksi) belum tertutup.
4. **Papan sesi.** Tiap sesi menulis satu berkas `.task-plans/sesi/<id>.json` berisi branch, task, tahap flow, dan waktu sentuh terakhir. Ditulis tiga hook: `SessionStart` (membuat), `UserPromptSubmit` (menyentuh), `SessionEnd` (menutup). `/papan-sesi` membacanya jadi satu tabel.

5. **Loop otonom** (revisi 2026-09-06). `/brief <masalah>` menulis Quick Brief Spec ke `.task-plans/briefs/<tanggal>-<slug>.md` (`templates/brief.md`: tujuan, kriteria lolos yang bisa diverifikasi, batas). **Routing terjadi di `/brief`**: repo ditentukan dari kata kunci dan LLM hanya dipakai bila ambigu; domain dari kata kunci dengan urutan menang fix > test > refactor > docs; tebakan ditandai `(ditebak)`. `/kerjakan <brief>` membaca repo dan domain dari brief → `worktree-baru` membuat worktree dari `origin/main` di path pendek `%USERPROFILE%\wt\<fe|be|mb|ad>-<slug>` (maks 60 karakter, tanpa spasi), branch `<domain>/<slug>` → agen `loop-<domain>` (`sonnet`) mengerjakan tanpa commit → `/judge` → bila gagal, eksekutor diulang dengan temuan judge, maksimum 2 pengulangan → bila lolos: commit conventional, push (kena `pre-push`; penolakannya diperlakukan sebagai kegagalan judge, bukan dilewati `--no-verify`), `gh pr create`. **Berhenti di PR.** Gagal 3× → worktree dibiarkan, path dan temuan dicetak untuk manusia. Brief domain docs dikerjakan langsung di vault `main`, tanpa worktree dan tanpa PR. Setelah PR merged, `worktree-bersih.ps1` membuang worktree-nya.
6. **Judges dua lapis.** `/judge` menjalankan `gerbang.ps1` DAN agen `loop-judge` (`opus`, hanya `Read/Grep/Glob`) yang menilai kepatuhan brief per kriteria, `review-checklist` Pass 1, dan solusi nakal. Isi gerbang mesin: repo Node `pnpm tsc`, `lint`, `build`, dan vitest dibanding `baseline/<repo>.json`; bip-erp `go build ./...` dan `go test` per service tersentuh, dibanding baseline. Lolos hanya bila **keduanya** lolos; agen tidak berwenang membatalkan mesin. ⚠️ Untuk repo jenis lain `gerbang.ps1` hanya mencatat *"jenis repo 'lain': tidak ada gerbang deterministik"* dan tetap mengembalikan lolos karena tak ada gerbang yang gagal, sehingga di sana yang benar-benar menilai tinggal agen judge. Log gerbang dua brief `mybharata-app` (2026-09-09) sama-sama mencatat nol gerbang dan lolos; pada salah satunya orkestrator menambahkan pemeriksaan pengganti (`flutter test`, `dart analyze`) secara manual, dan tidak ada skrip kit yang menjalankannya.
7. **Supervisi dan ekstraksi skill.** `/supervise` → agen `loop-supervisor` (`fable`) membaca brief/verdict/sesi/skill dan menulis laporan + **draft** ke `skills/_draft/`; `/supervise --terapkan <nama>` dijalankan manusia. `/ekstrak-skill` → `transkrip-ringkas` (skrip, menolak bila skema transkrip tidak terurai) → agen `loop-ekstrak-skill` (`fable`) → draft.

8. **Kantor Agent** (kit 1.20.0, v2 di 1.21.0). `/kantor-agent` membuka denah kantor isometrik berisi sesi Claude Code yang **terbuka** di workspace ini beserta apa yang sedang dikerjakannya, termasuk sesi yang menunggu izin Anda, diperbarui tiap 2 detik tanpa layanan dan tanpa hook. Rincian di § Kantor Agent.

**Yang sengaja TIDAK termasuk**

- Layanan orkestrasi eksternal (Trigger.dev), vendor model lain, layanan web live (Kantor Agent memperbarui diri lewat berkas, bukan server), agent merge, supervisor auto-apply. Alasan tiap substitusi di ADR bagian Revisi.
- Menghidupkan kembali GitHub Actions atau branch protection. Di luar mandat, alasan biaya dan paket akun.
- Memperbaiki review kode. Angka review 2,2% adalah masalah orang, bukan masalah alat.
- Suite E2E baru. Yang ada hanya **baseline** suite yang sudah ada; bahan bakar sebesar sistem rujukan (E2E tests 288/1.644) belum ada di sini.

## Cara Kerja

**Mengapa gerbangnya lokal.** Tiga batas mengunci pilihan ini dan ketiganya di luar mandat untuk diubah: Actions berbayar tidak boleh diandalkan, branch protection tidak tersedia pada paket akun sekarang, dan self-hosted runner lokasinya tidak diketahui ([[IT - CI-CD]]). Yang tersisa adalah mesin developer sendiri.

**Sebuah aturan baru dianggap gerbang hanya bila ada proses yang keluar dengan status bukan nol, atau hook yang mengembalikan penolakan eksplisit.** Kalimat perintah di dalam berkas prosa bukan gerbang. Konsekuensinya `wrap-completion-gate.md` dan `review-checklist.md` tetap dipakai dan tetap berharga, tetapi namanya turun kelas menjadi checklist.

**Distribusi hook adalah bagian tersulitnya, bukan isinya.** `.git/hooks/` tidak ikut ter-clone, jadi hook wajib disimpan sebagai berkas ter-commit di repo lalu diaktifkan lewat `git config core.hooksPath`, dan pengaktifannya wajib menjadi langkah `init`. Tanpa itu gerbangnya cuma hidup di mesin yang kebetulan memasangnya, dan itu mengulang persis pola disiplin-tanpa-penjaga yang sudah gagal 18 kali berturut-turut di repo `audit-bharata`.

**Papan sesi berupa berkas, bukan layanan**, supaya ia tidak ikut mati saat layanannya mati. Satu-satunya saat orang membutuhkan papan ini adalah saat keadaan sedang kacau.

## Persona / Pengguna

| Persona | Peran & Divisi | Akses / RBAC | Device |
|---|---|---|---|
| Developer | Tech Development | tidak lewat RBAC ERP, cukup akses repo | Workstation |
| Agent AI | dijalankan developer di workspace | mewarisi akses mesin yang menjalankannya | Workstation |

- **Tujuan**: menjalankan banyak sesi kerja tanpa kehilangan jejak, dan tidak mendorong perubahan yang belum lolos pemeriksaan dasar.
- **Pain point**: nol gerbang otomatis, sehingga kesalahan hanya ketahuan sesudah mendarat; dan empat sesi lebih berjalan bersamaan tanpa cara melihat keadaannya selain membuka satu per satu.
- **Aksi utama**: menjalankan flow wajib per task; gerbang menyala sendiri saat commit dan push; papan sesi dibaca lewat satu command.

Karyawan pengguna ERP **tidak** menjadi persona di sini. Perkakas ini tidak menyentuh satu pun layar ERP dan tidak memuat data karyawan.

## Konsumen Data

- [[DEVELOPER GUIDE]] — flow wajib per task yang digerbangi perkakas ini
- [[RUN - Onboarding Developer Baru]] — jalur pemasangan; pengaktifan `core.hooksPath` menjadi langkah di sini
- [[IT - Development Apps and Tools]] — daftar perkakas internal tim

## Kendala

- **Gerbang lokal bisa dilewati** dengan `--no-verify`. Diterima sadar: ia menahan kelalaian, bukan niat, dan kelalaian adalah yang benar-benar terjadi di sini.
- **Gerbang lokal tidak berlaku bagi yang belum memasangnya.** Inilah alasan `core.hooksPath` wajib jadi langkah `init`, bukan anjuran.
- **Branch protection tetap tidak ada**, jadi tidak ada apa pun di sisi GitHub yang menahan push langsung ke `main`.
- **`pnpm test` erp-frontend tidak pernah hijau penuh di `main`**, jadi test tidak bisa dipakai sebagai syarat lolos dalam bentuk mentah. Karena itu test dibandingkan dengan **baseline bertanggal** (`baseline/<repo>.json`, keduanya diukur 2026-09-06: erp-frontend 11.554 test dengan 37 gagal di `c8993067`, bip-erp 14.562 test dengan 14 gagal di `12bd8484`), dan hanya kegagalan **baru** yang menggagalkan. Baseline itu dipakai `/judge`, bukan `pre-push`. Ia menua saat `main` bergerak; ukur ulang dengan `baseline-test.ps1` di checkout `origin/main` yang bersih, jangan di branch fitur.
- **Waktu tunggu push bertambah.** `build` erp-frontend tidak murah, dan di bip-erp perubahan `shared-library` membuat `pre-push` mem-build **semua** service. Bila ternyata mengganggu, yang diturunkan adalah cakupannya, bukan sifat menolaknya.

## Batas dengan Papan Aktivitas Developer

[[IT - Papan Aktivitas Developer]] mencatat peristiwa GitHub yang **sudah terjadi** (push, PR, review) lewat webhook, di Cloudflare. Papan sesi mencatat pekerjaan yang **sedang berjalan dan belum menghasilkan peristiwa apa pun**.

Sejak 2026-09-07 (kit 1.17.0 + PR #1 `feat/loop-ingest` di papan, merged hari itu juga), kedua sumber itu **bertemu di papan tim tanpa menghitung ulang angka PR**: hook kit mengirim peristiwa sesi/brief/judge/PR ke `POST /loop/ingest` (opt-in per mesin, best-effort, tanpa judul), dan papan menampilkannya di bagian Loop otonom di samping tabel PR yang sudah ada. Dashboard lokal `/dashboard` tetap dipertahankan sebagai cadangan yang tidak butuh jaringan dan satu-satunya tempat judul brief terlihat. Yang tetap benar: sesi yang macet tanpa commit hanya terlihat lewat jalur sesi ini, bukan lewat webhook GitHub.

## Dashboard (kit 1.16.0, 2026-09-07)

Dibangun sebagai **HTML statis interaktif**, bukan layanan: `dashboard.ps1` (Windows) / `dashboard.py` (mac/linux) mengumpulkan data lalu menanamkannya sebagai JSON ke `dashboard.template.html`, satu-satunya penulis UI; filter rentang 7/14/30 hari dan repo dihitung di halaman dari data 30 hari yang ditanam, jadi tidak butuh server. `--loop <detik>` menulis ulang berkala dan halaman me-refresh diri tiap 60 detik. Bentuk bagan mengikuti skill dataviz (stacked bar horizontal untuk komposisi, bukan donat; line 2 seri untuk tren; ubin untuk angka tunggal; legend selalu ada; tabel kembar per bagan), palet dark divalidasi. PR ditarik `gh` **per irisan mingguan** karena bip-erp menembus batas 500 dalam 30 hari; irisan yang penuh diperingatkan di halaman, bukan disembunyikan.

| Panel | Sumber | Keadaan |
|---|---|---|
| SHIPPED (dibuka/merged per hari, merge rate, cycle) · MIX · HOTSPOTS · CYCLE | `gh pr list` bip-erp + erp-frontend | ✅ |
| LOOP (brief → judge → PR, status merged dicocokkan ke data gh) | `.task-plans/briefs`, `.task-plans/judge` | ✅ data lokal, sejak kit 1.15.0 |
| SESI | `.task-plans/sesi` | ✅ |
| BASELINE | `.agent-kit/baseline` | ✅ bertanggal |
| SPEND (biaya per PR) · RISK / PATCH-ARCHITECTURAL | tidak ada | ditulis di kaki halaman sebagai "tidak ada sumber" |

### Pemetaan kelayakan panel (2026-09-06, sebelum dibangun)

Ditinjau memakai dasbor sistem rujukan sebagai daftar panel. Saat itu diputuskan tetap berkas dulu; sehari kemudian pemilik meminta tampilannya dan dibangun sebagai HTML statis di atas. Pemetaan dipertahankan sebagai rekaman alasan panel mana yang ada dan tidak:

| Panel | Bisa diisi di sini | Catatan |
|---|---|---|
| Jumlah PR dibuka/merge, grafik, cycle median total, hotspot komponen | Ya, **tapi sudah ada** di [[IT - Papan Aktivitas Developer]] | menyalinnya melahirkan dua angka untuk satu pertanyaan |
| Komposisi fix/test/docs/feature | **Ya** | 90% judul PR erp-frontend dan 87% bip-erp sudah berpola conventional commit (diukur 2026-09-06 atas 60 PR merged terakhir tiap repo) |
| Merge rate | Ya, tapi tak berguna | akan selalu di sekitar 99% karena 90% PR di-merge penulisnya sendiri |
| Cycle dipecah investigate/develop/QA | Tidak | tidak ada tahap QA otomatis, jadi pecahannya tidak punya sumber |
| Sumber temuan (test yang menemukan, lalu diperbaiki) | Belum | menuntut baseline test lebih dulu |
| Biaya per PR | Tidak | tidak ada pelacakan biaya per task sama sekali, menuntut instrumentasi baru |
| Klasifikasi risiko dan jenis perubahan | Tidak, dan berisiko | klasifikasi otomatis tampil sebagai angka pasti padahal tebakan |

Yang perlu diingat saat meninjau ulang: **panel yang paling dibutuhkan justru tidak ada di dasbor rujukan itu.** Dasbor itu menghitung PR yang sudah jadi, sedangkan kebutuhan di sini adalah sesi yang sedang berjalan dan belum menghasilkan PR apa pun.

## Kantor Agent (kit 1.20.0; v2 di 1.21.0; arah hadap robot di 1.22.0, 2026-09-16)

`/kantor-agent` menjawab pertanyaan yang tak bisa dijawab papan sesi: sesi mana **sedang melakukan apa sekarang**. Papan sesi hanya tahu `tahap`, yang berubah lewat slash command (61 dari 72 sesi aktif masih `mulai`), dan status `aktif`, yang terukur tak bisa dipercaya (72 dari 99 berkas aktif, hanya 7 transkripnya ditulis dalam 10 menit terakhir; keduanya diukur 2026-09-15). Karena itu sumbernya bukan berkas sesi, melainkan **registri sesi Claude Code** (sejak 1.21.0) untuk sesi mana yang terbuka dan apakah ia sedang bekerja, ditambah **ekor transkrip** untuk tool yang sedang dipakai. Desain dan keputusannya: `architecture-draft/.agent-kit/docs/2026-09-15-kantor-agent-design.md` (§ v2 untuk 1.21.0).

**Bentuknya.** Tiap sesi hidup tampil sebagai robot **Lead** di denah kantor isometrik (SVG, tanpa library), dan tiap subagent hidup sebagai robot kecil berperan menurut `agentType` (`general-purpose` Generalis, `Explore` Peneliti, `Plan` Arsitek, agen `loop-*` sesuai perannya, jenis lain dengan nama aslinya). Robot berjalan lewat koridor ke area sesuai tool yang sedang dipakai:

| Tool yang tertunda | Area |
|---|---|
| Read, Grep, Glob, WebFetch, WebSearch, Skill, ToolSearch | Perpustakaan |
| Edit, Write, NotebookEdit; juga saat berpikir di antara tool | Meja |
| PowerShell, Bash, Monitor, TaskOutput, TaskStop; tool MCP dan tool tak dikenal; juga saat giliran selesai tetapi tugas shell latar belum selesai | Ruang server |
| Agent, Workflow, SendMessage; juga saat giliran selesai tetapi subagent masih hidup | Ruang rapat |
| AskUserQuestion, ExitPlanMode; juga saat giliran selesai tanpa subagent, atau dialog yang bukan izin | Lounge (menunggu Anda) |

Sejak **1.22.0** robot juga menghadap ke arah yang semestinya, dibulatkan ke empat mata angin: duduk menghadap perabot yang dipakainya, berjalan menghadap arah jalannya. Proyeksi isometrik ini hanya memperlihatkan sisi selatan dan timur, jadi robot yang menghadap utara atau barat tampil dari punggung **tanpa wajah**; itu disengaja, dan siapa dia tetap terbaca dari label nama serta warnanya.

Sesi yang **menunggu izin** tetap di area tool yang dimintakan izinnya (Lounge bila tool-nya belum tertulis di transkrip); robotnya bersinar dengan gelembung **!** yang tak pernah diredupkan, karena makin lama ia menunggu makin perlu dilihat.

Dalam satu batch tool paralel, hasil tool singkat sering baru tertulis ke transkrip setelah tool lambat di batch yang sama selesai (diukur atas 25 transkrip), jadi yang menentukan area adalah tool tertunda **paling awal di luar Perpustakaan/Meja**, bukan yang terakhir.

**Cara kerjanya.** `hooks/kantor-agent.py` satu-satunya penulis data, hanya pustaka standar Python. Tiap 2 detik ia membaca registri sesi Claude Code (`~/.claude/sessions/<pid>.json`, format internal, diamati di 2.1.269): sesi = entri yang prosesnya masih hidup (waktu buat proses dicocokkan dengan `procStart`, supaya PID yang didaur ulang tak terbaca hidup) dan `cwd`-nya di dalam workspace; `status` busy/idle/waiting menentukan apakah ia bekerja, dan `waitingFor` menandai dialog yang menunggu Anda. Tool yang sedang dipakai diambil dari ekor transkrip sesi itu (subagent: ≤ 10 menit dan belum `end_turn`). Registri dicocokkan dengan `claude agents --json` (terdokumentasi) tiap 60 detik lewat subprocess yang tak menahan tick; dua ketidakcocokan berturut-turut memasang banner. Registri yang tak terbaca menurunkan penulis ke cara 1.20.0 (transkrip yang ditulis ≤ 30 menit). Tugas shell latar dilacak bertahap per transkrip, bukan dari ekornya: jarak awal tugas ke notifikasi selesainya terukur p90 480 KB dan maks 6,6 MB atas 430 tugas dalam 7 hari, jauh melampaui ekor 64 KB. Tugas yang dihentikan TaskStop (tak pernah mendapat notifikasi) dan tugas milik proses Claude Code yang lama tidak ditunggu. Hasilnya ditulis ke `.task-plans/kantor-agent-data.js` (versi 2) secara atomik. `hooks/kantor-agent.template.html` satu-satunya penulis UI; halaman `.task-plans/kantor-agent.html` memuat ulang data itu lewat `<script>` yang disuntik ulang, yang terbukti membaca isi terbaru di `file://`, dan tiap kartu memuat tombol salin id sesi beserta asal (VS Code/terminal), nama, dan pid. Launcher `hooks/kantor-agent.ps1` / `.sh` mencari Python (venv vault, `py -3`, `python3`) dan tidak menyalakan penulis kedua bila PID yang tercatat masih hidup; penulis sendiri memegang kunci berkas, jadi dua launcher serentak tetap menghasilkan satu penulis. `--berhenti` menghentikannya, dan penulis berhenti sendiri setelah 60 menit tanpa sesi hidup. Data tidak dikirim ke mana pun, beda dari peristiwa `loop-ingest` ke papan tim.

**Tak ada yang senyap.** Penulis mati: banner data basi setelah 10 detik dan robot diredupkan. Format transkrip berubah: banner "perbarui kit", bukan kantor kosong. Python tak ada: launcher exit 2 dan menyebut lokasi yang dicari. Data dari `--sekali`: banner snapshot sekali, bukan penulis mati. Registri tak terbaca, atau dua kali berturut-turut tak cocok dengan `claude agents`: banner. Data versi lain (penulis dari kit lama masih jalan): robot dipulangkan dan banner menyuruh `--berhenti` lalu `/kantor-agent`.

**Terukur.** 1.20.0: tick p95 68,9 ms atas 6 sesi hidup nyata; perubahan transkrip terbaca halaman dalam 0,7 sampai 2,7 detik; penulis tetap hidup setelah panggilan tool yang menyalakannya selesai. 1.21.0, di workspace nyata 2026-09-15: 6 dari 6 sesi di halaman sama dengan `claude agents --json`, termasuk sesi yang diam 6 jam dan tak terlihat dari transkrip; dialog pertanyaan sesi lain tercatat `waiting` + `input needed` dan tampil menunggu Anda; tugas latar sungguhan (`git push` sesi lain yang masih berjalan, dan tugas uji yang awalnya ~100 KB di luar ekor) tampil menunggu tugas latar; dua launcher serentak menghasilkan satu penulis; tombol salin di halaman terpasang mengisi clipboard; tick p50 8 ms, p95 15 ms sesudah tick pertama (tick pertama membaca jendela tugas latar 8 MB per transkrip, p95 tujuh tick awal 423 ms). Test: `tests/test_kantor_agent.py` (110 test atas templat baris transkrip nyata yang dibersihkan; kontrol mutasi `procStart`, kunci penulis, dan aturan pelacak tugas latar terbukti merah), `tests/test-init.ps1` (registri palsu, dua launcher serentak), dan `tests/kantor-agent-browser.ps1` (manual lewat CDP, 27 check termasuk clipboard yang dibaca balik; 38 sejak 1.22.0). Seperti test kit lain, ketiganya dijalankan manual (catatan 6 di Status).

**Batas yang disadari**

- Menunggu izin dibaca dari registri: `waitingFor` yang memuat "permission" menjadi gelembung **!**. Diukur 2026-09-16 dengan dialog izin tool sungguhan: registri berubah ke `waiting` + `waitingFor: "permission prompt"`, gelembungnya tampil 1,7 detik kemudian, dan hilang 3,1 detik sesudah disetujui. Bila registri tak terbaca, prompt izin kembali hanya ditebak: tool yang tertunda ≥ 60 detik diberi tanda `?`.
- Sesi yang masih tertahan di layar awal, dan sesi anak yang dijalankan dari shell tool sesi lain (mewarisi `CLAUDE_CODE_CHILD_SESSION`), tidak punya entri registri sendiri sehingga tidak tampil.
- Satu mesin, dan hanya sesi yang `cwd`-nya di dalam workspace.
- Tugas shell latar yang dimulai sebelum 8 MB terakhir transkrip, saat penulis pertama melihat sesinya, tak terlihat; sesi yang hanya menunggu tugas setua itu tampil menunggu Anda.
- Tool yang sudah berjalan sementara model masih menulis tool call berikutnya di pesan yang sama belum tercatat di transkrip, karena baris pesan baru ditulis setelah pesannya lengkap. Selama itu robot tampil berpikir di Meja (terukur 22 detik untuk pesan yang memuat perintah panjang, 2026-09-15).
- Halaman tidak bisa memfokuskan jendela sesi; kartunya memberi id, asal, nama, dan pid untuk menemukannya sendiri.
- Launcher `.sh` belum pernah dijalankan di mac/linux.
- ADR 0077 §5 menyebut "tanpa dashboard"; halaman ini dicatat sebagai baris di tabel Revisi ADR itu karena prinsip berkas-bukan-layanan tetap dipatuhi.

## Belum Diputuskan (TBD)

- Apakah papan sesi berkas perlu lintas-mesin. Dirancang untuk satu mesin karena jumlah dev yang benar-benar memakai kit belum diukur. Sejak kit 1.17.0 peristiwa sesi dari mesin yang menyalakan ingest sudah tampil di papan tim, tetapi tanpa judul task; papan berkas yang lengkap tetap satu mesin.
- ~~Apakah keluaran papan sesi layak disalurkan ke [[IT - Papan Aktivitas Developer]] sebagai sumber kedua, atau justru harus tetap terpisah agar tidak melahirkan dua angka yang menyimpang.~~ **Dijawab 2026-09-07** (kit 1.17.0): disalurkan sebagai peristiwa opt-in ke `POST /loop/ingest` dan ditampilkan di bagian Loop otonom yang terpisah dari tabel PR, jadi angka PR tidak dihitung ulang. Rinciannya di § Batas dengan Papan Aktivitas Developer dan [[ADR - 0034 Papan Aktivitas Developer di Luar Arsitektur ERP]].
- Bentuk gerbang untuk repo selain Node dan Go. Loop sudah dipakai di `mybharata-app`, sementara `pre-push` dan `gerbang.ps1` sama-sama tidak memeriksa apa pun di sana (Ruang Lingkup butir 2 dan 6). Belum diputuskan apakah keduanya perlu mengenali Flutter (`flutter test`, `dart analyze`), atau `gerbang.ps1` perlu gagal-tertutup untuk jenis repo yang tak dikenalnya.
- ~~Ekstraksi skill dari sesi manual. Bahan mentahnya sudah menumpuk (`erp/.agents/AGENTS.md`, 721 baris, 26 entri ber-`originSessionId`) dan cetakan pipeline-nya sudah terbukti di `Tools/`, tetapi urutannya sesudah gerbang dan papan sesi.~~ **Dibangun 2026-09-06** (kit 1.15.0) sebagai `/ekstrak-skill`, lihat Ruang Lingkup butir 7.
- Agent milik tool `Workflow` di Kantor Agent. Tidak ditampilkan: pemindaian 78 transkrip utama 14 hari (2026-09-15) menemukan 0 pemanggilan `Workflow` nyata, jadi lokasi dan bentuk transkrip agent-nya belum pernah teramati. Lead yang memanggil `Workflow` tetap tampil di ruang rapat.
- Tautan dari panel SESI `/dashboard` ke Kantor Agent. Belum dibuat.

## Dokumen Terkait

- [[ADR - 0077 Otonomi Merge Agent Digerbang Mekanisme yang Bisa Menolak]] — keputusan dan alasannya
- [[IT - CI-CD]] — keadaan pipeline, jalur deploy produksi yang belum terverifikasi
- [[IT - Papan Aktivitas Developer]] — papan peristiwa GitHub, beda lingkup
- [[ADR - 0034 Papan Aktivitas Developer di Luar Arsitektur ERP]] — preseden perkakas developer di luar arsitektur ERP
- [[RUN - Onboarding Developer Baru]] — pemasangan kit
- [[DEVELOPER GUIDE]] — flow wajib per task
- [[IT - SOP Dokumentasi Vault]] — konvensi dokumentasi
