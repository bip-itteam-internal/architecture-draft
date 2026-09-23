---
description: Tulis Quick Brief Spec untuk satu task kecil, siap dilempar ke /kerjakan
---

Tulis **Quick Brief Spec** dari teks yang diberikan user, lalu simpan ke
`.task-plans/briefs/<YYYY-MM-DD>-<slug>.md`. Brief adalah kontrak antara user, eksekutor, dan
judge: eksekutor mengerjakan persis yang tertulis, judge menilai persis yang tertulis. Brief yang
kabur menghasilkan loop yang berputar; brief yang jelas menghasilkan PR dalam satu putaran.

Ini **bukan** `/plan`: tidak ada rencana per berkas, tidak ada eksplorasi panjang. Batasi
grounding pada satu dua pencarian yang mengisi bagian Konteks.

## Langkah

1. **Teks kosong** → minta user menulis satu dua kalimat: apa yang salah/ingin ada, dan di mana
   terlihatnya. Jangan menebak dari nol.

2. **Repo**, deterministik dari kata kunci lebih dulu, LLM hanya bila ambigu:
   - `erp-frontend`: halaman, komponen, tsx, tabel, filter, i18n, layar, tombol, dashboard
   - `bip-erp`: service, handler, endpoint, gateway, mongo, koleksi, cron, go, 502, payload
   - `architecture-draft`: dok, dokumentasi, ADR, vault, runbook, status marker
   - `mybharata-app`: mobile, flutter, aplikasi karyawan, absen di HP
   Bila cocok lebih dari satu (mis. kontrak BE + layar FE) → **dua brief**, BE dulu, dengan
   catatan urutan deploy di bagian Batas. Bila tidak ada yang cocok → pilih yang paling mungkin
   dan tulis `(ditebak)` di sebelahnya.

2b. **Paralel**, isi field `Paralel` di tiap brief. Nilai `aman` hanya bila repo-nya berbeda DAN
   pekerjaannya tidak saling menunggu. **Ragu berarti `tidak`**, karena salahnya senyap: FE bisa
   merged lebih dulu lalu layarnya patah di produksi sementara seluruh gerbang hijau.
   Bila dua brief menyentuh **satu endpoint yang sama**, tulis bagian `## Kontrak` berisi bentuk
   request dan respons yang disepakati, **identik di kedua brief**; sesudah itu `Paralel: aman`
   sah, karena keduanya membangun terhadap bentuk yang sama. Tanpa blok itu tulis
   `Paralel: tidak (BE dulu, perubahan kontrak)`. Urutan deploy BE sebelum FE tetap berlaku
   apa pun isi field ini: yang diparalelkan waktu mengetik, bukan waktu deploy.

3. **Domain**, urutan menang bila lebih dari satu cocok: **fix** (bug, salah, gagal, error,
   tidak muncul, 502, hilang) > **test** (uji, test, coverage, kontrol negatif) > **refactor**
   (rapikan, pisahkan, duplikat, pindahkan) > **docs** (dok, dokumentasi, ADR, README,
   sinkron). Tidak ada yang cocok → satu keputusan klasifikasi olehmu, tandai `(ditebak)`.

4. **Grounding ringan** (maksimal beberapa menit): pakai `codebase-memory-mcp`
   (`search_graph`/`trace_path`/`get_code_snippet`) **lebih dulu**, bukan `Grep` polos — bedanya
   bukan gaya, tapi pertanyaan yang bisa dijawab: `Grep` menemukan `file:line`, `trace_path`
   menjawab **konsumen lain** yang memegang fakta yang sama (§ SATU FAKTA SATU TEMPAT). Masukkan
   `file:line` **dan** konsumen lain itu ke Konteks. **Tulis satu baris status kesegaran graf**
   (segar, atau basi/berapa commit tertinggal dari `origin/main`) — grafnya di-index dari working
   tree, jadi ia bisa menjawab tentang kode berbulan lalu dengan percaya diri tanpa berbunyi.
   Graf basi, belum ter-index, atau MCP-nya mati **bukan alasan berhenti**: lanjutkan dengan
   `git grep` seperti biasa, asal ketidaksegarannya **ditulis** di Konteks, bukan didiamkan.
   Tambahkan juga bagian `team-memory.md` yang menyangkut area itu. Yang tidak ditemukan
   **tidak ditulis**; Konteks kosong lebih jujur daripada Konteks karangan.

