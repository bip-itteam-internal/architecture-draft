# ANALISA - Psikotes Multi-Jenis

Papan kerja hasil `/analisa-kebutuhan` 2026-09-10. Keputusannya di [[ADR - 0087 Katalog Tipe Psikotes Jadi Master Data, Tiga Bentuk Jawaban Tetap Kode]], cara kerjanya di [[HRIS - Bank Soal dan Paket Psikotes]]. Berkas ini berubah tiap item selesai; ia **papan kerja, bukan arsitektur**.

## Yang menghalangi sebelum kerja dimulai

- [ ] **B1. HRD menjawab legalitas item CFIT dan DISC.** Keduanya instrumen berlisensi. **Bank soal tidak boleh diisi sebelum ini dijawab.** Ini bukan pekerjaan teknis dan tidak menghalangi T0 sampai T2, tetapi **memblokir T3 ke atas**.
- [ ] **B2. Putuskan mesin kandidat mana yang menang**, erp-frontend atau career-bharata. Selama keduanya hidup, tiap bentuk jawaban dibangun dua kali. Menunda keputusan ini melipatgandakan T3 dan T5.

## Yang bisa dikerjakan tanpa kode

- [ ] **D1. Setel ulang config Kraepelin ke permintaan HRD** (45 kolom, 30 detik per kolom, sekitar 22 menit). Rentang yang didukung sudah mencakupnya, jadi ini **penyetelan data, bukan pengembangan**. Verifikasi: terbitkan satu sesi uji dan pastikan konfigurasinya terbawa.
- [ ] **D2. Rapikan `sequence_number` babak di prod.** Terukur 2026-09-10 berisi 1, 1, 2, 3, 3, 5, 7 — dua pasang bertabrakan, dua angka bolong. Sekaligus tentukan apakah Psikotest dipindah ke posisi yang disepakati HRD (setelah Background Check) atau keputusan HRD yang diperbarui. **Tulis prod dijalankan manusia.**

## Urutan kerja

### Tahap 0 — tutup lubang yang sedang berjalan (tidak bergantung apa pun)

- [ ] **T0. Laporan psikotes tersambung, dan skor artefak berhenti menyamar sebagai hasil.**
	Dua hal dalam satu task karena keduanya menjawab keluhan yang sama. Komponen laporan dan kurva kerja **sudah jadi dan sudah ada test-nya**, tetapi belum pernah di-import di berkas mana pun, sehingga HR tak punya cara membuka hasil. Bersamaan dengan itu, sesi yang berakhir `ditinggalkan` atau `kedaluwarsa` tetap menulis skor yang tak bisa dibedakan dari hasil sungguhan.
	**Bentuk perbaikan skornya diputuskan saat pengerjaan** (menahan penulisan, menandainya, atau keduanya); yang dikunci ADR adalah bahwa ini didahulukan.
	**Gerbang verifikasi:** buka laporan untuk ketiga sesi prod yang ada sebagai orang, bukan lewat `curl`, dan pastikan sesi yang terputus di kolom 1 **terlihat sebagai terputus** tanpa perlu membaca angka.

### Tahap 1 — fondasi katalog

- [ ] **T1. Katalog `psikotes_tipe` sebagai master data.**
	Koleksi + CRUD bergerbang HR + halaman pengelolaan di Pengaturan Rekrutmen. Field: nama, deskripsi, `jenis_jawaban`, punya-subtes + `subtes[]` berdurasi, punya-timer + durasi, status.
	`jenis_jawaban` adalah **daftar-izin tertutup**; tipe yang menunjuk jenis tanpa mesin **ditolak saat disimpan**, bukan gagal saat kandidat mengerjakannya.
	Pola `LookupPage` tidak cukup (bentuknya datar); cetakan yang dipakai adalah dialog template onboarding yang sudah punya baris item dinamis berfield angka. Tab baru wajib ditaruh **di ujung** daftar Pengaturan.
	**Gerbang:** simpan tipe ber-`jenis_jawaban` yang belum ada mesinnya dan pastikan ditolak dengan pesan yang terbaca.

