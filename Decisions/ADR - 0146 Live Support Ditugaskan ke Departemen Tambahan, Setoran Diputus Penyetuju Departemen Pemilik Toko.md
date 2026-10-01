# ADR - 0146 Live Support Ditugaskan ke Departemen Tambahan, Setoran Diputus Penyetuju Departemen Pemilik Toko

## Deskripsi

*Seorang Live Support boleh ditugaskan resmi ke **departemen tambahan** lewat daftar penugasan milik marketing-analytics, tanpa menyentuh `work_data.department`. Pilihan toko setoran karya = toko TikTok departemen aslinya ditambah departemen penugasannya, dan setiap setoran menyimpan **departemen pemilik toko** yang menentukan penyetujunya. KPI tetap menghitung setoran per orang, tidak berubah. Mengubah [[ADR - 0106 Tema dan Teaser Live Support Disetor dan Diputus Penyetuju Departemen sebagai Dasar KPI]] §8.*

- **Status**: 🟡 Diusulkan (2026-10-01). Belum ada kode.
- **Path di repo**:
  - bip-erp `services/marketing-analytics/live_support_penugasan.go` (baru), `live_support_penugasan_store.go` (baru), `karya_live_support.go`, `karya_live_support_handler.go`, `karya_live_support_store.go`, `index.go`, `routes.go`
  - erp-frontend `src/features/marketing/live-support-karya/` (pemilih toko berkelompok, kolom departemen toko), `src/features/marketing/live-support-penugasan/` (baru, layar penugasan), `src/i18n/locales/id.ts` + `en.ts`
- **Tanggal**: 2026-10-01
- **Terkait**: [[ADR - 0106 Tema dan Teaser Live Support Disetor dan Diputus Penyetuju Departemen sebagai Dasar KPI]] · [[ADR - 0110 Kesiapan Live Dinilai Lintas Departemen dan Pendukung Diisi Backend saat Tunggal]] · [[ADR - 0045 Identitas Tim Tunggal dan Peta Kepemilikan Marketing]] · [[ADR - 0063 Siaran Serentak Dicatat sebagai Sesi Terpisah per Akun]] · [[Microservices - Marketing Analytics Service]] · [[REF - Kepemilikan Data]] · [[ANALISA - Live Support Memegang Departemen Tambahan]]

## Untuk Manajemen

**Apa yang berubah di layar.** HR mencatat bahwa seorang Live Support juga memegang departemen lain (contoh pertama: Live Support Kyura yang juga memegang live Beauty Hacks). Sesudah itu, saat menyetor Tema atau Teaser, pilihan tokonya memuat toko TikTok Kyura **dan** Beauty Hacks, dikelompokkan per departemen dan bisa dicari. Setoran untuk toko Beauty Hacks muncul di antrean Tinjau Setoran **atasan Beauty Hacks**, dan hanya dia yang bisa menyetujui atau menolaknya. Setoran untuk toko Kyura tetap diputus atasan Kyura.

**Siapa yang terdampak.** Pemegang posisi Live Support (saat ini satu orang), penyetuju Beauty Hacks yang kini menerima antrean, dan staf HR yang mencatat penugasannya.

**Yang tidak dijanjikan.**
- Orangnya **tidak** pindah atau bertambah departemen di data karyawan. Presensi, jadwal, payroll, atasan langsung, dan KPI lain tetap mengikuti satu departemen aslinya.
- Target KPI Tema dan Teaser **tidak** berubah. Setoran yang disetujui dari kedua departemen dijumlahkan untuk target yang sama.
- Layar Monitoring Sesi Live belum ikut menampilkan sesi Beauty Hacks. Itu pekerjaan terpisah bila diminta.
- Berlaku untuk posisi Live Support saja, bukan aturan umum rangkap departemen.

**Perkiraan besaran kerja.** Kecil sampai sedang: satu service backend (marketing-analytics) dan satu layar web, tanpa perubahan aplikasi MyBharata. Kira-kira 2 sampai 3 hari kerja termasuk verifikasi.

## Context

Permintaan datang 2026-10-01: Live Support Kyura juga mengurus live Beauty Hacks dan tak bisa menyetor Tema dan Teaser untuk toko Beauty Hacks karena pilihan tokonya tak memuatnya. Keputusan user: (1) setoran toko Beauty Hacks diputus penyetuju Beauty Hacks, (2) dihitung ke KPI orang yang sama, (3) orangnya dicatat resmi memegang dua departemen.

