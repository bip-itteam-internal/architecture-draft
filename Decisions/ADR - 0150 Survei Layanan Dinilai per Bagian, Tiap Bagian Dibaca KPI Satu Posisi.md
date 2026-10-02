# ADR - 0150 Survei Layanan Dinilai per Bagian, Tiap Bagian Dibaca KPI Satu Posisi

> **Status**: 🟢 **Diterima**, 2026-10-02, nol kode. Diputuskan user (Tech Development) dalam sesi kerja: survei "Penilaian Layanan Tech Development" disusun ulang jadi bagian per posisi, dan nilai Bagian "Aplikasi ERP dan MyBharata" menjadi sumber otomatis metrik KPI Fullstack Developer "Penilaian Layanan Tech Development" (bobot 0,2). Nomor 0150 diklaim saat push; bila sudah terpakai, geser ke nomor bebas berikutnya.

%% Vault ini PUBLIK. Nama orang dan employee_id tidak ditulis; yang disebut hanya form, posisi, departemen, dan angka agregat. %%

## Untuk Manajemen

**Masalahnya.** Survei kepuasan layanan IT menilai IT Support dan Fullstack Developer sekaligus dalam satu angka. Dari total bobot 21 di form yang berjalan, hanya 3 yang murni menilai IT Support, 6 murni Fullstack, dan 12 campuran yang tidak bisa dibagi, karena responden tidak ditanya urusannya soal jaringan atau soal aplikasi. Angka itu karena itu tidak layak dipakai menilai salah satu posisi: Fullstack ikut turun karena Wi-Fi, IT Support ikut turun karena keluhan fitur ERP.

**Yang diputuskan.** Pertanyaannya dipisah ke bagian yang masing-masing hanya menilai satu posisi (Bagian A "Jaringan dan Perangkat" untuk IT Support, Bagian B "Aplikasi ERP dan MyBharata" untuk Fullstack). Sistem menghitung satu nilai per bagian tiap bulan, dan template KPI posisi membaca bagian miliknya.

**Yang diterima sadar.** Survei menilai tim, bukan orang: semua Fullstack Developer mendapat nilai yang sama untuk metrik ini.

## Deskripsi

*Indeks layanan departemen (`metric_key: service_index`) diperluas dari satu angka per form menjadi juga satu angka per BAGIAN (field bertipe `section`), memakai perhitungan yang sama. Pemetaan bagian ke posisi ditulis di konfigurasi otomatis template KPI, bukan di form.*

- **Tanggal**: 2026-10-02
- **Diukur ke**: bip-erp `origin/main` (`services/form-builder`, `services/employee`), data PROD baca-saja 2026-10-02.
- **Hubungan dengan dok lain**:
  - [[Microservices - Form Builder Service]]: indeks layanan departemen (`service_index.go`) dan indeks layanan tim (`service_team_index.go`).
  - [[HRIS - Matriks KPI per Departemen]] § Fullstack Developer dan § IT Support.
  - [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]]: employee-service boleh menarik angka dari service lain selama tetap pemilik tunggal `kpi_score`.
  - [[ADR - 0142 Pengisi Penilaian dan Survei Selalu Anonim, IT Membuka Identitas lewat Jalur Audit Bercatatan]]: berlaku untuk form ini, tidak saling bergantung.

## Context

**Mekanisme yang ada (terverifikasi di kode).**

- Form survei bertanda `metric_key: service_index` diringkas jadi satu indeks 0..100 per periode oleh `hitungIndeks(fields, responses)` (`services/form-builder/service_index.go`), fungsi murni yang memakai aritmatika `skor_gabungan.go`. Pertanyaan berskala berbobot 0 tidak ikut dihitung dan dilaporkan terpisah sebagai pembanding.
- Angka itu hanya terbuka lewat `GET /me/service-index`, bergerbang cakupan supervisi pemanggil, dan konsumennya satu: kartu Ringkasan IT di erp-frontend. **Tidak ada sumber KPI yang membacanya.**
- Susunan pertanyaan form berulang tersimpan per periode (`models_period.go` `Fields`; dibaca `loadReadFields`), jadi menyunting form berlaku untuk periode berikutnya dan tidak mengubah periode yang sedang berjalan.
- Pola sumber KPI yang membaca form-builder sudah ada: `indeks_layanan_tim` / `nilai_layanan_pribadi` (`services/employee/kpi_sumber_indeks_layanan_tim.go`) memanggil `/internal/service-team-index`, untuk form PENILAIAN per orang.

