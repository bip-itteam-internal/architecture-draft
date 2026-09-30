# ADR - 0141 Potret Sasaran Penilaian Form Berulang Diambil Ulang tiap Periode, Beku di Dalam Periode

> **Status**: 🟡 **Diusulkan**, 2026-09-29, BELUM diputuskan dan nol kode. Linear: BHA-359. Pengambil keputusan: **TBD** (pemilik form penilaian di HR bersama tim IT; lihat §Pertanyaan terbuka). Bila diputuskan sesuai usulan, ADR ini **menggantikan** butir keputusan 2026-09-28 "karyawan baru tidak ditambahkan ke potret yang sudah terbit" di [[Microservices - Form Builder Service]] §Sasaran yang resign dikecualikan. Sampai §Decision diisi, butir 2026-09-28 itu yang berlaku. Nomor 0141 diklaim saat push; bila sudah terpakai, geser ke nomor bebas berikutnya.

%% Status di blockquote atas supaya terbaca VAULT-INDEX.json (15 baris pertama), pola sama dengan ADR 0136 sampai 0138. %%

%% Vault ini PUBLIK. Nama orang dan employee_id sengaja tidak ditulis; yang disebut hanya nama form, jabatan, tanggal, dan angka agregat. %%

## Untuk Manajemen

**Masalahnya dalam satu kalimat.** Form penilaian yang berulang tiap bulan (mis. "Pelayanan Tim Office Boy") memotret daftar orang yang dinilai **sekali saja saat form diterbitkan**, lalu memakai potret itu untuk **semua bulan sesudahnya**, sehingga karyawan yang masuk sesudah tanggal terbit **tidak pernah dinilai**, tanpa satu pun galat. Sebaliknya, karyawan yang pindah ke jabatan lain tetapi masih aktif **terus ditagih** sebagai jabatan lamanya; yang keluar otomatis hanya yang resign.

**Yang perlu diputuskan.** Apakah daftar orang yang dinilai diambil ulang **tiap kali periode baru dibuka** (tetap beku di dalam satu periode, supaya semua penilai bulan itu menilai daftar yang sama), atau tetap satu daftar seumur form seperti sekarang.

**Yang tidak dijanjikan.** Orang yang masuk di tengah bulan baru ikut dinilai **mulai bulan berikutnya**, bukan bulan itu juga. Penilaian bulan-bulan yang sudah lewat untuk orang yang terlewat tidak bisa dibuat mundur. Sampai keputusan diambil, yang menutup celahnya adalah tindakan manual (tutup lalu terbitkan ulang form), bukan kode.

## Deskripsi

*Usulan untuk mengubah potret sasaran penilaian (`subject.resolved`) pada form **berulang** dari satu potret seumur form menjadi satu potret **per periode**, diambil saat periode dibuka dan beku sepanjang periode itu, mengikuti pola `FormPeriod.Participants` yang sudah dipakai kaizen. Alasan desain beku (adil antar penilai) dipertahankan di dalam periode; yang dibuang hanya bekunya lintas periode. Empat opsi dibandingkan; usulan penulis ditandai jelas sebagai usulan.*

