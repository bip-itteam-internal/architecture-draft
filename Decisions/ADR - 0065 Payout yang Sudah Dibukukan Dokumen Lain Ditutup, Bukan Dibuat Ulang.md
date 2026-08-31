## Untuk Manajemen

- **Yang berubah di layar**: 233 penerimaan Juli yang selama tiga minggu tercatat GAGAL kini bertanda **"Dibukukan di luar auto-sync"**. Bukan uang baru — uangnya memang sudah ada di Accurate sejak awal, cuma di dokumen bernomor lain.
- **Siapa terdampak**: finance yang mencocokkan pencairan TikTok, dan siapa pun yang membaca daftar Auto-Sync lalu menyimpulkan "ada Rp263,7 juta belum terbukukan".
- **Tidak dijanjikan**: sistem **tidak** membuat ulang dokumen yang hilang, dan tidak akan. Membuat ulang berarti penerimaan dobel.
- **Besaran kerja**: kecil di kode, besar di pembuktian — sebagian besar usaha dipakai membuktikan bahwa dokumen penggantinya memang milik toko yang sama.

## Deskripsi

*Bila payout sebuah statement sudah dibukukan oleh dokumen Accurate yang BUKAN milik auto-sync, receipt-nya ditutup di sisi ERP dan dicatat siapa pembukunya — tidak dibuat ulang, tidak pula ditautkan ke dokumen itu.*

- **Status**: ✅ **Accepted**, 2026-08-30. Diterapkan ke 233 receipt Juli 2026 pada hari yang sama.
- **Path di repo**: `bip-erp/services/integration/internal/usecase/receipt_dibukukan_eksternal.go` · `internal/domain/entity/accurate_daily_invoice.go` (`HoldReasonBookedExternally`) · `cmd/receiptbooked`
- **Tanggal**: 2026-08-30

## Context

239 receipt TikTok Juli 2026 berstatus `FAILED`. Errornya bermacam-macam — 401 token, "receipt id not found in accurate for edit" — dan percobaan terakhirnya tertanggal **5 Agustus**. Sejak itu tak satu pun dicoba lagi: `ReceiptMaxAutoAttempts = 5` membuat setiap jalur otomatis melewatinya **diam-diam**, tanpa alarm.

Dilihat dari ERP, ini tampak seperti **Rp263,7 juta penerimaan Juli yang belum terbukukan**. Dicari lewat `accurate_id` → tidak ada. Dicari lewat nomor `INC/2026/07/…` → juga tidak ada.

Yang menutup celahnya adalah pencarian lewat **nilai**: seluruh 826 penerimaan Accurate sepanjang Juli didaftar, lalu dicocokkan tanggal + nilai. Dokumennya ada — dengan skema penomoran yang sama sekali berbeda:

| Yang ERP cari | Yang berdiri di Accurate | Cheque |
|---|---|---:|
| INC/2026/07/13/009-BH | KTB-TIKTOK-BHCOID-20260713-014-MXS | 17.701.150 |
| INC/2026/07/16/010-KY+GB | KTK-TIKTOK-KYURAOFC-20260716-016-MXS | 20.314.286 |
| INC/2026/07/22/011-BH | KTB-TIKTOK-BHSTORE-20260722-022-MXS | 2.008.890 |

Satu dokumen dibuka isinya: `KTB-TIKTOK-BHSTORE-20260722-022-MXS` memuat 13 baris faktur, Σ `paymentAmount` 2.963.000 − potongan 954.110 = cheque **2.008.890**, sama persis dengan `payable_amount` statement. Dokumen itu utuh dan balance, dalam model yang sama dengan yang dipakai auto-sync — bukan tempelan.

Jadi ERP membuat dokumen `INC/…`, pihak lain membukukan payout yang sama lewat skema `MXS`, lalu dokumen ERP dihapus. Yang tersisa di ERP hanyalah penunjuk yang sudah mati.

## Decision

**Berhenti, dan catat siapa yang membukukannya.** Receipt diberi `last_status = SKIPPED` + `hold_reason = BOOKED_EXTERNALLY`, dengan `last_error` memuat nomor dan id dokumen pembukunya. `accurate_id` dan `last_sent_at` **tidak** disentuh — keduanya jejak audit.

