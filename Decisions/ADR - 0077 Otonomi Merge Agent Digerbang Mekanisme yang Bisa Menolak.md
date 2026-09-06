# ADR - 0077 Otonomi Merge Agent Digerbang Mekanisme yang Bisa Menolak

## Untuk Manajemen

- **Yang berubah di layar**: tidak ada. Keputusan ini tidak menyentuh satu pun layar ERP dan tidak terlihat oleh karyawan. Yang berubah adalah cara kerja di dalam repo: mulai sekarang ada langkah otomatis yang bisa **menolak** sebuah penyimpanan perubahan bila pemeriksaan dasarnya belum dijalankan, dan ada satu papan yang menunjukkan sesi kerja mana sedang mengerjakan apa.
- **Siapa terdampak**: developer dan siapa pun yang menjalankan asisten AI di workspace ini. Pengguna ERP tidak terdampak sama sekali, dan produksi tidak tersentuh.
- **Tidak dijanjikan**: keputusan ini **tidak** membuat asisten AI bekerja sendiri tanpa diawasi, dan justru **menunda** kemampuan itu sampai ada yang bisa menahannya. Ia juga **tidak** menghidupkan kembali pemeriksaan otomatis di GitHub, karena itu menuntut biaya yang tidak dianggarkan dan paket akun yang sekarang tidak mengizinkannya. Yang dipasang adalah pemeriksaan di komputer masing-masing, yang secara sadar **masih bisa dilewati** oleh orang yang memang bermaksud melewatinya. Ia menahan kelalaian, bukan niat. Dan ia **tidak** menjanjikan review kode mulai berjalan; itu masalah orang, bukan masalah alat.
- **Besaran kerja**: kecil. Sebagian besar bahannya sudah ada dan tinggal diubah dari pengingat menjadi penolak. Tidak ada server baru, tidak ada langganan baru, tidak ada biaya berjalan.

## Deskripsi

*Usulan mengadopsi arsitektur multi-agent otonom bertingkat (lapisan eksekusi, Judges, Supervisor, orkestrasi, dashboard) ditolak untuk sekarang. Yang diputuskan sebagai gantinya adalah memasang lebih dulu satu hal yang selama ini tidak dimiliki rantai kerja ini sama sekali, yaitu mekanisme yang benar-benar bisa mengatakan tidak. Wewenang merge oleh agent ditahan sampai gerbang itu berdiri, karena `main` pernah terbukti mendarat di produksi lewat jalur yang sampai hari ini belum terverifikasi.*

- **Status**: 🟡 **Diusulkan**, 2026-09-06, kode belum ada. Berdiri di atas pengukuran langsung ke GitHub API, isi repo, dan isi agent-kit pada tanggal yang sama.
- **Path di repo**: `architecture-draft/.agent-kit/hooks/pre-commit-reminder.ps1` · `architecture-draft/.agent-kit/hooks/session-start.ps1` · `architecture-draft/.agent-kit/init.ps1` · `architecture-draft/.agent-kit/init.sh` · `architecture-draft/.agent-kit/commands/papan-sesi.md` (baru) · `erp-frontend/scripts/githooks/pre-push` (baru) · `bip-erp/scripts/githooks/pre-push` (baru)
- **Tanggal**: 2026-09-06

## Context

### Yang diusulkan bukan yang dibutuhkan

Usulan datang sebagai dokumen arsitektur bernama *AI Engineering Loop System*, dengan tujuan yang dinyatakan sendiri sebagai *"skalabilitas setara puluhan tim engineering 24/7 dengan SDM minimal"*. Wawancara dengan pemilik proses pada 2026-09-06 menghasilkan masalah yang jauh lebih kecil dan jauh lebih spesifik: **lebih dari empat sesi kerja berjalan bersamaan di satu mesin, dan jejaknya hilang, yaitu sesi mana sedang mengerjakan apa.**

Arsitektur yang diusulkan berukuran untuk masalah yang berbeda. Menerimanya apa adanya akan menghasilkan sistem yang benar secara teknis untuk masalah yang belum dimiliki, sambil membiarkan masalah yang dimiliki tetap terbuka.

### Gerbang otomatisnya kosong, dan itu terukur