- **Tanggal**: 2026-09-29
- **Diukur ke**: bip-erp `origin/main` `add699c9` (klaim kode di dok ini diverifikasi ulang ke commit itu); data PROD baca-saja 2026-09-29 (diukur sesi lain, angka dikutip apa adanya).
- **Hubungan dengan ADR dan dok lain**:
  - [[Microservices - Form Builder Service]] §Potret sasaran diambil sekali saat terbit dan §Sasaran yang resign dikecualikan: bila diputuskan sesuai usulan, **menggantikan** butir "Karyawan baru TIDAK ditambahkan ke potret yang sudah terbit (keputusan user 2026-09-28)" untuk form berulang. Cron pengecualian (`subject.excluded`) **tetap**, cakupannya berpindah ke potret periode (lihat Opsi 1).
  - [[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]]: kaizen adalah pemakai `FormPeriod.Participants`, preseden potret per periode yang dipakai usulan ini. ADR ini **tidak mengubah** kaizen.
  - [[ADR - 0090 Inspeksi Satgas 5R dan K3 di Form Builder dengan Nilai dari Cek Ulang Terakhir]]: form Satgas memakai tipe `evaluation` dengan sasaran `positions` Office Boy dan Security dan berulang bulanan, jadi selama mekanismenya masih hidup ia terkena celah yang sama. [[ADR - 0122 Satgas Per-PIC Input Bebas Gantikan Form Builder, SLA Temuan dan Skor dari Approval]] memindahkan Satgas keluar dari Form Builder; sampai itu live, keputusan ini juga berlaku untuk form Satgas.
  - [[ADR - 0044 Mutasi Antar-Tenant Mempertahankan employee_id]]: salah satu kasus PROD adalah orang yang dimutasi antar-perusahaan sesudah form terbit. Potret diambil per perusahaan form, jadi orang itu baru bisa masuk lewat potret baru.

## Context

### Kenapa potret dibuat beku

Komentar kode menyatakannya eksplisit (`models_form.go:386-395`): potret `subject.resolved` bukan cache semata, melainkan supaya daftar orang yang dinilai **tidak bergeser di tengah periode**. Orang pindah jabatan dan karyawan baru masuk kapan saja; daftar yang berubah membuat sebagian penilai mendapat orang yang tak pernah dilihat penilai lain, lalu angkanya dibandingkan seolah setara. Efek sampingnya jalur pengisian tak menyentuh employee-service sama sekali.

Alasan itu **benar untuk satu periode**. Untuk form berulang, kode menerapkannya **lintas periode**, dan di situ celahnya.

### Bagaimana kode bekerja hari ini (diverifikasi ulang ke `add699c9`)

- **Potret diambil sekali, saat transisi ke terbit.** `updateForm` menghitung `publishing := req.Status == StatusPublished && form.Status != StatusPublished` (`form_handlers.go:508`), lalu `resolveSubjects` memotret dan menulis `subject.resolved` sekaligus mengosongkan `subject.excluded` (`form_handlers.go:560-579`).
- **Sumber potret**: `resolveSubjects` (`employees.go`) memanggil `fetchActiveEmployees` (`employees.go:41-61`, `GET /list?type=employee` ke employee-service dengan header perusahaan dari permintaan), lalu `selectSubjects` (`subject.go:121-148`) yang lewat `matchesSubject` (`subject.go:95-113`) mencocokkan aturan `positions` dengan `work_data.position` (tak peka huruf). Gagal memotret menggagalkan penerbitan (`422`); batas 300 orang.
- **Sasaran dikunci sesudah terbit.** `updateForm` hanya menerima `subject` dan `form_type` baru saat form masih draft (`form_handlers.go:371-378`).
- **Cron periode tidak memotret ulang.** `bukaPeriodeJatuhTempo` (cron tiap jam, `cron.go`) memanggil `ensurePeriod` untuk tiap form berulang yang terbit; satu-satunya potret yang diambil di sana adalah `snapshotParticipants`, dan hanya bila `kaizenActive(form)`.
- **Preseden per periode sudah ada.** `FormPeriod.Participants` (`models_period.go:51-63`) sengaja dipotret per periode, dengan komentar yang menyebut akibat potret seumur form persis: "akan menagih orang yang sudah resign selamanya sekaligus tak pernah menagih karyawan baru". Komentar yang sama menyatakan bedanya dengan `FormSubject.Resolved` disengaja ("di sana yang dijaga adalah keadilan pembanding penilaian"). Potret kaizen diambil dari cron lewat `fetchEmployeesForCompany(form.CompanyID)`, karena cron tak punya `fiber.Ctx`; kegagalannya menandai `participants_partial` dan dicoba lagi jam berikutnya (`perluPotret`).
- **Cron pengecualian hanya mengurangi, dan hanya atas status aktif.** `segarkanSasaranKeluar` (`sasaran_keluar.go`, cron `*/15`) mengisi `subject.excluded` lewat `hitungSasaranKeluar` (`sasaran_keluar.go:38-68`), yang mengeluarkan anggota potret hanya bila `employee_id`-nya **tidak ada di daftar aktif**. Jabatan tidak dibandingkan sama sekali, jadi karyawan yang pindah jabatan tetapi masih aktif tetap di potret. Ia tidak pernah menambah orang.
- **Jawaban di luar potret ditolak.** `findSubject` (`subject.go:226-232`) mencocokkan `subject_employee_id` kiriman klien ke potret; orang yang tak ada di potret tidak bisa dinilai sama sekali.
- **Yang dibaca pengisi dan gerbang**: `sasaranAktif` (`subject.go:170`) = `resolved` dikurangi `excluded`, dipakai `/me/forms`, `/subjects`, validasi simpan jawaban, dan `sasaranWajibBagi` (`analytics_subject.go:181`). Gerbang presensi mode block (`penilaianSelesai`, `compliance.go:90`) menahan absen sampai **seluruh** sasaran aktif milik pengisi dinilai pada periode berjalan. Laporan per orang membaca `rosterLaporan` (`subject.go:190`), juga dari potret form.

