# ADR - 0167 Izin HRIS Dipecah per Fitur dengan Cadangan Peran per Fitur

> **Status**: 🟢 **Diterima**, 2026-10-10, oleh irfanarfianto (diusulkan 2026-10-10). Kode belum ada; pekerjaan di bip-erp#2941 dan sub-issue-nya. Aturan persetujuan ADR di [[ADR - 0151 Issue Siap Dikerjakan Agent Bila Keputusannya Bisa Ditunjuk, Ditandai Manusia]].

## Untuk Manajemen

**Apa yang berubah di layar.** Hak akses HRIS bisa diberikan per fitur (data karyawan, kontrak, mutasi, resign, surat peringatan, presensi, cuti), tidak lagi satu paket untuk semuanya. Setelah semua tahap selesai, IT bisa memasang ke tiap jabatan HR hanya fitur yang dikerjakannya, sehingga misalnya staf rekrutmen tidak lagi membuka presensi atau pengaturan organisasi.

**Siapa yang terdampak.** Pada tahap pertama tidak ada yang merasakan perubahan hak: hak setiap akun sesudah pemecahan harus sama persis dengan sebelumnya. Satu perubahan yang terlihat: dua orang HR (Culture & Industrial dan Recruitment & Onboarding) akan melihat menu kontrak, mutasi, resign, dan presensi yang hari ini sudah bisa mereka akses lewat sistem tetapi tidak tampil di menu. Penyempitan hak per jabatan baru dilakukan di tahap terakhir, jabatan demi jabatan, dan setiap penyempitan itu disengaja serta dicatat.

**Apa yang tidak dijanjikan.**

- Pekerjaan ini sendiri tidak mengurangi apa yang dilihat siapa pun. Ia membuat pengurangan itu mungkin.
- Fitur HRIS yang hari ini masih diatur lewat peran (data pribadi karyawan, pengaturan organisasi, jadwal kerja, dokumen HRD, pengumuman) belum ikut dipecah.
- Tombol tambah dan ubah di layar HRIS yang hari ini tidak dijaga tidak ikut dijaga di pekerjaan ini.
- Tidak ada tanggal selesai di dokumen ini.

**Perkiraan besaran kerja.** Tiga pekerjaan (dua di backend, satu di web), satu langkah penyalaan sakelar di produksi oleh manusia, lalu penyempitan per jabatan yang dikerjakan sesuai kebutuhan HR.

## Deskripsi

*Katalog izin modul `hris` dipecah dari tiga izin umum (`hris.view`, `hris.work`, `hris.manage`) menjadi pasangan lihat dan kelola per fitur, dengan cadangan peran lama yang dinilai per fitur, bukan per modul. Langkah pertamanya netral: paket yang ada dipetakan ke izin baru yang setara, sehingga hak setiap akun tidak berubah dan dibuktikan dengan alat banding dari [[ADR - 0164 Hak Akses Satu Pintu, Peran Dibawa Paket Hak dan Dirakit saat Token Terbit]]. Penyempitan per jabatan baru mungkin setelah cadangan peran `hris` dimatikan.*

- **Status**: 🟡 Diusulkan (lihat baris status di atas).
- **Path di repo** (yang AKAN disentuh): `bip-erp/shared-library/common/catalog_hris.go` · `bip-erp/services/employee/hris_gate.go` · `bip-erp/services/attendance/hris_gate.go` · `bip-erp/services/employee/{contract,contract_summary,contract_pkwt_handler,mutasi_routes,resign,account_status_backlog,warning,warning_file,compliance_note,compliance_violation_type,karyawan_masuk,main}.go` · `bip-erp/services/attendance/main.go` · `bip-erp/scripts/hris-paket-setara/` (baru) · `erp-frontend/src/components/layout/sidebar-menus.tsx` · `erp-frontend/src/utils/menu-permission.ts` · `erp-frontend/src/app/(main)/hris/vacation/page.tsx` · `erp-frontend/src/components/layout/sidebar-gerbang-hrga.test.ts`
- **Tanggal**: 2026-10-10

