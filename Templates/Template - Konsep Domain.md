%% ============================================================
TEMPLATE — Konsep / Domain (business view)
Pakai untuk prefix: Sales - · HRIS - · GA - · WH - · Finance - · IT - · External - / Vendor -
Cara pakai:
  • Manusia (Obsidian): Templates plugin → "Insert template" di catatan baru.
  • Agent: copy isi file ini, ganti semua placeholder, HAPUS blok komentar %% %% ini.
Aturan: dok konsep/bisnis. WAJIB di-link ke dok implementasinya (di Core System and Modules) bila ada.
Bagian yang belum ada datanya → kosongkan atau tulis TBD; jangan mengarang.
Saat mengisi wikilink, tulis tanpa backtick agar resolve.
Lihat: IT - SOP Dokumentasi Vault · CLAUDE.md §1 §4 §5 §6
============================================================ %%

# {{title}}

## Deskripsi

*Ringkas dalam 1 paragraf (miring): konsep bisnis ini untuk apa/siapa, dan kaitannya ke implementasi.*

- **Status**: `🟡 Konsep | ✅ Implemented (backend) | ⚠️ Implemented (ada catatan)`
- **Implementasi**: `[[Microservices - ...]]` (bila ada; hapus baris ini bila murni konsep)

## Latar Belakang

- `kenapa ada / masalah yang dipecahkan`

## Ruang Lingkup / Cakupan (business view)

- `fitur / proses bisnis utama`

## Konsumen Data

%% Siapa yang memakai data/output ini. Tautkan dengan wikilink tanpa backtick. %%
- `[[Dok konsumen]]` — `pakai data apa`

## Kendala

%% Kendala nyata (teknis/bisnis). Kosongkan bila belum ada. %%
- `kendala (opsional)`

## Belum Diputuskan (TBD)

- `keputusan yang belum diambil`

## Dokumen Terkait

- `[[Dok implementasi / dok terkait]]`
