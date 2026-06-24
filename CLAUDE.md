# CLAUDE.md — Rulebook untuk AI Agent (architecture-draft)

Repo ini adalah **Obsidian vault dokumentasi arsitektur ERP Bharata**. Tugas AI agent: menjaga dokumentasi **selaras dengan kode** (grounded), konsisten, dan saling tertaut. Ikuti aturan di bawah **persis**.

> Catatan notasi di file ini: wikilink Obsidian ditulis dengan **dua kurung siku** mengapit basename file (tanpa ekstensi); embed gambar memakai tanda **`!`** di depannya. Contoh sengaja tidak ditulis literal di sini agar tidak jadi link palsu.

## 0. Prasyarat workspace (PENTING)

Agent butuh akses ke **kode (sumber kebenaran)** dan **vault (target)** sekaligus. Clone vault + repo kode sebagai **folder bersebelahan (sibling)** lalu buka folder induk:

```
erp/                      ← working directory agent
├── architecture-draft/   ← vault ini (target dokumentasi)
├── bip-erp/
├── erp-frontend/
├── mybharata-app/  · task-management/  · ideamiils/  · scraping/  · guestbook-system/
```
Tidak wajib semua repo — cukup vault + repo yang sedang didokumentasikan.

## 1. Prinsip utama

- **Grounded-in-code**: tulis hanya yang benar-benar ada di kode/sumber. Yang belum ada → tandai **TBD**. **Jangan mengarang.** Bila rencana ≠ implementasi, catat gap-nya secara eksplisit.
- **Konsep ↔ implementasi**: dok konsep/bisnis ada di folder domain (mis. Marketing, HRIS), implementasi/service di Core System and Modules. Keduanya **saling di-link**.
- **Bahasa**: Bahasa Indonesia, istilah teknis tetap English (endpoint, request, service, JWT, dll).

## 2. Struktur folder (domain)

`Application` · `Core System and Modules` · `Finance System` · `General Affairs` · `Human Resource Information System` · `Manufacture` · `Marketing` · `Quality & Regulatory` · `Tech Development` · `Third-party Software` · `Warehouse` · `Unknown or not listed`

> `Quality & Regulatory` (prefix `QA -`) = domain fungsi **QA/RA farmasi** (CPOB/GMP, BPOM/izin edar, batch record & traceability, deviation/CAPA, ED & recall, CDOB). Mengikuti §1/§4/§5 seperti domain lain.

**Area non-domain:** `Logs` — artefak **operasional** (korespondensi vendor, dump access-log, catatan insiden). Sifatnya **point-in-time record**, **bukan** dokumentasi arsitektur → **dikecualikan** dari grounded-in-code (§1), status marker (§5), dan template (§6). Tetap ikut konvensi nama (§3) dan **flat** (tanpa sub-pohon domain). Tautkan tiap log ke dok arsitektur terkait via wikilink.

**Area non-domain:** `Templates` — file **skeleton** untuk dok baru (dipakai via plugin Templates Obsidian atau di-copy agent). Bukan dokumentasi → **dikecualikan** dari §1/§5/§6; isinya placeholder + komentar `%% %%` (tanpa wikilink hidup). Prosedur lengkap: `Tech Development/IT - SOP Dokumentasi Vault.md`.

**Area non-domain:** `Reference` (prefix `REF -`) — referensi **lintas-domain** (glosarium istilah/singkatan, data dictionary, ownership/RACI). **TETAP grounded** (ikut §1/§4/§5) — beda dari Logs/Templates. Flat, tanpa sub-pohon domain.

**Area non-domain:** `Benchmark` — **riset/perbandingan produk eksternal** (mis. `Benchmark - ERPGo`, prefix `ERPGo -`). Sifatnya *point-in-time research*: sisi produk eksternal **dikecualikan** dari grounded-in-code; **sisi Bharata tetap grounded + wikilink**. Tiap dok ditandai status 🟡 dan menaut ke dok arsitektur terkait.

**Area non-domain:** `Decisions` (prefix `ADR -`) — **Architecture/Business Decision Records**: satu file per keputusan (mis. `ADR - 0001 Akuntansi via Accurate`), format Context → Decision → Consequences. Grounded ke kondisi nyata; tandai `Superseded` bila digantikan ADR lain.

> **Dok meta root** (di akar vault, tanpa prefix): `README` · `HOMEPAGE` (peta) · `CLAUDE` (rulebook) · `SCRUM SPECS` (proses) · `ROADMAP` (arah/prioritas) · `DEVELOPER GUIDE` (cara kerja dev). Bukan domain; jangan beri prefix.

## 3. Konvensi penamaan file

