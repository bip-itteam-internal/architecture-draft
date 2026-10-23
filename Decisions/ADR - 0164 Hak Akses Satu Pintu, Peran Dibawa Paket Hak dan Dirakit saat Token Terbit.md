# ADR - 0164 Hak Akses Satu Pintu, Peran Dibawa Paket Hak dan Dirakit saat Token Terbit

> **Status**: 🟢 **Diterima**, 2026-10-10, oleh irfanarfianto (diusulkan 2026-10-10). Kode belum ada; pekerjaan di bip-erp#2933 dan sub-issue-nya. Aturan persetujuan ADR di [[ADR - 0151 Issue Siap Dikerjakan Agent Bila Keputusannya Bisa Ditunjuk, Ditandai Manusia]].

## Untuk Manajemen

**Apa yang berubah di layar.** Hak akses diatur di satu tempat saja, yaitu menu **Hak Akses**. Isian peran per modul di menu **Akun Karyawan** dihapus; menu itu tinggal mengurus akun (aktif dan nonaktif, reset kata sandi, lupakan perangkat). Peran yang selama ini diketik per orang berubah menjadi paket yang dipasang ke **jabatan**, sehingga karyawan baru atau karyawan yang pindah jabatan langsung mendapat hak yang sesuai. Orang yang haknya memang berbeda dari jabatannya dicatat sebagai **pengecualian** yang terlihat di layar. Menu Hak Akses juga mendapat tampilan baru: hak satu orang beserta asalnya (dari jabatan atau dari pengecualian).

**Siapa yang terdampak.** Tim IT yang mengatur hak (cara kerjanya berubah). Karyawan lain **tidak merasakan apa pun**: menu dan akses tiap orang sesudah peralihan harus sama persis dengan sebelumnya, dan itu dibuktikan per akun sebelum peralihan dinyalakan.

**Apa yang tidak dijanjikan.**

- Tidak ada hak yang dirapikan, ditambah, atau dicabut dalam pekerjaan ini. Hak yang hari ini keliru tetap keliru sesudahnya; bedanya ia kini terlihat dan bisa dibetulkan dari satu layar.
- Aplikasi MyBharata tidak berubah.
- Cara sistem memeriksa hak di balik layar belum berubah di tahap ini. Memindahkannya adalah tahap berikutnya, modul demi modul.
- Tidak ada tanggal selesai yang dijanjikan di dokumen ini.

**Perkiraan besaran kerja.** Tujuh pekerjaan: empat di backend, dua di web, ditambah satu kali pemindahan data di produksi yang dijalankan manusia dengan uji coba dan cadangan. Selama pemindahan data berlangsung, perubahan hak dibekukan.

## Deskripsi

*Pengaturan hak akses ERP disatukan ke paket hak: peran per modul (`system_roles`) tidak lagi diketik per akun, melainkan dibawa oleh paket berjenis peran yang dipasang ke jabatan dengan pengecualian per akun, lalu dirakit saat token terbit. Bentuk keluarannya sengaja tidak berubah, sehingga gerbang backend, sidebar, gerbang rute web, dan MyBharata tetap bekerja tanpa disentuh, dan kesamaan hak dibuktikan dengan membandingkan isi token tiap akun. Ini melanjutkan [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] dan menuntaskan pembongkaran yang dijanjikan [[ADR - 0043 Peran Sistem Diturunkan dari Jabatan]].*

- **Status**: 🟡 Diusulkan (lihat baris status di atas).
- **Path di repo** (yang AKAN disentuh): `bip-erp/services/employee/permission_resolve.go` · `bip-erp/services/employee/peran_dari_jabatan.go` · `bip-erp/shared-library/models/employee/permission_set.go` · `bip-erp/services/employee/banding_token*.go` (baru) · `bip-erp/scripts/hak-akses-satu-pintu/` (baru) · `bip-erp/orchestrator/it/set_roles.go` · `bip-erp/services/employee/external_account_routes.go` · `erp-frontend/src/app/(main)/it/hak-akses/page.tsx` · `erp-frontend/src/features/hris/master-data/components/` · `erp-frontend/src/features/it/employee/components/account-role-form.tsx` · `erp-frontend/src/features/hris/external-accounts/components/access-dialog.tsx`
- **Tanggal**: 2026-10-10

## Context

Hak seseorang hari ini datang dari tiga sumber yang diatur di tempat berbeda:

1. **Peran per modul yang diketik per akun** (`system_authentication.system_roles`, peta modul ke satu nilai). Layarnya menu Akun Karyawan, lewat `POST /api/it/roles/set`. Untuk akun pihak luar ada jalur tulis kedua, tab Role Modul.
2. **Peran yang diturunkan dari jabatan** saat token terbit ([[ADR - 0043 Peran Sistem Diturunkan dari Jabatan]]): tabel di kode Go mengisi modul yang kosong dan tidak pernah menimpa nilai yang diketik (`services/employee/peran_dari_jabatan.go:281-341`, dibaca di `origin/main` 2026-10-10). Hasilnya tidak ditulis ke database, jadi database tidak menceritakan peran yang berlaku.
3. **Paket hak** (`permission_sets`) yang dipasang ke jabatan dan, sebagai pengecualian, ke akun ([[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]). Layarnya menu Hak Akses.

Pemilik produk memutuskan (2026-10-10) bahwa ini harus satu pintu: paket hak menggantikan peran sebagai tempat mengatur, pengaturan peran di Akun Karyawan dihilangkan, dan **pengguna tidak boleh merasakan perubahan pada haknya**.

Vault belum punya keputusan itu. [[CORE - RBAC dan Permission Set]] menulis bahwa menyatukan sumbu "modul mana yang ada untuk saya" dengan paket hak "adalah keputusan arsitektur tersendiri", dan [[APP - Web ERP]] mencatat bahwa `system_roles` belum pensiun sebagai sumbu akses.

**Yang diukur untuk keputusan ini (2026-10-10).**

- Produksi, `employee_db`, baca saja: 220 akun (183 aktif); 122 akun menyimpan peran; 35 akun memegang paket per akun; 74 akun aktif tidak punya peran maupun paket. Dari 125 jabatan di master, 38 sudah berpaket. Ada 130 paket di 26 modul.
- Dari 78 jabatan yang punya pemegang, **14 jabatan pemegangnya menyimpan peran yang tidak seragam**, menyangkut 23 orang yang menyimpang dari mayoritas jabatannya. ⚠️ Angka ini dihitung dari peran **tersimpan**; peran yang berlaku sudah ditambah penurunan dari jabatan, jadi angka sebenarnya bisa berbeda dan wajib diukur ulang dengan alat banding (Decision butir 6).
- Nilai peran tidak baku: dua ejaan hidup berdampingan (`admin gudang RM` dengan spasi, `admin_gudang` dengan garis bawah), dan cara kode membandingkannya tidak seragam (ada yang persis, ada yang menyamakan spasi dan garis bawah, ada yang menerima nilai apa pun yang tidak kosong).
- Backend: 35 gerbang berbasis peran didefinisikan di `shared-library/common/roles.go`, dan beberapa service masih sepenuhnya digerbang peran tanpa katalog izin (warehouse, marketing-analytics, sebagian besar integration, insentive, kedua orchestrator). Gerbang modul berkatalog memilih sumber berurutan, klaim modul dulu baru peran, bukan gabungan (`common.KlaimMemuatIzinModul`).
- Web: 126 dari 231 definisi menu belum bertanda izin dan hanya digerbang kategori dari peran; gerbang rute di server (`src/proxy.ts`) hanya membaca cookie `system_roles`; susunan sidebar belum berupa fungsi murni sehingga belum bisa dibandingkan per akun.
- MyBharata: peran hanya datang dari respons tiga endpoint login dan disimpan di perangkat. Versi yang beredar menggagalkan login bila `system_roles` tidak ada di respons atau ada nilainya yang bukan teks (`lib/src/features/auth/data/implements/auth_implements.dart:66-72`, `origin/dev`), dan aplikasinya tidak punya paksa-pembaruan.

**Kenapa tidak langsung menghapus peran.** Tiga hal di atas (service tanpa katalog, menu tanpa izin, MyBharata) membuat penghapusan langsung mengunci orang dari modulnya dan menggagalkan login mobile. Syarat "tidak merasakan perubahan" hanya bisa dipenuhi bila bentuk yang dikonsumsi gerbang dan aplikasi tidak berubah.

**Dok yang dijadikan pijakan dan statusnya.** [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] dan [[ADR - 0043 Peran Sistem Diturunkan dari Jabatan]] berstatus Implemented. [[ADR - 0149 Sidebar Satu Daftar Urusan, Menu Digerbang Izin Posisi, Beranda Ruang Kerja Posisi]] sedang berjalan per departemen. [[ADR - 0137 Model Persetujuan Tunggal dan Pemisahan Tugas Lintas Modul]] masih 🟡 Diusulkan dan **tidak** dijadikan dasar keputusan ini.

## Decision

**1. Satu pintu pengaturan.** Hak diatur hanya lewat paket hak di menu Hak Akses. Peran tidak lagi diketik per akun, baik untuk karyawan maupun akun pihak luar.

**2. Paket peran.** Peran dibawa oleh paket berjenis peran: satu paket memuat tepat satu pasangan modul dan nilai peran, tanpa izin. Ia disimpan bersama paket hak yang ada dan dipasang lewat mekanisme yang sama (ke jabatan, atau ke akun sebagai pengecualian). Paket peran sengaja tidak membawa izin, supaya pemasangannya tidak mengubah klaim izin siapa pun dan tidak memicu aturan "klaim modul menang atas peran" yang pernah mencabut akses di produksi (2026-09-08, dicatat di [[CORE - RBAC dan Permission Set]]).

**3. Nilai peran disalin apa adanya.** Paket peran dibangkitkan dari pasangan modul dan nilai yang benar-benar hidup, dengan ejaan persis seperti tersimpan. Menormalkan ejaan dilarang di pekerjaan ini, karena pembanding di kode tidak seragam dan penyeragaman akan melebarkan atau menyempitkan hak tanpa gejala.

**4. Dirakit saat token terbit, di keempat jalur** (login, PIN, biometrik, refresh). Untuk tiap modul: pengecualian akun menang; bila tidak ada, dipakai paket peran jabatannya. Satu modul satu nilai, jadi dua paket peran untuk modul yang sama pada satu jabatan ditolak saat disimpan. Pengecualian akun boleh berbunyi **tanpa peran**, untuk orang yang sengaja tidak memegang peran jabatannya.

**5. Bentuk keluaran tidak berubah.** Klaim `system_roles` di token, header yang diteruskan gateway, dan respons login tetap berupa peta modul ke satu teks; klaim `permissions` tidak disentuh. Gerbang backend, sidebar, gerbang rute web, dan MyBharata tidak diubah di tahap ini.

**6. "Sama persis" dibuktikan, per akun, per lingkungan.** Sebuah alat banding menghitung isi token (peran dan izin) setiap akun dengan cara lama dan cara baru, termasuk akun nonaktif dan akun pihak luar. Sisi lama wajib memakai peran yang berlaku (tersimpan ditambah turunan jabatan), bukan isi database. Selisih ke arah mana pun, hak hilang maupun hak bertambah, adalah kegagalan. Sakelar perakitan baru hanya boleh dinyalakan di sebuah lingkungan bila selisihnya nol di lingkungan itu.

**7. Jabatan yang pemegangnya tidak seragam tidak diseragamkan.** Jabatan menerima paket peran yang dipegang mayoritas pemegangnya; yang berbeda dijadikan pengecualian per akun, sehingga hak semua orang tetap. Merapikan pengecualian itu adalah pekerjaan terpisah sesudahnya.

**8. Tabel peran dari jabatan menjadi data.** Isi tabel di kode Go dipindahkan menjadi paket peran yang terpasang di jabatan, lalu tabel dan sakelarnya dibongkar setelah perakitan baru stabil. Ini menuntaskan pembongkaran yang dijadwalkan [[ADR - 0043 Peran Sistem Diturunkan dari Jabatan]].

**9. Jalur tulis peran ditutup sesudah sakelar menyala.** Form peran di Akun Karyawan dan tab Role Modul akun pihak luar dihapus, dan endpoint penulisnya ditolak. Kolom peran yang tersimpan **tidak dihapus** di tahap ini: ia menjadi cadangan pembatalan dan tidak lagi dibaca perakit.

**10. Pembaca peran di luar token dipindah ke sumber yang sama.** Kode yang memilih penerima notifikasi atau menyusun daftar admin dengan membaca peran langsung dari database harus memakai hasil perakitan yang sama dengan token.

**11. Pengelola tidak berubah.** Yang boleh memasang paket ke jabatan tetap supervisor IT.

**12. Pemindahan data dijalankan manusia, dan perubahan hak dibekukan selama itu.** Skripnya menyediakan uji coba, cadangan, dan pembatalan. Sakelar bawaannya mati.

**13. Tahap berikutnya.** Memindahkan gerbang dan menu dari peran ke izin tetap dikerjakan modul demi modul menurut [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] dan [[ADR - 0149 Sidebar Satu Daftar Urusan, Menu Digerbang Izin Posisi, Beranda Ruang Kerja Posisi]]. Aturan butir 6 berlaku juga di sana, di tingkat izin dan menu.

**Alternatif yang ditolak.**

- *Menyatukan layarnya saja* (Hak Akses ikut menyunting peran per akun): peran tetap diketik per orang dan tabel di kode tetap hidup.
- *Menambah isian peran pada paket hak biasa*: modul tanpa katalog izin tidak bisa punya paket, jadi tetap butuh paket tanpa izin.
- *Memindahkan semua gerbang ke izin sekaligus*: lihat "Kenapa tidak langsung menghapus peran".

## Consequences

- ➕ Pertanyaan "orang ini boleh apa dan dari mana" terjawab dari satu layar, termasuk peran yang hari ini hanya ada sebagai tabel di kode.
- ➕ Karyawan baru dan mutasi mendapat peran dari jabatannya tanpa pengisian per akun.
- ➕ Bukti kesamaan menjadi perbandingan dua peta kecil per akun, bukan penelusuran ratusan gerbang.
- ➖ Di balik layar gerbang tetap membaca peran. "Satu pintu" di tahap ini adalah satu pintu pengaturan, belum satu mekanisme penegakan.
- ➖ Jumlah paket bertambah sebanyak pasangan modul dan nilai yang hidup, dan layar paket perlu memisahkan paket peran dari paket izin supaya tetap terbaca.
- ➖ Layar Hak Akses belum bisa menampilkan hak efektif satu orang. Tampilan itu wajib ada sebelum form peran dihapus, karena form itu satu-satunya tempat melihat peran seseorang.
- ⚠️ **Hak dibekukan saat token terbit dan token berlaku 72 jam.** Sesudah sakelar menyala ada masa token lama dan baru beredar bersamaan. Karena isinya harus sama, masa itu tidak boleh berdampak; bila berdampak, alat bandingnya yang salah.
- ⚠️ **Sakelar dibaca saat container dibuat.** Menyalakannya menuntut container dibuat ulang, dan keadaannya diperiksa di container, bukan di berkas compose (pelajaran percobaan 2026-08-09 di [[CORE - RBAC dan Permission Set]]).
- ⚠️ **Migrasi saat service menyala.** Paket ber-key bawaan diselaraskan ulang tiap service menyala, jadi paket peran wajib memakai key baru. Pemulihan admin pusat membaca peran tersimpan; karena kolom itu dipertahankan (butir 9), perilakunya tidak berubah di tahap ini.
- ⚠️ **Urutan deploy.** Backend sebelum web. Web baru boleh kehilangan form peran setelah backend menyediakan hak efektif per orang.
- ⚠️ **Pembaca peran di luar token (butir 10) bisa mengubah perilaku.** Hari ini mereka membaca peran tersimpan, sehingga pemegang peran turunan tidak ikut terpilih. Memindahkannya ke hasil perakitan bisa menambah penerima notifikasi. Itu perubahan yang terlihat dan harus diukur serta diputuskan sebelum dikerjakan (lihat TBD).

## Belum Diputuskan (TBD)

- Apakah pemegang peran turunan ikut menjadi penerima notifikasi berbasis peran (butir 10), atau daftar penerima dibekukan seperti hari ini.
- Kapan kolom peran tersimpan dihapus, dan apa syaratnya.
- Apakah ejaan nilai peran diseragamkan kelak, dan bagaimana membuktikan kesamaannya.
- Nasib tiga akun pengembang yang memegang peran sangat lebar dan saling berbeda: tetap sebagai pengecualian, atau dirapikan.

## Dokumen Terkait

- [[CORE - RBAC dan Permission Set]] · [[Microservices - Employee Service]] · [[IT - Employee System]] · [[APP - Web ERP]] · [[APP - MyBharata]]
- [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] · [[ADR - 0043 Peran Sistem Diturunkan dari Jabatan]] · [[ADR - 0149 Sidebar Satu Daftar Urusan, Menu Digerbang Izin Posisi, Beranda Ruang Kerja Posisi]] · [[ADR - 0051 Pencabutan Tampilan Menu per Posisi]]
- [[ADR - 0078 Fase Satu WMS Menggabungkan Matriks dan Paket Hak, Bukan Menggantikannya]] · [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]] · [[RUN - Onboarding Akun Eksternal (Vendor & Mitra)]]
