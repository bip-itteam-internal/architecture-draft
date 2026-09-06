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

3. **Domain**, urutan menang bila lebih dari satu cocok: **fix** (bug, salah, gagal, error,
   tidak muncul, 502, hilang) > **test** (uji, test, coverage, kontrol negatif) > **refactor**
   (rapikan, pisahkan, duplikat, pindahkan) > **docs** (dok, dokumentasi, ADR, README,
   sinkron). Tidak ada yang cocok → satu keputusan klasifikasi olehmu, tandai `(ditebak)`.

4. **Grounding ringan** (maksimal beberapa menit): satu dua `Grep` untuk menemukan `file:line`
   yang relevan, dan bagian `team-memory.md` yang menyangkut area itu. Masukkan ke Konteks.
   Yang tidak ditemukan **tidak ditulis**; Konteks kosong lebih jujur daripada Konteks karangan.

5. **Kriteria lolos**: minimal satu yang bisa dibuktikan **mesin** (test bernama, perintah yang
   harus hijau, `file:line` yang harus berubah) dan minimal satu dari sudut **orang yang
   memakainya** ("di layar X, setelah Y, terlihat Z"). Kriteria "kodenya bagus" ditolak.

6. **Batas**: sebutkan yang TIDAK boleh disentuh. Untuk erp-frontend hampir selalu: komponen
   shared (`FilterTable`, `MainTable`, `ScrollArea`) tidak ditambahi prop demi satu pemanggil.
   Untuk bip-erp: kontrak respons yang sudah dikonsumsi FE/mobile.

7. **Ukuran**: S bila satu eksekutor bisa menyelesaikannya dalam satu putaran; L bila menyentuh
   lebih dari satu repo atau lebih dari satu modul → **pecah**, jangan menulis brief L.

8. Tulis berkas dari `architecture-draft/.agent-kit/templates/brief.md` (ganti semua `__X__`),
   slug kebab-case maksimum 30 karakter. Lalu cetak:

```
Brief: .task-plans/briefs/<tanggal>-<slug>.md
Repo <repo> · Domain <domain> · Ukuran <S/M>
Kriteria: <n> (mesin: <m>)
Berikutnya: /kerjakan .task-plans/briefs/<tanggal>-<slug>.md
```

## Jangan

- Jangan menulis solusi di brief. Brief menyebut **apa yang harus benar**, eksekutor yang
  memutuskan caranya, judge yang menilai.
- Jangan menulis brief untuk yang menyentuh uang, sanksi, jatah cuti, atau ambang disiplin
  tanpa membuka `mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md` dulu dan
  mengutip pasalnya ke Konteks. Potongan mangkir pernah dibangun setengah dari aturannya.
