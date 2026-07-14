%% ============================================================
TEMPLATE — Implementasi / Service (grounded-in-code)
Pakai untuk prefix: Microservices - · CORE - · DB - · APP - · BASE -
Cara pakai:
  • Manusia (Obsidian): Templates plugin → "Insert template" di catatan baru.
  • Agent: copy isi file ini, ganti semua placeholder, HAPUS blok komentar %% %% ini.
Aturan: tulis HANYA yang ada di kode (grounded). Belum ada → tandai TBD. Jangan mengarang.
Saat mengisi wikilink, tulis tanpa backtick agar resolve (mis. [[CORE - API Master Gateway]]).
Lihat: IT - SOP Dokumentasi Vault · CLAUDE.md §1 §4 §5 §6
============================================================ %%

# {{title}}

## Deskripsi

*Ringkas dalam 1 paragraf (miring): apa service ini, tujuannya, dan cakupan utamanya.*

- **Stack**: `bahasa + framework + datastore (mis. Go + Fiber v2 + MongoDB + Redis)`
- **Path**: `path di repo kode (mis. services/integration)`
- **Status**: `✅ Implemented | ⚠️ Implemented (ada catatan) | 🟡 Konsep | 🔴 Stub` — `catatan singkat`

## Persona / Pengguna

%% OPSIONAL — isi bila service punya UI/pengguna langsung; HAPUS seksi ini utk service backend-only.
   Siapa MANUSIA yang memakai (gambaran utk developer/AI). Alur banyak-aktor kompleks →
   dok terpisah `<Prefix> - <Fitur> Persona` (Template - Persona), link di sini. Grounded, jangan mengarang. %%

| Persona | Peran & Divisi | Akses / RBAC | Device |
|---|---|---|---|
| `nama/label` | `jabatan, divisi/grup` | `role sistem / permission` | `Web ERP / MyBharata` |

- **Tujuan**: `yang ingin dicapai`
- **Pain point**: `masalah lama yang dipecahkan`
- **Aksi utama**: `langkah inti di sistem`

## Endpoint / Fitur (Sudah Diimplementasikan)

%% Kelompokkan per area dengan sub-header ###. Tulis hanya yang BENAR ada di kode. %%

### `Nama Grup (mis. Webhooks)`
- `METHOD /path` — `deskripsi singkat`

## Belum Diimplementasikan / Catatan

%% Gap nyata: 501 / route di-comment / stub / TODO. Bila masih konsep murni, tulis TBD. %%
- `gap / catatan / TODO`

## Dependensi & Integrasi

%% Tautkan ke dok lain pakai wikilink TANPA backtick, mis. [[DB - Overview and Notes]] %%
- `[[Dok lain]]` — `peran/relasi`

## Dokumen Terkait

- `[[Dok konsep/domain terkait]]`
