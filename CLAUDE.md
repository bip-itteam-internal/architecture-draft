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
- **Konsep ↔ implementasi**: dok konsep/bisnis ada di folder domain (mis. Sales, HRIS), implementasi/service di Core System and Modules. Keduanya **saling di-link**.
- **Bahasa**: Bahasa Indonesia, istilah teknis tetap English (endpoint, request, service, JWT, dll).

## 2. Struktur folder (domain)

`Application` · `Core System and Modules` · `Finance System` · `General Affairs` · `Human Resource Information System` · `Manufacture` · `Sales` · `Quality & Regulatory` · `IT` · `Third-party Software` · `Warehouse` · `Unknown or not listed`

> `Quality & Regulatory` (prefix `QA -`) = domain fungsi **QA/RA farmasi** (CPOB/GMP, BPOM/izin edar, batch record & traceability, deviation/CAPA, ED & recall, CDOB). Mengikuti §1/§4/§5 seperti domain lain.

**Area non-domain:** `Logs` — artefak **operasional** (korespondensi vendor, dump access-log, catatan insiden). Sifatnya **point-in-time record**, **bukan** dokumentasi arsitektur → **dikecualikan** dari grounded-in-code (§1), status marker (§5), dan template (§6). Tetap ikut konvensi nama (§3) dan **flat** (tanpa sub-pohon domain). Tautkan tiap log ke dok arsitektur terkait via wikilink.

**Area non-domain:** `Templates` — file **skeleton** untuk dok baru (dipakai via plugin Templates Obsidian atau di-copy agent). Bukan dokumentasi → **dikecualikan** dari §1/§5/§6; isinya placeholder + komentar `%% %%` (tanpa wikilink hidup). Prosedur lengkap: `IT/IT - SOP Dokumentasi Vault.md`.

**Area non-domain:** `Reference` (prefix `REF -`) — referensi **lintas-domain** (glosarium istilah/singkatan, data dictionary, ownership/RACI). **TETAP grounded** (ikut §1/§4/§5) — beda dari Logs/Templates. Flat, tanpa sub-pohon domain.

**Area non-domain:** `Decisions` (prefix `ADR -`) — **Architecture/Business Decision Records**: satu file per keputusan (mis. `ADR - 0001 Akuntansi via Accurate`), format Context → Decision → Consequences. Grounded ke kondisi nyata; tandai `Superseded` bila digantikan ADR lain.

**Area non-domain:** `API Reference` (prefix `API -`) — daftar **endpoint per service** (grounded ke kode). Satu file `API - <Service>.md` + `API - Index`; ikut §1/§4/§5; sinkron via `/sync-docs` saat rute berubah.

**Sub-area generated:** `API Reference/<Vendor>/` (mis. `Shopee Open API v2/`) — cache dokumentasi **API pihak ketiga** yang **di-generate skrip** (`Tools/*.py`), bukan ditulis tangan. Dibaca agent lewat **path file**, bukan graph Obsidian. **Dikecualikan** dari konvensi nama §3, template §6, dan kewajiban wikilink §4 (isinya di-overwrite tiap regenerate, jadi wikilink manual akan hilang); penamaan file mengikuti konvensi vendor (mis. `order.get_order_list.md`). Yang **tetap wajib**: `README.md` folder tersebut menjelaskan alur pakai + cara regenerate, dan field `Confidence` di tiap file cache (grounded §1 tetap berlaku: jangan mengarang nama field). Konsekuensinya file-file ini muncul sebagai **orphan** di graph view; itu normal, sembunyikan lewat filter graph, jangan "diperbaiki" dengan menambah wikilink.

**Area non-domain:** `Runbooks` (prefix `RUN -`) — **pengetahuan operasional non-kode**: runbook, how-to, onboarding, troubleshooting. **TETAP grounded** (ikut §1/§4/§5: prosedur harus benar-benar jalan, status marker, wikilink 0-broken) dan **tetap di-publish** ke wiki. Flat, tanpa sub-pohon domain.

