> **Status**: ✅ Implemented (21 Juli 2026) — empat menu WMS dipecah dua sub-tab; stempel `created_by_name` aktif di semua jalur tulis manual. Verifikasi visual baru tuntas untuk **Inbound RM** & **Master Resi**; Keluar FG / Input Gudang FG / Laporan Hasil Produksi menunggu pengecekan dengan role yang sesuai (`admin gudang FG`, `admin produksi`).

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
| Keluar FG | resi marketplace (`manufacture_resi`) | transaksi OUTBOUND ber-`marketplaceSalesDetection` |
| Inbound RM Harian | Procurement PO | transaksi penerimaan ber-`picQc` |
| Input Gudang FG | Surat Jalan status `IN TRANSIT` | transaksi INBOUND ber-`gudangSimpan` |

Sumber Inbound RM adalah **Procurement PO**, bukan Accurate — keputusan user 21 Juli 2026 setelah dipastikan tidak ada feed penerimaan barang dari Accurate (sync-nya hanya master & angka stok, bukan transaksi penerimaan). Jadi yang dibandingkan adalah *apa yang dipesan* vs *apa yang benar-benar datang & lolos QC*.

**2. Badge status "sudah/belum dicatat" HANYA di tab yang punya kunci join.**

Return Ekspedisi mempertahankan badge tiga-nilai. Keluar FG dan Inbound RM **sengaja tanpa badge status** — tanpa kunci join, status apa pun di sana adalah tebakan, dan tebakan salah tentang "barang ini sudah keluar/diterima" lebih berbahaya bagi Finance daripada tidak ada badge sama sekali.

Input Gudang FG tidak butuh badge: daftar `IN TRANSIT` per definisi adalah yang belum diterima.

**3. Baris sumber bisa diklik → membuka form terisi**, mengikuti pola `openReturnForm` yang sudah ada. Karena Keluar FG tak punya konsep "belum diinput", semua barisnya bisa diklik dan tooltipnya berbunyi *"memuat resi ini ke form"* — bukan klaim status.

**4. Nama penginput distempel SERVER, bukan dikirim client.** Field `created_by_name` diisi handler dari `c.Get(common.Header.Username)` dan **selalu menimpa** nilai yang datang di body. Alternatif "frontend kirim username dari cookie" ditolak: nilainya dikirim browser sehingga bisa dipalsukan, dan jejak yang bisa dipalsukan bukan jejak audit.

Distempel di: `transaksi` (termasuk `transaksi_fg` & tiga titik di `production`), `production_log`, `resi`, `material_order`, `marketing_po`, `procurement_po`.

**5. Resi hasil sync marketplace TIDAK distempel.** `upsertResiFeed` sengaja dibiarkan kosong — datanya datang dari marketplace, bukan diketik orang. Mengisi nama pemicu sync akan membuat kolom "Diinput oleh" berbohong tentang ribuan baris. Konsekuensi yang diambil sebagai keuntungan: ada/tidaknya nama sekaligus menjadi penanda asal data (manual vs sync) di [[Microservices - Manufacture Service]] tab Master Resi.

## Consequences

**Yang membaik**

- Finance bisa membandingkan sumber vs pencatatan gudang di empat menu, bukan hanya retur.
- Log WMS menampilkan penginput yang tak bisa dipalsukan, terpisah jelas dari field PIC yang diketik manual.
- Baris sumber jadi titik masuk kerja (klik → form terisi), bukan sekadar tabel baca.

**Yang harus diterima**

- **Data lama tampil `—`.** Username tak pernah disimpan sebelumnya dan tidak bisa diisi surut — audit log punya username tapi `Target`-nya tak cukup untuk join balik.
- **Tab sumber Keluar FG & Inbound RM tidak bisa menjawab "mana yang belum diinput"** sampai kunci join ditambahkan (menyimpan nomor resi/PO pada transaksi saat input). Itu perubahan terpisah dan hanya akan akurat untuk data sesudahnya.
- **PO multi-bahan tidak mengisi form penuh.** Form Inbound RM satu bahan per input; untuk PO berisi banyak bahan hanya supplier & tanggal yang diisi, sisanya diserahkan operator. Menebak bahan mana yang sedang diterima akan salah lebih sering daripada benar.
- **Daftar "SJ Belum Diterima" bukan angka pasti.** Status SJ berubah `DELIVERED` hanya bila penerimaan dibuat lewat pilihan *Terima dari Surat Jalan*; penerimaan yang diketik manual tidak menutup SJ-nya, sehingga SJ itu tetap tampil tertunggak walau barangnya sudah masuk. Perilaku pra-ada, baru terlihat sekarang karena datanya ditampilkan sebagai daftar.
- **Tab sumber Keluar FG dibatasi** per tanggal RTS + maksimal 300 baris (`resiList` memuat jendela 60 hari ≈ 14 ribu record); jumlah yang disembunyikan ditampilkan eksplisit agar daftar terpotong tak terbaca sebagai daftar utuh.

## Dokumen Terkait

- [[Microservices - Manufacture Service]] · [[APP - Web ERP]] · [[API - Manufacture Service]]
- [[Manufacture - Stock & Material Management]] (konsep domain)
- [[ADR - 0002 Database-per-Service]] (sebab join retur dikerjakan di kode Go, bukan `$lookup`)
- [[ADR - 0015 Push Pergerakan WMS ke Accurate]] (Input Gudang FG = titik pengakuan stok FG)
