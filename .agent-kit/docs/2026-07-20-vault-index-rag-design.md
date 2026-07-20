# Desain: Vault Index (retrieval untuk `architecture-draft`) — Fase 1

**Tanggal**: 2026-07-20
**Status**: Disetujui, belum diimplementasi
**Ruang lingkup**: Fase 1 saja (manifest + kanal agent). Fase 2 dan 3 punya spec sendiri.

## Latar Belakang

Tiga keluhan memicu desain ini:

1. Tim non-IT (HRD, GA, Finance, QA) sulit menemukan informasi. Mereka tidak membuka Obsidian, tidak tahu dokumen mana yang relevan, dan akhirnya bertanya ke tim IT.
2. Agent AI (`/ask`, `/start-task`) kadang meleset memilih dokumen, karena pencarian keyword saja tidak cukup.
3. Agent membaca terlalu banyak berkas besar untuk menjawab hal kecil (boros token, lambat).

Pertanyaan awalnya "apakah kita butuh RAG". Jawabannya: tidak, bukan RAG klasik.

## Kenapa bukan RAG klasik

Ukuran korpus tidak mendukungnya. Vault berisi **367 berkas markdown**, tapi **149 di antaranya adalah cache Shopee Open API v2** yang di-generate skrip dan dikecualikan dari konvensi vault. Korpus tulisan tangan yang sebenarnya: **219 berkas, 1.443 KB**, sekitar 400 ribu token. Itu muat dalam satu context window Opus 1M, dua kali lipat malah. RAG dirancang untuk korpus yang tidak muat.

Alasan kedua lebih penting. **Chunking merusak struktur yang sudah sengaja dibangun.** Vault punya status marker di kepala dokumen (✅ / ⚠️ / 🟡 / 🔴), template seksi tetap, wikilink antar-dokumen, dan konvensi prefix nama berkas. Potong jadi chunk 500 token, dan chunk berisi "endpoint X sudah jalan" kehilangan marker 🟡 Konsep di kepala dokumen. Agent lalu menjawab bahwa sesuatu sudah diimplementasi padahal masih rencana. Itu melanggar prinsip nomor satu rulebook vault (grounded-in-code).

Alasan ketiga: nama berkas sudah setengah jalan menjadi retrieval. `HRIS - Overtime.md`, `ADR - 0006 Swap Jadwal Same-Department.md`, `API - Notification Service.md`. Sinyalnya kuat dan gratis.

## Pendekatan: Manifest + agentic fetch

Satu berkas index berisi metadata dan ringkasan per dokumen. Agent membaca index, memilih 3 sampai 5 dokumen relevan, lalu membaca dokumen itu **utuh**. Tanpa embedding, tanpa vector store, tanpa chunking.

Jalur naik tetap terbuka: kalau eval membuktikan recall kurang, BM25 (fase 3a) lalu vektor (fase 3b) bisa ditambahkan di atas manifest tanpa membuang apa pun.

### Alternatif yang ditolak

| Pendekatan | Alasan ditolak |
|---|---|
| RAG klasik (chunk + embed + vector store + reranker) | Berat untuk korpus 1,4 MB. Chunking memutus status marker. Perlu pipeline re-index, model embedding di VM, dan dua sistem yang harus sinkron dengan vault yang berubah tiap `/sync-docs`. |
| BM25 / SQLite FTS5 + manifest | Jalan tengah yang valid, tapi belum terbukti perlu. Ditunda ke fase 3a, dipicu oleh angka eval, bukan asumsi. |

## Ruang lingkup korpus

Satu manifest, dua profil konsumen, dibedakan flag `publik` per entri.

