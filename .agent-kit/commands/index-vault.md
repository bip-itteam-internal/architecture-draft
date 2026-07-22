---
description: Bangun/segarkan VAULT-INDEX.json (manifest pencarian vault) — ringkasan dibuat subagent
argument-hint: [--full]
---

Bangun atau segarkan `architecture-draft/VAULT-INDEX.json`, manifest yang dipakai
`/ask` dan `/start-task` untuk memilih dokumen relevan dari sebuah pertanyaan.

Argumen: $ARGUMENTS (kosong = incremental, hanya dokumen yang berubah; `--full` = semua)

Ringkasan dibuat oleh subagent Claude Code, **bukan API**. Tidak ada biaya di luar
langganan. Jangan pernah memasang paket `anthropic` atau memanggil Anthropic API di
alur ini — ada dua tes yang menguncinya.

Semua perintah dijalankan dari **akar `erp/`** (bukan dari dalam vault). Sebut
interpreter venv-nya eksplisit; `python` global di banyak mesin tim menunjuk ke venv
proyek lain.

```
PY=architecture-draft/Tools/.venv/Scripts/python.exe
CLI=architecture-draft/Tools/build-vault-index.py
```

## Langkah

**1. Cek dulu apakah ada yang perlu dikerjakan.**

```
$PY $CLI --check --root architecture-draft
```

Exit 0 berarti index sudah sinkron — laporkan dan **berhenti**, jangan lanjut.
Exit 1 berarti ada dokumen yang belum terwakili. Perintah ini juga memperingatkan
bila ada artefak `VAULT-INDEX.tugas*.json` / `VAULT-INDEX.hasil*.json` tertinggal
dari run yang gagal sebelumnya; kalau ada, lanjutkan dari langkah 3 memakai artefak
itu alih-alih membuat yang baru.

**2. Pecah jadi potongan.**

```
$PY $CLI --daftar-tugas --pecah 25 --root architecture-draft $ARGUMENTS
```

Menulis `architecture-draft/VAULT-INDEX.tugas.NNN.json`. Untuk perubahan rutin
`/sync-docs` yang menyentuh 2 sampai 3 dokumen, ini cuma menghasilkan satu potongan.

**3. Sebar subagent, satu per potongan.**

Kirim **seluruh potongan dalam satu pesan** supaya jalan paralel. Tiap subagent
menerima path potongannya sendiri dan tidak perlu konteks lain — berkas potongan
sudah memuat panduan lengkap, bentuk keluaran, dan nama berkas hasil yang harus
ditulis.

Prompt untuk tiap subagent (ganti `NNN`):

> Baca `architecture-draft/VAULT-INDEX.tugas.NNN.json`. Berkas itu memuat field
> `panduan` yang menjelaskan gaya ringkasan yang diminta, bentuk JSON keluaran, dan
> nama berkas yang harus kamu tulis (`berkas_keluaran`). **Ikuti panduan itu persis.**
>
> Untuk tiap entri di `tugas`, buat `ringkasan` dan `kata_kunci` berdasarkan `isi`.
> Salin kembali `path` dan `hash` apa adanya — `hash` dipakai untuk mendeteksi
> dokumen yang berubah selagi kamu bekerja, dan entri tanpa hash yang cocok akan
> ditolak.
>
> Tulis hasilnya ke berkas yang disebut `berkas_keluaran`, di dalam folder
> `architecture-draft/`. Jangan menulis berkas lain, jangan mengubah dokumen vault,
> jangan menjalankan git.
>
> Balas singkat: jumlah dokumen yang kamu ringkas dan nama berkas yang kamu tulis.

**4. Serap.**

```
$PY $CLI --serap --root architecture-draft
```

Menggabungkan seluruh berkas hasil, memvalidasi, menulis `VAULT-INDEX.json`, lalu
menghapus artefak sementara **hanya bila serap bersih sepenuhnya**.

Kalau ada entri ditolak, basi, atau tak ditemukan: exit non-nol dan artefak
**dipertahankan**. Baca laporannya, perbaiki berkas hasil yang bermasalah (atau
suruh ulang subagent untuk dokumen itu saja), lalu jalankan `--serap` lagi.

**5. Verifikasi.**

```
$PY $CLI --check --root architecture-draft
```

Harus exit 0. Lalu periksa `VAULT-INDEX.json`: jumlah dokumen masuk akal, `gagal`
kosong, dan tidak ada dokumen `IT/`, `Workspace/`, `Logs/`, atau `Templates/` yang
bernilai `publik: true`.

**6. Commit.**

Stage **per-nama berkas** (`git add -- VAULT-INDEX.json`), jangan `git add -A` —
vault dikerjakan banyak orang dan sering ada perubahan yang belum di-commit. Jangan
sertakan berkas `VAULT-INDEX.tugas*` / `VAULT-INDEX.hasil*`; keduanya sudah
di-gitignore.

## Yang perlu diingat

- **Jangan mengarang ringkasan tanpa membaca dokumennya.** Isi tiap dokumen sudah
  disertakan di potongan; tidak perlu membuka berkas aslinya, tapi juga tidak boleh
  menebak dari judul.
- **Status implementasi tidak diringkas LLM.** Marker ✅/⚠️/🟡/🔴/🔜/⛔ diambil
  deterministik oleh skrip. Subagent tidak boleh menyimpulkannya.
- Dokumen 🔴 Stub tidak masuk daftar tugas; ringkasannya dibuat lokal.
- Kalau `--serap` menolak karena bentuk berkas salah, **jangan hapus berkasnya** dan
  jangan ulangi dari nol. Bentuk yang benar ada di `panduan`; biasanya cukup
  membungkus ulang isinya.