Pemilik proses menyatakan agent boleh melaju sampai merge *"kalau gerbang lolos"*. Pengukuran 2026-09-06 menunjukkan tidak ada gerbang yang bisa lolos maupun gagal:

| Yang diperiksa | Hasil terukur |
|---|---|
| `ci.yml` erp-frontend | `disabled_manually`. Run terakhir 2026-08-13 tidak sempat jalan: *"The job was not started because recent account payments have failed or your spending limit needs to be increased"* |
| `deploy.yml` bip-erp | `disabled_manually` |
| `pr-notification.yml` bip-erp | tercatat `active`, tetapi seluruh isinya dikomentari, sehingga tiap push memicu run gagal 0 detik |
| Branch protection `main`, kedua repo | `protected: false`. Endpoint proteksi 404 di keduanya |
| Rulesets, kedua repo | 403 `"Upgrade to GitHub Pro or make this repository public to enable this feature"` |
| Hook git lokal, kedua repo | nol berkas aktif di `.git/hooks/` selain `.sample`; tidak ada husky |
| Target `test:` Makefile bip-erp | bukan `go test`, melainkan `docker compose up --build` |

Di agent-kit sendiri keadaannya sejenis. Kelima berkas `rules/` adalah prosa instruksi, bukan skrip. `wrap-completion-gate.md` menuliskan *"BERHENTI. Jangan commit"*, tetapi tidak ada apa pun yang mencegah commit tetap berjalan. Kedua hook yang terpasang selalu `exit 0` dan tidak pernah mengembalikan penolakan. Satu-satunya gerbang di seluruh kit yang benar-benar punya exit code adalah `build-vault-index.py --check`, dan lingkupnya cuma kesegaran indeks dokumentasi.

Dua cacat kecil memperjelas polanya. Pertama, hook `PreToolUse` dipasang dengan `"matcher": "Bash"`, sementara di mesin dev Windows ini seluruh git dijalankan lewat PowerShell karena Bash praktis tidak berfungsi, sehingga satu-satunya pengingat pre-commit yang dimiliki tim **tidak pernah menyala di mesin tempat ia paling dibutuhkan**. Kedua, `tests/test-init.ps1` milik kit pernah merah beberapa rilis tanpa ada yang menyadarinya, karena tidak ada `.github/` di `architecture-draft` maupun di `erp/`. Kit yang mengatur disiplin tim ini sendiri tidak tergerbang.

### Merge ke main pernah mendarat di produksi

[[IT - CI-CD]] mencatat, terverifikasi 2026-08-13, bahwa `main` pernah mendarat di produksi lewat jalur **di luar GitHub Actions** yang mekanismenya sampai sekarang ditulis belum terverifikasi, lalu menyimpulkan *"gerbang sebelum merge adalah satu-satunya gerbang"*. Selama kalimat itu belum terbantah, memberi agent wewenang merge secara praktis setara memberinya wewenang deploy produksi, dan itu menabrak aturan mengikat tim bahwa deploy produksi dijalankan manusia (keputusan 2026-08-14).

### Yang membuat ini bukan risiko baru, melainkan risiko yang diperbesar

[[IT - Papan Aktivitas Developer]] sudah mengukur perilaku merge se-organisasi: **38 dari 1.702 PR (2,2%) pernah di-review orang lain, 90% PR di-merge oleh penulisnya sendiri dengan median 2,2 menit sejak dibuka**, dan menyimpulkan *"PR di sini berfungsi sebagai catatan perubahan, bukan gerbang mutu"*. Pengukuran ulang 2026-09-06 atas 20 PR merged terakhir di kedua repo mengembalikan `reviews: []` untuk seluruhnya.

Ini penting supaya keputusan ini tidak dibaca sebagai tuduhan terhadap agent. Manusia di sini sudah merge tanpa review. Yang dilakukan otonomi agent bukan memperkenalkan kelas risiko baru, melainkan **menaikkan lajunya** pada sistem yang sudah tidak punya rem. Karena itu jawabannya bukan melarang agent, melainkan memasang rem lebih dulu.

### Sistem rujukannya berjalan di atas dua hal yang belum dimiliki di sini

