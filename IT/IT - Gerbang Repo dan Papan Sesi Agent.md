# IT - Gerbang Repo dan Papan Sesi Agent

## Deskripsi

*AI Engineering Loop di agent-kit: **gerbang lokal** yang menolak commit di branch utama dan push yang gagal pemeriksaan dasar, **papan sesi** yang menunjukkan sesi kerja mana sedang mengerjakan apa, dan **loop otonom** `/brief` → `/kerjakan` yang mengerjakan satu task kecil lewat agen domain, dinilai dua lapis (mesin dan penilai), lalu berhenti di PR. Semuanya hidup di mesin developer, tanpa layanan dan tanpa biaya berjalan di luar langganan Claude. Keputusan, substitusi dari dokumen rujukan, dan batasnya ada di [[ADR - 0077 Otonomi Merge Agent Digerbang Mekanisme yang Bisa Menolak]].*

- **Status**: ⚠️ **Implemented (ada catatan)**, agent-kit **1.15.0**, 2026-09-06. Sumber: `architecture-draft/.agent-kit/` (`agents/`, `commands/`, `hooks/`, `baseline/`), disebar lewat `init` + restart sesi. Catatan: (1) gerbang lokal bisa dilewati `--no-verify`, disadari; (2) papan sesi satu mesin; (3) baseline test diukur sekali pada tanggal ini dan wajib diukur ulang saat `main` bergerak jauh; (4) `/supervise` menulis draft, tidak pernah auto-apply; (5) agent berhenti di PR, merge tetap manusia.

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

1. **Gerbang lapis satu, hook Claude Code.** Mengembalikan penolakan nyata alih-alih mencetak pengingat lalu lolos. Matcher mencakup PowerShell selain Bash.
2. **Gerbang lapis dua, `pre-push` git hook per repo.** Menjalankan pemeriksaan yang benar-benar bisa gagal: `tsc --noEmit`, `lint`, `build` untuk erp-frontend; `go build ./...` untuk bip-erp. Dipilih `pre-push` dan bukan `pre-commit` karena gerbang yang berbunyi tiap beberapa menit akan dimatikan orang dalam sepekan.
3. **Gerbang kit atas dirinya sendiri.** `tests/test-init.ps1` dan pytest `Tools/` ikut dijalankan.
4. **Papan sesi.** Tiap sesi menulis satu berkas status ke `.task-plans/` berisi branch, task, tahap flow, dan waktu sentuh terakhir, ditulis hook `SessionStart` yang sudah ada. Satu command membacanya jadi satu tabel.

5. **Loop otonom** (revisi 2026-09-06). `/brief <masalah>` menulis Quick Brief Spec (`templates/brief.md`: tujuan, kriteria lolos yang bisa diverifikasi, batas). `/kerjakan <brief>`: routing deterministik dari kata kunci (LLM hanya bila ambigu) → `worktree-baru` di path pendek (`~/wt/fe-<slug>`, pola yang sudah dipakai tim) → agen `loop-<domain>` (`sonnet`) mengerjakan tanpa commit → `/judge` → bila gagal, eksekutor diulang dengan temuan judge, maksimum 2 pengulangan → bila lolos: commit conventional, push (kena `pre-push`), `gh pr create`. **Berhenti di PR.** Gagal 3× → worktree dibiarkan, path dan temuan dicetak untuk manusia.
6. **Judges dua lapis.** `/judge` menjalankan `gerbang.ps1` (tsc/lint/build; `go build` per service tersentuh; test dibanding `baseline/<repo>.json`) DAN agen `loop-judge` (`opus`, hanya `Read/Grep/Glob`) yang menilai kepatuhan brief per kriteria, `review-checklist` Pass 1, dan solusi nakal. Lolos hanya bila **keduanya** lolos; agen tidak berwenang membatalkan mesin.
7. **Supervisi dan ekstraksi skill.** `/supervise` → agen `loop-supervisor` (`fable`) membaca brief/verdict/sesi/skill dan menulis laporan + **draft** ke `skills/_draft/`; `/supervise --terapkan <nama>` dijalankan manusia. `/ekstrak-skill` → `transkrip-ringkas` (skrip, menolak bila skema transkrip tidak terurai) → agen `loop-ekstrak-skill` (`fable`) → draft.

