> **Status**: ✅ Implemented (21 Juli 2026) — **lima** menu WMS dipecah dua sub-tab; stempel `created_by_name` aktif di semua jalur tulis manual (termasuk jalur proposal). Verifikasi visual tuntas untuk **Inbound RM**, **Kirim FG**, & **Master Resi**; Keluar FG / Input Gudang FG / Laporan Hasil Produksi menunggu pengecekan dengan role yang sesuai (`admin gudang FG`, `admin produksi`). **Follow-up 22 Juli 2026:** batasan "PO multi-bahan tak mengisi form penuh" diselesaikan — form Inbound RM jadi multi-baris (klik baris PO memuat seluruh bahan), lihat Consequences.

## Context

Log tiap menu WMS mencampur dua hal yang asalnya berbeda: **data dari sumber** (retur marketplace, resi, PO ke supplier, Surat Jalan produksi) dan **data hasil input gudang**. Di tab *Return Dari Ekspedisi* keduanya tampil berbaur di satu tabel; di menu lain sumbernya tak terlihat sama sekali. Akibatnya Finance sulit menjawab pertanyaan paling dasar: **apa yang seharusnya masuk/keluar, dan mana yang belum dicatat gudang.**

Masalah kedua: log tidak menunjukkan **siapa** yang menginput. `metadata.created_by` hanya menyimpan employee ID, sedangkan field seperti `admin_pic`, `marketing_pic`, `procurement_pic`, dan "kepala produksi" adalah **field bisnis yang diketik operator di form** — bisa berisi orang lain sama sekali dan tidak bisa dipakai sebagai jejak akuntabilitas.

Kondisi teknis yang membatasi pilihan (diverifikasi ke kode, bukan asumsi):

- Header `BIP-Username` **sudah** di-inject [[CORE - API Master Gateway]] dari JWT untuk setiap request (`gateway_request.go` menghapus header kiriman client lalu menulis ulang dari claims), tapi di manufacture-service hanya dibaca `audit.go`.
- `manufacture_audit_log` menyimpan username, tapi field `Target`-nya hanya kode/ID (mis. `tx.KodeBahan`), **bukan `_id` dokumen** — join balik dari audit ke baris log tertentu tidak andal.
- **Hanya satu feed sumber yang punya kunci join**: `GET /returns` menurunkan `record_status` dari `detail.returnKey` = `dedupe_key`. Transaksi Keluar FG **tidak** menyimpan nomor resi yang dipakai (hanya keterangan "Dari N resi master"), dan transaksi penerimaan RM **tidak** menyimpan nomor PO.

## Decision

**1. Log tiap menu dipecah dua sub-tab: SUMBER dan INPUT WMS.**

| Menu | Tab sumber | Tab input WMS |
|---|---|---|
| Return Dari Ekspedisi | feed retur marketplace (`GET /returns`) | transaksi INBOUND ber-`namaMarket` |
| Keluar FG | resi marketplace **diagregasi per SKU** (lihat §3) | transaksi OUTBOUND ber-`marketplaceSalesDetection` |
| Inbound RM Harian | Procurement PO | transaksi penerimaan ber-`picQc` |
| Input Gudang FG | Surat Jalan status `IN TRANSIT` | transaksi INBOUND ber-`gudangSimpan` |
| **Kirim FG ke Gudang Jadi** | Laporan Hasil Produksi belum dibuatkan SJ | transaksi OUTBOUND ber-`driver` (SJ) |

Sumber Inbound RM adalah **Procurement PO**, bukan Accurate — keputusan user 21 Juli 2026 setelah dipastikan tidak ada feed penerimaan barang dari Accurate (sync-nya hanya master & angka stok, bukan transaksi penerimaan). Jadi yang dibandingkan adalah *apa yang dipesan* vs *apa yang benar-benar datang & lolos QC*.

**2. Badge status "sudah/belum dicatat" HANYA di tab yang punya kunci join.**

Return Ekspedisi mempertahankan badge tiga-nilai. Keluar FG dan Inbound RM **sengaja tanpa badge status** — tanpa kunci join, status apa pun di sana adalah tebakan, dan tebakan salah tentang "barang ini sudah keluar/diterima" lebih berbahaya bagi Finance daripada tidak ada badge sama sekali.

Dua menu tidak butuh badge karena daftarnya **sudah** berupa tunggakan menurut definisi: Input Gudang FG (`IN TRANSIT` = belum diterima) dan Kirim FG (laporan produksi yang belum tertaut `refLaporanProduksi`). Kirim FG bahkan punya kunci join yang paling bersih — laporan hilang sendiri dari tab sumber begitu dipakai membuat SJ.

