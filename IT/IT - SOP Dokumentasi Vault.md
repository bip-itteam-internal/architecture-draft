*Dok ini = SOP/prosedur (penjelasan + contoh + langkah). Sumber-kebenaran ATURAN tetap CLAUDE.md di root vault. Bila ada konflik, CLAUDE.md menang.*

## Deskripsi

*Standard Operating Procedure penulisan dokumentasi di vault ini — supaya tiap agent/manusia menulis dengan struktur, penamaan, dan penautan yang konsisten. Ini versi "cara kerja + contoh" dari rulebook ringkas di root (`CLAUDE.md`); SOP menjelaskannya, bukan menggantinya.*

- **Status**: ✅ Berlaku — SOP aktif; sumber aturan tetap `CLAUDE.md` root.
- **Untuk siapa**: AI agent & kontributor manusia
- **Sumber aturan**: `CLAUDE.md` (root vault) — bila bertentangan, `CLAUDE.md` yang menang
- **Skeleton siap-pakai** (folder `Templates/`): [[Template - Implementasi Service]] · [[Template - Konsep Domain]] · [[Template - Log Operasional]] · [[Template - Runbook]] · [[Template - Persona]] · [[Template - Meeting Note]] · [[Template - Daily Note]]

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
| Konsep bisnis Marketing | Sales | `Sales -` |
| Konsep bisnis HR | Human Resource Information System | `HRIS -` |
| General Affairs | General Affairs | `GA -` |
| Tech Development / IT ops | IT | `IT -` |
| Warehouse | Warehouse | `WH -` |
| Finance | Finance System | `Finance -` |
| Software pihak ketiga | Third-party Software | `External -` / `Vendor -` |
| Log / korespondensi operasional | Logs | `LOG -` |
| QA/RA farmasi (CPOB/BPOM/batch/CAPA/ED) | Quality & Regulatory | `QA -` |
| Glosarium / data dictionary / ownership | Reference | `REF -` |
| Keputusan arsitektur/bisnis (ADR) | Decisions | `ADR -` |
| Daftar endpoint per service | API Reference | `API -` |
| Runbook / how-to / onboarding / troubleshoot | Runbooks | `RUN -` |
| Notulen rapat | Workspace/Meetings | `MTG -` |
| Daily note / idea capture | Workspace/Inbox | (bebas, `YYYY-MM-DD`) |
| Belum jelas domainnya | Unknown or not listed | (sesuaikan terdekat) |

> Obsidian resolve wikilink lewat **basename** → pindah folder aman; **rename file = perbarui semua wikilink** yang menunjuk nama lama.

## 2. Pilih bentuk dokumen (3 bentuk)

| Bentuk | Untuk | Template | Urutan section |
|---|---|---|---|
| **Implementasi / Service** | dok grounded ke kode (service, gateway, DB, app) | [[Template - Implementasi Service]] | Deskripsi (Stack/Path/Status) → Endpoint/Fitur (Sudah Diimplementasikan) → Belum Diimplementasikan/Catatan → Dependensi & Integrasi → Dokumen Terkait |
| **Konsep / Domain** | konsep bisnis sisi domain (Sales/HRIS/GA/…) | [[Template - Konsep Domain]] | Deskripsi → Latar Belakang → Ruang Lingkup/Cakupan → Konsumen Data → Kendala → Belum Diputuskan (TBD) → Dokumen Terkait |
| **Log Operasional** | artefak point-in-time (korespondensi, access-log, insiden) | [[Template - Log Operasional]] | header Tipe/Tanggal/Konteks → isi point-in-time |
| **Runbook** | prosedur operasional non-kode (grounded, di-publish) | [[Template - Runbook]] | Tujuan → Kapan dipakai → Prasyarat → Langkah → Verifikasi → Bila gagal/Rollback → Dokumen Terkait |
| **Persona / Pengguna** | siapa pemakai fitur (alur banyak-aktor kompleks) | [[Template - Persona]] | Aktor (ringkas) → Persona detail (Peran/RBAC/Device/Tujuan/Pain/Aksi) → Alur (opsional) → Skenario Gagal (opsional) → Dokumen Terkait |
| **Capture (privat)** | daily note / notulen — TIDAK di-publish, exempt | [[Template - Daily Note]] · [[Template - Meeting Note]] | bebas / Agenda → Catatan → Keputusan → Aksi → Naik kelas |

