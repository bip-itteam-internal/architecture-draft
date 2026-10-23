# ADR - 0159 Serapan Anggaran Dibaca dari Pengajuan sebagai Bagian dari Terpakai, Rute Tulis Anggaran Digerbang Izin Sendiri

> **Status**: 🟡 **Diusulkan** (belum ada baris `🟢 Diterima, <tanggal>, oleh <login/jabatan>`; aturan persetujuan ADR di [[ADR - 0151 Issue Siap Dikerjakan Agent Bila Keputusannya Bisa Ditunjuk, Ditandai Manusia]]). Asal keputusan, menurut badan issue bip-erp#2779: **K1 sampai K8** "disetujui pemilik produk di sesi desain 2026-10-07/08" (nama penyetuju tidak tertulis di issue); **K9** (paket izin) diputuskan **PIC Azzerith 2026-10-08** dan **menunggu konfirmasi Pemutus wirkancil** (diminta dikoreksi sebelum PR-nya di-merge, bip-erp#2811 sudah ter-merge tanpa jawaban tertulis di issue per 2026-10-08). ✅ **Kodenya sudah merged ke `main` 2026-10-08** (bip-erp#2795, bip-erp#2811; erp-frontend#2185, #2186, #2188, #2193). **Deploy prod: TBD** (urutan BE dulu, lihat [[Finance - Serapan Anggaran dan Cost Control]] §Urutan Deploy). Belum ada layar yang dicek di browser dan belum ada endpoint yang dicoba lewat gateway (catatan penutup bip-erp#2779, 2026-10-08).

## Untuk Manajemen

**Apa yang berubah di layar.** Halaman Anggaran & Cost Control kini dibuka di tab **Serapan**: per pos biaya terlihat Anggaran, Terpakai, dan Sisa, lengkap dengan peringatan untuk pos yang sudah lewat anggaran. Dana yang terserap lewat Pengajuan Barang/Dana tampil sebagai keterangan "dari pengajuan" di dalam angka Terpakai, dan pengajuan yang sudah lolos Cost Control tetapi belum dicatat Accounting tampil di antrean tersendiri per departemen pengaju. Isian anggaran bulanan keluar dari dasar tab Master menjadi tab sendiri, dan ada tombol unduh template Excel. Accounting melihat sisa pos di form pencatatan, dan Cost Control melihat kartu Anggaran saat memeriksa pengajuan.

**Siapa yang terdampak.** Cost Control (unggah dan koreksi anggaran, memantau serapan), Accounting (mencatat pengajuan), Supervisor Finance, dan pengaju pengajuan secara tidak langsung. Staf finance biasa tetap bisa membaca laporan tetapi tidak lagi bisa mengubah anggaran.

**Apa yang TIDAK dijanjikan.** Lewat anggaran hanya **memperingatkan**, tidak memblokir pengajuan dan tidak meminta alasan. Tidak ada anggaran per proyek, tidak ada isian rencana mingguan, tidak ada peringatan otomatis, dan Opex Marketing tidak disatukan ke Serapan. Pengajuan yang belum dicatat **tidak dipetakan ke pos**, jadi angka Terpakai baru naik setelah dicatat dan realisasinya tersinkron dari Accurate. Perubahan hanya sah setelah deploy prod, yang belum terjadi.

**Perkiraan besaran kerja.** Sudah dikerjakan: dua pekerjaan backend dan empat pekerjaan layar. Yang tersisa adalah keputusan terbuka di bip-erp#2814 dan pengecekan di layar nyata.

## Deskripsi

*Layar Anggaran & Cost Control sebelumnya tidak menunjukkan dana yang terserap lewat pengajuan, dan isian anggaran terkubur di dasar tab Master di bawah tiga panel laporan. Keputusan ini menetapkan bagaimana serapan dibaca (Terpakai tetap realisasi Accurate, dana dari pengajuan hanya bagian darinya), bagaimana pengajuan yang belum dicatat ditampilkan, dan siapa yang boleh menulis anggaran.*

- **Path di repo**: `bip-erp/services/procurement/pengajuan_barang_serapan.go` · `bip-erp/services/integration/internal/interface/http/finance_baca_gate.go` + `anggaran_handler.go` + `usecase/anggaran_template.go` · `bip-erp/shared-library/common/catalog_finance.go` · `erp-frontend/src/features/finance/anggaran/` · `erp-frontend/src/features/pengajuan-barang/`
- **Tanggal**: 2026-10-08
- **Terkait**: [[Finance - Serapan Anggaran dan Cost Control]] (aturan membaca angka dan alur) · [[Finance - Rancangan Finance Service]] · [[CORE - RBAC dan Permission Set]] · [[ADR - 0130 Dashboard FAT Diringkas, Isi Posisi Pindah ke Modul Kerjanya]] (asal halaman bertab)

## Context

