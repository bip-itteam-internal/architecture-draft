## Untuk Manajemen

- **Yang berubah di layar**: menu dan halaman **Sesi Live Host** di web ERP (Marketing, alamat `/marketing-analytics/live-shift`) dihapus. Host mencatat sesi live (Mulai, Jeda, Akhiri) hanya lewat MyBharata. Membuka alamat lamanya menampilkan halaman "tidak ditemukan", dan halaman Analisis Live tidak lagi menautkan ke sana.
- **Siapa terdampak**: host live dan live support yang masih membuka web untuk mencatat sesi, dan leader marketing yang memakai halaman itu untuk melihat sesi berjalan serta riwayat per sesi seluruh tim. Ringkasan kinerja per host tetap ada di Analisis Live dan di panel Performa Tim Host Live ICC. Tidak menyentuh backend, skor KPI, maupun MyBharata.
- **Tidak dijanjikan**: tidak ada lagi layar web yang menampilkan riwayat per sesi seluruh tim, dan tidak ada lagi jalan bagi leader untuk mencatat sesi atas nama host. Tombol Ambil alih versi web yang direncanakan ADR 0088 batal.
- **Besaran kerja**: kecil. Hanya erp-frontend (penghapusan), tanpa backend dan tanpa migrasi data. Deploy hanya `frontend-hris`.

## Deskripsi

*Pencatatan sesi live oleh host kini hanya punya satu klien, MyBharata. Halaman Sesi Live Host di web ERP beserta menunya dihapus karena host mencatat sesinya lewat MyBharata, sehingga web tidak perlu jalur kedua. Keputusan ini mencabut bagian web dari [[ADR - 0063 Siaran Serentak Dicatat sebagai Sesi Terpisah per Akun]] §5 dan §6 serta bagian web dari [[ADR - 0088 Ambil Alih Sesi Live oleh Host Terjadwal dan Tutup Otomatis Akhir Shift]].*

