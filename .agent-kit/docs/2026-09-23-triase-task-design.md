# Desain — Triase task: keputusan dulu, atau langsung brief

- Tanggal: 2026-09-23
- Status: DRAFT, menunggu review
- Menyentuh: `rules/team-memory.md`, `commands/start-task.md`, `commands/brief.md`, `commands/kerjakan.md`, `VERSION`, `tests/test-init.ps1`
- Tidak menyentuh: judge, gerbang deterministik, pre-commit, pre-push, `/wrap`, kewenangan merge, deploy prod

## 1. Masalah, dengan angkanya

Diukur 2026-09-23. Tiap angka menyebut perintahnya supaya bisa diukur ulang, bukan dipercaya.

| Yang diukur | Angka | Perintah |
|---|---|---|
| PR buatan loop, sepanjang sejarah | 16 (15 merged, 1 closed, 0 open) | `gh search prs --owner bip-itteam-internal "AI Engineering Loop"` |
| PR terbaru 3 repo sebagai pembanding | 548 | `gh pr list --repo ... --state all --limit 200` |
| Umur loop | 17 hari, 0,94 PR/hari, berkelompok | tanggal PR loop pertama 2026-09-06 |
| Artefak `/plan` vs brief, September | 146 vs 26 | `.task-plans/*.md` vs `.task-plans/briefs/*.md` |
| Titik berhenti manusia per task manual | 3 | `/start-task` §5, `/plan` §4, `/wrap` §7 |
| Pertanyaan ke manusia di dalam `/kerjakan` | 0, dari brief sampai PR | `commands/kerjakan.md` |
| Sesi yang tak pernah keluar tahap `mulai` | 155 dari 173 | `.task-plans/sesi/*.json` |

Manusia bukan tertahan di gerbang. PR loop median 30 menit open sampai merge dan nol yang
menggantung; PR tim umumnya median 4,5 sampai 8,9 menit. Manusia tertahan karena **hampir semua
pekerjaan lewat jalur manual**, tempat orang mengetik tiap command dan berhenti tiga kali per
task, sementara jalur yang sudah berjalan tanpa satu pun pertanyaan cuma dipakai untuk 16 PR.

Sebabnya bukan loop-nya lemah. Loop harus **diingat**: task masuk lewat `/start-task` kecuali
seseorang sengaja memilih `/brief`.

## 2. Probe: apa yang sebenarnya muat

20 artefak rencana terbaru (2026-09-18 sampai 09-23) dinilai satu per satu terhadap kriteria
`/brief` yang ditetapkan **sebelum** melihat datanya.

| Putusan | Jumlah |
|---|---|
| Muat jadi brief hari ini | 8 (40%) |
| Sebagian — muat setelah satu keputusan diambil | 8 (40%) |
| Tidak, dan memang tidak seharusnya | 4 (20%) |

**Pembedanya bukan ukuran, melainkan apakah keputusannya sudah diambil.** `komplain-satu-pintu`
(213 baris, dua repo) dan `jejak-keluar-bertanggal` (238 baris, dua repo) **muat**, karena ADR-nya
sudah memutuskan sehingga yang tersisa tinggal "apa yang harus benar".
`reviews-asimetri-channel` (177 baris, satu repo) **tidak muat**, karena intinya justru memutuskan
bagaimana dua angka yang tak sebanding disajikan.

Lintas repo bukan penghalang: `/brief` §2 memang memecahnya jadi dua brief, BE dulu.

Batas probe: 20 dari 232 artefak, semuanya yang terbaru, dan penilaiannya belum dicek orang kedua.

## 3. Keputusan desain

Tiga hal sudah diputuskan bersama pemilik sebelum desain ini ditulis.

1. **Kriteria triase = apakah keputusannya sudah diambil**, bukan ukuran task.
2. **Gerbangnya berbasis keyakinan.** Keputusan tertulis yang bisa ditunjuk → `/kerjakan`
   langsung. Ragu → brief ditampilkan, tunggu persetujuan.
3. **Tempatnya gabungan**: aturan pendek di `team-memory.md` sebagai pemicu universal (menyala
   juga di sesi tanpa slash command, yaitu mayoritasnya), prosedur lengkap sebagai langkah 0 di
   `/start-task`.

## 4. Kriteria triase

Task dialihkan ke brief bila **seluruhnya** benar:

1. **Keputusannya sudah tertulis dan bisa DITUNJUK**: ADR, dok domain vault, atau
   `Workspace/ANALISA - *.md`. "Sudah jelas" tidak cukup — sumbernya harus masuk ke field
   `Sumber` di brief.
2. **Apa yang harus benar bisa dinyatakan tanpa memilih pendekatan.** Brief menyebut hasil, bukan
   cara (`brief.md` §Jangan).