## Context

**Pemicu.** Staf HR membuka fitur yang bukan tugasnya (jawaban pemilik produk, 2026-10-10). Sebabnya struktural, diukur di `origin/main` 2026-10-10:

- Katalog `hris` hanya berisi `hris.view`, `hris.work`, `hris.manage`, dua izin pengajuan, dan `hris.divisi.view` (`shared-library/common/catalog_hris.go`).
- Di web, `hris.manage` menggerbangi 12 menu (atasan langsung, kontrak, mutasi, resign, jadwal, kehadiran, fingerprint, cuti, laporan kehadiran, ulang tahun, pengaturan organisasi, pengaturan kepegawaian), `hris.work` 3 menu (surat peringatan, pengumuman, dokumen HRD), `hris.view` 2 menu (`erp-frontend/src/components/layout/sidebar-menus.tsx`).
- Peran `hris` tingkat apa pun memberi ketiga izin umum sama rata (`HrisTierDefault`, `catalog_hris.go:153-158`).

**Menu dan gerbang backend tidak sejalan.** Di backend, kontrak, mutasi, resign, surat peringatan, dan catatan kepatuhan dibaca dengan `hris.view` dan ditulis dengan `hris.work` (`gateHris` di `services/employee`), sedangkan menunya di web digerbang `hris.manage`. `hris.manage` di backend hanya dipakai `POST`/`DELETE /holiday`. Menu cuti digerbang `hris.manage`, tombol ubah kuotanya `hris.work`. Tombol tulis lain di layar HRIS tidak digerbang sama sekali.

**Cadangan peran mati per modul.** Gerbang `hris` memakai izin di token bila token memuat satu saja izin `hris.*`, dan baru jatuh ke peran bila tidak ada (`catalog_hris.go:286-293`). Akibatnya satu paket `hris` yang sempit mencabut seluruh hak `hris` yang datang dari peran. Ini sudah terjadi di produksi: Recruitment & Onboarding (peran `hris: staff`, paket `hris_lihat`) dan Culture & Industrial (peran `hris: staff`, paket `hris_pelaksana`) memegang lebih sedikit dari perannya (sensus 2026-10-10). Pola cadangan per area sudah dipakai finance untuk insentif (`shared-library/common/gerbang_insentif.go:100-118`).

**Siapa yang memegang hak HRIS hari ini** (produksi `employee_db`, baca saja, 2026-10-10; ukur ulang sebelum dipakai):

- 8 akun aktif memegang izin `hris` lewat paket; enam di antaranya memegang `hris.manage`.
- 14 akun aktif memegang peran `hris`; enam di antaranya tanpa paket `hris` sama sekali (Direktur, Corporate Secretary, Internal Audit, IT Support, satu Fullstack Developer, satu staf Finance Percetakan), sehingga mendapat ketiga izin dari peran.

**Batas yang ditemukan.** Empat pembaca di service employee mencocokkan `hris.view` persis di dalam handler (`compliance_note.go:324`, `:807`, `warning.go:319`, `warning_file.go:127`). Migrasi saat service menyala hanya menambah izin ke paket ber-key bawaan dan tidak pernah menghapus (`services/employee/selaras_izin_paket.go`). Validasi paket menolak izin di luar katalog. Lompatan internal dari orchestrator HRIS ke attendance tidak membawa izin, sehingga gerbang di sana hanya menilai peran.

**Status pijakan.** [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] Implemented. [[ADR - 0164 Hak Akses Satu Pintu, Peran Dibawa Paket Hak dan Dirakit saat Token Terbit]] masih 🟡 Diusulkan; keputusan ini memakai aturan kesamaan hak dan alat bandingnya, jadi bergantung pada pekerjaan yang belum ada kodenya. [[ADR - 0149 Sidebar Satu Daftar Urusan, Menu Digerbang Izin Posisi, Beranda Ruang Kerja Posisi]] berjalan untuk HRGA dan tidak memecah izin `hris`.

## Decision