### Perilaku sekarang per jenis perubahan

| Perubahan data karyawan sesudah form terbit | Perilaku sekarang | Mekanisme |
|---|---|---|
| Resign / akun dinonaktifkan | **otomatis keluar** dari kewajiban (paling lama 15 menit) | `hitungSasaranKeluar` mengisi `subject.excluded` |
| Karyawan baru dengan jabatan yang dinilai | **tidak otomatis**: tak pernah masuk potret | tak ada jalur tambah; `findSubject` menolak jawaban atasnya |
| Mutasi masuk ke jabatan yang dinilai (termasuk mutasi antar-perusahaan) | **tidak otomatis**: tak pernah masuk potret | sama dengan karyawan baru |
| Mutasi keluar dari jabatan yang dinilai, masih aktif | **tidak otomatis**: tetap di potret dan terus ditagih sebagai jabatan lamanya, termasuk oleh gerbang presensi | `hitungSasaranKeluar` hanya memeriksa status aktif, bukan jabatan |
| Daftar jabatan di aturan form diubah pengelola | **tidak bisa**: `subject` terkunci sesudah terbit | `updateForm` hanya menerima `subject` saat draft (`form_handlers.go:371-378`) |

Satu-satunya jalan untuk empat baris terakhir hari ini adalah menutup lalu menerbitkan ulang form.

### Data PROD (2026-09-29)

- **Form "Pelayanan Tim Office Boy"** terbit 11 Agustus dengan potret **4** orang. Satu Office Boy baru masuk **18 Agustus** dan **tidak pernah dinilai** (0 jawaban), sementara Office Boy lain menerima **148** penilaian di periode September.
- **Form "Pelayanan Tim Security"**: potret **7** orang, sedangkan pemegang jabatan Security kini **8**. Selisihnya satu orang hasil mutasi antar-perusahaan tanggal 19 Agustus dengan departemen Percetakan; apakah ia memang anggota tim yang dinilai **perlu dikonfirmasi** (lihat §Pertanyaan terbuka butir 3), jadi kasus ini belum tentu celah.
- **Arah sebaliknya**: satu Office Boy yang resign 15 Agustus masih dinilai **136 kali** sebelum cron pengecualian rilis 28 September. Ini sudah ditutup `subject.excluded`, dicatat di sini karena menunjukkan dua arah dari akar yang sama: potret seumur form.

### Kenapa celahnya senyap

Tak ada galat di mana pun: pengisi tidak melihat orang yang tak ada di potret, gerbang presensi lepas setelah sasaran yang ada dinilai, dan laporan per orang tidak memuat baris untuk orang yang terlewat. Pertanyaan "kenapa Office Boy baru tak punya nilai" hanya bisa dijawab dengan membandingkan potret ke daftar jabatan saat ini.

