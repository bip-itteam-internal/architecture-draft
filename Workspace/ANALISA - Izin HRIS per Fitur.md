# ANALISA - Izin HRIS per Fitur

> **Menunggu [[ADR - 0167 Izin HRIS Dipecah per Fitur dengan Cadangan Peran per Fitur]] Diterima: sebelum itu ANALISA ini BUKAN keputusan yang bisa ditunjuk `/brief`.**

- **Keputusan**: [[ADR - 0167 Izin HRIS Dipecah per Fitur dengan Cadangan Peran per Fitur]] (ðŸŸ¡ Diusulkan, 2026-10-10)
- **Dok domain**: [[CORE - RBAC dan Permission Set]]
- **Pemutus**: irfanarfianto
- **Ukuran**: **Besar**. Dua repo harus berubah (`bip-erp` dua PR, `erp-frontend` satu PR). `my-bharata` tidak dihitung: aplikasi tidak membaca klaim izin sama sekali (pembacaan peran hanya dari respons login, `lib/src/features/auth/data/implements/auth_implements.dart:66-72`, `origin/dev`).
- **Dibuat**: 2026-10-10 oleh `/analisa-kebutuhan`, tanpa label `Siap Agent`.

## Urutan

| Urut | Issue | Repo | Judul |
|---|---|---|---|
| induk, tanpa PR sendiri | bip-erp#2941 | `bip-erp` | Izin HRIS dipecah per fitur |
| 1 | bip-erp#2942 | `bip-erp` | [BE] Katalog izin HRIS per fitur, cadangan per fitur, gerbang beralih (bagian 1/2) |
| 2, deploy sesudah BE 1/2 | erp-frontend#2289 | `erp-frontend` | [FE] Menu HRIS dan tombol cuti ke izin per fitur |
| 3, lalu fase dua hris oleh manusia | bip-erp#2943 | `bip-erp` | [BE] Paket hris setara untuk pemegang peran, lompatan ke attendance membawa izin (bagian 2/2) |

## Langkah manusia

