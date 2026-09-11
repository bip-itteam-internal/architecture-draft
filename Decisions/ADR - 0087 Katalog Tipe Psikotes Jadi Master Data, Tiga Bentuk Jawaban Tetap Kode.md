> **Status**: 🟡 **Diusulkan** — disetujui 2026-09-10, kode belum ada. Rincian di `## Deskripsi`.

## Untuk Manajemen

HRD bisa mengelola sendiri **daftar tipe tes** (CFIT, DISC, Kraepelin, dan tipe lain di kemudian hari), **soal-soalnya**, dan **paket tes** per posisi, tanpa menunggu developer. Kandidat menerima satu tautan, mengerjakan seluruh paket sekali duduk secara berurutan, dan sistem yang menghitung skornya. Tujuannya menghapus koreksi manual yang selama ini dikerjakan HR dengan tangan di atas lembar kertas.

**Apa yang berubah di layar:** tiga menu baru di Pengaturan Rekrutmen (Tipe Tes, Bank Soal, Paket Tes), satu halaman laporan hasil psikotes yang sekarang belum bisa dibuka sama sekali, dan halaman kandidat yang kini bisa menjalankan lebih dari satu jenis tes dalam satu tautan.

**Siapa yang terdampak:** HRD (mengelola tipe tes, soal, dan paket, lalu membaca hasil), kandidat (mengerjakan tes), dan pengguna internal lain tidak terdampak sama sekali.

**Apa yang TIDAK dijanjikan.** Empat hal, dan keempatnya sengaja:

1. **"Tanpa coding" ada batasnya.** HRD bisa menambah tipe tes baru selama **cara menjawabnya** salah satu dari tiga yang dibangun: pilihan ganda, pilih-paling-sesuai dan paling-tidak-sesuai, atau mengisi angka. Tipe tes dengan bentuk jawaban keempat — misalnya tes menggambar — tetap menuntut developer. EPPS kemungkinan besar muat di bentuk kedua, tetapi itu **belum diperiksa** dan tidak dijanjikan di sini.
2. **Sistem tidak menyimpulkan kepribadian atau IQ.** Yang dihasilkan adalah skor mentah dan grafik. Konversi ke IQ, profil, atau kesimpulan "cocok untuk posisi X" tetap penafsiran HR. Sistem juga tetap berhenti di status "menunggu keputusan", tidak pernah meluluskan atau menggugurkan kandidat sendiri.
3. **Legalitas soal bukan urusan sistem.** CFIT dan DISC adalah instrumen berlisensi. Keputusan boleh atau tidaknya item-itemnya didigitalkan dan disimpan di server perusahaan **harus diambil HRD sebelum bank soal diisi**, bukan sesudah.
4. **Tarik-lepas (drag and drop) untuk mengurutkan tes tidak dibuat.** Urutan diatur dengan tombol naik dan turun. Alasannya di bagian teknis di bawah.

**Yang belum diputuskan, dan perlu diketahui sekarang:** tes dikerjakan kandidat **sendiri, tanpa pendamping HR**, di mana saja dan kapan saja, dan tautannya **tidak punya tenggat**. Sistem hari ini tidak memeriksa siapa yang mengerjakan maupun di mana. Untuk tes kecepatan seperti Kraepelin risikonya terbatas; untuk CFIT, yang punya jawaban benar, pengerjaan di rumah tanpa pengawasan bisa dibantu orang lain. Boleh atau tidaknya itu keputusan HRD, dan **harus diambil sebelum CFIT dibangun**. Rinciannya di bagian Belum Diputuskan di bawah.

**Perkiraan besaran kerja: besar, dan dipecah empat tahap.** Tahap pertama kecil dan memperbaiki sesuatu yang sedang salah hari ini. Sebagian besar bahan sudah ada di sistem dan dipakai ulang: mesin sesi tes bertoken, kerangka layar kandidat, pembaca berkas Excel, dan pola unggah gambar. Yang benar-benar baru: tiga koleksi data, tiga menu, dan dua mesin penilaian. Perlu rilis backend lebih dulu, lalu web.

## Deskripsi