## Opsi

### Opsi 0: tetap seperti sekarang

Satu potret seumur form; karyawan baru masuk hanya bila form ditutup lalu diterbitkan ulang.

- **Konsekuensi**: keadilan antar penilai terjaga di seluruh umur form. Karyawan baru tidak pernah dinilai tanpa tindakan manual, dan tindakan manual itu (terbit ulang) mengosongkan `excluded` dan memotret ulang seluruh daftar.
- **Ongkos**: nol kode; beban ingatan pada pengelola form tiap ada karyawan baru atau mutasi ke jabatan yang dinilai.
- **Risiko**: disiplin tanpa penjaga dan tanpa pemberitahuan. Pengelola form tidak diberi tahu ada karyawan baru yang cocok dengan aturan sasaran, jadi celah hari ini akan berulang.

### Opsi 1: potret ulang saat periode baru dibuka, disimpan per periode (pola kaizen)

1. **Bentuk.** Form berulang yang bersasaran menyimpan potret sasaran **di dokumen periode** (`FormPeriod`), sejajar `Participants`, diambil oleh cron periode saat periode dibuka lewat `fetchEmployeesForCompany(form.CompanyID)` dan `selectSubjects` dengan aturan `subject` form. Potret periode beku sepanjang periode itu.
2. **Pembaca.** `sasaranAktif`, `findSubject`, `sasaranWajibBagi`/`sasaranTerpenuhiBagi`, dan `rosterLaporan` membaca potret **periode yang bersangkutan**, bukan `subject.resolved` form. Satu fungsi resolusi "potret untuk form F pada periode P" dipakai semua pembaca; tak ada pembaca yang membaca `subject.resolved` mentah untuk form berulang.
3. **Kegagalan memotret.** Berbeda dari penerbitan (yang gagal-keras `422`), kegagalan cron tidak bisa menolak apa pun. Usulan: periode tetap terbuka dengan **potret periode sebelumnya** sebagai cadangan dan penanda parsial, lalu dicoba lagi tiap jam seperti `perluPotret`. Periode tanpa potret sama sekali tidak boleh membuat pengisi melihat daftar kosong sementara gerbang gagal-terbuka tanpa jejak.
4. **Pengecualian.** Cron `*/15` tetap mengisi `excluded`, tetapi terhadap potret **periode berjalan**. Potret periode baru hanya berisi karyawan aktif, jadi `excluded` periode baru mulai kosong, sama seperti terbit ulang hari ini.

- **Konsekuensi**:
  - **Menutup keempat celah "tidak otomatis" di tabel §Perilaku sekarang mulai periode berikutnya**: karyawan baru dan mutasi masuk ikut dipotret, mutasi keluar tidak lagi dipotret, dan aturan sasaran diterapkan ulang atas data jabatan saat periode dibuka. Perubahan daftar jabatan di aturan form tetap terkunci sesudah terbit (di luar cakupan ADR ini), tetapi aturan yang sama kini dievaluasi ulang tiap periode. Di dalam satu periode semua penilai tetap menilai daftar yang sama, jadi alasan desain beku utuh.
  - **Laporan per orang membaca potret periodenya**: bulan Agustus dilaporkan atas daftar Agustus, September atas daftar September. Laporan lintas periode (mis. tren per orang) harus menerima bahwa satu orang bisa muncul mulai bulan tertentu, bukan dianggap "tak dinilai" di bulan sebelum ia masuk.
  - **Gerbang presensi tidak menagih sasaran yang masuk di tengah periode**, karena ia membaca potret periode berjalan. Ini diinginkan: menahan absen seluruh kantor karena satu orang baru masuk hari ini adalah kegagalan yang sama dengan menagih orang resign.
  - **Form non-berulang tetap beku** dengan `subject.resolved` seperti sekarang (lihat §Pertanyaan terbuka butir 1).
  - Periode lampau kebal terhadap perubahan data karyawan sesudahnya, sama seperti papan kepatuhan kaizen.
