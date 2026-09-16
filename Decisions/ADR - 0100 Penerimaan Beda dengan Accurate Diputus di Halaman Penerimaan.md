# ADR - 0100 Penerimaan Beda dengan Accurate Diputus di Halaman Penerimaan

## Deskripsi

*Keputusan atas dokumen **Penerimaan** (Bukti Terima Kas) yang isinya di Accurate berbeda dari hitungan ERP: yang selaras ditutup mesin tanpa manusia, yang benar-benar berbeda diputuskan finance di halaman Penerimaan, dan adopsi dihitung terhadap hitungan ERP SEKARANG.*

- **Status**: ⚠️ Implemented (ada catatan) — kode selesai & ber-test di dua branch (`bip-erp` `feat/adopsi-penerimaan-finance`, `erp-frontend` `feat/penerimaan-beda-accurate`); **PR belum dibuka, belum deploy**.
- **Tanggal**: 2026-09-16
- **Terkait**: [[Microservices - Integration Service]] · [[APP - Web ERP]] · [[IT - Background Jobs & Schedulers]]

## Context

Mesin menahan penulisan penerimaan bila isi dokumen di Accurate berbeda dari yang terakhir ia kirim (`hold_reason=EXTERNAL_EDIT` + draf di Kotak Adopsi / "Penyesuaian Manual"). Tiga fakta terukur membuat mekanisme itu tak pernah menutup lingkarannya:

1. **Nol keputusan finance sepanjang hidup fitur.** Riwayat draf penerimaan di prod (2026-09-15): 180 ditolak "sistem (pembersihan artefak)", 29 diadopsi "sistem (pemulihan incpulih)", 176 tanpa `resolved_by`, **2 oleh staf IT**, nol oleh finance. Sebabnya bukan kemauan: chip `EXTERNAL_EDIT` tak dikenal frontend (baris tampak normal di daftar), tak ada tautan dari penerimaan ke drafnya, dan ringkasan draf penerimaan berbunyi *"Tidak ada beda terbaca"* karena penghitung diff hanya mengenal dimensi barang milik faktur.

