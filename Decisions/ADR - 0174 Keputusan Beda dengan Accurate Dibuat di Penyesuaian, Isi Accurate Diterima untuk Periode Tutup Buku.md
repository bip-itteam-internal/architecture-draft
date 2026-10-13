> **Status**: 🟢 **Diterima, 2026-10-13, oleh bagusizzanm (Tech Development)** atas makna perilaku "Terima isi Accurate" dan arah satu tempat keputusan. **Finance menjawab "setuju" atas seluruh rekomendasi butir 1 sampai 10** pada pesan keputusan yang dikirim lewat grup (2026-10-13). Dua butir **tidak terjawab**: butir 0 (finance lupa apakah ada tombol konfirmasi) dan butir 3b (`INC/2026/09/30/046-KY+GB`, pesan tidak memberi rekomendasi sehingga "sesuai rekomendasi" tidak menjawabnya). **Belum ada kode.**

## Untuk Manajemen

**Apa yang diputuskan.**
1. **Menu Penyesuaian jadi satu-satunya tempat memutuskan** draf "Beda dengan Accurate" (receipt dan faktur). Halaman Penerimaan hanya menampilkan chip dan satu tautan ke Penyesuaian. Finance tidak lagi memantau di satu menu dan memutuskan di menu lain.
2. **Aksi baru "Terima isi Accurate"** untuk periode yang finance nyatakan sudah tutup buku (Agustus dan September 2026). Artinya: isi Accurate dianggap benar, ERP **berhenti menulis ke dokumen itu**, tidak ada yang dikirim ke Accurate, dan alasan finance tercatat di tiap dokumen. Bisa dijalankan sekaligus untuk banyak draf.
3. **Koreksi ke depan lewat menu Koreksi Manual ERP, bukan mengetik langsung di Accurate, mulai 1 November 2026.**

**Siapa yang terdampak.** Finance (cara memutuskan draf dan cara mengoreksi), tim IT (mengubah layar dan satu penahan baru di backend).

**Kenapa perlu ditulis.** Per 2026-10-10 ada 100 draf menunggu (73 receipt, 27 faktur) dan hampir semuanya tidak punya jalan keluar yang aman. Adopsi membangun ulang dan **mengirim ulang** dokumen ke Accurate, padahal Accurate periode Agustus dan September sudah dipastikan benar finance lewat rekon kas toko. Tolak menimpa Accurate. Finance mencoba Adopsi, tidak melihat hasil apa pun, dan draf tetap ada.

**Apa yang tidak dijanjikan.**
- **Angka di ERP untuk dokumen yang diterima tidak disalin dari Accurate.** Hanya ditandai. ERP dan Accurate bisa berbeda untuk dokumen itu, dan Accurate yang benar.
- **Tidak berlaku untuk periode berjalan.** Di sana Adopsi (koreksi permanen) tetap jalurnya.
- **Juli (7 receipt) ditunda**, dan `INC/2026/09/30/046-KY+GB` belum diputuskan.

**Perkiraan besaran kerja.** Sedang (estimasi, belum diukur): backend satu penahan baru dan satu endpoint massal; frontend satu dialog Detail yang diperluas, satu aksi massal, dan penunjuk di halaman Penerimaan.

## Deskripsi

*Penyederhanaan keputusan "Beda dengan Accurate": satu tempat (Penyesuaian), satu aksi baru untuk periode tutup buku yang tidak menulis ke Accurate, dan aturan koreksi ke depan. Menggantikan Decision 2 [[ADR - 0100 Penerimaan Beda dengan Accurate Diputus di Halaman Penerimaan]].*

- **Status**: lihat blockquote di baris pertama dokumen ini
- **Path di repo**: `bip-erp/services/integration/internal/usecase/external_edit_draft_usecase.go` (`resolve`) · `external_edit_draft_receipt.go` (`adoptReceipt`) · `internal/domain/entity/accurate_daily_invoice.go` (penahan `hold_reason`) · `erp-frontend/src/features/integration/accurate/adoption/components/adoption-draft-detail-dialog.tsx` · `.../receipts/components/receipt-external-edit-section.tsx`
- **Tanggal**: 2026-10-13
- **Pelacakan**: bip-erp#2199 (audit auto-sync penerimaan, dulu BHA-297)
- **Desain visual**: kanvas Design "Desain Penyesuaian Satu Tempat" (5 artboard, privat milik pemilik produk; bukan sumber kebenaran, dok ini yang mengikat)