*Psikotes diperluas dari satu jenis (Kraepelin) menjadi multi-jenis. **Katalog tipe tes, bank soal, dan paket tes menjadi master data yang dikelola HRD**, sementara **bentuk jawaban tetap kode**: tiga mesin penilaian (pilihan ganda berkunci, MOST/LEAST, angka-kolom) yang menjadi kontrak antara katalog dan mesin. Paket tes dijalankan sebagai **satu sesi, satu tautan, sekali duduk berurutan**, sehingga index unik `(candidate_id, round_id)` yang sudah ada tetap sah. Menyimpang dari kalimat di [[HRIS - Psikotes Kraepelin]] yang menjanjikan "jenis tes baru cukup menambah file skoring", dengan alasan yang dicatat di bawah.*

- **Status**: 🟡 **Diusulkan**, rencana disetujui 2026-09-10; kode katalog, bank soal, dan paket belum ada. **Tahap nol (Decision 8)** dikerjakan 2026-09-10 di PR bip-erp #1828 · erp-frontend #1522 · career-bharata #9 (merged 2026-09-10: bip-erp `6681c997`, erp-frontend `5fd30185`, career-bharata `77bfafc5`; naik di dev dan terverifikasi lewat gateway hari itu; naik di prod 2026-09-11 oleh manusia dan lolos gerbang, bersama perbaikan cache gateway T0a bip-erp #1832); bentuk yang dipilih: sesi tak-tuntas menulis Hasil Tes **tanpa skor**, laporan tampil di kartu Psikotest, dan Kirim Ulang tersedia dari layar yang sama. Rincian: [[HRIS - Psikotes Kraepelin]]. Artefak kerja: `Workspace/ANALISA - Psikotes Multi-Jenis.md`
- **Path di repo**: `bip-erp/services/recruitment/psikotes_tipe*.go` (baru) · `psikotes_item*.go` (baru) · `psikotes_paket*.go` (baru) · `psikotes_jenis_jawaban.go` (baru, dispatcher) · `psikotes_selesai.go` · `psikotes_public_handlers.go` · `psikotes_hr_handlers.go` · `bip-erp/api-gateway/main.go` · `erp-frontend/src/features/hris/recruitment/psikotes/*` · `erp-frontend/src/app/(main)/pengaturan/rekrutmen/page.tsx` · `career-bharata/src/components/psikotes/*` · `career-bharata/src/lib/recruitment-api.ts` (halaman kandidat yang dipakai prod) · `erp-frontend/src/features/psikotes/*` (versi kedua, nasibnya menunggu butir 4 Belum Diputuskan)
- **Tanggal**: 2026-09-10

## Context

### Kebutuhan sebenarnya berbeda dari yang diminta

Yang diminta manajemen adalah tiga menu. Yang sakit, menurut wawancara, adalah **CFIT dan DISC masih dikerjakan di kertas lalu dikoreksi HR dengan tangan**, dan bebannya menumpuk musiman saat lowongan dibuka. "Master tipe tes yang bisa ditambah sendiri" adalah cara yang diusulkan supaya developer tidak perlu dipanggil tiap alat tes berganti; itu kebutuhan yang sah, tetapi bukan yang sedang menyakitkan. Bukti pendukung: EPPS disebut sebagai contoh, sementara ketiga tipe yang benar-benar dipakai sudah diketahui namanya semua.

Pembedaan ini menentukan urutan kerja, dan menentukan satu kalimat yang harus jujur disampaikan (butir 1 di `## Untuk Manajemen`).

### Keadaan yang terukur di prod, bukan diasumsikan

Diukur langsung di `recruitment_db` prod 2026-09-10 (baca saja):

| Yang diukur | Hasil |
|---|---|
| `psikotes_session` | **3**, dan **nol** berstatus `tuntas` |
| Sesi 1 | `kedaluwarsa` di **kolom 1** dari 30, skor tersimpan **1 (Rendah)** |
| Sesi 2 | `pending`, belum pernah dibuka |
| Sesi 3 | `ditinggalkan` di **kolom 3** dari 50, skor tersimpan **1 (Rendah)** |
| `candidate_test_result` | 2, keduanya di babak Psikotest, keduanya `score=1 result=Pending` |
| `candidate` | 8 |
| `interview_round.sequence_number` | 1, 1, 2, 3, 3, 5, 7 — **dua pasang bertabrakan, dua angka bolong** |
| `assessment_type` | 4 entri: Psikotest, Background Check, Technical Test, Phone Screening |

