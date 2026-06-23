%% Dok ini = SOP/prosedur (penjelasan + contoh + langkah). Sumber-kebenaran ATURAN tetap CLAUDE.md di root vault. Bila ada konflik, CLAUDE.md menang. %%

## Deskripsi

*Standard Operating Procedure penulisan dokumentasi di vault ini — supaya tiap agent/manusia menulis dengan struktur, penamaan, dan penautan yang konsisten. Ini versi "cara kerja + contoh" dari rulebook ringkas di root (`CLAUDE.md`); SOP menjelaskannya, bukan menggantinya.*

- **Untuk siapa**: AI agent & kontributor manusia
- **Sumber aturan**: `CLAUDE.md` (root vault) — bila bertentangan, `CLAUDE.md` yang menang
- **Skeleton siap-pakai** (folder `Templates/`): [[Template - Implementasi Service]] · [[Template - Konsep Domain]] · [[Template - Log Operasional]]

## TL;DR — alur 6 langkah

1. **`git pull`** dulu (vault dikerjakan paralel).
2. Tentukan **folder + prefix** (decision-tree §1).
3. Pilih **bentuk dok** → copy template yang sesuai (§2).
4. **Isi** grounded-in-code (belum ada = TBD), tambah **status marker** & **wikilink**.
5. **Verifikasi semua wikilink resolve** (0 broken) + embed gambar ada filenya.
6. **Stage per-file** → commit `docs: ...` → **push**.

## 1. Pilih folder + prefix (decision-tree)

Format nama file **selalu**: `Prefix - Nama.md` — flat, tanpa `/` di nama (pakai `-`, mis. `IT - CI-CD`).

| Isi dokumen | Folder | Prefix |
|---|---|---|
| Service bip-erp (Go) | Core System and Modules | `Microservices -` |
| Gateway / SSO / Orchestrator / shared service | Core System and Modules | `CORE -` |
| Database / skema / koleksi | Core System and Modules | `DB -` |
| Aplikasi FE / mobile / desktop | Application | `APP -` / `BASE -` |
| Konsep bisnis Marketing | Marketing | `Sales -` |
| Konsep bisnis HR | Human Resource Information System | `HRIS -` |
| General Affairs | General Affairs | `GA -` |
| Tech Development / IT ops | Tech Development | `IT -` |
| Warehouse | Warehouse | `WH -` |
| Finance | Finance System | `Finance -` |
| Software pihak ketiga | Third-party Software | `External -` / `Vendor -` |
| Log / korespondensi operasional | Logs | `LOG -` |
| Belum jelas domainnya | Unknown or not listed | (sesuaikan terdekat) |

> Obsidian resolve wikilink lewat **basename** → pindah folder aman; **rename file = perbarui semua wikilink** yang menunjuk nama lama.

## 2. Pilih bentuk dokumen (3 bentuk)

| Bentuk | Untuk | Template | Urutan section |
|---|---|---|---|
| **Implementasi / Service** | dok grounded ke kode (service, gateway, DB, app) | [[Template - Implementasi Service]] | Deskripsi (Stack/Path/Status) → Endpoint/Fitur (Sudah Diimplementasikan) → Belum Diimplementasikan/Catatan → Dependensi & Integrasi → Dokumen Terkait |
| **Konsep / Domain** | konsep bisnis sisi domain (Sales/HRIS/GA/…) | [[Template - Konsep Domain]] | Deskripsi → Latar Belakang → Ruang Lingkup/Cakupan → Konsumen Data → Kendala → Belum Diputuskan (TBD) → Dokumen Terkait |
| **Log Operasional** | artefak point-in-time (korespondensi, access-log, insiden) | [[Template - Log Operasional]] | header Tipe/Tanggal/Konteks → isi point-in-time |

Konsep & implementasi **saling di-link**: konsep di folder domain ↔ implementasi di Core System and Modules. Contoh nyata: [[Sales - Marketplace Integration]] (konsep) ↔ [[Microservices - Integration Service]] (implementasi).

## 3. Aturan inti (wajib)

- **Grounded-in-code** (`CLAUDE.md` §1): tulis hanya yang ada di kode/sumber. Belum ada → **TBD**. Rencana ≠ implementasi → catat gap eksplisit. **Jangan mengarang.**
- **Status marker** di awal dok (`CLAUDE.md` §5): ✅ Implemented · ⚠️ Implemented (ada catatan) · 🟡 Konsep/Draft · 🔴 Stub.
- **Wikilink 0-broken** (`CLAUDE.md` §4): semua `[[...]]` harus resolve sebelum commit; embed gambar harus ada filenya.
- **Bahasa**: Indonesia; istilah teknis tetap English (endpoint, service, request, JWT, dll).
- **Pengecualian**: dok di `Logs/` & file di `Templates/` **dikecualikan** dari grounded/status/template (masing-masing point-in-time record & scaffold).

## 4. Cara pakai template

**Manusia (Obsidian):**
1. Settings → **Templates** → set *Template folder location* = `Templates` (sekali per-vault; config `.obsidian/*` tidak ikut repo).
2. Buat catatan baru dengan nama sudah `Prefix - Nama` → Command palette → *Insert template* → pilih bentuk.
3. Token `{{title}}` / `{{date}}` terisi otomatis; ganti placeholder lain; **hapus blok komentar `%% %%`**.

**Agent:**
1. `Read` file template yang sesuai di `Templates/`.
2. Tulis dok baru: ganti semua placeholder, isi grounded, **hapus komentar `%% %%`**, dan tulis wikilink **tanpa backtick** agar resolve.

## 5. Alur git (`CLAUDE.md` §8–§9)

1. `git pull` (selalu pull sebelum push; vault paralel).
2. Edit/buat dok.
3. **Verifikasi wikilink 0 broken.**
4. **Stage per-file**: `git add -- "Folder/Nama.md"`. **JANGAN `git add -A`.** Jangan commit `.obsidian/*`.
5. Commit ringkas `docs: ...`.
6. Push.

## 6. Checklist pra-commit

- [ ] File di folder benar; nama `Prefix - Nama.md` (tanpa `/`)
- [ ] Bentuk dok sesuai template; komentar `%% %%` sudah dihapus
- [ ] Status marker ada (untuk dok arsitektur)
- [ ] Grounded: tidak ada klaim di luar kode; gap ditandai TBD
- [ ] Semua wikilink resolve (0 broken) + embed gambar ada filenya
- [ ] Konsep ↔ implementasi saling di-link
- [ ] Staged per-file; `.obsidian/*` tidak ikut

## Dokumen Terkait

- [[CLAUDE]] — rulebook ringkas (sumber aturan)
- [[Template - Implementasi Service]] · [[Template - Konsep Domain]] · [[Template - Log Operasional]]
- [[HOMEPAGE]] — peta dokumentasi vault
