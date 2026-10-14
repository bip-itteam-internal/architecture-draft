> **Status**: ⚠️ Implemented (ada catatan) — audit baca-saja selesai 2026-10-14; perbaikan BELUM dikerjakan, menunggu keputusan SPV setelah user membaca laporan.

Papan kerja hasil audit gudang/WMS/scan/manufaktur 2026-10-14. **Laporan lengkap ada di luar vault** (repo kode, bukan dokumen arsitektur): `_audit-gudang-2026-10/LAPORAN-AUDIT-FINAL.md`, dengan lima laporan sumber `A-manufaktur-wms.md` · `B-fulfillment-scan.md` · `C-retur-sinkron.md` · `D-inventory-scanner.md` · `E-delay-skip-approve.md` dan verifikasi silang `QA-verifikasi.md`. Berkas ini adalah **ringkasan papan kerja** yang berubah tiap item selesai; status per baris audit Juni diperbarui di [[Manufacture - Issue Code Audit 2026-06]].

# Audit Gudang, WMS, Scan & Manufaktur 2026-10

**Permintaan user (Kukuh):** *"tolong audit system gudang dan manufactur, wms, scan dan semuanya"*, ditambah keluhan lanjutan *"dari approve pesanan sampai scan kurir sepertinya data ada delay bahkan ada order yg terskip dari approve"*.

**Sifat kerja:** baca-saja. Nol perubahan kode, nol PR, nol akses data produksi. Label TERVERIFIKASI berarti *kodenya dibaca pada SHA di bawah*, bukan *dilihat terjadi*.

| Repo | origin/main yang diaudit |
|---|---|
| `bip-erp` | `6f98d349e` |
| `erp-frontend` | `5329c7d21` |
| `my-bharata` | `989dc6526` |
| vault | `a77cef90` |

**Mutu bukti:** 59 baris temuan A–D diverifikasi silang → **56 KONFIRMASI, 3 SEBAGIAN, 0 SALAH**. **Nol temuan dibuang.** 13 kandidat temuan tambahan milik verifikator sendiri dibuang setelah grep membuktikannya tidak ada. 7 pasang duplikat lintas laporan digabung agar tidak dihitung dua kali. Laporan E (delay & skip) **tidak lewat verifikasi silang** — sembilan temuannya (E-1…E-8, E-11) dibuka ulang ke `file:baris` saat konsolidasi; **E-9 dan E-10 belum diverifikasi siapa pun**.

---

## Temuan terverifikasi per severity

Rincian (kutipan kode, dampak, usulan fix, label bukti) ada di tabel §2 laporan final.

### 🔴 Critical — 9

| Kode | Inti masalah | Dokumen terkait |
|---|---|---|
| **B1 ≡ C-1** | Peran penyetuju koreksi stok dibaca dari **body JSON**, bukan header yang dijamin gateway → alur PPIC→SPV dilewati sepenuhnya | [[Microservices - Manufacture Service]], [[Manufacture - Issue Code Audit 2026-06]] |
| **A1** | Migrasi kode bahan/produk + cascade ke 10+ koleksi **tanpa transaksi**; gagal di tengah → basis data campur permanen. Cacat identik ada di **dua** berkas | [[Microservices - Manufacture Service]], [[RUN - Selaraskan Kode Bahan WMS ke Accurate]] |
| **T-1** | WMS menandai **semua** order `LABEL_PRINTED` begitu layanan resi membalas 200, padahal jawabannya berisi `READY/PROCESSING/FAILED` per order → paket tanpa resi masuk antrian Serah Terima | [[WH - Fulfillment Flow & WMS Tinggarjaya]], [[Microservices - Warehouse Service]] |
| **T-3** | Status dievaluasi ulang terhadap snapshot lama setelah panggilan HTTP 5 menit → `RTS_OK` tertimpa `RTS_FAILED` walau AWB terbit → order **buntu permanen** | [[WH - Fulfillment Flow & WMS Tinggarjaya]] |
| **C-2** | Kill switch `ACCURATE_WMS_PUSH` **default hidup** di compose, melawan komentar kodenya sendiri dan ADR-nya → pembukuan sungguhan ditulis otomatis tiap 10 menit | [[ADR - 0015 Push Pergerakan WMS ke Accurate]] |
| **C-3** | Tanggal dokumen Penyesuaian Persediaan diambil dari **jam pemindaian**, bukan tanggal transaksi → dokumen terbit di bulan buku yang salah tanpa jejak | [[ADR - 0015 Push Pergerakan WMS ke Accurate]] |
| **D-01** | Menu QR Code tampil untuk semua karyawan, endpoint yang dipanggil digerbang `ga.view` milik staf GA → scan aset praktis mati bagi non-GA, dan pesannya terlihat seperti masalah jaringan | [[APP - MyBharata]], [[Microservices - Inventory Service]] |
| **E-1** | Layar Antrian menampilkan *"N order berhasil disetujui"* dari jumlah yang **dikirim**; jawaban server `{transitioned, skipped, failed}` dibuang tanpa dibaca → **inilah "order terskip dari approve"** | [[WH - Fulfillment Flow & WMS Tinggarjaya]], [[APP - Web ERP]] |
| **E-3** | Jalur dorong mencap `update_time` dengan **jam server**, jalur tarik & sweep dengan **jam marketplace** → gerbang anti-event-basi menolak semua pembaruan jalur tarik; **pembatalan pembeli & auto-close tidak pernah diterapkan**. Akar yang membuat T-9 dan T-11 tak punya penyembuh otomatis | [[Microservices - Warehouse Service]], [[Microservices - Integration Service]] |

