## Deskripsi

*Jatah cuti tahunan terbit otomatis di **ulang tahun kontrak masing-masing karyawan**, bukan diketik HR per orang dan bukan serentak 1 Januari. Patokannya `start_date` kontrak paling awal yang tipenya sudah lepas masa evaluasi. Saldo dicatat sebagai **ledger kejadian** (`vacation_ledger`), dan `work_data.vacation` turun pangkat jadi salinan ringkas demi kompatibilitas MyBharata.*

- **Status**: 🟡 **Diusulkan** — belum ada di kode. Keputusan diambil 2026-08-29 setelah pengukuran data produksi; daftar task ada di `Workspace/ANALISA - Akrual Cuti Tahunan Otomatis`.
- **Path di repo (yang akan disentuh)**: `bip-erp/services/employee/vacation_accrual.go` (baru) · `vacation_ledger.go` (baru) · `cron.go` (ubah) · `main.go` (endpoint cuti) · `bip-erp/shared-library/models/employee/models.go` · `bip-erp/services/attendance/main.go` (pemotongan hari kerja) · `erp-frontend/src/features/hris/vacation/**` · skrip migrasi `join_date` (dijalankan manusia)
- **Tanggal**: 2026-08-29

## Untuk Manajemen

**Apa yang berubah di layar.** Jatah cuti tahunan muncul sendiri pada tanggal ulang tahun kerja tiap orang. HR tidak lagi perlu mengetik angkanya satu per satu, dan karyawan tidak perlu menunggu diingat. Layar Kelola Cuti tetap seperti sekarang, ditambah tanggal patokan tiap orang, kapan sisa cutinya hangus, dan penanda merah bagi orang yang datanya belum bisa dipakai.

**Siapa yang terdampak.** Seluruh karyawan aktif. Saat ini 15 orang sudah bekerja lebih dari satu tahun tetapi jatahnya masih kosong sehingga mereka tidak bisa mengajukan cuti sama sekali; yang paling lama menunggu sudah 79 bulan. Sebaliknya 23 orang sudah menerima jatah padahal belum genap satu tahun. Karyawan magang dan yang masih dalam masa evaluasi tidak akan menerima jatah, dan itu memang sesuai aturan.

**Apa yang TIDAK dijanjikan.** Angka jatah tetap **5 hari**, sama seperti yang berlaku sekarang, dan sistem tidak menghitungnya sendiri dari jumlah Cuti Bersama tahun berjalan. Bila jumlah hari Cuti Bersama tahun depan berbeda, angka itu harus diubah manual dan tidak ada yang mengingatkan. Sistem juga tidak mencabut jatah yang terlanjur diberikan kepada 23 orang tadi, tidak menghitung mundur jatah tahun-tahun yang sudah lewat, dan tidak memotong jatah untuk Cuti Bersama karena pemotongan itu sudah tercermin di angka 5. Lima orang yang data kontraknya tidak cocok dengan tanggal masuk sengaja **tidak** diproses otomatis, melainkan dilaporkan ke HR untuk diperiksa.

**Perkiraan besaran kerja.** Satu modul baru di layanan kepegawaian, penyesuaian di layanan presensi, satu layar diperbarui, dan satu skrip perapian data yang dijalankan sekali. Perkiraan kasar 5 sampai 8 hari kerja pengembangan, ditambah verifikasi.

## Context

Keluhan pemicunya sederhana: seorang karyawan bermasa kerja 14 bulan melihat jatah cutinya 0 di layar Kelola Cuti. Penelusuran menemukan bahwa yang salah bukan perhitungannya, melainkan **tidak ada apa pun yang menerbitkan hak**.

### Keadaan kode hari ini

Satu-satunya penulis `work_data.vacation.quota` adalah `POST /vacation/quota` di employee-service, yang dipanggil hanya dari modal edit per baris di layar Kelola Cuti. Tidak ada perhitungan dari `join_date`, tidak ada kaitan ke kontrak, tidak ada aksi massal.

`cronResetAnnualLeave` (1 Januari 00:05 WIB) terdengar seperti pemberi jatah tetapi bukan: filternya `vacation.quota > 0` dan isinya hanya menyetel `used=0, available=true, history=[]`. Karyawan berkuota 0 dilewati selamanya. Commit aslinya berjudul *"post-process for annual leave with quota assigment"*, dan kata "assignment" di situ merujuk endpoint manual tadi.