Pemilik proses menyerahkan tangkapan layar dasbor sistem aslinya pada 2026-09-06. Angka di bawah **dibaca dari gambar, bukan diukur sendiri**, jadi diperlakukan sebagai indikasi besaran dan bukan sebagai data. Sebagian labelnya terpotong dan sengaja tidak dikutip. Satu ketidakcocokan kecil sudah terlihat di gambar itu sendiri (337 dibuka lawan 323 merge dalam tujuh hari memberi 95,8%, sementara panel merge rate menulis 99%), dan itu justru menguatkan alasan memperlakukannya sebagai indikasi.

**Ongkosnya.** `SPEND 7D $38.244,32` atas `MRG 7D 323`, yaitu **$118,40 per PR merged** dan sekitar **$5.463 per hari**. Bila lajunya bertahan, itu di kisaran $164.000 per bulan. Berapa pun tagihan GitHub Actions yang ditolak pada keputusan yang sama, ia beberapa orde besaran di bawah angka itu. Menyalin arsitektur ini tanpa menyalin anggarannya menghasilkan sistem yang berhenti di tengah.

**Bahan bakarnya.** Panel `SOURCE - MERGED / FOUND` menempatkan **E2E tests di 288/1.644** sebagai sumber pekerjaan terbesar, jauh di atas sumber lain. Artinya mesin itu tidak menghasilkan pekerjaan dari ketiadaan: ia mengubah **temuan test otomatis** menjadi perbaikan. Di sini `pnpm test` erp-frontend tidak pernah hijau penuh di `main`, `Makefile` bip-erp tidak memanggil `go test`, dan seluruh CI mati. Membangun loop-nya lebih dulu berarti membangun loop tanpa bahan bakar.

**Bentuk keluarannya.** Komposisinya **74% Fix, 12% Test, 6% Docs, dan hanya 3% Feature**. Sistem itu mesin perawatan, bukan pabrik fitur. Perlu disebut supaya harapan "setara puluhan tim engineering" tidak dibaca sebagai fitur baru yang datang sendiri.

**Lapisan Judges-nya.** Merge rate yang ditampilkan 99%. Apa pun yang dikerjakan lapisan validasi di sistem itu, pada tahap PR ia praktis tidak menolak apa pun. Ini tidak membuktikan lapisannya tak berguna, tetapi ia melemahkan alasan menyalin lapisan itu lebih dulu.

Ketiganya menunjuk arah yang sama dengan §2: yang perlu berdiri lebih dulu adalah bahan bakarnya, yaitu pemeriksaan otomatis yang benar-benar berjalan dan menghasilkan temuan.

### Batas yang mengunci pilihan

Tiga hal mempersempit ruang solusi, dan ketiganya di luar mandat keputusan ini untuk diubah:

1. **GitHub-hosted Actions tidak boleh diandalkan.** Keputusan pemilik proses 2026-09-06, alasan biaya, konsisten dengan kegagalan billing pada run terakhir.
2. **Branch protection tidak tersedia pada paket akun sekarang** untuk repo privat, dibuktikan balasan 403 yang menawarkan upgrade atau membuka repo.
3. **Self-hosted runner lokasinya tidak diketahui.** [[IT - CI-CD]] mencatat nol proses runner di VPS Biznet dan enumerasi API ditolak.

Konsekuensinya tegas: satu-satunya gerbang yang bisa dipasang tanpa biaya dan tanpa mengubah paket GitHub adalah **gerbang lokal**.

## Decision

### 1. Wewenang merge tidak diberikan sampai ada yang bisa menolak

Agent tidak diberi wewenang merge ke `main` di repo mana pun. Batas otonominya berhenti di **membuka PR**. Keputusan merge tetap tindakan manusia.

Ini bukan penilaian atas kemampuan agent. Ini konsekuensi dari fakta bahwa tidak ada mekanisme apa pun yang bisa membatalkan keputusan itu bila keliru, ditambah fakta bahwa `main` pernah terbukti mendarat di produksi. Prasyarat pencabutannya ditulis di §6 supaya tidak diputuskan ulang secara diam-diam di sesi lain.

### 2. Gerbang dipasang LOKAL, bukan di GitHub

Dua lapis, keduanya tanpa biaya:

- **Hook Claude Code** yang mengembalikan penolakan nyata, bukan mencetak pengingat lalu `exit 0`. Matcher wajib mencakup **PowerShell**, bukan cuma `Bash`, kalau tidak ia mati persis di mesin yang paling memerlukannya.
- **`pre-push` git hook per repo kode** yang menjalankan pemeriksaan yang benar-benar bisa gagal: `tsc --noEmit`, `lint`, dan `build` untuk erp-frontend; `go build ./...` untuk bip-erp.

Alasan memilih `pre-push` dan bukan `pre-commit`: commit sering dan murah, push jarang dan mahal untuk dibatalkan. Gerbang yang berbunyi tiap beberapa menit akan dimatikan orang dalam sepekan, dan gerbang yang dimatikan lebih buruk daripada gerbang yang tidak pernah ada karena ia meninggalkan keyakinan palsu bahwa ada yang menjaga.

### 3. Gerbangnya wajib punya exit code, bukan kalimat

Sebuah aturan dianggap gerbang hanya bila ada proses yang keluar dengan status bukan nol, atau hook yang mengembalikan penolakan eksplisit. Kalimat "BERHENTI" di dalam berkas prosa **bukan gerbang**, dan tidak boleh dihitung sebagai gerbang dalam dokumen mana pun sesudah ini.

Konsekuensi langsungnya, `wrap-completion-gate.md` dan `review-checklist.md` tetap berharga tetapi turun kelas namanya menjadi **checklist**, bukan gerbang. Keduanya dibiarkan sebagaimana adanya, karena nilainya nyata dan sudah terbukti: [[Microservices - Vault MCP Service]] mencatat PR yang merge sebelum `/review` sempat jalan, lalu reviewnya menemukan tiga celah keamanan yang lolos 74 test hijau.

### 4. Test milik agent-kit ikut digerbang

`tests/test-init.ps1` dan pytest `Tools/` dijalankan sebagai bagian dari gerbang lokal vault. Alasannya sudah terbukti sendiri: test itu pernah merah beberapa rilis tanpa terdeteksi. Kit yang menuntut disiplin dari orang lain tanpa menundukkan dirinya sendiri pada disiplin yang sama tidak akan dipercaya lama.

### 5. Papan sesi berupa berkas, bukan layanan

Kebutuhan asli, yaitu melihat sesi mana mengerjakan apa, dijawab dengan tiap sesi menuliskan satu berkas status ke `.task-plans/` (branch, task, tahap flow, waktu sentuh terakhir), ditulis oleh hook `SessionStart` yang sudah ada, ditambah satu command yang membacanya menjadi satu tabel.

Tanpa layanan, tanpa basis data, tanpa dashboard. Alasannya bukan hemat, melainkan bahwa papan yang menuntut layanan hidup akan ikut mati saat layanannya mati, dan satu-satunya saat orang membutuhkan papan ini adalah saat keadaan sedang kacau.

**Ini BUKAN duplikat [[IT - Papan Aktivitas Developer]] dan tidak boleh digabungkan ke sana.** Papan itu mencatat peristiwa GitHub yang **sudah terjadi** (push, PR, review) lewat webhook. Papan sesi mencatat pekerjaan yang **sedang berjalan dan belum menghasilkan peristiwa apa pun**. Keduanya tidak bisa saling menggantikan: sesi yang macet tiga jam tanpa satu commit pun tidak akan pernah muncul di papan aktivitas.

### 6. Yang TIDAK dibangun, beserta alasannya

- **Orkestrasi eksternal (Trigger.dev atau sejenisnya)**: ditolak. Masalahnya empat sesi di satu mesin, bukan penjadwalan lintas mesin. Menambah layanan berarti menambah yang bisa mati.
- **Judges sebagai agen LLM terpisah**: ditolak untuk sekarang. Selama gerbang deterministiknya kosong, menambahkan penilai probabilistik menaikkan biaya tanpa menaikkan kepastian. Pertimbangkan ulang setelah §2 berdiri.
- **Supervisor Agent yang memperbarui skill library sendiri**: ditolak. Ia menuntut kemampuan menilai kualitas skill, dan tidak ada metrik yang tersedia untuk itu di sini. `pnpm test` erp-frontend tidak pernah hijau penuh di `main`, jadi metrik lolos-test tidak bisa dipakai mentah sebagai umpan balik.
- **Triangulated Metrics berbasis test pass rate**: ditolak dalam bentuk mentah, alasan sama.

### 7. Skill extraction ditunda, bukan dibuang

