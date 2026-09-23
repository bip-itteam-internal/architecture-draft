## Deskripsi

*Pecahan kerja untuk [[ADR - 0114 Antrean Persetujuan Terpusat di Web, Satu Tabel Seragam dari Agregator Employee-Service]]. Bukan rencana per berkas; tiap butir cukup jelas untuk langsung dilempar ke `/start-task`.*

- **Status**: 🟡 Sebagian irisan 1 sudah mendarat di `main` (erp-frontend [#1665](https://github.com/bip-itteam-internal/erp-frontend/pull/1665) merged 2026-09-21, disusul [#1667](https://github.com/bip-itteam-internal/erp-frontend/pull/1667)); irisan 2 belum dikerjakan. ⚠️ Status **per task** belum diukur ulang satu per satu — ukur sebelum memakainya sebagai dasar rencana.
- **Tanggal**: 2026-09-21

## Irisan 1 — tayang tanpa menyentuh backend

Memakai `GET /hr/requests?as=reviewer&include=booking` apa adanya. Tujuh kategori: Izin, Cuti, Sakit, Dinas, Koreksi Presensi, Tukar Jadwal, Booking Ruang. Tujuannya membuktikan bentuk tabelnya di layar sebelum ongkos backend dikeluarkan.

**T1. Halaman `/portal/persetujuan` berisi satu tabel seragam.**
Struktur tabel HRIS (`MainTable` + `useTableState` + `Banner` di dalam prop `toolbar`). Kolom: Kategori, Perihal, Pemohon, Nilai, Menunggu sejak, Tahap. Tanpa kolom Aksi. Urut dari yang paling lama menunggu. Kategori dan Tahap jadi penyaring `select` di toolbar. Sumber data `/hr/requests?as=reviewer&include=booking`; Tahap diturunkan dari `steps[]`, **bukan** dari `status` mentah. Kolom Nilai kosong untuk seluruh kategori irisan ini kecuali Dinas, yang punya `Budget`.
*Tergantung*: tidak ada.

**T2. Hitungan di judul memisahkan "menunggu Anda" dari "pantauan".**
Dua angka terpisah, tidak pernah dijumlahkan jadi satu. Baris pantauan tampil dengan tahap yang jujur dan tanpa tombol keputusan.
*Tergantung*: T1.

**T3. Sheet detail berangka tiga, aksi di footer.**
Header tetap, badan `flex-1 min-h-0 overflow-y-auto px-4 pb-4`, footer memakai `SheetFooter`. Badan diisi per kategori dari `GET /hr/requests/detail?type=&id=&as=reviewer`; untuk cuti dan dinas pakai ulang potongan bebas-rangka di `features/hris/requests/components/detail-sections.tsx`. Footer berisi Setujui dan Tolak untuk kategori yang bisa diputus di tempat, plus "Setujui lalu buka berikutnya"; kategori lain berisi "Buka halaman penuh". Sheet dikendalikan query param (`?detail=<kategori>:<id>`), `useSearchParams` dibungkus `Suspense`.
*Tergantung*: T1. ⚠️ `AlertDialog` di dalam `Sheet` adalah modal bersarang Radix; wajib dicoba dengan tangan termasuk jalur Escape, jsdom buta terhadapnya.

**T4. Aksi menembak endpoint keputusan milik modul asalnya.**
`PATCH /attendance/request/review`, `/business-trip/review`, `/schedule-exchange/review`, `/attendance/correction/{id}/review`, `POST /inventory/peminjaman/{nomor}/setujui|tolak`. Sesudah keputusan, baris hilang dari tabel dan angka di judul turun. Konfirmasi `AlertDialog` yang menyebut objeknya untuk baris bernilai uang.
*Tergantung*: T3.

**T5. Menu dan pintu masuk.**
Satu menu "Persetujuan" di Portal Saya, plus kartu di hub `/portal/pengajuan` yang sudah ada berikut angkanya. ⛔ Gerbang menunya **jangan** peran: ikuti pola MyBharata, tampil bila antreannya tidak kosong. Menurunkannya dari peran akan mengulang cacat yang diperingatkan [[ADR - 0106 Tema dan Teaser Live Support Disetor dan Diputus Penyetuju Departemen sebagai Dasar KPI]].
*Tergantung*: T1.

**T6. Ruang Direktur menyematkan komponen tabel yang sama.**
Menggantikan enam panel `features/direktur/components/*-menunggu-panel.tsx` di tab Persetujuan. Tab Kinerja dan Keuangan tidak tersentuh. Tujuannya menghapus salinan kedua, bukan memindah halaman.
*Tergantung*: T1, T4.

## Irisan 2 — agregator, dan kategori selebihnya

**T7. `GET /pengajuan/antrean` di employee-service.**
Bersaudara dengan `/pengajuan/ringkasan`, memakai ulang seluruh mekanismenya: registri sumber satu baris per antrean, identitas disalin sekali sebelum goroutine, batas waktu per sumber, badan dibatasi, balasan `{data, degraded}` dengan aturan **401/403 bukan degraded**. Mengembalikan baris dalam bentuk seragam, bukan angka. Rute literal didaftarkan sebelum saudara ber-`:param`.

⚠️ **Endpoint yang SAMA melayani dua sumbu** (keputusan pemilik produk 2026-09-22, [[ADR - 0114 Antrean Persetujuan Terpusat di Web, Satu Tabel Seragam dari Agregator Employee-Service]] butir 11): menunggu keputusan pembaca, dan yang sudah ia putuskan, dibedakan satu parameter. Bukan dua endpoint: keduanya menyaring dengan identitas yang sama dan memungut sumber yang sama, jadi memisahkannya melahirkan dua registri sumber yang wajib sepakat.

⛔ **"Riwayat" berarti KEPUTUSAN PEMANGGIL, bukan "sudah diputus siapa pun"**, dan itu tidak gratis: tiap adapter wajib membawa penanda **per baris** siapa yang memutus. Bentuk longgar yang berlaku hari ini di absensi mencocokkan **departemen**; diukur prod 2026-09-22, klausa tahap HR yang terbuka mengembalikan **1282 baris** keputusan orang lain, dan tak ada satu pun gejala yang membedakannya dari keputusan sendiri.
*Tergantung*: T1 (bentuk kolomnya sudah terbukti di layar).

**T8. Adapter tiga sumber "menunggu saya" yang belum ikut.**
Tinjau Setoran Live Support (`/live-support/karya/antrean`), Pengajuan Barang (`/pengajuan-barang/antrean`), Permintaan ERP (`/permintaan-erp/persetujuan`). Ketiganya sudah menyaring per pemanggil, jadi tak ada keputusan produk baru. Permintaan Barang GA (`/permintaan/perlu-aksi`) menyusul, dengan catatan daftarnya dipotong di 200.

⚠️ **"Sudah menyaring per pemanggil" cukup untuk sumbu MENUNGGU, tidak untuk sumbu RIWAYAT.** Menunggu bisa disaring dengan slot yang masih terbuka; riwayat menuntut nama orang yang benar-benar memutus, dan itu field tersendiri. Adapter yang melewatkannya akan mengembalikan baris yang sah tapi bukan milik pembacanya, tanpa satu pun gejala. Lihat T7 dan ADR 0114 butir 11.
*Tergantung*: T7.

**T9. Adapter tiga sumber "daftar modul".**
Pesanan ERP, Payroll run, Rekrutmen. Ketiganya bukan antrean pribadi, jadi wajib bertahap "Pantauan modul" dan tidak ikut hitungan "menunggu Anda".

✅ **Keputusan produk diambil 2026-09-23: HANYA bagi pemegang modulnya.** Payroll tampil bagi orang Finance, Rekrutmen bagi HR, dan seterusnya — bukan bagi semua penyetuju.

⛔ **Konsekuensinya prasyarat pindah ke SERVICE SUMBER, bukan ke agregator.** "Tahu siapa pegang modul apa" adalah aturan hak akses, dan menuliskannya di agregator dilarang [[ADR - 0114 Antrean Persetujuan Terpusat di Web, Satu Tabel Seragam dari Agregator Employee-Service]] butir 7. Satu-satunya jalan yang bersih: ketiga endpoint itu **menggerbang dirinya sendiri**, lalu agregator menerima **403** untuk yang bukan pemegangnya — dan 403 memang sudah diperlakukan sebagai "bukan urusan saya", bukan `degraded`, oleh kerangka yang sudah ada.

⛔ **Paragraf lama di sini KELIRU dan sudah dicabut. Diukur ulang ke `origin/main` 2026-09-24.** Ia berbunyi *"ketiganya belum menggerbang: `listPayrollRuns`, `listOffers`, dan `listRequisitions` memakai filter kosong sehingga seluruh baris terkirim ke siapa pun yang memanggil"*, lalu menyimpulkan T9 berisi **tiga** pekerjaan gerbang di tiga service sebelum adapternya boleh ditulis. Dua dari tiga premisnya tidak benar, dan kesimpulannya ikut salah — biayanya nyata: tiga brief yang tak perlu.

Yang membuatnya keliru: pemeriksaannya berhenti di badan handler. `listPayrollRuns` memang membuka dengan `filter := bson.M{}`, dan dibaca sampai situ saja ia tampak seperti kebocoran yang meyakinkan. Gerbangnya ada satu lapis di atasnya, **di pendaftaran rutenya**.

| Endpoint | Keadaan sebenarnya | Cukup untuk T9? |
|---|---|---|
| `GET /payroll-runs` (`services/payroll/routes.go:109`) | `gate(common.PermPayrollView, isHR)`. Kill-switch `PAYROLL_PERMISSION_ENFORCEMENT` pun jatuh ke `require(isHR)`, bukan ke terbuka. Membalas **403** | ✅ sudah |
| `listRequisitions` (`services/recruitment/requisition_handlers.go:144`) | `bolehLihatSeluruhRequisition` = `isHR(id) \|\| izin RecruitmentView`; yang bukan pemegang jatuh ke `filter["requested_by"] = id.EmployeeID` | ✅ sudah, semantik pemegang modul |
| `listOffers` (`services/recruitment/offer_menu_handlers.go:67`) | digerbang **cakupan perusahaan** (`idKandidatDalamCakupan`), bukan modul. Sudah memancarkan `CanApprove` per pemanggil lewat `bolehSetujuiOffer` | ⚠️ satu-satunya celah |

Dan agregator **sudah** memperlakukan 401/403 sebagai "bukan urusan saya", bukan `degraded` (`hasilSumber`, `antrean_pengajuan.go`) — jadi untuk payroll dan requisition mekanismenya sudah lengkap hari ini, tanpa satu pun perubahan di service sumber.

**T9 karena itu SATU brief adapter**, bukan tiga brief gerbang, dengan satu keputusan tersisa: offers digerbang perusahaan sehingga orang non-HR dalam perusahaan yang sama tetap melihatnya. Putuskan apakah `CanApprove` yang sudah ada dipakai sebagai syarat masuk antrean, atau gerbang modul ditambahkan di recruitment.

⚠️ **Pelajaran yang lebih mahal daripada task ini**, dan alasan paragraf ini ditulis panjang: klaim "X belum digerbang" ditulis di sini tanpa memeriksa lapisan rutenya, lalu berdiri sebagai fakta sampai ada yang mengukurnya. Gerbang di bip-erp lazim dipasang di **pendaftaran rute**, bukan di kueri handler — membaca badan handler saja akan berulang kali menghasilkan tuduhan kebocoran yang keliru.

*Tergantung*: T7. Gerbang per pemanggil **tidak** jadi prasyarat, kecuali keputusan offers di atas.

**T10. Pelatihan dan Tiket ikut masuk.**
Keduanya sudah ada di `registriRingkasan` sebagai angka; di sini mereka menyumbang baris.
*Tergantung*: T7.

**T15. Mode riwayat untuk Pengajuan Barang, di procurement.**
Antrean `/pengajuan-barang/antrean` hari ini hanya mengembalikan yang **menunggu tahap si pemanggil**; tak ada mode "sudah saya putus". Dibangun di service asalnya, bukan direkonstruksi di agregator — merekonstruksinya berarti menuliskan ulang aturan "siapa memutus apa" milik procurement, yaitu sumber kebenaran kedua yang dilarang butir 7 ADR 0114. Wajib membawa penanda per baris siapa yang memutus, bukan sekadar status akhir. Ini juga yang mencabut baris `punyaRiwayat()` di `features/direktur/lib/tab-antrean.ts:210-217`, yang hari ini mengecualikan Pengajuan Barang dengan catatan "begitu endpointnya punya mode riwayat, baris ini yang dicabut, bukan panelnya yang diakali".
*Tergantung*: tidak ada (bisa jalan paralel dengan T7).

**T16. Mode riwayat untuk Booking Ruang, di inventory.**
Inventory tak menyimpan daftar booking yang pernah diputus seseorang; itu keputusan sadar 2026-09-15, dicatat di `services/attendance/pengajuan_booking.go:128-130`. ⚠️ Datanya sebenarnya **ada**: `Peminjaman.riwayat[]` memuat `{aksi, oleh, nama, alasan, waktu}` dan sudah dibaca `langkahPenyetujuBooking`. Yang belum ada endpoint yang menyaringnya per penyetuju. Jadi ini menambah jalur baca, bukan menambah penyimpanan.
*Tergantung*: tidak ada (bisa jalan paralel dengan T7).

**T11. Test kontrak per sumber.**
Mengurai rekaman respons sungguhan tiap endpoint apa adanya, bukan struct tiruan. Ini satu-satunya penjaga terhadap adapter yang rusak diam-diam saat modul asalnya mengubah field, dan pola yang sama sudah dipakai `services/finance/audit_kontrak_test.go`.
*Tergantung*: T8.

**T14. Cabut menu persetujuan per-modul yang sudah digantikan antrean terpusat.**
Diminta pemilik produk 2026-09-22: begitu sebuah kategori benar-benar tampil di `/portal/persetujuan`, pintu lamanya dicabut supaya tak ada dua tempat memutuskan hal yang sama.

⛔ **Urutannya tidak boleh dibalik, dan inilah seluruh isi task ini.** Syarat cabut = kategorinya **terbukti tampil dan bisa diputus** di `/portal/persetujuan`, dibuktikan dengan satu perjalanan sebagai orang lewat gateway, bukan dengan diff atau test hijau. Mencabut lebih dulu tidak menghasilkan galat apa pun: penyetujunya sekadar kehilangan satu-satunya pintu keputusan, dan yang terlihat cuma antrean yang tak pernah berkurang.

Yang benar-benar ada di menu Portal hanya **dua**, keduanya konstanta di `components/layout/portal-menu.ts`:

| Konstanta | Rute | Isi |
|---|---|---|
| `URL_PORTAL_PERSETUJUAN_PENGAJUAN_BARANG` | `/persetujuan/pengajuan-barang` | Pengajuan Barang (T8) |
| `URL_PORTAL_PERSETUJUAN_BUDGET` | `/persetujuan/pengajuan` | Persetujuan Pengajuan **Budget** kas kecil, penyetuju SPV Finance / Direktur — **belum punya task adapter sama sekali**, jadi belum boleh dicabut walau namanya mirip |

`/persetujuan/permintaan-barang` dan `/persetujuan/pesanan-pembelian` **sudah sengaja tidak ada di menu Portal**, dikunci `portal-menu.test.ts:532-533`. Rutenya tetap hidup dan masih dipakai dari menu modulnya; jangan menyimpulkan keduanya sudah pensiun.

⚠️ **Mencabut menu bukan mencabut rute.** Ruang Direktur memanggil antrean Pengajuan Barang lewat jalurnya sendiri (`features/direktur/lib/tab-antrean.ts`, `ANTREAN_PENGAJUAN_BARANG`), jadi rute dan komponennya tetap dibutuhkan sampai T6 selesai. Yang dicabut entri menunya, bukan halamannya.

*Tergantung*: T8 untuk Pengajuan Barang. Budget kas kecil menunggu keputusan apakah ia ikut sama sekali.

## Task terpisah, bukan bagian ADR 0114

**T12. Ukur kenapa 119 pengajuan mati karena didiamkan.**
Diukur prod 2026-09-21: 87 cuti, 12 dinas, 20 koreksi berakhir "Diabaikan oleh sistem (melebihi 24 jam)", lawan 13 yang benar-benar ditolak. Pintu MyBharata sudah ada saat itu semua terjadi, jadi sebabnya bukan ketiadaan layar. Kandidat yang perlu diukur, bukan ditebak: jendela 24 jam terlalu pendek, notifikasi tak sampai, atau aplikasi tak dibuka. **Ini kemungkinan besar masalah yang lebih besar daripada seluruh ADR 0114.**

**T13. Buktikan apakah kartu `pembelian` di beranda portal selamanya degraded.**
`registriRingkasan` (`services/employee/ringkasan_pengajuan.go:86`) menunjuk `/pengajuan-pembelian/perlu-aksi`; di seluruh `services/` pada `origin/main` string itu hanya muncul di baris registrinya sendiri. Dibuktikan dengan **satu panggilan ke endpoint lewat gateway**, bukan dengan grep.

## Dokumen Terkait

- [[ADR - 0114 Antrean Persetujuan Terpusat di Web, Satu Tabel Seragam dari Agregator Employee-Service]]
- [[REF - Alur Persetujuan]] · [[HRIS - Employee Request & Approval]] · [[APP - Web ERP]] · [[Microservices - Employee Service]]
