# ANALISA - Kompensasi Logistik TikTok Pasca-Retur

Papan kerja hasil `/analisa-kebutuhan` 2026-09-28, dari dokumen finance "Revisi Sistem Income"
(`z-file-hasil/finance/revisi sistem income.docx`, Kasus 2). Keputusannya ada di
[[ADR - 0133 Kompensasi Logistik TikTok Pasca-Retur Dibedakan per Kondisi Barang, Otomasi
Ditunda]] — berkas ini hanya papan kerja, bukan sumber keputusan.

Opsi yang dipilih: **C — SOP manual dulu, otomasi ditunda** (populasi historis kecil: 16 order per
2026-09-28). Task di bawah mencerminkan itu — bukan rencana bangun kode.

## Task sekarang (Opsi C)

1. **Sebarkan SOP ke tim finance/accounting** yang mengoreksi retur TikTok manual di Accurate.
   Isinya tabel di [[ADR - 0133 Kompensasi Logistik TikTok Pasca-Retur Dibedakan per Kondisi
   Barang, Otomasi Ditunda]] §Decision 1. Bukan task kode — koordinasi/komunikasi ke tim.
2. **Konfirmasi ke finance**: pertanyaan terbuka soal dokumen retur campuran kondisi (satu dokumen
   Accurate berisi beberapa order/SKU, sebagian reject sebagian reuse/rework — seluruh dokumen
   dihapus atau hanya baris yang reject?). Lihat ADR §Context "Pertanyaan terbuka ke finance".
   Jawabannya PENTING sebelum Opsi A pernah dipertimbangkan lagi — jangan ditebak.
3. **Ukur ulang populasi secara berkala** (tiap kali ADR-0133 dirujuk kembali, atau minimal per
   kuartal) — query di ADR §Context ("Populasi terukur"). Kalau naik signifikan dari 16 order,
   itu salah satu pemicu meninjau ulang Opsi A (ADR-0133 §Decision 3).

## Task TERTUNDA (hanya bila Opsi A dipicu — lihat ADR §Decision 3)

Dicatat di sini SEBAGAI REFERENSI, bukan untuk langsung dikerjakan. Bila salah satu pemicu di
ADR-0133 §Decision 3 terpenuhi, jalankan langsung `/start-task` per item (lewati
`/analisa-kebutuhan` ulang — keputusan arsitekturnya sudah ada):

1. `/start-task` bip-erp `services/integration/internal/usecase/kompensasi_tiktok.go` — lepas
   `kompensasiJadiPendapatanLain`/`pisahkanKompensasiPayoutPositif` dari syarat "TANPA retur" untuk
   sub-populasi (ada retur SENT **dan** kompensasi `LOGISTICS_REIMBURSEMENT`).
2. `/start-task` bip-erp `services/integration/internal/usecase/accurate_rts_usecase.go` — panggil
   `DeleteSalesReturn` (sudah ada, pola sudah teruji) untuk kasus kondisi barang **reject** dalam
   populasi ini.
3. `/start-task` bip-erp `services/manufacture/` — mekanisme koreksi stok WMS mengikuti penghapusan
   dokumen retur (baru; belum ada endpoint/fungsi serupa sekarang — verifikasi dengan `git grep`
   sebelum mengasumsikan tak ada apa pun yang bisa dipakai ulang).
4. Jawab dulu pertanyaan dokumen campuran (task #2 di atas) SEBELUM menulis kode #1-3 — menentukan
   apakah unit kerja "hapus/pisah" itu per-DOKUMEN atau per-ORDER/baris dalam grup.
5. Test regresi wajib: populasi ADR-0119 yang TIDAK berubah (payout>0 + ada retur, kompensasi
   BUKAN logistik) harus tetap melunasi faktur seperti sekarang — kontrol negatif sama pentingnya
   dengan kasus positif (pola yang sama seperti [[ADR - 0119 Kompensasi TikTok Dipisah Menurut
   Sudah atau Belum Ada Uang Masuk]] saat implementasi Kasus 1).

## Terkait

- [[ADR - 0133 Kompensasi Logistik TikTok Pasca-Retur Dibedakan per Kondisi Barang, Otomasi Ditunda]]
- [[Finance - Proses Retur dan Piutang Marketplace]]
