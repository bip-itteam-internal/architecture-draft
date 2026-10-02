# ANALISA - Sidebar Satu Daftar Urusan

> Papan kerja hasil `/analisa-kebutuhan` 2026-10-02. Keputusannya: [[ADR - 0149 Sidebar Satu Daftar Urusan, Menu Digerbang Izin Posisi, Beranda Ruang Kerja Posisi]]. Dok domain: [[APP - Web ERP]]. Rancangan rinci per posisi: enam Artifact privat (tautan di bawah), disetujui user 2026-10-02.

## Kebutuhan sebenarnya

Solusi yang diminta: "sidebar tanpa pembatas Portal Saya, menu sama untuk semua". Masalah di baliknya:

1. Orang mencari pekerjaannya menurut urusan, sidebar menyusunnya menurut departemen; satu URL muncul di dua sampai empat kategori.
2. Menu yang tampil ditentukan kategori `system_roles`, bukan izin posisi; sekitar 126 dari 215 menu tanpa `perm`. Akibatnya Security tak melihat Buku Tamu, Corporate Secretary tak melihat Ruang Direktur, Tax Staff tak bisa membuka Pajak.
3. Hak di prod menumpuk di akun, bukan di posisi (melanggar ADR 0030); sebagian menyentuh pemisahan tugas atas uang dan hak akses (rincian: issue privat).

## Asumsi yang disetujui

1. Cakupan gudang Manufaktur tahap ini diturunkan dari jabatan dan peran gudang yang ada; Admin Warehouse dipecah per gudang. Penugasan gudang per orang TBD.
2. Akses Darurat IT dan pencabutan bypass IT menunggu SA-1 ADR 0137; bypass Direktur dicabut lewat paket jabatan.
3. Ruang Direktur untuk Corporate Secretary digerbang paket "Persetujuan: Direksi", bukan field `SetaraDirektur` di FE.
4. Sensus prod 2026-10-01 di Artifact bertanggal; ukur ulang sebelum mengeksekusi perbaikan data.
5. Temuan keamanan hanya dirujuk "issue privat" di vault; issue-nya di repo kode.

## Rancangan per departemen (Artifact privat)

Enam Artifact (Marketing, FAT, HRGA, Tech Development, Kesekretariatan, Manufaktur), masing-masing bertab Per posisi, Matriks lihat, Matriks aksi, Pemisahan tugas & jejak, Perbaikan data, Uji pakai. **Tautannya sengaja tidak ditulis di sini** karena vault ini repo publik dan beberapa Artifact memuat temuan akses; tautan dicantumkan di badan issue induk per departemen di GitHub Project #15 (repo privat).

## Jenis task

- **S**: sidebar FE, susun per urusan di dalam kategori yang masih ada (label lewat i18n id+en, URL ganda disatukan, induk per urusan, daun tanpa "Saya").
- **G**: gerbang FALLBACK, setiap daun departemen itu diberi `perm` + entri `FALLBACK` tier (atau `public`/gerbang khusus yang disengaja), tombol aksi digerbang izin aksi, gerbang rute `proxy.ts` diselaraskan. Perilaku tak boleh berubah bagi pemegang tier lama.
- **B**: ruang kerja Beranda (zona D), menurut ADR 0076: posisi tanpa data kerja tak diberi ruang kerja.
- **D**: perbaikan paket/peran prod, skrip dry-run + daftar sebelum/sesudah; dijalankan MANUSIA. Paket ke posisi, sertakan paket setara tier lama (jebakan paket sempit), pemegang login ulang.
- **X**: temuan keamanan, issue privat di repo kode; perbaikannya task kode biasa yang merujuk issue itu.

S dan G satu departemen boleh satu brief (G lebih dulu di dalamnya). Semua repo kode lewat PR dengan `Closes`.

## Urutan dan dependensi

```
U1 penjaga per daun ──┬─> {M,F,H,T,K,P}-SG (per departemen, urutan bebas, Marketing dulu)
                       │
{M,F,H,T,K,P}-D (manusia) ─────────────┐
                                        v
U2 urusan umum ─────────────────> U3 penyatuan akhir (cabut kategori)
{M,F,H,T,K,P}-B   (bebas, tak memblok)
```