3. **Ada kriteria yang bisa dibuktikan mesin DAN satu yang terlihat di layar** (`brief.md` §5).
4. **Ukuran S per brief.** Lintas repo dipecah, BE dulu (`brief.md` §2, §7). Lintas repo bukan
   diskualifikasi.
5. **Tidak menyentuh uang, sanksi, jatah cuti, atau ambang disiplin** tanpa mengutip
   `mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md` ke Konteks
   (`brief.md` §Jangan).

Task tetap lewat flow manual bila salah satu benar:

- Keputusannya belum ada, dan yang diminta justru memutuskan.
- Program yang menghasilkan beberapa PR berurutan.
- Deploy prod, atau keadaan luar yang hanya manusia bisa sediakan.
- Audit atau riset tanpa kriteria lolos-gagal.

## 5. Tingkat keyakinan dan gerbangnya

| Tingkat | Syarat | Yang terjadi |
|---|---|---|
| `yakin` | Seluruh §4 terpenuhi **dan** sumber keputusan berhasil diresolusi (berkasnya benar-benar ditemukan) | Tulis brief, jalankan `/kerjakan` langsung. Cetak satu baris: `Triase: yakin · dasar <sumber>` |
| `ragu` | §4 terpenuhi tapi sumber tak bisa ditunjuk, atau repo/domain bertanda `(ditebak)` | Tulis brief, **tampilkan**, tunggu persetujuan sebelum `/kerjakan` |
| `tidak` | Ada satu syarat §4 yang gagal | Lanjutkan `/start-task` seperti sekarang |

⛔ **Sumber wajib diresolusi, bukan diingat.** Menyebut nomor ADR dari ingatan tanpa membuka
berkasnya = `ragu`, bukan `yakin`. Ini bukan formalitas: `team-memory.md` § Memori & sumber
kebenaran mencatat empat klaim "X tidak ada" dalam satu sesi yang semuanya lancar, spesifik, dan
salah. Jalur `yakin` melewati manusia, jadi ia satu-satunya tempat klaim palsu tak tertangkap.

Default saat ragu adalah `ragu`, bukan `yakin`. Gagal-tertutup, sama seperti `pre-commit-gate.ps1`.

## 6. Perubahan per berkas

### 6a. `rules/team-memory.md` — blok baru, 5 sampai 8 baris

Di bawah § Skill & tooling AI. Isinya hanya pemicu dan kriterianya dalam satu kalimat, plus
penunjuk ke `/start-task` untuk prosedur lengkapnya. **Jangan menyalin seluruh §4 ke sini**:
berkas ini dibaca tiap sesi, jadi tiap baris dibayar berulang.

Distribusinya cukup `git pull architecture-draft`, tanpa re-run `init`.

### 6b. `commands/start-task.md` — langkah 0 baru

Sebelum langkah 1 (baca CLAUDE.md). Langkah lama bergeser turun. Isinya: jalankan §4, tentukan
tingkat §5, lalu alihkan atau lanjutkan. Bila dialihkan, `/start-task` berhenti di situ dan tidak
memuat arsitektur — memuatnya adalah pekerjaan yang dibuang.

### 6c. `commands/brief.md` — beri arti pada field `Sumber`

Field `Sumber: __SUMBER__` **sudah ada** di `templates/brief.md` tapi tidak disebut sama sekali di
prosedur `brief.md`. Tak perlu field baru; yang kurang artinya. Tambahkan ke langkah 4
(Grounding ringan): `Sumber` diisi ADR/dok/ANALISA yang memutuskan, dan bila tak ada yang bisa
ditunjuk, tulis `tidak ada` — yang otomatis menurunkan triase ke `ragu`.

### 6d. `commands/kerjakan.md` §5 — badan PR menyebut dasarnya

Tambah satu baris di badan PR: `Dasar keputusan: <isi field Sumber>`. Murah, dan ia yang membuat
gerbang merge berhenti jadi klik buta: yang menekan merge bisa membantah premisnya di titik
terakhir. Relevan karena terukur nol `reviewDecision` tercatat pada 634 PR dalam 30 hari.

### 6e. `tests/test-init.ps1` — dua `Check` baru

Pakai helper `Check <bool> <label>` yang sudah ada (lihat baris 74).

- `start-task.md` hasil salin memuat langkah triase.
- `brief.md` hasil salin menyebut `Sumber` beserta aturan turun ke `ragu`.

Test ini menahan kelas kegagalan yang nyata: langkah triase terhapus saat penyuntingan berikutnya
dan tak ada yang berbunyi.

