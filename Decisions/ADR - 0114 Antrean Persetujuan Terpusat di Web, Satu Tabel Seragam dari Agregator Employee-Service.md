## Untuk Manajemen

Penyetuju di web mendapat **satu halaman berisi semua yang menunggu keputusannya**, dari cuti bawahan sampai pesanan pembelian, dalam satu tabel dengan kolom yang sama. Sekarang antrean itu tersebar: sebagian hanya ada di aplikasi MyBharata, sebagian di Ruang Direktur yang hanya dibuka jabatan Direktur, sebagian lagi tak punya pintu sama sekali di web. Seorang supervisor yang bekerja di depan komputer sepanjang hari harus membuka ponselnya untuk menyetujui cuti timnya.

**Terdampak**: setiap orang yang pernah jadi penyetuju, dari supervisor departemen sampai Direktur. Pemohon tidak terdampak sama sekali; cara mengajukan tidak berubah.

**Yang TIDAK dijanjikan**: (1) ini **bukan** obat untuk pengajuan yang mati karena didiamkan. Diukur di produksi 2026-09-21, 119 pengajuan absensi berakhir "Diabaikan oleh sistem" karena lewat 24 jam, sembilan kali lebih banyak daripada yang benar-benar ditolak, dan itu terjadi **ketika pintu di MyBharata sudah ada**. Sebabnya belum diukur dan layar ini tidak akan menyembuhkannya; pengukurannya dipisah jadi task tersendiri. (2) Tidak ada perubahan pada siapa yang berwenang memutuskan apa pun. (3) Tidak ada penggabungan alur pengajuan antar modul; yang digabung hanya tampilannya.

**Besaran kerja**: besar. Satu endpoint agregat baru di employee-service yang memungut 11 endpoint antrean di 7 service, ditambah satu halaman web baru. Dikerjakan beririsan: irisan pertama memakai antrean absensi yang sudah tergabung dan bisa tayang tanpa perubahan backend sama sekali.

## Deskripsi

*Penyetuju di web mendapat satu tabel seragam berisi seluruh antrean keputusan miliknya, dirakit oleh satu endpoint agregat di employee-service yang memungut endpoint antrean tiap modul apa adanya, meneruskan identitas pemanggil sehingga gerbang tiap baris tetap milik service asalnya, dan membedakan "bukan urusan saya" dari "sumber gagal".*

- **Status**: 🟡 **Diusulkan** — kode belum ada.
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

**2. Kolom "Perihal" diisi satu kalimat jadi dari agregator**, bukan dirakit frontend dari field tiap modul. Layar tidak boleh tahu apa itu `leave_type` atau nomor PO.

**3. Kolom "Tahap", bukan "Status".** Antrean menurut definisi berisi yang menunggu, jadi status hampir selalu bernilai sama. Yang membedakan baris adalah menunggu siapa. Untuk absensi diambil dari `steps[]` yang sudah dihitung backend; untuk sumber lain dipetakan agregator ke kosakata yang sama.

**4. Baris yang bisa dilihat tetapi bukan pembaca yang memutus TETAP TAMPIL, bertanda jelas.** Tahapnya jujur ("Menunggu Direktur", "Pantauan modul"), tanpa tombol keputusan, dan hitungan di judul memisahkan **menunggu Anda** dari **pantauan**. Ini mempertahankan kegunaan yang hari ini dipakai staf Kesekretariatan, dan tidak mengubah siapa yang berwenang.

**5. Detail dibuka lewat `Sheet`, aksinya di FOOTER sheet, bukan di baris tabel.** Rangkanya satu (header tetap, badan menggulir ber-padding, footer aksi), badannya berganti menurut kategori. Tabel karena itu tidak punya kolom Aksi, dan seluruh barisnya jadi satu sasaran klik. Pola `aksi` yang dirender pemanggil sudah ada di `sheet-detail-pengajuan.tsx`, lahir dari kebuntuan yang sama.

**6. Agregatornya di employee-service, BUKAN di attendance.** `/hr/requests` sudah menggabungkan enam jenis, tetapi ia milik domain absensi; menumpangkan baris payroll dan procurement ke sana membuat satu service memiliki bentuk data enam modul lain. Employee-service sudah memegang registri lintas modul dan bukan pemilik antrean mana pun, jadi ia tempat yang benar. Endpoint baru `GET /pengajuan/antrean` bersaudara dengan `/pengajuan/ringkasan` dan memakai ulang seluruh mekanismenya.

**7. Adapter per sumber tinggal di agregator untuk sumber yang sudah ada; sumber BARU wajib menyediakan bentuk seragamnya sendiri.** Ini kompromi yang diambil sadar. Menuntut 7 service mengubah endpointnya lebih dulu akan menahan seluruh pekerjaan; menaruh adapter selamanya di agregator melahirkan sumber kebenaran kedua. Aturannya karena itu: yang sudah ada diadaptasi, yang lahir sesudah ADR ini menyetor bentuk seragam, sama seperti feed `calendar-service`.

**8. Tidak ada sumber kebenaran ketiga.** Zona B beranda portal ([[ADR - 0105 Beranda Portal Menumpuk Zona Personal di Atas Ruang Kerja Posisi]]) tetap hanya angka dan tautan, dan tautannya menunjuk ke halaman ini. Ruang Direktur menyematkan komponen tabel yang sama alih-alih memelihara enam panelnya sendiri.

**9. Dikerjakan beririsan.** Irisan 1 memakai `/hr/requests?as=reviewer&include=booking` apa adanya: tujuh kategori, nol perubahan backend, dan bentuk tabelnya terbukti di layar lebih dulu. Irisan 2 dan seterusnya memindahkan pemanggilan ke agregator baru sambil menambah sumber.

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
