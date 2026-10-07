> **Status**: ⚠️ **Implemented (ada catatan)**. Berjalan sejak 2026-09-29 di satu PC IT; skrip runner belum masuk repo mana pun (hanya ada di PC itu), jadi belum bisa direplikasi dari git.

## Tujuan

Menjalankan agent Claude Code tanpa ditunggui untuk mengerjakan backlog **Prioritas Low dan Medium** di GitHub Project #15 sampai **PR terbuka**, lalu mengabari grup WhatsApp IT. Merge, deploy, dan status Done tetap di tangan manusia.

## Kapan dipakai

- Menyalakan, menghentikan, atau memeriksa agent backlog otonom.
- Menelusuri kenapa sebuah issue tak kunjung dikerjakan agent, atau kenapa agent berhenti.
- Mereview hasil kerja agent: PR, komentar di issue, dan log bulanan.

## Cara kerja

1. **Pemicu**: Windows Task Scheduler, task `ERP Bharata - Agent Backlog`, tiap jam. Sebuah `run.lock` membuat pemicu yang jatuh saat run masih berjalan langsung keluar, jadi tak pernah ada dua run bersamaan.
2. **Mode terus**: satu run terdiri dari beberapa putaran; tiap putaran menjalankan `claude -p` headless untuk maksimal 3 issue. Selesai satu putaran dan masih ada kandidat, putaran berikutnya langsung mulai. Run berhenti bila kandidat habis, atau bila 2 putaran berturut-turut tak menghasilkan PR (jeda; pemicu jam berikutnya mencoba lagi dan grup IT dikabari).
3. **Kandidat**: item Project #15 berstatus Backlog/Todo, Prioritas Low atau Medium, **berlabel `Siap Agent`**, bukan Jenis Keputusan, tanpa label `Butuh Info`. Issue tanpa label `Siap Agent` tidak disentuh sama sekali (tidak dikerjakan, tidak dikomentari, tidak diberi `Butuh Info`).
   - Gerbang `Siap Agent` dari [[ADR - 0151 Issue Siap Dikerjakan Agent Bila Keputusannya Bisa Ditunjuk, Ditandai Manusia]] diterapkan di skrip (`run.ps1` dan `prompt.md`) sejak 2026-10-07. Diukur hari itu: dari 40 kandidat menurut kriteria lama, 3 yang berlabel `Siap Agent`.
   - **Belum diterapkan di skrip**: antrean ulang hanya lewat pelepasan label `Butuh Info` oleh manusia (skrip masih melepasnya sendiri bila ada komentar manusia sesudah pertanyaan agent), dan pertanyaan yang menyebut `@<Pemutus>`.
4. **Per issue** agent: mengisi field **Mulai** dan **Estimasi Selesai** plus komentar dasar estimasinya, Status In Progress, lalu `/brief` dan `/kerjakan` (worktree, eksekutor `loop-fe`/`loop-be`, gerbang deterministik, `loop-judge`, perbaikan maks 2 kali), PR dengan `Closes bip-itteam-internal/<repo>#<n>`, Status **In Review**, komentar link PR.
   - Spesifikasi tak cukup atau brief `ragu`: komentar berisi pertanyaan, label `Butuh Info`, kembali ke Backlog. Begitu manusia menjawab di issue, agent mengambilnya lagi.
   - Gagal: kembali ke Backlog dengan komentar alasan.
   - **Tindak lanjut PR sendiri (sejak 2026-10-07)**: di awal tiap putaran, sebelum mengambil issue baru, agent menjalankan `.agent-runner\pr-saya.ps1` untuk PR buatannya 14 hari terakhir. Skrip itu satu-satunya penentu apa yang harus dikerjakan:
     - **Review "Changes requested" dari anggota org**: agent merevisi di branch yang sama (gerbang + judge seperti biasa), membalas per butir di PR, dan meminta review ulang. Paling banyak dua putaran revisi per PR; sesudah itu ia menyerahkan ke manusia lewat komentar. Komentar biasa dan review "Comment"/"Approve" **tidak** menggerakkan agent, dan permintaan di luar cakupan issue-nya tidak dikerjakan.
     - **PR merged**: agent membersihkan worktree (`worktree-bersih.ps1`), menghapus tanda "(menunggu merge PR ...)" di dok vault, dan mencatatnya di log. Status issue tidak disentuh.
     - **PR ditutup tanpa merge**: dianggap arahnya ditolak. Agent tidak membuka PR lagi; issue diberi komentar pertanyaan dan label `Butuh Info`, kembali ke Backlog.
     - Yang sudah ditangani dicatat di `.agent-runner\pr-ditangani.json` supaya tidak diulang.
5. **Keterlambatan**: item In Progress milik agent yang lewat Estimasi Selesai mendapat komentar **"Terlambat"** (sebab nyata, estimasi baru) dan satu baris pelajaran. Pelajaran dibaca ulang sebelum estimasi berikutnya. Item milik orang lain tidak dikomentari agent.
6. **Catatan vault**: tiap issue yang disentuh dicatat di log bulanan `LOG - Agent Backlog Otonom <YYYY-MM>`. Bila perilaku yang terdokumentasi berubah, dok terkait diperbarui lewat prosedur `/sync-docs`. Agent hanya commit di vault; **runner** yang mendorongnya ke `main` sesudah putaran, karena izin agent melarang push ke `main`.
7. **Notifikasi**: agent menulis ringkasan PR ke antrean; runner mengirimnya ke grup WhatsApp IT lewat NotifAPI, jalur yang sama dengan [[Microservices - Notification Service]] (kunci dan id grup dibaca dari `.env` bip-erp, tak pernah dicetak). Kiriman gagal tetap di antrean dan dicoba lagi.

