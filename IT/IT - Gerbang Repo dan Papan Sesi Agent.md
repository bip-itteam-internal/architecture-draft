# IT - Gerbang Repo dan Papan Sesi Agent

## Deskripsi

*AI Engineering Loop di agent-kit: **gerbang lokal** yang menolak commit di branch utama dan push yang gagal pemeriksaan dasar, **papan sesi** yang menunjukkan sesi kerja mana sedang mengerjakan apa, **Kantor Agent** yang menampilkan sesi yang sedang hidup sebagai robot di denah kantor sesuai alat yang sedang dipakai, dan **loop otonom** `/brief` → `/kerjakan` yang mengerjakan satu task kecil lewat agen domain, dinilai dua lapis (mesin dan penilai), lalu berhenti di PR. Semuanya hidup di mesin developer, tanpa layanan dan tanpa biaya berjalan di luar langganan Claude. Keputusan, substitusi dari dokumen rujukan, dan batasnya ada di [[ADR - 0077 Otonomi Merge Agent Digerbang Mekanisme yang Bisa Menolak]].*

- **Status**: ⚠️ **Implemented (ada catatan)**, agent-kit **1.15.0** (2026-09-06), terakhir berubah di **1.27.0** (2026-09-21, Kantor Agent dibagi jadi pos per departemen); bagian lain diperiksa ulang ke kit 1.19.0 pada 2026-09-15. Sumber: `architecture-draft/.agent-kit/` (`agents/`, `commands/`, `hooks/`, `baseline/`), disebar lewat `init` + restart sesi. Catatan: (1) gerbang lokal bisa dilewati `--no-verify`, disadari; (2) papan sesi berkas satu mesin; (3) baseline test diukur sekali 2026-09-06 dan wajib diukur ulang saat `main` bergerak jauh; (4) `/supervise` menulis draft, tidak pernah auto-apply; (5) agent berhenti di PR, merge tetap manusia; (6) ✅ gerbang kit atas dirinya sendiri **berjalan sejak 1.25.0** lewat `pre-push` vault, tetapi ia menyala hanya bila push menyentuh `.agent-kit/` atau `Tools/` dan bisa dilewati sadar lewat `AGENTKIT_SKIP_KIT_TESTS=1`; `tests/kantor-agent-browser.ps1` sengaja tetap manual; (7) ✅ **nol gerbang tidak lagi dihitung lulus sejak 1.25.0**, jenis `flutter` dikenali dan `node` menerima lockfile apa pun, tetapi logikanya masih punya **dua implementasi** (`.ps1` untuk Windows, `.py` untuk mac/linux) yang dijaga test paritas alih-alih disatukan; (8) **Kantor Agent membaca dua format internal Claude Code**, registri sesi `~/.claude/sessions` dan transkrip, jadi bisa patah di rilis mana pun; kerusakannya tampil sebagai banner (registri dicocokkan dengan `claude agents --json` yang terdokumentasi), bukan kantor kosong.

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
2. **Gerbang lapis dua, `pre-push` git hook** (`hooks/githooks/pre-push`, satu skrip `sh` untuk semua OS). `init` memasangnya lewat `core.hooksPath` absolut ke setiap repo sibling ber-`.git` **dan, sejak kit 1.25.0, ke vault juga**; repo yang sudah punya `hooksPath` lain (mis. husky) dilewati, bukan ditimpa. Repo Node (`package.json` + `pnpm-lock.yaml`): `pnpm tsc`/`typecheck`/`lint` yang ada di scripts, lalu `pnpm build` (bisa dilewati sadar lewat `AGENTKIT_SKIP_BUILD=1`, dan itu dicetak). Repo Go multi-modul (bip-erp): `go build ./...` per `services/<x>` yang tersentuh, semua service bila `shared-library` tersentuh. Test sengaja tidak dijalankan di sini karena makan menit; itu urusan `/judge`. Dipilih `pre-push` dan bukan `pre-commit` karena gerbang yang berbunyi tiap beberapa menit akan dimatikan orang dalam sepekan.
3. ✅ **Gerbang kit atas dirinya sendiri** (ADR 0077 §4), **berjalan sejak kit 1.25.0** (2026-09-21). Sebelumnya tidak: vault tak punya `core.hooksPath` karena `init` sengaja melewatinya, dan tak ada satu pun hook, githook, atau skrip yang memanggil `tests/test-init.ps1` maupun pytest `Tools/`; keduanya bergantung pada ingatan orang yang mengubah kit. Kini `pre-push` vault memanggil `hooks/gerbang-kit.py` — **satu** implementasi untuk semua OS, bukan pasangan `.ps1`/`.py`, karena python sudah jadi syarat pytest-nya sendiri. Yang dijalankan: pytest (`Tools/tests`, `tests/test_kantor_agent.py`, `tests/test_gerbang.py`) lalu `tests/test-init.ps1`. `tests/kantor-agent-browser.ps1` sengaja **tidak** ikut: ia butuh Chrome dan sekitar tiga menit, dan tetap manual. Tiga hal menjaganya tidak mengganggu pekerjaan dokumentasi sehari-hari: **saringan path** (push yang tidak menyentuh `.agent-kit/` atau `Tools/` keluar seketika, dan `Toolsmith/` tidak tertipu), **penjaga rekursi** `AGENTKIT_KIT_TESTS_RUNNING` karena `test-init` menjalankan `init` yang memasang hook ini, dan **jalan keluar sadar** `AGENTKIT_SKIP_KIT_TESTS=1` yang dicetak keras. Venv dicari di worktree **utama** repo, sebab worktree tertaut tidak punya `Tools/.venv`; python tanpa pytest bukan kandidat, dan bila tak ada kandidat sama sekali gerbangnya **gagal** dengan pesan cara membuat venv, bukan lolos.

   ⛔ **Lingkungan git hook wajib dibuang sebelum memanggil test.** Git mewariskan `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`, dan `GIT_QUARANTINE_PATH` ke hook-nya, dan variabel itu **menang atas penemuan repo**: `git -C <folder lain> <perintah>` tetap mengenai repo yang sedang di-push. Ditemukan pada push pertama yang memicu gerbang ini (2026-09-21) dan akibatnya lebih berbahaya daripada lubang yang sedang ditutup: `test-init.ps1` membuat repo sandbox di `%TEMP%`, tetapi seluruh perintah gitnya mendarat di worktree vault yang sedang di-push — dua commit kosong bertambah di atas branch kerja, branch `feat/uji` lahir di repo nyata, HEAD berpindah ke `main`, dan `user.email=test@example.invalid` tertulis ke config repo. Tak satu pun terbaca sebagai galat; yang terlihat hanya test-init merah yang hijau bila dijalankan langsung. `gerbang-kit.py` kini membuang **seluruh** `GIT_*`, bukan daftar tertentu, karena yang diwariskan git bertambah antar versi; dan `test-init.ps1` **menolak jalan** bila masih melihat lingkungan itu, supaya test yang dijalankan tangan dari konteks hook berhenti alih-alih mengubah repo orang. Berlaku untuk hook mana pun yang memanggil skrip yang menyentuh git, bukan cuma gerbang ini.

   ⛔ **Daftar berkas yang tidak bisa ditentukan menyalakan gerbang, bukan mematikannya.** `$rsha` yang dioper git ke `pre-push` adalah tip remote sesungguhnya, dan itu bisa commit yang belum ada di mesin ini bila remote sudah maju; `git diff <commit asing> <lsha>` lalu gagal **diam-diam**, daftar berkasnya kosong, dan tiap cabang membaca kosong itu sebagai "tidak ada yang tersentuh". Terukur 2026-09-21 pada push kedua: perubahan `.agent-kit/` dilaporkan *"gerbang test kit DILEWATI"*, dan cabang Go akan berbunyi *"tidak ada services/<x> tersentuh"* dengan cara yang sama. `pre-push` kini memastikan basis diff benar-benar ada (`git cat-file -e`) dan, bila tidak, memeriksa **semua**: gerbang kit dinyalakan lewat `--paksa`, repo Go membangun seluruh service. Ini kelas yang sama dengan nol-gerbang-lolos, cuma satu lapis lebih awal — yang membuatnya sulit dilihat adalah keduanya mengaku "tidak ada yang perlu diperiksa" dengan kalimat yang terdengar benar.