Dua fakta di atas bergabung menjadi cacat yang sedang berjalan: **2 dari 2 hasil tersimpan adalah artefak sesi terputus, bukan pengukuran kemampuan**, dan HR **tidak punya cara melihatnya**. Komponen `LaporanIndividual` dan `KurvaKerja` sudah jadi beserta test-nya, tetapi `git grep` membuktikan keduanya **tidak pernah di-import di berkas mana pun**; tombol "lihat laporan" hanya melempar ke halaman detail kandidat yang tidak merender laporan apa pun. Satu kandidat sudah berstatus `Psikotest / Rejected`.

Menambah dua jenis tes di atas fondasi ini melipattigakan produksi angka yang tak bisa diperiksa.

### Yang sudah ada dan dipakai ulang

- **Lapisan sesi sudah jenis-agnostik**: `Config`/`Soal`/`Hasil` bertipe bebas, token magic link, mesin status, idempotensi, sapuan kedaluwarsa, dan index. Komentarnya menyatakan ini disengaja agar jenis tes baru tidak menuntut perubahan skema bersama.
- **Kerangka layar kandidat** (sapaan, instruksi, tes, selesai, lanjut-setelah-putus, `retryFinish` berlapis) tidak terikat jenis tes.
- **Alur terurut per lowongan sudah ada sekali**: `JobPosting.AssessmentTypeIDs` harfiah "terurut", dan `Lookup.Mandatory` sudah bersemantik "otomatis masuk, tak bisa dihapus, urutan tetap bisa diubah".
- **Pembaca Excel matang di FE** (`exceljs`, `baca-sheet-excel.ts`) plus modal impor lengkap dengan pemetaan kolom manual, pratinjau, dan laporan sebagian-gagal. Di BE, pola dry-run dengan `expected_hash` dan penolakan 409 bila berkas berubah antara pratinjau dan simpan.
- **Cetakan master bersub-struktur** sudah terbukti jalan: dialog template onboarding (header + baris item dinamis, tiap baris punya field angka).

### Yang tampak bisa dipakai ulang tetapi ternyata tidak

**Form Builder ditolak.** Nol konsep kunci jawaban, nol timer pengerjaan, opsi hanya teks tanpa gambar, dan nol import. Yang paling menentukan: identitas pengisi diambil dari header gateway, sementara kandidat tidak punya akun ERP. Postur privasinya juga berlawanan arah — Form Builder sengaja menampilkan identitas responden beserta seluruh jawabannya, psikotes sengaja menyembunyikan soal dan skor di level struct. Menaruh kunci jawaban di mesin yang dirancang memamerkan jawaban adalah cara tercepat membocorkannya. Ditambah preseden: `custom_question` form-builder sudah pernah dicoba di recruitment lalu dihapus.

**Mesin quiz `services/learning` tidak dipinjam, tetapi polanya dicontek.** Learning sudah punya tes pilihan ganda berwaktu dengan kunci jawaban, snapshot soal saat percobaan dimulai, timer yang ditegakkan server dari `started_at`, pencocokan jawaban lewat id soal sehingga pengacakan aman, dan kunci jawaban yang dibuang saat serialisasi. Memakainya langsung berarti salah satu dari dua pelanggaran: menyalinnya ke recruitment melahirkan sumber kebenaran kedua untuk skoring tes, atau membuka learning untuk kandidat eksternal yang mencampur dua domain yang dipisah [[ADR - 0002 Database-per-Service]]. Yang diambil adalah **polanya**, bukan kodenya. Satu pelajaran mahal di sana wajib dibaca sebelum meniru: menyembunyikan kunci jawaban dengan tag `json:"-"` **mematikan penguraian body**, sehingga seluruh kunci tersimpan bernilai nol.

### Yang benar-benar nol

Dibuktikan `git grep` terhadap `origin/main`, bukan checkout lokal (checkout lokal repo ini tertinggal ratusan commit dan sempat menyesatkan analisis ini sendiri):

- **Nol percabangan berdasarkan `jenis`** di seluruh jalur eksekusi psikotes. Sepuluh titik pemanggilan di tiga berkas memanggil Kraepelin langsung, dan jenis sesi ditulis konstan, tidak pernah dari input HR.
- **Bentuk "kolom" tidak bisa menampung soal bergambar atau MOST/LEAST.** Jembatan penyimpanannya hanya menulis dan membaca dua kunci, sehingga apa pun di luar itu hilang senyap pada perjalanan bolak-balik.
- **Nol pustaka drag-and-drop** dan nol implementasi buatan sendiri di seluruh erp-frontend.
- **Nol entitas** bank soal, paket tes, subtes, atau tipe tes di kedua repo.
- **Nol batas ukuran dan nol allowlist tipe berkas** pada unggahan recruitment; satu-satunya pagar adalah batas body 50 MB milik service.