⛔ U3 hanya setelah semua SG selesai dan D minimal keenam departemen dijalankan. Mencabut kategori lebih dulu membuka menu tanpa `perm` bagi semua orang.

## Task lintas departemen

- [ ] **U1 [FE] Penjaga gerbang per daun.** Test baru (`sidebar-gerbang.test.ts`) yang menyapu `menus` dan gagal bila sebuah daun tak punya `perm`, `public` yang disengaja, atau gerbang khusus terdaftar. Mulai dengan daftar-izin "belum bergerbang" yang hanya boleh menyusut (test merah bila bertambah). Tanpa perubahan perilaku. Kontrol negatif wajib.
- [ ] **U2 [FE] Urusan umum pengganti Portal Saya.** Pengajuan & Persetujuan (kartu persetujuan pindah dari Pengajuan ke Persetujuan), Tugas (tanpa Ajukan Tugas; jadi kartu Pengajuan; Permintaan Masuk pindah ke Tugas), KPI satu menu (lebur KPI Scoring HRIS dan KPI per departemen; rekap jadi tab), Kalender, Ruang Direktur. Insentif keluar dari Portal (ke F dan M). Masih di dalam kategori `erp` sampai U3.
- [ ] **U3 [FE] Penyatuan akhir.** Cabut `modules.includes(mod)` dan tambalan kategori di `sidebar.tsx`, hapus garis pemisah, satukan urutan menjadi satu daftar, cabut bypass `aksesSemuaMenu` untuk Direktur (IT menunggu ADR 0137), satukan definisi IT supervisor di `proxy.ts` dan sidebar. Tulis ulang test bentuk per kategori. Bergantung U1, U2, semua SG, dan D.
- [ ] **U4 [Vault] Sinkron dok** sesudah U3: [[APP - Web ERP]] (bagian Portal Saya dan `public: true`), [[CORE - RBAC dan Permission Set]], ADR 0039 dan ADR 0105 ditandai diubah sebagian.

## Marketing (percontohan)

- [ ] **M-SG [FE]** Susunan per Artifact Marketing: Toko & Penjualan, Iklan & Kampanye, Live, Layanan Pelanggan, Permintaan ke Unit Lain (Komplain Gudang + QC jadi Komplain Produk), Tim & Penugasan, Insentif (Rincian hanya bagi anggota skema lewat `GET /profit-dashboard/saya/keanggotaan`), Analisis, Kamus Metrik. Rekap KPI Tim jadi tab KPI. Setoran Tema & Teaser satu halaman. Gerbang per daun.
- [ ] **M-BE [BE]** Shop Quality dikenali `peranJabatanTabel` (`services/employee/peran_dari_jabatan.go`); cakupan S (toko milik sendiri) di endpoint marketing-analytics yang ditandai "baru" untuk pemegang toko. Deploy BE sebelum FE.
- [ ] **M-NEW [FE+BE]** Halaman Komplain Belum Dibalas dan SLA Chat (dari mart yang sudah ada). Task terpisah, sesudah M-SG.
- [ ] **M-B [FE]** Ruang kerja: Account Specialist/Marketplace Advertiser, Host Live, Live Support, Shop Quality, Engagement. Meta Advertiser menyebut keadaan "akun Meta belum tersambung", bukan nol.
- [ ] **M-D [manusia]** Lengkapi penugasan toko 7 Marketplace Advertiser; cabut peran insentif yang tak sesuai jabatan (6 orang) dan peran AS keliru di Engagement (2); lengkapi pemetaan CS ke toko (2 dari 3 belum); pastikan template KPI Marketplace Advertiser Kyura yang dipakai.

## FAT

