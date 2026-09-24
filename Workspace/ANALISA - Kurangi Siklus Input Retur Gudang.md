> Papan kerja hasil `/analisa-kebutuhan` 2026-09-24. Keputusannya di [[ADR - 0124 Input Retur Gudang Diukur Komposisinya Dulu, Lalu Konfirmasi Massal Hanya untuk Baris Cocok]], cara kerja alurnya di [[Microservices - Manufacture Service]]. Berkas ini berubah tiap item selesai; keduanya di atas tidak.

# Daftar Task

Dua task pertama adalah **gerbang**. Keduanya murah, tidak menyentuh kode produksi, dan hasilnya
menentukan apakah T4 dan seterusnya layak dikerjakan sama sekali. Mengerjakan T4 sebelum
gerbangnya lulus berarti mengulang persis preseden sweep 0-dari-5 di [[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]].

---

## Gerbang

### T1. Ukur komposisi siklus input retur

**Blocking untuk seluruh pelaksanaan.** ADR §1.

Angka yang dipakai menyusun keputusan ini, 854 submit per orang per bulan, **diturunkan dari
kesamaan total** `manufacture_audit_log` (17.755) dan `manufacture_transaksi` (17.715). Itu
inferensi, bukan ukuran. Bila satu paket ternyata memuat banyak baris, jumlah siklusnya jauh
lebih kecil dan ADR ini gugur.

Yang wajib terukur di produksi (baca-saja):

1. **Submit per hari per orang** — hitung dokumen `manufacture_transaksi` bertipe retur per hari
   per penginput, bukan per baris.
2. **Sebaran jumlah baris per paket** — berapa entri di dalam blob `detail` tiap transaksi.
   Median dan p90, bukan rata-rata.
3. **Porsi paket yang SELURUH barisnya cocok** dengan klaim marketplace. Ini yang menentukan
   seberapa besar gerbang konfirmasi massal di ADR §2 benar-benar menjangkau.

⚠️ `manufacture_transaksi` **tidak punya field tanggal di tingkat atas** (terbukti saat screening
2026-09-24: `per30d` balik `null`). Tanggalnya harus dicari di dalam dokumen lebih dulu; jangan
simpulkan nol dari ketiadaan field.

Keluaran: tiga angka di atas, masuk ke ADR sebagai koreksi bila berbeda dari dugaan.

Dependensi: tidak ada.

### T2. Ukur baseline proporsi rework dan reject per orang

**Blocking untuk T5.** ADR §4.

Angka 8,8% rework dan 1,1% reject berasal dari survei 2026-09-14 dan bersifat agregat. Gerbang
penerimaan ADR §4 menuntut perbandingan pra dan pasca, jadi baselinenya harus **per orang**,
bukan satu angka perusahaan: bila satu orang sudah hampir tak pernah mencatat kerusakan, turunnya
proporsi sesudah perubahan tak bisa dibedakan dari kebiasaannya sendiri.

Keluaran: proporsi per penginput, beserta jumlah baris tiap orang supaya proporsi dari sampel
kecil tidak dibaca setara.

Dependensi: tidak ada. Boleh paralel dengan T1.

---

## Prasyarat verifikasi

### T3. Baca kode yang belum sempat diverifikasi langsung

Grounding 2026-09-24 kehabisan kuota model sebelum dua agen backend selesai, sehingga empat hal
di bawah bersandar pada dokumentasi vault, **bukan pembacaan kode**. Semuanya perlu dikonfirmasi
sebelum T5 dikerjakan, dan salah satunya bisa mengubah ADR:

1. `deltaStokTransaksi` benar-benar menambah **seluruh** qty (bukan `reuse+rework`). ADR 0025 dan
   catatan Inbox 2026-07-17 menyatakan begitu; kodenya belum dibaca di sesi itu.
2. Gerbang RBAC rute input retur, dan apakah konfirmasi massal akan mewarisinya apa adanya.
3. Aturan pemakaian kolom `qtyReuse`/`qtyRework`/`qtyReject` terhadap `quantity` induknya:
   komponen sejajar atau himpunan bagian. Wajib dijawab eksplisit, dengan kutipan komentar Go-nya.
4. Apa yang menulis `detail.status`. Di produksi seluruh baris bernilai `REUSE` dan field itu
   **tidak mencerminkan kondisi barang** — pencarian yang sempat berjalan tidak menemukan penulis
   di sisi Go, jadi kemungkinan besar dikirim frontend. Perlu dipastikan sebelum ada aksi massal
   yang ikut menuliskannya.

Dependensi: tidak ada. Boleh paralel dengan gerbang.

---

## Pelaksanaan

### T4. Putuskan mekanisme seleksi baris

`MainTable` **tidak punya seleksi baris sama sekali** (`git grep enableRowSelection|rowSelection`
di erp-frontend: nol hasil). Satu-satunya tabel di repo yang punya adalah `IntegrationTable`
(`selectedIds`, `onToggleSelect`, `onToggleSelectAll`, checkbox tri-state), tetapi ia bergaya
visual modul Integration dan bertipe khusus.

Tiga jalan, dan pilihannya keputusan tersendiri: menambah seleksi ke `MainTable` (ongkosnya jatuh
ke puluhan halaman, dan aturan tim menahan penambahan prop ke komponen shared demi satu
pemanggil), meniru polanya secara lokal di fitur manufacture, atau memakai `IntegrationTable` apa
adanya dan menerima gaya visualnya.

⚠️ Layar ini **belum memakai struktur tabel HRIS sama sekali** (nol impor `@/components/table`,
nol `useTableState`, tabel dirakit tangan). Jadi "pakai `MainTable`" di sini bukan penyesuaian
kecil melainkan migrasi.

