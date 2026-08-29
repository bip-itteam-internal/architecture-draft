## Deskripsi

*Modul Pengajuan Budget diganti menjadi **Pengajuan Pembelian** bertipe empat (barang umum, raw material, software, iklan), dengan rantai persetujuan yang berlanjut sampai barang diterima. Kas kecil dipensiunkan bertahap.*

- **Status**: ⚠️ **Implemented (ada catatan)** — kode backend dan frontend sudah di `main` kedua repo (diverifikasi 27 Agustus 2026: 22 berkas `services/procurement/pengajuan_pembelian*` dan modul `erp-frontend/src/features/procurement/pembelian`). **Keadaan deploy tidak diverifikasi** pada pemeriksaan itu. Catatan yang masih terbuka ada di bagian bawah dokumen ini. Spesifikasi lengkap: `bip-erp/docs/superpowers/specs/2026-08-26-pengajuan-pembelian-empat-tipe-design.md`
- **Path di repo**: `bip-erp/services/procurement/pengajuan_budget*.go` (diganti) · `bip-erp/services/inventory` · `bip-erp/services/manufacture`
- **Tanggal**: 2026-08-26

## Context

Modul Pengajuan Budget yang berjalan sekarang berhenti di status `DISETUJUI`, dan efek satu-satunya adalah menambah `TambahanTopUp` pada plafon kas kecil unit periode itu. Pengajunya **SPV**, jalurnya ditentukan `Tujuan` yang dipilih pemohon (FINANCE/GA/PROCUREMENT), dan rantainya satu sampai tiga tahap.

Kebutuhan yang diminta pemilik proses berbeda pada empat hal pokok:

1. **Pengaju adalah staf**, bukan SPV. Persetujuan tahap pertama justru datang dari SPV.
2. **Jalur ditentukan jenis belanjanya**, bukan pilihan pintu. Empat jenis dengan perlakuan berbeda: barang umum, raw material, software, iklan.
3. **Alur berlanjut sampai barang diterima** — pembelian oleh Procurement, pembayaran oleh AP, persetujuan pembayaran oleh SPV Finance, lalu penerimaan di gudang. Modul lama berhenti jauh sebelum titik itu.
4. **Tidak semua divisi boleh mengajukan semua jenis.**

[[REF - Rantai Pengajuan Lintas Modul]] §3 mencatat modul ini sebagai salah satu rantai yang terputus: `PengajuanBudget` → `TransaksiKas` tersambung **hanya lewat agregat plafon**, sehingga *"transaksi mana merealisasikan pengajuan mana"* tak terjawab. Dokumen yang sama, §5, membuktikan `BuatPenerimaanHandler` hanya `InsertOne` — **penerimaan barang di ERP tidak menambah stok mana pun.**

Pemeriksaan kode untuk desain ini (26 Agustus 2026) mengonfirmasi keduanya secara independen, dan menemukan satu hal lagi: `services/inventory` **tidak punya stok berjumlah sama sekali** — nol referensi qty/stok; barang GA dilacak sebagai **aset per unit** (master item, kategori, repair, handover).

## Decision

### 1. Ganti total, bukan modul berdampingan

`PengajuanBudget` diganti `PengajuanPembelian` pada koleksi baru `pengajuan_pembelian`. Modul lama tidak dipertahankan berdampingan: dua pintu pengajuan untuk maksud yang sama akan membuat orang memilih salah satu tanpa dasar.

Yang **dipertahankan** karena sudah terbukti: nominal dihitung server dari rincian item, `JenjangWajib` dan `AmbangTerpakai` dibekukan saat diajukan, alokasi akuntansi dengan nama disalin, penomoran `PB-<DEPT>-<YYYYMMDD>-<NNN>`, dan penjaga "pengaju tidak boleh menyetujui dirinya sendiri".

### 2. Tipe menentukan rantai

