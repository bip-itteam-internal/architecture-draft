> **Status**: 🟡 Konsep / Direncanakan (20 Agustus 2026), rancangan disetujui, belum ada kode. Ini **potongan B** dari empat potongan di [[ADR - 0046 Percobaan Pengajuan Dijejaki Middleware, Bukan Panggilan per Cabang]]; A sudah merged tapi **belum terbukti jalan di dev**, C belum dirancang.

## Context

[[ADR - 0046 Percobaan Pengajuan Dijejaki Middleware, Bukan Panggilan per Cabang]] membuat koleksi `submission_attempt` yang mencatat tiap percobaan pengajuan beserta alasan penolakannya. Kode itu **hanya menulis**: tidak ada satu pun rute baca, jadi satu-satunya cara melihatnya adalah query Mongo langsung. Itu jelas bukan sesuatu yang bisa dipakai orang.

Potongan ini membuat permukaan bacanya. Pemilik fitur memutuskan ia tinggal di **modul IT** dan hanya boleh dibuka **orang departemen IT**.

### Ukuran yang mengubah pertanyaannya

"Departemen IT" ternyata tidak ada. Diukur langsung ke prod 20 Agustus 2026:

- **Tidak ada departemen bernama "IT"**. Yang ada **Tech Development** (`employee.DeptIT = "Tech Development"`).
- **15 orang memegang `system_roles.it`**, 10 di antaranya aktif.
- **11 orang berdepartemen Tech Development**, 6 di antaranya aktif. Kesebelasnya sudah punya peran IT, jadi tak ada yang tertinggal ke arah itu.
- **Empat pemegang peran IT bukan orang Tech Development**: `okyfirman` dan `WirawanWidiAtmoko` (Kesekretariatan), `SenoPrakoso13` (Human Resource), dan `AlfaAndriyatno` (Finance, nilai perannya kosong sehingga sebenarnya tak lolos `checkRole` mana pun).

