# ANALISA - Psikotes Multi-Jenis

Papan kerja hasil `/analisa-kebutuhan` 2026-09-10. Keputusannya di [[ADR - 0087 Katalog Tipe Psikotes Jadi Master Data, Tiga Bentuk Jawaban Tetap Kode]], cara kerjanya di [[HRIS - Bank Soal dan Paket Psikotes]]. Berkas ini berubah tiap item selesai; ia **papan kerja, bukan arsitektur**.

## Yang menghalangi sebelum kerja dimulai

- [ ] **B1. HRD menjawab legalitas item CFIT dan DISC.** Keduanya instrumen berlisensi. **Bank soal tidak boleh diisi sebelum ini dijawab.** Ini bukan pekerjaan teknis dan tidak menghalangi T0 sampai T2, tetapi **memblokir T3 ke atas**.
- [ ] **B2. Putuskan resmi mesin kandidat mana yang dipertahankan**, erp-frontend atau career-bharata. **De facto di prod sudah career portal**: `ERP_FRONTEND_URL` prod berisi alamat career portal (dibaca 2026-09-10), dan commit career-bharata `761b4ec` berjudul "pindahkan halaman tes kandidat dari ERP ke portal karir", jadi arah pemindahannya pernah dinyatakan di kode. Selama keduanya hidup, tiap bentuk jawaban berisiko dibangun dua kali; menunda keputusan ini melipatgandakan T3 dan T5. T0 sudah merasakannya: perbaikan layar 404 hanya dibuat di career portal, dan versi erp-frontend sengaja dibiarkan dengan bug 404/410 lamanya.
- [ ] **B3. HRD memutuskan pendampingan psikotes.** Tes hari ini dikerjakan mandiri tanpa pendamping dan tanpa jejak tempat pengerjaan, menyimpang dari keputusan HRD yang tercatat ("dilaksanakan staf HR langsung"). **Memblokir T3 (CFIT)**: menentukan apakah soal CFIT boleh dibuka lewat tautan publik, dan bila boleh, timernya wajib ditegakkan server. Rincian: [[ADR - 0087 Katalog Tipe Psikotes Jadi Master Data, Tiga Bentuk Jawaban Tetap Kode]] §Belum Diputuskan.
- [ ] **B4. HRD memutuskan tenggat tautan.** Tautan `pending` tidak pernah kedaluwarsa, dan kandidat yang sudah ditolak tetap bisa mengerjakan. Tidak memblokir T0 sampai T2.

## Yang bisa dikerjakan tanpa kode

- [ ] **D1. Setel ulang config Kraepelin ke permintaan HRD** (45 kolom, 30 detik per kolom, sekitar 22 menit). Rentang yang didukung sudah mencakupnya, jadi ini **penyetelan data, bukan pengembangan**. Verifikasi: terbitkan satu sesi uji dan pastikan konfigurasinya terbawa.
- [ ] **D2. Rapikan `sequence_number` babak di prod.** Terukur 2026-09-10 berisi 1, 1, 2, 3, 3, 5, 7 — dua pasang bertabrakan, dua angka bolong. Sekaligus tentukan apakah Psikotest dipindah ke posisi yang disepakati HRD (setelah Background Check) atau keputusan HRD yang diperbarui. **Tulis prod dijalankan manusia.**

## Urutan kerja

### Tahap 0 — tutup lubang yang sedang berjalan (tidak bergantung apa pun)