## Context

1. **Dua layar untuk satu keputusan.** ADR 0100 (2026-09-16) memindahkan keputusan ke halaman Penerimaan, sementara Penyesuaian tetap daftar lintas dokumen. Bagian keputusan di Penerimaan hanya tampil bila dokumen berstatus ditahan (`EXTERNAL_EDIT`): 30 dari 73 draf receipt pada pengukuran 2026-10-10. Untuk 43 sisanya (mode deteksi `log`) hanya Penyesuaian yang bisa memutuskan, dan di sana tidak ada kolom hitungan ERP sekarang. Faktur tidak punya halaman Penerimaan sama sekali.
2. **Adopsi receipt menulis ke Accurate.** `adoptReceipt` membandingkan **hitungan ERP sekarang** dengan isi Accurate, menyimpan koreksi permanen (`receipt_manual_adjustments`), menutup draf, lalu membangun ulang dan mengirim receipt (`external_edit_draft_receipt.go`). Bila isi Accurate sudah sama dengan hitungan sekarang, draf ditutup BASI tanpa koreksi. Bila selisihnya tidak bisa diterjemahkan, adopsi ditolak dengan alasan. Tolak menimpa Accurate pada sinkronisasi berikutnya.
3. **Hasil keputusan tidak terlihat jelas.** Dialog Detail punya dua langkah (form lalu "Konfirmasi adopsi"), dan galat tampil sebagai teks merah kecil. Finance mencoba Adopsi, tidak melihat hasil, dan lupa apakah ada tombol konfirmasi. Dari data prod tidak ada draf yang diputuskan dan tidak ada koreksi hasil adopsi sejak 2026-10-10.
4. **Finance menyatakan Accurate benar untuk Agustus dan September** (rekon kas toko sudah sesuai, 2026-10-12). Dari 73 draf receipt per 2026-10-10: 37 Agustus (diubah), 26 September (diubah), 3 September (dihapus di Accurate), 7 Juli. Dari 27 draf faktur: 4 Agustus, 22 September, 1 Oktober. Semuanya berjenis diubah.
5. **Padanan di kode sudah ada.** Faktur: Adopsi hanya memasang penanda `ADOPTED_MANUAL` dan mesin berhenti menimpa (berlaku sampai komposisi qty snapshot berubah, bukan selamanya). Receipt: penahan `BOOKED_EXTERNALLY` menghentikan jalur otomatis, dan hanya Retry manual yang menembusnya. Receipt berstatus `EXTERNAL_EDIT` (mode `hold`) sudah tertahan sampai ada keputusan.
6. **Sebab selisih tak selalu manusia.** ADR 0100 mencatat banyak draf lahir dari sistem sendiri (baseline usang, rumus berubah). Label deteksi tetap netral, "Beda dengan Accurate".

## Decision

1. **Penyesuaian adalah satu-satunya tempat keputusan** untuk draf receipt dan faktur, ditahan maupun tidak. Penerimaan menampilkan chip "Beda dengan Accurate" dan tautan "Buka di Penyesuaian", **tanpa tombol keputusan**. Detail draf di Penyesuaian wajib memuat:
   - ringkasan tiga angka (uang diterima, faktur berbeda, akun beban berbeda);
   - perbandingan tiga kolom (terakhir dikirim, isi Accurate, hitungan ERP sekarang) yang menampilkan baris berbeda saja, dengan tombol untuk membuka semuanya;
   - total cheque sebelum dan sesudah;
   - dua pilihan dengan **akibat tertulis di bawah tiap tombol**, dan alasan wajib;
   - langkah konfirmasi yang menyatakan "keputusan belum tersimpan" sampai ditekan;
   - keadaan **sedang diproses** (terlihat, bisa sampai 30 detik), **ditolak** (banner merah di puncak dialog berisi alasan dari sistem dan jalan keluar), dan **berhasil** (hasil tertulis).