Keempat nama itulah seluruh isi keputusan ini. Isi jejaknya menyebut **siapa mengajukan Sakit, kapan, dan berapa hari**, dan itu keterangan kesehatan walaupun teks alasan serta fotonya sengaja tidak disimpan ([[ADR - 0046 Percobaan Pengajuan Dijejaki Middleware, Bukan Panggilan per Cabang]] #5). Memberi aksesnya ke HR dan Kesekretariatan adalah keputusan yang berbeda dari memberikannya ke tim developer.

Catatan yang relevan: `system_roles` adalah **hak akses MODUL**, bukan hierarki organisasi, dan keanggotaan departemen hidup di `work_data`. Keduanya sudah lama tercatat sebagai sumbu yang berbeda, dan di sini perbedaannya berhenti jadi teori.

## Decision

**1. Permukaan bacanya di modul IT: `src/app/(main)/it/jejak-pengajuan`.**

Sejajar `it/hak-akses`, `it/status-infrastruktur`, dan halaman IT lain yang sudah ada.

**2. Digerbang DEPARTEMEN (`employee.DeptIT`), BUKAN `system_roles.it`.**

Ini penyimpangan sadar dari seluruh gerbang IT lain di sistem ini, yang semuanya memakai `checkRole("it", ...)`. Alasannya bukan estetika: memakai peran modul akan memberi akses ke empat orang di luar Tech Development, termasuk HR, atas data kesehatan rekan kerja mereka sendiri. Enam orang aktif yang benar-benar merawat sistem ini sudah cukup untuk menjawab "kenapa pengajuan si A gagal".

Konsekuensi yang diterima: orang Tech Development baru **wajib login ulang** sebelum menunya muncul, karena departemen dibaca dari klaim JWT. Pola yang sama pernah menggigit saat HRGA.

Kedua helper yang ada, `IsITMember` dan `HasITRole`, **tidak dipakai** di sini. Keduanya kebetulan berisi ekspresi yang persis sama (`checkRole("it", staff|supervisor|admin)`) dengan dua komentar tujuan yang berbeda; itu duplikasi yang sudah ada sebelum ADR ini dan sengaja tidak dirapikan di sini.

**3. Gerbangnya middleware tingkat rute, bukan `if` di dalam handler.**

Alasan yang sama dengan #2 di ADR 0046: satu handler baru yang lupa memanggil pemeriksanya berarti data kesehatan bocor tanpa satu gejala pun. Middleware membuatnya mustahil dilupakan. Menolak **403** dengan pesan yang menyebut halaman ini khusus Tech Development, bukan 404 yang menyesatkan.

**4. Rute didaftarkan lewat `registerSubmissionAttemptRoutes(app)`, BUKAN inline di `main()`.**

Review menyeluruh potongan A menemukan bahwa dua dari empat pintu tak bisa diuji kehadiran middleware-nya justru karena didaftarkan di dalam `main()` yang panjangnya ribuan baris. Cacat itu sudah tercatat di ADR 0046 §9; mengulanginya di potongan yang menggerbang data kesehatan tidak bisa dibenarkan.

**5. DUA endpoint, bukan satu, dan bukan ringkasan yang dihitung frontend.**

- `GET /submission-attempt`, daftar berpaginasi (`page`, `limit`, `search`, `kind`, `outcome`, `reject_code`, `from`, `to`), respons ber-`pagination` mengikuti konvensi service ini (`total_items`, `total_pages`, `has_next`, `has_prev`).
- `GET /submission-attempt/summary`, hitungan per `outcome`, per `reject_code`, dan per `kind` untuk filter yang sama tanpa paginasi.

Satu endpoint gabungan ditolak karena tiap klik paginasi akan menghitung ulang agregasi seluruh rentang. Ringkasan yang dihitung di frontend dari data yang sudah diambil ditolak lebih keras: ia hanya akan mencerminkan halaman yang sedang terbuka, sehingga menampilkan "3 gagal karena lampiran" untuk rentang yang sebenarnya 40. Angka yang berbohong lebih buruk daripada tidak ada angka.

Keduanya wajib menjawab konsisten untuk filter yang sama; dua endpoint yang boleh berbeda jawaban adalah dua sumber kebenaran.

**6. Rentang tanggal punya bawaan 7 hari terakhir, dan bawaannya DIUMUMKAN.**

Tanpa bawaan, tiap pembukaan halaman memindai koleksi setahun penuh. Tapi bawaan yang diam-diam membatasi data adalah kelas jebakan yang sudah berulang di sini, jadi `range.default_applied` ikut dikirim supaya halaman menulis "menampilkan 7 hari terakhir" alih-alih membiarkan orang mengira itu seluruhnya.

**7. Menu digerbang departemen juga, meniru `dariDeptHR` yang sudah ada.**

Entri `it.jejak-pengajuan.view` di map `FALLBACK` (`erp-frontend/src/utils/menu-permission.ts`) dengan predikat `(_r, k) => k.department === "Tech Development"`. Berkas itu sudah memuat invarian yang mengikat kita: *menu yang lebih longgar dari endpoint-nya menghasilkan halaman terbuka yang kemudian menolak, dan kalau perbandingan di backend dilonggarkan, longgarkan di sini pada perubahan yang sama.*

Dua-duanya wajib diverifikasi, karena masing-masing menangkap kegagalan yang berlawanan: menu tersembunyi dengan endpoint terbuka adalah kebocoran, menu tampil dengan endpoint tertutup adalah alur terputus.

**8. Kode alasan ditampilkan MENTAH, tidak diterjemahkan.**

Ada 59 kode di empat pintu. Menerjemahkannya ke dua bahasa berarti 118 kunci i18n yang dirawat selamanya untuk audiens enam orang developer. Yang ditampilkan: kode sebagai badge monospace untuk disaring, dan `reject_msg` sebagai baris yang dibaca manusia. Ini sejalan dengan pembagian di ADR 0046 #3, kode untuk mesin dan pesan untuk orang.

Teks **antarmukanya** tetap lewat i18n dua bahasa; yang dikecualikan hanya isi datanya.

**9. Halaman memakai pola tabel HRIS apa adanya**: satu kartu, `Banner bare` di dalam prop `toolbar` milik `MainTable`, seluruh keadaan di `useTableState`, memuat data pakai `Skeleton` bukan spinner. Tanggal diformat di `render` kolom dengan `intlLocale(lang)`, **bukan** di lapisan fetch, karena memformat di fungsi transform membuat kolomnya mustahil ikut bahasa aktif dan tak satu pun test menangkapnya.

Seluruh filter muat di `FilterTable` apa adanya (`kind`, `outcome`, `reject_code` sebagai `select`; `from`/`to` sebagai `date`), jadi keterbatasannya yang hanya mengenal dua tipe itu tidak tersentuh.

**10. `company_id` dikunci dari pemanggil**, walaupun hari ini prod cuma punya satu tenant (BIP, 207 karyawan). Menambahkannya sekarang gratis; menambahkannya setelah tenant kedua masuk berarti ada jendela waktu ketika satu perusahaan melihat yang lain.

## Consequences

**Yang membaik**

- Pertanyaan "kenapa pengajuan si A gagal" bisa dijawab dari layar, bukan dari query Mongo oleh orang yang kebetulan punya akses DB.
- Kartu ringkasan memunculkan lonjakan tanpa menunggu ada yang mengeluh. Fakta "15 dari 18 gagal" pada insiden 20 Agustus akan terlihat sendiri.
- Gerbang per departemen memberi contoh pertama di sistem ini bahwa akses ke data pribadi tidak harus menumpang hak akses modul.

**Yang harus diterima**

- **Empat pemegang peran IT kehilangan akses** yang akan mereka dapat di bawah pola biasa. Kalau kelak salah satunya benar-benar perlu, jawabannya **bukan** melonggarkan gerbang ini diam-diam, melainkan memutuskan ulang siapa yang boleh melihat data kesehatan dan mencatatnya sebagai amandemen di sini.
- **Backend dan menu wajib diubah bersamaan.** Melonggarkan salah satunya saja menghasilkan kebocoran atau alur terputus.
- **Butuh login ulang** sesudah pindah departemen.
- **Kode alasan mentah tidak ramah** bagi siapa pun di luar developer. Itu harga yang dibayar sadar untuk menghindari 118 kunci i18n; kalau audiensnya kelak melebar, penerjemahannya harus ikut diputuskan ulang.
- **Potongan B tak bisa diverifikasi sampai potongan A ada di dev dan sudah menghasilkan record.** Per 20 Agustus 2026 dev masih tertinggal 27 commit dari `main` dan koleksinya belum pernah terisi. Halaman yang bagus di atas koleksi kosong tidak membuktikan apa pun, dan membangun B sebelum A terbukti berarti kekeliruan di A akan ditemukan lewat layar yang menampilkan data salah, bukan lewat gerbang dev yang sederhana.

## Dokumen Terkait

- [[ADR - 0046 Percobaan Pengajuan Dijejaki Middleware, Bukan Panggilan per Cabang]] (potongan A, yang menulis koleksinya)
- [[Microservices - Attendance Service]] · [[APP - Web ERP]]
- [[CORE - RBAC dan Permission Set]] (sumbu peran modul, yang sengaja TIDAK dipakai di sini)
- [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] · [[ADR - 0043 Peran Sistem Diturunkan dari Jabatan]]
- [[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]] (kenapa label halaman tetap dua bahasa walau kode alasannya tidak)