1. Sesudah BE 1/2 terpasang: jalankan alat banding (bip-erp#2934) di produksi; selisih yang boleh hanya bertambahnya menu bagi pemegang paket Lihat atau Pelaksana.
2. Rapikan dua kasus paket sempit (Recruitment & Onboarding, Culture & Industrial) sebelum fase dua.
3. Sesudah BE 2/2: jalankan skrip paket setara (uji coba dulu), lalu nyalakan `HRIS_TIER_FALLBACK=off` di employee dan attendance (container dibuat ulang, nilainya diperiksa di container), lalu alat banding sekali lagi.
4. Penyempitan per jabatan: satu issue per jabatan, tiap issue menyebut fitur yang dicabut.

## Draf issue

### Izin HRIS dipecah per fitur

Repo tujuan: `bip-erp` Â· Urutan: induk, tanpa PR sendiri Â· https://github.com/bip-itteam-internal/bip-erp/issues/2941

**Pemutus:** @irfanarfianto
**PIC:** belum ditetapkan

#### Masalah

Staf HR membuka fitur yang bukan tugasnya, karena katalog izin `hris` hanya punya tiga izin umum: `hris.manage` membuka 12 menu, `hris.work` 3, `hris.view` 2. Menu web dan gerbang backend juga tidak sejalan (kontrak, mutasi, resign, SP ditulis dengan `hris.work` di backend tetapi menunya digerbang `hris.manage`), dan satu izin `hris.*` di token mematikan cadangan peran untuk seluruh modul (`shared-library/common/catalog_hris.go:286-293`).

#### Keputusan

ADR "Izin HRIS Dipecah per Fitur dengan Cadangan Peran per Fitur" (vault `architecture-draft`, folder Decisions). Layak `Siap Agent` sesudah ADR itu berstatus Diterima (saat issue ini dibuat masih Diusulkan).

Bentuknya, ringkas:
- Pasangan lihat/kelola per fitur: karyawan, kontrak, mutasi, resign, sp, presensi (+ `hris.presensi.koreksi`), cuti. Prefiks tetap `hris.`.
- Langkah pertama netral: paket yang ada dipetakan setara, cadangan peran dinilai per fitur, izin lama dibaca sebagai payung.
- Penyempitan per jabatan baru sesudah paket setara terpasang dan fase dua `hris` dinyalakan.

#### Yang harus benar

- [ ] Ketiga sub-issue merged.
- [ ] Di produksi, alat banding (bip-erp#2934) melaporkan selisih nol sesudah langkah netral, kecuali bertambahnya menu bagi pemegang paket Lihat atau Pelaksana yang memang diputuskan.
- [ ] Sesudah fase dua, memasang paket satu fitur ke sebuah jabatan hanya membuka fitur itu.

#### Di luar cakupan

- Fitur HRIS yang masih digerbang peran (data pribadi, pengaturan organisasi, jadwal, dokumen HRD, pengumuman).
- Menggerbangi tombol tulis web yang hari ini tanpa gerbang.
- Mencabut izin payung `hris.view`/`work`/`manage` dari katalog.
- Penyempitan per jabatan (dikerjakan per issue sesudah fase dua).

#### Data / bukti pendukung

Produksi `employee_db`, baca saja, 2026-10-10 (ukur ulang sebelum dipakai):
- 8 akun aktif memegang izin `hris` lewat paket; 6 di antaranya memegang `hris.manage`.
- 14 akun aktif memegang peran `hris`; 6 tanpa paket `hris` sama sekali (Direktur, Corporate Secretary, Internal Audit, IT Support, satu Fullstack Developer, satu staf Finance Percetakan).
- Paket sempit: Recruitment & Onboarding (peran `hris: staff`, paket `hris_lihat`) dan Culture & Industrial (peran `hris: staff`, paket `hris_pelaksana`) memegang lebih sedikit dari perannya.

#### Prasyarat

Issue ini induk tanpa PR sendiri. Urutan: BE 1/2, FE 1/1, BE 2/2, lalu perapian dua kasus paket sempit dan penyalaan fase dua `hris` oleh manusia. Alat banding bip-erp#2934 dibutuhkan untuk membuktikan langkah netral.

### [BE] Katalog izin HRIS per fitur, cadangan per fitur, gerbang beralih (bagian 1/2)

Repo tujuan: `bip-erp` Â· Urutan: 1 Â· https://github.com/bip-itteam-internal/bip-erp/issues/2942

**Pemutus:** @irfanarfianto
**PIC:** belum ditetapkan

#### Masalah

Gerbang `hris` hanya mengenal tiga izin umum, dan cadangan perannya mati untuk seluruh modul begitu token memuat satu izin `hris.*` (`shared-library/common/catalog_hris.go:286-293`). Akibatnya hak tidak bisa diberikan per fitur, dan paket sempit mencabut hak dari peran.

#### Keputusan

ADR "Izin HRIS Dipecah per Fitur dengan Cadangan Peran per Fitur" (vault `architecture-draft`, folder Decisions), Decision butir 1, 2, 4, 5, 6. Layak `Siap Agent` sesudah ADR itu berstatus Diterima (saat issue ini dibuat masih Diusulkan).

Bentuknya: katalog `hris` mendapat izin lihat/kelola per fitur ditambah `hris.presensi.koreksi`; rute `gateHris` dan empat pembaca di handler beralih ke izin fiturnya; cadangan peran dinilai per fitur; izin lama tetap terdaftar dan dibaca sebagai payung.

#### Yang harus benar

- [ ] Katalog `hris` memuat 15 izin fitur baru, izin pengajuan dan `hris.divisi.view` tidak berubah, dan `hris.view`/`hris.work`/`hris.manage` tetap terdaftar.
- [ ] Setiap rute yang hari ini `gateHris(PermHrisView, ...)` beralih ke izin lihat fiturnya; `PermHrisWork` ke izin kelola fiturnya; `PATCH /:id/update` ke `hris.presensi.koreksi`; `POST`/`DELETE /holiday` ke `hris.presensi.manage`; dua `GET` PKWT ke `hris.kontrak.manage`. Ada uji tabel rute yang mengunci pemetaan ini.
- [ ] Pembaca di `compliance_note.go:324`, `:807`, `warning.go:319`, `warning_file.go:127` memakai izin lihat fiturnya.
- [ ] Payung: token berisi `hris.view` lolos semua izin lihat; `hris.work` lolos semua izin kelola kecuali `hris.presensi.manage`; `hris.manage` lolos `hris.presensi.manage`. Ada ujinya.
- [ ] Cadangan per fitur: token yang hanya memuat izin satu fitur tetap mendapat fitur lain dari peran `hris`. Ada uji untuk kasus Recruitment & Onboarding (`hris.view` + peran staff).
- [ ] Peran `hris` tingkat apa pun memberi semua izin fitur baru.
- [ ] Paket bawaan dipetakan: `hris_lihat` semua lihat; `hris_pelaksana` semua lihat + semua kelola kecuali `hris.presensi.manage`, + `hris.presensi.koreksi`; `hris_admin` semuanya.
- [ ] Uji kesetaraan: untuk setiap kombinasi peran `hris` dan paket bawaan, himpunan rute yang boleh diakses sebelum dan sesudah sama persis.
- [ ] Sakelar `HRIS_TIER_FALLBACK` dan `HRIS_PERMISSION_ENFORCEMENT` tetap berlaku seperti sekarang.

#### Di luar cakupan

- Rute HRIS yang masih digerbang peran.
- Mencabut izin lama dari katalog.
- Web (sub-issue FE).

#### Data / bukti pendukung

Produksi `employee_db`, baca saja, 2026-10-10 (ukur ulang sebelum dipakai):
- 8 akun aktif memegang izin `hris` lewat paket; 6 di antaranya memegang `hris.manage`.
- 14 akun aktif memegang peran `hris`; 6 tanpa paket `hris` sama sekali (Direktur, Corporate Secretary, Internal Audit, IT Support, satu Fullstack Developer, satu staf Finance Percetakan).
- Paket sempit: Recruitment & Onboarding (peran `hris: staff`, paket `hris_lihat`) dan Culture & Industrial (peran `hris: staff`, paket `hris_pelaksana`) memegang lebih sedikit dari perannya.

#### Prasyarat

Tidak ada untuk kodenya. Penyalaan di produksi menunggu alat banding bip-erp#2934. Bagian 1/2.

### [FE] Menu HRIS dan tombol cuti ke izin per fitur

Repo tujuan: `erp-frontend` Â· Urutan: 2, deploy sesudah BE 1/2 Â· https://github.com/bip-itteam-internal/erp-frontend/issues/2289

**Pemutus:** @irfanarfianto
**PIC:** belum ditetapkan

#### Masalah

Menu HRIS digerbang tiga izin umum yang tidak sejalan dengan backend: kontrak, mutasi, resign, cuti, presensi, laporan, jadwal, fingerprint digerbang `hris.manage`, padahal backend membuka bacaannya dengan `hris.view`. Tombol ubah kuota cuti memakai `hris.work`.

#### Keputusan

ADR "Izin HRIS Dipecah per Fitur dengan Cadangan Peran per Fitur" (vault `architecture-draft`, folder Decisions), Decision butir 3 dan 5. Layak `Siap Agent` sesudah ADR itu berstatus Diterima (saat issue ini dibuat masih Diusulkan).

Bentuknya: menu fitur HRIS digerbang izin lihat fiturnya, tombol ubah kuota cuti digerbang `hris.cuti.manage`, tiap izin baru punya entri cadangan `hrisStaffPlus`, dan izin lama tetap diterima sebagai payung.

#### Yang harus benar

- [ ] Menu Kontrak, Promosi & Mutasi, Resign, Surat Peringatan, Kehadiran, Laporan Kehadiran, Cuti digerbang izin lihat fiturnya masing-masing; Daftar Karyawan dan Bagan Organisasi tetap `hris.view` atau `hris.karyawan.view`.
- [ ] Menu yang tidak punya fitur di ADR (atasan langsung, jadwal, fingerprint, ulang tahun, pengumuman, dokumen, pengaturan organisasi dan kepegawaian) tidak berubah gerbangnya.
- [ ] Tombol ubah kuota cuti digerbang `hris.cuti.manage`.
- [ ] Setiap izin baru punya entri di tabel cadangan; uji "tiap perm punya entri FALLBACK" tetap hijau.
- [ ] Token berisi izin lama (`hris.view`/`work`/`manage`) tetap membuka menu yang sama seperti pemetaan payung di backend.
- [ ] Uji persona di `sidebar-gerbang-hrga.test.ts` diperbarui: HRD Supervisor, Personalia, Training melihat menu yang sama seperti sebelum; Culture & Industrial dan Recruitment & Onboarding mendapat menu fitur yang dibuka backend (perubahan yang diputuskan ADR).
- [ ] Komentar basi di `vacation/page.tsx:27-28`, `proxy.ts:42-45`, `menu-permission.ts:306` dibetulkan.
- [ ] Semua teks baru lewat i18n di `id.ts` dan `en.ts`.

#### Di luar cakupan

- Menggerbangi tombol tulis yang hari ini tanpa gerbang.
- `proxy.ts` (berbasis peran, tidak berubah).

#### Data / bukti pendukung

Produksi `employee_db`, baca saja, 2026-10-10 (ukur ulang sebelum dipakai):
- 8 akun aktif memegang izin `hris` lewat paket; 6 di antaranya memegang `hris.manage`.
- 14 akun aktif memegang peran `hris`; 6 tanpa paket `hris` sama sekali (Direktur, Corporate Secretary, Internal Audit, IT Support, satu Fullstack Developer, satu staf Finance Percetakan).
- Paket sempit: Recruitment & Onboarding (peran `hris: staff`, paket `hris_lihat`) dan Culture & Industrial (peran `hris: staff`, paket `hris_pelaksana`) memegang lebih sedikit dari perannya.

#### Prasyarat

Sub-issue BE bagian 1/2 merged dan terpasang di dev. Deploy sesudah BE.

### [BE] Paket hris setara untuk pemegang peran, lompatan ke attendance membawa izin (bagian 2/2)

Repo tujuan: `bip-erp` Â· Urutan: 3, lalu fase dua hris oleh manusia Â· https://github.com/bip-itteam-internal/bip-erp/issues/2943

**Pemutus:** @irfanarfianto
**PIC:** belum ditetapkan

#### Masalah

Penyempitan hak HRIS per jabatan baru berlaku setelah cadangan peran `hris` dimatikan (fase dua). Itu hanya aman bila setiap pemegang peran `hris` sudah memegang paket yang setara, dan bila jalur ke attendance yang hari ini hanya membawa peran ikut membawa izin.

#### Keputusan

ADR "Izin HRIS Dipecah per Fitur dengan Cadangan Peran per Fitur" (vault `architecture-draft`, folder Decisions), Decision butir 8. Layak `Siap Agent` sesudah ADR itu berstatus Diterima (saat issue ini dibuat masih Diusulkan).

Bentuknya: skrip yang dijalankan MANUSIA (uji coba bawaan, cadangan, pembatalan, pola `scripts/hrga-perbaikan-peran`) memasang paket `hris` setara peran ke setiap pemegang peran `hris` yang belum punya; lompatan internal orchestrator HRIS ke attendance membawa izin.

#### Yang harus benar

- [ ] Bawaannya uji coba; tanpa tanda terapkan tidak ada yang ditulis.
- [ ] Setiap akun aktif yang memegang peran `hris` dan tidak memegang paket `hris` mendapat paket setara perannya; mode terapkan menolak berjalan bila alat banding melaporkan selisih yang bukan nol.
- [ ] Paket buatan tangan `personalia` dipetakan ke izin baru yang setara.
- [ ] Lompatan orchestrator HRIS ke attendance (`PATCH /:id/update`, `POST`/`DELETE /holiday`) membawa izin pemanggil, dan ada uji bahwa dengan cadangan peran mati jalur itu tetap lolos bagi pemegang paket yang berhak.
- [ ] Idempoten, ada cadangan dan perintah pembatalan.
- [ ] Laporan uji coba mencantumkan akun yang akan dipasangi dan selisih hak per akun.

#### Di luar cakupan

- Menyalakan fase dua (manusia).
- Penyempitan per jabatan.
- Merapikan dua kasus paket sempit (dikerjakan di perapian paket terpisah).

#### Data / bukti pendukung

Perlu ukur prod: daftar akun aktif yang memegang peran `hris` tanpa paket `hris`, menurut peran yang BERLAKU (tersimpan ditambah turunan jabatan), dari alat banding bip-erp#2934. Angka di bawah dihitung dari peran tersimpan.

Produksi `employee_db`, baca saja, 2026-10-10 (ukur ulang sebelum dipakai):
- 8 akun aktif memegang izin `hris` lewat paket; 6 di antaranya memegang `hris.manage`.
- 14 akun aktif memegang peran `hris`; 6 tanpa paket `hris` sama sekali (Direktur, Corporate Secretary, Internal Audit, IT Support, satu Fullstack Developer, satu staf Finance Percetakan).
- Paket sempit: Recruitment & Onboarding (peran `hris: staff`, paket `hris_lihat`) dan Culture & Industrial (peran `hris: staff`, paket `hris_pelaksana`) memegang lebih sedikit dari perannya.

#### Prasyarat

Bagian 1/2 merged dan terpasang. Jendela pemasangan tidak boleh tumpang tindih dengan pemindahan data ADR "Hak Akses Satu Pintu, Peran Dibawa Paket Hak dan Dirakit saat Token Terbit" (bip-erp#2936). Bagian 2/2.