| Area | Perkiraan dok | Agent | Manusia (fase 2) |
|---|---|---|---|
| Domain (HRIS, Sales, GA, Finance, Manufacture, QA, WH, Application, Core System and Modules, Third-party Software, Unknown or not listed) | 123 | ya | ya |
| `Decisions/` (ADR) | 23 | ya | ya |
| `Runbooks/` | 8 | ya | ya |
| `Reference/`, `API Reference/` tulisan tangan | 18 | ya | ya |
| Dok meta root (README, HOMEPAGE, ROADMAP, DEVELOPER GUIDE, SCRUM SPECS) | 5 | ya | ya |
| `IT/` | 15 | ya | **tidak** |
| `Workspace/` (Inbox, Meetings) | 14 | ya | **tidak** |
| `Logs/`, `Templates/` | 9 | ya | tidak |
| `Additional documents/` (aset Excalidraw) | 2 | **tidak** | tidak |
| `API Reference/Shopee Open API v2/` | 149 | **tidak** | tidak |

Total korpus ter-index untuk agent: **217 dokumen** (219 berkas dikurangi 2 aset Excalidraw).

### Keputusan: `IT/` dikecualikan utuh dari kanal manusia

Folder `IT/` memuat dokumen dengan kredensial plaintext (`IT - Server, VMs and Databases`, `IT - Monitoring System`). Keberadaan kredensial itu adalah keputusan sadar tim IT dan **bukan** isu yang perlu diperbaiki. Yang menjadi masalah adalah paparan baru: chatbot yang dipakai HRD/GA/Finance bisa menyedot kredensial itu ke jawaban untuk orang yang selama ini tidak punya akses.

Pengecualian dilakukan **per folder, bukan per berkas**. Memilah berkas mana yang mengandung kredensial adalah penilaian berulang yang gampang meleset saat dokumen baru ditambahkan; mengecualikan satu folder adalah aturan yang tidak bisa bocor diam-diam. Kalau nanti `IT - Helpdesk` terbukti sering dibutuhkan staf, promosikan berkas itu lewat frontmatter opt-in eksplisit.

**Default gagal harus menutup**: dokumen di folder yang belum dikenal klasifikasinya mendapat `publik: false`.

### Keputusan: Shopee cache dikecualikan dari keduanya

Isinya referensi endpoint vendor yang dibaca agent lewat path langsung saat mengerjakan integrasi Shopee, bukan lewat pencarian semantik. 149 entri akan mendominasi manifest tanpa memberi nilai.

## Pemfasean

| Fase | Isi | Status |
|---|---|---|
| **1** | Generator manifest, `VAULT-INDEX.json` ter-commit, `/ask` dan `/start-task` diubah membacanya, eval set | **Spec ini** |
| 2 | Kanal manusia: service chat (API + UI + SSO gateway), filter `publik` | Spec terpisah, belum dibuat |
| 3 | BM25 (3a) lalu vektor (3b) | Kondisional, dipicu angka eval fase 1 |

Fase 2 sengaja tidak dispesifikasikan sekarang. Keputusan besarnya (hosting, auth, UI, model penjawab) belum matang, dan mengarangnya sekarang menghasilkan spec yang usang sebelum dieksekusi.

## Arsitektur

Tiga komponen, batas antarmuka jelas, bisa dites terpisah.

```
architecture-draft/
├── VAULT-INDEX.json              # artefak (ter-commit)
├── Tools/
│   ├── build-vault-index.py      # generator
│   ├── eval-questions.yaml       # eval set
│   └── tests/                    # pytest
└── .agent-kit/commands/
    ├── ask.md                    # konsumen
    └── start-task.md             # konsumen
```

| Komponen | Tugas | Bergantung pada |
|---|---|---|
| `build-vault-index.py` | Baca berkas vault, hasilkan `VAULT-INDEX.json` | Berkas vault, Anthropic API |
| `VAULT-INDEX.json` | Kontrak data antara generator dan konsumen | — |
| `ask.md` / `start-task.md` | Pilih dokumen dari manifest, baca utuh, jawab | `VAULT-INDEX.json` |

Konsumen tidak pernah memanggil generator. Generator tidak tahu siapa konsumennya. Satu-satunya kontrak adalah skema JSON di bawah.

## Skema `VAULT-INDEX.json`

Ditaruh di akar vault. Namanya bukan `INDEX.json` karena sudah ada `API Reference/Shopee Open API v2/Index.md` dan dua hal berbeda tidak boleh bernama sama.

