**Status**: ✅ Diputuskan 2026-09-02, **terimplementasi, BELUM di-deploy**. bip-erp branch `feat/attendance-jadwal-host-live` (6 commit) + erp-frontend branch `feat/marketing-jadwal-host-live` (2 commit). Verifikasi lewat gateway belum dijalankan.

## Context

Jadwal siaran Host Live **nyatanya disusun marketing**, lalu diserahkan ke HR untuk dimasukkan ke sistem. Sistem tidak pernah mengakui kenyataan itu: seluruh kelola jadwal (definisi shift, pola rotasi, penugasan ke karyawan) digerbang `RequireHRISStaffOrITSupervisor` dan layarnya tinggal di `/hris/schedule`, rute yang menuntut `roles.hris`.

Akibatnya orang yang benar-benar tahu jam siarannya tak bisa memasukkannya, dan orang yang bisa memasukkannya tak tahu jam siarannya. Setiap perubahan campaign melewati satu penyerahan manual yang tak tercatat di mana pun.

[[ADR - 0036 Roster Harian Menimpa Jadwal Dasar]] sudah mengakui akar masalah yang bersebelahan — posisi Host Live tak punya pola, jam siarnya mengikuti campaign — tetapi menyelesaikannya dengan menambah layar di modul HRIS. Ia memindahkan **bentuk datanya**, bukan **kepemilikan pekerjaannya**.

Pertanyaan yang harus dijawab: siapa yang boleh menyusun jadwal host live? Dua jawaban berbentuk daftar peran sama-sama salah, dan salahnya ke arah berlawanan:

- **SPV marketing** — belum tentu orang yang menyusunnya. Penyusunnya sering Leader tim, bukan supervisor divisi.
- **Siapa pun ber-`work_data.is_supervisor`** — `is_supervisor` diturunkan dari nama jabatan, sehingga menyimpan seseorang sebagai "Leader" diam-diam memberinya hak menulis ulang jadwal satu tim.

## Decision

**Kewenangan menyusun jadwal Host Live adalah IZIN yang ditugaskan lewat layar Hak per Posisi, bukan efek samping dari peran di modul mana pun.**

Aturan turunannya:

1. **Izinnya hidup di modul `jadwal` TERSENDIRI, bukan di dalam `hris`.** Ini keputusan yang paling mudah salah dan paling tak terlihat dari sisi backend: `kunciModulAktif` di frontend menurunkan **kategori sidebar** dari PREFIKS tiap izin di klaim. Izin ber-prefiks `hris` akan memunculkan kategori HRIS di sidebar orang marketing, lengkap dengan menu yang tak ber-`perm` sehingga ikut tampil lalu memantul di gerbang rutenya sendiri. Prefiks izin karena itu bukan penamaan, ia ikut menentukan navigasi. Rinciannya di [[CORE - RBAC dan Permission Set]].

2. **Gerbangnya BERDAMPINGAN dengan gerbang lama, tidak menggantikannya.** `HasPermission(jadwal.hostlive.manage)` **ATAU** `RequireHRISStaffOrITSupervisor`. Menambah pemilik baru tidak boleh menyempitkan pemilik lama; staf HR tetap mengerjakan semua yang dikerjakannya hari ini, dari layar yang sama, tanpa satu pun perubahan.

3. **Pemegang izin dibatasi ISI permintaannya, bukan hanya di pintu.** Dua lapis, mengikuti bentuk `gerbangRoster`: middleware menjawab "boleh masuk", lalu tiap handler tulis menilai payloadnya. Pemegang izin hanya boleh pola berkategori `hostlive`, hanya di departemen yang memang punya jadwal host live, dan penugasannya wajib memenuhi **dua** syarat sekaligus — pola tujuan berkategori hostlive DAN karyawannya di departemen yang punya host live. Satu syarat saja meloloskan karyawan Manufaktur ke rotasi host live, atau host Kyura ke rotasi satpam.

4. **Penugasan jadwal STATIS ditolak untuk jalur izin.** Memindahkan host ke `BIP-REGULAR` berarti mencabut shift siarannya — perubahan besar yang tak pernah disebut nama izinnya.

5. **"Departemen yang punya jadwal host live" DITURUNKAN, tidak didaftar.** Jawabannya dihitung dari picker jadwal yang sudah ada (`scheduleListForDepartment` + `IsScheduleHostlive`). Menuliskan `{"Kyura", "Beauty Hacks"}` sebagai daftar akan jadi salinan kedua yang tak ikut berubah saat departemennya bertambah.

6. **Marketing mandiri penuh: shift, pola, penugasan, dan arsip.** Bukan hanya memakai pola yang sudah ada. Pola dirakit dari shift yang sudah ada, jadi tanpa kewenangan membuat shift, alurnya buntu tepat saat campaign berganti jam siaran — dan jalan keluarnya ada di layar yang justru menolak orangnya.

7. **Tidak ada jejak persetujuan,** mengikuti kelola jadwal HRIS yang juga tidak punya. Menambahkannya hanya untuk marketing membuat dua aturan untuk satu pekerjaan.