### 🟠 Major — 27

Pengelompokan sesuai akarnya (satu akar = satu paket perbaikan):

- **Tulisan status tidak bersyarat** (satu pola): **T-2** reprint palsu · **T-4** handover ganda tanpa compare-and-set · **A3** apply proposal tanpa filter status → stok INBOUND naik dua kali.
- **Jalur push WMS→Accurate** (satu paket, **C-2 satu baris compose didahulukan**): **C-4** nol pagar bulan buku · **C-6** kelompok dari `PENDING` saja sementara protokol edit menghapus baris lama → **qty yang sudah terkirim HILANG dari pembukuan** · **C-5** cascade align tak mencakup outbox → `item_no` tak dikenal Accurate · **A2** `ReconcileStok` menimpa baseline Accurate tanpa dry-run.
- **Integritas data manufaktur**: **A4** hapus stok & saldo awal yatim tanpa jejak, tanpa mengecualikan baris terkunci Stok Opname · **A5** `qty_terima` mutasi gudang tanpa batas atas → saldo lokasi dari udara · **A6** nomor batch SPK dibuat di browser dengan `Math.random()`, nol pemeriksaan tabrakan → dua SPK menyatu di dossier Batch Record · **B6** `context.Background()` di 19 titik jalur request · **B7** partial-failure `return 500` di tengah loop.
- **Jalur masuk order WMS**: **E-2** "Pilih Semua" hanya satu halaman · **E-11** Serah Terima/Cetak Resi/RTS hard 50 **tanpa paginasi** · **E-4** jendela reconciler `kursor − 5 menit` = pagar bukan jaring · **E-5** webhook Lazada **tidak memanggil** pendorong ke WMS · **E-7** order ditutup otomatis ke `HANDED_OVER` melompati approve..handover, `handed_over_at` palsu masuk KPI · **E-6**/**E-8** (🟡–🟠) order melompati `TO_SHIP` dibuang "ignored"; `FindOne` pakai `order_id` tanpa `channel` padahal indeks uniknya gabungan.
- **Verifikasi scan & gerbang**: **T-5** `PostPack` tak menolak SKU asing / qty negatif · **T-7** `queue/export` menulis tapi terbuka untuk admin_qc · **T-9** gerbang watermark men-skip `CANCELLED` · **T-12** WMS nol operasi stok → nol risiko ganda, tapi risiko **terlewat** tanpa satu layar pembanding.
- **FE menyimulasikan ulang backend**: **F4** stok lokal ditambah setelah refetch di 10 titik panggil.
- **Aset & stok GA**: **D-02** `specs` array-vs-Map → spesifikasi tak pernah tampil di mobile · **D-03** laporan kerusakan tak mengubah aset → aset rusak masih bisa dijanjikan · **D-04** `HoldPeriod.IsActive` hard-code `true` · **D-05** KPI `akurasi_aset_ga` memberi 100 ke perlengkapan → angka di layar ≠ angka yang menilai orang · **D-06** tiga endpoint register aset tanpa gerbang apa pun · **D/A1** [[ADR - 0175 Stok GA di ERP Jadi Stok Operasional, Barang Keluar dan Penyesuaian Dikirim ke Accurate]] Diterima tapi **nol kode** → selisih ERP vs Accurate pasti membesar tanpa alarm.

### 🟡 Minor — 29

**B2/B3** berubah bentuk sejak Juni (non-atomisitas hilang, TOCTOU tetap) · **B8** `parseNum` · **F6** ternary `ACTIVE:ACTIVE` di dua jalur FG · **A7** list inti tanpa paginasi & tanpa index · **A8** snapshot saldo awal cek-lalu-tulis · **A9** FE menyimulasikan ulang efek approve · **T-6** `/rts` tanpa batas batch · **T-8** `$regex` tanpa `QuoteMeta` · **T-10** cancel membatalkan order yang resinya sudah tercetak, tanpa jalan kembali · **T-11** order menggantung selamanya · **T-13**…**T-18** (context, `total_today`, test yang tak memanggil handler, kunci layanan di query string, blob URL bocor, menu Kelola Pesanan 100% dummy) · **C-7** pagar idempotensi retur bergantung mutex per-proses · **C-8** dua rute pembukuan hanya digerbang gateway key global · **C-9**/**C-10** visibilitas kegagalan push & penjaga anti-dobel retur pakai nama gudang literal · **C-11** `NotifyWarehouse` fire-and-forget (disengaja, dicatat sebagai ketergantungan) · **D-07**…**D-15** · **E-9**/**E-10** (**belum diverifikasi**).

---

## Yang dinyatakan SEHAT dan jangan diganggu

Dasar lengkapnya di tiap laporan sumber; 13 kandidat temuan dibuang justru karena area ini terbukti sehat.

- **RBAC per-rute `services/manufacture`** — 151 gerbang, **nol** rute tanpa middleware (diuji falsifikasi: regex atas 158 pendaftaran = nol hasil). Pemisahan "yang mengisi ≠ yang menyetujui" ditegakkan di gerbang **dan** di handler. Ini menutup B9 audit Juni.
- **Pagar scan retur** [[ADR - 0158 Scan Retur Gudang Dijaga Satu Kali dan Selaras dengan Pembukuan, Koreksi Bertahap]] — idempotensi per referensi (balas 200 + `sudah_tercatat`), batas kumulatif vs klaim marketplace, penolakan **tanpa menulis apa pun**, kunci per (order, SKU), jalur simpan atomik. Area tersehat di seluruh cakupan. Lihat [[ANALISA - Pengaman Scan Retur Gudang]].
- **Pembatasan toko mitra Sadewa** — dipasang server-side di satu titik, **sesudah** filter query sehingga tak bisa diperluas klien; galat dikembalikan, tidak ditelan. Lihat [[WH - Warehouse Sadewa]].
- **Satu pintu perubahan stok perlengkapan GA** — syarat bersyarat ada **di dalam filter Mongo**, bukan di kode pemanggil → nol jendela TOCTOU. Lihat [[Microservices - Inventory Service]].
- **Reconciler & sweep WMS** — deadlock kursor yang pernah terjadi di produksi sudah diperbaiki dengan paginasi + dorong-maju lapis kedua; bagian paling matang di service itu.
- **Penomoran & idempotensi penerimaan aset** — nomor tertinggi + 1 dengan retry duplicate-key, jejak diperiksa di dua tempat, sanitasi nama menutup bug path nyata.
- **Stempel penginput** [[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]] — `created_by_name` ditimpa server dari header di semua jalur tulis yang diperiksa.

---

## Daftar paket perbaikan (PR) — BELUM dikerjakan

Rincian isi, berkas, ukuran S/M/L, dan prasyarat ada di §3 laporan final. **Yang memutuskan dikerjakan atau tidak = SPV.**

| Gelombang | Isi | Catatan urutan |
|---|---|---|
| **W0** (3 paket, semua **S**, semua Critical) | balik default kill switch push Accurate · label hanya untuk yang `READY` · peran penyetuju dari header | Paralel, nol ketergantungan. **Nilai per-baris-kode tertinggi di seluruh daftar** |
| **W1** (7 paket) | jejak + alasan aksi batch (BE) → layar jujur (FE) · **satukan satuan jam `update_time`** · compare-and-set · auto-close yang benar-benar jalan · `PostPack` tolak SKU asing + test lewat handler · batas batch `/rts` | **Satukan jam WAJIB sebelum perbaikan T-9/T-11 apa pun** — tanpa itu tambalannya tetap mati di gerbang watermark |
| **W2** (4 paket) | pilih seluruh hasil filter + paginasi layar tahap akhir · panel "ditutup otomatis / tak lewat gudang" · kebersihan layar WMS · `c.UserContext()` | Independen dari W1 |
| **W3** (5 paket) | jaring "siap-kirim yang tidak ada di WMS" · `(order_id, channel)` + normalisasi channel · retry/outbox notify · filter tanggal pakai tanggal marketplace · rekonsiliasi resi WMS ⟷ manufaktur | **Tunggu hasil cek data.** Bila selisihnya nol, prioritasnya turun drastis |
| **M** (16 paket) | align atomik **dua berkas** · tanggal push dari tanggal kejadian · kelompok push `PENDING ∪ SENT` · pagar bulan buku · filter status proposal · anti-minus · jejak sebelum hapus + hormati kunci SO · validasi `qty_terima` · nomor SPK dari server · ReconcileStok dry-run/hapus · context · kebersihan · visibilitas push · penjaga tak bergantung instance · gerbang dua rute pembukuan · FE satu sumber kebenaran | **Matikan kill switch dulu**, baru betulkan isi jalur pembukuan |
| **I** (8 paket) | gerbang tiga endpoint aset · scan aset mobile benar-benar hidup · `specs` array · laporan kerusakan mengubah aset · KPI tak hitung perlengkapan · kebersihan inventory · penanda robot positif · Fase push ADR-0175 | Beberapa menunggu keputusan manusia (lihat bawah) |

**Tiga aturan urutan yang tidak boleh dilanggar:** (1) satukan jam sebelum auto-close; (2) matikan kill switch sebelum membetulkan tanggal/kelompok push; (3) layar jujur sebelum compare-and-set — compare-and-set akan **menambah** jumlah `skipped`, dan bila layarnya belum jujur, perbaikan itu justru memperbanyak pekerjaan yang hilang sunyi.

---

## PERLU CEK DATA — 12 set query baca-saja

Seluruh besaran dampak di laporan ini masih **DUGAAN** sampai query ini dijalankan SPV dari host. Query lengkapnya di §4 laporan final (10 set paling menentukan) dan di tiap laporan sumber (37 set seluruhnya). Yang paling mengubah prioritas:

1. **Apakah jalur tulis ke pembukuan sungguhan sudah tereksekusi** — bila ya, [[ADR - 0015 Push Pergerakan WMS ke Accurate]] §Status ("belum pernah tereksekusi") sudah usang dan ini insiden, bukan pencegahan.
2. **Apakah ada `(tanggal, arah)` yang dikirim dua gelombang** — bila ya, ada qty yang **sudah hilang** dari pembukuan Accurate.
3. **Apakah `update_time` di WMS berisi jam server** — membuktikan/membantah E-3 sekaligus menjelaskan mengapa T-9/T-11 tak pernah tertambal.
4. **Berapa order `TO_SHIP` di integration yang tidak ada di WMS** — angka yang **langsung menjawab** keluhan "ada order yang terskip".
5. **Berapa order sudah diserahkan/terkirim tanpa `approved_at`** — keluhan harfiah user, terukur.
6. **Apakah align pernah berhenti di tengah / ada ledger yatim / ada saldo awal terkunci SO yang masternya hilang** — bila ya, pemulihan data mendahului perbaikan kode, dan `/stok/align` **jangan dijalankan** sampai paketnya merge.
7. **Siapa yang pernah approve proposal dan apakah rolenya memang SPV** — silangkan dengan `system_roles.manufacture`; approve tahap SPV oleh akun non-supervisor = B1 sudah dieksploitasi, termasuk tanpa niat jahat (FE mengirim role sesuai tombol yang diklik).
8. **Satu panggilan HTTP dengan token karyawan non-GA** — satu-satunya cara mengonfirmasi D-01; `403` mengonfirmasi, pembanding token GA pada aset sama harus `200`.

**Catatan tafsir yang wajib dibaca:** sync Accurate menimpa stok tiap 6 jam, jadi **ketiadaan stok minus BUKAN bukti race tak pernah terjadi**. Dan backend **tidak** mencatat hasil batch approve ke mana pun, jadi E-1 tak bisa dibuktikan langsung dari data — itu sendiri temuan (ketiadaan jejak audit untuk approve yang gagal).

---

## Menunggu keputusan manusia (bukan pekerjaan kode)

| Yang harus diputuskan | Siapa | Memblokir |
|---|---|---|
| [[ADR - 0136 Pemilik Master Barang dan Master Gudang]] Decision masih **TBD** | SPV + GA + Finance | perbaikan struktural di dua service (gudang dokumen tertinggal saat toko dipindah; master kembar dari pengajuan) |
| Apakah larangan "dokumen terbukuk tidak boleh diubah" **mengamandemen** [[ADR - 0158 Scan Retur Gudang Dijaga Satu Kali dan Selaras dengan Pembukuan, Koreksi Bertahap]] atau sebaliknya | SPV + Finance | jalur bangun-ulang dokumen Retur Penjualan (disengaja per ADR, bukan bug) |
| Boleh/tidak `ReconcileStok` dipakai sama sekali | SPV + Finance | paket M10 |
| Apakah **Lazada masuk cakupan WMS** | SPV | paket W3-1, severity E-5 |
| Pelabelan & panel untuk order yang ditutup otomatis / dibatalkan setelah resi tercetak | SPV + gudang | paket W2-2 |
| Niat fitur **scan QR aset mobile**: semua karyawan atau hanya GA | SPV + GA | paket I2 |
| [[ADR - 0123 Preventive Maintenance Berjadwal per Aset di Inventory Service, Skor dari Penyelesaian Berbukti]] §8 **TBD** — tiket vs `repair_history` sebagai catatan resmi kerusakan | SPV + GA | paket I4. Lihat juga [[ANALISA - Preventive Maintenance Berjadwal per Aset]] |
| Hak **Admin QC** pada `queue/export` (premis "read-only MVP" belum diuji ke vault) | SPV | T-7 |
| Menu **Kelola Pesanan**: sembunyikan atau ganti angka dummy jadi placeholder | SPV | T-18. Lihat [[WH - Kelola Pesanan (Order Management)]] |
| Ambang pagar bulan buku untuk push WMS | Finance | paket M4 |
| Koreksi dokumen Accurate yang sudah terbit salah tanggal/qty | Finance | paket M2, M3 |
| Skor KPI `akurasi_aset_ga` yang sudah terbit terkontaminasi | HR + SPV | paket I5 |
| Jadwal Fase push [[ADR - 0175 Stok GA di ERP Jadi Stok Operasional, Barang Keluar dan Penyesuaian Dikirim ke Accurate]] | SPV + Finance | paket I8 |

---

## Yang TIDAK diperiksa siapa pun — jujur

Ketiadaan temuan di area berikut **bukan** pernyataan sehat.

**Manufaktur:** dossier Batch Record + Rekonsiliasi MO (hanya rute & gerbangnya dibaca; lihat [[Manufacture - Dokumen Produksi Batch]]) · ekspor & sweep retur (~2.500 baris; area dengan 70+ test dan sejarah insiden 56 scan hilang) · **seluruh rumus KPI** (lihat [[Manufacture - Kesiapan Otomasi KPI (menunggu WMS)]]) · bundle/SKU mapping, substitusi, selisih RM, konsinyasi, K3, ceklis GMP, lot bahan, resi.

**Gudang/WMS:** modul komplain (~1.500 baris) — brief menyebutnya sebagai cakupan, **ini lubang terbesar** · laporan produk terkirim + notifikasi WhatsApp (1.422 baris, **live di produksi sejak 2026-10-12**; lihat [[WH - Laporan Produk Terkirim per Gudang]]) · import xlsx produk gudang · perhitungan skor KPI dispatch/waste · sisi integration sampai klien marketplace (perilaku async Shopee vs sync TikTok).

**Retur/pembukuan:** FE auto-sync-return & inventories — **nol temuan dan nol klaim sehat** · penerimaan procurement termasuk [[ADR - 0100 Penerimaan Beda dengan Accurate Diputus di Halaman Penerimaan]] (lihat [[WH - Inbound (Receiving)]]) · isi penuh usecase retur (9.421 baris).

**Aset/inventory:** modul Booking Ruang · modul Permintaan Barang GA (rantai persetujuan, notifikasi, transisi status) · pembagi stok dengan kunci in-process yang **tidak menjaga apa pun bila service berjalan >1 replika** — DUGAAN, belum diverifikasi, layak task sendiri (relevan dengan [[ADR - 0155 Build Sekali di Lokal, Image yang Sama Naik ke Prod lewat Jenkins dan Docker Swarm]]) · scanner lain di [[APP - MyBharata]] yang memakai pola `mobile_scanner` serupa.

**Lintas-area:** pemeriksaan sistematis "test hijau yang tak membuktikan apa pun" · **nol `go build`, nol `go test` dijalankan** · angka agregat yang tidak dihitung ulang (sampel barisnya selalu dibuka, hitungannya tidak) · ADR-0069/0123/0136/0158 dipakai lewat klaim laporan + grep ketiadaan kode, bukan pembacaan penuh.

**Bias yang wajib diketahui:** verifikasi silang membaca kode yang **sama** dengan auditornya. Ia menangkap klaim yang salah baca atau salah baris; ia **tidak** menangkap temuan yang keempat laporan lewatkan bersama-sama. Dan tidak satu pun dari rangkaian audit ini menyentuh data produksi.

---

## Dokumen Terkait

- [[Manufacture - Issue Code Audit 2026-06]] — status per baris audit Juni diperbarui 2026-10-14 sesuai re-cek yang terverifikasi
- [[Microservices - Manufacture Service]] · [[Microservices - Warehouse Service]] · [[Microservices - Inventory Service]] · [[Microservices - Integration Service]]
- [[WH - Fulfillment Flow & WMS Tinggarjaya]] · [[WH - Management System]] · [[WH - Warehouse Sadewa]] · [[WH - Outbound (Sending)]]
- [[Manufacture - Stock & Material Management]] · [[Manufacture - Material Order (SPK)]]
- [[APP - Web ERP]] · [[APP - MyBharata]]
- [[ADR - 0015 Push Pergerakan WMS ke Accurate]] · [[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]] · [[ADR - 0069 Perlengkapan Per-Unit Opsional di inventory dengan Guard Anti-Kontaminasi]] · [[ADR - 0123 Preventive Maintenance Berjadwal per Aset di Inventory Service, Skor dari Penyelesaian Berbukti]] · [[ADR - 0136 Pemilik Master Barang dan Master Gudang]] · [[ADR - 0144 Retur yang Sudah Dibukukan Manual oleh Finance Ditandai per Order dan Dihormati Semua Jalur Auto-Sync]] · [[ADR - 0158 Scan Retur Gudang Dijaga Satu Kali dan Selaras dengan Pembukuan, Koreksi Bertahap]] · [[ADR - 0175 Stok GA di ERP Jadi Stok Operasional, Barang Keluar dan Penyesuaian Dikirim ke Accurate]]
- [[RUN - Selaraskan Kode Bahan WMS ke Accurate]]
- [[ANALISA - Pengaman Scan Retur Gudang]] · [[ANALISA - Preventive Maintenance Berjadwal per Aset]] · [[ANALISA - Kurangi Siklus Input Retur Gudang]] · [[ANALISA - Selisih Retur]]