### Keputusan lain yang mengikat

- [[ADR - 0085 Industrial Relation Catatan Kepatuhan Ringan Terpisah dari SP dan KPI]] §3 sudah memutuskan pola yang persis dibutuhkan di sini: katalog jenis adalah **master data yang bisa diubah HR, bukan enum Go**, karena sifatnya data referensi, bukan aturan sistem.
- [[ADR - 0041 Izin Tipe Form Menempel di Departemen]] menuntut arah default ditentukan dari "apa yang rusak bila salah", dan menegaskan aturan berlaku saat sesuatu **ditetapkan**, bukan saat disunting.
- [[REF - Kepemilikan Data]] menetapkan fakta baru di domain yang sudah ada berarti koleksi baru di service pemiliknya. Ia juga mencatat recruitment **belum masuk peta sama sekali**, sehingga gerbang "cari sebelum membangun" di sini lolos lewat `git grep`, bukan lewat peta.
- Istilah **"bank soal" sudah dipakai** desain LMS People Development untuk quiz karyawan internal (nol kode, desainnya berdiri). Menurut aturan kepemilikan data itu **dua fakta berbeda, bukan salinan**, dan yang dilarang adalah membiarkan keduanya lahir tanpa ada yang tahu ada dua.

## Decision

**1. Katalog tipe tes menjadi master data, bentuk jawaban tetap kode.**
Koleksi baru `psikotes_tipe` di `recruitment_db`: nama, deskripsi, **jenis jawaban**, daftar subtes berdurasi, punya-timer, dan status aktif. HRD mengelolanya penuh tanpa deploy. Yang **tidak** menjadi data adalah cara menilai: `jenis_jawaban` adalah **daftar-izin tertutup** yang dijaga kode.

**2. Tiga bentuk jawaban, dan hanya tiga.**

| `jenis_jawaban` | Bentuk soal | Penilaian | Dipakai |
|---|---|---|---|
| `pilihan_ganda` | teks dan/atau gambar, satu kunci benar | benar/salah, skor mentah per subtes | CFIT |
| `most_least` | satu grup berisi empat kata sifat | tally empat dimensi, **tanpa benar/salah** | DISC |
| `angka_kolom` | deret digit per kolom | kecepatan, ketelitian, keajegan, ketahanan | Kraepelin (sudah ada) |

Menambah bentuk jawaban keempat **wajib lewat ADR baru**, bukan lewat menu. Ini batas yang dijanjikan ke manajemen dan harus terlihat di layar: tipe tes yang menunjuk jenis jawaban yang belum ada mesinnya **ditolak saat disimpan**, bukan gagal diam-diam saat kandidat mengerjakannya.

**3. Paket tes dijalankan sebagai SATU sesi, satu tautan, sekali duduk berurutan.**
Konsekuensinya index unik `(candidate_id, round_id)` yang sudah ada **tetap sah dan tidak disentuh**. Sub-progres per bagian disimpan di dalam sesi. Ini keputusan sadar: menjadikan tiap tipe tes satu sesi tersendiri menuntut mengganti index, dan mengganti index tidak terjadi lewat deploy — Mongo menolaknya diam-diam dan penjaganya cuma log, sehingga index lama tetap berlaku sementara build tampak sukses.

**4. Bank soal menjadi `psikotes_item` di `recruitment_db`, dan namanya sengaja dibedakan** dari `quiz` milik LMS. Barisnya ditambahkan ke [[REF - Kepemilikan Data]] pada tahap yang sama, sekaligus menutup sebagian lubang "recruitment belum masuk peta".

**5. Paket tes memakai kembali semantik yang sudah ada**: urutan dan aktif/nonaktif per tipe di dalam paket, mengikuti bentuk `AssessmentTypeIDs` yang sudah terurut dan flag `Mandatory` yang sudah bersemantik "otomatis masuk, tak bisa dihapus, urutan tetap bisa diubah". **Menonaktifkan sebuah tipe tidak boleh mengunci paket atau sesi lama yang terlanjur memakainya.**

**6. Urutan diatur dengan tombol naik dan turun, bukan drag-and-drop.** Repo belum punya satu pun pustaka DnD; menambah dependensi demi satu layar tidak sebanding, dan sudah ada dua komponen pengurut bertombol yang terbukti dipakai.