- [x] **T0. Laporan psikotes tersambung, dan skor artefak berhenti menyamar sebagai hasil.**
	Dua hal dalam satu task karena keduanya menjawab keluhan yang sama. Komponen laporan dan kurva kerja **sudah jadi dan sudah ada test-nya**, tetapi belum pernah di-import di berkas mana pun, sehingga HR tak punya cara membuka hasil. Bersamaan dengan itu, sesi yang berakhir `ditinggalkan` atau `kedaluwarsa` tetap menulis skor yang tak bisa dibedakan dari hasil sungguhan.
	**Bentuk perbaikan skornya diputuskan saat pengerjaan** (menahan penulisan, menandainya, atau keduanya); yang dikunci ADR adalah bahwa ini didahulukan.
	**Gerbang verifikasi:** buka laporan untuk ketiga sesi prod yang ada sebagai orang, bukan lewat `curl`, dan pastikan sesi yang terputus di kolom 1 **terlihat sebagai terputus** tanpa perlu membaca angka.
	✅ **Selesai 2026-09-11: live di prod dan lolos gerbang.** Riwayat: **2026-09-10 merged dan terverifikasi di dev** (bip-erp #1828 `6681c997` · erp-frontend #1522 `5fd30185` · career-bharata #9 `77bfafc5`), sesudah review dengan tiga temuan kritis ditutup. Bentuk yang dipilih: sesi tak-tuntas menulis Hasil Tes **tanpa skor** (`$unset`), penutup yang kalah balapan tidak menulis Hasil Tes, laporan tampil di kartu Psikotest tab Hasil Tes dengan blok "Tes terputus", badge Terputus + Kirim Ulang di tabel, header detail, dan kartu, serta layar "tautan tidak berlaku" di career portal. Di dev hari itu: biner Recruitment-Service dan bundle FE terbukti memuat kode baru; lewat gateway, sesi uji yang ditinggalkan di kolom 1 menulis Hasil Tes **tanpa skor** dan status/laporan membawa `selesai_karena`/`col_index`; sebagai HR di browser, badge Terputus mengantar ke tab Hasil Tes, blok peringatan terbaca tanpa angka, Kirim Ulang menerbitkan tautan baru yang tetap bisa disalin, dan tautan lama lalu `404`. Layar career portal tidak bisa diuji di dev (portalnya tidak ada di VM dev, dan tautan dev mengarah ke `erp-dev`), jadi layarnya ikut gerbang prod. **Gerbang prod 2026-09-11:** recruitment-service, erp-frontend, api-gateway, dan career-portal dinaikkan manusia; biner dan bundle terbukti memuat kode baru; skrip pengosongan dijalankan (kedua baris artefak kini tanpa skor); gateway prod membalas token acak `404`; layar career untuk token acak menampilkan "Tautan tes ini sudah tidak berlaku."; sebagai HR, kartu Seno terbaca "Tes terputus … setelah 3 dari 50 kolom" dengan Skor kosong, dan tabel sesuai (Izan Terputus, Hening menunggu) per konfirmasi user.

- [x] **T0a. Status massal, laporan, dan hasil tes psikotes keluar dari cache gateway.** *(tidak bergantung apa pun; lahir dari review T0 2026-09-10)*
	api-gateway meng-cache GET `/api/recruitment/*` selama 3 menit (Redis), dan tak satu pun jalur penutupan sesi (`/finish`, `/abandon`, sweep) mengosongkannya, jadi badge Terputus dan laporan bisa terlambat sampai 3 menit sesudah kandidat keluar. `/candidates/:id/test-results` ikut (keputusan 2026-09-10): kartu yang sama membacanya, barisnya ditulis penutup sesi yang sama, dan versi basinya membuat isian Skor kosong lalu tertimpa (lihat T0b). Container api-gateway ikut naik saat deploy.
	✅ **Selesai 2026-09-11: live di prod.** Riwayat: **merged (bip-erp #1832 `4ef28e21`) dan terverifikasi di dev hari itu.** Bentuk yang dipilih: entri ber-`:id` di `noCacheRoutes` yang sama, dicocokkan per segmen, sementara 13 entri prefix lama tak berubah arti (dikunci test regresi); path ketiga rute dijaga test di recruitment-service. Di dev: API-Gateway naik 38 detik sesudah merge (biner memuat `psikotes/report` dan `test-results`); lewat gateway ketiga rute tak pernah `HIT` sementara GET kontrol `HIT`, Redis 0 kunci psikotes; gerbang di bawah lolos versi dev (status `finished` + `selesai_karena: "ditinggalkan"` seketika sesudah `abandon`); sebagai HR di Chrome, badge berganti Terputus 12,6 detik sesudah kandidat keluar, tanpa reload. **Prod:** api-gateway dinaikkan manusia 2026-09-11 08.43 WIB bersama #1824 (biner `psikotes/report` 1, `recruitment/track` 0). Gerbang di bawah versi prod **tidak dijalankan** (butuh sesi uji di data prod), dan Redis prod tiap kali diukur berisi 0 kunci recruitment (tak ada yang sedang membuka layar); jadi bukti prod bersandar pada biner prod, sedangkan perilakunya terbukti di dev.
	**Gerbang:** tinggalkan satu sesi lewat career portal, lalu GET status massal lewat gateway dalam 3 menit memuat `selesai_karena` dengan header `X-Cache` bukan `HIT`. Di dev (tanpa career portal) setara lewat `abandon` di API publik, ditambah satu GET kontrol yang wajib `HIT` supaya "tanpa HIT" tidak jadi bukti kosong.

- [ ] **T0b. Menyimpan Hasil Tes dengan Skor kosong tidak lagi menimpa skor otomatis psikotes.** *(tidak bergantung apa pun; lahir dari /start-task T0a 2026-09-10)*
	`submitTestResult` menulis `score` apa adanya (`$set score: nil` bila tak dikirim), dan form Hasil Tes mengirim tanpa skor bila isiannya kosong. Skor sesi `tuntas` yang ditulis penutup sesi karena itu jadi `null` begitu HR menyimpan Pass/Fail tanpa mengisi Skor; isiannya kosong bila HR membuka kartu sebelum kandidat selesai (atau respons `/test-results` masih versi cache, ditutup T0a). **Keputusan dulu:** Skor kosong berarti "jangan diubah" atau "HR sengaja menghapus". Menyentuh recruitment-service, dan mungkin form FE.
	**Gerbang:** sesi tuntas berskor, lalu HR menyimpan Pass dengan isian Skor kosong lewat gateway; skornya tetap ada (atau terhapus hanya lewat aksi hapus yang eksplisit, sesuai keputusan).

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

- [ ] **T3. Mesin `pilihan_ganda` + bank soal teks.** *(butuh T1, B1, B2, B3)*
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
- Pola galat test yang menyesatkan, ditemukan saat T0: `beforeEach(() => spy.mockReset())` berbadan ekspresi mengembalikan spy, dan vitest memanggilnya sebagai teardown. Test jalur galat lalu merah dengan galat fixture-nya sendiri, apa pun isi kode yang diuji. Tulis `beforeEach` berbadan blok di test psikotes berikutnya.
