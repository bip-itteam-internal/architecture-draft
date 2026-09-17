# ANALISA - Selisih Retur

Papan kerja hasil `/analisa-kebutuhan` 2026-09-17. Keputusan dan alasannya di [[ADR - 0104 Selisih Retur Dihitung Terjadwal per Periode dan Bisa Ditandai Beres]]; cara kerjanya di [[Microservices - Integration Service]]. Mockup yang disetujui user: tab kelima Auto Sync Retur dengan kartu per jenis, daftar, panel detail tiga sisi (order · scan gudang · Accurate), dan dialog Tandai beres beralasan.

Urutan di bawah mengikuti dependensi. Tiap item ditulis supaya bisa langsung dilempar ke `/start-task`.

## Tahap 1 — selisih dari data ERP dan WMS

### T1 · Dua izin finance + gerbang akses dua sisi
- **Isi**: tambah `finance.returselisih.view` dan `finance.returselisih.tandai` ke katalog finance, cadangan tier finance selama transisi, dan gerbang frontend (menu Auto Sync Retur muncul bagi pemegang `.view` walau tanpa peran finance/integration; tab dan tombol mengikuti izin).
- **Repo**: bip-erp (shared-library, employee seed paket) · erp-frontend (menu, akses)
- **Bergantung**: —
- **Selesai bila**: admin gudang yang hanya memegang `.view` melihat menu dan tab tanpa tombol Tandai beres; akun finance tanpa paket tetap melihat keduanya.
- `/start-task Tambah izin finance.returselisih.view/.tandai beserta gerbang menu & tab Auto Sync Retur (ADR-0104 §6)`

### T2 · Model temuan dan penyimpanannya
- **Isi**: koleksi temuan per periode (jenis, kunci order/resi, toko, dokumen, sisi order/scan/Accurate, nilai terdampak, umur, status, jejak beres) + catatan tiap perhitungan (kapan, data sampai, diperiksa, gagal dibaca). Aturan tutup otomatis dan buka kembali.
- **Repo**: bip-erp (integration)
- **Bergantung**: —
- **Selesai bila**: perhitungan ulang atas data yang sama tidak menggandakan temuan; temuan yang penyebabnya hilang pindah ke beres; temuan beres yang penyebabnya berubah bentuk terbuka lagi.
- `/start-task Model & repository temuan Selisih Retur per periode dengan status dan jejak beres (ADR-0104 §2, §4)`

### T3 · Detektor kelompok 1 (data ERP)
- **Isi**: belum terbukukan menunggu scan >30 hari · dibukukan tanpa bukti scan · komponen paket belum discan · barang discan berbeda dari yang dibeli. Memakai ulang aturan yang ada (`komponenKurangOrder`, `DibukukanTanpaScan`, penilaian SKU sah order), bukan salinan.
- **Repo**: bip-erp (integration)
- **Bergantung**: T2
- **Selesai bila**: dijalankan atas prod periode Agustus/September, angkanya bisa dijelaskan terhadap pengukuran 2026-09-17 (601 menunggu scan, 191 >30 hari, 33 order komponen belum discan).
- `/start-task Detektor Selisih Retur kelompok 1 dari data integration (ADR-0104 §3)`

### T4 · Endpoint manufacture: data scan retur per periode
- **Isi**: endpoint internal yang menyajikan scan retur per periode secara lengkap (bukan feed layar yang terpotong 2.000 baris): konfirmasi tertunda dan scan tak tertaut order, dengan paginasi dan penanda terpotong.
- **Repo**: bip-erp (manufacture)
- **Bergantung**: —
- **Selesai bila**: satu bulan penuh terbaca tanpa terpotong, dan jumlahnya cocok dengan hitungan langsung di manufacture_db.
- `/start-task Endpoint internal manufacture untuk data scan retur per periode (ADR-0104 §3, Consequences)`

### T5 · Detektor kelompok 2 (sisi gudang)
- **Isi**: sudah discan tapi tidak sampai ke pembukuan · scan tak tertaut order, dari T4. Gagal baca dicatat sebagai kelengkapan, bukan dianggap bersih.
- **Repo**: bip-erp (integration)
- **Bergantung**: T2, T4
- **Selesai bila**: manufacture dimatikan sementara di dev → perhitungan tercatat tidak lengkap, bukan nol temuan.
- `/start-task Detektor Selisih Retur kelompok 2 dari endpoint manufacture (ADR-0104 §3, §5)`

