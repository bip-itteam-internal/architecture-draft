## ADR 0028 - Code Index bip-erp (manifest deterministik, generator Go, artefak gitignore)

- **Status**: ✅ Accepted (Slice 1+2 sudah jalan di kode; Slice 3 direncanakan)
- **Tanggal**: 2026-07-23
- **Konteks dok**: [[RUN - Code Index bip-erp]] · [[ADR - 0005 Vault sebagai Team Knowledge Base]] · [[CORE - API Master Gateway]]

## Context

Agent AI (`/ask`, `/start-task`) dan developer sering perlu memahami **relasi antar-file** di `bip-erp` sebelum menyentuh kode: paket mana meng-import apa, berkas mana mendefinisikan fungsi/tipe tertentu, dan endpoint mana ditangani service mana. Menjawabnya dengan membaca berkas satu per satu itu lambat dan boros token, padahal `bip-erp` besar: **601 berkas Go** ter-indeks, **18 service** (tiap service module Go sendiri dengan `go.mod` terpisah, lihat [[ADR - 0002 Database-per-Service]]), router **Fiber v2**, dan gateway yang mem-proxy `/api/:module/*` ke service internal ([[CORE - API Master Gateway]]).

Masalah dan pendekatannya persis paralel dengan yang sudah dipecahkan untuk **dokumentasi vault** oleh `VAULT-INDEX.json` ([[ADR - 0005 Vault sebagai Team Knowledge Base]], desain di `architecture-draft/.agent-kit/docs/2026-07-20-vault-index-rag-design.md`): satu manifest ringkas dibaca lebih dulu, agent memilih yang relevan, lalu membaca sumber utuh. **Bukan RAG** (tanpa chunking/embedding). Bedanya, di sini targetnya **source code Go**, bukan markdown.

Kunci yang membedakan kode dari dokumen: **relasi antar-kode bersifat deterministik.** Import, simbol, dan pendaftaran route bisa diambil persis dari AST. Tidak perlu LLM untuk menyimpulkannya, sehingga generator bisa murni deterministik.

## Decision

Bangun **CODE-INDEX**: manifest deterministik relasi antar-file `bip-erp`, digenerate oleh tool Go di `bip-erp/tools/code-index/`, **syntax-only** (`go/parser` + `go/ast` + `go/doc`). Tidak meng-compile, tidak mengunduh module, tidak butuh jaringan, tidak memanggil LLM/API. Mengikuti pola VAULT-INDEX: manifest JSON ber-`versi_skema`, regenerasi **incremental by-hash**, CLI (`--root --out --check --full`).

Isi `CODE-INDEX.json`:

| Bagian | Isi |
|---|---|
| `file[]` | per berkas: package, service, `imports`, `simbol` (func/type/const/var + baris + godoc), `ringkasan` (dari package doc-comment; kosong bila tak ada), `hash` |
| `paket[]` | import graph per package: `depends_on` + `depended_by` (in-repo) |
| `service[]` | `module` (dari `go.mod`) + `depends_on_shared` (paket shared-library yang dipakai) |
| `endpoint[]` | route Fiber: `method`, `path` (prefix group teresolusi), `handler` (nama fungsi atau `inline@file:line`), `middleware` |
| `gateway_modul[]` | tabel `InternalURL` gateway: `module` -> `env_ref` -> `prefix` `/api/<module>` (sisi BE dari kontrak FE-BE) |

**Dua divergensi sadar dari VAULT-INDEX**, keduanya dijustifikasi:

1. **Generator Go, bukan Python.** VAULT-INDEX pakai Python karena korpusnya markdown. Target di sini Go, jadi toolchain Go (`go/ast`, `go/doc`) adalah alat yang benar dan paling akurat; memparse Go dari Python akan rapuh. Karena relasi deterministik, **tidak ada** komponen LLM (VAULT-INDEX memakai subagent untuk ringkasan; di sini ringkasan diambil dari doc-comment secara deterministik).
2. **Artefak di-`.gitignore`, bukan di-commit.** `bip-erp` `commit = published` (auto-push), dan `CODE-INDEX.json` berukuran ~1,9 MB serta berubah tiap edit kode. Meng-commit-nya akan bising dan rawan konflik. Artefak digenerate lokal on-demand/incremental.

## Consequences

**Konsekuensi menerima:**

- **Import graph, bukan call graph.** Edge di level import path (berkas -> paket), bukan "fungsi A memanggil fungsi B" (butuh type info, di luar mode syntax-only). Cukup untuk pertanyaan "ubah berkas/paket ini berdampak ke mana".
- **~6% endpoint `unresolved`.** Route yang didaftarkan di berkas terpisah lewat router yang dioper ke fungsi (mis. `orchestrator/hris/*`, sebagian `services/employee/*`) tidak menampakkan prefix group-nya di berkas itu; `path` direkam sebagai fragmen + flag `unresolved: true`. Route yang didaftarkan langsung pada `app`/group di berkas yang sama teresolusi penuh (mayoritas service + gateway).
- **`gateway_modul.env_ref` adalah ekspresi sumber** (mis. `common.Env.EmployeeModuleURL`), bukan nilai string env-nya (resolusi konstanta lintas-paket di luar lingkup).
- **Artefak tak ada di clone baru** sampai `go run` pertama (karena gitignore). Generator cepat, jadi ini murah. `--check` cocok untuk pre-commit/CI mengingatkan index basi.
- Angka korpus (per 2026-07-23: 601 berkas, 103 paket, 18 service, 705 endpoint, 16 module gateway) **bergerak**; jangan dijadikan konstanta.

**Alternatif yang ditolak:**

- **RAG / embedding / vector store.** Alasan sama seperti VAULT-INDEX: berat, dan di sini makin tak perlu karena relasi kode sudah deterministik. Jalur naik tetap terbuka bila kelak terbukti perlu.
- **Meng-commit artefak** (seperti VAULT-INDEX yang di-commit ke vault): ditolak karena auto-push + ukuran/churn `bip-erp`.

**Belum dikerjakan (Slice 3, TBD):**

- Wiring konsumsi: `/ask` dan `/start-task` membaca `CODE-INDEX.json` saat task menyentuh `bip-erp`.
- Join **sisi FE** dari kontrak: memetakan hook/route `erp-frontend` ke endpoint BE lewat `gateway_modul`. Pilot ini baru menyediakan sisi BE-nya.

## Dokumen Terkait

- [[RUN - Code Index bip-erp]] — cara pakai tool + batasan
- [[ADR - 0005 Vault sebagai Team Knowledge Base]] — preseden VAULT-INDEX (manifest + agentic fetch, bukan RAG)
- [[ADR - 0002 Database-per-Service]] — struktur module-per-service yang diindeks
- [[CORE - API Master Gateway]] — sumber tabel `InternalURL` (gateway_modul) + proxy `/api/:module/*`
- [[DEVELOPER GUIDE]] — cara kerja dev, tempat tool dev dirujuk