```json
{
  "versi_skema": 1,
  "digenerate": "2026-07-20",
  "jumlah_dokumen": 217,
  "dokumen": [
    {
      "path": "Human Resource Information System/HRIS - Overtime.md",
      "judul": "HRIS - Overtime",
      "area": "Human Resource Information System",
      "jenis": "domain",
      "status": "✅ Implemented",
      "publik": true,
      "ringkasan": "Menjawab: bagaimana karyawan mengajukan lembur, siapa yang menyetujui, dan bagaimana upah lembur dihitung. Mencakup alur pengajuan via MyBharata dan aturan batas jam.",
      "kata_kunci": ["lembur", "overtime", "SPL", "upah lembur", "approval", "batas jam"],
      "tautan": ["Microservices - Attendance Service", "APP - MyBharata"],
      "hash": "3f9a1c8e...",
      "ukuran_kb": 7.2
    }
  ],
  "gagal": []
}
```

### Nilai `jenis`

`domain` · `adr` · `api` · `runbook` · `reference` · `meta` · `workspace` · `log` · `template`

### Pembagian: fakta deterministik vs prosa LLM

Ini keputusan desain paling penting dalam spec ini.

| Field | Sumber | Metode |
|---|---|---|
| `path`, `judul`, `ukuran_kb` | Filesystem | Langsung |
| `area` | Path folder | Langsung |
| `jenis` | Prefix nama berkas + folder | Aturan (lihat rulebook vault §3) |
| `publik` | Folder | Allowlist, default `false` |
| `status` | Isi dokumen | Regex marker |
| `tautan` | Isi dokumen | Regex wikilink |
| `hash` | Isi dokumen | SHA-256 |
| **`ringkasan`** | Isi dokumen | **LLM** |
| **`kata_kunci`** | Isi dokumen | **LLM** |

Hanya dua field terakhir yang di-generate LLM. Sisanya deterministik.

Alasannya bukan sekadar efisiensi. Status marker adalah **klaim faktual** tentang apakah sesuatu sudah ada di kode. Kalau LLM menyimpulkan status dari isi dokumen, ia akan sesekali salah, dan agent akan menjawab "sudah diimplementasi" untuk hal yang masih rencana. Regex tidak berhalusinasi. Ini yang menjaga prinsip grounded-in-code tetap utuh.

### Ekstraksi `status`

Dua format yang beredar di vault harus dikenali:

1. Marker di baris awal: `✅ Implemented`, `⚠️ Implemented (ada catatan)`, `🟡 Konsep`, `🔴 Stub`
2. Format `**Status**: ✅ Implemented` (hasil cleanup vault 2026-07-18)

Tidak ditemukan → `"status": null`. Bukan tebakan.

### Ringkasan: apa yang diminta dari LLM

Prompt memaksa ringkasan menjawab **"dokumen ini menjawab pertanyaan apa"**, bukan memadatkan isi. Bedanya besar untuk retrieval:

- Buruk: "Berisi endpoint dan alur lembur."
- Baik: "Menjawab: bagaimana cara mengajukan lembur, siapa yang menyetujui, bagaimana upah lembur dihitung."

Bahasa Indonesia, istilah teknis lazim English dibiarkan English, sesuai aturan vault. `kata_kunci` sengaja campur dua bahasa ("lembur" dan "overtime") karena vault memang campur dan pertanyaan staf memakai bahasa sehari-hari.

## Generator

`architecture-draft/Tools/build-vault-index.py`, Python.

Python dipilih karena vault sudah punya preseden (`setup_shopee.py` di akar, `API Reference/Shopee Open API v2/Tools/*.py`) dan folder `Tools/` per-area sudah jadi konvensi. Vault bukan repo JS, jadi aturan pnpm tim tidak berlaku di sini.

### Antarmuka

```
python Tools/build-vault-index.py            # incremental (default)
python Tools/build-vault-index.py --full     # regen semua, abaikan hash
python Tools/build-vault-index.py --check    # exit 1 kalau index basi, tanpa menulis
```

