> **Papan kerja**, bukan dokumen arsitektur. Berubah tiap item selesai. Keputusannya ada di
> `Decisions/ADR - 0123 Preventive Maintenance Berjadwal per Aset di Inventory Service, Skor dari Penyelesaian Berbukti.md`;
> cara kerjanya di `General Affairs/GA - Building Maintenance.md`. Yang di sini cuma urutan kerjanya.
>
> ⚠️ Berkas ini di `Workspace/`, jadi dok yang terbit ke wiki DILARANG menautkannya.

# Preventive Maintenance Berjadwal per Aset — daftar task

Disusun 2026-09-24 dari ADR 0123. Membuka **0,55 bobot** di dua posisi: `Realisasi Preventif Maintenance Building & Fasilitas` (0,30, posisi Building Maintenance) dan `Persentase SLA Preventife Maintenance Alat Operational Tepat Waktu` (0,25, posisi GA Staff).

## Urutan dan ketergantungan

```
T0 (GA, bukan dev) ──┐
                     ├── T5 ── T7 ── T8
T1 ── T2 ── T3 ── T4 ┘
      └── T6 ────────┘
```

T1 sampai T4 bisa jalan tanpa menunggu T0. **T7 dan T8 tidak bisa** — tanpa isi jadwal, penyebutnya nol dan tak ada yang bisa dibuktikan.

## T0 — GA menyusun daftar perawatan berkala per aset ⛔ BUKAN PEKERJAAN DEV

Sumbernya dokumen GA **"Checklist Jumlah Aset yang di-maintenance"**, yang **belum diperiksa isinya** saat papan ini dibuat. Yang dibutuhkan per baris: aset mana (cocokkan ke `inventory`, 899 dokumen di prod), pekerjaan apa, dan **frekuensinya**.

⚠️ Ini penghalang sesungguhnya, dan ia tidak hilang dengan menulis kode. Yang perlu dijawab lebih dulu: apakah daftarnya tetap tiap bulan, atau berubah mengikuti apa yang sempat dikerjakan. Kalau yang kedua, ia bukan jadwal melainkan catatan realisasi, dan penyebutnya harus dicari dari tempat lain.

## T1 — Koleksi dan CRUD `pm_jadwal` di inventory-service

`(company_id, asset_id, pekerjaan, frekuensi, mulai_berlaku, aktif, dibuat_oleh, dibuat_pada)`.

- `asset_id` **merujuk** `inventory`, jangan menyalin nama atau kategorinya. Satu fakta satu tempat.
- Gerbang mengikuti yang sudah dipakai `/perlengkapan-opname` (`gateGa`), jangan merakit gerbang baru.
- Frekuensi ditetapkan eksplisit: bulanan, triwulan, semesteran, tahunan. **Sub-harian tidak didukung** dan bukan lingkup ini.
- ⚠️ Nama koleksi ditulis sebagai **literal** di argumen pemanggilan koleksi, jangan konstanta bernama: penjaga soft-delete di repo ini hanya mengenali literal dan akan lolos diam-diam tanpa memeriksa apa pun.

## T2 — `pm_realisasi` + unggah foto + verifikasi

`(company_id, jadwal_id, period_key, tanggal_selesai, pelaksana, foto_sebelum[], foto_sesudah[], catatan, status, diverifikasi_oleh, diverifikasi_pada, alasan_tolak)`.

- **Foto wajib**, realisasi tanpa foto ditolak di server. Ini inti keputusannya, bukan validasi kosmetik.
- Status: `menunggu` → `diverifikasi` | `ditolak`. SPV **tidak memberi angka**, hanya menerima atau menolak beserta alasan.
- Pola unggah meniru track Inspeksi Area (submit dulu lalu unggah), jangan membuat alur unggah baru.

## T3 — Penurunan jatuh tempo, sebagai FUNGSI MURNI

Dari `(frekuensi, mulai_berlaku, period_key)` menghasilkan daftar jadwal yang jatuh tempo pada periode itu.

⚠️ **Wajib fungsi murni dengan test sendiri.** Inilah penyebut seluruh metrik; kalau ia salah, angkanya tetap masuk akal dan tak ada yang berbunyi. Kasus tepi yang harus dikunci: `mulai_berlaku` di tengah periode, jadwal yang baru dinonaktifkan, periode sebelum `mulai_berlaku`, dan frekuensi yang tidak jatuh tempo pada periode berjalan.

## T4 — `GET /internal/pm-metrik?periode=`

Mengembalikan per karyawan: jatuh tempo, terverifikasi, menunggu, dan nilainya.