Keluaran: putusan tertulis beserta alasannya, masuk ke dok domain.

Dependensi: **T1 lulus.**

### T5. Konfirmasi massal untuk paket yang seluruh barisnya cocok

ADR §2. Hanya paket ber-badge cocok yang boleh dipilih banyak lalu disimpan sekaligus; yang
kurang atau lebih tetap lewat form satu per satu.

Yang wajib diputuskan di dalam task ini:

- **Apa yang disimpan.** Konfirmasi massal tetap membuat transaksi per paket, bukan satu
  transaksi gabungan, supaya jejak dan stempel penginputnya tidak berubah bentuk.
- **Tampilan untuk paket yang gagal di tengah batch.** Sebagian berhasil sebagian tidak adalah
  keadaan normal; yang gagal wajib disebut beserta sebabnya, bukan dilewati diam-diam.
- **Batas ukuran batch**, supaya satu aksi tak melewati batas 30 detik gateway.

Dependensi: **T1, T2, T3 lulus, dan T4 sudah berbentuk.**

### T6. Jamin idempotensi per paket sebelum tombolnya ada

ADR §5. Form sekarang selalu membuat transaksi baru dan **tidak punya jalur edit**, jadi simpan
kedua menambah stok dua kali. Aksi massal memperbesar permukaan kesalahan yang sama karena satu
klik menyentuh banyak paket.

Ini bukan penyempurnaan T5 melainkan syaratnya: dikerjakan lebih dulu di dalam task yang sama,
dengan test yang membuktikan pengiriman ulang tidak menambah stok.

Dependensi: bagian dari T5, dicatat terpisah supaya tidak tergeser.

### T7. i18n untuk seluruh teks yang tersentuh

Layar ini warisan tanpa i18n: hanya **2 kunci** (`manufacture.returTanpaResi`,
`manufacture.returTanpaResiHint`), sisanya hardcoded Indonesia, dan komentar di berkasnya sendiri
mengakuinya. Tiap teks baru atau tersentuh wajib kunci di `id.ts` **dan** `en.ts`
([[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]]).

⚠️ Kedua berkas locale itu yang paling sering disunting paralel. Sebelum merge: `git merge
origin/main` lokal, lalu `pnpm tsc` **dan** `pnpm build`. Auto-merge git pernah menelan kurung
tutup sehingga seluruh build mati.

Dependensi: bagian dari T5.

---

## Perapian yang berdiri sendiri

### T8. Koreksi dok yang basi soal Reject menambah stok

[[Microservices - Manufacture Service]] masih menuliskan "Qty Reject pada retur ikut menambah
stok FG, padahal reject seharusnya ke scrap, belum diperbaiki" sebagai gap terbuka. Keputusan
22 Juli 2026 **membalik arahnya**: ketiga kondisi memang sama-sama menambah stok, dan catatan
temuannya ditutup dengan "jangan memperbaiki ini balik ke scrap".

Siapa pun yang membaca dok itu untuk mengerjakan T5 akan menyimpulkan ada bug yang harus ikut
dibereskan. Dikoreksi bersama ADR ini; dicatat di sini supaya terlihat sudah dikerjakan.

Dependensi: tidak ada.

### T9. Periksa apakah BALIK_RM punya pola yang sama

Catatan `Workspace/Inbox/2026-07-17 Temuan - Reject retur menambah stok FG` menyisakan satu
pertanyaan yang **belum dijawab di mana pun**: apakah `GudangBahanBakuView` (tab BALIK_RM, kolom
`qtySj`/`qtyLolos`/`qtyReject`) memiliki pola pengurangan stok yang sama dengan yang dulu keliru
di Gudang Barang Jadi.

Bukan bagian dari ADR ini, tetapi ditemukan saat menyusunnya dan akan hilang bila tidak dicatat.

Dependensi: tidak ada.

---

## Catatan

- Seluruh angka di papan ini berasal dari pengukuran produksi **2026-09-24** (baca-saja, 19
  container Mongo) dan survei **2026-09-14**. Skrip pengukurannya ada di
  `.task-plans/2026-09-24-screening-kerja-manusia.{js,ps1}` dan
  `.task-plans/2026-09-24-screening-persetujuan.{js,ps1}`.
- ⚠️ Query produksi diblokir classifier untuk agent (`[Production Reads]`); skrip dijalankan
  manusia lalu keluarannya ditempel. Task yang butuh angka baru wajib menyiapkan `.ps1` sejak
  awal, bukan mencoba menjalankannya sendiri.
- Dua kandidat lain yang ikut diperiksa 2026-09-24 **sengaja tidak masuk papan ini**, dan
  alasannya dicatat supaya tidak diusulkan ulang: verifikasi **kas kecil** mengantre di modul yang
  sedang dipensiunkan bertahap (69 dokumen, tidak bertambah sejak 2026-08-26, menu sidebar sudah
  dicabut), dan **`permintaan_barang`** ternyata cermin baca-saja Accurate yang layarnya tidak
  lagi dirender sejak 2026-08-06 sehingga 39 baris `WAITING` di sana tidak mengukur kerja manusia
  mana pun. **Pemetaan SKU** juga tidak masuk: alat berbasis pengecualiannya sudah ada (halaman
  Mapping SKU secara bawaan hanya menampilkan yang perlu dipetakan, plus jalur massal Excel
  [[ADR - 0077 Koreksi Faktur via Impor Rekap Lengkap Mengalir ke Master-Data, Bukan Override per Baris]]),
  dan vault melarang tegas arah menebaknya.
- Tiap task dilempar ke `/start-task` satu per satu, bukan sekaligus.