4. **Papan sesi.** Tiap sesi menulis satu berkas `.task-plans/sesi/<id>.json` berisi branch, task, tahap flow, dan waktu sentuh terakhir. Ditulis tiga hook: `SessionStart` (membuat), `UserPromptSubmit` (menyentuh), `SessionEnd` (menutup). `/papan-sesi` membacanya jadi satu tabel.

5. **Loop otonom** (revisi 2026-09-06). `/brief <masalah>` menulis Quick Brief Spec ke `.task-plans/briefs/<tanggal>-<slug>.md` (`templates/brief.md`: tujuan, kriteria lolos yang bisa diverifikasi, batas). **Routing terjadi di `/brief`**: repo ditentukan dari kata kunci dan LLM hanya dipakai bila ambigu; domain dari kata kunci dengan urutan menang fix > test > refactor > docs; tebakan ditandai `(ditebak)`. `/kerjakan <brief>` membaca repo dan domain dari brief → `worktree-baru` membuat worktree dari `origin/main` di path pendek `%USERPROFILE%\wt\<fe|be|mb|ad>-<slug>` (maks 60 karakter, tanpa spasi), branch `<domain>/<slug>` → agen `loop-<domain>` (`sonnet`) mengerjakan tanpa commit → `/judge` → bila gagal, eksekutor diulang dengan temuan judge, maksimum 2 pengulangan → bila lolos: commit conventional, push (kena `pre-push`; penolakannya diperlakukan sebagai kegagalan judge, bukan dilewati `--no-verify`), `gh pr create`. **Berhenti di PR.** Gagal 3× → worktree dibiarkan, path dan temuan dicetak untuk manusia. Brief domain docs dikerjakan langsung di vault `main`, tanpa worktree dan tanpa PR. Setelah PR merged, `worktree-bersih.ps1` membuang worktree-nya.