**3. Tab sumber Keluar FG diagregasi PER SKU, bukan daftar per-resi** (21 Juli 2026, setelah user mempertanyakan bentuk awalnya).

Alasannya bukan sekadar jumlah baris. Tab WMS mencatat **per SKU** (diagregasi lintas banyak resi), sedangkan daftar per-AWB adalah dokumen pengiriman — dua tab berbicara dalam granularitas berbeda sehingga **tak bisa dibandingkan berdampingan**, padahal itu justru tujuan pemisahan tab. Terukur di dev: 931 resi → 19 SKU untuk satu tanggal RTS.

Bundle **dipecah ke komponen** agar sebanding dengan tab WMS (transaksi menyimpan SKU komponen). Tanpa ini baris dengan qty TERBESAR justru tak pernah punya pasangan — di dev, bundle `PJG-002 + PJG-004` menyumbang 641 dari ~900 qty. Kode bundle asal tetap ditampilkan sebagai keterangan agar bisa ditelusuri balik ke listing marketplace.

**4. Hanya resi berstatus `COMPLETED` + `SHIPPED` yang terhitung keluar gudang.**

Kanonikalisasi status marketplace (6 kategori, memetakan ~24 nilai mentah TikTok/Shopee) diekstrak dari `ResiMasterView` ke `features/manufacture/resi-status.ts` supaya semua layar memakai satu definisi.

Bukan `COMPLETED` saja: pada tanggal RTS yang baru ~47% resi masih `SHIPPED` (= `IN_TRANSIT`, sudah dibawa kurir) padahal barangnya jelas sudah pergi — memfilter ke Completed membuat pencatatan **kurang**, bukan lebih akurat.

`TO_SHIP` (`AWAITING_COLLECTION`, masih menunggu kurir) dikecualikan karena asimetri jalur koreksi: kalau batal **setelah** dibawa kurir, barangnya kembali fisik dan tercatat di menu Return — stok tetap benar. Kalau batal **sebelum** diambil, tak ada barang yang kembali sehingga tak akan pernah tercatat di mana pun, dan stok yang terlanjur dipotong **tak punya jalur perbaikan**. `IN_TRANSIT` adalah titik pertama yang aman.

Status **tak dikenal tetap dihitung dan dilaporkan**, bukan disaring diam-diam — varian Shopee belum pernah terlihat di dev (semua resi TikTok), dan pengiriman yang lenyap tanpa jejak lebih berbahaya daripada baris yang minta ditinjau. Prinsip sama dengan feed retur.

Aturan ini ditegakkan di **semua** pintu masuk form, bukan hanya tab sumber: klik baris, **Ambil Rentang**, dan **scan resi**. Di Ambil Rentang filter dipasang saat *memasukkan*, bukan saat *menomori* — daftar `f4RangeList` sengaja dibiarkan utuh supaya nomor urut 1..N tetap cocok dengan penomoran Master Resi (kontrak urutan `_id`, lihat `resi.go`). Scan ditolak dengan **alasan + status resinya**, tidak dilewati diam-diam, karena operator sedang memegang paketnya.

**5. Baris sumber bisa diklik → membuka form terisi**, mengikuti pola `openReturnForm` yang sudah ada. Untuk Input Gudang FG & Kirim FG, logika pengisian diekstrak jadi fungsi bersama (`pilihSjUntukTerima` / `pilihLaporanProduksi`) supaya dropdown di dalam form dan klik baris memakai satu jalur. Di Keluar FG baris mewakili satu SKU lintas banyak resi, jadi kliknya memuat **seluruh resi tanggal RTS itu** (setara "Ambil Rentang" sekali klik) — memuat "resi baris ini" tak punya arti di tingkat agregat.

**6. Nama penginput distempel SERVER, bukan dikirim client.** Field `created_by_name` diisi handler dari `c.Get(common.Header.Username)` dan **selalu menimpa** nilai yang datang di body. Alternatif "frontend kirim username dari cookie" ditolak: nilainya dikirim browser sehingga bisa dipalsukan, dan jejak yang bisa dipalsukan bukan jejak audit.

Distempel di: `transaksi` (termasuk `transaksi_fg` & tiga titik di `production`), `production_log`, `resi`, `material_order`, `marketing_po`, `procurement_po`, dan `proposal`.

