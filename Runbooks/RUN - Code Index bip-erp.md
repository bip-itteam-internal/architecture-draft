> **Status**: ✅ Implemented (Slice 1+2: generator + manifest inti); Slice 3 (wiring `/ask` & `/start-task`, join FE) direncanakan. Lihat [[ADR - 0028 Code Index bip-erp]] untuk keputusan & batasan.

## Tujuan

Memberi agent AI dan developer sebuah manifest deterministik relasi antar-file `bip-erp`, supaya bisa menelusuri "paket ini dipakai siapa", "berkas ini mendefinisikan apa", dan "endkoint ini ditangani service mana" **tanpa membaca tiap berkas** (lebih cepat, hemat token). Analog [[ADR - 0005 Vault sebagai Team Knowledge Base|VAULT-INDEX]] tapi untuk source code.

## Kapan dipakai

- Sebelum mengubah kode `bip-erp` yang belum dikenal: cek `depended_by` sebuah paket untuk tahu dampak perubahan.
- Saat mencari endpoint: `endpoint[]` memberi method, path, handler (`inline@file:line` atau nama fungsi), dan middleware, plus `gateway_modul[]` untuk tahu module mana di-proxy ke service mana lewat `/api/:module/*` ([[CORE - API Master Gateway]]).
- Saat perlu ringkasan peran berkas tanpa membukanya: field `ringkasan` (dari package doc-comment).

## Prasyarat

- Go terpasang (module di `bip-erp/tools/code-index`, hanya stdlib).
- Akses repo `bip-erp`.

## Cara pakai

Dari `bip-erp/tools/code-index` (tunjuk `--root` ke akar `bip-erp`):

```
go run . --root ../..              # bangun/segarkan (incremental by-hash)
go run . --root ../.. --full       # bangun ulang penuh, abaikan hash lama
go run . --root ../.. --check      # exit 1 bila index basi; tidak menulis
go run . --root ../.. --out X.json # lokasi output kustom
```

Output default: `bip-erp/CODE-INDEX.json` (**di-.gitignore**, artefak generated ~1,9 MB; regen lokal saat perlu). Detail lengkap + skema di `bip-erp/tools/code-index/README.md`.

## Isi index

| Bagian | Menjawab |
|---|---|
| `file[]` | package, service, `imports`, `simbol` (+ baris + godoc), `ringkasan`, `hash` |
| `paket[]` | `depends_on` + `depended_by` (in-repo) — dampak perubahan |
| `service[]` | `module` + `depends_on_shared` (paket shared-library) |
| `endpoint[]` | route Fiber: method, path, handler, middleware |
| `gateway_modul[]` | `module` -> `env_ref` -> prefix `/api/<module>` |

## Batasan (jujur)

- **Import graph, bukan call graph** (edge di level import path, bukan pemanggilan fungsi).
- **~6% endpoint `unresolved`**: route via router yang dioper ke fungsi lintas-berkas (mis. `orchestrator/hris/*`) tak menampakkan prefix group-nya; `path` direkam sebagai fragmen + flag `unresolved: true`.
- **`env_ref`** ekspresi sumber (mis. `common.Env.EmployeeModuleURL`), bukan nilai string env.
- **Sisi FE kontrak belum dijoin** (Slice 3). Pilot ini baru sisi BE.

## Dokumen Terkait

- [[ADR - 0028 Code Index bip-erp]] — keputusan, divergensi dari VAULT-INDEX, konsekuensi
- [[ADR - 0005 Vault sebagai Team Knowledge Base]] — preseden VAULT-INDEX
- [[CORE - API Master Gateway]] — proxy `/api/:module/*` + tabel `InternalURL`
- [[DEVELOPER GUIDE]] — cara kerja dev