Akibat hilirnya keras dan senyap: attendance-service menolak pengajuan `Cuti tahunan` dengan **400 `Annual leave (vacation) quota has not been set, contact HR`** begitu kuotanya 0. Jadi kuota kosong bukan sekadar angka nol di layar HR, orangnya benar-benar tidak bisa mengajukan cuti. Koleksi `submission_attempt` mencatat **nol** penolakan berkode `VACATION_QUOTA_UNSET`, artinya mereka tidak pernah sampai mencoba. Keluhan datang dari melihat layar, bukan dari sistem memberi tahu.

### Yang ditemukan saat data produksi diukur (2026-08-29)

| Ukuran | Angka |
|---|---|
| Akun aktif | 182, **180** di antaranya punya `work_data` |
| `vacation.quota` = 5 | 123 orang |
| `vacation.quota` = 0 | 33 orang |
| Tanpa field `vacation` sama sekali | 23 orang |
| `vacation.quota` = 4 | 1 orang |
| Masa kerja ≥ 12 bulan | 115 orang |
| **Sudah ≥ 12 bulan tetapi kuota kosong** | **15 orang** |
| **Belum 12 bulan tetapi sudah berkuota** | **23 orang** |
| Masa kerja ≥ 5 tahun | 2 orang |

Tak seorang pun berkuota 12 atau 14. Ini sempat terbaca sebagai penyimpangan dari Pasal 15, dan ternyata **bukan**.

### Asal-usul angka 5, yang selama ini hanya hidup di kepala HR

Pasal 15 memberi 12 hari kerja dan menyatakan Cuti Bersama memotong jatah cuti tahunan. `company_holiday` mencatat 8 tanggal bertipe `Cuti Bersama` untuk BIP tahun 2026 (20 sampai 26 Maret, dan 28 Mei), salah satunya jatuh Minggu sehingga **7 di antaranya hari kerja**.

```
12 hari kerja  (jatah Pasal 15)
-7 hari kerja  (Cuti Bersama 2026)
---
 5 hari        <- persis angka pada 123 orang
```

Jadi `vacation.quota` **bukan jatah tahunan**. Ia menyimpan **sisa setelah Cuti Bersama dipotong**, dan pemotongan itu dikerjakan HR di luar sistem lalu hasilnya diketik. Nama kolomnya berbohong tentang isinya, dan aturan pemakaiannya tidak tertulis di mana pun. Pencatatan asal-usul angka 5 di ADR ini adalah setengah dari alasan ADR ini ada: tanpanya, orang berikutnya akan menyimpulkan perusahaan hanya memberi 5 hari dan melanggar aturannya sendiri.

### Tiga jebakan data yang mengubah rancangan

1. ⛔ **`join_date` tersimpan dalam dua tipe BSON**: 91 `date` dan 89 `string`. MongoDB tidak membandingkan lintas tipe, jadi filter `{join_date: {$lt: <Date>}}` **melewati separuh karyawan tanpa satu pun galat**. Sensus pertama untuk ADR ini sendiri jatuh ke lubang ini dan menjawab 7 padahal 15. Cron akrual yang menyaring `join_date` dengan cara biasa akan diam-diam melewatkan separuh karyawan, dan hasilnya terlihat persis seperti cron yang bekerja.
2. **`employee_contract` justru bersih**: `start_date` **225 dari 225** bertipe `date`. Memindahkan patokan ke kontrak menghapus jebakan di atas sekaligus.
3. **Tetapi kontraknya sebagian besar perkiraan**: 204 dari 225 dokumen bertanda `migrated: true`, yang `start_date`-nya disalin dari `join_date` dan oleh komentar kodenya sendiri disebut "HANYA PERKIRAAN". Dari 180 karyawan aktif, **165 hanya punya satu kontrak** dan hanya **15** yang punya kontrak kedua. Karena itu "kontrak kedua" tidak dapat dipakai sebagai patokan.

### Status kepegawaian ternyata sudah membedakan masa evaluasi

`EmploymentTypes` di shared-library adalah enum empat nilai yang divalidasi saat kontrak dibuat, dan dua di antaranya persis menjawab syarat "setelah evaluasi" pada Pasal 15:

| Konstanta | Nilai | Karyawan aktif |
|---|---|---|
| `Permanent` | `PKWTT` | 1 |
| `Contract` | `PKWT` | 167 |
| `Probation` | `PKWT (Evaluasi)` | 4 |
| `Internship` | `Magang` | 8 |

Jadi kelayakan tidak perlu disimpulkan dari urutan kontrak. Ia sudah tercatat eksplisit, dan 12 orang yang memang belum berhak dapat disaring tanpa menebak.

### Sumber aturannya tidak ada di vault ini

Peraturan Perusahaan 2026-2028 hidup sebagai `assets/docs/company_policy.pdf` di repo **mybharata-app**, diturunkan jadi `docs/policy/leave_terms.md` dan `docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md`. Dokumen terakhir itu dinyatakan **menang** atas perilaku sistem oleh `CLAUDE.md` repo tersebut. Ringkasan yang ditampilkan ke karyawan di aplikasi menyebut "berhak 12 hari cuti setelah 1 tahun bekerja" **tanpa** menyinggung Kontrak Kedua, sementara dua dokumen internal menambahkan syarat itu. Perbedaan janji ke dua audiens itu adalah keputusan HR, bukan keputusan teknis, dan sengaja tidak diselesaikan oleh ADR ini.

## Decision

### 1. Patokan adalah kontrak yang sudah lepas evaluasi, bukan kontrak kedua

```
patokan = start_date kontrak PALING AWAL bertipe PKWT atau PKWTT
          (bukan Magang, bukan PKWT (Evaluasi))
```

"Kontrak kedua" ditolak sebagai patokan karena hanya 15 dari 180 karyawan memilikinya, sehingga 165 orang tidak akan punya patokan sama sekali. Tipe kontrak menjawab pertanyaan yang sama (*sudahkah lewat evaluasi*) dengan cakupan penuh.

### 2. Ketidakcocokan kontrak dan `join_date` dilaporkan, tidak ditebak

Patokan disilangkan dengan `join_date`. Selisih lebih dari 30 hari **tidak** diselesaikan dengan mengambil yang lebih awal maupun yang lebih akhir: orangnya dilewati dan dilaporkan ke HR.

Alasannya konkret. Satu karyawan ber-`join_date` 2024-05-15 memiliki kontrak tunggal yang mulai 2026-07-24, selisih 26 bulan. Bila `join_date` yang benar, memakai kontrak membuatnya kehilangan dua tahun masa kerja; bila kontraknya yang benar, memakai `join_date` memberinya hak yang belum jadi haknya. Sistem tidak punya cara mengetahui mana yang betul, jadi yang benar adalah berhenti dan bertanya. Saat ini ada **5 orang** dalam keadaan ini. Karyawan tanpa kontrak sama sekali diperlakukan sama.

### 3. Hak terbit di ulang tahun patokan, dan cron berjalan HARIAN

Hak pertama terbit pada `patokan + 12 bulan`, dengan syarat status saat itu bukan `Magang` maupun `PKWT (Evaluasi)`. Periode berikutnya jatuh tiap ulang tahun patokan.

`cronResetAnnualLeave` yang berjalan setahun sekali **dicabut** dan diganti job harian. Job tahunan yang jatuh saat container mati melewatkan **satu tahun penuh** tanpa ada yang tahu, dan repo ini sudah pernah mengambil pelajaran yang sama pada `cronFinalisasiKPI` yang sengaja dibuat harian dengan alasan tertulis persis itu. Keamanannya datang dari **idempotensi per pasangan (karyawan, periode)**: entri "terbit" yang sudah ada membuat jalan berikutnya melewatinya, sehingga job harian aman diulang berapa kali pun.

### 4. Jatah adalah angka TETAP dari konfigurasi, bukan hasil hitungan

```
5 hari  untuk umum
7 hari  untuk masa kerja >= 5 tahun
```

Alternatif yang ditolak: menerbitkan 12 (atau 14) lalu memotong hari kerja Cuti Bersama dari `company_holiday` secara otomatis. Alternatif itu lebih benar secara model, membuat tangga senioritas jalan sendiri, dan ikut menyesuaikan diri bila jumlah Cuti Bersama berubah. Ia ditolak **atas keputusan sadar pemilik proses** demi memperkecil lingkup rilis pertama. Konsekuensinya dicatat di bawah dan tidak boleh dianggap sudah selesai.

