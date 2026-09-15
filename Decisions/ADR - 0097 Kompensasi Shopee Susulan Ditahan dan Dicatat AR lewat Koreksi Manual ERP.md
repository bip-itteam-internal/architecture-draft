## Untuk Manajemen

Shopee kadang membayar kompensasi satu pesanan **lebih dari sekali** (contoh prod `260727RQANT17V`: Rp50.000 cair 20 Agustus, lalu Rp109.000 cair 24 Agustus), dan tidak memberi tanda kapan cicilannya selesai. Mulai tanggal yang diisi di pengaturan `shopee-compensation-susulan-hold-date`, **cicilan pertama tetap dibukukan otomatis**, sedangkan **cicilan kedua dan seterusnya ditahan**: tidak masuk penerimaan Accurate, dikabarkan lewat notifikasi, dan dicatat tim AR dari laman baru **Kompensasi Cicilan** lewat koreksi manual ERP dengan nominal, pesanan, dan akun sudah terisi. Akun sarannya: cicilan kedua cair di bulan yang sama dengan cicilan pertama → akun diskon (4003); beda bulan → Pendapatan Lain-lain (8001).

**Terdampak**: tim AR/finance (antrean baru, notifikasi, chip "Kompensasi ditahan" di Auto-Sync Penerimaan, field Akun di form koreksi manual). **Yang TIDAK dijanjikan**: pembukuan otomatis cicilan kedua; penanda "kompensasi final" (Shopee tak punya); penerimaan hari yang isinya hanya kompensasi ditahan **tidak** bisa dicatat lewat ERP (dicatat langsung di Accurate); mengambil editan manual di Accurate ke ERP (dikerjakan terpisah). **Besaran kerja**: sedang, sudah terimplementasi di branch.

## Deskripsi