5b. **Peran per lapisan tim IT** (kit 1.24.0). Sejak 1.24.0 eksekutornya dipilih dari **dua sumbu, domain kali repo**, bukan domain saja, supaya perannya sama dengan Development Team di [[SCRUM SPECS]] (BE/FE/DevOps, QA yang masih dirangkap Scrum Master):

   | Domain | Repo | Eksekutor |
   |---|---|---|
   | `docs` | architecture-draft | `loop-docs` (Penulis) |
   | `test` | mana pun | `loop-test` (QA) |
   | `fix`, `refactor` | erp-frontend | `loop-fe` |
   | `fix`, `refactor` | bip-erp | `loop-be` |
   | `fix`, `refactor` | mybharata-app | `loop-mobile` |
   | `fix`, `refactor` | menyentuh CI, compose, env, urutan deploy | `loop-devops` |
   | `fix`, `refactor` | repo lain | `loop-fix` / `loop-refactor` (cadangan) |

   `loop-devops` sengaja **tidak diberi `PowerShell` maupun `Bash` di `tools`**: ia menulis compose, workflow, skrip, dan urutan deploy, tetapi tak punya alat menjalankannya. Itu menjadikan aturan "deploy PROD dijalankan manusia" sebuah gerbang, bukan kalimat di dalam prosa, sesuai §3 [[ADR - 0077 Otonomi Merge Agent Digerbang Mekanisme yang Bisa Menolak]] yang menuntut gerbang punya exit code.

   **Paralel.** `/kerjakan <a> <b>` menjalankan dua eksekutor bersamaan bila repo-nya berbeda, kedua brief bertanda `Paralel: aman`, dan pasangan yang berbagi endpoint memuat blok `## Kontrak` yang identik. Maksimum dua sekaligus karena satu mesin; terukur 2026-09-21, dua pekerjaan berbasis Chrome bersamaan membuat salah satunya gagal dengan *"target CDP tidak ditemukan dalam 120 detik"*. Yang diparalelkan waktu **mengetik**, bukan waktu deploy: untuk perubahan kontrak, BE tetap di-deploy sebelum FE, dan badan PR wajib menuliskannya. Brief lama tanpa field `Paralel` dibaca sebagai `tidak`.

   Ukuran yang mendasarinya (14 hari, 64 transkrip, 2026-09-21): 40 sesi memanggil agent, **32 dari 40 tak pernah punya lebih dari satu subagent hidup bersamaan**, agen `loop-*` hanya 52 dari 624 panggilan, dan **5 dari 12 brief butuh percobaan kedua**. Jeda PR dibuka sampai di-merge **p50 6 menit** di kedua repo, jadi manusia bukan hambatan dan mempercepat loop memang terasa sampai ujung. Apakah peran spesialis benar-benar menurunkan pengulangan **belum terbukti**; log judge mencatat field `agen` supaya itu bisa diukur, bukan diyakini.
