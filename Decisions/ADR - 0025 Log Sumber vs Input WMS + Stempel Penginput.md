> **Status**: ✅ Implemented (21 Juli 2026) — **lima** menu WMS dipecah dua sub-tab; stempel `created_by_name` aktif di semua jalur tulis manual (termasuk jalur proposal). Verifikasi visual tuntas untuk **Inbound RM**, **Kirim FG**, & **Master Resi**; Keluar FG / Input Gudang FG / Laporan Hasil Produksi menunggu pengecekan dengan role yang sesuai (`admin gudang FG`, `admin produksi`). **Follow-up 22 Juli 2026:** (a) batasan "PO multi-bahan tak mengisi form penuh" diselesaikan — form Inbound RM jadi multi-baris (klik baris PO memuat seluruh bahan); (b) **backend gerbang gudang** (retur barang-balik ditahan sampai gudang scan; Decision #8) — cakupan ADR ini diperluas dari log-split FE ke fondasi backend yang membuatnya bermakna; **terbukti end-to-end di prod**; (c) **form retur dilengkapi** (pengaman qty/status, panel konteks, scan dari daftar, retur basi terlipat; Decision #9); (d) **resi paket BALIK** diutamakan di form + scan (sumber Shopee `get_return_detail`), plus **search/filter/export laporan + auto-isi PIC** (Decision #10). **Follow-up 30 Juli 2026 (✅ deployed):** gerbang gudang **PER-ORDER** (fix under-book — konfirmasi 1 member membuka gerbang seluruh grup: 189 grup/1.437 order ~Rp142jt) + status **SEBAGIAN** turunan — lihat amandemen Decision #8. Lihat Consequences.

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

**8. Backend: retur BARANG-BALIK ditahan sampai gudang mengonfirmasi** (fondasi yang membuat "belum dicatat gudang" bermakna; ✅ live, **terbukti end-to-end prod 22 Juli 2026**). Retur `solution=0` yang lolos gerbang payout ([[ADR - 0024 Retur Gerbang Payout + Tanggal per-Solution]]) **tidak** langsung dibukukan ke Accurate — `holdForWarehouse` menahannya status **PENDING** sampai form ini tersimpan, lalu manufacture memanggil `POST /accurate/daily-returns/warehouse-confirm`. **Kondisi fisik (Reuse/Rework/Reject) menentukan pembukuan** — membalik [[ADR - 0022 Retur via Sales Return per Mode + Keep Invoice Line]] ("tak perlu tunggu barang fisik"): membukukan saat marketplace menyetujui berarti menebak qty yang belum dilihat siapa pun. Ketiga kondisi **sama-sama menambah stok** (label informasi; barang rusak disesuaikan finance manual — keputusan 21 Juli). Detail mekanisme (akumulasi per `(order_id, SKU)`, lookup by-member, re-key ke tanggal gudang) + audit `cmd/returnrecon` ada di [[Microservices - Integration Service]] §Auto-Sync Retur. **Amandemen 2026-08-05 (✅ deployed 2026-08-05, commit `779b0a06`):** cadangan pencarian **by-key** di `ConfirmReturnFromWarehouse` kini mengabaikan baris `SKIPPED`, menyamakannya dengan lookup utama. Tanpa itu, scan gudang bisa **menghidupkan** retur yang sengaja tak dibukukan — entah karena refundnya sudah diserap Auto Sync Income ([[ADR - 0024 Retur Gerbang Payout + Tanggal per-Solution]]) atau karena era manual pra-cutover — dan `rebuildAndSendGroup` tak punya gerbang payout sendiri untuk menahannya. Terbukti tes regresi: 1 dokumen Retur Penjualan terbukukan dobel sebelum fix.

> **Amandemen — gerbang PER-ORDER, bukan per-grup** (✅ **deployed 2026-07-30**). `holdForWarehouse` semula membuka gerbang **seluruh grup** begitu `WarehouseConfirmedAt` terisi — cukup **SATU** paket member discan → dokumen dibukukan hanya baris member itu, member lain jadi anggota grup **SENT TANPA baris** (**under-book**; prod `RTR/2026/07/29/017-BH`: 3 order → 1 baris. Audit: **189/192 grup SENT, 1.437 order ~Rp142jt**). Bukan "SENT hantu" — dokumen ADA di Accurate, cuma kurang baris. **Fix:** gerbang menahan tiap member sampai barang **ORDER-nya sendiri** discan (`orderHasWarehouseItem` — cek `warehouse_items` ber-`order_id`), aktif hanya bila grup sudah punya rincian scan; guard cegah grup SENT turun ke PENDING saat menahan member baru (pelajaran retur-hilang 21 Juli). Grup yang **sebagian** discan ditandai **"SEBAGIAN"** — field **turunan** `WarehousePending` (member barang-balik belum discan; **refund-only `solution=1` dikecualikan** — tak perlu scan, dibukukan langsung), dihitung saat baca (list/detail/export), **tak dipersist**. Backlog tampil SEBAGIAN **otomatis tanpa backfill**; dokumen **self-heal** saat paket sisa discan (rebuild menambah baris). Presisi solution per-member hanya di export+detail (order termuat); badge list konservatif.

**9. Form retur dilengkapi + daftar difokuskan** (22 Juli 2026). Perbaikan FE `GudangBarangJadiView` di atas fondasi #8:
- **Pengaman input**: keterangan kondisi (dropdown Rework: isi berkurang/segel terbuka; Reject: pecah/barang tidak sesuai—klaim ekspedisi) **wajib** saat qty terisi; total per baris tak boleh **melebihi** klaim marketplace (over-retur diblokir — Accurate pasti menolak), **kurang** disorot (parsial sah).
- **Panel konteks retur read-only** (order, no. retur, channel/toko, status order, alasan marketplace **yang di-humanize** dari kode mentah, nilai refund) — sebelumnya form tak menampilkan retur mana yang dicatat.
- **Field "Cancel Order" manual dihapus** — diturunkan dari `order_status` marketplace (sistem sudah tahu; ketik ulang = sumber salah).
- **Scan resi dari halaman daftar** membuka form terisi + tertaut (auto-fokus untuk scanner); pesan sukses membedakan tertaut vs catatan WMS lepas.
- **Daftar difokuskan**: default hanya retur yang bisa dikerjakan; badge memimpin angka **aktif**, retur **basi** (>14 hari, barang mungkin tak datang) diberi angka redup + dilipat di bawah. Ambang 14 hari heuristik (idealnya per-SLA channel).
- **Resi paket BALIK diutamakan** (22 Juli 2026): form mengisi resi dari `reverse_tracking_no` (label paket retur yang diterima gudang), Master Resi (forward) hanya cadangan; **scan mencocokkan ke resi-balik dulu** sebelum Master Resi. Sumber & backfill di [[Microservices - Integration Service]].

**10. Search + filter + export laporan retur, dan auto-isi PIC** (22 Juli 2026, FE-only, tab Return). Logika murni di-TDD (vitest, `features/manufacture/utils/*`):
- **Search + filter**: kotak cari (order/retur/**resi-balik**/resi-forward/toko/SKU, partial+case-insensitive, `cocokPencarian`) + filter channel; disambung ke daftar tanpa mengubah perilaku default.
- **Export laporan fleksibel** (`buildBarisExport`): modal pilih **kolom** (24 kolom termasuk resi-balik/kurir/status-logistik + Reuse/Rework/Reject + dicatat-oleh) + **filter** (rentang tanggal, channel, status catat) + **toggle granularitas per-retur / per-SKU** → **xlsx** (`exceljs`+`file-saver` dynamic import, pola `ResiMasterView`). Murni client-side dari feed yang sudah dimuat (batas truncation >2000 diberitahukan).
- **Auto-isi "Nama Pengecek (PIC)"** dari **`full_name` JWT** (cookie `token`, fallback `username`), diisi **hanya bila kosong** — DEFAULT kenyamanan, **BUKAN** pengganti stempel audit `created_by_name` (#6) yang tetap server-side & otoritatif. Ini pembedaan penting: PIC = field bisnis bisa disunting, stempel = jejak audit tak bisa dipalsukan.

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
- **"SEBAGIAN" bisa over-flag** (amandemen gerbang per-order). Order yang barangnya **genuinely tak balik** (hilang/`TANPA_BARANG_BALIK` — tercatat di manufacture-service, tak terlihat integration per [[ADR - 0002 Database-per-Service]]) tetap dihitung "belum discan" → grup tampil SEBAGIAN padahal sebenarnya beres. Konservatif yang **disengaja** (over-flag lebih aman dari under-book — "cek ini" > sembunyikan). Menyempurnakannya butuh status fisik dari manufacture-svc (perubahan lintas-service terpisah).
- **Tab sumber Keluar FG disaring per tanggal RTS.** `resiList` memuat jendela 60 hari (≈14 ribu record); agregasi per SKU membuat batas 300 baris yang sempat dipasang tidak lagi diperlukan (satu tanggal ≈ 19 baris) dan sudah dihapus.
- **Angka tab sumber Keluar FG bukan "seluruh resi hari itu".** Yang batal/retur dan yang belum diambil kurir dikecualikan, jadi totalnya lebih kecil dari jumlah resi mentah. Jumlah yang dikecualikan ditampilkan eksplisit di header supaya selisihnya bisa dijelaskan, bukan tampak sebagai data hilang.
- **Perilaku terhadap status Shopee belum teruji** — di dev semua resi TikTok, tak ada satu pun Shopee meski endpoint sync-nya ada. Begitu Shopee aktif di produksi, kategori kanoniknya perlu dicek sekali; status yang tak terpetakan akan ikut terhitung (dan dilaporkan merah), bukan lenyap.
- **Gerbang ini punya TANGGAL LAHIR, dan itu penting saat membetulkan data lama** (temuan remediasi 2026-08-06). Gerbang backend baru terbukti jalan **22 Juli 2026**; retur untuk order yang lebih tua **tak pernah** melewatinya, jadi ketiadaan `warehouse_items` pada dokumen lama **bukan** tanda barangnya belum discan — memang tak pernah ada mekanismenya. Konsekuensi praktis: saat membukukan ulang data lama, `--skip-warehouse-gate` **hanya sah untuk dokumen pra-22-Juli**. Dipukul-rata ke dokumen yang lebih baru, ia membukukan barang yang belum dilihat siapa pun — persis yang gerbang ini ada untuk mencegah. Rinciannya di [[ADR - 0040 Retur Paket Utuh via Baris Induk Faktur]].
- **`cmd/cancelretrigger` & `cmd/returnrebook` salah membaca "belum dibukukan"** (ditemukan 2026-08-06, **belum diperbaiki**). Keduanya menyimpulkan sebuah order tak punya baris dengan mencari baris **per-order**, padahal sejak model grup ([[ADR - 0016 Retur Grouped per Faktur + Tanggal Retur]]) pembukuannya sering hidup sebagai **member** di baris grup order lain. `returnrebook` karenanya melaporkan "gagal 41" padahal ~20 di antaranya memang sudah terbukukan dengan benar; `cancelretrigger` sebaliknya menghitung baris **apa pun** (termasuk `SKIPPED`/`FAILED`) sebagai "sudah ditangani". Dua arah salah, satu akar: kunci pencariannya kurang satu sisi (`members.order_id`). Laporan kedua alat ini **tak boleh dibaca apa adanya** sampai difix. ANTREAN.
- **Retur "basi" belum punya penutupan resmi** (#9). Retur barang-balik yang barangnya tak akan datang menumpuk di "belum dicatat" selamanya — melipatnya di FE hanya kosmetik. Perlu aksi backend "tutup retur basi" (state penutupan) + keputusan finance (siapa boleh menutup, kapan). ANTREAN.
- **Stok WMS = stok Accurate untuk semua kondisi** (#8; selisih Reject **diselesaikan 22 Juli**). Backend `deltaStokTransaksi` kini menambah **seluruh qty** (Reuse+Rework+Reject) ke stok WMS — SAMA dengan yang Accurate bukukan (`RETURNED`), jadi tak ada lagi selisih otoritatif. Ini **membalik arah** temuan awal 17 Juli ("reject ke scrap"): karena Accurate membukukan ketiganya, mengurangi Reject di WMS justru menciptakan selisih permanen — satu pintu penyesuaian (finance manual, keputusan 21 Juli) lebih mudah dijaga daripada dua sistem menebak. Sisa: FE `onUpdateStock` masih menambah Reuse+Rework saja untuk update optimistik lokal, tapi itu **kosmetik & sekejap** — tertimpa `loadData()` yang mengambil stok server (semua qty). Diselaraskan di iterasi FE berikutnya.

## Dokumen Terkait

- [[Microservices - Manufacture Service]] · [[APP - Web ERP]] · [[API - Manufacture Service]]
- [[Manufacture - Stock & Material Management]] (konsep domain)
- [[ADR - 0002 Database-per-Service]] (sebab join retur dikerjakan di kode Go, bukan `$lookup`)
- [[ADR - 0015 Push Pergerakan WMS ke Accurate]] (Input Gudang FG = titik pengakuan stok FG)