- Realisasi ber-status `menunggu` **keluar dari pembilang dan penyebut** (ADR 0123 §6).
- Jatuh tempo nol menghasilkan **nilai absen**, bukan 0 dan bukan 100.
- ⚠️ `/internal/` **bukan** batas keamanan: gateway tetap meneruskannya dari internet, jadi endpoint ini wajib memeriksa identitas pemanggil sendiri.
- ⚠️ Balasan kosong dikirim sebagai daftar kosong yang eksplisit, bukan `null`. Konsumen ber-pointer tak bisa membedakan `null` dari kunci yang hilang.

## T5 — Sumber KPI `pemeliharaan_preventif` di employee-service

Memetakan payload T4 jadi `Cuplikan`. **Jangan menghitung ulang di sini** — definisi kedua akan menyimpang diam-diam dan angkanya tetap tampak masuk akal.

- Scope `individu`, sama seperti sumber sejenis.
- Isi `Rincian` supaya layar detail metrik tidak kosong: baris per aset yang jatuh tempo beserta keadaannya. Hanya 7 dari 27 sumber KPI yang mengisinya, dan yang tidak mengisi membuat layar rinciannya hampa.
- Penulis `kpi_score` tetap `POST /kpi`, tidak berubah.

## T6 — Layar GA di erp-frontend

Tiga hal: daftar jatuh tempo bulan berjalan, tandai selesai + unggah foto, dan antrean verifikasi SPV.

- Struktur halaman daftar mengikuti pola tabel HRIS, jangan merakit tabel dan filter sendiri.
- Seluruh teks lewat `react-i18next`, kunci di **dua** berkas locale.
- ⚠️ Antrean verifikasi sebaiknya menumpang agregator antrean persetujuan terpusat yang sudah ada, bukan membuat kotak masuk sendiri.
- ⚠️ Layar verifikasi **wajib menampilkan tunggakan beserta umurnya**. Karena yang `menunggu` keluar dari kedua sisi rasio, tunggakan yang mengendap menjadi tak terlihat di angka; kalau layarnya juga tidak menampilkannya, ia hilang sama sekali.

## T7 — Pasang metrik ke dua template ⛔ KONFIGURASI, BUKAN KODE

Pasang sumber `pemeliharaan_preventif` ke metrik 0,30 di `Building and Maintenance Staff` dan metrik 0,25 di `General Asset Staff HRGA`.

- **Bobot, target, dan arah TIDAK diubah** — diatur SK.
- Butuh T0 sudah terisi. Memasang sumber di atas jadwal kosong menghasilkan nilai absen, dan itu akan terbaca sebagai fitur gagal.

## T8 — Verifikasi end-to-end lewat gateway

⛔ `docker ps` dan `/health` **tidak diterima sebagai bukti**. Yang membuktikan: satu jadwal dibuat, satu realisasi diunggah berfoto, SPV memverifikasinya, lalu angkanya muncul di scorecard — seluruhnya lewat gateway, bukan lewat panggilan lokal ke service.

Urutan deploy: inventory-service dan employee-service naik **lebih dulu**, baru frontend. Tidak ada kategori inbox baru, jadi notification-service tidak wajib ikut. Tidak ada env baru, jadi `--force-recreate` tidak diperlukan.

## Ukuran keberhasilan, dan kapan dinyatakan gagal

⛔ **Bukan "modulnya jadi".** Tiga mekanisme sebelumnya di lingkup ini dibangun lalu tidak pernah terisi: modul Training dengan `quiz_attempt` **0**, sumber Satgas dengan **nol form**, dan form Checklist OB dengan **1 jawaban** lalu ditutup.

Ukurannya: **dokumen Google teknisi berhenti dipakai**. Bila setelah **dua periode** teknisi masih mengetik di sana, keputusan ini gagal dan layak ditinjau ulang, bukan ditambal dengan pengingat.

## Yang sengaja TIDAK dikerjakan di sini

- **Metrik biaya** (0,35 Building + 0,20 GA Staff) menunggu master anggaran GA yang belum ada. Itu rumpun tersendiri berbobot 1,05 di tiga posisi, dan layak analisanya sendiri.
- **Patroli Security tiap 3 jam** (0,30) bentuknya berbeda dan sudah punya keputusan sendiri di ADR 0112.
- **Catatan resmi perbaikan kerusakan** (tiket atau `repair_history`) masih TBD; ADR 0123 hanya menetapkan tempat perawatan berkala.
- **Metrik kebersihan OB dan Security** bergantung pada redesign Satgas di ADR 0122, bukan pada papan ini.