Konsep & implementasi **saling di-link**: konsep di folder domain ↔ implementasi di Core System and Modules. Contoh nyata: [[Sales - Marketplace Integration]] (konsep) ↔ [[Microservices - Integration Service]] (implementasi).

> **Persona / Pengguna** (CLAUDE.md §6): dok **domain** & **service ber-UI** cantumkan seksi `## Persona / Pengguna` — tabel aktor (Persona · Peran & Divisi · Akses/RBAC · Device) + Tujuan/Pain/Aksi. Cukup **inline** untuk kasus sederhana; alur **banyak-aktor kompleks** → **dok terpisah** dari [[Template - Persona]], nama `<Prefix> - <Fitur> Persona` di folder domain, link dua arah dg dok induk. Persona **ikut status** dok induk, tetap grounded (dari peran/RBAC nyata).

## 3. Aturan inti (wajib)

- **Grounded-in-code** (`CLAUDE.md` §1): tulis hanya yang ada di kode/sumber. Belum ada → **TBD**. Rencana ≠ implementasi → catat gap eksplisit. **Jangan mengarang.**
- **Status marker** di awal dok (`CLAUDE.md` §5): ✅ Implemented · ⚠️ Implemented (ada catatan) · 🟡 Konsep/Draft · 🔴 Stub.
  **Dua bentuk penulisan sama-sama sah**, ditetapkan template masing-masing — pakai yang sesuai template dok yang sedang ditulis, jangan dicampur:
  - `- **Status**: ✅ ...` — bullet di dalam `## Deskripsi`. Dipakai [[Template - Implementasi Service]] & [[Template - Konsep Domain]].
  - `> **Status**: ⚠️ ...` — blockquote di baris pertama. Dipakai [[Template - Runbook]].

  Keduanya dibaca `VAULT-INDEX.json` dan muncul di `/ask`. **Harus di 15 baris pertama** — di bawah itu tak terbaca (mencegah heading seperti `## Status Rollout` ikut tertangkap). Sampai 2026-08-06 parser hanya mengenali bentuk bullet, sehingga seluruh runbook terbaca tanpa status; kalau menemui dok yang statusnya jelas ada tapi tak muncul di index, curigai formatnya lebih dulu.
- **Wikilink 0-broken** (`CLAUDE.md` §4): semua `[[...]]` harus resolve sebelum commit; embed gambar harus ada filenya.
- **Bahasa**: Indonesia; istilah teknis tetap English (endpoint, service, request, JWT, dll).
- **Pengecualian**: dok di `Logs/` & file di `Templates/` **dikecualikan** dari grounded/status/template (point-in-time record & scaffold). Dok di `Workspace/` (Inbox + Meetings) **dikecualikan** dari grounded/status/template **dan** dari gate wikilink 0-broken (§4) — privat, tidak di-publish. `Runbooks/` **tidak** dikecualikan (grounded penuh + di-publish).

## Naik kelas (capture → dok permanen)

Capture mentah di `Workspace/` sifatnya sementara. Saat matang, **pindahkan isinya** ke rumah permanen lalu arsip/hapus yang mentah:

| Dari (Workspace) | Isi matang | Ke (permanen) |
|---|---|---|
| Inbox / Meetings | keputusan | `Decisions/ADR - ...` |
| Inbox / Meetings | konteks/aturan bisnis | "Latar Belakang" dok domain |
| Inbox / Meetings | prosedur operasional | `Runbooks/RUN - ...` |
| Inbox | fakta arsitektur/kode | dok domain/service terkait |

`Workspace/` harus tetap **ramping**; kalau menggembung → ada yang belum naik kelas. Dok published **tidak boleh** nge-link ke `Workspace/`.

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

## 7. Contoh prompt untuk agent

Copy salah satu prompt di bawah, ganti placeholder `<...>`, tempel ke agent. Semua prompt mengasumsikan agent punya akses **vault + repo kode bersebelahan** (lihat `CLAUDE.md` §0) dan **diawali membaca `CLAUDE.md` + SOP ini** agar aturannya ter-load.

### A. Dokumentasikan service baru dari kode (implementasi)

