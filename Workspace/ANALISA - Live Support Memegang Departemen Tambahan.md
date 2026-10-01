## Deskripsi

*Pecahan kerja untuk [[ADR - 0146 Live Support Ditugaskan ke Departemen Tambahan, Setoran Diputus Penyetuju Departemen Pemilik Toko]]. Bukan rencana per berkas; tiap butir cukup jelas untuk langsung dilempar ke `/start-task`. Cara kerjanya di [[Microservices - Marketing Analytics Service]] § Setoran karya Live Support → Departemen tambahan Live Support.*

- **Status**: 🟡 Belum dikerjakan (2026-10-01).
- **Tanggal**: 2026-10-01
- **Pemicu**: Live Support Kyura (`BIP-0240-05-26`) juga mengurus live Beauty Hacks dan tak bisa menyetor Tema/Teaser untuk toko Beauty Hacks.

## Backend (bip-erp, marketing-analytics)

**T1. Koleksi `live_support_penugasan` + rute baca/tulis.**
Satu dokumen per `{company_id, employee_id}`: `departemen_tambahan[]`, `diubah_oleh`, `diubah_pada`. Index unik `{company_id, employee_id}`. Rute: daftar penugasan perusahaan (untuk layar admin) dan ganti penugasan satu orang. Tulis digerbang **staf HRIS ke atas atau supervisor IT**. Validasi: departemen tambahan wajib nama departemen yang punya baris `department_shops` channel TIKTOK (tolak 400 bila tidak, supaya penugasan tak bisa mengarah ke departemen tanpa toko), tak boleh memuat departemen asli orangnya, tanpa duplikat. Field disimpan lewat daftar-izin eksplisit seperti `dokumenKarya`.
*Tergantung*: tidak ada.

**T2. Pilihan toko dan validasi setor memakai himpunan departemen sah.**
Himpunan = header `BIP-Department` ∪ `departemen_tambahan` milik pemanggil. `GET /live-support/toko` mengembalikan toko TikTok seluruh himpunan, tiap toko membawa `department`. `POST` dan `PATCH` setoran memvalidasi toko terhadap himpunan **saat itu**, lalu mencap `department_toko` dari `department_shops`, bukan dari body. Kirim ulang yang tokonya berasal dari penugasan yang sudah dicabut: 400 dengan pesan yang menyebut penugasannya. `department` tetap departemen penyetor. Penugasan tak terbaca (Mongo galat) = 503, bukan "tanpa tambahan" (jangan diam-diam menyempitkan pilihan).
*Tergantung*: T1.

**T3. Penyetuju mengikuti `department_toko`.**
Antrean (`handleAntreanKarya`) dan keputusan (`handleKeputusanKarya`/`bolehPutus`) memakai `department_toko`, jatuh ke `department` bila kosong (setoran lama). Respons antrean membawa `department_toko`. Test wajib: setoran Beauty Hacks oleh penyetor Kyura muncul HANYA di antrean penyetuju Beauty Hacks, penyetuju Kyura dapat 403 saat memutusnya, setoran lama tanpa field tetap diputus penyetuju Kyura, dan guard setoran sendiri tetap berlaku. Satu test lewat `app.Test` untuk jalur galat.
*Tergantung*: T2 (field `department_toko` lahir di sana).

## Frontend (erp-frontend)

**T4. Pemilih toko berkelompok dan bisa dicari, kolom departemen toko.**
Dialog Setor: toko dikelompokkan per `department` dan bisa dicari (55 toko untuk pemegang dua departemen). Tabel Setor dan halaman Tinjau menampilkan **departemen toko**, bukan departemen penyetor. Teks `tokoKosong` disesuaikan karena kini bisa kosong walau ada penugasan. Semua teks baru lewat `t()` di `id.ts` dan `en.ts`.
*Tergantung*: T2, T3. Deploy sesudah marketing-analytics.

**T5. Layar penugasan departemen tambahan Live Support.**
Daftar pemegang posisi Live Support beserta departemen asli dan tambahan, aksi ubah lewat `Sheet` berangka tiga (header tetap, badan menggulir, footer aksi). Menu hanya untuk staf HRIS ke atas dan supervisor IT, cermin gerbang server. Struktur tabel HRIS. Umpan balik sesudah simpan menyebut bahwa pilihan toko orang itu langsung berubah (tak perlu login ulang, karena penugasan dibaca per permintaan, bukan dari token).
*Tergantung*: T1.

## Verifikasi dan pemasangan

**T6. Verifikasi lewat gateway DEV, lalu siapkan perintah PROD untuk manusia.**
Di DEV: tetapkan penugasan Beauty Hacks ke akun uji Live Support; `GET /live-support/toko` memuat toko Beauty Hacks; setor ke toko Beauty Hacks → muncul di antrean penyetuju Beauty Hacks, **tidak** di antrean penyetuju Kyura; setujui → `/kpi/karya-live-support` orang itu bertambah satu; cabut penugasan → pilihan toko kembali ke Kyura saja. Bandingkan **bentuk** respons, bukan status 200. PROD: deploy marketing-analytics lalu `frontend-hris`, dijalankan manusia (skill `deploy-bip-erp` §0). Sesudahnya HR mencatat penugasan Beauty Hacks untuk `BIP-0240-05-26` lewat layar T5.
*Tergantung*: T1 sampai T5.

## Di luar lingkup (dicatat supaya tak diusulkan ulang tanpa keputusan)

- Monitoring Sesi Live ([[ADR - 0108 Monitoring Sesi Live di Web Hanya Baca untuk Leader dan Live Support]]) memakai penugasan yang sama. Bisa jadi task lanjutan bila diminta.
- Antrean persetujuan pusat ([[ADR - 0114 Antrean Persetujuan Terpusat di Web, Satu Tabel Seragam dari Agregator Employee-Service]]) menampilkan departemen toko untuk kategori `live_support`. Tergantung irisan 2 agregator.
- Target KPI khusus untuk pemegang dua departemen (perubahan template KPI, bukan kode).
