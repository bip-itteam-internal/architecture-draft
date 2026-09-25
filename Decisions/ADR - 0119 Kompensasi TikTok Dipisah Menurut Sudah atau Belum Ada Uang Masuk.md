## Untuk Manajemen

Kompensasi TikTok atas pesanan yang uangnya **sudah pernah cair** dan **tidak punya dokumen retur** tidak lagi menambah nilai bayar faktur — fakturnya sudah lunas, jadi menambahnya berarti membayar dua kali. Kompensasi semacam itu dicatat sebagai **Pendapatan Lain-lain tanpa mengisi nilai bayar**. Dua keadaan lain **tidak berubah**: pesanan yang **belum pernah menerima uang** (batal, paket hilang di logistik) tetap dilunasi kompensasinya, dan pesanan yang **sudah punya retur** tetap dicatat sebagai income biasa — returnya yang membalik penjualan, kompensasi cuma menggantikan refund yang keluar.

Terukur di produksi 25 September 2026: **11 pesanan senilai Rp1.328.198** yang perlu dibetulkan, berhadapan dengan **375 pesanan senilai Rp36,1 juta** yang sudah benar dan tidak disentuh. Dari 11 itu, yang benar-benar dibetulkan sistem **7 pesanan** (penerimaannya jatuh di September); sisanya dimasukkan manual atas permintaan finance. **Nilai uang yang diterima tidak berubah sama sekali** — yang bergeser hanya ke mana ia dibukukan.

**Terdampak**: tim AR/finance yang menelusuri piutang minus dan kompensasi TikTok. **Yang TIDAK dijanjikan**: membetulkan pesanan yang penerimaannya di luar September, membereskan retur lama yang menggantung menunggu scan gudang, mengubah aturan kanal Shopee, menyediakan tuas koreksi untuk pemindahan pelunasan yang hari ini masih ditolak sistem, dan memperbaiki 138 penerimaan TikTok berstatus gagal yang dokumennya tertinggal versi lama (Rp21,3 juta — masalah tersendiri). **Besaran kerja**: sedang — kecil di nominal, tetapi tiga tempat harus berubah bersamaan.

## Deskripsi

*Penyesuaian statement TikTok dipisah oleh **dua pembeda**: pesanannya sudah pernah menerima uang atau belum, lalu punya Retur Penjualan atau tidak. Belum pernah ada uang masuk → kompensasi melunasi faktur (perilaku sekarang, dari [[ADR - 0056 Penyesuaian Statement TikTok Menambah Payout Order]]). Sudah ada uang masuk tapi ADA retur → tetap income biasa. Sudah ada uang masuk dan TANPA retur → kompensasi jadi baris Pendapatan Lain-lain tanpa menyentuh bayar faktur. Gerbang retur memakai pembeda pertama yang sama, dan seluruhnya digerbangi kv tanggal per hari penerimaan.*

- **Status**: ⚠️ **Implemented (ada catatan)** — kode selesai di branch `feat/tiktok-kompensasi-payout` (2026-09-25), **belum merge, belum deploy, kv cutover belum diisi**. Selama kv kosong perilakunya persis seperti sebelum ADR ini ada. Aturannya diputuskan finance (tiket "Revisi Sistem Income" + penegasan 2026-09-22, 09-24, dan 09-25).
- **Path di repo**: `bip-erp/services/integration/internal/usecase/kompensasi_tiktok.go` **(baru)** · `internal/usecase/accurate_rts_usecase.go` (`diserapPenyesuaianStatement`) · `internal/usecase/accurate_receipt_usecase.go` (`processTiktokStatement`) · `internal/usecase/accurate_receipt_export_detail.go` (`dikompensasi`) · `internal/usecase/penyesuaian_tanpa_order.go` (`tempelPotonganPendapatanLain`, mekanik dipakai bersama) · `internal/domain/entity/accurate.go` (kv `tiktok-kompensasi-cutover-date`) · `internal/domain/entity/transaction.go` (`PayoutSebelumPenyesuaian`, `PayoutCair`) · `internal/infrastructure/repository/transaction_repo.go` (`terapkanPenyesuaian`, `incomeHanyaPenyesuaian` — pengisi penanda payout) · `internal/usecase/accurate_receipt_kompensasi_tiktok_test.go` + `..._orkestrasi_test.go` **(baru)**
- **Tanggal**: 2026-09-22 (diamandemen 2026-09-25)