```text
Kamu mendokumentasikan ERP Bharata di Obsidian vault ini.

1. Baca dulu `CLAUDE.md` (root) dan `IT/IT - SOP Dokumentasi Vault.md`,
   lalu patuhi seluruh aturannya (grounded-in-code, penamaan, wikilink 0-broken, alur git).
2. Sumber kebenaran = kode di `/bip-erp/services/<nama-service>`. Baca kode itu
   (routes, handler, model, worker/cron). JANGAN mengarang; yang belum ada tandai TBD.
3. Buat dok `Core System and Modules/Microservices - <Nama Service>.md` mengikuti
   template `Templates/Template - Implementasi Service.md`: Deskripsi (Stack/Path/Status) →
   Endpoint/Fitur (Sudah Diimplementasikan, grouped) → Belum Diimplementasikan/Catatan →
   Dependensi & Integrasi (wikilink) → Dokumen Terkait.
4. Tautkan ke dok terkait yang sudah ada (gateway, DB, konsep domain) + backlink bila relevan.
5. Verifikasi semua wikilink resolve (0 broken) → git pull → stage per-file →
   commit `docs: ...` → push. Jangan commit `.obsidian/*`.
```

### B. Update dok existing setelah perubahan kode (sync)

```text
Kamu menyinkronkan dokumentasi ERP dengan perubahan kode terbaru.

1. Baca `CLAUDE.md` + `IT/IT - SOP Dokumentasi Vault.md`, patuhi aturannya.
2. `git pull` di vault dan repo kode. Lihat diff/commit terbaru di
   `<repo/path, mis. bip-erp/services/employee>`.
3. Tentukan dok terdampak (pakai pemetaan repo→dok di `CLAUDE.md` §7). Update HANYA yang
   berubah: tambah endpoint/fitur baru ke section yang tepat, perbarui Status marker,
   pindahkan item dari "Belum Diimplementasikan" → "Sudah Diimplementasikan" bila sudah jadi.
4. Jaga grounded: ubah/hapus klaim yang tak lagi sesuai kode; catat gap baru sebagai TBD.
5. Verifikasi wikilink 0-broken → stage per-file → commit `docs: ...` → push.
```

### C. Buat dok konsep/domain (bisnis)

```text
Kamu menulis dokumentasi KONSEP/bisnis (bukan implementasi) untuk domain
<Sales/HRIS/GA/Warehouse/Finance/...>.

1. Baca `CLAUDE.md` + `IT/IT - SOP Dokumentasi Vault.md`, patuhi aturannya.
2. Buat dok `<Folder domain>/<Prefix> - <Nama>.md` mengikuti template
   `Templates/Template - Konsep Domain.md`: Deskripsi → Latar Belakang →
   Ruang Lingkup/Cakupan → Konsumen Data → Kendala → Belum Diputuskan (TBD) → Dokumen Terkait.
3. WAJIB saling-link dengan dok implementasinya bila ada (service di Core System and Modules).
   Hal yang belum diputuskan tulis sebagai TBD — jangan mengarang detail teknis.
4. Verifikasi wikilink 0-broken → stage per-file → commit `docs: ...` → push.
```

### D. Catat log operasional (korespondensi / access-log / insiden)

```text
Kamu mencatat artefak OPERASIONAL (korespondensi vendor / dump access-log / catatan insiden)
— ini bukan dokumentasi arsitektur.

1. Baca `CLAUDE.md` §2 (area non-domain Logs) + `IT/IT - SOP Dokumentasi Vault.md`.
2. Buat file `Logs/LOG - <Judul Ringkas>.md` mengikuti template
   `Templates/Template - Log Operasional.md`: header Tipe/Tanggal/Konteks-arsitektur →
   isi point-in-time. MASK kredensial (token/sign/password).
3. Tautkan ke dok arsitektur terkait (service/konsep yang relevan).
4. Stage per-file → commit `docs: ...` → push.
```

## Dokumen Terkait

- [[CLAUDE]] — rulebook ringkas (sumber aturan)
- [[Template - Implementasi Service]] · [[Template - Konsep Domain]] · [[Template - Log Operasional]] · [[Template - Persona]]
- [[HOMEPAGE]] — peta dokumentasi vault