- **Status**: ⚠️ **Diputuskan, di PROD** (2026-09-11, keputusan user). Kodenya di erp-frontend [#1540](https://github.com/bip-itteam-internal/erp-frontend/pull/1540), merged 2026-09-11 20:02 WIB, **di PROD sejak 2026-09-12** (image `frontend-hris` 07:35 WIB dibangun dari HEAD yang memuat merge-nya). Cek layar di DEV maupun PROD belum dijalankan, dan tidak tercatat apakah prasyarat deploy PROD (host aktif sudah memakai build MyBharata yang memuat Sesi Live) dipastikan lebih dulu.
- **Path di repo**: erp-frontend `src/app/(main)/marketing-analytics/live-shift/page.tsx` dan `src/features/marketing-analytics/components/live-shift/` (dihapus) · `src/features/marketing-analytics/hooks/use-live-shift.ts` (tinggal `usePerformaHost`) · `src/features/marketing-analytics/constants/izin.ts` (`sesiLive` dan `bolehSesiLive` dibuang) · `src/components/layout/sidebar-menus.tsx` · `src/features/marketing-analytics/components/analisis-live/blok-kinerja-host.tsx` dan `tautan-analisis-live.tsx`
- **Tanggal**: 2026-09-11

## Context

### Dua klien untuk satu pencatatan

Sampai keputusan ini, sesi live dicatat lewat dua klien yang memanggil endpoint yang sama (`/live-shifts*` di [[Microservices - Marketing Analytics Service]]):

| | Web ERP (dihapus) | MyBharata |
|---|---|---|
| Gerbang tampil | `insentive: host_live` ATAU leader marketing (`bolehSesiLive`) | host saja |
| Mulai, Jeda, Akhiri | ada; Jeda/Akhiri mengikuti `boleh_kelola` dari backend | ada |
| Pilih toko dan akun | beberapa akun dari beberapa toko dalam satu dialog | pemilih toko, akun (`GET /live-shifts/akun`), dan co-host di `origin/dev` |
| Mencatat atas nama host lain | leader memilih host dari daftar | tidak ada |
| Sesi berjalan | milik sendiri; leader seluruh tim | milik sendiri, beberapa sesi serentak (`origin/dev`) |
| Riwayat | tabel 30 hari, porsi per host, badge tutup otomatis dan perlu koreksi; leader seluruh tim | riwayat milik sendiri |

Fitur Sesi Live di MyBharata ada di `origin/dev` (1.16.0+160) dan tidak ada di `origin/main` (1.14.5+135, commit terakhir 2026-08-03). `main` MyBharata bukan penanda rilis, jadi dari repo tidak bisa dipastikan apakah build yang terpasang di HP setiap host sudah memuatnya.

### Pengukuran produksi 2026-09-11

| Ukuran | Angka |
|---|---|
| Sesi tercatat | 74 sejak 2 September, oleh 9 host; rutin 21 sampai 25 sesi per hari sejak 9 September |
| Sesi yang dicatat oleh orang yang bukan host-nya (hanya mungkin lewat dialog leader di web) | **1**, tanggal 2 September, sebelum pemakaian sungguhan |
| Beberapa akun dimulai host yang sama dalam 20 detik (penanda dialog multi-akun web) | 1 kali |
| Sesi Shopee | 0 |
| Klien pencatat (web atau MyBharata) | **tidak terukur**: tidak ada field yang menyimpannya (`dibuat_oleh` hanya ID orang), dan log API-Gateway maupun Marketing-Analytics-Service tidak mencatat request |

Dua kemampuan yang hanya ada di web, mencatat atas nama host dan memulai beberapa akun sekaligus, praktis tidak dipakai.

## Decision

1. **Halaman dan menu Sesi Live Host di web ERP dihapus.** Alamat lama tidak dialihkan; ia jatuh ke `src/app/not-found.tsx` yang sudah ada.
2. **Pembaca performa dipertahankan.** `usePerformaHost` (`GET /live-shifts/performa`) tetap dipakai blok kinerja host Analisis Live dan panel Performa Tim Host Live ICC. Dua kunci i18n `marketing.liveShift.perluKoreksi` dan `marketing.liveShift.durasiEfektif` tetap ada karena dipinjam panel ICC, dijaga `panel-performa-host-live-i18n.test.ts`.
3. **Izin frontend `marketing.sesi-live.work` dan `bolehSesiLive` dibuang.** Host live yang hanya punya `insentive: host_live` tidak lagi mendapat kategori MARKETING di sidebar web; leader marketing tetap mendapatnya lewat `bolehTim`.
4. **Tautan dari Analisis Live ke halaman itu dibuang**, di kepala blok kinerja host dan di kartu tautan dasar halaman.
5. **Backend tidak berubah.** Endpoint `/live-shifts*` tetap melayani MyBharata, dan gerbang `RequireLiveShiftUser` tetap meloloskan leader marketing lewat API walau tak ada lagi layar yang memakainya.

### Yang dicabut dari keputusan lain

- [[ADR - 0063 Siaran Serentak Dicatat sebagai Sesi Terpisah per Akun]] §5 (klien menampilkan seluruh sesi): kini hanya berlaku untuk MyBharata. §6 (visibilitas): pembukaan riwayat per sesi seluruh tim untuk leader di web dicabut; leader membaca kinerja per host lewat ringkasan di Analisis Live dan ICC.
- [[ADR - 0088 Ambil Alih Sesi Live oleh Host Terjadwal dan Tutup Otomatis Akhir Shift]]: T3 (tombol Ambil alih dan label riwayat di web) batal. Badge alasan tutup otomatis di riwayat web (§1, erp-frontend #1539, tayang di PROD 2026-09-11) ikut hilang bersama halamannya; label riwayat "Diambil alih oleh" dan "Ditutup otomatis: shift berakhir" (§4) kini hanya milik MyBharata.

## Consequences

### Yang membaik

- Satu klien pencatatan. Aturan klien yang lahir dari bentuk data service (opsi akun berkunci toko dan akun, kegagalan sebagian tak membatalkan yang lain, penolakan 409 yang menyebut pemegang) cukup dirawat di satu tempat.
- Tombol Ambil alih tidak perlu dibangun dua kali.
- Menu Marketing di web lebih ringkas, dan host live tak lagi mendapat kategori yang isinya cuma satu menu.

### Yang memburuk atau tetap terbuka

- ⚠️ **Leader tak punya lagi riwayat per sesi seluruh tim di layar mana pun.** Analisis Live dan ICC hanya ringkasan per orang, dan MyBharata hanya sesi milik sendiri. Bila rincian per sesi dibutuhkan lagi, itu keputusan baru.
- ⚠️ **Host yang belum memasang build MyBharata yang memuat Sesi Live tidak bisa mencatat sesi.** Prasyarat deploy `frontend-hris` ke PROD: host aktif sudah memakai build itu.
- **Leader tidak bisa lagi mencatat sesi atas nama host**, dan belum diperiksa apakah MyBharata memulai beberapa akun dalam satu dialog seperti web.
- **Alamat lama tidak memberi petunjuk ke MyBharata**: halaman tidak ditemukan yang umum.
- **Koreksi sesi `perlu_koreksi` tetap lewat skrip tulis DB** oleh manusia (tidak berubah). Keterangan "perlu koreksi" di Analisis Live tak lagi menyebut Sesi Live Host sebagai tempat mengoreksi, karena tempat itu memang tak pernah punya fitur koreksi.
- **Gerbang API lebih longgar dari layar yang tersisa**: `RequireLiveShiftUser` masih mengizinkan leader memanggil `POST /live-shifts`. Tidak ada UI yang memakainya; dibiarkan karena mengubahnya menyentuh MyBharata dan backend.

### Yang sengaja tidak dilakukan

- **Mengalihkan alamat lama ke Analisis Live** (user memilih halaman tidak ditemukan).
- **Memindahkan riwayat per sesi ke Analisis Live** (tidak diminta).
- **Mengubah backend atau gerbang API** (tetap dipakai MyBharata).
- **Mengganti nama `use-live-shift.ts`** yang kini hanya berisi pembaca performa: menyentuh empat pemakai tanpa mengubah perilaku.

## Dokumen Terkait

- [[ADR - 0063 Siaran Serentak Dicatat sebagai Sesi Terpisah per Akun]] (§5 dan §6 dicabut bagian web-nya)
- [[ADR - 0088 Ambil Alih Sesi Live oleh Host Terjadwal dan Tutup Otomatis Akhir Shift]] (T3 web batal)
- [[Microservices - Marketing Analytics Service]] § Pencatatan sesi live oleh host · [[API - Marketing Analytics Service]]
- [[APP - Web ERP]] · [[APP - MyBharata]]
