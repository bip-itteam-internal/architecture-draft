## Untuk Manajemen

Penyetuju di web mendapat **satu halaman berisi semua yang menunggu keputusannya**, dari cuti bawahan sampai pesanan pembelian, dalam satu tabel dengan kolom yang sama. Sekarang antrean itu tersebar: sebagian hanya ada di aplikasi MyBharata, sebagian di Ruang Direktur yang hanya dibuka jabatan Direktur, sebagian lagi tak punya pintu sama sekali di web. Seorang supervisor yang bekerja di depan komputer sepanjang hari harus membuka ponselnya untuk menyetujui cuti timnya.

**Terdampak**: setiap orang yang pernah jadi penyetuju, dari supervisor departemen sampai Direktur. Pemohon tidak terdampak sama sekali; cara mengajukan tidak berubah.

**Yang TIDAK dijanjikan**: (1) ini **bukan** obat untuk pengajuan yang mati karena didiamkan. Diukur di produksi 2026-09-21, 119 pengajuan absensi berakhir "Diabaikan oleh sistem" karena lewat 24 jam, sembilan kali lebih banyak daripada yang benar-benar ditolak, dan itu terjadi **ketika pintu di MyBharata sudah ada**. Sebabnya belum diukur dan layar ini tidak akan menyembuhkannya; pengukurannya dipisah jadi task tersendiri. (2) Tidak ada perubahan pada siapa yang berwenang memutuskan apa pun. (3) Tidak ada penggabungan alur pengajuan antar modul; yang digabung hanya tampilannya.

**Besaran kerja**: besar. Satu endpoint agregat baru di employee-service yang memungut 11 endpoint antrean di 7 service, ditambah satu halaman web baru. Dikerjakan beririsan: irisan pertama memakai antrean absensi yang sudah tergabung dan bisa tayang tanpa perubahan backend sama sekali.

## Deskripsi

*Penyetuju di web mendapat satu tabel seragam berisi seluruh antrean keputusan miliknya, dirakit oleh satu endpoint agregat di employee-service yang memungut endpoint antrean tiap modul apa adanya, meneruskan identitas pemanggil sehingga gerbang tiap baris tetap milik service asalnya, dan membedakan "bukan urusan saya" dari "sumber gagal".*