- **Ongkos**: sedang, satu service (form-builder): model periode, cron periode, empat pembaca, migrasi (potret form yang terbit disalin ke periode berjalan supaya September tidak berubah di tengah jalan), dan test. Tidak menyentuh MyBharata bila bentuk respons `/me/forms` dan `/subjects` tidak berubah (perlu diukur saat `/plan`).
- **Risiko**: pembaca yang lupa dipindah tetap membaca potret form tanpa gejala, jadi dibutuhkan pemindai (lihat §Penjaga). Dua tempat penyimpanan potret (form untuk non-berulang, periode untuk berulang) harus dijembatani satu fungsi resolusi, bukan cabang yang disalin di tiap pembaca.

### Opsi 2: sinkron otomatis tiap ada karyawan baru atau mutasi

Potret form ditambah (dan dikurangi) begitu employee-service mencatat karyawan baru atau perubahan jabatan, lewat cron pembanding atau peristiwa dari employee-service.

- **Konsekuensi**: orang baru langsung ditagih, termasuk di tengah periode.
- **Ongkos**: sedang sampai besar; peristiwa lintas service atau cron pembanding yang menulis ke potret.
- **Risiko**: **membatalkan alasan desain beku**: di tengah periode sebagian penilai sudah menilai daftar lama sementara sisanya mendapat daftar baru, lalu hasilnya ditumpuk seolah setara (persis yang dicegah komentar `form_handlers.go:371-374`). Gerbang presensi mode block langsung menagih orang baru ke seluruh pengisi di hari ia masuk, sehingga seisi kantor bisa tertahan absen karena satu data HR. Ditolak penulis.

### Opsi 3: tombol "tambah sasaran" manual

Pengelola form menambah orang ke potret form yang sudah terbit dari layar, tanpa terbit ulang.

- **Konsekuensi**: celah ditutup kasus per kasus oleh orang yang tahu ada karyawan baru.
- **Ongkos**: kecil sampai sedang (endpoint tulis, layar, jejak siapa menambah kapan).
- **Risiko**: sama dengan Opsi 0 soal ingatan: tak ada yang memberi tahu pengelola bahwa ada orang baru yang cocok. Bila tombolnya menambah ke potret berjalan, ia juga membawa risiko Opsi 2 (daftar bergeser di tengah periode) kecuali tambahan hanya berlaku mulai periode berikutnya. Berguna sebagai **pelengkap** Opsi 1 untuk form non-berulang (lihat §Pertanyaan terbuka butir 1), bukan sebagai jalan utama.

### Ringkasan pembanding

| Kriteria | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| Karyawan baru ikut dinilai tanpa tindakan manual | tidak | ya, periode berikutnya | ya, segera | tidak |
| Mutasi keluar (masih aktif) berhenti ditagih | tidak | ya, periode berikutnya | ya, segera | tidak |
| Daftar sama untuk semua penilai dalam satu periode | ya | ya | tidak | tergantung |
| Gerbang presensi menagih orang di hari ia masuk | tidak | tidak | ya | tergantung |
| Laporan bulan lampau kebal perubahan data karyawan | tidak (terbit ulang menimpa) | ya | tidak | tidak |
| Service yang disentuh | tidak ada | form-builder | form-builder + employee | form-builder + FE |

## Rekomendasi penulis (USULAN, bukan keputusan)

1. **Opsi 1** untuk form berulang yang bersasaran: potret per periode, diambil saat periode dibuka, beku di dalam periode, dengan satu fungsi resolusi yang dipakai semua pembaca.
2. **Form non-berulang tetap beku** (Opsi 0) sampai ada kasus nyata; bila muncul, Opsi 3 dipertimbangkan khusus untuk jenis itu.
3. **Opsi 2 ditolak**: membatalkan alasan desain beku dan membuat gerbang presensi menagih orang di hari ia masuk.