```
UMUM        spv_divisi     → spv_finance → [direktur] → procurement → ap → spv_finance_bayar → terima_ga
RAWMATERIAL spv_manufactur → spv_finance → [direktur] → procurement → ap → spv_finance_bayar → qc → terima_rm
SOFTWARE    spv_divisi     → spv_finance → [direktur] → procurement → ap → spv_finance_bayar
IKLAN       spv_divisi     → spv_finance → [direktur] → procurement → ap → spv_finance_bayar
```

`[direktur]` disisipkan hanya bila nominal mencapai ambang (default Rp 3.000.000, **parameter berversi** bukan konstanta). `Tipe` beku setelah diajukan.

Raw material selalu disetujui **SPV Manufactur** meskipun pengajunya staf gudang — approver tahap pertama diturunkan dari tipe, bukan dari departemen pengaju.

### 3. Status tetap kasar, posisi di `TahapSaatIni`

`DRAFT`/`BERJALAN`/`SELESAI`/`DITOLAK`/`REVISI`/`DIBATALKAN`. Rantainya sudah tersimpan di `JenjangWajib`; status per tahap berarti satu fakta direkam dua kali. Mesin `TahapBerikutnya` menelusuri lewat **posisi dalam jenjang**, sehingga rantai delapan tahap tidak lebih rumit daripada tiga.

`DITOLAK` **hanya** untuk penolakan di gerbang persetujuan, saat belum ada uang keluar.

### 4. QC tidak lolos mengembalikan ke Procurement, bukan menutup dokumen

Satu-satunya jalur mundur. `TahapSaatIni` kembali ke `procurement`, status tetap `BERJALAN`, alasan wajib. **Putaran tidak boleh menyentuh uang**: tahap `procurement` memeriksa `NomorPO` — bila sudah terisi, PO baru tidak dibuat. Membeli ulang berarti pengajuan baru.

### 5. Penerimaan bertahap, satu RI per pengajuan

Barang boleh datang sebagian; `QtyDiterima` diakumulasi per baris. **RI terbit sekali** saat lengkap atau saat ditutup paksa dengan alasan — bukan satu RI per pengiriman, supaya tidak lahir dokumen penerimaan berulang untuk satu pesanan.

### 6. Ekor menyentuh stok lewat jalur yang sudah ada

- **Raw material** memanggil `POST /transaksi` milik `services/manufacture` (ber-`deltaStok`).
- **Barang umum** melahirkan **item aset** di `services/inventory`, satu per unit — bukan menambah angka stok, karena GA memang bukan gudang berjumlah.

Tidak ada jalur stok baru yang dibuat.

### 7. RBAC lewat permission per tipe

`budget.pengajuan.umum` · `budget.pengajuan.rawmaterial` · `budget.pengajuan.software` · `budget.pengajuan.iklan`, ditambah `budget.ap.bayar` · `budget.approve.pembayaran` · `budget.qc.periksa` · `budget.terima.ga` · `budget.terima.rm`.

Bukan matriks tipe×departemen yang dikelola terpisah: matriks semacam itu menjadi sumber kebenaran kedua di samping RBAC.

Izin approve pembayaran **dipisah** dari approve pengajuan meskipun keduanya SPV Finance, supaya orangnya bisa dibedakan tanpa mengubah kode.

### 8. Kas kecil dipensiunkan bertahap

Tahap pertama mencabut rute dan menu, memindahkan kode yang masih dipakai ke nama netral, dan **tidak menyentuh koleksi Mongo**. Penghapusan berkas menyusul di perubahan terpisah, dengan prasyarat dibuktikan lebih dulu: `kas_jurnal_outbox` tidak punya baris `PENDING`.

## Consequences

### Yang membaik