- [ ] **F-SG [FE]** Susunan per Artifact FAT: Piutang & Penerimaan, Pengeluaran & Anggaran (Kas Kecil jadi menu), Pembukuan, Payroll Run (pindah dari HRIS, tampil untuk FAT sesuai izin), Insentif Marketing, Sinkron Penjualan ke Accurate (satu tempat, menu ganda digabung bertab), Pajak, Panduan Accurate. `/finance` keluar dari sidebar. Menu Karyawan Terlambat untuk Cost Control dihapus. Menu KPI Finance tanpa gerbang dilebur.
- [ ] **F-POS [FE]** Peta posisi: Account Receivable (ruang kerja AR; bagian penagihan tim bagi `is_supervisor`); Junior Accountant dilebur ke Senior Accountant; nama lama tetap dikenali selama peralihan.
- [ ] **F-B [FE]** Ruang kerja baru: Finance Supervisor, Tax Staff, Cost Control, Account Payable; ringkasan divisi masuk zona D.
- [ ] **F-D [manusia]** (peran yang melebihi jabatan: issue privat) Paket Pajak untuk posisi Tax Staff; paket AP untuk posisi Account Payable; posisi Account Receivable baru (5 orang, `is_supervisor` untuk atasan, pasang paket ke posisi baru karena nama baru = kunci posisi baru); Junior Accountant: HR menetapkan posisi baru 2 orangnya; Accounting CV: paket ke posisi dan `position_key` sendiri; bersihkan paket akun Senior Accountant yang tak terkait.
- [ ] **F-X** Pemisahan tugas kas kecil dan anggaran: issue privat repo kode.

## HRGA

- [ ] **H-SG [FE]** Susunan per Artifact HRGA: Data Karyawan, Kehadiran & Cuti (Pengajuan Karyawan pindah dari Portal ke sini), Payroll (Pengaturan Gaji pindah ke sini), Disiplin & Hubungan Industrial, Rekrutmen (Pengaturan Rekrutmen pindah ke sini), Pelatihan & Penilaian (Pengaturan Pelatihan pindah ke sini; Template KPI), Budaya & Komunikasi (Program Culture empat menu jadi satu bertab), Form Builder (satu menu), Aset & Perlengkapan, Ruang & Booking, Buku Tamu & Keamanan (terlihat Security), Organisasi & Aturan. KPI, KPI Scoring, dan KPI GA satu menu (bagian U2). `/hris` keluar dari sidebar. Gerbang per daun untuk Daftar Karyawan, Jadwal, Fingerprint, menu Pengaturan, Cuti (rute tak lagi publik, tombol ubah bersyarat), Materi E-Learning, tombol buat aset. HRGA label grup, bukan nama departemen.
- [ ] **H-BE [BE]** `peranJabatanTabel`: Building Maintenance dikenali sebagai GA; hapus baris GA "leader" yang tak terpakai; HRD Supervisor atasan GA lewat label HRGA. Deploy BE sebelum FE; pemegang jabatan login ulang.
- [ ] **H-B [FE]** Ruang kerja baru: HRD Supervisor (termasuk aset dan permintaan GA), Training & Performance Officer, Culture & Industrial, Building Maintenance; Personalia, Recruitment & Onboarding, GA Staff, Security sudah ada. Ringkasan divisi HRGA di zona D.
- [ ] **H-D [manusia]** Rapikan peran yang melebihi jabatan (daftar per orang: issue privat); Training & Performance Officer: pastikan akun aktif, samakan peran, cabut paket Marketing; Building Maintenance: `position_key` sendiri; master GA: hapus GA Supervisor dan Legal Staff, putuskan Admin General Service; Office Boy: rapikan akun nonaktif.
- [ ] **H-X** Pemisahan tugas payroll (ubah gaji vs tanda tangan; penerbit slip) dan peran pengelola hak akses di luar IT: issue privat repo kode.

## Tech Development