Gerbangnya sungguh ada, diverifikasi 2026-09-23: vault memakai `core.hooksPath` ke
`.claude/hooks/githooks/pre-push`, yang menjalankan test kit **hanya bila push menyentuh
`.agent-kit/` atau `Tools/`** (push dokumentasi biasa keluar seketika; lewati sadar dengan
`AGENTKIT_SKIP_KIT_TESTS=1`). Yang dipanggilnya, `.agent-kit/hooks/gerbang-kit.py`, dibaca relatif
ke repo yang di-push, jadi test baru ikut jalan tanpa re-run `init`.

⚠️ `.git/hooks` milik vault memang kosong. Memeriksa di sana menghasilkan kesimpulan keliru bahwa
tak ada gerbang sama sekali — jebakan yang sudah menggigit saat desain ini ditulis.

### 6f. `commands/kerjakan.md` §3 — log judge mencatat keputusan berikutnya

⚠️ Berkasnya `kerjakan.md`, bukan `judge.md`. Diperiksa 2026-09-23: `/judge` hanya menulis
`<slug>-gerbang.json` dan `<slug>-diff.patch`; yang menulis `.task-plans/judge/<slug>-<n>.json`
adalah `/kerjakan` §3. Menyunting `judge.md` tidak akan berpengaruh apa pun.

Murni instrumentasi, **nol perubahan perilaku**. Tambah satu field ke
`.task-plans/judge/<slug>-<n>.json`: `keputusan_lanjut` bernilai `ulangi`, `berhenti_lolos`, atau
`berhenti_gagal`, ditulis pada saat log itu dibuat.