## Context

### Aturan yang finance tetapkan

Ditanyakan langsung dan dijawab 22 September 2026, dengan pembeda yang sangat sederhana:

> Kalau pesanannya **belum pernah ada uang masuk** → kompensasi dicatat seperti income biasa. Kalau **sudah pernah ada uang masuk** → dicatat sebagai **Pendapatan Lain-lain**, dan **tidak mengisi nilai bayar**.

Ditambah tiga penegasan: **dokumen retur tetap dicatat**; berlaku **sekarang dan ke depan** (bukan mundur); dan aturan ini **untuk TikTok saja**.

### Kenapa ini bukan pembatalan ADR-0056, melainkan penyempitannya

[[ADR - 0056 Penyesuaian Statement TikTok Menambah Payout Order]] memutuskan kompensasi **melipat ke payout pesanan**, dan secara eksplisit **menolak** alternatif "Pendapatan Lain-lain terpisah". Penolakan itu berdasar: populasinya pesanan **batal** yang fakturnya tak pernah dibayar pembeli, sehingga kompensasi itulah satu-satunya yang melunasinya, dan hasilnya sudah dicocokkan ke hitungan manual finance.

Populasi tiket ini **berbeda**: pesanan cair normal lebih dulu, kompensasi datang belakangan. Diukur di prod atas seluruh 428 pesanan berkompensasi:

| Populasi | Pesanan | Nilai | Keadaan |
|---|---|---|---|
| **Sudah** ada uang masuk | **14** | **Rp1.610.697** | populasi tiket — salah hari ini |
| **Belum** ada uang masuk | 360 | Rp34.872.894 | populasi ADR-0056 — sudah benar |
| tak ada padanan pesanan | 54 | — | di luar lingkup, dicatat di bawah |

**Diukur ulang 2026-09-25** (populasinya tumbuh, tapi yang menentukan tidak bergerak):

| Populasi | Pesanan | Nilai |
|---|---|---|
| **Payout > 0, TANPA retur** — yang berubah | **11** | **Rp1.328.198** |
| Payout > 0, **ADA retur** — tetap income biasa | 3 | Rp282.499 |
| Payout ≈ 0 — populasi ADR-0056, tak berubah | 372 | Rp35.856.793 |
| Tak ada padanan pesanan — di luar lingkup | 73 | Rp5.846.833 |
| **Total** | **459** | **Rp43.314.323** |

Angka **14** bertahan lintas tiga pengukuran (22, 24, dan 25 September) meski total barisnya
naik dari 428 ke 459 — itu yang membuat keputusan ini bisa dipatok, bukan mengejar sasaran
yang bergerak.

Contoh populasi tiket: `585616915329615127` berstatus COMPLETED dengan payout Rp74.679 lalu menerima kompensasi Rp94.500.

Menerapkan aturan baru menyeluruh **akan merusak 360 pesanan yang sudah benar** — faktur mereka tak punya pelunas lain. Karena itu yang berubah bukan keputusannya, melainkan batas populasinya.

### Aturan ini sudah berjalan di kanal Shopee

Jalur kompensasi Shopee sudah menerapkan pembeda yang sama: alokasi ke faktur **hanya** bila pesanan belum menerima uang; selebihnya satu baris ke akun pendapatan lain **tanpa menyentuh bayar faktur**, dengan alasan tertulis "mustahil dobel bayar karena tidak menyentuh Bayar faktur". TikTok tidak melewati jalur itu.

Jadi yang dikerjakan adalah **memindahkan aturan yang sudah teruji ke kanal kedua**, bukan merancang yang baru.

### Dua sisi, bukan satu — dan ini yang paling mudah terlewat

Gerbang retur hari ini men-**skip** pembukuan Retur Penjualan bila payout ditambah kompensasi melewati ambang, dengan alasan "penerimaan yang melunasi faktur". Gerbang itu **tidak membedakan** kedua populasi di atas.