Alasannya: pola ini sudah dibuktikan di service yang sama (`FormPeriod.Participants` kaizen), komentarnya sendiri sudah menyebut celah ini sebagai alasan kaizen memotret per periode, dan ia memisahkan dua hal yang hari ini tercampur: keadilan **di dalam** periode (dipertahankan) dan kelengkapan **antar** periode (diperbaiki). Kelemahan usulan: orang yang masuk tanggal 2 menunggu hampir sebulan sebelum dinilai, dan empat pembaca harus dipindah serentak.

## Pertanyaan terbuka

1. **Form non-berulang**: apakah tetap beku seumur form? Form sekali-jalan yang terbuka lama (berbulan-bulan) punya celah yang sama tanpa periode untuk memotret ulang.
2. **Mutasi keluar di TENGAH periode**: dikeluarkan **seketika** seperti resign (cron `*/15` diperluas membandingkan jabatan terhadap aturan sasaran, sehingga penilai tak lagi ditagih orang yang sudah tak mereka layani), atau **menunggu periode berikutnya** (konsisten dengan beku di dalam periode; penilai masih bisa menilai layanan bulan itu)? Opsi 1 sendiri hanya menjamin yang kedua. Hari ini `hitungSasaranKeluar` hanya mengenal status aktif, jadi orang yang dimutasi tetap ditagih sampai form diterbitkan ulang. Catatan: mengeluarkan seketika berarti mengulang pemanggilan jabatan tiap 15 menit dan mengurangi daftar di tengah periode, yang aman bagi keadilan antar penilai (sama seperti resign) karena hanya mengurangi, tidak menambah.
3. **Keanggotaan tim bukan sekadar jabatan**: kasus Security hasil mutasi antar-perusahaan (departemen Percetakan) menunjukkan aturan `positions` bisa memasukkan orang yang tidak dilayani penilainya. Apakah itu diterima, atau aturan sasaran perlu dipersempit (mis. `positions` dan `departments` sekaligus, yang hari ini digabung OR)?
4. **Siapa berhak memicu potret ulang manual** di tengah periode (mis. setelah data HR dibetulkan): pengelola form, HR, atau tidak seorang pun (tunggu periode berikutnya)? Bila diizinkan, penilaian yang sudah masuk untuk periode itu diperlakukan bagaimana?
5. **Waktu potret**: tepat saat periode dibuka (cron tiap jam), atau sejumlah jam sesudahnya supaya perubahan data HR hari pertama ikut terbaca?

## Decision

**TBD.** Diisi setelah §Pertanyaan terbuka dijawab dan pengambil keputusan ditetapkan. Sampai saat itu dok ini tidak boleh dikutip sebagai keputusan, dan butir 2026-09-28 di [[Microservices - Form Builder Service]] tetap berlaku.

## Tindakan sementara (tanpa kode, dijalankan manusia)

Untuk form "Pelayanan Tim Office Boy" (dan "Pelayanan Tim Security" bila keanggotaannya sudah dikonfirmasi): **tutup lalu terbitkan ulang** form **sesudah gerbang presensi periode September berakhir dan sebelum periode Oktober dibuka**. Terbit ulang memotret daftar aktif saat itu dan mengosongkan `excluded`, jadi Office Boy yang masuk 18 Agustus ikut dinilai mulai Oktober.

- Waktu itu dipilih supaya penilai periode September tidak mendapat daftar yang berubah di tengah jalan (alasan desain beku), dan gerbang tidak mendadak menagih satu orang tambahan ke seluruh pengisi.
- Yang menjalankan pengelola form dari layar, bukan agent. Sebelum menutup, ukur dulu apakah menutup form berulang memengaruhi periode yang masih terbuka atau jawaban yang sudah masuk; jangan diasumsikan aman.
- Ini menambal satu kali. Karyawan berikutnya yang masuk sesudah terbit ulang kembali terlewat sampai keputusan ini diambil.

## Langkah sesudah diputuskan (daftar task kasar, bila Opsi 1)

