# Desain — `/dampak`: impact analysis antar-dok vault dan kode sebelum menyunting

- Tanggal: 2026-10-07
- Status: DRAFT, menunggu review
- Menyentuh: `Tools/dampak.py` (baru), `Tools/tests/test_dampak.py` (baru), `commands/dampak.md` (baru),
  `commands/analisa-kebutuhan.md` §5, `commands/sync-docs.md`, `rules/team-memory.md`, `VERSION` (1.36.0),
  `README.md` kit (changelog)
- Tidak menyentuh: kode repo mana pun, `build-vault-index.py`, skema `VAULT-INDEX.json`, hook git, judge
- Asal: sub-proyek 1 dari 3 hasil breakdown speckit.tech (2 lainnya, wawancara pilihan ganda dan blueprint
  per fitur, punya spec sendiri)

## 1. Masalah

SpecKit (speckit.tech) punya *Impact Analysis*: sebelum satu dokumen spesifikasi diubah, ia menunjukkan
dokumen lain yang ikut terdampak ("Change affects 3 docs") lalu menyelaraskannya. Kit kita tidak punya
padanannya:

- `/sync-docs` bekerja satu arah, **diff kode → dok**, lewat pemetaan repo→dok rulebook vault §7.
  Ia tidak mencari dok **lain** yang masih menyatakan fakta lama.
- `/analisa-kebutuhan` §5 menulis ADR + dok domain tanpa memeriksa dok yang sudah menyatakan hal
  sebaliknya.

Kelas bug yang paling sering tercatat di `rules/team-memory.md` justru ini: satu fakta (ambang, rumus,
daftar-izin, nama rute) hidup di dua tempat lalu menyimpang diam-diam (ambang KPI 75 vs 80, target profit
diketik di insentif dan template KPI). Tidak ada gerbang yang bertanya "di mana lagi fakta ini ditulis"
saat faktanya diubah.

## 2. Keputusan yang sudah diambil (brainstorming 2026-10-07)

| Pertanyaan | Keputusan |
|---|---|
| Wewenang | Lapor + usul suntingan dok, **terapkan setelah disetujui per dok**. Kode tidak disunting, hanya didaftar. |
| Pemicu | Manual (`/dampak`) + dipanggil `/analisa-kebutuhan` §5 dan `/sync-docs`. **Tanpa hook git.** |
| Mesin | Kandidat dihitung **skrip deterministik**, relevansi dinilai **agent**. Bukan prompt saja (tak bisa diulang/diuji), bukan embedding (infrastruktur belum ada, dan meleset untuk duplikasi literal). |

## 3. Skrip `Tools/dampak.py`

Deterministik, **read-only**, keluaran JSON ke stdout. Dijalankan dari venv vault seperti
`build-vault-index.py`.

### Input

```
dampak.py --root architecture-draft --sumber "<path atau judul dok>" --teks "<perubahan yang dimaksud>"
dampak.py --root architecture-draft --diff            # dok vault yang berubah di working tree vs HEAD
          [--repo-root <akar erp/>]                   # default: induk --root
```

`--teks` dan `--diff` saling eksklusif; salah satunya wajib.

### Output

```json
{
  "sumber": ["Decisions/ADR - 0079 ....md"],
  "fakta": ["80", "target_profit", "/kpi/template"],
  "kandidat_dok": [
    {"path": "...", "alasan": ["backlink", "fakta:80"], "status_emoji": "✅"}
  ],
  "kandidat_kode": [
    {"repo": "bip-erp", "ref": "origin/main", "berkas": "...", "baris": 42, "fakta": "target_profit"}
  ],
  "dilewati": [
    {"jenis": "fakta", "nilai": "5", "alasan": "angka satu digit"},
    {"jenis": "repo", "nilai": "mybharata-app", "alasan": "folder tidak ada"}
  ],
  "index_segar": true
}
```

### Aturan yang dikunci di skrip

1. **Graf** dari `VAULT-INDEX.json` (`dokumen[].tautan`):
   - tautan keluar dan backlink sumber, satu lompatan;
   - bila sumber berjenis ADR (`Decisions/`), ditambah lompatan kedua;
   - dok di `Workspace/`, `Logs/`, `Templates/` tidak ikut sebagai kandidat (bukan arsitektur, rulebook §2).
2. **Ekstraksi fakta**, dari `--teks` atau dari baris tambah/hapus `--diff`:
   - angka dengan ≥ 2 digit (termasuk desimal dan persen);
   - token `snake_case` (mengandung `_`);
   - path rute yang diawali `/`;
   - isi backtick `` `...` ``.
   Angka satu digit dan kata biasa masuk `dilewati`, tidak dibuang diam-diam.
3. **Fakta di vault**: cari literal tiap fakta di seluruh dok vault yang di-index. Fakta yang cocok di
   **lebih dari 40 berkas** ditandai `terlalu umum` dan masuk `dilewati`. Ambang 40 adalah konstanta bernama
   di skrip.
4. **Fakta di kode**: `git grep -n -F` atas **ref remote**, bukan working tree:
   `bip-erp` dan `erp-frontend` → `origin/main`, `mybharata-app` → `origin/dev`.
   Alasan: tool `Grep`/ripgrep melewati berkas ber-byte NUL, dan checkout lokal bisa ribuan commit
   tertinggal (team-memory § Gotchas lingkungan, § Memori & sumber kebenaran). `git grep` dijalankan dengan
   `-c core.fsmonitor=false`. Ambang "terlalu umum" yang sama berlaku per repo.
5. **Kesegaran index**: memakai ulang fungsi publik yang dipakai `--check`
   (`vault_index/build.py`): `pilih_yang_perlu_diringkas(scan_vault(root), muat_index(...), full=False)`
   tidak kosong = basi. Impor modul, bukan subprocess, dan tanpa menyalin aturannya.
   Basi → `index_segar: false`, **bukan** galat yang menghentikan proses.