**Yang sengaja TIDAK termasuk**

- Layanan orkestrasi eksternal (Trigger.dev), vendor model lain, dashboard web live, agent merge, supervisor auto-apply. Alasan tiap substitusi di ADR bagian Revisi.
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
- **`pnpm test` erp-frontend tidak pernah hijau penuh di `main`**, jadi test tidak bisa dipakai sebagai syarat lolos dalam bentuk mentah. Yang dipakai di gerbang push adalah `tsc`, `lint`, dan `build`; menambahkan test menuntut baseline pembanding lebih dulu.
- **Waktu tunggu push bertambah.** `build` erp-frontend tidak murah. Bila ternyata mengganggu, yang diturunkan adalah cakupannya, bukan sifat menolaknya.

## Batas dengan Papan Aktivitas Developer

[[IT - Papan Aktivitas Developer]] mencatat peristiwa GitHub yang **sudah terjadi** (push, PR, review) lewat webhook, di Cloudflare. Papan sesi mencatat pekerjaan yang **sedang berjalan dan belum menghasilkan peristiwa apa pun**.

Sejak 2026-09-07 (kit 1.17.0 + PR `feat/loop-ingest` di papan), kedua sumber itu **bertemu di papan tim tanpa menghitung ulang angka PR**: hook kit mengirim peristiwa sesi/brief/judge/PR ke `POST /loop/ingest` (opt-in per mesin, best-effort, tanpa judul), dan papan menampilkannya di bagian Loop otonom di samping tabel PR yang sudah ada. Dashboard lokal `/dashboard` tetap dipertahankan sebagai cadangan yang tidak butuh jaringan dan satu-satunya tempat judul brief terlihat. Yang tetap benar: sesi yang macet tanpa commit hanya terlihat lewat jalur sesi ini, bukan lewat webhook GitHub.

## Belum Diputuskan (TBD)

- Apakah papan sesi kelak perlu lintas-mesin. Sekarang dirancang untuk satu mesin, karena jumlah dev yang benar-benar memakai kit belum diukur.
- Apakah keluaran papan sesi layak disalurkan ke [[IT - Papan Aktivitas Developer]] sebagai sumber kedua, atau justru harus tetap terpisah agar tidak melahirkan dua angka yang menyimpang.
- Bentuk gerbang untuk repo selain `erp-frontend` dan `bip-erp`.

### Dashboard (kit 1.16.0, 2026-09-07)

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
- Ekstraksi skill dari sesi manual. Bahan mentahnya sudah menumpuk (`erp/.agents/AGENTS.md`, 721 baris, 26 entri ber-`originSessionId`) dan cetakan pipeline-nya sudah terbukti di `Tools/`, tetapi urutannya sesudah gerbang dan papan sesi.

## Dokumen Terkait

- [[ADR - 0077 Otonomi Merge Agent Digerbang Mekanisme yang Bisa Menolak]] — keputusan dan alasannya
- [[IT - CI-CD]] — keadaan pipeline, jalur deploy produksi yang belum terverifikasi
- [[IT - Papan Aktivitas Developer]] — papan peristiwa GitHub, beda lingkup
- [[ADR - 0034 Papan Aktivitas Developer di Luar Arsitektur ERP]] — preseden perkakas developer di luar arsitektur ERP
- [[RUN - Onboarding Developer Baru]] — pemasangan kit
- [[DEVELOPER GUIDE]] — flow wajib per task
- [[IT - SOP Dokumentasi Vault]] — konvensi dokumentasi