Tangga senioritas tetap dipertahankan sebagai angka kedua supaya Pasal 15 tidak hilang seluruhnya. Saat ini 2 orang memenuhi syarat 5 tahun, dan salah satunya kini menerima 5 padahal seharusnya 7.

### 5. Cuti Bersama tetap TIDAK dipotong sistem

Sudah tercermin di angka 5. Menambahkan pemotongan otomatis sekaligus mempertahankan angka tetap akan memotong dua kali.

### 6. Saldo per periode, hangus setelah periode berikutnya lewat

Pasal 15: cuti yang tidak dipakai pada tahun berjalan hangus pada akhir tahun berikutnya. Diterjemahkan ke periode ulang tahun, jatah periode ke-N dapat dipakai selama periode ke-N dan ke-N+1, lalu hangus di awal periode ke-N+2. Pemakaian selalu mengambil dari periode **tertua** lebih dulu.

Cron 1 Januari yang lama menyetel `used = 0` tanpa memindahkan sisa, sehingga sisa hangus satu tahun lebih cepat dari yang diatur. Itu ikut diperbaiki di sini.

### 7. `vacation_ledger` jadi sumber kebenaran, `work_data.vacation` jadi salinan ringkas

Satu dokumen per kejadian: `terbit`, `pakai`, `hangus`, `koreksi`. Saldo, sisa, dan riwayat adalah turunan.

`work_data.vacation` **tetap ditulis** berisi `quota`, `used`, `remaining`, `available`, dan `history` sebagaimana sekarang, karena MyBharata membacanya di menu Sisa Cuti dan attendance-service membacanya sebagai gerbang kuota lewat `/list?type=vacation`. Versi aplikasi yang sudah terpasang di ponsel orang tidak bisa dipaksa naik, jadi kompatibilitas ini bukan kemewahan.

Aturannya mengikuti preseden `employee_contract` di service yang sama: **hanya modul cuti yang boleh menulis field itu**. Tanpa aturan tersebut, salinan ringkas berubah menjadi sumber kebenaran kedua yang pasti menyimpang.

Ledger sekaligus menutup satu cacat yang sudah ada: hari ini `used` dan `history` adalah dua representasi fakta yang sama, dan `POST /vacation/quota` dapat menyetel `used` tanpa menyentuh `history` sehingga keduanya menyimpang tanpa galat. Sesudah ADR ini keduanya turunan dari entri ledger yang sama, dan entri `pakai` menyimpan `leave_request_id` sebagai rujukan.

### 8. Pemotongan dihitung HARI KERJA

`decrementVacationQuota` di attendance-service merangkai tanggal dengan `AddDate(0, 0, 1)` dari tanggal awal sampai akhir tanpa menyaring hari non-kerja, sehingga cuti Jumat sampai Senin memotong 4 hari. Jatahnya hari kerja, jadi pemotongannya harus hari kerja. Perusahaan bekerja Senin sampai Sabtu, sehingga yang dikecualikan adalah Minggu, `Libur Nasional`, dan `Cuti Bersama` di `company_holiday`.

Selama kuota diisi manual selisih ini tersamar. Begitu penerbitannya presisi, selisihnya jadi terlihat.

### 9. Akrual tidak pernah mencabut hak, dan backfill hanya periode berjalan

Cron hanya menambah. 23 orang yang menerima jatah sebelum genap 12 bulan tidak diutak-atik; mencabut hak yang sudah diberikan adalah keputusan HR. HR tetap dapat menyesuaikan angka lewat endpoint yang sudah ada, dan sesudah ADR ini penyesuaian itu **menambah baris `koreksi`**, bukan menimpa.

Saat rilis, 15 orang yang ulang tahun patokannya sudah lewat menerima satu entri `terbit` bertanggal ulang tahun tersebut. Tidak ada penerbitan mundur ke periode sebelumnya: tanpa batas itu, karyawan berpatokan 2020-01-19 akan menerima enam penerbitan sekaligus.

### 10. Normalisasi `join_date` adalah prasyarat, bukan pekerjaan sampingan

89 dokumen ber-`join_date` string dinormalisasi menjadi `date` sebelum modul ini menyala, sebagai skrip terpisah dengan dry run. Ia menulis ke database produksi, jadi **dijalankan manusia**, bukan agent.

