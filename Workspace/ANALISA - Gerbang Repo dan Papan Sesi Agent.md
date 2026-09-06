# ANALISA - Gerbang Repo dan Papan Sesi Agent

Papan kerja hasil `/analisa-kebutuhan` 2026-09-06. Keputusan dan alasannya di [[ADR - 0077 Otonomi Merge Agent Digerbang Mekanisme yang Bisa Menolak]]; cara kerjanya di [[IT - Gerbang Repo dan Papan Sesi Agent]]. Berkas ini berubah tiap item selesai, jadi jangan dijadikan rujukan arsitektur.

## Ringkas

Usulan aslinya arsitektur multi-agent otonom bertingkat. Yang diterima cuma dua irisan terbawahnya, dengan urutan yang dipilih pemilik proses: **gerbang dulu, papan sesi berikutnya**, sisanya ditolak atau ditunda.

Aturan yang berlaku untuk seluruh daftar ini: **sebuah item baru boleh ditandai selesai bila gerbangnya terbukti pernah MENOLAK sesuatu.** Gerbang yang meloloskan segalanya terlihat persis sama dengan gerbang yang bekerja, dan itu kelas kegagalan yang sudah berulang di tim ini. Tiap item karena itu punya **kontrol negatif** wajib.

## Keadaan 2026-09-06 malam (kit 1.15.0, keputusan pemilik: bangun sesuai dokumen)

Urutan aslinya dibalik oleh keputusan pemilik pada hari yang sama (ADR 0077 § Revisi): seluruh loop dibangun sekaligus sebagai agent-kit 1.15.0, dengan substitusi tercatat. Keadaan per task, diukur saat menutup sesi:

| Task | Keadaan | Bukti |
|---|---|---|
| T1 gerbang pre-commit + matcher PowerShell | **selesai** | `hooks/pre-commit-gate.ps1`; kontrol positif langsung di sesi: commit di `main` repo temp DITOLAK, termasuk bentuk `-C $t` (gagal-tertutup); `tests/test-init.ps1` 44 lulus |
| T2 + T3 pre-push erp-frontend / bip-erp | **selesai, bentuknya berubah** | satu `hooks/githooks/pre-push` di kit, dipasang `init` lewat `core.hooksPath` ke 11 repo sibling (repo kode tidak disentuh); terbukti menyala pada push PR #1739 |
| T4 init memasang hooksPath | **selesai** | `init.ps1`/`init.sh` §7; assertion di test-init |
| T5 kit menundukkan diri sendiri (test kit masuk gerbang vault) | **belum** | vault sengaja tanpa hooksPath; `test-init.ps1` masih dijalankan manual. Butuh keputusan: hook `pre-push` khusus vault yang menjalankan `tests/test-init.ps1` + pytest `Tools/` |
| T6 bump VERSION, sebar, runbook | **selesai** | `VERSION` 1.15.0, README changelog, RUN Onboarding + DEVELOPER GUIDE diperbarui; tim tinggal `git pull` + init + restart |
| T7 + T8 papan sesi (hook + pembaca) | **selesai** | `session-start`/`sesi-sentuh`/`sesi-selesai` + `papan-sesi.ps1` (tabel + HTML); `/papan-sesi` |
| T9 pembersihan sesi basi | **selesai** | `papan-sesi.ps1 -Bersihkan7Hari` |
| T10 rapikan `pr-notification.yml` | **PR terbuka**, merge manusia | bip-erp **#1739**, dikerjakan lewat `/kerjakan` sungguhan: eksekutor → gerbang → judge (lolos, 0 temuan) → PR |
| T11 nomor ADR 0058 ganda | **belum** | butuh keputusan siapa yang dinomori ulang (keduanya sudah tertaut) |
| T12 ekstraksi skill | **dibangun, belum dipakai** | `/ekstrak-skill` + `transkrip-ringkas` + agen `loop-ekstrak-skill`; belum ada draft yang dihasilkan dari sesi nyata |
| T13 baseline test | **selesai** | `baseline/erp-frontend.json` (11.554 test, 37 gagal, `c8993067`) dan `baseline/bip-erp.json` (14.562 test, 14 gagal, `12bd8484`), keduanya 2026-09-06 di worktree `origin/main` bersih |
| Pembersihan 31 worktree merged | **selesai sebagian, yang benar** | 27 dihapus (14 bip-erp + 13 erp-frontend); 3 `owfe-*` dilewati karena punya perubahan belum di-commit; 1 belum merged dan 3 detached dibiarkan. Terdaftar kini 4 + 7 |

Yang masih perlu **restart sesi** untuk terpakai penuh: agen kustom `loop-*` (dibaca saat sesi mulai). Di sesi pembangunnya, `/kerjakan` memakai jalan darurat `general-purpose` dengan definisi agen disisipkan, dan itu dicatat di log judge.

## Fase 1 — Gerbang yang bisa menolak