**Area non-domain:** `Workspace` — **corong capture privat**, **dikecualikan dari publish wiki**. Dua sub-area: `Workspace/Inbox` (daily notes `YYYY-MM-DD.md` + idea capture, nama bebas) & `Workspace/Meetings` (notulen, prefix `MTG -`, mis. `MTG - 2026-06-25 Standup`). Di **akar** `Workspace/`: daftar task hasil `/analisa-kebutuhan` (prefix `ANALISA -`) — papan kerja yang berubah tiap item selesai, bukan arsitektur; ADR dan dok domain yang menyertainya tetap terbit ke folder domain masing-masing. **Dikecualikan** dari grounded-in-code (§1), status marker (§5), template (§6), dan gate wikilink 0-broken (§4) — capture boleh nge-link ke catatan yang belum ada. Catatan matang **"naik kelas"** jadi dok domain / `RUN -` / `ADR -`, lalu yang mentah diarsip/dihapus. **Larangan:** dok published TIDAK boleh nge-link ke `Workspace/` (akan broken di wiki). Exclusion publish via ignore-glob `Workspace/**` dan/atau frontmatter `publish: false`.

> **Dok meta root** (di akar vault, tanpa prefix): `README` · `HOMEPAGE` (peta) · `CLAUDE` (rulebook) · `SCRUM SPECS` (proses) · `ROADMAP` (arah/prioritas) · `DEVELOPER GUIDE` (cara kerja dev). Bukan domain; jangan beri prefix.

## 3. Konvensi penamaan file

Format: **`Prefix - Nama.md`**. Prefix sesuai domain/jenis:
- `CORE -` (gateway, SSO, orchestrator, shared service), `Microservices -` (service bip-erp), `DB -` → **Core System and Modules**
- `APP -` / `BASE -` → **Application**
- `HRIS -` → HRIS · `Sales -` → Sales · `GA -` → General Affairs · `IT -` → IT · `WH -` → Warehouse · `Manufacture -` → Manufacture · `Finance -` → Finance System · `External -` / `Vendor -` → Third-party Software
- `LOG -` → **Logs** (artefak operasional; mis. `LOG - Shopee API Rate Limit Request`)
- `QA -` → **Quality & Regulatory** (QA/RA farmasi; mis. `QA - CPOB (GMP)`)
- `REF -` → **Reference** (glosarium, data dictionary, ownership; mis. `REF - Glossary`)
- `ADR -` → **Decisions** (mis. `ADR - 0002 Database-per-Service`)
- `API -` → **API Reference** (mis. `API - Employee Service`)
- `RUN -` → **Runbooks** (operasional non-kode; mis. `RUN - Onboarding Developer Baru`)
- `MTG -` → **Workspace/Meetings** (notulen rapat; mis. `MTG - 2026-06-25 Standup`)
- `ANALISA -` → **Workspace** (akar; daftar task hasil `/analisa-kebutuhan`, mis. `ANALISA - Dashboard Performa Cabang`)
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

**Bentuk penulisan** — dua-duanya sah, pakai yang sesuai template dok yang sedang ditulis:
`- **Status**: ✅ ...` (bullet di `## Deskripsi`; template Implementasi Service & Konsep Domain) atau
`> **Status**: ✅ ...` (blockquote di baris pertama; template Runbook).
Wajib berada di **15 baris pertama** — di bawah itu tak terbaca `VAULT-INDEX.json` sehingga dok jadi tak berstatus di `/ask`. Detail: `IT/IT - SOP Dokumentasi Vault.md`.

## 6. Template struktur dokumen

```
## Deskripsi          (1 paragraf miring + bullet: Stack, Path di repo, Status)
## Endpoint / Fitur (Sudah Diimplementasikan)   (grouped)
## Belum Diimplementasikan / Catatan            (501/stub/TODO/gap; TBD bila konsep)
## Dependensi & Integrasi                        (dengan wikilink)
## Dokumen Terkait                               (wikilink)
```
Untuk dok konsep murni: `## Latar Belakang`, `## Ruang Lingkup`, `## Belum Diputuskan (TBD)`, dst.

> **Skeleton siap-pakai** untuk tiap bentuk ada di folder `Templates/` (Implementasi Service · Konsep Domain · Log Operasional · Persona). Prosedur lengkap + decision-tree penamaan: `IT/IT - SOP Dokumentasi Vault.md`.