8. **HR tetap melihat dan bisa mengoreksi semuanya.** Layar `/hris/schedule` tak disentuh sama sekali, dan gerbang rutenya sengaja TIDAK dilonggarkan: melonggarkannya demi menu baru ini akan ikut membuka tab Kelola Shift dan Rotasi Shift untuk seluruh perusahaan.

## Consequences

**Konsekuensi yang diterima:**

- **Fiturnya tidak hidup sampai IT memasang paketnya ke sebuah posisi.** Ini konsekuensi langsung dari keputusan nomor satu, dan disengaja: yang berhak jadi fakta yang bisa dilihat dan diubah di layar, bukan aturan yang harus dibaca dari kode. Harganya satu langkah manusia setelah deploy, dan tanpa langkah itu fiturnya ada tetapi tak seorang pun bisa memakainya.
- **Katalog modul harus didaftarkan di TIGA tempat**: `services/employee/permission_catalogs.go` (validasi + seed), `services/attendance/main.go` (penegak), dan setup uji `shared-library/models/employee/permission_set_test.go`. Katalog yang lupa didaftarkan gagal **senyap** — paketnya tetap tersimpan dan tetap bisa dipasang; yang gagal hanya validasinya, dan itu jarang dicoba. Kelas ini sudah menggigit dua kali sebelumnya.
- **Deploy menuntut `employee-service` DAN `attendance-service` naik bersama.** Keduanya memegang salinan `shared-library`, dan yang tak ikut naik memakai katalog lama.
- **Menu baru duduk di kategori Marketing sementara izinnya bermodul `jadwal`.** Modul `jadwal` sengaja tak punya kategori sidebar, jadi kategorinya harus dibukakan secara eksplisit — hasil `bolehMenu` dioper ke `bolehLihatModulMarketing`. Tanpa itu, pemegang paket yang tak punya peran marketing melihat menu yang kategorinya tak pernah muncul.

**Yang ditemukan saat implementasi, bukan saat merancang:**

- ⛔ **Cache kategori shift 5 menit menolak pola yang baru dibuat.** `kategoriRotasiKustom()` sudah lama di-cache tanpa invalidasi, dan itu tak berbahaya selama kategori shift cuma dipakai Tukar Shift. Begitu ia ikut menentukan boleh-tidaknya sebuah penugasan, pola host live yang baru dibuat dinilai "tanpa kategori" dan penugasannya ditolak **403 berbunyi "pola X bukan jadwal host live"** — pesan yang menyatakan sesuatu yang tidak benar, menyerang persis urutan kerja yang jadi alasan fitur ini ada, dan **sembuh sendiri** setelah beberapa menit. Gabungan itu membuat pemakainya menyimpulkan sistemnya kadang rusak alih-alih melaporkannya. Ditutup dengan invalidasi di ketiga jalur tulis rotasi.

  Pelajaran yang lebih luas: **menjadikan nilai yang sudah lama di-cache sebagai penentu OTORISASI mengubah arti keterlambatannya.** Cache yang tadinya cuma membuat daftar sedikit basi kini membuat aksi ditolak dengan alasan yang salah.

- **Nama jabatan tidak dipakai menyaring siapa pun.** Layar menampilkan `position` supaya pembacanya bisa membedakan Host Live dari Live Support, tetapi penyaringnya DEPARTEMEN — sumbu yang sama dengan gerbangnya. Nama jabatan datang dari master data yang diketik bebas dan sudah pernah berubah (label "ICC" jadi "Account Specialist"); menyaring dengannya berarti orang lenyap dari layar pada hari master data disunting.

**Yang belum dikerjakan (menyusul):**

- **Verifikasi lewat gateway belum dijalankan sama sekali.** Yang paling menentukan bukan angka 201-nya melainkan PASANGANNYA dengan 403, plus pembanding akun `hris:staff` yang membuktikan nol regresi.
- **Roster harian tetap milik HRIS.** Marketing menugaskan grup rotasi, bukan mengisi sel per tanggal. Membuka keduanya berarti dua jalur mengubah tanggal yang sama.
- **`/marketing/*` masih di luar matcher `proxy.ts`,** sama seperti tiga halaman marketing yang sudah ada. Konsekuensi yang diwarisi: pengunjung tanpa token tak dialihkan ke `/login` di rute-rute itu. Layak jadi task tersendiri, bukan ditumpangkan ke sini.

## Terkait

- [[CORE - RBAC dan Permission Set]] (modul `jadwal`, katalog, fallback tier) · [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]
- [[Microservices - Attendance Service]] (gerbang dua lapis, rute) · [[API - Attendance Service]]
- [[ADR - 0036 Roster Harian Menimpa Jadwal Dasar]] (lapisan roster, tetap milik HRIS)
- [[APP - Web ERP]] (menu Marketing → Jadwal Host Live)
- [[HRIS - Attendance System]] (konsep presensi) · [[Sales - Incentive]] (insentif Host Live)