- Diukur 2026-10-07 (baca-saja, menurut badan bip-erp#2779): 94 pengajuan sudah lolos Cost Control tetapi belum dicatat Accounting; 2 pos sudah melewati anggaran Oktober; koleksi `cost_rekomendasi` berisi 0 dokumen sejak rilis 14 Agustus. Angka rupiah sengaja tidak disalin ke vault publik.
- Master anggaran OPEX sudah hidup di integration-service, per **akun Accurate × departemen Accurate × bulan** ([[Finance - Rancangan Finance Service]], [[REF - Kepemilikan Data]]). Realisasi dibaca dari salinan lokal yang disegarkan dari Accurate.
- Pengajuan Barang/Dana lima tipe ada di procurement-service ([[Microservices - Procurement Service]]); akun, departemen, dan project sebuah pengajuan ditetapkan Accounting di form pencatatan, bukan Cost Control.
- Rute tulis anggaran dijaga izin baca (`finance.accounting.view`) sampai keputusan ini; [[Finance - Rancangan Finance Service]] sudah mencatat bahwa modul finance belum punya izin tulis dan mengusulkan `finance.anggaran.kelola`.

## Decision

Sembilan keputusan, bernomor K1 sampai K9 seperti di badan bip-erp#2779 supaya rujukan di issue dan PR tetap terbaca.

| # | Keputusan |
|---|---|
| K1 | Dimensi anggaran **tetap** akun × departemen Accurate × bulan. Tidak ada dimensi proyek, departemen HRIS, atau peta departemen. |
| K2 | "Per project" untuk marketing = beban per orang yang **sudah ada** (`beban_marketing_orang`, tab Opex Marketing). Tidak dibangun ulang. |
| K3 | COA, departemen, dan project sebuah pengajuan ditetapkan **Accounting** di form pencatatan (sudah berjalan). Cost Control tidak memilih pos. |
| K4 | **Terpakai = realisasi jurnal Accurate. Sisa = Anggaran − Terpakai. "Dari pengajuan" adalah BAGIAN dari Terpakai, tidak dijumlahkan.** |
| K5 | Pengajuan lolos Cost Control yang belum dicatat = satu antrean "Menunggu dicatat Accounting" per **departemen pengaju**, **tidak dipetakan ke pos**. |
| K6 | Lewat anggaran tidak memblokir dan tidak meminta alasan. Tidak ada ambang selain di atas 100% (ambang "mendekati" menunggu erp-frontend#1862). |
| K7 | Forecast kas mingguan dan KPI Cost Control #4 **tidak berubah** (6 akun, otomatis, tanpa isian). Hanya ditambah tampilan rincian per akun. |
| K8 | Tab `/finance/anggaran`: Serapan (bawaan) · Opex Marketing · Rekomendasi · Anggaran Bulanan · Forecast Mingguan. |
| K9 | Rute tulis anggaran digerbang izin baru `finance.anggaran.kelola`, dipasang meniru `finance.pajak.kelola`: paket bawaan baru `finance_anggaran` (`finance.accounting.view` + `finance.anggaran.kelola`, pasangan wajib), masuk tier supervisor dan admin, **tidak** masuk tier staff. *(Diputuskan PIC, menunggu Pemutus.)* |

Di luar cakupan: anggaran per proyek, isian rencana mingguan, perubahan cakupan KPI #4, alert otomatis, penyatuan Opex Marketing ke Serapan.

Cara baca tiap kolom (turunan K4 dan K5) tinggal di **satu tempat**: [[Finance - Serapan Anggaran dan Cost Control]] §Aturan Membaca Angka. Dok ini tidak mengulanginya.

## Consequences

- **Perubahan perilaku yang disengaja**: akun yang klaimnya memuat izin finance lain tanpa `finance.anggaran.kelola` (mis. paket `finance_view`), staf finance tier staff, dan IT mendapat 403 saat menulis anggaran dan tidak melihat tombol tulis. Belum diukur di prod apakah ada staf yang selama ini mengisi anggaran (bip-erp#2811).
- **Urutan deploy mengikat**: paket `finance_anggaran` harus dipasang ke posisi Cost Control sebelum integration-service naik, kalau tidak Cost Control sendiri kena 403; token lama pemegang paket perlu login ulang. Rincian di [[Finance - Serapan Anggaran dan Cost Control]].
- **Gerbang endpoint serapan lebih sempit dari gerbang layar**: tanpa cadangan tier finance, akun ber-peran finance tanpa paket membuka halaman tetapi melihat "tidak berwenang" di blok dana dari pengajuan. Menyamakannya menuntut aturan cadangan dipindah ke `shared-library` (task tersendiri).
- **Dokumen di luar kedua daftar** (jurnal gagal terbit, atau dicatat tanpa nomor jurnal) tidak tampil di mana pun; dibiarkan sementara.
- Konfirmasi Pemutus atas K9 dan lima keputusan terbuka lain dilacak di bip-erp#2814.

## Belum diputuskan

Daftar lengkap ada di [[Finance - Serapan Anggaran dan Cost Control]] §Belum Diputuskan (TBD). Ringkasnya: tiga bagian sheet rincian pos yang belum dirender, dokumen di luar kedua daftar, kesetaraan gerbang endpoint dengan gerbang layar, penjumlahan "sisa sesudah dicatat" per pos, dan ketergantungan template pada Accurate.

## Dokumen Terkait

- [[Finance - Serapan Anggaran dan Cost Control]]
- [[Finance - Rancangan Finance Service]]
- [[CORE - RBAC dan Permission Set]]
- [[API - Procurement Service]]
- [[API - Integration Service]]
- [[APP - Web ERP]]
- [[REF - Kepemilikan Data]]
- [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]