## Batas yang dijaga

- Agent berjalan dengan `--permission-mode auto --permission-prompts none`: aksi yang biasanya meminta izin **ditolak**, bukan menunggu manusia.
- Daftar tolak di `settings.local.json` workspace: merge PR, push ke `main`/`master`/`dev`, force push, menutup/menghapus/memindah issue, docker, ssh selain host dev, membaca `.env.deployment`/`.env.production`.
- Gerbang agent-kit tetap berlaku: pre-commit menolak commit di branch utama repo kode, pre-push menjalankan tsc/lint/build atau go build (lihat [[ADR - 0077 Otonomi Merge Agent Digerbang Mekanisme yang Bisa Menolak]]).
- Agent tidak pernah mengisi Status Done, Menunggu Adopsi, atau Canceled (aturan [[ADR - 0143 Backlog Pindah dari Linear ke GitHub Project]]).

## Prasyarat

- PC Windows dengan user yang **tetap login** (layar boleh terkunci), sleep saat terhubung listrik dimatikan.
- Workspace agent-kit (vault + repo kode sebagai sibling) sudah di-`init`, lihat [[RUN - Onboarding Developer Baru]].
- Node 22 + pnpm 10.25, Go, Python 3.12; Docker Desktop (WSL2) untuk menyalakan service bip-erp lokal.
- `gh` login dengan scope `project`; identitas git terisi.
- `.env` dev di `bip-erp` dan `erp-frontend`.

## Langkah

1. Daftarkan jadwal (sekali): `powershell -ExecutionPolicy Bypass -File .agent-runner\daftar-jadwal.ps1`.
2. Menjalankan manual satu issue (uji coba): `powershell -ExecutionPolicy Bypass -File .agent-runner\run.ps1 -HanyaIssue erp-frontend#<n>`.
3. Membatasi PR per hari bila review tim tak mengejar: parameter `-MaksPrPerHari <n>` di aksi task (bawaan 0 = tanpa batas).
4. Menghentikan: `Disable-ScheduledTask -TaskName 'ERP Bharata - Agent Backlog'`; menghapus: `Unregister-ScheduledTask -TaskName 'ERP Bharata - Agent Backlog' -Confirm:$false`.

## Verifikasi

- `.agent-runner\logs\runner.log`: satu baris per putaran (mulai, jumlah PR baru, alasan berhenti).
- `.agent-runner\logs\run-*.log`: ringkasan akhir tiap putaran dari agent.
- Project #15: item agent berpindah Backlog, In Progress, In Review dengan Mulai/Estimasi Selesai terisi.
- Grup WhatsApp IT menerima satu pesan per PR.
- **Agent Live** (`powershell -File .agent-runner\pantau\buka.ps1`, berhenti dengan `-Berhenti`): halaman lokal satu layar yang menampilkan issue yang dikerjakan beserta langkahnya (Brief sampai Merge, termasuk status review PR), planner kalender 14 hari, antrean mesin, dan log runner. Hanya membaca; hanya bisa dibuka di PC runner. Seperti skrip runner, berkasnya belum masuk repo mana pun.

## Bila gagal / Rollback

- **Putaran berakhir tanpa PR dan log berhenti di "sedang berjalan di background"**: agent memakai perintah latar belakang; di mode headless sesi selesai begitu agent berhenti membalas. Prompt runner melarangnya; bila tetap terjadi, lanjutkan sesi yang sama dengan `claude -p --resume <id sesi>` dan instruksi mengerjakan semuanya di foreground.
- **Path worktree ber-spasi ditolak** skrip worktree kit: agent memakai `C:\wt\<slug>`. Catatan untuk kit.
- **Test penuh erp-frontend sekitar 14 menit**, melewati batas 10 menit per perintah; agent menunggunya di sesi yang sama.
- **Run terputus di tengah issue** (kuota Claude habis, mesin mati): issue-nya tertinggal In Progress tanpa PR, dan runner tidak akan melanjutkannya karena hanya mengambil Backlog/Todo. Terjadi 2026-10-03 pada `erp-frontend#1821` dan `#1823`. Periksa item In Progress milik akun agent yang tak punya PR, lalu lanjutkan manual dari worktree-nya di `C:\wt\` (merge `main`, gerbang, judge, PR).
- **Salah arah**: tutup PR-nya (tidak di-merge), kembalikan Status issue manual; agent tidak mengulang issue berstatus selain Backlog/Todo.

## Dokumen Terkait

- [[ADR - 0143 Backlog Pindah dari Linear ke GitHub Project]]
- [[ADR - 0151 Issue Siap Dikerjakan Agent Bila Keputusannya Bisa Ditunjuk, Ditandai Manusia]]
- [[ADR - 0077 Otonomi Merge Agent Digerbang Mekanisme yang Bisa Menolak]]
- [[LOG - Agent Backlog Otonom 2026-09]]
- [[Microservices - Notification Service]]
- [[IT - CI-CD]]
