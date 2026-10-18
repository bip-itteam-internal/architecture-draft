---
description: Nilai sebuah worktree terhadap brief — gerbang deterministik (tsc/lint/build/go build, test vs baseline) DAN agen judge read-only (plus judge desain untuk layar erp-frontend); lolos hanya bila semuanya lolos
---

Lapisan **Judges** AI Engineering Loop, lapis-lapis yang **semuanya** harus lolos (lapis ketiga
hanya menyala untuk layar erp-frontend):

1. **Gerbang deterministik** (`gerbang.ps1`): tsc, lint, build, test dibanding baseline untuk repo
   Node; `go build ./...` dan `go test` per service tersentuh untuk bip-erp. Mesin, bukan opini.
2. **Agen judge** (`loop-judge`, read-only): kepatuhan brief per kriteria, prinsip arsitektur
   (`review-checklist.md` Pass 1), dan solusi nakal (test di-skip, `eslint-disable` baru, `any`,
   kondisi khusus yang cuma memuaskan brief).
3. **Judge desain** (`loop-judge-desain`, read-only), **hanya** untuk diff `erp-frontend` yang
   menyentuh layar: konsistensi terhadap aturan tertulis dan kemudahan pakai, dari diff plus
   tangkapan layar yang diambil skrip (langkah 3b). Temuan kritisnya ikut memblokir.

Agen **tidak berwenang** membatalkan gerbang: gerbang gagal = verdict gagal. Triangulasi ini yang
mencegah "mengakali satu metrik dengan mengorbankan yang lain".

Argumen: `<path worktree>` (bawaan: repo di cwd), `--brief <path>` (bawaan: brief terbaru di
`.task-plans/briefs/` yang slug-nya cocok dengan nama branch), `--tanpa-build`, `--tanpa-test`
(hanya untuk iterasi cepat; verdict-nya dicatat sebagai **tidak lengkap**), `--test-penuh`
(`-TestPenuh`: suite Node penuh walau diff kecil).

**Cakupan test Node (kit 1.40.0)**: bawaannya `vitest related <berkas tersentuh>` (test yang
mengimpor berkas yang berubah, langsung atau lewat rantai impor), dibanding baseline penuh. Suite
penuh otomatis bila lingkungan semua test berubah (`package.json`, lockfile, `tsconfig*`,
`vitest/vite.config*`, setup test), ada berkas sumber terhapus/dipindah, atau lebih dari 150 berkas
tersentuh. Gerbang menulis `cakupan test: <mode> (<alasan>)` di `catatan` dan `cakupan` di gerbang
`test`; sebutkan di verdict. `0 test dijalankan` pada mode related bukan bukti aman: judge menilai
apakah diff itu memang butuh test baru.

## Langkah

1. **Gerbang deterministik**

   ```
   powershell -NoProfile -ExecutionPolicy Bypass -File .claude/hooks/gerbang.ps1 -Path "<wt>" -Keluaran ".task-plans/judge/<slug>-gerbang.json"
   ```
   (mac/linux: `gerbang.sh`). Jalankan dengan **`run_in_background: true`**: sejak kit 1.30.0 tiap
   langkahnya mengantre di belakang run penuh sesi lain, jadi bisa melampaui batas 10 menit tool
   (status "[antre] menunggu ..." tercetak ke stderr; `/papan-sesi` menampilkan pemegangnya). Exit 0 = semua lolos. Tampilkan tabel: nama gerbang, lolos, durasi,
   `gagal_baru` untuk test. Perhatikan `catatan`: **"TIDAK ADA BASELINE"** berarti test tidak
   dibandingkan dengan apa pun; sebutkan itu terang di verdict, jangan diam.

2. **Diff untuk judge**

   ```
   git -C "<wt>" -c core.fsmonitor=false add -N .
   git -C "<wt>" -c core.fsmonitor=false diff $(git -C "<wt>" -c core.fsmonitor=false merge-base origin/main HEAD)
   ```
   `add -N` (intent-to-add) supaya berkas baru ikut tampil di diff; aman karena worktree ini
   terisolasi. Simpan ke `.task-plans/judge/<slug>-diff.patch`. Diff kosong → berhenti: tidak ada
   yang dinilai, katakan begitu.