Begitu kompensasi tak lagi melunasi faktur untuk populasi tiket, alasan skip itu **hilang** — tetapi returnya tetap ter-skip. Akibatnya penjualan **tidak terbalik sama sekali**: kebalikan dari dobel yang tiket ini hendak perbaiki, dan sama senyapnya. [[ADR - 0024 Retur Gerbang Payout + Tanggal per-Solution]] sudah menuliskan peringatan bentuk ini ("dua tempat WAJIB berubah bersamaan"); ini kejadian yang sama dengan arah berlawanan.

### "Ada retur dulu" adalah urutan yang stabil, bukan kebetulan waktu

Pembeda kedua (§1) bersandar pada keberadaan dokumen retur, dan pertanyaan yang wajar adalah
apakah urutannya bisa terbalik — kompensasi lebih dulu, retur menyusul — sehingga pesanan yang
sama jatuh ke perlakuan berbeda hanya karena jam sinkronisasi.

Diukur 2026-09-25 atas seluruh 459 pesanan berkompensasi:

| | Jumlah |
|---|---|
| **Retur duluan**, kompensasi menyusul | **109** |
| Kompensasi duluan, retur menyusul | **3** |

Dan ketiga "pengecualian" itu bukan pengecualian: selisihnya paling ekstrem **−1 jam**,
ketiganya dibuat di hari yang sama (dua proses sinkronisasi berdekatan), dan ketiganya
ber-payout **negatif** sehingga tak satu pun masuk populasi payout > 0.

Jeda normalnya **median 432 jam ≈ 18 hari**, paling lama 66 hari. Itu sifat alurnya, bukan
kebetulan: retur terdeteksi lewat API retur yang cepat, sementara kompensasi baru muncul di
statement settlement yang terbit belakangan.

### Cicilan kompensasi: diukur, bukan diasumsikan

Shopee menangani kompensasi bertahap lewat penahanan dan pencatatan manual AR ([[ADR - 0097 Kompensasi Shopee Susulan Ditahan dan Dicatat AR lewat Koreksi Manual ERP]]). Apakah TikTok perlu hal yang sama? Diukur: dari **428** pesanan berkompensasi, hanya **1** yang punya lebih dari satu baris penyesuaian. Membangun mekanisme penahanan untuk satu kejadian adalah permukaan yang tak sebanding.

## Decision

### 1. DUA pembeda: payout pesanan itu sendiri, lalu ada-tidaknya retur

> **Amandemen 2026-09-24.** Versi pertama ADR ini menulis SATU pembeda (payout saja). Finance
> kemudian menambahkan yang kedua, dan itu mengubah perlakuan 3 pesanan.

| Keadaan | Perlakuan kompensasi |
|---|---|
| **Payout ≈ 0** — belum pernah ada uang masuk | melipat ke payout, **melunasi faktur** *(tidak berubah, [[ADR - 0056 Penyesuaian Statement TikTok Menambah Payout Order]])* |
| **Payout > 0 dan ADA Retur Penjualan** | **melunasi faktur** *(tidak berubah — aturan finance)* |
| **Payout > 0 dan TANPA Retur Penjualan** | baris **Pendapatan Lain-lain**, **nilai bayar tidak diisi** |

Yang dinilai adalah payout pesanan itu sendiri, **bukan** payout ditambah kompensasinya —
gerbang lama menjumlahkan keduanya, dan penjumlahan itulah yang membuat kedua populasi jatuh
ke keputusan yang sama.

Pembeda kedua datang dari finance, bukan turunan kode: *"kalau ada uang kompensasi setelah
retur, masuk ke income biasa"*. Logikanya — returnya yang membalik penjualan, jadi kompensasi
cuma menggantikan refund yang keluar.

⚠️ **Penandanya `Order.Return`, BUKAN `Income.TotalRefund`.** `incomeHanyaPenyesuaian`
menolkan seluruh angka income termasuk refund untuk pesanan yang ditarik lewat jalur
"kompensasi datang di statement lebih baru", sehingga refund di situ **selalu 0** dan pesanan
ber-retur akan salah digolongkan. Sub-dokumen `Return` tak tersentuh penggantian income mana pun.

### ⛔ Payout WAJIB dibawa terpisah — kompensasi datang di statement LAIN, 11 dari 11

Kelas kegagalan yang nyaris membuat seluruh ADR ini **no-op**, ditemukan 2026-09-25 dari
screenshot finance, bukan dari test.