Ekstraksi skill dari sesi manual adalah bagian paling matang dari usulan aslinya dan bahan mentahnya sudah menumpuk: `erp/.agents/AGENTS.md` memuat 721 baris dengan 26 entri ber-`originSessionId`, dan `Tools/` sudah menyediakan cetakan pipeline yang terbukti, yaitu daftar-tugas lalu fan-out subagent lalu serap. Ia dikerjakan **sesudah** §2 dan §5, bukan sebagai gantinya.

## Consequences

**Yang membaik**

- Ada, untuk pertama kalinya, mekanisme di rantai kerja ini yang bisa menolak. Sebelum keputusan ini jumlahnya nol.
- Pengingat pre-commit yang selama ini mati di mesin Windows menjadi hidup, karena matcher-nya diperbaiki.
- Sesi yang macet menjadi terlihat tanpa membuka satu per satu.
- Kit menundukkan dirinya pada disiplin yang ia tuntut dari orang lain.

**Yang tetap terbuka, dan disadari**

- **Gerbang lokal bisa dilewati** dengan `--no-verify`. Ini diterima sadar. Ia menahan kelalaian, bukan niat, dan kelalaian adalah yang benar-benar terjadi di sini.
- **Gerbang lokal hanya hidup di mesin yang memasangnya.** `.git/hooks/` tidak ikut ter-clone, jadi hook wajib disimpan sebagai berkas ter-commit dan diaktifkan lewat `core.hooksPath`, dan pengaktifannya wajib jadi langkah `init`. Tanpa itu, keputusan ini mengulang persis pola "disiplin tanpa penjaga" yang sudah gagal 18 kali berturut-turut di repo `audit-bharata`.
- **Review kode tetap tidak berjalan.** Keputusan ini tidak menyentuhnya sama sekali. Angka 2,2% akan tetap 2,2% sesudah ini, dan itu bukan masalah yang bisa diselesaikan alat.
- **Branch protection tetap tidak ada**, jadi tidak ada apa pun di sisi GitHub yang menahan push langsung ke `main`. Yang menahan hanya konvensi dan gerbang lokal.
- **Jalur deploy produksi tetap belum terverifikasi.** Keputusan ini berdiri di atas kalimat [[IT - CI-CD]] yang sendirinya menandai dirinya belum terverifikasi. Bila kelak terbukti `main` **tidak** mendarat di produksi, prasyarat di §1 layak ditinjau ulang, dan peninjauan itu wajib lewat ADR baru, bukan lewat kesimpulan sesi.

**Prasyarat mencabut §1**

Wewenang merge oleh agent baru layak dibahas ulang bila ketiganya terpenuhi sekaligus: gerbang §2 berdiri dan terbukti pernah menolak sesuatu yang nyata; jalur deploy produksi terverifikasi mekanismenya; dan ada cara membatalkan merge yang salah tanpa menunggu manusia. Selama salah satunya belum, §1 berlaku.

**Deploy**

Tidak ada. Tidak ada service baru, tidak ada env baru, tidak ada kategori inbox baru, tidak ada perubahan kontrak backend maupun frontend, dan produksi tidak tersentuh. Yang berubah hanya `.agent-kit/` di vault dan `.claude/` hasil re-init, sehingga penyebarannya lewat bump `VERSION` lalu tim `git pull` dan re-init, sebagaimana [[RUN - Onboarding Developer Baru]].

## Dokumen Terkait

- [[IT - Gerbang Repo dan Papan Sesi Agent]] — cara kerjanya
- [[IT - CI-CD]] — keadaan pipeline dan jalur deploy produksi
- [[IT - Papan Aktivitas Developer]] — papan peristiwa GitHub, beda lingkup dari papan sesi
- [[ADR - 0034 Papan Aktivitas Developer di Luar Arsitektur ERP]] — preseden perkakas developer di luar arsitektur ERP
- [[ADR - 0058 Kapabilitas AI Digerbang Kelayakan Data, Bukan Kelayakan Teknologi]] — prinsip sejenis, kapabilitas AI digerbang kelayakan, bukan ketersediaan teknologi
- [[RUN - Onboarding Developer Baru]] — jalur penyebaran perubahan kit
- [[DEVELOPER GUIDE]] — flow wajib per task