2. **Sebagian besar penahanan tak punya uang yang berubah.** Pembanding penahanan adalah **kiriman terakhir**, bukan hitungan sekarang. Begitu rumus berubah ([[ADR - 0024 Retur Gerbang Payout + Tanggal per-Solution]] cabang retur penuh se-statement, PR #1875) sementara finance lebih dulu mengoreksi hal yang sama secara manual, keduanya bertemu di angka yang sama tetapi baseline-nya usang. Dari **30 dokumen tertahan**, perbandingan kanonik lengkap (cheque + alokasi per faktur + komponen GL) menemukan **18 sudah sama persis** dengan hitungan ERP terbaru.

3. **Adopsi bisa memotong dua kali.** Adopsi menerjemahkan selisih *kiriman lama → Accurate* menjadi koreksi permanen yang ikut di **setiap** pembangunan ulang, sementara pembangunan ulang memakai rumus terkini. Pada `INC/2026/08/15/013-BH`, faktur `INV/2026/08/03/027-BH`: kiriman lama 584.000, Accurate 485.000, rumus baru 485.000 — mengadopsi versi lama menghasilkan **386.000**.

## Decision

1. **Selaras = tak ada keputusan yang perlu diambil.** Di jalur kirim, sebelum gerbang deteksi, isi Accurate dibandingkan dengan payload yang akan dikirim **sekarang**. Sama → dokumen tidak ditahan, kiriman tetap jalan, dan draf BARU dokumen itu ditutup berstatus **BASI** dengan `resolved_by="sistem"`. Gagal menutup draf dicatat log dan **tidak** menggagalkan kiriman — akibat terburuknya draf tetap terlihat, bukan uang yang salah.

2. **Yang berbeda diputuskan di tempat masalahnya terlihat.** Keputusan pindah ke modal detail **Penerimaan**: chip netral "Beda dengan Accurate", tabel tiga kolom rupiah (*terakhir dikirim ERP · isi Accurate · hitungan ERP sekarang*), dan dua tombol yang menyebut akibatnya sebelum ditekan. Kotak Adopsi tetap ada sebagai daftar lintas dokumen dan menautkan tiap draf penerimaan ke halaman itu.

3. **Adopsi dihitung terhadap hitungan ERP sekarang**, bukan kiriman lama. Bila hitungan sekarang tak bisa dibuat, adopsi **ditolak** beserta alasannya; bila Accurate sudah sama dengannya, tak ada koreksi yang dibuat dan draf ditutup BASI.

4. **Label deteksi dijaga netral.** "Beda dengan Accurate", bukan "diedit manual" — penyebab selisih tak selalu manusia, dan label menuduh sudah pernah menggiring operator menyalahkan finance atas selisih yang lahir dari sistem sendiri.

## Consequences

- **Beban keputusan turun tajam tanpa menyentuh uang**: 18 dari 30 dokumen tertahan selesai sendiri pada siklus `receipt-sync` berikutnya; nilai di Accurate tidak berubah sedikit pun karena yang dikirim identik dengan yang sudah ada.
- **Potongan ganda tertutup di jalurnya**, bukan lewat disiplin operator. Dikunci test yang meniru kasus prod 027-BH beserta kontrol negatifnya.
- **Hitungan ERP sekarang ada ongkosnya**: dry-run jalur kirim terukur 6–11 detik di prod, jadi hanya dijalankan saat satu draf dibuka (bukan di daftar), dan draf dokumen yang sudah dihapus dilewati. Batas gateway 30 detik tetap jadi pagar yang diukur, bukan diasumsikan.
- **Lazada belum punya kolom ketiga**: dry-run Lazada belum ada, sehingga tombol "Pertahankan angka Accurate" nonaktif untuk channel itu dengan alasan tertulis. Nol draf Lazada terbuka saat keputusan ini diambil.
- ⛔ **Pemindahan pelunasan ke akun GL belum punya tuas koreksi.** Prod `INC/2026/09/08/028-BH`: pelunasan `INV/2026/08/10/030-BH` (Rp89.000) dipindahkan ke akun **8001 Pendapatan Lain-lain** tanpa mengubah uang diterima; penerjemah koreksi hanya mengenal *geser antar-faktur* dan *tambah uang*, jadi adopsinya ditolak dengan pesan bernominal. Menambah tuasnya menuntut keputusan finance lebih dulu: uang yang lepas dari faktur itu dicatat ke pos apa. **Task terpisah.**
- **Yang tetap terbuka**: endpoint Kotak Adopsi (`/accurate/external-edit-drafts*`) sampai kini **tak tercatat** di [[API - Integration Service]]; field respons baru `sistem_sekarang` karena itu juga belum punya tempat di sana. Dicatat sebagai utang dokumentasi, bukan diam-diam dianggap ada.
- **Komentar kode yang menyesatkan ikut dicabut**: `receipt_sync.go` dan `RunDaily` masih menyatakan jalur ini "DIMATIKAN SEMENTARA" oleh konstanta yang sudah tidak ada di repo, padahal kv prod `receipt-scheduled-sync` bernilai `on` sejak 2026-08-06 dan job-nya menulis 5× sehari.

## Dokumen Terkait

- [[Microservices - Integration Service]] — gerbang selaras, `sistem_sekarang`, adopsi terhadap hitungan sekarang.
- [[APP - Web ERP]] — chip, seksi keputusan, tautan dari Penyesuaian Manual.
- [[IT - Background Jobs & Schedulers]] — `receipt-sync` (5× sehari) sebagai siklus yang menutup draf selaras.
- [[ADR - 0024 Retur Gerbang Payout + Tanggal per-Solution]] — rumus retur yang perubahannya melahirkan selisih baseline ini.