Kompensasi TikTok hampir selalu terbit di statement yang **berbeda** dari penjualannya.
Untuk statement kompensasi itu pesanannya tak punya baris transaksi, jadi ditarik lewat
`incomeHanyaPenyesuaian` — yang sengaja **menolkan seluruh angka income kecuali
kompensasinya**, dan itu benar: memakai income tersimpan akan membukukan ulang penjualan
yang sudah dibukukan di statement lain (ADR-0056 §2).

Akibatnya pembeda yang dihitung sebagai `TotalSettlementAmount − PenyesuaianStatement`
membaca **0** untuk pesanan yang uangnya jelas sudah cair:

```
585673721052759108   penjualan cair 30/08  statement 7679250248153171713  INC/2026/08/30/023-BH
                     kompensasi cair 14/09  statement 7684810541168150279  INC/2026/09/14/029-BH
                     payout asli Rp159.790 · kompensasi Rp198.000
                     selisih settlement = 198.000 − 198.000 = 0   <-- SALAH
```

Diukur: **11 dari 11** pesanan terdampak lewat jalur ini. Nol yang se-statement. Jadi
rumus selisih itu bukan "kurang tepat di kasus pinggir" — ia salah untuk **seluruh
populasi**, tanpa satu pun galat maupun test merah.

**Yang benar**: payout dibawa terpisah lewat `TransactionIncome.PayoutSebelumPenyesuaian`
(transient, `bson:"-"`), diisi repo selagi income tersimpan masih utuh — direkam sebelum
penggantian porsi, lalu dipasang oleh `terapkanPenyesuaian` dan `incomeHanyaPenyesuaian`.

⚠️ **Godaan menyederhanakannya kembali ke selisih akan terlihat benar**, karena fixture
se-statement memang lolos. Dikunci `TestPayoutSebelumKompensasiBukanSelisihSettlement`,
yang fixture-nya sengaja membuat kedua cara memberi jawaban berbeda.

### 2. Gerbang retur memakai pembeda yang SAMA

- **Payout ≈ 0** → retur tetap **di-skip**; kompensasi yang melunasi faktur, membukukan retur berarti pembalikan dobel.
- **Payout > 0** → kompensasi **tidak lagi menyerap**, jadi alasan men-skip retur hilang bersamanya.

⚠️ **Pemeriksaan kas akhir untuk payout ≤ 0 WAJIB dipertahankan.** Bentuk yang tampak lebih
sederhana (`payout > 0 → tidak diserap; selain itu → diserap`) merusak kasus payout **negatif**
yang kompensasinya tak menutup refund: kas akhirnya tetap ≤ 0, penjualannya memang batal, dan
returnya harus tetap dibukukan. Dikunci `TestGerbangReturKompensasiTakMenutupTetapBook`.

⚠️ **Diukur 2026-09-25: sisi retur ini TIDAK menyentuh satu pun dari 11 pesanan terdampak.**
Sebelas-belasnya berstatus COMPLETED tanpa dokumen retur sama sekali (paket hilang, barang tak
pernah kembali), jadi `SyncOrderReturn` tak pernah berjalan untuk mereka. Perannya **mencegah
kejadian berikutnya**, bukan membetulkan yang ada — dan §3 di bawah tetap berlaku justru karena
itu.

### 3. Kedua sisi berubah dalam satu perubahan, tidak boleh dipisah

Menerapkan sisi penerimaan saja menghasilkan penjualan yang tak pernah terbalik; menerapkan sisi retur saja menghasilkan pembalikan dobel. Keduanya salah dan keduanya senyap. Satu PR, satu deploy, dan test yang mengunci **kedua** sisi terhadap pembeda yang sama.

⚠️ **Titik ketiga, tak terduga saat ADR ini ditulis**: `accurate_receipt_export_detail.go`
(`dikompensasi`) menyatakan jawaban atas pertanyaan yang sama — "penjualan ini batal atau
tidak?" — untuk **rekap yang finance lihat**. Komentarnya sudah lama menyebut dirinya cermin
gerbang retur, tapi rumusnya ditulis terpisah. Kalau tertinggal, angka yang finance baca
berselisih dari yang dibukukan, tanpa satu pun galat. Aritmetikanya kini dipakai bersama lewat
`kompensasiMenyerapRefund`, dan `TestPorsiSepakatDenganGerbangRetur` mengunci keduanya agar
tak bisa menyimpang.