2. **"Terima isi Accurate"** berarti:
   - Isi Accurate diakui sebagai yang benar; **tidak ada yang dikirim atau ditulis ke Accurate**.
   - Dokumen **ditandai** sehingga semua jalur otomatis berhenti menulisnya (pengiriman terjadwal, penyisir, serap, Retry otomatis).
   - Draf ditutup berstatus diadopsi dengan catatan alasan, dan diff tetap tersimpan sebagai arsip.
   - **ERP tidak menyalin angka Accurate** ke catatannya (hanya menandai). Penyamaan `cheque_amount` ERP dengan Accurate (B3 di audit) tetap terbuka.
   - Receipt memakai penahan baru; faktur memakai `ADOPTED_MANUAL` yang sudah ada. Nama penahan receipt ditetapkan di brief.
   - Aksi bisa dijalankan **massal** dengan satu alasan yang tercatat di tiap dokumen, setelah dialog konfirmasi yang menyebut jumlah dan periode.
   - Aksi ini **hanya untuk periode yang finance nyatakan tutup buku**. Sistem tidak mengecek status tutup buku itu sendiri; pembatasan dilakukan lewat pemilihan dan teks konfirmasi.
3. **Lingkup pertama:** 63 receipt Agustus dan September yang diubah di Accurate, dan 26 faktur Agustus dan September. Finance setuju (butir 1 dan 2). Satu faktur Oktober diputuskan satu per satu.
4. **Receipt yang dihapus di Accurate:** `INC/2026/09/07/037-BH` dan `INC/2026/09/09/041-BH` (TikTok Narathiwat.Beauty, bernilai Rp0 di ERP): penghapusan disengaja dan tidak dibuat ulang (butir 3a, jawaban finance). `INC/2026/09/30/046-KY+GB` (Rp229.477): **belum diputuskan**.
5. **Koreksi ke depan lewat Koreksi Manual ERP mulai 1 November 2026** (butir 4). Sampai itu, mengetik langsung di Accurate masih boleh, dan hasilnya akan muncul sebagai draf.
6. **Juli (7 receipt) ditunda**, diperlakukan sama hanya bila finance mengonfirmasi tutup buku.

## Belum Diputuskan (TBD)

- **`INC/2026/09/30/046-KY+GB`**: dihapus di Accurate, bernilai Rp229.477, berstatus `FAILED` di ERP. Disengaja atau perlu dibuat ulang (Retry)? Finance belum menjawab.
- **Cara melepas beku** dan apakah Retry manual boleh menembus penahan baru. Usulan: Retry manual menolak selama beku, melepas hanya lewat aksi eksplisit beralasan dan berjejak.
- **Salin angka Accurate ke catatan ERP?** Diputuskan hanya menandai untuk lingkup pertama; menyalin menuntut keputusan B3 tersendiri.
- **Tampilan layar rekonsiliasi untuk dokumen beku.** Lapis "Accurate" di layar itu adalah `cheque_amount` Mongo berstatus SENT, bukan isi Accurate, sehingga dokumen beku bisa tetap menampilkan angka ERP lama. Belum diperiksa per layar.
- **Batas aksi massal** (jumlah per permintaan) terhadap batas gateway 30 detik.
- **Juli** dan **faktur Oktober** seperti di atas.

## Consequences

- ✅ Satu menu, satu keputusan: beban memilah dua layar hilang, dan 43 draf receipt tak-ditahan akhirnya bisa dibaca terhadap hitungan ERP sekarang.
- ✅ Nol penulisan ke Accurate periode yang sudah direkon.
- ⚠️ ERP dan Accurate **sengaja berbeda** untuk dokumen yang diterima. Laporan yang membaca angka ERP bisa menampilkan angka lama.
- ⚠️ Beku bukan solusi akar. Draf baru tetap lahir selama selisih antara hitungan ERP dan Accurate muncul; pencegahannya ada di aturan nomor 5 (koreksi lewat ERP) dan di pengukuran sebab selisih (belum dikerjakan).
- ⚠️ Perilaku baru di jalur uang dan penahan. Butuh test yang mengunci bahwa dokumen beku tidak pernah ditulis jalur mana pun (kontrol negatif), dan satu uji melalui gateway sebelum diklaim selesai.

## Dokumen Terkait

- [[ADR - 0100 Penerimaan Beda dengan Accurate Diputus di Halaman Penerimaan]] (Decision 2 digantikan oleh dok ini; Decision 1, 3, 4 tetap)
- [[ADR - 0152 FO yang Dilaporkan Sesudah Uang Cair Mengecilkan atau Menghapus INC, FO Tidak Masuk Penjualan]] · [[ADR - 0162 Receipt Lazada Mengikuti Uang yang Benar-benar Cair, Selisih terhadap Hitungan Order Ditandai]]
- [[Microservices - Integration Service]] · [[APP - Web ERP]]