Dua jalan keluar lain ditolak, dan penolakannya yang justru penting:

- **Mengosongkan `accurate_id`** supaya jalurnya jadi CREATE → **penerimaan dobel Rp263,7 juta**. Penjaga yang ada (bila `accurate_id` terisi tapi dokumennya tak terbaca, proses berhenti dan tak pernah membuat baru) sudah benar dan tidak dilonggarkan.
- **Menautkan ulang** `accurate_id` ke dokumen `MXS` → request simpan Accurate ikut membawa field `Number`, sehingga EDIT akan **mengganti nama** dokumen itu jadi `INC/…` sekaligus menimpa seluruh barisnya. Dokumen itu bukan milik kami.

**Padanan wajib dibuktikan tiga lapis**, dan setiap keraguan berakhir dilewati — tak pernah ditebak:

1. **Nilai** — `payable_amount` statement + tanggal, toleransi Rp1. Kuncinya payable, **bukan** `cheque_amount` tersimpan: pada 9 dari 26 receipt yang ditelusuri, cheque tersimpan melenceng jauh dari payout (Rp139.468 vs Rp33.149.499; satu bahkan negatif) — sisa hitungan yang gagal, bukan uang yang cair. `payable_amount` datang dari TikTok, satu-satunya angka yang bukan hitungan kami sendiri.
2. **Kepemilikan** — tiap baris faktur dokumen padanan ditelusuri ke `accurate_daily_invoices`. **Satu** baris milik toko/kanal lain membatalkan padanan. Tanpa lapis ini, dua toko yang cair dengan nilai sama di hari yang sama cukup untuk menautkan statement ke dokumen yang keliru — tanpa selisih yang bisa dilihat siapa pun, karena totalnya memang sama.
3. **Balance** — Σ `paymentAmount` − Σ potongan = cheque. Menangkap dokumen bertotal benar dengan alokasi kacau, yang lolos dari dua lapis sebelumnya.

Pembatalan disediakan sejak awal: `cmd/receiptbooked -undo` memulihkan dari arsip nilai lama, dan Retry manual dari layar menembus penahan.

## Consequences

- **233 dari 239** receipt Juli ditutup (dry-run dan apply memberi angka sama). Sisa 6: satu dokumennya ternyata masih ada (prasyarat menolaknya, lalu Retry biasa menyembuhkannya), lima tak berpadanan.
- **Nol tulisan ke Accurate.** Alatnya tak punya jalur tulis ke sana sama sekali — bukan kehati-hatian, melainkan bentuk kodenya: salah logika pun tak bisa membuat dokumen dobel.
- Penahan mengikat jalur **otomatis** saja, dan dipasang di **tiga kanal** (TikTok/Shopee/Lazada) sekaligus meski kejadiannya baru di TikTok — pola "diperbaiki di satu kanal saja" sudah berulang di layanan ini.
- **Yang belum selesai**: lima receipt Juli sisa (±Rp2,56 juta) ternyata fakturnya sudah lunas oleh dokumen `KTG-TIKTOK-GLOWFAST-*-MXS`, jadi tak bisa dicocokkan 1:1 lewat nilai — pengelompokan dokumennya berbeda. Penutupannya belum dikerjakan.
- **Akar yang belum ditutup**: cap 5 percobaan yang menyerah tanpa alarm. Ia sudah jadi penghalang sebenarnya **tiga kali berturut-turut** (233 receipt Juli, 3 receipt Juli sisa, 28 receipt Agustus). Selama kegagalan bisa berhenti tanpa berbunyi, temuan berikutnya akan datang lagi dari pertanyaan kebetulan. Lihat [[Microservices - Integration Service]] § Belum Diimplementasikan.

## Dokumen Terkait

- [[Microservices - Integration Service]] — Auto-Sync → Accurate, penahan dokumen
- [[ADR - 0056 Penyesuaian Statement TikTok Menambah Payout Order]] — statement TikTok, sumber `payable_amount`
- [[ADR - 0014 Accurate Token DB-backed via OAuth]] — kredensial yang dipakai pembacaan Accurate
- [[APP - Web ERP]] — chip penahan di layar Auto-Sync