### 4. Tidak dibuat penahanan cicilan seperti Shopee

Satu kejadian dari 428 tidak cukup untuk melahirkan antrean, laman, dan aturan akun tersendiri. Bila kelak jumlahnya tumbuh, keputusannya ditinjau ulang dengan angka baru — bukan diantisipasi sekarang.

**Diukur ulang 2026-09-25: kini 0 dari 459** pesanan berkompensasi punya lebih dari satu baris penyesuaian. Keputusannya makin kuat, bukan melemah.

### 5. Berlaku maju, digerbangi kv tanggal per HARI PENERIMAAN

> **Amandemen 2026-09-25.** Versi pertama menulis "berlaku maju, dokumen terbit tidak
> disentuh" tanpa menyebut mekanismenya — dan itu **tidak terjadi dengan sendirinya**.
> Penerimaan di dalam jendela pindai 45 hari (`ReceiptStatementScanDays`) ditulis ulang
> otomatis begitu komposisi barisnya berubah, termasuk yang sudah SENT. Tanpa gerbang,
> Agustus ikut tersentuh — persis yang finance larang.

kv **`tiktok-kompensasi-cutover-date`** berisi hari penerimaan WIB pertama yang memakai aturan
baru. Kosong atau format salah → **mati**, perilaku lama persis (gagal-tertutup disengaja:
perbandingan string mentah atas format rusak seperti `"2026-9-1" <= "20260906"` bernilai true
dan akan menerapkannya ke seluruh periode).

Terdaftar di `AccurateKVDateCatalog`, jadi **muncul sendiri di layar Config Accurate** beserta
catatan akibatnya — diisi operator, tanpa deploy dan tanpa panggilan API manual.

**Patokannya hari PENERIMAAN**, bukan hari kirim, hari statement, atau hari sinkronisasi.
Dikonfirmasi finance 2026-09-25 — ditanya apakah "bulan September" berarti pencairan atau
penjualan, jawabannya *"yang pencairannya bulan September"*. Konfirmasi itu menentukan:
diukur **0 dari 11** pesanan terdampak dikirim bulan September, jadi memakai hari kirim akan
membuat perubahan ini tak mengenai satu pun dari mereka.