### T1. Ubah pre-commit dari pengingat jadi gerbang, dan hidupkan di PowerShell

Hook `PreToolUse` sekarang bermatcher `Bash` saja, padahal seluruh git di mesin dev Windows lewat PowerShell, jadi ia tidak pernah menyala. Ia juga `exit 0` tanpa syarat sehingga tidak bisa menolak apa pun.

- Perluas matcher agar mencakup PowerShell.
- Kembalikan penolakan eksplisit, bukan sekadar `additionalContext`.
- Tentukan syarat tolaknya sesempit mungkin dulu, supaya tidak berisik sejak hari pertama.

**Dependensi**: tidak ada. Ini titik masuk paling murah.
**Kontrol negatif**: jalankan `git commit` lewat PowerShell dalam keadaan yang seharusnya ditolak, dan pastikan ia benar-benar tidak jadi commit. Lalu pastikan keadaan normal tetap lolos, supaya bukan gerbang yang menolak segalanya.

### T2. `pre-push` erp-frontend: `tsc --noEmit`, `lint`, `build`

Disimpan sebagai berkas ter-commit di repo (bukan langsung ke `.git/hooks/`, yang tidak ikut ter-clone), diaktifkan lewat `git config core.hooksPath`.

`pnpm test` **tidak** masuk gerbang ini: ia tidak pernah hijau penuh di `main`, jadi memasukkannya berarti gerbang yang selalu merah lalu dimatikan orang. Memasukkannya nanti menuntut baseline pembanding lebih dulu.

**Dependensi**: tidak ada, tapi kerjakan sesudah T1 supaya polanya seragam.
**Kontrol negatif**: buat galat tipe yang disengaja, pastikan push benar-benar ditolak, lalu buang galatnya dan pastikan push lolos.

### T3. `pre-push` bip-erp: `go build ./...`

Pola sama dengan T2. Perhatikan `Makefile` target `test:` bip-erp **bukan** test suite, melainkan `docker compose up --build`, jadi jangan memanggilnya dari hook.

**Dependensi**: T2 (menirukan polanya).
**Kontrol negatif**: sama seperti T2 dengan galat kompilasi.

### T4. `init` mengaktifkan `core.hooksPath` otomatis

Ini item yang menentukan apakah T2 dan T3 berguna bagi tim atau cuma bagi satu mesin. Tanpa ini, gerbangnya mengulang pola disiplin-tanpa-penjaga yang gagal 18 kali di `audit-bharata`.

- `init.ps1` dan `init.sh` menyetel `core.hooksPath` di tiap repo kode yang terdeteksi.
- Tambah assertion di `tests/test-init.ps1` bahwa penyetelan itu benar-benar terjadi.

**Dependensi**: T2, T3.
**Kontrol negatif**: jalankan `init` di sandbox tanpa penyetelan itu dan pastikan test-nya merah pada assertion yang dimaksud, bukan merah karena sebab lain.

### T5. Kit menundukkan dirinya sendiri

`tests/test-init.ps1` dan pytest `Tools/` masuk gerbang lokal vault. Alasannya sudah terbukti: test itu pernah merah beberapa rilis tanpa ada yang tahu.

**Dependensi**: T4.
**Kontrol negatif**: rusakkan satu assertion, pastikan gerbangnya menolak push ke vault.

### T6. Bump `VERSION` kit, sebar, perbarui runbook onboarding

Perubahan hook dan `init` hanya sampai ke tim lewat bump versi lalu `git pull` dan re-init. Tambahkan langkah pengaktifan gerbang ke [[RUN - Onboarding Developer Baru]].

**Dependensi**: T1 sampai T5.
**Kontrol negatif**: di mesin atau sandbox bersih, ikuti runbook apa adanya lalu buktikan gerbangnya menolak. Kalau runbook-nya tidak cukup, yang salah runbook-nya.

## Fase 2 — Papan sesi

### T7. `SessionStart` menulis status sesi ke `.task-plans/`

Satu berkas per sesi berisi branch, task, tahap flow, waktu sentuh terakhir. Hook-nya sudah ada dan sudah menjalankan git, jadi yang ditambah cuma penulisannya.

**Dependensi**: tidak ada teknis, tapi dikerjakan sesudah Fase 1 sesuai urutan yang dipilih pemilik proses.
**Kontrol negatif**: buka dua sesi bersamaan dan pastikan keduanya muncul terpisah, bukan saling menimpa.

### T8. Command pembaca papan sesi

Membaca berkas-berkas T7 jadi satu tabel: sesi, branch, task, tahap, terakhir disentuh.

**Dependensi**: T7.
**Kontrol negatif**: matikan satu sesi lalu pastikan barisnya tetap terbaca sebagai basi, bukan lenyap diam-diam.

### T9. Pembersihan sesi basi