**Keadaan PROD 2026-10-02.**

- Form "Penilaian Layanan Tech Development": tipe survei, berulang bulanan (dibuka tanggal 25), pemilik Tech Development, responden 11 departemen lain. Jawaban: 172 (periode 2026-08), 160 (2026-09).
- Template KPI `Fullstack` memuat metrik "Penilaian Layanan Tech Development" bobot 0,2 **tanpa** konfigurasi otomatis.
- Template KPI `IT Support` belum punya metrik untuk survei ini.

## Decision

1. **Satu bagian, satu posisi.** Form disusun ulang jadi 16 pertanyaan: pembuka (tidak dipetakan), **Bagian A "Jaringan dan Perangkat"** (4 pertanyaan berskala, untuk IT Support), **Bagian B "Aplikasi ERP dan MyBharata"** (5 pertanyaan berskala + 1 teks, untuk Fullstack Developer), "Masalah yang Tidak Dilaporkan" dan penutup (tidak dipetakan). Pertanyaan yang dulu campur dipecah jadi versi jaringan/perangkat dan versi aplikasi. Dua pertanyaan soal penanganan tiket (mudah melapor, dapat kabar perkembangan) dibuang karena sudah dinilai CSAT tiket yang menjadi metrik KPI sendiri; memasukkannya lagi menghitung hal yang sama dua kali. Perubahan isi dilakukan pemilik form lewat layar Form Builder dan berlaku mulai periode berikutnya.
2. **Nilai per bagian dihitung di form-builder dengan rumus yang sama.** Bagian = rentang pertanyaan sesudah sebuah field `section` sampai `section` berikutnya. Nilai bagian adalah `hitungIndeks` atas pertanyaan bagian itu saja; tidak ada rumus kedua di service mana pun.
3. **Pemetaan bagian ke posisi tinggal di template KPI.** Sumber KPI baru di employee-service membaca nilai satu bagian; bagian mana yang dibaca ditulis di konfigurasi otomatis metrik. Form tidak mengenal posisi.
4. **Bagian yang tak ditemukan adalah galat, bukan nol dan bukan kosong.** Bila konfigurasi menyebut bagian yang tidak ada pada susunan periode itu (mis. judul bagian diganti sehingga key-nya berubah), metrik dilaporkan gagal hitung dengan pesan yang menyebut bagiannya. Periode tanpa jawaban di bagian itu dilaporkan sebagai belum ada nilai, bukan nol.
5. **Nilainya tingkat departemen.** Semua pemegang posisi menerima angka yang sama.

## Consequences

- Fullstack Developer mendapat metrik otomatis ketiga; IT Support bisa menyusul dengan menambah metrik di templatenya (bobot dan asalnya belum diputuskan).
- Judul Bagian A dan B menjadi bagian dari kontrak dengan KPI: menggantinya memutus metrik sampai konfigurasinya disesuaikan. Butir 4 membuat putusnya terlihat, bukan senyap.
- Periode 2026-08 dan 2026-09 memakai susunan lama yang campur, jadi nilai per bagiannya tidak sebanding dengan periode sesudah perubahan. Target awal sebaiknya diambil dari periode pertama dengan susunan baru.

## Pertanyaan terbuka

- Target metrik Fullstack (dan IT Support bila ditambahkan).
- Cara penyunting template memilih bagian: daftar bagian di katalog sumber bersifat dinamis (isi form), sedangkan katalog hari ini statis. Diputuskan di implementasi, dengan syarat penyunting tidak perlu mengetik key mentah dan menyimpan template lewat layar tidak membuang pilihan itu.

## Dokumen Terkait

- [[Microservices - Form Builder Service]]
- [[HRIS - Matriks KPI per Departemen]]
- [[HRIS - Otomasi Skor KPI]]
- [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]]
