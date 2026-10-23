# sop_bharata: salin SOP BHARATA 2026 ke vault

Skrip yang menghasilkan dok `* - SOP Posisi *` (satu dok per posisi) dan
[[REF - SOP Bharata 2026 per Posisi]] dari folder SOP hasil ekspor Google Drive.
Isinya disalin apa adanya, tidak dirangkum. Dok hasilnya **jangan disunting tangan**:
jalankan ulang skrip ini supaya salinan tetap sama dengan sumber.

## Yang dikerjakan

| Berkas | Fungsi |
|---|---|
| `docx_struktur.py` | Membaca `.docx` (paragraf, tingkat daftar, tabel, teks kotak flowchart, kop) tanpa pustaka luar. `--dump <berkas>` mencetak strukturnya untuk diperiksa. |
| `tulis_vault.py` | Menulis 64 dok posisi + dok peta. Pemetaan folder sumber ke posisi, folder vault, dan prefix ada di daftar `POSISI`. |
| `cek_lengkap.py` | Gerbang kelengkapan: setiap paragraf dan sel tabel sumber wajib muncul di dok hasil. Harus `hilang=0`. |
| `isi_index.py` | Mengisi ringkasan `VAULT-INDEX` untuk dok-dok ini tanpa subagent (dari tabel "Daftar SOP" tiap dok). |

Yang sengaja dibuang: nama orang di blok tanda tangan (jabatan tetap dicatat), dan subfolder
`HRGA/HRD/PERSONALIA/KONTRAK KERJA` (data pribadi; repo vault ini publik).

## Cara pakai

Jalankan dari akar `erp/`, dengan venv vault, dan selalu `-I` karena folder sumber adalah unduhan:

```
PY=architecture-draft/Tools/.venv/Scripts/python.exe
SRC="<folder>/SOP BHARATA 2026"

# 1. SOP Inspeksi Diri berbentuk PDF: ambil teksnya dulu
pdftotext -enc UTF-8 "$SRC/QUALITY/QUALITY TEKNOLOGI PANGAN/1. INSPEKSI DIRI.pdf" <tmp>/inspeksi-diri.txt

# 2. tulis dok (menimpa dok SOP yang ada; menolak bila nama bertabrakan dengan dok lain)
$PY -I architecture-draft/Tools/sop_bharata/tulis_vault.py "$SRC" architecture-draft --vault architecture-draft --pdf-inspeksi <tmp>/inspeksi-diri.txt

# 3. gerbang kelengkapan
$PY -I architecture-draft/Tools/sop_bharata/cek_lengkap.py "$SRC" architecture-draft

# 4. index: --daftar-tugas, lalu isi_index.py <akar vault>, lalu --serap dan --check (lihat Tools/README.md)
```

Sesudah menulis, periksa `git diff`: SOP yang tidak berubah di sumber tidak boleh berubah di vault.

## Yang perlu diingat

- **Posisi atau folder baru di sumber** tidak otomatis masuk: tambahkan barisnya ke `POSISI`.
  `tulis_vault.py` mencetak `.docx` yang tidak masuk posisi mana pun; daftar itu harus berisi
  hanya dua berkas di akar sumber (form inspeksi lintas departemen dan bukti foto inspeksi).
- **Dua tabel penutup PDF Inspeksi Diri** disusun ulang di kode karena kolomnya tercampur di
  hasil `pdftotext`. Bila PDF-nya direvisi, skrip berhenti dengan pesan "tabel penutup tak cocok
  lagi"; perbarui bagian itu di `salin_pdf_inspeksi`.
- Sebelum push, sapu hasilnya untuk nama orang dan data pribadi. Di PowerShell 5.1 jangan pakai
  `Select-String -Quiet` atas banyak berkas di dalam `if` (selalu benar); gabungkan teksnya lalu
  `[regex]::IsMatch`, dengan kontrol positif.