3. **Agen judge**

   Jalankan **3b(a)** lebih dulu (`layar-lib.py perlu`): hasilnya menentukan isi prompt di sini.
   Dispatch `Agent` `subagent_type: loop-judge`, `run_in_background: false`, prompt berisi path
   absolut: brief, diff, hasil gerbang JSON, worktree, dan
   `architecture-draft/.agent-kit/rules/review-checklist.md`.

   - **Bila judge desain menyala (langkah 3b), `ui-checklist.md` TIDAK dikirim ke `loop-judge`**,
     dan prompt memuat kalimat ini apa adanya:
     ```
     Judge desain menyala: lewati review-checklist.md §F dan §J untuk berkas erp-frontend; i18n tetap kamu nilai.
     ```
     Aturan UI cuma punya satu penilai; dua penilai atas aturan yang sama dengan hasil berbeda
     adalah satu fakta di dua tempat.
   - **Bila judge desain tidak menyala tetapi diff menyentuh berkas layar** (UI mybharata: judge desain
     belum mencakup Flutter), sertakan path `architecture-draft/.agent-kit/rules/ui-checklist.md`
     supaya `loop-judge` menilai kriteria UX di sana — rujuk **path-nya saja**, jangan salin isinya
     ke prompt.
   - Diff yang tak menyentuh layar (brief backend/docs) tidak menyertakannya; mengirimnya tanpa
     syarat membakar konteks judge untuk brief yang tak punya layar sama sekali.

   Ambil JSON di antara
   `<<VERDICT>>` dan `<<END>>`. JSON tidak sah atau penanda tidak ada → `lolos: false`, `catatan:
   "verdict tidak terurai"`; jangan menebak isinya.

3b. **Judge desain** (hanya `erp-frontend` yang menyentuh layar)

   Seluruh keputusan yang tak butuh penilaian (menyala atau tidak, manifest sah atau tidak,
   tangkapan mana yang gagal) diambil `layar-lib.py`, bukan ditimbang ulang di sini. `<n>` = nomor
   percobaan dari `/kerjakan` (bawaan `1` bila dipanggil langsung). `$PY` =
   `architecture-draft/Tools/.venv/Scripts/python.exe`. Semua berkas di bawah `.task-plans/judge/`
   (di luar worktree, jadi tak ikut commit).

   a. **Menyala atau tidak.** Daftar berkas diff (basis = merge-base langkah 2), lalu tanya mesin:
      ```
      git -C "<wt>" -c core.fsmonitor=false diff --name-only <merge-base> | Set-Content -Encoding utf8 .task-plans/judge/<slug>-berkas.txt
      & $PY .claude/hooks/layar-lib.py perlu --repo <repo brief> --berkas-dari .task-plans/judge/<slug>-berkas.txt
      ```
      `"perlu": false` → lewati 3b seluruhnya: `verdict_desain` = `null`, laporan menulis
      `Desain: tidak menyala`. Diff yang hanya mengubah locale, test, atau `lib/` memang tidak
      menyalakannya, begitu pula repo selain `erp-frontend`.
   b. **Manifest layar** `.task-plans/judge/<slug>-layar.json` (ditulis eksekutor, bukan judge):
      ```
      & $PY .claude/hooks/layar-lib.py validasi .task-plans/judge/<slug>-layar.json
      ```
      Exit 0 = sah. Berkas tidak ada, atau exit 1 → **jangan tangkap**; `layar` = `"tidak tersedia:
      manifest tidak ada"` atau `"tidak tersedia: manifest tidak sah: <galat>"`, dan judge desain
      **tetap dijalankan** dari kode saja (`layar_dinilai: false`). Temuan kritis "manifest layar
      tidak ada / tidak sah" (dibebankan ke eksekutor) ditulis **oleh judge desain sendiri** (jenis 4,
      `file` = path manifest, `line` 0); `/judge` tidak menambahkannya lagi supaya tak terhitung dua kali.
   c. **Tangkap** (hanya bila manifest sah, dan **sesudah** langkah 1: skripnya memakai build yang
      ditinggalkan gerbang lewat `pnpm start`). Hapus dulu `.task-plans/judge/<slug>-<n>-layar/`
      bila ada (sisa run lain dengan slug dan nomor yang sama; hanya folder itu, bukan milik
      percobaan lain), supaya PNG lama tak ikut terbaca sebagai tangkapan percobaan ini:
      ```
      powershell -NoProfile -ExecutionPolicy Bypass -File .claude/hooks/tangkap-layar.ps1 -Path "<wt>" -Manifest ".task-plans/judge/<slug>-layar.json" -Keluaran ".task-plans/judge/<slug>-<n>-layar"
      ```
      Jalankan dengan **`run_in_background: true`** (sekitar 15 detik per entri matriks); langkah 3
      boleh dikerjakan selagi menunggu. Exit 0 = `ringkasan.json` tertulis, dan galat apa pun (port
      dipakai, server tak listen, Chrome gagal) ada **di dalamnya**, bukan di exit code. Exit lain →
      `layar` = `"tidak tersedia: tangkap-layar exit <kode>"`, lanjut (d) dari kode saja.
      `--tanpa-build` → tak ada build untuk dinyalakan: lewati (c), `layar` = `"tidak tersedia:
      --tanpa-build"`. Bila `ringkasan.json` ada:
      ```
      & $PY .claude/hooks/layar-lib.py ringkas .task-plans/judge/<slug>-<n>-layar/ringkasan.json --berkas-dari .task-plans/judge/<slug>-berkas.txt | Set-Content -Encoding utf8 .task-plans/judge/<slug>-<n>-layar/ringkas.json
      ```
      Keluarannya `{"rute": [...], "layar_dinilai": bool, "galat": str|null}`. **`galat` bukan
      `null`** = kegagalan global tangkapan (build tak ada, port dipakai, server tak listen, node tak
      ada; `rute` kosong): `layar` = `"tidak tersedia: <galat>"` dan teks yang sama itulah yang
      dikirim ke judge desain di (d), persis seperti cabang manifest gagal di (b). Selain itu
      `layar` = path `ringkasan.json`. `layar_dinilai` **dibaca** dari keluaran ini, tidak
      disimpulkan: ringkasan yang `rute`-nya kosong atau seluruhnya `tangkapan_gagal` = `false`,
      bukan layar bersih. **Tangkapan gagal tidak memblokir**; alasannya (field `layar`) dibawa ke
      verdict, log, dan badan PR.
   d. **Dispatch** `Agent` `subagent_type: loop-judge-desain`, `run_in_background: false`, prompt
      berisi path absolut: brief, diff, `architecture-draft/.agent-kit/rules/ui-checklist.md` (path
      saja, jangan salin isinya), manifest (atau `tidak ada`), `ringkas.json` (atau teks `tidak
      tersedia: <alasan>` dari b/c, termasuk `galat` global), worktree, bantahan eksekutor
      `.task-plans/judge/<slug>-<n>-bantahan.json` (dari `/kerjakan` §4; `kosong` pada percobaan 1
      atau bila berkasnya tak ada), dan verdict desain sebelumnya
      `.task-plans/judge/<slug>-<n-1>-verdict-desain.json` bila ada (temuan yang dibantah dikutip
      persis dari situ).
   e. **Urai** JSON di antara `<<VERDICT_DESAIN>>` dan `<<END>>`, simpan ke
      `.task-plans/judge/<slug>-<n>-verdict-desain.json`. JSON tidak sah atau penanda tidak ada →
      `{"lolos": false, "layar_dinilai": false, "catatan": ["verdict desain tidak terurai"]}`; jangan
      menebak isinya. Verdict yang tak terurai **tetap disebut** di laporan (baris `Desain: gagal`
      dengan alasan `verdict desain tidak terurai`), dan `/kerjakan` §4 mengirimnya balik sebagai
      temuan supaya percobaan itu tidak hangus tanpa jejak. `layar_dinilai` di verdict wajib sama
      dengan keluaran `ringkas` (atau `false` bila `tidak tersedia`); bila beda, nilai mesin yang
      dipakai dan bedanya ditulis di `Catatan`.