1. **Ukur dulu** (baca-saja, PROD): jumlah form berulang bersasaran yang terbit, ukuran potret masing-masing dibanding jumlah pemegang jabatan saat ini, dan apakah jawaban tersimpan membawa `period_key` di semua form itu (penentu apakah laporan per periode bisa dibaca ulang).
2. **Model**: potret sasaran di `FormPeriod` (nama field dipilih di `/plan`), beserta waktu potret dan penanda parsial.
3. **Cron periode**: memotret sasaran untuk form berulang bersasaran saat periode dibuka, dengan cadangan potret periode sebelumnya bila gagal.
4. **Pembaca**: satu fungsi resolusi potret per (form, periode); `sasaranAktif`, `findSubject`, `sasaranWajibBagi`/`sasaranTerpenuhiBagi`, `rosterLaporan` memakainya. `segarkanSasaranKeluar` menulis `excluded` ke potret periode berjalan.
5. **Migrasi**: potret form yang sedang terbit disalin ke periode berjalan apa adanya, supaya periode itu tidak berubah. Kerangka dua fase (dry run, cadangan), dijalankan manusia di PROD.
6. **Sinkron dok**: [[Microservices - Form Builder Service]] (dua subbagian potret dan pengecualian), [[API - Form Builder Service]] bila bentuk respons berubah, [[IT - Form Builder]].

## Penjaga yang dibutuhkan

- **Test: karyawan baru masuk periode berikutnya, tidak masuk periode berjalan.** Fixture: form berulang bulanan bersasaran `positions`, potret periode 1 berisi A dan B; C dengan jabatan sama menjadi aktif di tengah periode 1. Assertion: `sasaranAktif` periode 1 tetap A dan B, `findSubject` atas C di periode 1 ditolak, gerbang pengisi di periode 1 lepas setelah A dan B dinilai; sesudah periode 2 dibuka, potret periode 2 memuat A, B, dan C, dan laporan periode 1 tidak berubah.
- **Kontrol negatif** untuk test itu: kembalikan sebentar pembaca ke `subject.resolved` form dan pastikan test merah **pada assertion C di periode 2**, bukan karena sebab lain. Kontrol kedua: potret ulang dipasang di pembukaan setiap jam tanpa syarat periode baru, dan pastikan assertion "periode 1 tetap A dan B" merah.
- **Fixture wajib memakai `employee_id` dan jabatan yang berbeda** untuk A, B, C; fixture yang menyamakannya lulus untuk implementasi yang salah.
- **Test pengecualian**: orang yang resign di periode 1 masuk `excluded` periode 1, dan tidak ada di potret periode 2.
- **Test mutasi keluar**: D di potret periode 1, pindah ke jabatan lain yang tak dinilai (masih aktif) di tengah periode 1. Assertion: potret periode 2 tidak memuat D; perilaku D di sisa periode 1 mengikuti jawaban §Pertanyaan terbuka butir 2.
- **Test kegagalan cron**: employee-service gagal saat periode 2 dibuka, periode tetap terbuka dengan potret cadangan dan penanda parsial, pengisi tidak mendapat daftar kosong.
- **Pemindai sumber**: menolak pembacaan `Subject.Resolved` di luar fungsi resolusi (daftar-izin per berkas yang hanya boleh menyusut), dengan kontrol negatif satu pembaca baru di berkas lain.
- **Satu uji lewat gateway DEV** sebelum diklaim selesai: dua periode berurutan dengan satu karyawan uji baru di antaranya, dibuktikan dari `/me/forms` pengisi, bukan dari unit test.

## Dokumen Terkait

- [[Microservices - Form Builder Service]] · [[API - Form Builder Service]] · [[IT - Form Builder]] · [[APP - MyBharata]]
- [[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]] · [[ADR - 0090 Inspeksi Satgas 5R dan K3 di Form Builder dengan Nilai dari Cek Ulang Terakhir]] · [[ADR - 0122 Satgas Per-PIC Input Bebas Gantikan Form Builder, SLA Temuan dan Skor dari Approval]] · [[ADR - 0044 Mutasi Antar-Tenant Mempertahankan employee_id]]