**7. Hasil tetap berhenti di `Pending`.** Sistem menghitung skor mentah dan menggambar grafik; ia tidak pernah menetapkan lolos atau gugur, tidak mengonversi ke IQ, dan tidak menyimpulkan profil. Tidak ada tabel norma yang disimpan.

**8. Tahap nol wajib didahulukan**, sebelum tipe tes apa pun ditambahkan: sambungkan laporan psikotes ke layar, dan hentikan sesi yang berakhir `ditinggalkan` atau `kedaluwarsa` dari menghasilkan skor yang tak bisa dibedakan dari hasil sungguhan. Bentuk perbaikannya diputuskan saat pengerjaan; yang dikunci di sini adalah **urutannya**, karena menambah jenis tes memperbanyak angka yang tak bisa diperiksa.

## Consequences

**Yang menjadi lebih baik**

- CFIT dan DISC berhenti dikoreksi dengan tangan. Ini kebutuhan yang sebenarnya, dan tahap 1 sampai 2 sudah menjawabnya.
- HRD mengubah nama tipe, durasi, subtes, jumlah soal, dan susunan paket tanpa menunggu rilis.
- Laporan psikotes yang selama ini menganggur menjadi terpakai, dan skor artefak berhenti menyamar sebagai pengukuran.
- Konfigurasi Kraepelin yang diminta manajemen (45 kolom, 30 detik per kolom, sekitar 22 menit) **sudah bisa dicapai hari ini tanpa satu baris kode**, karena rentang yang didukung sudah mencakupnya. Ini dikerjakan sebagai penyetelan data, bukan sebagai pekerjaan pengembangan.

**Yang menjadi lebih rumit**

- Sepuluh titik pemanggilan yang sekarang memanggil Kraepelin langsung harus melewati dispatcher. Selama transisi, salah satu jalur yang terlewat akan menilai tes DISC dengan rumus Kraepelin, dan **gagalnya tidak akan berupa galat** melainkan angka yang masuk akal. Setiap titik wajib punya test yang menguncinya.
- Gateway meng-hardcode kelima path psikotes. Endpoint publik berbentuk baru menuntut menyunting dan menaikkan gateway juga.
- Bank soal berisi kunci jawaban. Kebocorannya tidak akan terlihat sebagai galat, jadi endpoint pengelola dan endpoint kandidat wajib memakai bentuk respons yang terpisah dan diuji, mengikuti pola yang sudah ada di learning.
- Selama **dua implementasi mesin tes kandidat** masih hidup berdampingan (erp-frontend dan career-bharata), tiap bentuk jawaban baru berisiko dibangun dua kali. **Di prod pilihannya sudah terjadi de facto**: `ERP_FRONTEND_URL` di container recruitment prod berisi `https://career.bharatainternasional.com` (dibaca 2026-09-10), jadi kandidat prod mengerjakan di career portal. Keputusan resminya belum ada, dan biayanya berlipat justru karena ADR ini.

**Risiko yang diterima sadar**

- **Legalitas item CFIT dan DISC belum dijawab.** Ini risiko hukum, bukan teknis, dan berada di luar kendali sistem. Bank soal tidak boleh diisi sebelum HRD menjawabnya.
- **EPPS diasumsikan muat di `most_least`** tanpa pernah diperiksa. Bila ternyata tidak, ia menjadi bentuk jawaban keempat dan menuntut ADR baru.
- **Volume puncak musiman belum pernah terjadi di sistem** (prod baru 8 kandidat), jadi perilaku saat lonjakan belum teruji.
- **Menyimpang dari kalimat di [[HRIS - Psikotes Kraepelin]]** yang menjanjikan jenis tes baru cukup menambah file skoring. Kenyataannya nol titik ekstensi tersedia, sehingga janji itu diganti dengan janji yang lebih kecil dan bisa ditepati: **bentuk jawaban** yang menjadi titik ekstensi, bukan jenis tes.
- **Generalisasi lebih dulu dari pemakai ketiga.** Prinsip tim melarangnya, dan repo ini sudah membayar sekali lewat kapabilitas template form yang berakhir tanpa konsumen. Penyimpangan diterima karena ketiga pemakainya sudah konkret dan bernama, bukan diandaikan.

**Konsekuensi rilis**