6. **Judges dua lapis.** `/judge` menjalankan `gerbang.ps1` DAN agen `loop-judge` (`opus`, hanya `Read/Grep/Glob`) yang menilai kepatuhan brief per kriteria, `review-checklist` Pass 1, dan solusi nakal. Isi gerbang mesin: repo Node `pnpm tsc`, `lint`, `build`, dan vitest dibanding `baseline/<repo>.json`; bip-erp `go build ./...` dan `go test` per service tersentuh, dibanding baseline. Lolos hanya bila **keduanya** lolos; agen tidak berwenang membatalkan mesin.

   ⛔ **Nol gerbang dulu dihitung LULUS, dan sejak kit 1.25.0 tidak lagi.** `lolos` dihitung sebagai "tak ada gerbang yang gagal", dan daftar kosong memenuhi syarat itu, jadi repo yang jenisnya tak dikenali dinyatakan lolos tanpa satu pemeriksaan pun sementara yang benar-benar menilai tinggal agen judge. Log gerbang dua brief `mybharata-app` (2026-09-09) sama-sama mencatat nol gerbang dan lolos; pada salah satunya orkestrator menambahkan `flutter test` dan `dart analyze` secara manual, dan tak ada skrip kit yang menjalankannya. Diukur 2026-09-21 saat ditutup, yang jatuh ke jenis `lain` bukan satu melainkan **empat**: `architecture-draft`, `mybharata-app`, `guestbook-system`, dan `consolidated-accounting-app` (dua terakhir karena deteksi `node` dulu menuntut `pnpm-lock.yaml`, padahal keduanya memakai `package-lock.json`).

   Yang menentukan sekarang adalah **jenis repo, bukan jumlah gerbang**, karena nol gerbang punya dua arti yang berlawanan: jenis `lain` berarti kita tidak tahu cara memeriksanya (**GAGAL**), sedangkan repo Go yang branch-nya cuma menyentuh README memang tidak punya yang perlu diperiksa (lolos, dengan catatan bahwa lolos itu tidak membuktikan apa pun). Satu-satunya pengecualian adalah daftar-izin `RepoTanpaGerbang` berisi `architecture-draft`, dan daftar itu **bukan kekebalan**: gerbang yang benar-benar berjalan selalu menang. Jenis **`flutter`** kini dikenali dari `pubspec.yaml` (`dart analyze` atas folder `.dart` tersentuh, berbatas 300 detik dan terpisah dari `flutter test --machine` yang dibandingkan baseline), deteksi **`node`** menerima lockfile apa pun dengan pelaksana dibaca dari lockfile-nya (`pnpm` menang bila keduanya ada, seperti di `erp-frontend`), dan **alat yang tidak terpasang membuat gerbang gagal, bukan lenyap**. ⚠️ Logikanya punya **dua implementasi** (`gerbang-lib.ps1` untuk Windows, `gerbang-lib.py` untuk mac/linux); cabang yang cuma mendarat di satu sisi tidak berbunyi apa pun sampai seseorang menjalankan gerbang di OS lain, jadi `tests/test_gerbang.py` menguji paritas keduanya atas fixture yang sama.
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

## Kantor Agent (kit 1.20.0; v2 di 1.21.0; arah hadap robot di 1.22.0; panel bisa disembunyikan di 1.23.0; karakter robot baru dan kamera pengikut di 1.26.0; pos per departemen di 1.27.0, 2026-09-21)