- [ ] **T-SG [FE]** Susunan per Artifact Tech Dev: Akun & Hak Akses, Infrastruktur, Integrasi Marketplace (Setting OAuth satu menu; Gross Profit ke analitik; Ulasan ke Layanan Pelanggan; Inventories berdata tiruan dihapus), Form Builder (satu), Jejak Pengajuan. Menu KPI IT dilebur (U2). `/it` keluar dari sidebar. Gerbang per daun (Status Infrastruktur, Jaringan Kantor beraksi tercatat).
- [ ] **T-B [FE]** Ruang kerja untuk Leader, Fullstack Developer, IT Support (hari ini hanya supervisor IT).
- [ ] **T-DARURAT [FE+BE]** Akses Darurat dan riwayatnya. **Diblok** sampai SA-1 ADR 0137 diputuskan.
- [ ] **T-D [manusia]** Akun kerja tim Tech Dev turun ke hak jabatan, pengujian pakai akun uji (SA-2 ADR 0137); akun nonaktif dikosongkan; peran IT hanya di departemen Tech Development. Daftar per orang: issue privat.
- [ ] **T-X** Gerbang pengelolaan peran sistem dan pemasangan paket: issue privat repo kode.

## Kesekretariatan

- [ ] **K-SG [FE]** Susunan per Artifact Kesekretariatan: Ruang Direktur (digerbang paket Persetujuan: Direksi; Corporate Secretary tanpa tab Keuangan), Legal & Perizinan (Kontrak Vendor dan Data Pemasok baca), Registrasi & Pengembangan Produk (BOM dan Stok Bahan baca, digabung), Audit Internal. KPI Sekretariat dilebur (U2). Rute Data Pemasok membuka baca untuk Legal. Tombol tambah/hapus register Legal dan R&D digerbang izin aksi.
- [ ] **K-B [FE]** Ruang kerja: Corporate Secretary, Legal, QA RND, Internal Audit, tim kreatif.
- [ ] **K-OPS [manusia, tanpa kode]** Space Kreatif di Tugas; departemen lain mengajukan lewat Pengajuan.
- [ ] **K-ADR [analis]** ADR untuk SetaraDirektur dan Ruang Direktur, serta peleburan Legal + R&D ke Sekretariat.
- [ ] **K-D [manusia]** Paket Legal Pelaksana ke Legal dan R&D Pelaksana ke QA RND (lalu matikan cadangan tier); Direktur ke paket Persetujuan: Direksi; rapikan jabatan kosong dan akun nonaktif.
- [ ] **K-X** Independensi auditor dan gerbang halaman Ruang Direktur: issue privat repo kode.

## Manufaktur

- [ ] **P-SG [FE]** Susunan per Artifact Manufaktur: Perencanaan Produksi, Produksi, Gudang Bahan & Barang Jadi, Stok & Opname, Pengiriman Pesanan Online (Tinggar dan Sadewa satu urusan, disaring per gudang), K3 & Mutu (CAPA satu pintu), Master Data Produksi, Persetujuan & Riwayat. KPI Manufaktur dilebur (U2). `/manufacture` keluar dari sidebar. Gerbang per daun dari paket WMS; rute `/manufacture` dan `/warehouse` bergerbang. Label tanpa nama jabatan dan singkatan.
- [ ] **P-GUDANG [HR + BE + FE]** Pecah jabatan Admin Warehouse per gudang; cakupan G dari jabatan/peran gudang dan cakupan Sadewa. Penugasan per orang TBD.
- [ ] **P-B [FE]** Ruang kerja Manufaktur (delapan posisi). Produksi tampil sebagai panel jujur selama Dokumen Produksi Batch nol dokumen.
- [ ] **P-MO [BE]** Nomor Material Order dibuat server dan unik.
- [ ] **P-D [manusia]** Paket per jabatan WMS diselaraskan dengan pemisahan pembuat dan penyetuju batch (daftar: issue privat); Operator hanya laporan K3 (ADR 0043); Admin Return paket gudang online dan `position_key` sendiri; cabut peran yang tak terkait jabatan; putuskan Staff Purchasing dan Helper Packing.
- [ ] **P-X** Persetujuan koreksi stok: issue privat repo kode.

## Cara verifikasi (berlaku tiap SG/B)

- Uji pakai per jabatan dengan akun nyata atau akun uji berjabatan sama (bukan hanya supervisor), memakai skenario tab "Uji pakai" di Artifact.
- Kontrol negatif: akun tanpa paket modul itu tetap tak melihat menunya.
- `pnpm tsc --noEmit`, `pnpm lint`, `pnpm test` (dibanding baseline), `pnpm build`; i18n id+en.