4b. **`Sumber`** — field ini sudah ada di template dan selama ini tak pernah diisi berarti. Isi
   dengan ADR, dok domain vault, atau `Workspace/ANALISA - *.md` yang **memutuskan** hal ini, dan
   **buka berkasnya** untuk membuktikan ia ada. Tak ada yang bisa ditunjuk → tulis `tidak ada`.

   `Sumber` kosong, `tidak ada`, atau disebut dari ingatan tanpa dibuka → triase turun ke `ragu`:
   brief tetap ditulis, tetapi **ditampilkan ke user dan menunggu persetujuan** sebelum
   `/kerjakan`. Jalur `yakin` melewati manusia sepenuhnya, jadi ia satu-satunya tempat sumber
   karangan tidak akan tertangkap siapa pun.

5. **Kriteria lolos**: minimal satu yang bisa dibuktikan **mesin** (test bernama, perintah yang
   harus hijau, `file:line` yang harus berubah) dan minimal satu dari sudut **orang yang
   memakainya** ("di layar X, setelah Y, terlihat Z"). Kriteria "kodenya bagus" ditolak.

6. **Batas**: sebutkan yang TIDAK boleh disentuh. Untuk erp-frontend hampir selalu: komponen
   shared (`FilterTable`, `MainTable`, `ScrollArea`) tidak ditambahi prop demi satu pemanggil.
   Untuk bip-erp: kontrak respons yang sudah dikonsumsi FE/mobile.

7. **Ukuran**: S bila satu eksekutor bisa menyelesaikannya dalam satu putaran; L bila menyentuh
   lebih dari satu repo atau lebih dari satu modul → **pecah**, jangan menulis brief L.

8. Tulis berkas dari `architecture-draft/.agent-kit/templates/brief.md` (ganti semua `__X__`),
   slug kebab-case maksimum 30 karakter. Kirim ke papan tim (best-effort, no-op bila mesin ini
   tidak menyalakan ingest; judul TIDAK dikirim, hanya id hash slug, repo, domain):
   ```
   & '.claude/hooks/loop-kirim.ps1' -Jenis brief.dibuat -BriefSlug <slug> -Data '{"repo":"<repo>","domain":"<domain>"}'
   ```
   (panggil **in-process** dengan `&`, bukan `powershell -File`: proses baru melucuti tanda kutip
   di dalam JSON-nya diam-diam; mac/linux: `loop-kirim.sh brief.dibuat '{...}'` dengan id dihitung
   sama)
   Lalu cetak:

```
Brief: .task-plans/briefs/<tanggal>-<slug>.md
Repo <repo> · Domain <domain> · Ukuran <S/M> · Paralel <aman/tidak>
Kriteria: <n> (mesin: <m>)
Berikutnya: /kerjakan .task-plans/briefs/<tanggal>-<slug>.md
```

Bila kamu menulis **dua** brief sekaligus, cetak keduanya lalu satu baris penutup: perintah
paralel `/kerjakan <a> <b>` bila keduanya `Paralel: aman`, atau urutannya bila tidak.

## Jangan

- Jangan menulis solusi di brief. Brief menyebut **apa yang harus benar**, eksekutor yang
  memutuskan caranya, judge yang menilai.
- Jangan menulis brief untuk yang menyentuh uang, sanksi, jatah cuti, atau ambang disiplin
  tanpa membuka `mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md` dulu dan
  mengutip pasalnya ke Konteks. Potongan mangkir pernah dibangun setengah dari aturannya.