- **Backend sebelum frontend**, ini perubahan kontrak.
- Koleksi baru tidak menuntut env baru. Bila kelak ditambah env (misalnya batas ukuran gambar soal), container wajib dibuat ulang, bukan sekadar dimulai ulang.
- Menaikkan recruitment-service saja **tidak cukup** bila ada endpoint publik baru: gateway ikut naik.
- Bila tahap nol ditambahi pemberitahuan "hasil siap dinilai", itu **kategori inbox baru**, dan service pengirim beserta notification-service wajib naik bersama.

## Belum Diputuskan (TBD)

Ditemukan sesudah ADR ini disetujui, saat menelusuri apa yang sebenarnya dialami kandidat (2026-09-10, diverifikasi ke `origin` dan ke prod). Keempatnya keputusan HRD atau produk, bukan pekerjaan developer, dan butir 1 **memblokir tahap CFIT**.

1. **Pendampingan.** Psikotes yang terbangun dikerjakan kandidat sendiri lewat tautan tanpa login: tidak ada langkah HR memulai tes, identitas hanya dikonfirmasi lewat satu klik, dan BE tidak mencatat IP maupun perangkat. Itu menyimpang dari keputusan HRD yang tercatat di [[HRIS - Recruitment]] ("dilaksanakan & dicatat staf HR langsung"). Untuk Kraepelin risikonya terbatas karena tes kecepatan sulit dibantu orang lain. Untuk **CFIT**, yang berkunci jawaban, pengerjaan jarak jauh tanpa pengawasan membuka jalan bagi orang lain mengerjakan atau membantu, dan aturan butir 3 tidak mencegah orang kedua di perangkat lain. Pilihannya: boleh jarak jauh dengan risiko diterima tertulis, wajib diawasi di kantor, atau campuran per tipe tes. **Bila CFIT boleh jarak jauh, timernya wajib ditegakkan server.** Hari ini batas waktu per kolom hanya ditegakkan browser: server menerima kiriman kolom kapan saja selama sesi berjalan, dan jam satu-satunya di server adalah sapuan ketidakaktifan 6 × detik per kolom.
2. **Tenggat tautan.** `issued_at` hanya dicatat dan ditampilkan, tak pernah dibandingkan dengan waktu apa pun, sehingga tautan yang belum dibuka berlaku selamanya. Halaman kandidat juga tidak memeriksa status kandidat: yang sudah ditolak atau mengundurkan diri tetap bisa mengerjakan, dan hasilnya tetap tertulis ke Hasil Tes.
3. **Aturan "halaman tersembunyi = tes berakhir".** Versi career portal mengakhiri sesi **seketika** begitu halaman tersembunyi (pindah tab, peramban diminimalkan, layar ponsel terkunci, telepon masuk) atau ditutup. Disengaja, karena Kraepelin mengukur ketahanan di bawah tekanan waktu tak terputus. Harganya: satu dari dua sesi terputus di prod cocok dengan pola ini (berakhir di kolom 3, sekitar satu menit sesudah mulai), dan kandidat tidak diberi tahu aturan ini selain anjuran di email untuk memakai komputer. Perlu diputuskan apakah dipertahankan apa adanya, diberi jeda toleransi, atau diberitahukan terang di layar petunjuk.
4. **Mesin kandidat resmi.** Di prod pilihannya sudah terjadi de facto: `ERP_FRONTEND_URL` di container recruitment prod berisi `https://career.bharatainternasional.com`, jadi kandidat mengerjakan di career portal. Versi erp-frontend masih ada dan perilakunya berbeda (tanpa aturan butir 3). Keputusan tertulis mana yang dipertahankan belum ada, dan bentuk jawaban baru harus dibangun di tempat kandidat benar-benar berada.

## Dokumen Terkait

- [[HRIS - Bank Soal dan Paket Psikotes]] — cara kerjanya
- [[HRIS - Psikotes Kraepelin]] — jenis tes yang sudah berjalan
- [[HRIS - Recruitment]] — konsep dan keputusan HRD
- [[API - Recruitment Service]] — kontrak endpoint
- [[ADR - 0085 Industrial Relation Catatan Kepatuhan Ringan Terpisah dari SP dan KPI]] — preseden katalog jenis sebagai master data
- [[ADR - 0041 Izin Tipe Form Menempel di Departemen]] — arah default dan aturan saat ditetapkan
- [[REF - Kepemilikan Data]] — gerbang cari sebelum membangun