- Rantai §3 pada [[REF - Rantai Pengajuan Lintas Modul]] **tertutup dari sisi hulu**: satu dokumen berjalan dari pengajuan sampai barang diterima, dan "sekarang di mana" punya satu jawaban.
- Rantai §5 (penerimaan tidak menambah stok) tertutup **untuk jalur ini saja** — penerimaan yang lahir dari pengajuan akan menambah stok/aset.
- Mesin `JenjangWajib` + `TahapSaatIni`, yang [[REF - Rantai Pengajuan Lintas Modul]] sebut *"satu-satunya rantai n-tahap sungguhan"* di seluruh repo, dipakai untuk rantai yang jauh lebih panjang — menguji bentuknya sebelum ada yang mempertimbangkan mengangkatnya ke `shared-library`.

### Yang ditemukan setelah dipakai (27 Agustus 2026)

Pembedahan alur menemukan empat titik yang benar secara kode namun membuat orangnya tak dapat menyelesaikan pekerjaannya. Ditutup lewat [[ADR - 0057 Penyetuju Pengajuan Pembelian Ditetapkan per Tahap]]:

- **Rantainya tak punya alamat.** Satu-satunya notifikasi di modul ini adalah QC gagal, sehingga delapan tahap bergerak hanya bila orangnya kebetulan membuka menu.
- **Status `REVISI` tak punya layar sunting.** Yang tersedia bagi pengaju hanya tombol Ajukan, yaitu mengirim ulang dokumen yang sama persis yang baru saja dikembalikan.
- **Pembuatan selalu melahirkan DRAFT tanpa mengatakannya.** Tombolnya bernama "Simpan", layarnya berpindah, dan pengaju mengira sudah mengajukan.
- **`tautan` yang diisi pengaju tak pernah dirender**, jadi penyetuju memutuskan tanpa bahan yang sudah dikirimkan kepadanya.

### Yang memburuk atau tetap terbuka

- ⚠️ **Rantai `permintaan_erp` → `pesanan_erp` → `penerimaan_erp` menjadi jalur kedua.** Pengajuan Pembelian menerbitkan PO dan RI sendiri, sementara jalur PR→PO→RI yang ada tetap hidup. [[REF - Rantai Pengajuan Lintas Modul]] §4 sudah mencatat jalur itu setengah tersambung dengan empat konstanta status yang tak pernah ditulis. **Belum diputuskan** apakah keduanya akhirnya dilebur.
- **Stok bertambah sebelum RI terbit** pada penerimaan bertahap. Diterima sadar: menahan stok sampai lengkap berarti barang fisik ada di gudang sementara sistem menyatakan belum.
- **Barang gagal QC berhenti sebagai keadaan, bukan proses.** Retur ke pemasok di luar cakupan; notifikasi ke Procurement dan Finance yang menjaga agar dokumennya tidak diam tanpa penanggung jawab.
- **Jalur top-up plafon kas kecil hilang** bersama pensiunnya kas kecil.
- Butuh **endpoint baru** di `services/inventory` untuk membuat item aset dari procurement.

### Yang sengaja tidak dilakukan

- Tidak membangun mesin alur bersama di `shared-library`. [[REF - Rantai Pengajuan Lintas Modul]] menaruhnya di urutan terakhir dengan alasan yang berlaku di sini: mengangkat abstraksi sebelum ada tiga pemakai nyata adalah pola yang sudah berulang salah di repo ini.
- Tidak ada jalur "catat mundur" untuk tahap yang dilompati. Alur wajib tertib.
- Ambang tidak dibedakan per tipe, meskipun bentuk datanya menampung.

## Dokumen Terkait

- [[Finance - Kas Kecil dan Pengajuan Budget]] — modul yang digantikan
- [[REF - Rantai Pengajuan Lintas Modul]] — §3 dan §5 adalah rantai yang keputusan ini sentuh
- [[REF - Alur Persetujuan]] — siapa yang berwenang memutuskan
- [[Microservices - Procurement Service]] · [[Microservices - Inventory Service]] · [[Microservices - Manufacture Service]]
- [[CORE - RBAC dan Permission Set]] — katalog izin
- [[ADR - 0001 Akuntansi via Accurate]] — alasan modul ini tidak menjurnal sendiri