Tanpa ini papan akan penuh sesi mati dalam sepekan dan berhenti dibaca orang, kegagalan yang sama dengan sesi MCP yang menumpuk sampai kedaluwarsa 30 hari di [[Microservices - Vault MCP Service]].

**Dependensi**: T7.

## Fase 3 — Sesudahnya

### T10. Rapikan workflow yang mati tapi berisik

`pr-notification.yml` bip-erp tercatat `active` padahal seluruh isinya dikomentari, sehingga tiap push memicu run gagal 0 detik. Ini bukan gerbang yang rusak, ini kebisingan yang membuat kegagalan sungguhan sulit terlihat. Kecil dan berdiri sendiri, boleh dikerjakan kapan saja.

**Dependensi**: tidak ada.

### T11. Rapikan nomor ADR 0058 yang terpakai dua kali

`ADR - 0058 Kapabilitas AI Digerbang Kelayakan Data, Bukan Kelayakan Teknologi` dan `ADR - 0058 Tiket Engagement Memakai Koleksi dan State Machine Sendiri` memakai nomor yang sama. Wikilink tetap resolve karena memakai judul lengkap, jadi ini bukan kerusakan, tapi penomoran yang tidak unik akan menyesatkan orang berikutnya yang menghitung nomor berikutnya.

**Dependensi**: tidak ada. Perlu keputusan siapa yang dinomori ulang, karena keduanya sudah tertaut dari dokumen lain.

### T12. Ekstraksi skill dari sesi manual

Ditunda, bukan dibuang. Bahan mentahnya sudah menumpuk di `erp/.agents/AGENTS.md` (721 baris, 26 entri ber-`originSessionId`) dan cetakan pipeline-nya sudah terbukti di `Tools/` (daftar-tugas, fan-out subagent, serap).

Sebelum dikerjakan, jawab dulu satu hal yang belum terjawab: mekanisme apa yang menulis `AGENTS.md`, dan apakah ia memang layak dijadikan sumber masukan. Menyambungkan pipeline ke sumber yang belum dipahami akan melahirkan skill yang tidak ada yang bisa pertanggungjawabkan.

**Dependensi**: Fase 1 dan Fase 2.

### T13. Tegakkan baseline test supaya test bisa masuk gerbang

Dasbor sistem rujukan (2026-09-06) menempatkan **E2E tests 288/1.644** sebagai sumber pekerjaan terbesarnya. Artinya bahan bakar loop semacam itu adalah temuan test otomatis, dan di sini bahan bakar itu belum ada: `pnpm test` erp-frontend tidak pernah hijau penuh di `main`, dan `Makefile` bip-erp tidak memanggil `go test`.

Yang dikerjakan bukan "perbaiki semua test", melainkan yang jauh lebih kecil dan lebih menentukan: **tetapkan baseline yang bisa dibandingkan**, yaitu daftar test yang memang merah di `main` beserta tanggalnya, supaya gerbang bisa berbunyi hanya untuk kemunduran baru. Tanpa baseline, test tidak akan pernah bisa masuk gerbang push, dan tanpa itu tidak ada bahan bakar untuk apa pun yang dibangun sesudahnya.

**Dependensi**: Fase 1 (gerbangnya sudah berdiri dulu, baru diisi).
**Kontrol negatif**: perkenalkan satu kegagalan baru dan pastikan gerbang membedakannya dari yang sudah merah sejak baseline.

## Yang TIDAK dikerjakan, supaya tidak diusulkan lagi

- **Orkestrasi eksternal (Trigger.dev dan sejenisnya)** — masalahnya empat sesi di satu mesin, bukan penjadwalan lintas mesin.
- **Judges sebagai agen LLM terpisah** — selama gerbang deterministiknya kosong, penilai probabilistik menaikkan biaya tanpa menaikkan kepastian.
- **Supervisor Agent yang memperbarui skill library sendiri** — tidak ada metrik yang tersedia untuk menilai kualitas skill di sini.
- **Menghidupkan GitHub Actions berbayar** — keputusan pemilik proses 2026-09-06, alasan biaya.
- **Wewenang merge untuk agent** — ditahan, prasyarat pencabutannya ada di ADR §6 Consequences.

Alasan lengkap tiap penolakan ada di [[ADR - 0077 Otonomi Merge Agent Digerbang Mekanisme yang Bisa Menolak]] §6.

## Asumsi yang belum terjawab

Dicatat supaya tidak menyamar jadi fakta di kemudian hari:

- Jumlah dev yang benar-benar memakai kit **belum diukur**. Papan sesi dirancang untuk satu mesin dulu.
- Jalur deploy produksi dari `main` **belum terverifikasi mekanismenya** ([[IT - CI-CD]]). Seluruh keputusan menahan wewenang merge berdiri di atas ini.
- Self-hosted runner diasumsikan tetap tidak tersedia.
- Tidak ada anggaran tambahan (tidak ada GitHub Pro, tidak ada Actions berbayar, tidak ada layanan orkestrasi).