`/kantor-agent` menjawab pertanyaan yang tak bisa dijawab papan sesi: sesi mana **sedang melakukan apa sekarang**. Papan sesi hanya tahu `tahap`, yang berubah lewat slash command (61 dari 72 sesi aktif masih `mulai`), dan status `aktif`, yang terukur tak bisa dipercaya (72 dari 99 berkas aktif, hanya 7 transkripnya ditulis dalam 10 menit terakhir; keduanya diukur 2026-09-15). Karena itu sumbernya bukan berkas sesi, melainkan **registri sesi Claude Code** (sejak 1.21.0) untuk sesi mana yang terbuka dan apakah ia sedang bekerja, ditambah **ekor transkrip** untuk tool yang sedang dipakai. Desain dan keputusannya: `architecture-draft/.agent-kit/docs/2026-09-15-kantor-agent-design.md` (§ v2 untuk 1.21.0).

**Bentuknya.** Tiap sesi hidup tampil sebagai robot **Lead** di denah kantor isometrik (SVG, tanpa library), dan tiap subagent hidup sebagai robot kecil berperan menurut `agentType` (`general-purpose` Generalis, `Explore` Peneliti, `Plan` Arsitek, agen `loop-*` sesuai perannya, jenis lain dengan nama aslinya).

**Pos per departemen** (sejak **1.27.0**). Denah sebelumnya dibagi per AKTIVITAS dan masing-masing hanya ada satu, sehingga ia tak menjawab pertanyaan pemiliknya: sesi ini sedang mengerjakan sistem **departemen mana**. Sekarang denahnya memuat **9 pos** (HRGA, Marketing, Tech Development, Kesekretariatan, Finance, Procurement, Warehouse, Manufaktur, Quality) ditambah **Umum**, masing-masing ruangan berpintu dengan rak buku, meja, dan papan namanya sendiri. Nama departemennya grounded ke `deptKeyToNames` (`bip-erp/shared-library/common/roles.go`) dengan tiga penggabungan yang dicatat sadar: `Human Resource` + `General Affair` jadi **HRGA** (selaras master data, HRGA memang `supervision_label` keduanya, lihat [[Microservices - Employee Service]]), `Beauty Hacks` + `Kyura` jadi **Marketing**, dan `Legal` + `R&D Regulatory` melebur ke **Kesekretariatan**. `Marketing` dan `Warehouse` sendiri **tak punya key** di peta itu; memasukkannya keputusan kit, bukan turunan dari peta.

Departemen sebuah sesi ditentukan dari **path berkas yang disentuh**, jadi sesi bisa **berpindah pos** di tengah jalan. Potongan path yang ambigu (`services/insentive`, `services/integration`, yang bisa dibaca Finance maupun Marketing) sengaja **tidak dipetakan**: robot yang duduk di pos keliru tak berbunyi apa pun, sementara robot di pos `Umum` menyatakan dirinya sendiri. ⚠️ Ekor transkrip 64 KB **tidak cukup** untuk menentukannya (26 sampai 46 kejadian, dan yang terakhir hampir tak pernah berupa path berkas); diukur atas 8 transkrip hidup, 8 dari 8 jatuh ke `Umum`. Karena itu ada pindai mundur berbatas **4 MB** yang dipanggil hanya bila ekor dan cache tak punya, dan hasilnya diingat. Kedalaman yang benar-benar dibutuhkan terukur 1 MB untuk 6 sesi dan 2 MB untuk 2 sesi, 3 sampai 13 ms.