Meski patokan diambil dari kontrak, `join_date` tetap dipakai sebagai pembanding silang di §2, dan pembanding yang separuhnya tak terbaca bukan pembanding.

## Consequences

### Yang membaik

- 15 orang yang selama ini tidak dapat mengajukan cuti sama sekali langsung memperoleh jatahnya, dan tidak ada orang baru yang jatuh ke keadaan itu.
- Hak berhenti bergantung pada ingatan seseorang. Kesalahan arah kedua (jatah diberikan sebelum waktunya) juga berhenti bertambah, dan itu kesalahan yang tidak pernah dikeluhkan siapa pun karena tidak ada yang protes diberi lebih.
- Pertanyaan "kenapa sisa cuti saya segini" bisa dijawab dari data, bukan dikira-kira.
- 12 karyawan magang dan masa evaluasi tersaring benar, tanpa daftar manual.
- Jebakan `join_date` dua tipe hilang dari jalur ini, dan datanya ikut dirapikan untuk pemakai lain.

### Yang memburuk atau tetap terbuka

- ⚠️ **Angka 5 menjadi konstanta yang kehilangan asal-usulnya.** Ia berlaku hanya selama Cuti Bersama berjumlah 7 hari kerja. Bila tahun depan berbeda, konfigurasinya harus diubah manual dan **tidak ada yang mengingatkan**. Inilah harga yang dibayar untuk memperkecil lingkup rilis pertama.
- **Tujuh hari Cuti Bersama tetap dipotong di luar sistem.** Layar menampilkan 5 tanpa menjelaskan ke mana 7 lainnya pergi, sama seperti sekarang.
- **Tangga senioritas jadi angka kedua yang juga tetap.** Bila jatah dasar berubah, dua angka harus diubah, bukan satu.
- **Dua sumber angka yang harus dijaga sinkron** (`vacation_ledger` dan salinan di `work_data.vacation`), dengan aturan penulis tunggal sebagai satu-satunya penjaga.
- **employee-service dan attendance-service harus naik bersama**, karena gerbang kuota membaca bentuk yang berubah.
- **2 akun aktif tanpa `work_data`** tidak tersentuh akrual apa pun dan tidak akan terlihat di laporan mana pun.
- ⚠️ **Perbedaan janji antara ringkasan di aplikasi dan aturan internal belum diselesaikan** (lihat Context). ADR ini memakai tafsir "sudah lepas evaluasi dan total masa kerja 12 bulan"; bila HR memutuskan lain, §1 sampai §3 ikut berubah.

### Yang sengaja tidak dilakukan

- **Jatah tidak dihitung dari Cuti Bersama**, meski itu model yang lebih benar. Ditolak sadar demi lingkup, bukan karena tidak diketahui.
- **Ketidakcocokan kontrak dan `join_date` tidak dijatuhkan ke aturan otomatis apa pun.** "Ambil yang lebih awal" merugikan perusahaan pada sebagian kasus dan merugikan karyawan pada sebagian lain, dan keduanya senyap.
- **Kewajiban memakai minimal 1 hari cuti tiap bulan** yang disebut Pasal 15 tidak diimplementasikan. Belum ada mekanismenya, dan menambahkannya di sini melebarkan lingkup tanpa pemicu.
- **Aturan Izin lebih dari 2 hari yang memotong cuti tahunan** juga tidak diimplementasikan. Ia menyentuh subtipe lain dan pantas jadi keputusan tersendiri.

## Dokumen Terkait

- [[HRIS - Leave Request]] yang memuat cara kerja pengajuan dan gerbang kuotanya
- [[Microservices - Employee Service]] pemilik `work_data`, `employee_contract`, dan koleksi baru `vacation_ledger`
- [[Microservices - Attendance Service]] yang memanggil pemotongan kuota dan menggerbang pengajuan
- [[IT - Background Jobs & Schedulers]] yang mencatat cron 1 Januari yang dicabut keputusan ini
- [[APP - MyBharata]] konsumen `quota`, `used`, `remaining`, dan `history` yang wajib tetap kompatibel
- [[HRIS - Personalia]] tentang kontrak PKWT dan riwayat masa kerja
- [[ADR - 0044 Mutasi Antar-Tenant Mempertahankan employee_id]] yang mengatur `work_data` saat karyawan berpindah perusahaan