Format: **`Prefix - Nama.md`**. Prefix sesuai domain/jenis:
- `CORE -` (gateway, SSO, orchestrator, shared service), `Microservices -` (service bip-erp), `DB -` → **Core System and Modules**
- `APP -` / `BASE -` → **Application**
- `HRIS -` → HRIS · `Sales -` → Marketing · `GA -` → General Affairs · `IT -` → Tech Development · `WH -` → Warehouse · `Manufacture -` → Manufacture · `Finance -` → Finance System · `External -` / `Vendor -` → Third-party Software
- `LOG -` → **Logs** (artefak operasional; mis. `LOG - Shopee API Rate Limit Request`)
- `QA -` → **Quality & Regulatory** (QA/RA farmasi; mis. `QA - CPOB (GMP)`)
- `REF -` → **Reference** (glosarium, data dictionary, ownership; mis. `REF - Glossary`)
- `ERPGo -` (atau prefix nama-produk lain) → **Benchmark** (riset produk eksternal)
- `ADR -` → **Decisions** (mis. `ADR - 0002 Database-per-Service`)
- Karakter `/` tidak boleh di nama file (pakai `-`, mis. `IT - CI-CD`).

## 4. Wikilink

- Tautkan antar-dok memakai wikilink Obsidian (basename file, tanpa ekstensi). Obsidian resolve via **basename** — folder tidak berpengaruh.
- **Wajib**: sebelum commit, pastikan **semua wikilink resolve** ke file yang ada (0 broken). Embed gambar juga harus ada filenya.
- Pindah folder file = link aman; **rename file = perbarui semua wikilink** yang menunjuk ke nama lama.

## 5. Status marker (di awal dok)

- ✅ **Implemented** — sudah ada di kode
- ⚠️ **Implemented (ada catatan)** — jalan tapi ada gap/bug/parsial
- 🟡 **Konsep / Draft / Direncanakan** — belum di kode
- 🔴 **Stub** — kosong/skeleton

## 6. Template struktur dokumen

```
## Deskripsi          (1 paragraf miring + bullet: Stack, Path di repo, Status)
## Endpoint / Fitur (Sudah Diimplementasikan)   (grouped)
## Belum Diimplementasikan / Catatan            (501/stub/TODO/gap; TBD bila konsep)
## Dependensi & Integrasi                        (dengan wikilink)
## Dokumen Terkait                               (wikilink)
```
Untuk dok konsep murni: `## Latar Belakang`, `## Ruang Lingkup`, `## Belum Diputuskan (TBD)`, dst.

> **Skeleton siap-pakai** untuk tiap bentuk ada di folder `Templates/` (Implementasi Service · Konsep Domain · Log Operasional). Prosedur lengkap + decision-tree penamaan: `Tech Development/IT - SOP Dokumentasi Vault.md`.

## 7. Pemetaan repo kode → dokumen

| Repo kode | Dokumen utama |
|---|---|
| `bip-erp` (Go microservices) | `Core System and Modules/*` (API Master Gateway, SSO Flow, HRIS/IT Orchestrator, DB Overview, Microservices - <Service>, OCR Document Service) |
| `mybharata-app` (Flutter) | `Application/APP - Mobile Application` |
| `erp-frontend` (Next.js) | `Application/APP - Web Application`, `BASE - Enterance Point` |
| `task-management/bharata-task-manager-fe` | `Application/APP - Dynamic Task Tracker` (backend = Microservices - Task Management Service) |
| `guestbook-system` (Astro) | `General Affairs/GA - Guestbook System (Complete)` |
| `ideamiils` (Next.js + Veo) | `Application/APP - Ideamills` (app); konsep: `Marketing/Sales - Veo (Gemini) Implementation` (manual) & `... Automation Layer` |
| `scraping` (Python/FastAPI) | `Application/APP - TikTok Sentiment Pipeline` (app) & `Marketing/Sales - TikTok Sentiment Pipeline` (konsep) |

**Area non-kode (tanpa repo):**
- `Quality & Regulatory/*` ← sumber = **SOP/sertifikat QA-RA Bharata** (CPOB/BPOM/CDOB; diisi tim QA — bukan dari kode).
- `Reference/*` ← istilah & singkatan yang dipakai lintas vault + kode (glosarium), data dictionary, ownership.
- `Benchmark/*` ← riset produk eksternal (mis. ERPGo); sumber = dokumentasi produk ybs.

## 8. Alur kerja sync (tiap update)

1. `git pull` vault + repo kode (ambil terbaru)
2. Baca diff/kode repo terkait → tentukan dok yang terdampak
3. Update/buat dok (grounded; ikuti template & konvensi)
4. **Verifikasi semua wikilink resolve** (0 broken)
5. Commit & push

## 9. Aturan git

- **Stage per-nama file** (mis. `git add -- "Folder/Nama.md"`). **JANGAN `git add -A`** — bisa menyapu perubahan in-progress orang lain.
- **Pull sebelum push** (vault dikerjakan banyak orang/agent secara paralel).
- Pesan commit ringkas berformat `docs: ...`; jangan commit `.obsidian/*` kecuali diminta (itu state Obsidian).
- Jangan menimpa/menghapus dok yang **bukan dibuat sesi ini** tanpa konfirmasi; hormati file yang sedang diedit orang lain.

## 10. Jangan

- Jangan mengarang detail yang tak ada di kode.
- Jangan menghapus dok turunan hanya karena ada dok "induk" (induk = overview, turunan = detail).
- Jangan membuat wikilink rusak; selalu verifikasi sebelum commit.