- [ ] **T2. Paket tes + sesi multi-bagian.** *(butuh T1)*
	Koleksi `psikotes_paket` (daftar tipe berurutan, nyala/mati per tipe, total waktu **diturunkan** bukan diketik) + perluasan `psikotes_session` menjadi satu sesi berisi beberapa bagian berurutan dengan sub-progres.
	Urutan memakai **tombol naik/turun**, bukan drag-and-drop.
	⛔ Index unik `(candidate_id, round_id)` **tidak disentuh** — itu alasan paket dijalankan sebagai satu sesi.
	**Gerbang:** satu kandidat mengerjakan paket dua bagian sampai selesai lewat gateway, lalu ulangi dengan memutus di tengah bagian kedua dan pastikan ia melanjutkan dari sana, bukan mengulang dari awal.

### Tahap 2 — CFIT

- [ ] **T3. Mesin `pilihan_ganda` + bank soal teks.** *(butuh T1, B1, B2)*
	Koleksi `psikotes_item`, CRUD bergerbang HR, dan mesin penilaian benar/salah per subtes. Termasuk **dispatcher `jenis_jawaban`** yang menggantikan sepuluh titik yang sekarang memanggil Kraepelin langsung.
	Pola yang dicontek dari LMS: snapshot soal saat percobaan dimulai, **timer ditegakkan server** dari waktu mulai bukan dipercayakan klien, pencocokan jawaban lewat id soal sehingga pengacakan aman, dan kunci jawaban dibuang saat serialisasi.
	⛔ Baca lebih dulu pelajaran di LMS bahwa menyembunyikan kunci dengan tag `json:"-"` **mematikan penguraian body** sehingga seluruh kunci tersimpan nol.
	**Gerbang:** satu test per titik dispatcher yang membuktikan sesi non-Kraepelin **tidak** dinilai dengan rumus Kraepelin, plus test yang membuktikan respons endpoint kandidat tak memuat kunci jawaban.

- [ ] **T4. Soal bergambar.** *(butuh T3)*
	Unggah gambar soal dan gambar opsi ke MinIO mengikuti pola berkas kandidat, ditambah **batas ukuran dan allowlist tipe berkas yang ditulis sendiri** — unggahan recruitment saat ini tidak punya keduanya.
	**Gerbang:** unggah berkas melebihi batas dan berkas bertipe terlarang, pastikan keduanya ditolak dengan pesan terbaca, bukan tersimpan.

### Tahap 3 — DISC

- [ ] **T5. Mesin `most_least` + bank soal DISC.** *(butuh T1, B1, B2)*
	Grup empat kata sifat, pilih satu paling sesuai dan satu paling tidak sesuai, **tanpa benar/salah**, hasilnya tally empat dimensi dan grafik. Untimed, dengan teks anjuran waktu pengerjaan.
	**Gerbang:** pastikan tidak ada jalur yang memberi skor benar/salah pada tipe ini, dan grafiknya terbaca di kedua tema.

### Tahap 4 — massal

- [ ] **T6. Impor bank soal dari Excel.** *(butuh T3 dan/atau T5)*
	Cetakan yang dipakai: modal impor yang sudah ada (pemetaan kolom manual saat deteksi gagal, pratinjau sebelum simpan, baris ditolak **tetap ditampilkan** beserta sebabnya, laporan sebagian-gagal). Di BE: dry-run dengan `expected_hash` dan penolakan 409 bila berkas berubah antara pratinjau dan simpan.
	**Gerbang:** impor berkas berisi baris rusak dan pastikan barisnya ditolak satu per satu, bukan seluruh berkas.

### Penutup

- [ ] **T7. Sinkronkan dokumentasi dan peta kepemilikan data.**
	Perbarui [[HRIS - Bank Soal dan Paket Psikotes]] dari 🟡 ke status sebenarnya, tambahkan endpoint baru ke [[API - Recruitment Service]] dan rute publik baru ke [[CORE - API Master Gateway]], dan **tambahkan baris recruitment ke [[REF - Kepemilikan Data]]** — modul ini belum masuk peta sama sekali, dan `psikotes_item` wajib tercatat berbeda dari `quiz` milik LMS.

## Catatan yang jangan hilang

- Klaim tentang keadaan kode di seluruh analisis ini diuji ke **`origin/main`**, bukan checkout lokal. Checkout lokal `bip-erp` di mesin dev tertinggal 689 commit dan sempat membuat seluruh modul psikotes tampak belum ada.
- Angka prod yang mendasari tahap 0 diukur 2026-09-10: 3 sesi, nol tuntas, 2 hasil tersimpan yang keduanya artefak. **Ukur ulang sebelum dipakai** — ini keadaan yang bergerak.
- Volume puncak musiman belum pernah terjadi di sistem (prod baru 8 kandidat), jadi perilaku saat lonjakan belum teruji oleh apa pun.
