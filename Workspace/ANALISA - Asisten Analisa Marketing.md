# ANALISA - Asisten Analisa Marketing

Papan kerja hasil `/analisa-kebutuhan` 2026-09-22. Keputusannya di
[[ADR - 0120 Asisten Analisa Marketing Jadi Menu ERP, Template dan Jadwal Lebih Dulu Tanpa AI]].
Berkas ini berubah tiap item selesai.

**Empat item pertama adalah GERBANG**: murah, tidak menyentuh kode produksi, dan menentukan
apakah sisanya layak dikerjakan. G1 khususnya dapat membatalkan sebagian besar daftar ini.

---

## G1 — Buka layar yang sudah ada, bersama pemilik permintaan

**Status**: belum · **Memblokir**: seluruh irisan 1

Empat belas dari delapan belas halaman analitik sudah punya blok "Perlu tindakan". Pemilik
permintaan menyatakan belum pernah melihatnya, dan penyusun checklist manajemen menandainya
"Belum Mulai" dari melihat menu, bukan memeriksa kode.

Buka tiga layar bersama: Ringkasan (ubah rentangnya 7, 14, dan 30 hari, perhatikan vonisnya
berpindah dari "belum matang" ke "sehat"), Profit per Video tab GMV Max (blok "Perlu tindakan"),
dan Harga & Diskon serta Pelanggan & Cohort sebagai pembanding halaman yang sumbernya kosong.

**Yang harus terjawab**: apakah yang kurang bentuk kalimatnya, cara mengantarkannya, atau
cakupannya. Ketiganya menuntut pekerjaan yang sangat berbeda.

---

## G2 — Satukan target ROAS

**Status**: belum · **Memblokir**: kualitas seluruh vonis, bukan kelayakannya

Dashboard memakai 4,5, KPI Leader memakai 3,2. Selama dua angka beredar, setiap kalimat yang
menyebut sebuah kampanye atau orang "boros" memakai ambang yang belum disepakati siapa pun.

Keputusan manajemen, bukan pekerjaan developer. Sudah tercatat menunggu sejak
[[LOG - 2026-09-17 Audit Checklist Marketing dan Integration]].

---

## G3 — Putuskan siapa menyediakan daftar harga minimal

**Status**: belum · **Memblokir**: analisa apa pun di halaman Harga & Diskon

Halaman itu sudah punya tombol unggah dan simpan, tetapi sumbernya nol baris. Tanpa daftar
harga minimal, tidak ada pembanding untuk mendeteksi penjualan di bawah batas. Ini pekerjaan
Finance atau Marketing, bukan IT.

---

## G4 — Putuskan kepemilikan data jadwal

**Status**: belum · **Memblokir**: T2, T3

Asisten menyimpan jadwal, daftar penerima, dan riwayat kirim. Menaruhnya di marketing-analytics
membuat modul itu tahu soal penjadwalan dan notifikasi, yang bukan urusannya; menaruhnya di
tempat lain melahirkan pertanyaan service baru yang sudah dijawab ADR 0120 §1.

Putuskan sebelum koleksi pertama dibuat, karena memindahkannya sesudah ada data jauh lebih mahal.

---

# Irisan 1 — Template dan penjadwalan, TANPA AI

Memberi nilai penuh tanpa satu pun pemanggilan model.

## T1 — Katalog template analisa

**Status**: belum · **Dependensi**: G1

Daftar analisa siap pilih, dan setiap entri **wajib** menyebut sumber datanya beserta
keterbatasannya. Yang boleh masuk hanya yang datanya benar-benar ada.

Kandidat yang sudah terbukti punya data: ringkasan laba dan belanja iklan per periode,
perbandingan antar Account Specialist, penggerus dan peluang per level, video yang berbelanja
tanpa hasil di tab GMV Max, sesi live.

Yang **tidak boleh** masuk, beserta sebabnya: diskon mana yang menggerus laba (kolomnya belum
dipisah), konversi dan CPA iklan TikTok (cakupan di bawah 1%; Shopee justru lengkap), pola
musiman (riwayat efektif 8 bulan), Pelanggan & Cohort serta Harga & Diskon (sumber nol baris).

## T2 — Penyimpanan dan API jadwal

**Status**: belum · **Dependensi**: G4, T1

Menyimpan template yang dipilih, kekerapan, penerima, dan status aktif. Penerima ditulis
eksplisit, **tidak** diturunkan dari peran (ADR 0120 §6).

## T3 — Penjalan jadwal

**Status**: belum · **Dependensi**: T2