**Gedungnya** persegi dengan koridor **perempatan** di tengah. Tiap blok berisi tiga ruangan bersekat **kaca** yang semuanya menghadap koridor dengan **satu pintu**, dan pojok terjauh tiap blok jadi **taman dalam**: pojok itu tak dijadikan ruangan karena satu-satunya cara memberinya pintu adalah menembus ruangan tetangganya. **Ruang server menyatu dengan Tech Development** sebagai satu ruangan yang memanjang dua sel (rak server di sel utara, meja kerja di sel selatan), jadi sesi dari pos mana pun yang menjalankan perintah benar-benar berjalan ke sana. Ruang rapat berpintu; **lounge terbuka** dan memanjang dua sel. ⚠️ Isi ruangan dinyatakan dalam koordinat **lokal terhadap pintunya**, dan mukanya dipaksa selalu selatan atau timur: proyeksi ini tak pernah menggambar sisi utara dan barat, jadi aturan "menghadap pintu" yang terdengar wajar justru membuat rak di ruangan berpintu utara kehilangan mukanya sama sekali.

Sejak **1.26.0** robotnya **bulat dan melayang tanpa kaki**, berbadan **putih untuk semua sesi**, dengan visor gelap berisi dua mata dan senyum; perabot sengaja dibiarkan kotak supaya robot menonjol dari latarnya. ⚠️ **Identitas sesi ada di cahaya visor, bukan di badan**: mata dan senyum memakai warna sesi. Dua konsekuensi yang diterima sadar oleh pemilik saat memilihnya: sesi berwarna mirip lebih sulit dibedakan dari jauh, dan badan putih di atas lantai terang menyandarkan pemisahannya pada bayangan di bawahnya. Proyeksi ini hanya memperlihatkan sisi selatan dan timur, jadi robot yang menghadap utara atau barat memang **tanpa wajah**; punggungnya membawa satu indikator kecil berwarna supaya identitasnya tak hilang total.

**Menyorot sebuah sesi memperbesar denah ke robotnya dan mengikutinya berjalan** (1.26.0). Sorotan dipasang lewat kartu di panel samping maupun dengan mengklik robotnya langsung, dilepas lewat **Esc** atau klik lagi, dan selama kamera mengikuti ada petunjuk cara keluarnya di bawah denah. Yang dianimasikan `viewBox`, jadi label dan gelembung ikut membesar; kamera dijepit ke kotak denah supaya robot di pinggir tak memperlihatkan latar kosong.

Robot berjalan lewat koridor ke area sesuai tool yang sedang dipakai. Sejak 1.27.0 rak buku dan meja ada **di dalam ruangan pos sesi itu**, bukan di satu perpustakaan dan satu ruang meja bersama; ruang server, ruang rapat, dan lounge tetap dipakai bersama:

| Tool yang tertunda | Area |
|---|---|
| Read, Grep, Glob, WebFetch, WebSearch, Skill, ToolSearch | Rak buku **di ruangan pos sesi itu** |
| Edit, Write, NotebookEdit; juga saat berpikir di antara tool | Meja **di ruangan pos sesi itu** |
| PowerShell, Bash, Monitor, TaskOutput, TaskStop; tool MCP dan tool tak dikenal; juga saat giliran selesai tetapi tugas shell latar belum selesai | Ruang server, yang **hanya ada di pos Tech Development** |
| Agent, Workflow, SendMessage; juga saat giliran selesai tetapi subagent masih hidup | Ruang rapat |
| AskUserQuestion, ExitPlanMode; juga saat giliran selesai tanpa subagent, atau dialog yang bukan izin | Lounge (menunggu Anda) |

Panel **LEAD HIDUP** di sisi kanan bisa disembunyikan lewat saklar di kanan atas (sejak **1.23.0**), dan denahnya melebar mengisi ruangnya; pilihan itu diingat peramban bila penyimpanannya bisa dipakai. Bilah gulir panel dibuat tipis, terukur 6px lawan 15px bawaan peramban.

Sejak **1.22.0** robot juga menghadap ke arah yang semestinya, dibulatkan ke empat mata angin: duduk menghadap perabot yang dipakainya, berjalan menghadap arah jalannya. Proyeksi isometrik ini hanya memperlihatkan sisi selatan dan timur, jadi robot yang menghadap utara atau barat tampil dari punggung **tanpa wajah**; itu disengaja, dan siapa dia tetap terbaca dari label nama serta warnanya.

Sesi yang **menunggu izin** tetap di area tool yang dimintakan izinnya (Lounge bila tool-nya belum tertulis di transkrip); robotnya bersinar dengan gelembung **!** yang tak pernah diredupkan, karena makin lama ia menunggu makin perlu dilihat.