### T6 · Proses terjadwal malam
- **Isi**: menjalankan T3 + T5 per periode berjalan dan periode sebelumnya, disaklar lewat kv seperti job lain, menyimpan catatan kelengkapan.
- **Repo**: bip-erp (integration)
- **Bergantung**: T3, T5
- **Selesai bila**: job terlihat di daftar job, bisa dimatikan, dan dua run berturut-turut atas data tak berubah menghasilkan himpunan temuan yang sama.
- `/start-task Job malam Selisih Retur beserta saklar dan catatan kelengkapan (ADR-0104 §2, §5)`

### T7 · API baca dan Tandai beres
- **Isi**: ringkasan per jenis/toko, daftar berpaginasi, detail tiga sisi, Tandai beres (izin `.tandai`, wajib alasan), unduh Excel di jalur `/export`. Semua berizin `.view`.
- **Repo**: bip-erp (integration)
- **Bergantung**: T1, T6
- **Selesai bila**: dipanggil **lewat gateway** dengan tiga token (finance, admin gudang ber-`.view`, tanpa izin) → 200 / 200 tanpa aksi / 403; tanda beres tanpa alasan ditolak.
- `/start-task API Selisih Retur: ringkasan, daftar, detail, tandai beres, unduh (ADR-0104 §6, §7)`

### T8 · Tab Selisih Retur di frontend
- **Isi**: tab kelima Auto Sync Retur mengikuti mockup: garis kelengkapan, filter periode/toko/status, kartu per jenis sebagai saringan, daftar, panel detail tiga sisi dengan langkah berikutnya, dialog Tandai beres. Aksi mengikuti izin. Teks lewat i18n id+en. Struktur tabel HRIS.
- **Repo**: erp-frontend
- **Bergantung**: T7
- **Selesai bila**: satu perjalanan utuh per persona di browser — finance menandai beres satu temuan, admin gudang membuka WMS dari temuan komponen belum discan, Direktur hanya membaca.
- `/start-task Tab Selisih Retur di Auto Sync Retur sesuai mockup (ADR-0104 §1, §6)`

### T9 · Verifikasi prod Tahap 1
- **Isi**: jalankan job sekali di prod (manusia), bandingkan hasil terhadap pengukuran, pasang paket ke posisi finance, gudang, Direktur lewat /it/hak-akses, sampaikan bahwa perubahan paket berlaku setelah login ulang.
- **Bergantung**: T8
- `/start-task Verifikasi prod Tahap 1 Selisih Retur dan pemasangan paket izin`

## Tahap 2 — selisih catatan ERP vs isi Accurate

### T10 · Salinan dokumen Accurate terjadwal
- **Isi**: menyegarkan salinan dokumen retur per periode dengan batas kecepatan, melaporkan yang gagal dibaca, dan tidak berjalan bersamaan dengan perkakas yang menulis ke Accurate. Menuntaskan bagian pemindai [[ADR - 0066 Salinan Dokumen Retur Accurate + Pemindai Drift]] yang tak pernah dibuat.
- **Repo**: bip-erp (integration)
- **Bergantung**: T6
- `/start-task Penyegaran salinan dokumen retur Accurate terjadwal per periode (ADR-0104 §3 Tahap 2)`

### T11 · Detektor kelompok 3
- **Isi**: catatan ERP (`booked_total`) vs total salinan; 17 dokumen yang dibetulkan manual finance 2026-09-16/17 dipakai sebagai uji nyata (harus muncul, lalu bisa ditandai beres).
- **Repo**: bip-erp (integration) · erp-frontend (kartu kelompok 3 dibuka)
- **Bergantung**: T10, T8
- `/start-task Detektor Selisih Retur kelompok 3: catatan ERP vs isi Accurate (ADR-0104 §3, §4)`

## Sisa terbuka (belum dijadwalkan)
- Perbandingan **jumlah barang** yang lengkap: WMS menjumlahkan transaksi per order, pembukuan mengganti per order+SKU.
- Transaksi WMS `catatanSaja` yang menambah stok tanpa masuk pembukuan.
- Ubah/hapus transaksi WMS setelah dokumen retur terkirim.
- Keputusan label untuk kasus salah scan barang satuan di Laporan Retur (saat ini "Sebagian discan").