> **Persona / Pengguna** — dok **domain** & **service ber-UI** memuat `## Persona / Pengguna`: tabel aktor (**Persona · Peran & Divisi · Akses/RBAC · Device**) + poin **Tujuan · Pain point · Aksi utama**. Tujuan: developer/AI paham **siapa** pengguna fitur. Alur **banyak-aktor kompleks** → buat dok terpisah `<Prefix> - <Fitur> Persona` dari **Template - Persona** (folder domain, prefix domain) lalu link dari dok induk. Persona **ikut status** dok induk (tanpa marker terpisah) & tetap **grounded** (§1) — dari peran/RBAC nyata, jangan mengarang.

## 7. Pemetaan repo kode → dokumen

| Repo kode | Dokumen utama |
|---|---|
| `bip-erp` (Go microservices) | `Core System and Modules/*` (API Master Gateway, SSO Flow, HRIS/IT Orchestrator, DB Overview, Microservices - <Service>, OCR Document Service) |
| `mybharata-app` (Flutter) | `Application/APP - MyBharata` |
| `erp-frontend` (Next.js) | `Application/APP - Web ERP`, `BASE - Enterance Point` |
| `task-management/bharata-task-manager-fe` | `Application/APP - Dynamic Task Tracker` (backend = Microservices - Task Management Service) |
| `guestbook-system` (Astro) | `General Affairs/GA - Guestbook System (Complete)` |
| `ideamiils` (Next.js + Veo) | `Application/APP - Ideamills` (app); konsep: `Sales/Sales - Veo (Gemini) Implementation` (manual) & `... Automation Layer` |
| `scraping` (Python/FastAPI) | `Application/APP - Tiktok Insight Analyzer` (app) & `Sales/Sales - TikTok Sentiment Pipeline` (konsep) |
| `website-bharata` (Next.js + Go, **repo terpisah**, bukan bip-erp) | `Application/APP - Website Bharata Internasional` |
| `career-bharata` (Next.js 16, **repo terpisah**; konsumen `/public/recruitment/*`) | `Application/APP - Portal Karir Bharata` |
| `consolidated-accounting-app` (Next.js 16 + Supabase, **repo PRIBADI di luar org**; tidak menyentuh gateway) | `Application/APP - Buku Besar Konsolidasi CV FINCON` (app) & `Decisions/ADR - 0068 Buku Besar Konsolidasi 40 CV di Luar Accurate` (arah) |

**Area non-kode (tanpa repo):**
- `Quality & Regulatory/*` ← sumber = **SOP/sertifikat QA-RA Bharata** (CPOB/BPOM/CDOB; diisi tim QA — bukan dari kode).
- `Reference/*` ← istilah & singkatan yang dipakai lintas vault + kode (glosarium), data dictionary, ownership.

## 7b. Index pencarian (`VAULT-INDEX.json`)

Manifest seluruh dokumen vault: judul, area, jenis, status, tautan, ringkasan, dan kata kunci. Dipakai `/ask` dan `/start-task` untuk memilih dokumen relevan dari sebuah **pertanyaan**; §7 di atas memetakan dari **repo kode**. Sumbu berbeda, keduanya dipakai bersama.

Field `publik` menandai dokumen yang boleh muncul di kanal untuk staf non-IT nanti. `IT/`, `Workspace/`, `Logs/`, dan `Templates/` selalu `false`, dan folder yang belum dikenal otomatis `false` (fail-closed).

Diregenerasi lewat `/index-vault` — ringkasan dibuat subagent Claude Code, bukan API. **Jangan diedit tangan.** Wajib ikut ter-commit tiap `/sync-docs` yang mengubah dokumen. Detail: `Tools/README.md`.

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

<!-- shopee-context:start -->
## Integrasi eksternal

Konteks integrasi disimpan per folder dan dibaca **hanya saat relevan**.
Jangan load isinya kalau task tidak menyentuh integrasi tersebut.

| Integrasi | Folder | Baca kapan |
|---|---|---|
| Shopee Open API v2 | `API Reference/Shopee Open API v2/` | task menyentuh Shopee: order, produk, stok, logistik, iklan |

Saat relevan, baca `README.md` di folder tersebut lebih dulu — di situ ada
alur wajib, termasuk cara memperbarui dokumentasinya sendiri.
<!-- shopee-context:end -->
