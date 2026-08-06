# Tools — Vault Index

Generator `VAULT-INDEX.json`, manifest pencarian untuk seluruh vault.
Desain lengkap: `.agent-kit/docs/2026-07-20-vault-index-rag-design.md`

Ringkasan dibuat **subagent Claude Code**, bukan Anthropic API. Tidak ada API key,
tidak ada biaya di luar langganan. Paket `anthropic` sengaja **tidak** terpasang; ada
dua tes yang menguncinya.

## Setup

```
py -3 -m venv Tools/.venv
Tools/.venv/Scripts/python.exe -m pip install -r Tools/requirements.txt
```

Jangan pakai `python` global — di banyak mesin tim itu menunjuk ke venv proyek lain.

## Pemakaian

Cara normal: **`/index-vault`** di Claude Code. Command itu menjalankan seluruh alur
dan menyebar subagent untuk meringkas.

Manual, dari akar `erp/`:

| Perintah | Fungsi |
|---|---|
| `--check --root architecture-draft` | Exit 1 bila index basi. Tidak menulis apa pun. |
| `--daftar-tugas --pecah 25 --root architecture-draft` | Tulis `VAULT-INDEX.tugas.NNN.json` untuk difan-out |
| `--serap --root architecture-draft` | Gabungkan seluruh `VAULT-INDEX.hasil.*.json`, tulis manifest |
| `--full` | Dipakai bersama `--daftar-tugas`: abaikan hash, masukkan semua |

`--check` dipanggil di akhir `/sync-docs`.

## Tes

```
cd Tools && .venv/Scripts/python.exe -m pytest tests/ -v
```

## Yang perlu diingat

- **Fail-closed**: folder yang belum terdaftar di `vault_index/paths.py` otomatis
  `publik: false`, begitu juga berkas `.md` baru di akar vault yang tidak ada di
  allowlist dok meta. Menambah folder domain baru? Daftarkan di `KLASIFIKASI`.
- **`IT/` tidak pernah `publik: true`** — memuat kredensial plaintext yang disengaja
  untuk tim IT, tapi tidak boleh masuk kanal chat tim non-IT.
- **Status disimpan mentah**, tidak dinormalisasi. Enam emoji dipakai di vault
  (✅ ⚠️ 🟡 🔴 🔜 ⛔), dan sekitar sepertiga dokumen memang tidak punya status
  (seluruh dok meta root dan seluruh `API - *`).
- **Dua format status, dua-duanya sah.** `- **Status**:` (bullet, dipakai template
  Implementasi Service & Konsep Domain) dan `> **Status**:` (blockquote, dipakai
  template Runbook). Sampai 2026-08-06 parser hanya mengenali yang pertama, jadi
  12 runbook + 3 ADR + 2 Application + 1 Sales terbaca tanpa status — padahal
  semuanya menulisnya dengan benar menurut templatenya. Menambah format ketiga?
  Perbarui `_RE_STATUS` **dan** tesnya, jangan menyuruh dok menyesuaikan parser.
- **Peringatan status memeriksa `domain`, `adr`, dan `runbook`.** Tiga jenis itu
  wajib bawa status; `log`/`template`/`workspace` dikecualikan oleh `CLAUDE.md` §2,
  sedangkan `api`/`meta` memang normal tanpa status. Runbook dulu tak diperiksa —
  itu sebabnya salah-baca di atas tak pernah bersuara. Menambah jenis baru yang
  wajib berstatus? Daftarkan di `_peringatan_status`.
- **Rusak bukan berarti kosong.** Berkas hasil yang bentuknya tidak dikenali akan
  **menolak seluruh operasi**, bukan dianggap tidak berisi. Dua kali di proyek ini
  perlakuan "anggap kosong" menyebabkan kehilangan data.
- **Jumlah dokumen bergerak.** Vault ditulis banyak orang. Jangan menuliskan angka
  korpus sebagai assertion di tes; pakai `--check` untuk angka terkini.
