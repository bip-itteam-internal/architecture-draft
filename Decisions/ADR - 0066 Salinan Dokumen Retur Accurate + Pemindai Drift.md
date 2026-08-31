**Status**: ⚠️ **Implemented (ada catatan)** — kode selesai & ber-tes (PR #1552, **belum merge**). Ekspor belum dialihkan ke salinan; penjadwalan pemindai belum dipasang. Lihat "Belum selesai".

# ADR - 0066 Salinan Dokumen Retur Accurate + Pemindai Drift

Baris retur menyimpan **salinan** dokumen Retur Penjualan Accurate agar layar & ekspor tak menembak API tiap kali dipakai — berpasangan dengan pemindai yang membuktikan salinan itu masih mutakhir. Melengkapi [[ADR - 0016 Retur Grouped per Faktur + Tanggal Retur]].

## Context

- Isi dokumen retur **tak pernah disimpan**. Layar detail memanggil `sales-return/detail.do` tiap kali dibuka; ekspor "Laporan Retur" memanggil faktur sumber satu per satu untuk mengambil harga.
- Terukur prod 2026-08: sekali ekspor sebulan = **647 panggilan** (Juli, 3.491 baris) s.d. **955 panggilan** (Agustus, 4.496 baris) berurutan. Lambat, kena batas laju, dan **gagal total** saat Accurate tak terjangkau — layar diam-diam jatuh ke tampilan sintesis yang bentuknya berbeda.
- Accurate **tidak** memberi penanda kapan sebuah dokumen terakhir berubah. Jadi drift tak dapat dideteksi murah lewat perbandingan timestamp.
- Tetapi `sales-return/list.do` mengembalikan `id, number, transDate, **totalAmount**` **100 dokumen sekali panggil**. Memeriksa seluruh 5.019 dokumen SENT ≈ **50 panggilan**, bukan 5.019.
- Dokumen retur memang disunting di luar sistem ini: finance mengoreksi manual di Accurate, dan jalur `append`/`reduce` serta `returnredate` juga mengubahnya.

## Decision

**1. Baris menyimpan `AccurateMirror`** — kepala dokumen (nomor, pelanggan, tanggal, keterangan) + baris **apa adanya** termasuk ekspansi bundle induk/komponen + `Total` + `SyncedAt`. Kepala ikut disalin karena layar detail menampilkannya; salinan tanpa kepala tetap memaksa menembak Accurate sehingga tak menyelesaikan apa pun.

**2. CERMIN UNTUK MELIHAT, ACCURATE UNTUK MEMUTUSKAN.** Tak satu pun jalur pembukuan — rebuild, hapus, append — membaca salinan; semuanya tetap mengambil langsung. Cermin basi yang **ditampilkan** menyesatkan satu layar; cermin basi yang dipakai **membukukan** merusak buku.

**3. Diisi saat DIPAKAI, bukan lewat backfill.** Baris yang tak pernah dibuka tak perlu dibayar, dan tak ada operasi massal atas 5.019 baris yang bisa gagal separuh jalan. Ekspor pertama sebulan tetap selambat sekarang; berikutnya nol panggilan.

**4. Dibatalkan, bukan diperbarui, saat dokumen berubah.** `SetGroupResult` di-`$unset accurate_mirror` — fungsi itu dipanggil persis ketika identitas/isi dokumen berganti (book baru, rebuild, id dilupakan setelah hapus), jadi satu tempat itu membuat cermin mustahil tertinggal. Sengaja **tidak** diisi ulang di sana: itu menambah satu panggilan untuk tiap pembukuan, termasuk dokumen yang mungkin tak pernah dilihat siapa pun.

**5. `Total` dipisah dari baris** supaya pemindai cukup membandingkan satu angka lewat `list.do`.

**6. Pemindai drift `cmd/returndriftscan` — read-only, nol tulis.** Dua kelas temuan: `BEDA_TOTAL` (dokumen ada, nilainya bergeser) dan `DOKUMEN_HILANG` (baris masih mengaku SENT padahal dokumennya tak ada — pembalikan yang dikira tercatat ternyata lenyap). Daftar Accurate kosong (gagal ambil / rentang salah) **tidak** melahirkan temuan: melaporkan semuanya hilang di situ adalah alarm palsu massal yang membuat laporan ini diabaikan selamanya. Toleransi Rp0,5 meredam pembulatan.

**7. Perbaikan lewat manusia, bukan mesin.** `POST /accurate/daily-returns/:id/refresh` (tombol "Segarkan"). Pemindai melapor; ia tak mengoreksi diam-diam.

**8. Accurate tak terjangkau → pakai salinan lama**, bukan jatuh ke tampilan sintesis. Data bertanggal lebih berguna daripada layar yang diam-diam berganti rupa, dan `SyncedAt` ikut terkirim sehingga pembaca tahu persis seberapa lama.

## Consequences

- Layar detail: satu panggilan pada pembukaan pertama, **nol** sesudahnya.
- Salinan **wajib** datang sepaket dengan pemindainya. Men-deploy cermin tanpa pembuktian adalah keadaan yang tak aman: berkas ekspor dipakai finance mencocokkan dengan buku, dan bila ia disuapi salinan tak terverifikasi maka pencocokannya membandingkan salinan dengan salinan — **selalu cocok, selamanya**. Alat pemeriksa yang tak pernah bisa membantah lebih buruk daripada tak ada alat. Karena itu keduanya satu PR.
- **Batas yang diterima sadar**: pemindai membandingkan **total**, jadi perubahan yang tak mengubah total (tukar SKU berharga sama, qty 2×50 → 1×100) tak tertangkap. Menangkapnya perlu `detail.do` per dokumen — ribuan panggilan, justru yang dihindari.
- Field bersifat aditif; baris lama tanpa `accurate_mirror` berperilaku persis seperti sebelumnya lalu terisi sendiri.

## Belum selesai

- **Penjadwalan pemindai tiap malam** belum dipasang. Perkakasnya siap; tanpa jadwal, janji "basi jadi angka di laporan pagi" belum lunas.
- **Ekspor belum dialihkan ke salinan** — sengaja. Ekspor sekarang menghitung harga dari **faktur sumber**, bukan dari dokumen retur, jadi mengalihkannya berpotensi mengubah angka yang dilihat finance. Harus diukur dulu di data nyata bahwa keduanya sama; mengubah angka finance diam-diam lebih buruk daripada ekspor yang lambat. Sampai itu terjadi, keluhan awal (ekspor lambat) **belum terselesaikan**.
- **Frontend** label "disalin pada" + tombol Segarkan belum dibuat; endpoint sudah siap.

Grounded: `entity.AccurateReturnMirror`/`AccurateReturnLine`, `cerminDariAccurate`/`accurateDariCermin`/`detailDenganCermin`/`BandingkanCerminRetur` (`accurate_return_cermin.go`, `accurate_rts_usecase.go`), `SetAccurateMirror` + `$unset` di `SetGroupResult` (`accurate_daily_return_repo.go`), `cmd/returndriftscan`, `ProbeListSalesReturns`, tes `accurate_return_cermin_test.go` + `accurate_return_cermin_alur_test.go` + `accurate_return_drift_test.go`.

## Dokumen Terkait
- [[ADR - 0016 Retur Grouped per Faktur + Tanggal Retur]] — model grup & guard anti-dobel
- [[Microservices - Integration Service]] — Auto-Sync Retur
- [[API - Integration Service]] — endpoint `refresh`
- [[APP - Web ERP]] — halaman Auto-Sync Retur