Jalur **proposal** ditambahkan belakangan (21 Juli 2026): transaksi yang lahir dari approval deviasi BOM tidak ikut distempel di putaran pertama, sehingga kolom "Diinput oleh" di Keluar Produksi akan menampilkan `—` **selamanya, termasuk data baru**. `Proposal` kini menyimpan `created_by_name` sendiri dan mewariskannya ke transaksi saat `APPLIED` — yang ditampilkan adalah nama **pengaju**, bukan approver, karena kolomnya berjudul "Diinput oleh" dan yang mengisi form adalah operator (approver sudah terekam di `ppic_approval`/`spv_approval` + audit log).

**7. Resi hasil sync marketplace TIDAK distempel.** `upsertResiFeed` sengaja dibiarkan kosong — datanya datang dari marketplace, bukan diketik orang. Mengisi nama pemicu sync akan membuat kolom "Diinput oleh" berbohong tentang ribuan baris. Konsekuensi yang diambil sebagai keuntungan: ada/tidaknya nama sekaligus menjadi penanda asal data (manual vs sync) di [[Microservices - Manufacture Service]] tab Master Resi.

## Consequences

**Yang membaik**

- Finance bisa membandingkan sumber vs pencatatan gudang di **lima** menu, bukan hanya retur — dan di Keluar FG perbandingannya kini setingkat (per SKU vs per SKU).
- Log WMS menampilkan penginput yang tak bisa dipalsukan, terpisah jelas dari field PIC yang diketik manual.
- Baris sumber jadi titik masuk kerja (klik → form terisi), bukan sekadar tabel baca.
- Resi batal / belum diambil kurir **tidak lagi bisa masuk** form Keluar FG lewat pintu mana pun — sebelumnya angka sumber ikut menghitungnya dan form bisa menariknya, sehingga stok terpotong untuk barang yang tak pernah keluar.

**Yang harus diterima**

- **Data lama tampil `—`.** Username tak pernah disimpan sebelumnya dan tidak bisa diisi surut — audit log punya username tapi `Target`-nya tak cukup untuk join balik.
- **Tab sumber Keluar FG & Inbound RM tidak bisa menjawab "mana yang belum diinput"** sampai kunci join ditambahkan (menyimpan nomor resi/PO pada transaksi saat input). Itu perubahan terpisah dan hanya akan akurat untuk data sesudahnya.
- ~~**PO multi-bahan tidak mengisi form penuh.**~~ **Diselesaikan (22 Juli 2026):** form Inbound RM kini multi-baris — klik baris sumber PO memuat **seluruh** bahan PO sebagai baris (Qty SJ dari qtyOrder; Lolos/Reject diisi operator), baris bisa ditambah/dihapus, dan submit membuat satu transaksi INBOUND per bahan. Tiap baris menampilkan Nama Barang readonly dari master (kode tak dikenal ditandai jelas). Ini menghapus tebakan "bahan mana" — operator memfilter dari daftar lengkap, bukan mengetik ulang.
- **Daftar "SJ Belum Diterima" bukan angka pasti.** Status SJ berubah `DELIVERED` hanya bila penerimaan dibuat lewat pilihan *Terima dari Surat Jalan*; penerimaan yang diketik manual tidak menutup SJ-nya, sehingga SJ itu tetap tampil tertunggak walau barangnya sudah masuk. Perilaku pra-ada, baru terlihat sekarang karena datanya ditampilkan sebagai daftar.
- **Tab sumber Keluar FG disaring per tanggal RTS.** `resiList` memuat jendela 60 hari (≈14 ribu record); agregasi per SKU membuat batas 300 baris yang sempat dipasang tidak lagi diperlukan (satu tanggal ≈ 19 baris) dan sudah dihapus.
- **Angka tab sumber Keluar FG bukan "seluruh resi hari itu".** Yang batal/retur dan yang belum diambil kurir dikecualikan, jadi totalnya lebih kecil dari jumlah resi mentah. Jumlah yang dikecualikan ditampilkan eksplisit di header supaya selisihnya bisa dijelaskan, bukan tampak sebagai data hilang.
- **Perilaku terhadap status Shopee belum teruji** — di dev semua resi TikTok, tak ada satu pun Shopee meski endpoint sync-nya ada. Begitu Shopee aktif di produksi, kategori kanoniknya perlu dicek sekali; status yang tak terpetakan akan ikut terhitung (dan dilaporkan merah), bukan lenyap.

## Dokumen Terkait

- [[Microservices - Manufacture Service]] · [[APP - Web ERP]] · [[API - Manufacture Service]]
- [[Manufacture - Stock & Material Management]] (konsep domain)
- [[ADR - 0002 Database-per-Service]] (sebab join retur dikerjakan di kode Go, bukan `$lookup`)
- [[ADR - 0015 Push Pergerakan WMS ke Accurate]] (Input Gudang FG = titik pengakuan stok FG)