**1. Pasangan lihat dan kelola per fitur.** Izin umum diganti izin per fitur dengan prefiks tetap `hris.`:

| Fitur | Lihat | Kelola |
|---|---|---|
| Data karyawan (BPJS, analisis, karyawan masuk) | `hris.karyawan.view` | `hris.karyawan.manage` |
| Kontrak dan PKWT | `hris.kontrak.view` | `hris.kontrak.manage` |
| Mutasi | `hris.mutasi.view` | `hris.mutasi.manage` |
| Resign dan akun nonaktif | `hris.resign.view` | `hris.resign.manage` |
| Surat peringatan, catatan kepatuhan, jenis pelanggaran | `hris.sp.view` | `hris.sp.manage` |
| Presensi (entri, laporan, koreksi, hari libur) | `hris.presensi.view` | `hris.presensi.manage` |
| Cuti dan kuota | `hris.cuti.view` | `hris.cuti.manage` |

Izin pengajuan dan `hris.divisi.view` tidak berubah. Fitur yang hari ini digerbang peran (data pribadi karyawan, pengaturan organisasi, jadwal, dokumen HRD, pengumuman) tidak mendapat izin di pekerjaan ini.

**2. Pemetaan dari gerbang backend yang berlaku.** Tiap rute yang hari ini memakai `hris.view` beralih ke izin lihat fiturnya; yang memakai `hris.work` ke izin kelola fiturnya; `POST`/`DELETE /holiday` (`hris.manage`) ke `hris.presensi.manage`. Dua `GET` PKWT yang hari ini memakai `hris.work` beralih ke `hris.kontrak.manage`. Empat pembaca di dalam handler ikut beralih ke izin lihat fiturnya.

**3. Menu mengikuti backend.** Menu sebuah fitur tampil bagi pemegang izin lihat fitur itu; tombol ubah kuota cuti bagi pemegang `hris.cuti.manage`. Karena `hris.work` hari ini membuka tulis kontrak, mutasi, resign, dan surat peringatan, izin kelola keempat fitur itu dipegang paket Pelaksana, bukan hanya Admin.

**4. Pemetaan paket yang ada, setara.**

- `hris_lihat`: semua izin lihat.
- `hris_pelaksana`: semua izin lihat, ditambah izin kelola untuk semua fitur kecuali `hris.presensi.manage` (hari ini paket ini tidak memegang `hris.manage`, satu-satunya pemakai `hris.manage` di backend adalah hari libur). Koreksi presensi (`PATCH /:id/update`, hari ini `hris.work`) memakai izin tersendiri `hris.presensi.koreksi` supaya pemetaan ini tetap setara; izin itu ikut dipegang Pelaksana dan Admin.
- `hris_admin` dan paket buatan tangan `personalia`: semua izin baru.
- Peran `hris` tingkat apa pun (cadangan): semua izin baru, sama seperti hari ini mendapat ketiga izin umum.

**5. Cadangan peran per fitur.** Gerbang menilai cadangan per fitur: bila token memuat izin sebuah fitur, izin token dipakai untuk fitur itu; bila tidak, fitur itu dinilai dari peran. Izin umum lama yang masih ada di token dibaca sebagai payung: `hris.view` setara semua izin lihat, `hris.work` setara semua izin kelola kecuali `hris.presensi.manage`, `hris.manage` setara `hris.presensi.manage`. Tabel cadangan di web mengikuti aturan yang sama, dan setiap izin baru wajib punya entrinya.

**6. Izin lama ditahan sementara.** `hris.view`, `hris.work`, dan `hris.manage` tetap terdaftar di katalog (supaya paket tersimpan yang masih memuatnya tetap bisa disunting) dan tetap dibaca sebagai payung. Pencabutannya pekerjaan terpisah, sesudah semua paket tersimpan dipetakan dan token lama habis (72 jam).

**7. Kesamaan dibuktikan.** Langkah netral (butir 1 sampai 6) hanya boleh dinyalakan di sebuah lingkungan bila alat banding melaporkan selisih nol per akun, dengan payung dibuka menjadi izin barunya. Satu selisih yang diterima sadar: menu web bagi pemegang paket Lihat atau Pelaksana bertambah sesuai butir 3, karena gerbang backend-nya sudah terbuka bagi mereka.