Diukur di kode (`origin/main` bip-erp 2026-10-01) dan prod (baca saja, 2026-10-01):

1. **Penghalangnya satu: tahap setor.** `GET /live-support/toko` dan validasi `POST /live-support/karya` memakai header `BIP-Department` (`karya_live_support_handler.go`, `handleTokoKarya`, `handleSetorKarya` → `tokoDipilih`), dan `tokoKaryaDepartemen` mencocokkan `department_shops.department` persis. Header itu satu string dari `work_data.department`, diterbitkan saat login dan ditimpa gateway.
2. **KPI sudah netral departemen.** `/kpi/karya-live-support` menyaring `{employee_id, periode}` saja (`kpi_karya_live_support.go`, `DaftarKaryaMilik`); komentar kodenya menyatakan itu disengaja. Kebutuhan (2) sudah terpenuhi oleh kode yang ada.
3. **Penyetuju sudah mengikuti field `department` setoran, bukan departemen peninjau.** Antrean menanyakan penyetuju per `k.Department` dan `bolehPutus` membandingkan dengan penyetuju `k.Department` (`handleAntreanKarya`, `handleKeputusanKarya`). Yang membuatnya selalu Kyura adalah isi field itu, yang dicap dari header penyetor.
4. **Tak ada konsep satu karyawan dua departemen di seluruh sistem.** `WorkData.Department` tunggal (`shared-library/models/employee/models.go`), nol hasil `git grep` untuk `additional_department`, `secondary_department`, `departemen_tambahan`. `supervised_departments` adalah cakupan supervisi antar-departemen untuk supervisor, bukan keanggotaan staf. Rangkap jabatan masih TBD di [[HRIS - Organization Structure]] § Belum Diputuskan.
5. **Preseden**: keputusan user 2026-09-18, "posisi Live Support ditugaskan lintas departemen", dicatat [[ADR - 0110 Kesiapan Live Dinilai Lintas Departemen dan Pendukung Diisi Backend saat Tunggal]]. ⚠️ ADR itu berstatus 🟡 (PR terbuka saat ditulis), jadi yang dipakai di sini keputusannya, bukan kodenya.
6. **Data prod**: pemegang posisi Live Support **satu** orang (`BIP-0240-05-26`, `work_data.department` Kyura). `department_shops` channel TIKTOK: **Beauty Hacks 38 toko, Kyura 17**, departemen lain nol. Beauty Hacks punya satu `is_supervisor: true`, jadi rantai `atasanDepartemen` menemukan penyetuju. `live_support_karya` per 2026-09-18 berisi 0 dokumen (jumlah terkini belum diukur ulang).
7. **ICC mapping tak bisa dipakai ulang** sebagai pengikat orang ke toko: `tiktok_shop_id` unik di antara mapping aktif (`icc_mapping_repo.go`) dan maknanya penanggung jawab laba toko, sehingga baris Live Support akan mencemari atribusi itu.

## Decision

1. **Penugasan departemen tambahan disimpan di marketing-analytics**, koleksi baru `live_support_penugasan`: satu dokumen per `{company_id, employee_id}` berisi `departemen_tambahan[]`, `diubah_oleh`, `diubah_pada`. Departemen asli dari `work_data.department` **tidak** disalin ke situ; ia tetap dibaca dari header. Alasan pemiliknya marketing-analytics: satu-satunya konsumen adalah setoran karya, dan [[REF - Kepemilikan Data]] tetap menyatakan keanggotaan departemen milik employee. Penugasan ini wewenang kerja, bukan keanggotaan.
2. **`work_data.department`, klaim JWT, dan header tidak diubah.** Opsi departemen kedua di data karyawan ditolak: header membawa satu departemen untuk seluruh service, rangkap belum diputuskan, dan [[ADR - 0045 Identitas Tim Tunggal dan Peta Kepemilikan Marketing]] serta [[ADR - 0063 Siaran Serentak Dicatat sebagai Sesi Terpisah per Akun]] sengaja mengatribusikan omzet ke satu departemen per orang.
3. **Pilihan toko = toko TikTok departemen asli ∪ departemen tambahan**, dibaca dari `department_shops` lewat pembaca bercache yang sudah ada. Tiap toko di respons membawa `department` pemiliknya.
4. **Setoran menyimpan `department_toko`**: departemen pemilik toko saat setor, diturunkan server dari `department_shops`, tak pernah dari body. Field `department` tetap berarti departemen penyetor (riwayat).
5. **Penyetuju = penyetuju `department_toko`** di antrean dan keputusan. Setoran lama tanpa `department_toko` jatuh ke `department` (perilaku ADR 0106). Guard setoran sendiri, gagal-tertutup 502, dan supervisor IT lihat-saja tetap.
6. **Validasi toko saat setor dan kirim ulang** memakai himpunan departemen yang sah **saat itu** (asli ∪ tambahan). Kirim ulang yang tokonya berasal dari penugasan yang sudah dicabut ditolak **400** dengan pesan yang menyebut penugasannya, bukan "toko bukan milik departemenmu".
7. **Yang mengubah penugasan: staf HRIS ke atas dan supervisor IT**, lewat satu layar web. Penugasan bukan izin peran, jadi tidak menambah `system_roles` atau paket izin. Mencabut penugasan tak menyentuh setoran yang sudah tersimpan.
8. **KPI tidak berubah.** `karya_live_support` tetap menghitung per orang; target tetap dari template KPI (asumsi, lihat § Consequences).