*Menggantikan perlakuan cicilan susulan kompensasi Shopee yang dicatat di [[Microservices - Integration Service]] (PR #1731: susulan dibukukan sebagai tambahan pelunasan faktur; PR #1782: kelebihan kompensasi tetap diskon 4003 bernilai minus) — untuk hari penerimaan pada/sesudah tanggal kv. Hari sebelumnya tetap memakai model lama supaya dokumen yang sudah terkirim tak di-EDIT.*

- **Status**: ⚠️ **Diterima, terimplementasi di branch `fix/kompensasi-shopee-cicilan`, belum PR, belum merge, belum deploy** (diperiksa 2026-09-15: bip-erp 6 commit, erp-frontend 4 commit, keduanya belum di remote). Berlaku di prod hanya setelah deploy **dan** kv diisi manusia.
- **Path di repo**:
  - `bip-erp/services/integration/internal/usecase/accurate_receipt_wallet_adjustment.go` (penahanan di `resolveWalletAdjustments`, `catatPenahananShopee`, `penahananTersimpan`)
  - `bip-erp/services/integration/internal/usecase/accurate_receipt_kompensasi_cicilan.go` (laman, aturan akun, `statusPenahananPenerimaan`)
  - `bip-erp/services/integration/internal/usecase/accurate_receipt_usecase.go` (`processShopeeDay`, detail, `List`)
  - `bip-erp/services/integration/internal/domain/entity/accurate.go` · `accurate_receipt.go` (kv, `HeldCompensations`)
  - `bip-erp/services/integration/internal/interface/http/accurate_receipt_handler.go` · `main.go` (`GET /accurate/compensation-installments`)
  - `erp-frontend/src/app/(main)/integration-accurate/kompensasi-cicilan/page.tsx`
  - `erp-frontend/src/features/integration/accurate/kompensasi-cicilan/` · `lib/kompensasi-cicilan.ts` · `lib/held-compensation.ts` · `receipts/components/receipt-held-compensations-section.tsx` · `receipts/components/receipt-adjustment-form-modal.tsx`
- **Tanggal**: 2026-09-15

## Context

1. **Kasus prod.** Order `260727RQANT17V` (Kyura Beauty) menerima kompensasi Rp50.000 (20 Agu) dan Rp109.000 (24 Agu). Penerimaan otomatis membukukan cicilan kedua sebagai tambahan pelunasan faktur yang sudah lunas (model PR #1731), lalu dokumen `INC/2026/08/20/005-KY+GB` dan `INC/2026/08/24/003-KY+GB` diedit manual di Accurate. Enam order Agustus punya kompensasi bertahap; lima di antaranya kedua cicilannya di bulan yang sama.
2. **Shopee tak punya penanda "kompensasi sudah final".** Mesin hanya bisa tahu bahwa sebuah mutasi **bukan** yang pertama (Σ kompensasi pesanan yang sama dengan `create_time` lebih awal > 0), bukan kapan cicilannya berhenti.
3. **Keputusan finance 2026-09-14**: cicilan pertama tetap otomatis; cicilan kedua dst ditahan untuk tindak lanjut manual. **Aturan tim AR 2026-09-15**: satu bulan → dicatat di penerimaan tanggal cair cicilan kedua sebagai pembalik diskon (akun diskon); beda bulan → Pendapatan Lain-lain; pencatatan lewat ERP, bukan langsung di Accurate.
4. **Yang sudah ada dan dipakai ulang**: koreksi manual penerimaan (`receipt_manual_adjustments`, digabung tiap pembangunan ulang lewat `mergeManualAdjustments`), notifikasi receipt, akun dari kv Accurate (`discount`, `other-income`, `settlement-adjustment`).
5. **Temuan review 2026-09-15** yang membentuk §4 dan §5: (a) hari yang isinya **hanya** kompensasi ditahan di-SKIP **sebelum** koreksi manual digabung, sehingga koreksi di sana tak pernah terbukukan padahal status awal menandainya selesai; (b) daftar penahanan yang dihitung ulang tiap run bisa **melepas** entri (kv dikosongkan, riwayat yang sempat gagal kini terbaca) lalu membukukannya otomatis di samping koreksi manual finance — penjaga TERSUSUL koreksi hanya mengenal order escrow hari itu, jadi uangnya terbukukan dua kali tanpa galat.

## Decision

### 1. Cicilan kedua dst ditahan, maju dari tanggal kv

kv `shopee-compensation-susulan-hold-date` (`YYYY-MM-DD`, hari penerimaan WIB). Kosong / format salah → perilaku lama. Untuk hari penerimaan ≥ tanggal itu, kompensasi dengan kompensasi sebelumnya > 0,5 **tidak dibukukan lewat cabang mana pun** (termasuk fallback Pendapatan Lain-lain). Riwayat yang gagal dibaca juga ditahan (menahan paling buruk meminta finance memeriksa; membukukan bisa dobel). Vonis FO dan anti-dobel settlement diputus **lebih dulu**: uang pesanan FO / yang sudah terserap settlement memang tak masuk penerimaan.

Yang ditahan disimpan di dokumen penerimaan (`held_compensations`: order, `transaction_id` — string di JSON —, tipe, nominal, waktu cair, kompensasi sebelumnya, catatan), ditulis hanya bila berubah, dan dikabarkan **sekali** per mutasi baru dengan tautan laman. Tak masuk payload maupun cheque. Hari yang tak menghasilkan apa pun berketerangan SKIPPED "N kompensasi susulan ditahan", bukan "era manual".

### 2. Laman Kompensasi Cicilan dan aturan akun

`GET /accurate/compensation-installments` mendaftar tiap kompensasi ditahan: cicilan pertama (mutasi paling awal pesanan itu) beserta nomor penerimaannya, cicilan ditahan, akun saran, status. Aturan dinilai dari tanggal cair **dalam WIB**: bulan sama → kv `discount`; beda bulan → kv `other-income`; cicilan pertama tak ditemukan / riwayat gagal / kv kosong → akun kosong + catatan. Nomor akun tak pernah ditulis di kode maupun FE. Tombol **Catat** membuka form koreksi manual di penerimaan tanggal cair cicilan yang ditahan dengan nominal, pesanan, dan akun terisi; akun yang sama dipakai tombol "Bukukan manual" di detail penerimaan.

### 3. Field Akun di form koreksi manual

Opsional, hanya untuk koreksi uang (tambah/kurangi). `account_no` dikirim **hanya bila diisi**; kosong = default kv `settlement-adjustment` seperti sebelumnya.

### 4. Status tiga arah — "Selesai" hanya bila benar-benar terkirim

Satu fungsi (`statusPenahananPenerimaan`) dipakai laman, detail penerimaan (`held_statuses`), dan chip daftar (`held_waiting_count`):
- **MENUNGGU** — belum ada koreksi manual AKTIF yang memuat pesanan itu di penerimaan tempat ditahan;
- **TERTUNDA** — koreksinya ada, tapi penerimaan belum SENT dengan `last_sent_at` ≥ `created_at` koreksi;
- **SELESAI** — sudah terkirim sesudah koreksi dibuat.

Penerimaan **SKIPPED** ditandai kosong (`penerimaan_kosong` / `held_receipt_empty`): tombol Catat tak ditawarkan dan layar menyuruh mencatat langsung di Accurate. Filter bawaan laman **PERLU_TINDAKAN** = MENUNGGU ∪ TERTUNDA. Status dibaca tiap kali, tak disimpan: koreksi yang di-void mengembalikan barisnya ke MENUNGGU. Laman membalas galat bila koreksi gagal dibaca; detail dan chip fail-soft ke MENUNGGU.

### 5. Penahanan lengket

Mutasi yang sudah tersimpan di `held_compensations` **tetap ditahan persis seperti tersimpan** pada pembangunan berikutnya, apa pun jawaban gerbang sekarang — termasuk saat kv dikosongkan. Tak ada endpoint pelepasan: tindak lanjutnya adalah koreksi manual. Entri yang keluar dari daftar (mis. pesanannya kini divonis FO) dikabarkan "DILEPAS" beserta ada/tidaknya koreksi aktif. Jalur baca (dry-run, ekspor rincian) memakai penahanan tersimpan yang sama supaya komposisinya tak berbeda dari jalur kirim.

## Consequences

### Yang membaik

- Satu kompensasi tak lagi dibukukan dengan dua perlakuan (otomatis di satu dokumen, diedit manual di dokumen lain); akunnya dipilih aturan AR yang tertulis.
- Uang yang ditahan tak hanya hidup di satu notifikasi: ada di dokumen penerimaan, chip daftar, detail, dan laman lintas tanggal/toko.
- "Selesai" tak lagi bisa berarti "koreksi tersimpan tapi tak pernah sampai ke Accurate".

### Yang memburuk atau diterima sadar

- **Mengosongkan kv hanya menghentikan penahanan BARU.** Yang sudah ditahan tetap ditahan (§5); rollback penuh butuh pencatatan manualnya diselesaikan.
- **Penerimaan kosong tak bisa ditutup lewat ERP**: yang dicatat langsung di Accurate tetap tampil MENUNGGU di laman (ERP tak tahu). Menutupnya menunggu kemampuan mengambil editan Accurate.
- **Status dinilai per nomor pesanan, bukan per mutasi**: dua cicilan ditahan untuk pesanan yang sama di penerimaan yang sama selesai dengan satu koreksi.
- **Akun saran "satu bulan → diskon" menganggap cicilan pertama dibukukan sebagai pelunasan + diskon**; bila cicilan pertama jatuh ke fallback Pendapatan Lain-lain, sarannya perlu dikonfirmasi AR (belum diputuskan).
- **Laman menghitung semua baris sebelum filter & paginasi** (kueri koreksi per penerimaan, riwayat dompet per pesanan dengan `$regex` description, batas 2000 penerimaan). Aman untuk volume prod sekarang, akan menyentuh batas gateway seiring waktu.
- **Dua kompensasi dengan `create_time` identik sampai detik sama-sama dianggap pertama** (perilaku lama, tak diubah).
- **Notifikasi "sekali" bisa terulang** bila dua pembangunan berjalan bersamaan (dokumen dibaca sebelum lock), tanpa merusak data.
- **Deploy**: integration-service lebih dulu, lalu erp-frontend (field & endpoint aditif); tanpa env baru; kv diisi manusia sesudah deploy.

### Yang sengaja tidak dilakukan

- Membukukan cicilan kedua otomatis ke 8001 atau diskon: aturan akunnya bergantung bulan cicilan pertama dan pertimbangan AR per kasus.
- Menyimpan status ke dokumen penerimaan: salinan yang tak ikut berubah saat koreksi di-void.
- Endpoint "lepas penahanan": belum ada kasus yang memerlukannya.

## Dokumen Terkait

- [[Microservices - Integration Service]] — bagian Auto Sales Receipt (catatan PR #1731, #1782, dan penahanan)
- [[API - Integration Service]] — `GET /accurate/compensation-installments`, field `held_*`, `account_no` koreksi manual
- [[APP - Web ERP]] — laman Kompensasi Cicilan, chip, seksi detail, field Akun
- [[ADR - 0001 Akuntansi via Accurate]]