4. **Triangulasi dan laporan**

   `lolos = gerbang.lolos AND verdict.lolos AND verdict_desain.lolos` bila judge desain menyala;
   bila tidak menyala, `lolos = gerbang.lolos AND verdict.lolos`. Yang memblokir dari sisi desain
   hanya temuan `kritis` di `verdict_desain`, bukan tangkapan yang gagal. Cetak:

   ```
   JUDGE <slug> — LOLOS | GAGAL
   Gerbang: tsc ✓ 12s · lint ✓ 20s · build ✓ 95s · test ✓ (0 baru, 14 di baseline) 
   Brief: 3/3 kriteria terpenuhi
   Desain: <lolos|gagal|tidak menyala> · layar dinilai <ya|tidak: alasan> · kritis <n>
   Temuan kritis: <n>   informasional: <m>
   <daftar temuan file:line — alasan — saran; temuan judge desain diberi awalan [desain]>
   Catatan: <pertanyaan judge, peringatan baseline, alasan layar tak tertangkap>
   ```

   `Temuan kritis: <n>` menghitung temuan kritis **gabungan** `loop-judge` + judge desain; `kritis
   <n>` di baris `Desain:` adalah bagian judge desain saja (jadi selalu ≤ angka gabungan). Angka
   gabungan yang sama dipakai `temuan_kritis` di `/kerjakan` §3.

   Bila dipanggil langsung oleh manusia (bukan dari `/kerjakan`), tutup dengan langkah berikutnya:
   lolos → "lanjut commit/PR lewat `/kerjakan`" ; gagal → daftar yang harus diperbaiki.

## Jangan

- Jangan memperbaiki kode di sini. Judge menilai; `/kerjakan` yang mengulang eksekutor.
- Jangan menurunkan `kritis` jadi `informasional` supaya lolos. Kalau judge salah, perbaiki
  `review-checklist.md` atau agen `loop-judge`, bukan verdict-nya.
- Jangan menyimpulkan apa pun dari CI GitHub; verifikasi di sini lokal.
- Jangan menulis atau membetulkan manifest layar di sini, dan jangan mengulang tangkapan sampai
  berhasil. Manifest milik eksekutor; tangkapan yang gagal dicatat alasannya, bukan diakali.