## Consequences

### Yang membaik

- Live Support bisa menyetor untuk toko departemen yang benar-benar ia pegang, dan pekerjaan Beauty Hacks diputus atasan Beauty Hacks yang memang tahu pekerjaannya.
- Penugasannya tercatat resmi dengan siapa yang mengubah dan kapan, tanpa rangkap departemen yang belum diputuskan.

### Yang memburuk atau tetap terbuka

- ⚠️ **Asumsi: target KPI tetap.** Setoran Kyura dan Beauty Hacks dijumlahkan untuk target yang sama (minimal 10 tema, 10 teaser). Bila manajemen ingin target naik untuk orang yang memegang dua departemen, itu perubahan template KPI, bukan perubahan kode ini.
- ⚠️ **Field `department` setoran kini punya saudara bermakna lain.** `department` = penyetor, `department_toko` = penentu penyetuju. Pembaca yang mengelompokkan antrean per `department` akan menaruh setoran Beauty Hacks di bawah Kyura. Layar Tinjau dan antrean pusat ([[ADR - 0114 Antrean Persetujuan Terpusat di Web, Satu Tabel Seragam dari Agregator Employee-Service]]) wajib menampilkan `department_toko`.
- ⚠️ **Pilihan toko membesar dari 17 jadi 55 toko** untuk orang ini, jadi pemilihnya wajib berkelompok per departemen dan bisa dicari.
- ⚠️ **Gerbang menu Tinjau Setoran** sudah memuat supervisor/admin `beauty_hacks` (ADR 0106 § Consequences), jadi penyetuju Beauty Hacks yang punya peran itu langsung melihat menunya. Penyetuju tanpa peran itu tetap kena cacat cermin longgar yang sama dengan ADR 0106.
- **Monitoring Sesi Live** ([[ADR - 0108 Monitoring Sesi Live di Web Hanya Baca untuk Leader dan Live Support]]) masih menyaring Live Support ke toko departemen header. Penugasan ini bisa dipakai ulang di sana nanti, tetapi tidak termasuk keputusan ini.
- **Deploy**: kontrak berubah (field baru di respons toko dan setoran), jadi marketing-analytics **lebih dulu**, baru erp-frontend. Koleksi dan index baru lahir saat boot. Tidak ada env baru dan tidak ada kategori inbox baru.

### Yang sengaja tidak dilakukan

- **Departemen kedua di `work_data`** atau klaim JWT (lihat Decision §2).
- **Memakai ICC mapping** sebagai pengikat Live Support ke toko (lihat Context §7).
- **Membuka seluruh toko TikTok untuk setiap Live Support** tanpa penugasan. Itu lebih murah, tetapi tidak mencatat siapa memegang apa, dan pemegang posisi berikutnya akan melihat toko yang bukan tugasnya.

## Dokumen Terkait

- [[Microservices - Marketing Analytics Service]] § Setoran karya Live Support · [[API - Marketing Analytics Service]] § Setoran karya Live Support
- [[ANALISA - Live Support Memegang Departemen Tambahan]] (daftar task)
- [[REF - Kepemilikan Data]] · [[HRIS - Organization Structure]] · [[HRIS - Matriks KPI per Departemen]] § Kyura → Live Support