6. Repo atau ref yang tidak ada → masuk `dilewati`, bukan crash.

Skrip tidak memutuskan relevansi. Ia cuma menjamin daftar kandidatnya sama setiap kali dijalankan atas
keadaan yang sama.

## 4. Command `commands/dampak.md`

Pemanggilan: `/dampak <dok-atau-ADR> "<perubahan yang dimaksud>"`, atau `/dampak --diff`.

1. **Siapkan.** `git -C architecture-draft pull --ff-only`. Gagal → lanjut dengan peringatan "salinan
   lokal basi" di kepala laporan. Jalankan `dampak.py`, simpan JSON ke scratchpad.
2. **Nilai kandidat dok.** Buka tiap kandidat dengan `Read` (bukan ringkasan index). Satu dari tiga vonis,
   masing-masing dengan alasan satu kalimat:
   - **Terdampak**: dok itu menyatakan fakta yang sama atau bergantung pada keputusan yang berubah. Wajib
     kutipan baris.
   - **Hanya menyebut**: menautkan, tidak memuat fakta yang berubah.
   - **Tidak terkait**: kecocokan kebetulan (mis. `80` sebagai port).
3. **Nilai kandidat kode.** Kelompokkan per repo. Tidak disunting. Fakta yang sama di ≥ 2 berkas kode
   ditandai ⛔ **duplikasi fakta** (team-memory § SATU FAKTA SATU TEMPAT) sebagai kandidat task.
4. **Sajikan laporan**, lalu **BERHENTI**:
   - ringkasan "Perubahan ini menyentuh N dok + M berkas kode";
   - tabel dok: vonis, kutipan, usulan suntingan (diff singkat);
   - bagian **Dibuang** (vonis "hanya menyebut"/"tidak terkait" + isi `dilewati`);
   - bagian **Kode (tidak disunting)**.
5. **Persetujuan per dok** lewat `AskUserQuestion` multiSelect. Yang tidak dipilih tidak disentuh.
6. **Terapkan** yang disetujui: sunting, perbarui status marker bila berubah, verifikasi 0 wikilink rusak
   (rulebook §4), `--check` index → `/index-vault` bila basi, commit per nama berkas
   `docs: selaraskan <fakta> (dampak dari <sumber>)`, merge `origin/main`, push `main` (konvensi vault).

**Batas tegas:**
- tidak menyunting kode;
- tidak menyunting dok sumber (itu tugas pemanggil);
- tidak membuat ADR. Bila perubahannya menyimpang dari ADR yang berlaku, laporan menyatakan
  **"butuh ADR"** dan berhenti tanpa langkah 5-6.

## 5. Integrasi

Masing-masing satu langkah, merujuk `commands/dampak.md`, **tanpa menyalin prosedurnya**:

- **`/analisa-kebutuhan` §5**: sebelum menulis ADR/dok domain yang **mengubah** fakta yang sudah tertulis di
  dok lain, jalankan `/dampak` atas draf artefaknya. Usulan suntingan ikut disajikan bersama persetujuan
  artefak, jadi tidak ada gerbang persetujuan kedua. Artefak yang murni menambah hal baru boleh lewat.
- **`/sync-docs`**, di antara langkah 4 dan 5: `dampak.py --diff` atas dok yang baru disunting, untuk
  menangkap dok **lain** yang masih menyatakan fakta lama.
- **`rules/team-memory.md`** § Skill & tooling: satu butir "sebelum mengubah fakta di vault, `/dampak`".

## 6. Pengujian `Tools/tests/test_dampak.py`

pytest, fixture = vault mini + `VAULT-INDEX.json` kecil + repo git sementara dengan remote lokal.

| Kasus | Harapan |
|---|---|
| Backlink dan tautan keluar | keduanya muncul, alasan tercatat |
| Sumber ADR | lompatan kedua ikut; sumber non-ADR tidak |
| Dok yatim | kandidat kosong, tanpa galat |
| Dok `Workspace/` bertautan | tidak jadi kandidat |
| Ekstraksi | angka ≥ 2 digit, snake_case, rute, backtick terambil; angka satu digit di `dilewati` |
| Fakta di > 40 berkas | `terlalu umum` di `dilewati` |
| Berkas hanya di working tree | **tidak** muncul (yang dibaca ref remote) |
| Berkas kode ber-byte NUL | **tetap** ditemukan |
| Repo tidak ada | `dilewati`, exit 0 |
| Index basi | `index_segar: false`, exit 0 |

**Kontrol negatif** (dijalankan sekali saat implementasi, dicatat di PR/commit): ubah pencarian kode jadi
working tree → kasus "hanya di working tree" merah; hapus pengecualian `Workspace/` → kasusnya merah.

Sebelum implementasi, periksa apakah `Tools/tests/` dijalankan oleh pre-push vault / `hooks/gerbang-kit.py`.
Bila tidak, `test_dampak.py` didaftarkan di sana (catatan 1.35.0: test yang tak didaftarkan tak pernah jalan).

## 7. Rilis

`VERSION` → `1.36.0`, entri changelog di `README.md` kit. `init` menyalin `commands/dampak.md` ke
`.claude/commands/`; `Tools/dampak.py` tinggal di vault sehingga cukup `git pull`.

## 8. Di luar lingkup

- Hook pre-commit vault yang memperingatkan dok tertaut tak ikut berubah (ditolak: berisik).
- Membuat brief otomatis untuk kandidat kode.
- Pencarian semantik/embedding.
- Wawancara pilihan ganda dan blueprint per fitur (sub-proyek 2 dan 3).
