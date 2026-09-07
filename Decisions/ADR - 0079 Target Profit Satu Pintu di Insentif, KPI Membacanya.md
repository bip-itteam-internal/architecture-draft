## Untuk Manajemen

**Apa yang berubah di layar.** Target profit per orang per bulan diketik **satu kali**, di layar Master Data Insentif. SPV Beauty Hacks dan SPV Kyura mengetik target Leader, Account Specialist, dan Advertiser di divisinya sendiri. Target SPV sendiri diketik Finance atau Direktur. Layar Atur Target KPI berhenti meminta target profit; ia menampilkan angka yang sama dengan yang ada di insentif, dan skor KPI dihitung dari angka itu. Halaman Target Marketing (alur Finance menetapkan total, SPV memecah, Direktur menyetujui) ditutup karena tidak pernah dipakai dan bertentangan dengan keputusan ini.

**Siapa yang terdampak.** SPV Beauty Hacks dan Kyura (sekarang bisa menulis target bawahannya; sebelumnya ditolak sistem). Finance (tetap boleh menulis semua level, tidak kehilangan hak). HR (tidak lagi mengetik target profit di template KPI). Seluruh karyawan marketing (angka target di kartu KPI sama dengan angka di Insentif Saya). Direktur (tidak ada lagi antrean persetujuan target).

**Yang tidak dijanjikan.** Skor KPI bulan yang sudah dibekukan tidak dihitung ulang otomatis; koreksi tetap manual seperti sekarang. Angka realisasi profit di KPI tetap sedikit berbeda dari di insentif karena jendela periodenya memang berbeda, itu keputusan lama yang tidak diubah. Pencapaian SPV masih salah hitung sampai hierarki beban operasional dikerjakan (keputusan terpisah). Target harus sudah diisi sebelum tanggal 1 pukul 02.00 WIB; yang terlambat baru berlaku untuk bulan berikutnya.

**Perkiraan besaran kerja.** Sedang. Dua service backend (insentif dan kepegawaian), satu layar frontend dibenahi, satu alur dicabut, dan satu kali verifikasi angka lewat sistem yang berjalan. Lima task berurutan, dapat dikerjakan satu developer.

## Deskripsi

*Target profit tim marketing per entitas per periode hanya ditulis di satu tempat, koleksi target milik insentive-service, oleh orang yang berwenang atas level itu; sumber KPI `insentif_profit` membaca target dari sana bersama realisasi yang memang sudah dibacanya, sehingga template KPI berhenti menyimpan target untuk metrik profit. Alur target berjenjang Finance, SPV, Direktur yang tidak pernah terisi dipensiunkan.*

