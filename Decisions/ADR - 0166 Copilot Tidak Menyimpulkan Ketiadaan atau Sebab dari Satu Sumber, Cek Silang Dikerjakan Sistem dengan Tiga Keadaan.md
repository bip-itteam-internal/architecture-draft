# ADR - 0166 Copilot Tidak Menyimpulkan Ketiadaan atau Sebab dari Satu Sumber, Cek Silang Dikerjakan Sistem dengan Tiga Keadaan

> **Status**: 🟡 Diusulkan, 2026-10-10. Persetujuan ditulis manusia di baris ini (`🟢 Diterima, <tanggal>, oleh <login/jabatan>`). Bentuk keputusan dirumuskan dari perilaku yang sudah merged di `main` (bip-erp #2906 sampai #2919, erp-frontend #2272, #2273, #2276); ukur ulang sebelum mengandalkan kalimat ini.

## Untuk Manajemen

**Apa yang berubah di layar.** Bila sebuah angka di Copilot nol, turun, atau rendah, Copilot tidak lagi menebak sebabnya dari satu sumber. Contoh: hari tanpa penjualan live, tanggal tanpa laporan produksi, jumlah hari kerja yang berbeda dari periode pembanding, atau toko berlaba rendah. Sistem memeriksa fakta penjelasnya di data departemen lain dan menuliskan salah satu dari tiga keadaan:

- **Ada** (mis. "ada shift tercatat", "libur tercatat", "ada penanggung jawab").
- **Tidak ada** (mis. "tanpa shift tercatat", "tanpa libur tercatat", "tanpa penanggung jawab"): kalimatnya selalu berbunyi "tanpa X **tercatat**", bukan "tidak ada X".
- **Tidak diperiksa**, beserta alasannya (tidak berhak, sumber gagal, melewati batas, kalender belum diisi).

Aturan yang dijaga sistem:

- **Angka tidak pernah dihitung model.** Kelipatan, rata-rata, dan kisaran yang angkanya tidak ada di hasil alat dibuang sebelum sampai ke layar.
- **Laba yang belum final tidak dibaca sebagai kerugian.** Laba periode yang order terakhirnya belum cair ditandai belum final; kesimpulan hanya diambil dari kolom yang tidak menunggu pencairan.
- **Rujukan ke halaman hanya lewat token yang divalidasi sistem**; nama halaman yang dikarang model dibuang.
- Jawaban berdata paling banyak tiga kalimat; penjelasan dan saran ditulis terpisah.

**Siapa yang terdampak.** Semua pengguna Copilot yang bertanya tentang angka. Pemilik data yang dicek silang (kalender libur, shift host, penanggung jawab toko) tidak mengubah apa pun pada alurnya.

**Apa yang TIDAK dijanjikan.**

- **"Tidak ada" tidak pernah berarti pasti tidak ada.** Hanya "tercatat di sistem". Kalender libur yang belum diisi dibedakan dari tahun tanpa libur dengan menyatakan "tidak diperiksa".
- Tidak semua gejala punya cek silang. Pasangan yang butuh perubahan di sumber (mis. produk marketing ke kode stok, retur ke komplain gudang, penyetuju yang sedang cuti) belum dikerjakan, dan Copilot menulis penyebabnya sebagai dugaan yang menyebut data mana yang perlu dicek.
- Batas pada penjaga angka: rata-rata atau kisaran yang kebetulan memakai angka yang ada di hasil alat, dan hitungan tanpa kata pemicu, tidak tertangkap.

**Perkiraan besaran kerja.** Gelombang pertama sudah dikerjakan; setiap pasangan baru kira-kira satu pekerjaan backend kecil.

## Deskripsi

*Menetapkan bahwa pernyataan ketiadaan dan sebab tidak boleh dibuat model dari hasil satu alat. Pemeriksaannya dikerjakan sistem dengan tiga keadaan, angka tidak pernah dihitung model, dan rujukan halaman hanya lewat token yang divalidasi.*

- **Path di repo**: `bip-erp/services/assistant/` (`penjaga_hitungan.go`, `token_tautan.go`, `internal/alat/cek_hari_libur.go`, `mkt_live_laporan.go`, `mkt_labatoko_cek_pj.go`, `keadaan_belum_final.go`, `tanya.go` aturan 16 dan 17), `erp-frontend/src/features/copilot/`
- **Tanggal**: 2026-10-10
- **Terkait**: [[ADR - 0132 Asisten AI Tanya-Jawab Lintas Modul, Lapisan Data Bisnis per Service Bukan Terpusat]] · [[ADR - 0139 Penjelasan Tiap Tabel dan Diagram Laporan Ditulis AI, Angkanya Rujukan ke Fakta Backend]] · [[Microservices - Assistant Service]] · [[REF - Penyajian Laporan Copilot]]

## Context

Dibaca dari `origin/main` bip-erp dan erp-frontend (2026-10-10):

- Model memilih alat dan menulis kalimat. Jawaban benar secara angka dapat tetap menyesatkan karena sebab disimpulkan dari ketiadaan di satu sumber: hari ber-GMV nol dibaca "host tidak masuk" padahal tanggalnya libur; laba negatif dibaca kerugian padahal settlement belum cair.
- Fakta penjelas ada di data departemen lain dan hanya sistem yang bisa memeriksanya dengan hak penanya. Daftar yang isinya bergantung pada pemanggil (rencana jadwal siaran, daftar shift mentah) tidak bisa menjadi dasar menyatakan "tidak ada".
- Model terbukti menulis hitungan (kelipatan, rata-rata, kisaran) yang tidak ada di hasil alat; penjaga rupiah dan persen yang ada belum mencakup bentuk itu.
- Model sempat menulis nama layar dengan kata-katanya sendiri; rujukan yang dikarang tidak punya tujuan.

## Decision

- **K1. Cek silang dikerjakan sistem, bukan model.** Alat memanggil sumber penjelas dan mengirim hasilnya sebagai fakta. Tiga keadaan, tidak pernah dilebur: *ada*, *tidak ada (tercatat)*, *tidak diperiksa* dengan sebab. Tidak diperiksa bukan nol dan bukan "tidak ada".
- **K2. Pasangan yang berjalan** (2026-10-10): live dengan kalender libur dan shift host; produksi dan ringkasan kehadiran dengan kalender libur perusahaan; laba toko dengan status penanggung jawab. Sabtu, Minggu, dan jadwal kerja per orang bukan isi kalender libur dan tidak diperiksa.
- **K3. Kalender yang kosong sama sekali = tidak diperiksa.** Kalender yang belum diisi tidak bisa dibedakan dari tahun tanpa libur.
- **K4. Cek silang hanya menampilkan ada atau tidak ada**, bukan isi data pribadi (penanggung jawab toko: tanpa nama dan tanpa penilaian orangnya).
- **K5. Data belum final dinyatakan, bukan disimpulkan.** Laba yang masih menunggu pencairan ditandai belum final; dengan kolom yang tidak menunggu pencairan, kesimpulan diambil dari kolom itu lalu satu kalimat batas. Penilaian laba dalam penjelasan dan saran dibuang server pada giliran itu.
- **K6. Angka tidak pernah dihitung model.** Penjaga `hitungan_model` membuang kelipatan, rata-rata, dan kisaran yang angkanya tidak ada di hasil alat; berlaku juga untuk penjelasan dan dugaan/saran.
- **K7. Rujukan halaman hanya lewat token `[[buka:<nama_alat>]]`.** Server memvalidasi nama terhadap alat yang ditawarkan pada giliran itu dan membuang yang lain. Peta nama alat ke halaman dan hak klik ada di frontend.
- **K8. Ketiadaan dan sebab di luar hasil alat ditulis sebagai dugaan** yang menyebut data mana yang perlu dicek, atau alat yang bisa memeriksanya dipanggil.
- **K9. Label di layar jujur terhadap keadaan**: "tanpa X tercatat" bukan "tidak ada X"; "tidak diperiksa" bukan "tidak ada".

Pilihan yang ditolak:

- **Membiarkan model mengusulkan sebab dari satu sumber.** Fasih, spesifik, dan salah tanpa tanda.
- **Memakai daftar shift atau rencana jadwal sebagai dasar "tidak ada".** Isinya bergantung pada pemanggil.
- **Menolak jawaban sama sekali bila data belum final.** Kolom yang tidak menunggu pencairan tetap berguna.

## Consequences

- Tiap pasangan cek silang menambah satu panggilan ke sumber lain (paling banyak tujuh hari terbaru untuk cek shift live per panggilan; sisanya tidak diperiksa).
- Penjaga angka memakai pencocokan teks dan punya batas yang diterima (lihat Untuk Manajemen). Ia mengurangi, tidak menghilangkan, risiko hitungan model.
- Cek silang membaca data departemen lain dengan **hak penanya**; sumber yang menolak berarti "tidak diperiksa", bukan "tidak ada".
- Menambah alat baru yang bergejala nol atau turun berarti memutuskan apakah ia punya pasangan cek silang; tanpa itu aturan K8 berlaku.

## Belum diputuskan

Pekerjaan terbuka, belum dikerjakan (hasil penelusuran kandidat 2026-10-10, sebagian belum diverifikasi ke kode):

- Produk marketing ke kode stok: baris marketing tidak membawa kode manufaktur; pemetaan lewat nama tidak dipakai. Butuh rute sumber yang menyatakan pasangan itu.
- Retur ke komplain gudang: sumber retur tidak berbaris per toko, dan kesamaan id toko antar-sumber belum diverifikasi.
- Pengajuan lambat ke penyetuju yang sedang cuti: identitas penyetuju belum dikirim sumber ke alat; cuti orang lain data pribadi.
- Antrean gudang menumpuk: sumber hanya mencacah per status tanpa umur pesanan.
- Payroll naik-turun ke karyawan masuk/keluar: kunci periode tidak sama; run perlu membawa rentang tanggalnya.
- Pelanggaran SLA tiket ke kalender libur: baris pelanggaran tidak bertanggal tenggat.

## Dokumen Terkait

- [[Microservices - Assistant Service]] § Gelombang 2026-10-10
- [[REF - Penyajian Laporan Copilot]]
- [[ADR - 0139 Penjelasan Tiap Tabel dan Diagram Laporan Ditulis AI, Angkanya Rujukan ke Fakta Backend]]
- [[ADR - 0132 Asisten AI Tanya-Jawab Lintas Modul, Lapisan Data Bisnis per Service Bukan Terpusat]]