Dalam satu batch tool paralel, hasil tool singkat sering baru tertulis ke transkrip setelah tool lambat di batch yang sama selesai (diukur atas 25 transkrip), jadi yang menentukan area adalah tool tertunda **paling awal di luar Perpustakaan/Meja**, bukan yang terakhir.

**Cara kerjanya.** `hooks/kantor-agent.py` satu-satunya penulis data, hanya pustaka standar Python. Tiap 2 detik ia membaca registri sesi Claude Code (`~/.claude/sessions/<pid>.json`, format internal, diamati di 2.1.269): sesi = entri yang prosesnya masih hidup (waktu buat proses dicocokkan dengan `procStart`, supaya PID yang didaur ulang tak terbaca hidup) dan `cwd`-nya di dalam workspace; `status` busy/idle/waiting menentukan apakah ia bekerja, dan `waitingFor` menandai dialog yang menunggu Anda. Tool yang sedang dipakai diambil dari ekor transkrip sesi itu (subagent: ≤ 10 menit dan belum `end_turn`). Registri dicocokkan dengan `claude agents --json` (terdokumentasi) tiap 60 detik lewat subprocess yang tak menahan tick; dua ketidakcocokan berturut-turut memasang banner. Registri yang tak terbaca menurunkan penulis ke cara 1.20.0 (transkrip yang ditulis ≤ 30 menit). Tugas shell latar dilacak bertahap per transkrip, bukan dari ekornya: jarak awal tugas ke notifikasi selesainya terukur p90 480 KB dan maks 6,6 MB atas 430 tugas dalam 7 hari, jauh melampaui ekor 64 KB. Tugas yang dihentikan TaskStop (tak pernah mendapat notifikasi) dan tugas milik proses Claude Code yang lama tidak ditunggu. Hasilnya ditulis ke `.task-plans/kantor-agent-data.js` (versi 2) secara atomik. `hooks/kantor-agent.template.html` satu-satunya penulis UI; halaman `.task-plans/kantor-agent.html` memuat ulang data itu lewat `<script>` yang disuntik ulang, yang terbukti membaca isi terbaru di `file://`, dan tiap kartu memuat tombol salin id sesi beserta asal (VS Code/terminal), nama, dan pid. Launcher `hooks/kantor-agent.ps1` / `.sh` mencari Python (venv vault, `py -3`, `python3`) dan tidak menyalakan penulis kedua bila PID yang tercatat masih hidup; penulis sendiri memegang kunci berkas, jadi dua launcher serentak tetap menghasilkan satu penulis. `--berhenti` menghentikannya, dan penulis berhenti sendiri setelah 60 menit tanpa sesi hidup. Data tidak dikirim ke mana pun, beda dari peristiwa `loop-ingest` ke papan tim.

**Tak ada yang senyap.** Penulis mati: banner data basi setelah 10 detik dan robot diredupkan. Format transkrip berubah: banner "perbarui kit", bukan kantor kosong. Python tak ada: launcher exit 2 dan menyebut lokasi yang dicari. Data dari `--sekali`: banner snapshot sekali, bukan penulis mati. Registri tak terbaca, atau dua kali berturut-turut tak cocok dengan `claude agents`: banner. Data versi lain (penulis dari kit lama masih jalan): robot dipulangkan dan banner menyuruh `--berhenti` lalu `/kantor-agent`.