**8. Penyempitan sesudah fase dua.** Cadangan per fitur menjaga hak, tetapi juga membuat fitur di luar paket seseorang tetap terbuka selama ia memegang peran `hris`. Karena itu penyempitan per jabatan baru dikerjakan setelah:
1. setiap pemegang peran `hris` memegang paket yang setara dengan perannya;
2. cadangan peran `hris` dimatikan (fase dua, sakelar yang sudah ada), dijalankan manusia, dengan perubahan hak dibekukan selama itu dan tidak tumpang tindih dengan pemindahan data [[ADR - 0164 Hak Akses Satu Pintu, Peran Dibawa Paket Hak dan Dirakit saat Token Terbit]].

Setiap penyempitan per jabatan adalah perubahan hak yang disengaja dan dicatat di issue-nya.

**Alternatif yang ditolak.**

- *Cadangan per modul*: setiap paket fitur yang dipasang sebelum fase dua mencabut hak HRIS lain tanpa galat; dua kasusnya sudah ada di produksi.
- *Menyembunyikan menu per jabatan tanpa memecah izin*: API tetap terbuka, dan katalog menu terbatas menjadi daftar halaman, yang ditolak [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]].
- *Izin kelola hanya untuk Admin (mengikuti menu hari ini)*: mencabut hak tulis yang hari ini dimiliki paket Pelaksana lewat API.

## Consequences

- ➕ HR bisa diberi hak per fitur, dan menu web akhirnya sejalan dengan gerbang backend.
- ➕ Paket fitur yang dipasang sebelum fase dua tidak lagi mencabut hak HRIS lain.
- ➖ Izin bertambah dari 6 menjadi 18 di modul `hris`, ditambah tiga izin payung yang ditahan sementara.
- ➖ Dua tahap tambahan (paket setara dan fase dua) harus selesai sebelum manfaat utamanya, penyempitan, bisa dirasakan.
- ⚠️ **Dua akun melihat menu lebih banyak** (Culture & Industrial, Recruitment & Onboarding). Keduanya kasus paket sempit yang perlu dirapikan sebelum fase dua.
- ⚠️ **Lompatan internal dari orchestrator HRIS ke attendance tidak membawa izin.** Setelah fase dua, rute attendance yang dicapai lewat lompatan itu (koreksi presensi, hari libur) akan menolak semua orang kecuali lompatannya membawa izin. Ini harus dibereskan sebelum fase dua.
- ⚠️ **Paket ber-key bawaan diselaraskan ulang tiap service menyala.** Izin baru otomatis masuk ke paket bawaan yang tersimpan; paket buatan tangan (`personalia`) harus dipetakan oleh skrip.
- ⚠️ **Urutan deploy**: backend sebelum web. Menyalakan fase dua menuntut container employee dan attendance dibuat ulang, dan nilainya diperiksa di container.

## Belum Diputuskan (TBD)

- Izin untuk fitur HRIS yang masih digerbang peran (data pribadi, pengaturan organisasi, jadwal, dokumen HRD, pengumuman). Ambang perannya berbeda-beda (sebagian hanya supervisor, sebagian meloloskan IT), jadi memindahkannya mengubah hak dan butuh keputusan sendiri.
- Apakah tombol tulis di web yang hari ini tanpa gerbang ikut digerbang izin kelola.
- Kapan izin payung dicabut dari katalog.

## Dokumen Terkait

- [[CORE - RBAC dan Permission Set]] · [[Microservices - Employee Service]] · [[Microservices - Attendance Service]] · [[APP - Web ERP]]
- [[ADR - 0164 Hak Akses Satu Pintu, Peran Dibawa Paket Hak dan Dirakit saat Token Terbit]] · [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] · [[ADR - 0149 Sidebar Satu Daftar Urusan, Menu Digerbang Izin Posisi, Beranda Ruang Kerja Posisi]]