Presedennya sama bentuk dan sama alasannya: `shopee-shipping-rebate-cutover-date` ("hari
penerimaan WIB pertama", keputusan finance 2026-09-14).

**Keputusan finance 2026-09-24**: diterapkan untuk penerimaan **September 2026 saja**; yang
penerimaannya Agustus **direvisi manual**, *"takutnya ngerubah angka"*. Sebaran 11 pesanan
yang berubah, menurut hari penerimaannya:

| Kelompok | Pesanan | Nilai | Nasib |
|---|---|---|---|
| Penerimaan **September** | **7** | Rp804.700 | otomatis (kv `2026-09-01`) |
| Penerimaan **Agustus** (`INC/2026/08/31/038-BH`) | 2 | Rp354.500 | manual |
| Tanpa penerimaan (kirim Feb & Mar 2026, pra-cutover) | 2 | Rp168.998 | manual |

✅ **Yang meringankan kerja manual finance**: kedua pesanan berpenerimaan Agustus duduk di
penerimaan berstatus **FAILED** — kompensasinya belum pernah masuk Accurate. Jadi tak ada
angka Agustus yang bisa berubah; yang perlu dilakukan **memasukkan**, bukan **merevisi**.

⚠️ **Isi kv = keputusan atas 7 pesanan itu**, bukan sekadar saklar teknis: `2026-09-01`
berarti dikoreksi otomatis, tanggal deploy berarti dibiarkan. Dan pilihan "dikoreksi" punya
tenggat — penerimaan September tertua keluar dari jendela 45 hari sekitar **17 Oktober 2026**.
Menunda = memilih "dibiarkan", sebagian demi sebagian.

### 6. Hanya TikTok; aturan Shopee tidak ikut berubah

Finance menyatakannya eksplisit. Perbedaan yang tersisa dengan Shopee — kompensasi bertahap Shopee memilih akun menurut bulan, TikTok selalu Pendapatan Lain-lain — **dipertahankan sadar dan dicatat di sini**, supaya tidak terbaca sebagai ketidaksengajaan oleh yang membacanya nanti.

## Consequences

- **Nominalnya kecil, kelas kesalahannya tidak.** Rp1,6 juta di 14 pesanan, tetapi bentuknya piutang minus dan uang yang tak terbukukan — dua hal yang mahal ditelusuri AR dan tidak pernah muncul sebagai galat.
- ⚠️ **Dampak nyatanya lebih kecil dari 14, dan itu baru terlihat saat diukur 2026-09-25.** Tiga pesanan ber-retur **tidak berubah** (§1), jadi yang berubah **11 pesanan / Rp1.328.198**. Dari 11 itu, **4 penerimaannya masih FAILED** sehingga kompensasinya belum pernah masuk Accurate sama sekali — yang benar-benar salah di Accurate hari ini **7 pesanan**, dan yang terkoreksi otomatis (penerimaan September ber-status SENT) **5 pesanan / Rp580.200**. Kelimanya kebetulan satu faktur, `INV/2026/08/24/034-BH`.
- **Cheque tidak bergeser sama sekali.** Kompensasi keluar dari bayar faktur dan masuk sebagai potongan negatif akun pendapatan lain dengan nilai yang sama, jadi Σbayar − Σpotongan tetap. Yang berubah hanya ke mana uangnya dibukukan — dan justru karena itulah `lines_hash` berubah dan dokumennya dikirim ulang.
- **Sebagian retur yang kembali dibukukan akan tertahan menunggu scan gudang.** Itu benar dan memang dikehendaki per [[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]], bukan kemunduran.
- **Tidak menyelesaikan tuas koreksi pemindahan pelunasan ke akun GL.** Kasus prod yang tertolak karena penerjemah koreksi hanya mengenal geser-antar-faktur dan tambah-uang tetap terbuka; lihat [[ADR - 0100 Penerimaan Beda dengan Accurate Diputus di Halaman Penerimaan]]. Task terpisah.
- **Yang tetap terbuka**: retur lama yang menggantung menunggu barang yang takkan datang; **73** penyesuaian tanpa pesanan padanan senilai **Rp5.846.833** (naik dari 7 saat ADR-0056 ditulis, 54 saat ADR ini disusun — kenaikannya belum ditelusuri); dan pesanan yang penerimaannya di luar September, yang dimasukkan manual.
- ⚠️ **Temuan sampingan yang jauh lebih besar dari ADR ini, dan tak tersentuh olehnya**: **138 penerimaan TikTok berstatus FAILED**, 133 di antaranya **sudah punya dokumen di Accurate** yang isinya versi lama — 128 dari Agustus, galat terbanyak *"cek pemilik faktur INV/… gagal"*. Nilainya **Rp21,3 juta** kompensasi yang dokumennya tertinggal. Task tersendiri; jangan disisipkan ke perubahan ini karena sebab dan populasinya berbeda.
- ⚠️ **"Sudah masuk Accurate" TIDAK boleh dibaca dari `last_status`.** Penerimaan FAILED sebagian besar sudah punya `accurate_id`; yang gagal pembaruannya, bukan pencatatannya. Memakai status kirim sebagai penanda akan salah menghitung Rp21,3 juta sebagai "belum masuk". Penandanya ada-tidaknya `accurate_id`.
- **Deploy**: satu service (integration), tanpa env baru, tanpa perubahan kontrak ke frontend. Eksekusi prod dijalankan manusia.

## Dokumen Terkait

- [[ADR - 0056 Penyesuaian Statement TikTok Menambah Payout Order]] — keputusan yang dipersempit di sini, bukan dibatalkan
- [[ADR - 0024 Retur Gerbang Payout + Tanggal per-Solution]] — gerbang retur yang ikut berubah
- [[ADR - 0097 Kompensasi Shopee Susulan Ditahan dan Dicatat AR lewat Koreksi Manual ERP]] — aturan kanal sebelah yang sengaja TIDAK disamakan
- [[ADR - 0100 Penerimaan Beda dengan Accurate Diputus di Halaman Penerimaan]] — tuas koreksi yang belum ada
- [[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]] — gerbang gudang untuk retur barang-balik
- [[Microservices - Integration Service]] — Auto Sync Income & Auto-Sync Retur
- [[Finance - Proses Retur dan Piutang Marketplace]] — proses bisnis yang menaungi