`--check` dipanggil di akhir `/sync-docs`. Index basi lebih berbahaya daripada tidak ada index, karena agent akan mempercayai ringkasan yang salah.

### Regenerasi incremental

`hash` adalah SHA-256 isi berkas sumber. Saat regen, LLM hanya dipanggil untuk dokumen yang hash-nya berubah atau belum ada di manifest. Untuk perubahan rutin `/sync-docs` yang menyentuh 2 sampai 3 dokumen, biayanya di bawah satu sen dan selesai dalam hitungan detik. Ini juga membuat `VAULT-INDEX.json` layak di-commit: diff-nya kecil dan terbaca.

### Model dan biaya

**Claude Opus 4.8** (`claude-opus-4-8`) via **Batches API** (`client.messages.batches.create`) untuk generate awal. Batches memberi diskon 50 persen dan cocok karena pekerjaan ini tidak sensitif latensi.

| Komponen | Perhitungan |
|---|---|
| Input | ~400 rb token × $5/jt = $2,00 |
| Output | ~33 rb token × $25/jt = $0,82 |
| Subtotal | $2,82 |
| **Via Batches (−50%)** | **~$1,41** |

Sekali jalan penuh. Regen incremental setelahnya praktis gratis. Karena angkanya sekecil ini, tidak ada alasan menurunkan ke model lebih murah: kualitas ringkasan langsung menentukan kualitas retrieval, dan itu satu-satunya hal yang menentukan apakah desain ini berhasil.

Panggilan pakai SDK resmi `anthropic` (Python), bukan raw HTTP.

### Penanganan kasus khusus

| Kasus | Perlakuan |
|---|---|
| Dokumen besar (mis. `Microservices - Integration Service.md`, 139 KB) | Potong: kepala 8 KB + daftar seluruh heading. Ringkasan tingkat dokumen tidak butuh isi lengkap. |
| Dokumen 🔴 Stub | Ringkasan satu baris tanpa panggil LLM. Hemat dan jujur. |
| Dokumen di folder tak dikenal | `publik: false`, `jenis: null`, dilaporkan sebagai peringatan. |

### Penanganan error

- Panggilan LLM gagal setelah retry: entri ditandai `"ringkasan": null`, path masuk array `gagal`, skrip lanjut, ringkasan kegagalan dicetak di akhir, **exit code non-nol**. Tidak ada kegagalan senyap.
- Marker status tidak ditemukan: `"status": null`.
- Berkas tidak terbaca (permission, encoding): masuk `gagal`, skrip lanjut.

## Konsumen: `/ask` dan `/start-task`

Perubahan ditulis di **`architecture-draft/.agent-kit/commands/`**, bukan di `erp/.claude/`. Sesuai gotcha tim: `.claude/` di-generate `init` dan akan tertimpa saat init berikutnya. Konsekuensinya versi kit naik dan tim perlu `git pull architecture-draft` plus re-run `init`.

### Perubahan pada `ask.md`

Langkah 1 dan 2 saat ini berbunyi: buka `architecture-draft/CLAUDE.md` §7 untuk pemetaan repo ke dokumen, lalu baca dokumen vault terkait.

Diganti menjadi: baca `architecture-draft/VAULT-INDEX.json`, pilih 3 sampai 5 dokumen paling relevan berdasarkan `ringkasan` dan `kata_kunci`, baru baca dokumen itu utuh.

**Yang tidak berubah**: tetap read-only, tetap menyebut sumber (wikilink + `file:line`), tetap memakai status marker, tetap jatuh ke kode kalau vault diam atau usang, tetap jujur bilang "tidak ditemukan". Yang berubah hanya **cara menemukan** dokumen, bukan cara menjawab.

### Manifest tidak menggantikan CLAUDE.md §7

Keduanya berbeda sumbu dan agent butuh dua-duanya:

- **§7** memetakan **repo kode ke dokumen** (dari mana kode ini didokumentasikan). Dipakai saat titik awalnya adalah kode.
- **Manifest** memetakan **pertanyaan ke dokumen**. Dipakai saat titik awalnya adalah pertanyaan.

### Degradasi saat manifest tidak tersedia

`VAULT-INDEX.json` rusak, hilang, atau `versi_skema` tidak dikenal: agent kembali ke perilaku lama (grep dan baca berdasarkan §7) dan memberi tahu user bahwa index tidak tersedia. Degradasi, bukan kegagalan.

## Eval

`architecture-draft/Tools/eval-questions.yaml`, 20 sampai 30 pertanyaan nyata:

```yaml
- tanya: "Berapa lama masa evaluasi karyawan PKWT?"
  dok_benar: ["HRIS - Onboarding", "Microservices - Recruitment Service"]
- tanya: "Kenapa tukar shift saya ditolak?"
  dok_benar: ["ADR - 0006 Swap Jadwal Same-Department"]
```

**Metrik**: recall@5. Dari pertanyaan-pertanyaan itu, berapa persen yang dokumen benarnya masuk lima teratas pilihan agent. Diukur sekali setelah manifest jadi.

**Aturan keputusan fase 3**:

| recall@5 | Tindakan |
|---|---|
| ≥ 85% | Berhenti di fase 1. Fase 3 tidak perlu. |
| < 85% | Naik ke fase 3a (BM25 / SQLite FTS5), ukur ulang. |

Ini bukan formalitas. Tanpa angka, keputusan fase 3 jadi tebakan.

**Sumber pertanyaan wajib nyata**, dari tiket dan chat yang pernah masuk ke tim IT. Pertanyaan karangan cenderung memakai kosakata dokumen, dan itu justru menyembunyikan masalah retrieval yang paling nyata: staf bertanya "gaji telat", dokumen menulis "payroll cutoff".

## Testing

TDD untuk bagian deterministik. `pytest` dengan fixture vault mini.

| Yang dites | Kenapa |
|---|---|
| Ekstraksi status marker, empat varian × dua format | Format `**Status**:` mudah terlewat |
| Parsing wikilink, termasuk embed gambar `![[...]]` | Embed bukan tautan dokumen |
| Klasifikasi `jenis` dari prefix + folder | Aturan rulebook §3 |
| Klasifikasi `publik` per folder | Keamanan |
| **Folder tak dikenal → `publik: false`** | **Gagal harus menutup, bukan membuka** |
| Perhitungan hash stabil (idempoten) | Dasar mode incremental |
| Mode incremental: dokumen tak berubah tidak memicu panggilan LLM | Kontrol biaya |
| `--check` exit 1 saat index basi | Gate `/sync-docs` |
| Pemotongan dokumen besar | Batas token |

Bagian LLM **tidak** di-unit-test. Kualitas ringkasan diukur lewat eval set, bukan assertion.

## Kriteria selesai (fase 1)

1. `Tools/build-vault-index.py` jalan dan menghasilkan `VAULT-INDEX.json` untuk 217 dokumen.
2. Semua pytest hijau, termasuk tes default-tertutup untuk folder tak dikenal.
3. `--check` mendeteksi index basi dengan benar.
4. `.agent-kit/commands/ask.md` dan `start-task.md` diperbarui, versi kit dinaikkan.
5. `Tools/eval-questions.yaml` terisi 20+ pertanyaan nyata, recall@5 terukur dan tercatat.
6. Keputusan fase 3 diambil berdasarkan angka itu dan dicatat di dokumen ini.
7. `VAULT-INDEX.json` dan seluruh artefak ter-commit ke `architecture-draft`.

## Di luar ruang lingkup

- Kanal chat untuk manusia (fase 2)
- BM25, embedding, vector store, reranker (fase 3, kondisional)
- RBAC per-user dari `system_roles` (dipertimbangkan, ditolak untuk fase 1 karena allowlist folder sudah cukup dan jauh lebih sederhana)
- Meng-index cache Shopee Open API v2
- Mengubah isi dokumen vault mana pun