**Terukur.** 1.20.0: tick p95 68,9 ms atas 6 sesi hidup nyata; perubahan transkrip terbaca halaman dalam 0,7 sampai 2,7 detik; penulis tetap hidup setelah panggilan tool yang menyalakannya selesai. 1.21.0, di workspace nyata 2026-09-15: 6 dari 6 sesi di halaman sama dengan `claude agents --json`, termasuk sesi yang diam 6 jam dan tak terlihat dari transkrip; dialog pertanyaan sesi lain tercatat `waiting` + `input needed` dan tampil menunggu Anda; tugas latar sungguhan (`git push` sesi lain yang masih berjalan, dan tugas uji yang awalnya ~100 KB di luar ekor) tampil menunggu tugas latar; dua launcher serentak menghasilkan satu penulis; tombol salin di halaman terpasang mengisi clipboard; tick p50 8 ms, p95 15 ms sesudah tick pertama (tick pertama membaca jendela tugas latar 8 MB per transkrip, p95 tujuh tick awal 423 ms). Test: `tests/test_kantor_agent.py` (**158 test** sejak 1.27.0, dari 110; kontrol mutasi `procStart`, kunci penulis, aturan pelacak tugas latar, dan pindai pos terbukti merah), `tests/test-init.ps1` (registri palsu, dua launcher serentak), dan `tests/kantor-agent-browser.ps1` (manual lewat CDP, **51 check** sejak 1.27.0, dari 46, termasuk clipboard yang dibaca balik). Seperti test kit lain, ketiganya dijalankan manual (catatan 6 di Status).

⛔ **Dua cacat SENYAP di 1.27.0 layak diingat, karena keduanya membuat fitur pos mati total sambil denahnya tetap terlihat wajar.** Pertama, fungsi penyalin field di halaman tidak menyalin `pos`: nilai itu dibaca di dua tempat tetapi tak pernah diisi, jadi SELURUH robot jatuh ke bangku cadangan dan kesembilan ruangan departemen berdiri kosong tanpa satu pun galat. Yang menemukannya uji browser, bukan mata, dan gejalanya sempat dijelaskan keliru sebagai "robotnya masih berjalan". Kedua, ekor transkrip yang terlalu pendek (di atas). ⚠️ Pelajaran ketiga datang dari harness-nya sendiri: **patokan koordinat yang diketik ulang di berkas uji gagal senyap begitu denahnya digeser** — pusat meja rapat tertinggal di koordinat tata letak lama dan menuduh kursi yang sebenarnya sudah benar. Geometri kini dibaca dari halaman lewat `__KANTOR_UJI__.geometri()`, dan baseline `origin/main` diukur lebih dulu (46 check hijau) sebelum kegagalan apa pun dinilai sebagai regresi.

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
- ~~Bentuk gerbang untuk repo selain Node dan Go. Loop sudah dipakai di `mybharata-app`, sementara `pre-push` dan `gerbang.ps1` sama-sama tidak memeriksa apa pun di sana. Belum diputuskan apakah keduanya perlu mengenali Flutter, atau `gerbang.ps1` perlu gagal-tertutup untuk jenis repo yang tak dikenalnya.~~ **Dijawab 2026-09-21** (kit 1.25.0): keduanya, dan `gerbang.ps1` gagal-tertutup lewat jenis repo. Rinciannya di Ruang Lingkup butir 6. ⚠️ Yang **belum** ikut: `pre-push` masih memakai deteksi lamanya sendiri, yaitu Node **ber-`pnpm-lock.yaml` saja** dan Go. Jadi `mybharata-app` (Flutter) serta `guestbook-system` dan `consolidated-accounting-app` (Node ber-npm) baru digerbang di `/judge`, bukan saat push. Menyatukan deteksi itu dengan `gerbang-lib` adalah task tersendiri: `pre-push` ditulis `sh` dan tidak memanggil pustaka gerbang sama sekali, jadi penyatuannya berarti memindahkan cabangnya, bukan menyalin satu baris.
- Menyatukan `gerbang-lib.ps1` dan `gerbang-lib.py` jadi satu implementasi. Utang yang nyata: tiap aturan baru harus mendarat dua kali, dan yang menyimpang diam-diam adalah jalur mac/linux yang jarang dijalankan di sini. Untuk sekarang dijaga test paritas (`tests/test_gerbang.py`), bukan disatukan, karena menyentuhnya berarti menulis ulang jalur tersibuk gerbang.
- Apakah batas otonomi merge (ADR 0077 §1) layak ditinjau ulang sekarang kedua lubang tertutup. Sengaja **tidak** diputuskan bersamaan: yang baru dibangun belum punya jam terbang, dan pertanyaannya baru sah dijawab setelah gerbang ini terbukti menolak sesuatu yang memang pantas ditolak.
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
