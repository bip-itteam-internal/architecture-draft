# ANALISA - Gerbang Repo dan Papan Sesi Agent

Papan kerja hasil `/analisa-kebutuhan` 2026-09-06. Keputusan dan alasannya di [[ADR - 0077 Otonomi Merge Agent Digerbang Mekanisme yang Bisa Menolak]]; cara kerjanya di [[IT - Gerbang Repo dan Papan Sesi Agent]]. Berkas ini berubah tiap item selesai, jadi jangan dijadikan rujukan arsitektur.

## Ringkas

Usulan aslinya arsitektur multi-agent otonom bertingkat. Yang diterima cuma dua irisan terbawahnya, dengan urutan yang dipilih pemilik proses: **gerbang dulu, papan sesi berikutnya**, sisanya ditolak atau ditunda.

Aturan yang berlaku untuk seluruh daftar ini: **sebuah item baru boleh ditandai selesai bila gerbangnya terbukti pernah MENOLAK sesuatu.** Gerbang yang meloloskan segalanya terlihat persis sama dengan gerbang yang bekerja, dan itu kelas kegagalan yang sudah berulang di tim ini. Tiap item karena itu punya **kontrol negatif** wajib.

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