Harus tahan mati-hidup container dan tidak mengirim ganda. Perhatikan penjadwal mart yang sudah
ada aman hanya pada replika tunggal.

Kegagalan **wajib berbunyi**. Laporan yang berhenti tanpa ada yang tahu adalah bentuk kegagalan
paling umum di sistem ini.

## T4 — Kategori inbox dan pengiriman

**Status**: belum · **Dependensi**: T3

⛔ Kategori inbox baru hidup di daftar izin `shared-library`, sehingga marketing-analytics dan
notification-service **wajib naik bersamaan**. Sudah menggigit dua kali; gagalnya senyap.
Tujuan notifikasi memakai rute aplikasi, bukan URL eksternal (tidak berfungsi di MyBharata).

## T5 — Layar menu di frontend

**Status**: belum · **Dependensi**: T1, T2

Memilih template, mengatur jadwal, melihat riwayat kirim. Teks user-facing baru wajib lewat
`react-i18next` di dua locale (ADR 0010).

Setiap laporan membawa tautan ke layar yang menampilkan angkanya: laporan adalah pintu, bukan
tujuan.

## T6 — Ukur pemakaian, untuk kondisi berhenti

**Status**: belum · **Dependensi**: T4

Catat berapa laporan dibuka dan template mana yang dipilih. Tanpa ini, ADR 0120 §7 tidak dapat
ditegakkan, dan fitur akan hidup tanpa pernah ada yang memutuskan nasibnya.

Angka ini juga bahan utama merancang irisan 3.

---

# Irisan 2 — AI merangkai

**Bersyarat**: hanya dikerjakan bila T6 menunjukkan laporan irisan 1 benar-benar dibaca.

## T7 — Skema keluaran dan aturan kolom

**Status**: belum

Model menerima hasil hitung beserta penanda ketidakpastiannya, tidak pernah angka mentah
(ADR 0120 §4). Keluaran dikunci skema supaya dapat divalidasi sebelum dikirim.

Aturan yang wajib ikut: nilai pakai laba matang; `roas` null berarti tidak terhitung, bukan nol;
nol di level video dan level iklan berarti tidak diketahui; retur sudah terpotong di settlement.

## T8 — Integrasi klien AI

**Status**: belum · **Dependensi**: T7

Memakai `shared-library/ai` yang sudah ada, dipanggil dari service pemilik data. Pola asinkron
yang sudah terbukti ada di recruitment: goroutine terpisah, status tiga keadaan, dan penyaringan
ulang keluaran model meski skemanya sudah mengunci pilihan.

⚠️ Env `AI_*` dibaca saat container **dibuat**, jadi deploy menuntut `--force-recreate`. Saat ini
env itu hanya diinjeksikan ke blok recruitment di compose.

---

# Irisan 3 — Tanya-jawab bebas

**Bersyarat**: hanya bila T6 menunjukkan orang bertanya di luar template.

## T9 — Putuskan bentuk dan penghalangnya

**Status**: belum

Dua penghalang yang sudah diketahui dan belum dipilih jalan keluarnya: gateway membaca respons
penuh ke memori dengan batas 30 detik, sehingga giliran multi-alat dapat dibalas 502; dan hak
akses harus mengikuti orang yang bertanya, bukan satu identitas bersama.

Rancangan yang sudah ada di [[Microservices - Assistant Service]] menjadi bahan utama di sini.

---

# Yang sengaja TIDAK dikerjakan

- **Penambahan blok tindakan di tab Video selain GMV Max.** Diukur 2026-09-22: tab VSA berisi
  1.232 video yang 1.138 di antaranya juga muncul di tab GMV Max, VSA murni tinggal 94 video
  dengan belanja nol, dan seluruh belanja VSA 0,26% dari total. Hasilnya pengulangan, bukan
  cakupan baru. Alasan yang tertulis di kode sudah dikoreksi lewat erp-frontend #1680.
- **Rekomendasi anggaran iklan.** Simulasi alokasi sengaja dimatikan sejak 2026-08-15 karena
  hubungan belanja ke laba (R² 0,258) jauh lebih lemah daripada ke revenue (0,714).
- **Harness di netmon sebagai bagian produk.** Ia tetap alat uji (ADR 0120 §1).

---

## Terkait

- [[ADR - 0120 Asisten Analisa Marketing Jadi Menu ERP, Template dan Jadwal Lebih Dulu Tanpa AI]]
- [[ADR - 0058 Kapabilitas AI Digerbang Kelayakan Data, Bukan Kelayakan Teknologi]]
- [[Microservices - Marketing Analytics Service]]
- [[LOG - 2026-09-17 Audit Checklist Marketing dan Integration]]