- **Status**: ⚠️ **Diterima, irisan 1 terimplementasi dan BELUM merge** — erp-frontend [#1665](https://github.com/bip-itteam-internal/erp-frontend/pull/1665), 2026-09-21. Irisan 1 tidak menyentuh backend sama sekali. Irisan 2 (agregator `GET /pengajuan/antrean` dan enam kategori sisanya) belum dikerjakan. **Empat butir Decision di bawah ditandai menyimpang saat implementasi**; penyimpangannya diberi tanda di tempatnya masing-masing, bukan dengan menulis ulang keputusannya.
- **Path di repo**: `bip-erp/services/employee/antrean_persetujuan.go` (baru) · `bip-erp/services/employee/ringkasan_pengajuan.go` (pola yang dipakai ulang) · `erp-frontend/src/app/(main)/portal/persetujuan/` (baru) · `erp-frontend/src/features/persetujuan/` (baru) · `erp-frontend/src/components/layout/sidebar-menus.tsx` · `erp-frontend/src/features/direktur/components/antrean-persetujuan.tsx`
- **Tanggal**: 2026-09-21

## Context

### Kebutuhannya sudah bernama, dan bukan kerapian menu

[[REF - Alur Persetujuan]] sudah mencatat kelas cacatnya sejak 2026-08-10: **wewenang memutus tanpa kemampuan melihat**, yang gejalanya "tak ada apa-apa" dan bukan penolakan. Dokumen itu mendaftar tiga kejadian, dan menulis bahwa ketiganya **baru ketahuan saat antreannya ditampilkan di satu layar**. Ruang Direktur adalah obat untuk kelas itu yang kebetulan hanya diberikan kepada dua jabatan.

### Yang sudah ada, dan sudah jauh

Rancangan ini hampir seluruhnya menyusun dari yang ada:

| Sudah ada | Di mana | Yang ia selesaikan |
|---|---|---|
| Agregator ANGKA lintas modul | `services/employee/ringkasan_pengajuan.go:70-98` | registri lima sumber, identitas disalin sekali sebelum goroutine, batas 8 detik per sumber, badan ≤4 MB, balasan `{data, degraded}` |
| Agregator BARIS lintas jenis | `services/attendance/hr_admin.go:38` | `?as=reviewer` = antrean milik pemanggil, enam jenis absensi dalam satu panggilan |
| Overlay lintas service | `hr_admin.go:211-212` | `include=booking` memungut `/peminjaman/perlu-aksi` milik inventory lalu mengubahnya ke bentuk yang sama, lengkap dengan `degraded` |
| Bentuk baris seragam | `HRRequestSummary`, `hr_admin.go:56-75` | `request_type`, pemohon, tanggal per jenis, dan **`steps[]`** yaitu timeline review yang dihitung backend per jenis |
| Layar penyetuju agregat | MyBharata `ReviewerSubmissionPage` | sudah dipakai sehari-hari, digerbang DATA bukan peran |

Jadi polanya sudah terbukti dua kali di produksi. Yang belum ada hanyalah agregator baris yang **melampaui absensi**, dan pintunya di web.

### Tiga belas kategori, sebelas endpoint, tujuh service

Diukur di `origin/main` 2026-09-21:

| Kategori | Endpoint | Penyaringan |
|---|---|---|
| Izin · Cuti · Sakit · Dinas · Koreksi · Tukar | attendance `GET /hr/requests?as=reviewer` | menunggu pemanggil |
| Booking Ruang | inventory `GET /peminjaman/perlu-aksi` | menunggu pemanggil |
| Tinjau Setoran Live Support | marketing-analytics `GET /live-support/karya/antrean` | menunggu pemanggil |
| Pengajuan Barang | procurement `GET /pengajuan-barang/antrean` | menunggu pemanggil |
| Permintaan ERP | procurement `GET /permintaan-erp/persetujuan` | menunggu pemanggil |
| Permintaan Barang GA | inventory `GET /permintaan/perlu-aksi` | menunggu pemanggil |
| Pelatihan | learning `GET /training/requests?as=reviewer` | menunggu pemanggil |
| Tiket / Tugas | task-management `GET /tasks/filter?pending_my_approval=true` | menunggu pemanggil |
| Pesanan ERP | procurement `GET /pesanan-erp/persetujuan` | **daftar modul**, disempitkan nama jabatan `common.SetaraDirektur` |
| Payroll run | payroll `GET /payroll-runs` | **daftar modul**, digerbang izin |
| Rekrutmen (offers, requisitions) | recruitment `GET /offers`, `GET /requisitions` | **daftar modul**, kecuali `?scope=department` |

### Enam kosakata status untuk hal yang sama

Ini yang menentukan bentuk kontraknya, dan sudah terverifikasi per berkas: attendance memakai kalimat Bahasa Indonesia (`"Menunggu persetujuan"`), permintaan dan pesanan ERP kode huruf kecil (`"menunggu"`), pengajuan barang huruf besar (`"BERJALAN"`), permintaan GA huruf besar (`"DIAJUKAN"`), payroll Inggris huruf kecil (`"draft"`), rekrutmen Inggris Title Case (`"Submitted"`).

Frontend yang memetakan keenamnya sendiri akan menyimpang diam-diam begitu satu modul menambah nilai baru, dan gejalanya baris yang jatuh ke kategori yang salah tanpa satu pun galat. Karena itu pemetaan ke bentuk seragam dikerjakan **di agregator**, bukan di layar.

### Melihat tidak sama dengan memutus, dan itu disengaja

Di attendance, daftar memakai pencocokan nama departemen (`deptOrPositionMatch`) sementara tombol memakai `penyetujuSlotJabatan` yang **sengaja tidak** memakai pencocokan departemen. Akibatnya staf Kesekretariatan melihat baris berslot "Direktur" lalu ditolak saat menekan tombol. [[REF - Alur Persetujuan]] menyatakan asimetri itu disengaja dan mempersempitnya adalah keputusan yang belum diambil.

### Status dok yang jadi pijakan

Pijakan utama ADR ini adalah dua dokumen ✅ Implemented ([[REF - Alur Persetujuan]], [[HRIS - Employee Request & Approval]]) dan pembacaan kode langsung. [[REF - Rantai Pengajuan Lintas Modul]] yang berstatus ⚠️ *peta masalah, belum ada keputusan* **tidak** dijadikan pijakan: ia bersumbu rantai pengajuan hulu-hilir, bukan antrean penyetuju, dan ADR ini tidak menjawabnya.

## Decision

**1. Satu halaman `/portal/persetujuan`, satu tabel, tanpa sub-tab.** Kolom sama untuk semua kategori: Kategori, Perihal, Pemohon, Nilai, Menunggu sejak, Tahap. Urut dari yang paling lama menunggu, bukan per kategori. Kategori dan Tahap jadi penyaring di toolbar.

> ⚠️ **Irisan 1 menyimpang: kolom Nilai TIDAK dibangun.** `HRRequestSummary` (`services/attendance/hr_admin.go:56-75`) tak membawa field nominal apa pun, jadi kolomnya akan kosong untuk **ketujuh** kategori irisan ini, bukan sebagian. Premis keputusan awal keliru: `Budget` pada perjalanan dinas ada di model mentahnya, bukan di bentuk ringkas yang dikirim endpoint. Kolomnya masuk di irisan 2 bersama Pengajuan Barang (`Nominal`), Permintaan ERP (`TotalEstimasi`), dan Pesanan ERP (`Total`), yang ketiganya memang berangka.

**2. Kolom "Perihal" diisi satu kalimat jadi dari agregator**, bukan dirakit frontend dari field tiap modul. Layar tidak boleh tahu apa itu `leave_type` atau nomor PO.

**3. Kolom "Tahap", bukan "Status".** Antrean menurut definisi berisi yang menunggu, jadi status hampir selalu bernilai sama. Yang membedakan baris adalah menunggu siapa. Untuk absensi diambil dari `steps[]` yang sudah dihitung backend; untuk sumber lain dipetakan agregator ke kosakata yang sama.

**4. Baris yang bisa dilihat tetapi bukan pembaca yang memutus TETAP TAMPIL, bertanda jelas.** Tahapnya jujur ("Menunggu Direktur", "Pantauan modul"), tanpa tombol keputusan, dan hitungan di judul memisahkan **menunggu Anda** dari **pantauan**. Ini mempertahankan kegunaan yang hari ini dipakai staf Kesekretariatan, dan tidak mengubah siapa yang berwenang.

> ⚠️ **Irisan 1 menyimpang: hitungannya SATU angka, bukan dua.** `ReviewStep` (`hr_admin.go:79-85`) hanya membawa `{key, name, status, at, notes}` — **tanpa `employee_id`** — jadi dari payload daftar saja layar tak bisa menentukan baris mana yang benar-benar menunggu pembacanya. Dipakai kalimat netral "menunggu keputusan", tanpa kata "Anda", supaya tidak mengklaim lebih dari yang bisa dibuktikan. Pemisahannya menuntut penanda **per baris** dari server, dan polanya sudah ada: antrean Tinjau Setoran Live Support mengirim `boleh_putus` per baris. Itu jadi syarat irisan 2.

**5. Detail dibuka lewat `Sheet`, aksinya di FOOTER sheet, bukan di baris tabel.** Rangkanya satu (header tetap, badan menggulir ber-padding, footer aksi), badannya berganti menurut kategori. Tabel karena itu tidak punya kolom Aksi, dan seluruh barisnya jadi satu sasaran klik. Pola `aksi` yang dirender pemanggil sudah ada di `sheet-detail-pengajuan.tsx`, lahir dari kebuntuan yang sama.

> ⛔ **TIDAK setiap kategori boleh membuka Sheet, dan ini ditemukan saat review, bukan saat merancang.** `handleHRRequestDetail` (`hr_admin.go:351-352`) punya cabang `default` yang membalas **400** untuk `type` di luar enam jenis absensi; `JenisBooking` hanya dikenal jalur DAFTAR (`pengajuan_booking.go`), tak pernah jalur detail. Baris Booking yang masuk lewat `?include=booking` karena itu akan membuka panel galat berikut tombol "Coba lagi" yang tak akan pernah berhasil — jalan buntu yang terbaca sebagai data rusak, bukan sebagai batas fitur.
>
> Aturannya sekarang: kategori yang detailnya dilayani endpoint membuka Sheet; yang tidak, mengantar ke layar keputusannya sendiri (Booking → `/ga/peminjaman`, hidup di prod sejak 2026-09-15 lewat [[ADR - 0095 Pengajuan dan Persetujuan Booking Ruang Juga Lewat Web]]); yang tak dikenal keduanya tidak membuka apa pun, sebab baris yang diam lebih baik daripada panel yang dijamin 400. Daftarnya **diturunkan** dari `REQUEST_TYPES`, bukan diketik ulang, supaya tak lahir salinan kedua dari `switch` di handler. Lihat `features/persetujuan/lib/tujuan.ts`.
>
> ⚠️ Ini juga syarat yang mengikat irisan 2: tiap kategori baru wajib menyatakan **di mana detailnya dibuka** sebelum barisnya boleh masuk tabel.

**6. Agregatornya di employee-service, BUKAN di attendance.** `/hr/requests` sudah menggabungkan enam jenis, tetapi ia milik domain absensi; menumpangkan baris payroll dan procurement ke sana membuat satu service memiliki bentuk data enam modul lain. Employee-service sudah memegang registri lintas modul dan bukan pemilik antrean mana pun, jadi ia tempat yang benar. Endpoint baru `GET /pengajuan/antrean` bersaudara dengan `/pengajuan/ringkasan` dan memakai ulang seluruh mekanismenya.

**7. Adapter per sumber tinggal di agregator untuk sumber yang sudah ada; sumber BARU wajib menyediakan bentuk seragamnya sendiri.** Ini kompromi yang diambil sadar. Menuntut 7 service mengubah endpointnya lebih dulu akan menahan seluruh pekerjaan; menaruh adapter selamanya di agregator melahirkan sumber kebenaran kedua. Aturannya karena itu: yang sudah ada diadaptasi, yang lahir sesudah ADR ini menyetor bentuk seragam, sama seperti feed `calendar-service`.

**8. Tidak ada sumber kebenaran ketiga.** Zona B beranda portal ([[ADR - 0105 Beranda Portal Menumpuk Zona Personal di Atas Ruang Kerja Posisi]]) tetap hanya angka dan tautan, dan tautannya menunjuk ke halaman ini. Ruang Direktur menyematkan komponen tabel yang sama alih-alih memelihara enam panelnya sendiri.

**9. Dikerjakan beririsan.** Irisan 1 memakai `/hr/requests?as=reviewer&include=booking` apa adanya: tujuh kategori, nol perubahan backend, dan bentuk tabelnya terbukti di layar lebih dulu. Irisan 2 dan seterusnya memindahkan pemanggilan ke agregator baru sambil menambah sumber.

**10. Menu "Persetujuan" digerbang DATA, bukan peran.** Ia tampil bila antrean pembacanya tidak kosong, meniru kartu "Perlu Review" di MyBharata yang dirender tanpa satu pun cek peran dan menyembunyikan dirinya saat hitungannya nol. Menurunkannya dari peran mengulang cacat yang dicatat [[ADR - 0106 Tema dan Teaser Live Support Disetor dan Diputus Penyetuju Departemen sebagai Dasar KPI]]: penyetuju yang ditunjuk master data tanpa peran yang bersangkutan tak melihat menunya walau server mengizinkannya memutus.

> ⚠️ **Butir ini ditambahkan 2026-09-21 saat sinkronisasi, dan perlu dicatat kenapa.** Aturannya semula hanya hidup di daftar task ([[ANALISA - Antrean Persetujuan Terpusat di Web]] T5), sementara kode dan artefak rencananya merujuknya sebagai "ADR 0114 butir 5" — padahal butir 5 soal Sheet. Rujukan yang salah lebih buruk daripada tidak ada rujukan: ia mengirim pembaca berikutnya ke paragraf yang keliru dan membuat ADR ini seolah menyatakan sesuatu yang tak pernah ditulisnya.
>
> ⛔ **Irisan 1 menyimpang: menunya tampil untuk semua, tanpa gerbang.** Sebabnya harga, bukan prinsip. `handleHRRequestsList` (`hr_admin.go:279`) memotong halaman di MEMORI **sesudah** keempat koleksi ditarik penuh, jadi `?as=reviewer&limit=1` hemat di kabel tetapi tidak di server, dan gerbangnya akan berjalan pada setiap pemuatan sidebar oleh seluruh karyawan. Halamannya sendiri berkata jujur saat antreannya kosong, dan membalas keadaan Terkunci bagi yang memang tak berhak. Gerbang datanya masuk bersama agregator irisan 2, yang bisa memberi angka murah.

**11. SATU endpoint melayani dua sumbu, dan "riwayat" berarti KEPUTUSAN PEMANGGIL, bukan "sudah diputus siapa pun".** `GET /pengajuan/antrean` mengembalikan yang menunggu keputusan pembaca maupun yang sudah ia putuskan, dibedakan satu parameter. Bukan dua endpoint, karena keduanya menyaring dengan identitas yang sama dan memungut sumber yang sama; memisahkannya melahirkan dua registri sumber yang wajib sepakat.

> ⚠️ **Butir ini ditambahkan 2026-09-22 atas keputusan pemilik produk**, sesudah penelusuran kenapa riwayat tak muncul di `/portal/persetujuan`.
>
> ⛔ **Arti "riwayat" dipilih yang KETAT, dan itu menuntut penanda per baris.** Hari ini bentuk longgar-lah yang berlaku di absensi: klausa riwayat level-departemen `buildReviewFilter` (`services/attendance/main.go:3766`) mencocokkan **departemen**, bukan orang. Diukur prod 2026-09-22, bila klausa tahap HR terbuka bagi sebuah akun, `as=reviewed` mengembalikan **1282 baris** yang diputus orang lain di slot departemen yang sama. Kegagalannya senyap sempurna: barisnya sah, angkanya wajar, dan pembacanya menyimpulkan itu keputusannya sendiri. Karena itu tiap sumber wajib mengirim penanda **per baris** siapa yang memutus, pola yang sama dengan `boleh_putus` di antrean Tinjau Setoran Live Support. Peringatan yang setara sudah pernah ditulis di `features/direktur/lib/tab-antrean.ts:201-204` dan terbukti tidak cukup menjaga apa pun sendirian.
>
> ⛔ **Sumber yang belum punya mode riwayat dibangunkan di SERVICE ASALNYA, bukan ditambal di agregator.** Dua yang belum punya: **Pengajuan Barang** (antreannya hanya mengembalikan yang menunggu tahap pemanggil) dan **Booking Ruang** (keputusan 2026-09-15: inventory tak menyimpan daftar booking yang pernah diputus seseorang, `services/attendance/pengajuan_booking.go:128-130`). Merekonstruksinya di agregator berarti menuliskan ulang aturan "siapa memutus apa" milik modul lain, yaitu sumber kebenaran kedua yang justru dilarang butir 7.
>
> ⚠️ **Sumbu KETIGA tidak masuk ke endpoint ini.** Riwayat pengajuan milik pemakai sendiri disaring keluar secara struktural: `buildReviewFilter` membuang `employee_id == pemanggil` pada `$and` terluar, berlaku untuk kedua sumbu, karena orang tak boleh menyetujui dirinya sendiri. Sumbu itu sudah dilayani `GET /requests/mine` di attendance-service dan hari ini hanya dipakai MyBharata.

## Consequences

**Yang membaik.** Penyetuju di web punya satu tempat; supervisor tidak perlu membuka ponsel untuk menyetujui cuti timnya. Gerbangnya per dokumen dan per identitas, bukan per peran, sehingga sekaligus menutup kelas cacat yang diperingatkan [[ADR - 0106 Tema dan Teaser Live Support Disetor dan Diputus Penyetuju Departemen sebagai Dasar KPI]]: penyetuju yang ditunjuk master data tetapi tak punya peran hari ini tidak melihat menunya walau server mengizinkannya memutus.

**Yang memburuk, dan diterima.** Agregator memegang adapter untuk sumber yang sudah ada, jadi perubahan field di salah satu modul dapat merusak kolom Perihal-nya tanpa galat. Penjaganya test kontrak yang mengurai rekaman respons sungguhan tiap sumber, bukan tiruan struct.

**Yang tidak berubah.** Siapa berwenang memutuskan apa. Seluruh aksi tetap menembak endpoint keputusan milik modul asalnya, dengan gerbangnya sendiri. Agregator tidak pernah menulis.

**Prasyarat yang dicabut, bukan prinsip yang dibalik.** [[ADR - 0095 Pengajuan dan Persetujuan Booking Ruang Juga Lewat Web]] menyebut "daftar gabungan izin dan booking di web" sebagai yang sengaja tidak dilakukan, dengan alasan *"web belum punya daftar izin untuk karyawan"*. ADR ini menghapus alasan itu.

**Konsekuensi deploy.** Irisan 1 frontend saja. Irisan berikutnya menambah endpoint di employee-service beserta env base-URL tiap sumber di blok `employee-service` compose, jadi **backend sebelum frontend**, dan penambahan env menuntut `docker compose up -d --force-recreate`, bukan `restart`.

**Yang ditemukan sambil jalan dan bukan bagian ADR ini.** Kunci `pembelian` di `registriRingkasan` (`ringkasan_pengajuan.go:86`) menunjuk `/pengajuan-pembelian/perlu-aksi`, dan di seluruh `services/` pada `origin/main` string itu hanya muncul di baris registrinya sendiri. Bila benar rutenya tiada, kartu itu selamanya masuk `degraded`. Dibuktikan dengan satu panggilan ke endpoint, bukan dengan grep, dan ditangani sebagai task terpisah.

## Dokumen Terkait

- [[REF - Alur Persetujuan]] — inventaris alur dan siapa berwenang; kelas cacat "melihat ≠ memutus"
- [[HRIS - Employee Request & Approval]] — slot `spv_status`/`hr_status`, dan dua alur yang menaruh peninjau HR di slot SPV
- [[ADR - 0105 Beranda Portal Menumpuk Zona Personal di Atas Ruang Kerja Posisi]] · [[ADR - 0094 Booking Ruang lewat MyBharata, Penyetuju Ditunjuk HR, Satu Sumber Ruang Kantor]] · [[ADR - 0095 Pengajuan dan Persetujuan Booking Ruang Juga Lewat Web]] · [[ADR - 0106 Tema dan Teaser Live Support Disetor dan Diputus Penyetuju Departemen sebagai Dasar KPI]]
- [[APP - Web ERP]] · [[APP - MyBharata]] · [[Microservices - Employee Service]]