- **Status**: 🟡 **Diusulkan**, disetujui manajemen 2026-09-07 lewat wawancara `/analisa-kebutuhan`. **T1 (gerbang tulis per level dan divisi) sudah dikodekan** di bip-erp PR [#1767](https://github.com/bip-itteam-internal/bip-erp/pull/1767) (test hijau, kontrol negatif terbukti, **belum merge, belum deploy**); **T4 (Master Target per orang, sekaligus Dashboard Insentif, struktur HRIS + i18n) sudah dikodekan** di erp-frontend PR [#1473](https://github.com/bip-itteam-internal/erp-frontend/pull/1473) (draft, merge menunggu #1767 di dev); **T2 (KPI membaca target dari sumber insentif) sudah dikodekan** di bip-erp PR [#1775](https://github.com/bip-itteam-internal/bip-erp/pull/1775) (**merged 2026-09-07 14:42 UTC** ke `main` ce30a716; **live di dev 21:44 WIB dan di prod 22:16 WIB, keduanya terverifikasi 2026-09-07**: di prod `auto_target` Aan Budiyanto Agustus 44 jt (insentif) bukan 88 jt (template), Silvia 165 jt bukan 116,89 jt, Aan September "belum dapat dihitung: target profit belum diisi di Master Target insentif", skor beku Annisa Agustus tak berubah; lihat catatan transisi di §3 dan §7); T3, T5, T6 belum ada kodenya. Daftar task: `Workspace/ANALISA - Target Profit Satu Pintu.md` (papan kerja, bukan dok terbit).
- **Path di repo**: `bip-erp/services/insentive/gerbang_target.go` (baru, T1: predikat murni `putuskanTulisTarget` + middleware `gerbangTulisTarget`) · `bip-erp/shared-library/common/gerbang_insentif.go` (T1: ekspor boolean `BolehTulisMasterProfit`) · `bip-erp/services/insentive/func.go` (`POST /profit/targets`, `GET /profit-dashboard`) · `bip-erp/services/insentive/business_rules.go` · `bip-erp/services/employee/kpi_sumber_insentif_profit.go` dan `_test.go` (target dari sumber, test pengunci ditulis ulang) · `bip-erp/shared-library/models/employee/kpi_reduksi.go` (`TargetBerlaku`) · `bip-erp/services/employee/kpi_finalisasi.go` dan `kpi_score_tersimpan.go` (snapshot target) · `bip-erp/services/employee/kpi_target_marketing.go`, `kpi_target_marketing_routes.go` (dicabut) · `erp-frontend/src/features/finance/incentive/profit/components/master-target.tsx`, `editor-target.tsx` (tabel per orang, i18n) · `erp-frontend/src/features/hris/kpi/components/blueprint/atur-target-inline.tsx` (target profit jadi tampilan) · `erp-frontend/src/features/hris/kpi/components/target-marketing-view.tsx` dan halaman `/finance/target-marketing`, `/marketing/target-marketing`, panel antrean Direktur (dicabut)
- **Tanggal**: 2026-09-07

## Context

**Satu fakta, dua tempat, dan kode menyatakan itu disengaja.** Target profit per orang hidup di `incentive_profit_targets` (insentive-service, menentukan rate insentif) dan di `kpi_template.metrics[profit].auto.target` beserta `target_per_karyawan` (employee-service, menentukan skor KPI). Komentar di sumber KPI menetapkan pembagiannya: "REALISASI dari insentif, TARGET dari template KPI", dan menambahkan bahwa insentif "tetap punya targetnya sendiri untuk menghitung RATE" (`services/employee/kpi_sumber_insentif_profit.go:162-177`). Pembagian itu dikunci test `TestKatalog_TakAdaPencapaianTarget`. Keputusan itu lahir 2026-08-25 dari kekhawatiran yang benar (dua target diketik dua orang tanpa penyama), tetapi menyelesaikannya dengan **mempertahankan** dua target, bukan menyatukannya.

**Terukur menyimpang di produksi.** Diukur 2026-09-07 pukul 04.29 WIB untuk periode Agustus 2026: seluruh target insentif diketik tangan satu akun pada 2026-08-26; `incentive_org` kosong sehingga turunan dari target SPV selalu nol; dari 28 Account Specialist, 9 berbeda nilainya antara insentif dan template KPI; 4 orang bernilai nol di insentif tetapi 22 juta di KPI; dua Leader jatuh ke bawaan template 3,4 miliar tanpa satu pun galat. Sumber angka manusianya satu, yaitu spreadsheet bulanan tim Marketing, diketik dua kali.

**Keputusan manajemen (wawancara 2026-09-07).** Pertama, target insentif dan target KPI **satu angka yang sama**; bila berbeda itu bug, bukan kebijakan. Kedua, **SPV Marketing** berwenang menetapkan target bawahannya langsung, tanpa persetujuan tambahan. Ketiga, target **SPV sendiri** ditetapkan Finance atau Direktur; tak seorang pun menetapkan target untuk dirinya sendiri.

**Yang sudah ada, dan sejauh mana menjawab.**

- Koleksi target insentif adalah penyimpanan target paling terjaga di sistem: kunci `{level, entity_id, periode}`, riwayat perubahan beralasan, kunci `disetujui`, aturan `BolehUbahTarget` (bebas sebelum periode, wajib alasan saat berjalan, ditolak setelah disetujui). Ketik per orang sudah didukung lewat baris manual di level icc (`shared-library/models/insentive/models.go:143-158`, `services/insentive/business_rules.go:230-241`).
- Gerbang tulisnya `RequireMasterProfitWriter` meloloskan finance, IT, dan Direktur, dan **sengaja menolak** atasan marketing (`shared-library/common/gerbang_insentif.go:56-73`, keputusan pemilik produk 2026-08-25). Alasannya, menulis target berarti menentukan uang keluar. Alasan itu tetap sah untuk target diri sendiri, dan itulah yang dijaga keputusan ketiga.
- `GET /profit-dashboard` sudah mengembalikan `target` dan `employee_id` di baris yang sama; employee-service sudah memanggilnya untuk realisasi dan sudah men-decode field `Target` tanpa memakainya (`services/employee/kpi_sumber_insentif_profit.go:60`, `:241-242`). Jalur datanya sudah ada.
- Pembekuan skor tanggal 1 pukul 02.00 WIB menyimpan template beserta target, dan skor beku memakai target snapshot (`services/employee/kpi_finalisasi.go:695-710`, `kpi_score_tersimpan.go:149-153`). Kekebalan skor beku terhadap perubahan target sudah ada dan wajib dipertahankan.
- Alur `/kpi/target-marketing` (Finance menetapkan total, SPV memecah, Direktur menyetujui) lengkap dengan layar dan antrean Direktur, tetapi koleksinya **nol dokumen seumur hidup**, hanya mengenal Leader dan ICC (Advertiser dikecualikan atas "perintah user", `services/employee/kpi_target_marketing.go:58-67`), daftar departemennya ditulis mati (`:18`), dan metrik bawaannya `gross_profit` sementara sumber profit mendaftar `profit`, sehingga materialisasinya akan jatuh ke `tak_termaterialisasi` tanpa galat (`kpi_target_marketing_routes.go:26`, `:411`). Ia bertentangan langsung dengan keputusan kedua.

**Gerbang aturan bisnis.** `mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md` tidak menyebut insentif, profit, maupun target. Otoritas skema insentif adalah SK Direktur 010/DIR/Rev-SK6/VII/2026 dan 011/DIR/SK6/VII/2026 ([[Finance - Incentive]]), dan lampiran SK yang memuat target sesungguhnya masih ditunggu. ADR ini **tidak menetapkan angka**; ia menetapkan tempat dan penulisnya.

**Status dok yang jadi landasan.** [[Finance - Incentive]] dan [[Microservices - Insentive Service]] berstatus ⚠️ (engine selesai, master data belum terisi, angka belum layak membayar). Amandemen [[ADR - 0033 Beban Operasional Insentif dari Proyek Accurate]] tentang hierarki beban SPV sudah diputuskan tetapi belum di kode, sehingga pencapaian SPV masih salah hitung apa pun targetnya. Keputusan ini berdiri di atas kenyataan itu, bukan di atas rencana.

## Decision

### 1. Koleksi target insentif adalah satu-satunya tempat target profit ditulis

`incentive_profit_targets` dengan kunci `{level, entity_id, periode}` tetap. Target per orang untuk Account Specialist dan Advertiser ditulis di level `icc` (insentif sudah menilai Advertiser di level itu), Leader di level `leader`, SPV di level `supervisor`. Tidak ada tempat lain yang menerima ketikan target profit: bukan template KPI, bukan alur target-marketing, bukan spreadsheet yang diimpor.

### 2. Gerbang tulis per level dan per divisi, dan tak seorang pun menulis targetnya sendiri

Level `icc` dan `leader` boleh ditulis oleh SPV Marketing untuk **divisinya sendiri**, ditambah finance, IT, dan Direktur seperti sekarang. Level `supervisor` tetap finance, IT, dan Direktur. Peran SPV diturunkan dari jabatan dan departemen di `work_data`, pola yang sudah ada di `perananTarget`, bukan dari `system_roles`. Server menolak permintaan yang `entity_id`-nya adalah pemanggil sendiri, apa pun perannya. `BolehUbahTarget`, `riwayat[]`, dan kunci `disetujui` tidak berubah dan kini melindungi KPI juga.

**Sebagaimana dikodekan (T1, branch `feat/insentive-gerbang-target`, belum merge).** Jabatan dan departemen dibaca dari **rekaman hierarki** (`GET /list?type=employee&with_supervisor=true` milik employee-service, yaitu `work_data` segar), bukan dari header `BIP-Position`/`BIP-Department` yang bisa basi 72 jam dan tidak membawa `position_key`. Pengenal Supervisor memakai `berposisiSupervisor` dan pembanding divisi `departemenSama`, keduanya yang sudah dipakai penyusun baris dashboard, supaya "siapa SPV" tidak punya dua jawaban. Hierarki tidak terbaca → **503** bertulisan (fail-closed); jalur finance, IT, Direktur tidak menyentuh hierarki sama sekali. Level tidak dikenal → **400**, dan level disimpan kanonik (huruf kecil) karena `ambilTargets` menyaring level persis. **Konsekuensi yang diterima sadar**: Supervisor departemen mana pun bisa menulis baris icc/leader untuk anggotanya sendiri; barisnya yatim, karena dashboard membangun baris dari hierarki dan pemetaan toko lalu mencari target per entitas, sehingga tidak pernah dibaca maupun dibayar. Bila kelak perlu dipersempit, syaratnya berbasis data (entitas memang punya baris di level itu), bukan daftar nama departemen, dan bukan `system_roles`.

### 3. KPI membaca target dari sumber, bukan dari template

Sumber `insentif_profit` menyediakan target metrik `profit` dari field `target` pada baris `/profit-dashboard` yang sudah ditariknya. Mesin KPI mendapat satu konsep baru: **target dari sumber**, yang berlaku hanya untuk metrik yang sumbernya menyatakan menyediakannya, dan untuk metrik itu template **tidak lagi** menjadi tempat target. Metrik lain tetap memakai empat lapis `TargetBerlaku`. Layar Atur Target menampilkan angka dari insentif untuk metrik profit, tidak menerimanya sebagai isian.

**Sebagaimana dikodekan (T2, PR [#1775](https://github.com/bip-itteam-internal/bip-erp/pull/1775) merged dan live di prod 2026-09-07).** Konsepnya berupa registry `DaftarkanTargetSumber(sumber, tempat, metrik...)` di employee-service dan field `Cuplikan.TargetSumber`; `targetUntukCuplikan` memakai target sumber untuk metrik terdaftar dan **menolak** jatuh ke template. Target yang dipakai tersimpan di `KPIMetric.AutoTarget` (ikut snapshot beku), dan katalog sumber mengumumkan `target_dari_sumber[]` untuk layar. **Urutan transisi yang diputuskan 2026-09-07**: sampai T5 naik, template **masih boleh menyimpan** target untuk metrik profit dan mesin mengabaikannya. Frontend hari ini memblokir simpan bila `auto.target <= 0`, jadi membersihkan atau menolaknya di backend lebih dulu akan membuat HR tak bisa menyimpan template yang sudah ber-`target_per_karyawan` sampai layar berubah. Pembersihan, pelonggaran validasi, dan penolakan tegas dipasang **bersama T5**. Ini urutan deploy, bukan perubahan keputusan.

### 4. Target yang tidak ada berarti "belum bisa dinilai", bukan bawaan

Bila insentif belum punya target untuk seseorang pada periode itu, metrik profit KPI-nya **tidak dinilai**: nilai kosong dengan keterangan "target belum diisi", ikut ke cakupan dan peringatan yang sudah ada. Tidak ada bawaan 50 juta, 2 miliar, atau 3,4 miliar. Jatuh diam-diam ke bawaan template adalah persis mekanisme yang membuat dua Leader dinilai terhadap 3,4 miliar pada Agustus 2026.

### 5. Snapshot beku menyimpan target yang dipakai

Pembekuan tanggal 1 pukul 02.00 WIB menyimpan target dari sumber ke dalam snapshot skor (`auto_target`), sehingga pembacaan skor beku tidak lagi menghitung ulang dari template maupun dari insentif. Target yang diubah sesudah beku tidak menyentuh skor beku; koreksinya lewat finalisasi ulang manual, seperti sekarang. Setelah hasil insentif periode itu `disetujui`, targetnya terkunci di insentif, dan KPI mengikuti.

### 6. Alur target-marketing dipensiunkan

Rute `/kpi/target-marketing`, halaman `/finance/target-marketing` dan `/marketing/target-marketing`, panel antrean "Target KPI Marketing" di Ruang Direktur, dan koleksi `kpi_target_marketing` dicabut. Tidak dipertahankan "untuk jaga-jaga": jalur tulis kedua yang hidup adalah masalah yang keputusan ini tutup.

### 7. Test pengunci ditulis ulang dengan arah sebaliknya

`TestKatalog_TakAdaPencapaianTarget` beserta komentar di sekitarnya diganti. Yang dikunci sekarang: sumber `insentif_profit` **wajib** menyediakan target untuk metrik `profit`, dan template yang memuat target untuk metrik itu ditolak validasi. Alasannya ditulis di test: keputusan manajemen 2026-09-07 bahwa keduanya satu angka. Menghapus test lama tanpa menulis yang baru berarti mengundang pembalikan keempat dari sejarah yang sudah tiga kali bolak-balik.

**Sebagaimana dikodekan (T2).** Test penggantinya `TestSumberProfit_TargetDariInsentif` (sumber wajib membawa target `profit`, hanya `profit`, target nol jadi `nil` dan mesin menolak menilai tanpa jatuh ke template) plus `kpi_target_sumber_test.go`; kontrol negatifnya dijalankan (fallback ke template dihidupkan sebentar membuat tiga test merah pada assertion yang diklaim). Bagian "template yang memuat target ditolak validasi" **belum dikunci test** karena penolakannya sendiri digeser ke T5 (lihat §3); saat T5 dikerjakan, test itu wajib ditambahkan bersama pelonggaran validasinya.

### 8. Hanya target yang disatukan, realisasi tetap dua angka sah

Realisasi versi KPI memakai `mode=bergeser` dan sah berbeda tipis dari versi insentif (keputusan pemilik produk 2026-08-27, [[Microservices - Insentive Service]] §Dua jendela periode). Keputusan ini tidak menyentuhnya.

### 9. Layar target insentif ikut ADR 0010 dan memakai pola yang ada

Layar Master Target belum ber-i18n sama sekali. Saat diubah menjadi tabel per orang, seluruh teksnya lewat `react-i18next` ([[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]]), dan tabelnya mengikuti pola `TargetMassalModal` yang sudah menangani "kosong berarti tidak diisi" dan format ribuan, bukan merakit tabel baru.

## Consequences

### Yang membaik

- Pertanyaan "target profit si A bulan ini berapa" punya satu jawaban, dan jawaban itu yang dipakai membayar sekaligus menilai.
- SPV Marketing mengetik sekali di layar yang memang ia buka tiap bulan; HR berhenti mengetik angka yang bukan miliknya.
- Riwayat perubahan target beralasan dan kunci setelah disetujui, yang selama ini hanya melindungi uang, kini melindungi skor.
- Empat orang yang bernilai nol di insentif tetapi 22 juta di KPI tidak mungkin terjadi lagi: yang kosong terbaca kosong di kedua sisi.

### Yang memburuk atau tetap terbuka

- Skor KPI bergantung pada insentive-service saat pembekuan. Ini sudah berlaku untuk realisasi sejak 2026-08-26, jadi ketergantungannya tidak baru, tetapi sekarang kegagalannya mematikan target juga. Penjaga fail-closed yang ada tetap berlaku.
- Riwayat "siapa mengubah target profit" pindah dari `kpi_template_audits` ke `riwayat[]` insentif. Layar riwayat konfigurasi KPI tidak lagi memuatnya; yang membutuhkannya membaca di insentif.
- Dua kelompok penulis (SPV untuk bawahannya, Finance dan Direktur untuk semua) tetap ada untuk level `icc` dan `leader`, tetapi di satu tempat dengan satu riwayat. Ini bukan duplikasi fakta; ini dua orang berwenang atas satu fakta.
- Skor Agustus 2026 yang sudah beku dengan target lama tidak dikoreksi otomatis.
- Dua hal pra-eksisting yang peluangnya naik begitu penulisnya bertambah (temuan `/review` T1, jadi task lanjutan): `incentive_profit_targets` **tidak punya indeks unik** pada `{level, entity_id, periode}` sehingga dua penulis paralel pada baris baru bisa menggandakan dokumen; dan daftar level ditulis di tiga tempat (`kanonLevel`, validasi `/profit-dashboard`, validasi `/profit/org`).
- Deploy: gerbang tulis hidup di `shared-library`, jadi insentive-service dan employee-service naik bersama, lalu erp-frontend. T1 sendirian cukup menaikkan insentive-service. Tidak ada env baru. Kontrak berubah (payload sumber KPI membawa target), jadi BE sebelum FE.
- [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]] tetap berlaku: tidak ada service lain yang menulis ke `employee_db`; target masuk lewat pembacaan HTTP, bukan tulis lintas-DB.
- `posisiDibreakdown` dan daftar departemen mati di alur lama tidak diwarisi; keanggotaan divisi datang dari `work_data` lewat employee-service seperti pada `/profit-dashboard`.

### Yang sengaja tidak dilakukan

- **Tidak menyatukan realisasi.** Dua jendela periode adalah keputusan sadar dengan alasan keadilan pembayaran.
- **Tidak menambah persetujuan Direktur** untuk target per orang. Manajemen memutuskan SPV menulis langsung; persetujuan yang ada di insentif (hasil periode) sudah cukup sebagai kunci.
- **Tidak membangun sinkron dua arah** maupun pemindai drift antara template dan insentif. Salinan yang diawasi tetap dua tempat; keputusan ini menghapus tempat keduanya.
- **Tidak mempertahankan alur target-marketing** sebagai opsi. Alur yang tak pernah terisi selama hidupnya tidak membuktikan apa pun selain bahwa ia tidak dibutuhkan.

## Dokumen Terkait

- [[REF - Kepemilikan Data]] §Duplikasi, tempat masalah ini pertama kali dicatat dan dituntut ADR
- [[Finance - Incentive]] · [[Microservices - Insentive Service]] · [[API - Insentive Service]]
- [[HRIS - Otomasi Skor KPI]] · [[Microservices - Employee Service]] · [[HRIS - Alur KPI Otomatis]]
- [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]] · [[ADR - 0033 Beban Operasional Insentif dari Proyek Accurate]] · [[ADR - 0053 Struktur dan Target KPI Disatukan di Satu Halaman]] · [[ADR - 0045 Identitas Tim Tunggal dan Peta Kepemilikan Marketing]]
- [[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]] · [[APP - Web ERP]]
