%% ============================================================
TEMPLATE — Persona / Pengguna (untuk alur banyak-aktor yang kompleks)
Pakai bila persona tak cukup ditaruh inline di dok domain/service (aktor banyak / alur bercabang).
Nama file: `<Prefix> - <Fitur> Persona.md` di folder domain (prefix sama dg dok induk, mis. `HRIS - Tukar Jadwal Kerja Persona`).
Cara pakai:
  • Manusia (Obsidian): Templates plugin → "Insert template" di catatan baru.
  • Agent: copy isi file ini, ganti semua placeholder, HAPUS blok komentar %% %% ini.
Aturan: grounded — persona dari peran/RBAC nyata & kode, jangan mengarang. Persona IKUT status dok induk.
WAJIB di-link dari dok domain/service induk (dan sebaliknya). Wikilink ditulis tanpa backtick agar resolve.
Lihat: IT - SOP Dokumentasi Vault · CLAUDE.md §1 §4 §5 §6
============================================================ %%

# {{title}} — Persona & Alur

> Menggambarkan **siapa** yang memakai `[[Dok domain/service induk]]` dan **bagaimana** alurnya. Status ikut dok induk (`🟡 Konsep | ✅ Implemented | ⚠️ ada catatan`).

## Aktor (ringkas)

%% Satu baris per persona. "Muncul di" = sub-fitur/alur tempat ia berperan. %%

| Persona | Peran & Divisi | Akses / RBAC | Device | Muncul di |
|---|---|---|---|---|
| `nama/label` | `jabatan, divisi/grup` | `role sistem / permission` | `Web ERP / MyBharata` | `alur/sub-fitur` |

## Persona detail

%% Ulangi blok ### per persona. Isi grounded; hilangkan baris yang tak relevan. %%

### `Nama` — `perannya`
- **Peran & Divisi**: `jabatan + divisi/grup`
- **Akses / RBAC**: `role sistem + permission/scope (mis. approver, HR admin)`
- **Device**: `Web ERP | MyBharata (mobile) | keduanya`
- **Tujuan**: `apa yang ingin ia capai`
- **Pain point**: `masalah lama yang dipecahkan`
- **Aksi utama**: `langkah inti yang ia lakukan di sistem`

## Alur (opsional)

%% Diagram/urutan langkah lintas persona. Boleh embed Excalidraw: ![[<Fitur> - Flow.excalidraw]]. Hapus bila tak perlu. %%

```
`persona A` → `aksi` → `persona B (keputusan)` → `hasil`
```

## Skenario Gagal (opsional)

%% Failure paths yang penting dipahami developer (penolakan, validasi, guard). Hapus bila tak perlu. %%

- `kondisi gagal` → `akibat / penanganan`

## Dokumen Terkait

- `[[Dok domain/service induk]]` · `[[dok terkait lain]]`