Kenapa perlu, dan kenapa bentuknya begini. Status akhir sebenarnya **sudah** dicatat — di bagian
`## Hasil` milik brief, ditulis `/kerjakan` §4 atau §6. Diperiksa 2026-09-23 atas tiga brief yang
berhenti: dua menuliskannya dengan benar ("Percobaan 1/3 — gerbang LOLOS, judge GAGAL, loop
DIHENTIKAN lebih awal", lengkap dengan worktree dan branch), satu masih memuat placeholder template
`_(diisi /kerjakan: ...)_`.

Kelemahannya bukan formatnya melainkan **siapa yang menulis**: catatan itu ditulis di akhir run,
jadi run yang terputus di tengah tak meninggalkan apa pun. Log judge ditulis per percobaan oleh
langkah yang sudah pasti jalan. Dengan `keputusan_lanjut`, log percobaan-1 yang berbunyi `ulangi`
tanpa adanya log percobaan-2 **membuktikan** run-nya terputus — itu satu-satunya cara membedakan
"sudah diulang dan tetap gagal" dari "tak pernah sempat diulang", dan tanpa pembedaan itu mutu
pemulihan kesalahan tak bisa dievaluasi sama sekali.

Catatan lapangan yang perlu diperiksa pemilik, bukan diputuskan desain ini: kedua brief di atas
berhenti di percobaan **1 dari 3**, sementara §4 menyuruh mengulang sampai tiga. Entah loop-nya
dihentikan orang, entah §4 tidak diikuti. `keputusan_lanjut` akan membuat perbedaan itu terbaca
sendiri ke depan.

### 6g. `VERSION` → `1.28.0`

Minor: menambah perilaku, tidak mengubah kontrak command yang ada.

## 7. Yang sengaja TIDAK berubah

Supaya ini tidak terbaca sebagai pelemahan gerbang:

- Judge dua lapis utuh. Gerbang deterministik tetap mesin, agen judge tetap read-only, dan agen
  tetap tak berwenang membatalkan gerbang.
- `/kerjakan` tetap berhenti di PR. **Merge tetap manusia** (ADR 0077 §1).
- Deploy prod tetap dijalankan manusia (keputusan 2026-08-14).
- `pre-commit`, `pre-push`, dan gerbang kelengkapan `/wrap` tak disentuh.
- Batas maksimum 3 percobaan per brief tetap.
- Batas "task kecil" di `/brief` **tidak** diperlebar. Yang berubah cuma pintu masuknya.

Usul terpisah yang **dibatalkan** dengan alasan terukur: membuat `/wrap` membuktikan sendiri item
keadaan-luar di dev. `KEADAAN-LUAR` cuma disebut di 5 dari 232 artefak rencana, jadi hasilnya
kecil, sementara ongkosnya nyata dan risikonya bukti lemah yang lolos sebagai terbukti.

## 8. Lubang yang diketahui

**Judge menilai kepatuhan pada brief, bukan kebenaran brief.** Brief yang salah premis
menghasilkan PR rapi yang lolos dua lapis. Tak ada gerbang yang dirancang menangkap ini, dan
triase memperbesar permukaannya karena lebih banyak task lewat sana.

Tiga lapis yang menahannya, tak satu pun sempurna:

1. Gerbang keyakinan §5 — yang tak bisa menunjuk sumber tidak pernah jalan sendiri.
2. `Sumber` wajib diresolusi, sehingga premisnya selalu tertaut ke keputusan yang pernah dibuat
   orang.
3. `Dasar keputusan` di badan PR, supaya premisnya bisa dibantah saat merge.

Ini diterima sadar, bukan diselesaikan. Bila §9 menunjukkan PR loop yang ditutup tanpa merge
meningkat, penyebab pertama yang diperiksa adalah lubang ini.

## 9. Cara mengukur berhasil atau gagal

Ukur ulang 30 hari sesudah dipasang, dengan perintah yang sama seperti §1.

| Metrik | Baseline 2026-09-23 | Arah yang diharapkan |
|---|---|---|
| PR loop per hari | 0,94 | naik |
| Porsi PR yang dibuat loop | 16 dari 548 (≈3%) | naik |
| PR loop closed tanpa merge | 1 dari 16 | **tidak naik** — ini metrik pengamannya |
| Brief `ragu` vs `yakin` | belum ada | dibaca, bukan ditargetkan |
| Loop yang benar-benar habis 3 percobaan vs terputus | tak terbedakan sebelum §6f | dibaca, bukan ditargetkan — ia yang membuat mutu pemulihan bisa dievaluasi nanti |

Bila PR loop naik **dan** closed-tanpa-merge ikut naik, triasenya terlalu berani: perketat §4
nomor 1. Bila hampir semua brief jatuh ke `ragu`, triasenya terlalu penakut dan manusia cuma
dapat satu pertanyaan tambahan tanpa imbalan — itu kegagalan, dan cara membatalkannya di §10.

## 10. Risiko dan cara membatalkan

| Risiko | Gejalanya | Penanganan |
|---|---|---|
| Triase salah merutekan task yang butuh keputusan | PR rapi, premis salah, ketahuan saat merge | Perketat §4.1; turunkan ke `ragu` |
| Gesekan bertambah, bukan berkurang | Hampir semua brief `ragu` | Batalkan, atau hapus jalur `yakin` saja |
| Langkah triase terhapus diam-diam | Tak ada gejala | Ditahan test §6e |
| **Aturan auto-load diabaikan agent** | Task yang muat tetap lewat manual, tanpa satu pun gejala | Tak ada gerbang yang bisa memaksanya — ini batas sadar dari pendekatan berbasis aturan. Hanya terbaca lewat §9: porsi PR loop tak naik |
| Aturan di `team-memory.md` membengkak | Konteks tiap sesi naik | Batas keras 8 baris, prosedur tetap di command |

**Membatalkannya murah**: hapus blok `team-memory.md` dan langkah 0 `start-task.md`, turunkan
`VERSION`. Tak ada data yang bermigrasi, tak ada skema yang berubah, tak ada yang terlanjur
terkirim ke luar.

## 11. Di luar lingkup

- Memperluas batas "task kecil" `/brief`.
- Menambah atau mengubah agen eksekutor.
- Menyentuh **logika** judge, `/wrap`, atau kewenangan merge. (§6f hanya menambah satu field ke
  log yang sudah ditulis; penilaiannya tak berubah sama sekali.)
- Mengotomatiskan merge atau deploy.
- Menyatukan berhenti `/start-task` dan `/plan` — ditolak: berhenti pertama itu justru penjaga
  premis, dan menghapusnya memperbesar lubang §8.
- **Perbaikan dinamis** — percobaan 2 dan 3 memilih peran atau strategi berbeda alih-alih
  mengulang prompt yang sama. Ditunda, bukan ditolak. Tiga alasan: n = 15 brief terlalu kecil
  untuk membuktikan perubahan strategi apa pun (menyetel di atas derau); kalau dipasang
  berbarengan dengan triase, kenaikan PR loop tak bisa dipisahkan sebabnya; dan kebebasan memilih
  strategi memperbesar permukaan mengakali yang justru sedang diburu judge. Tinjau ulang sesudah
  60 sampai 100 brief, dengan `keputusan_lanjut` §6f sudah terkumpul.
- **Membawa serta ringkasan pendekatan yang gagal** ke percobaan berikutnya. Ditunda dengan alasan
  yang sama: ia mengubah perilaku, jadi ia mengacaukan metrik §9 bila dipasang bersamaan.
- **Berhenti lebih awal saat temuan judge berulang.** Ditolak, dan ini diputuskan oleh ukuran,
  bukan selera: diperiksa 2026-09-23 atas kelima brief yang butuh lebih dari satu percobaan,
  temuan percobaan kedua **selalu** di `file:line` berbeda dari percobaan pertama. Sinyal
  "berulang" itu tidak ada, jadi gerbangnya tak akan pernah menyala.
