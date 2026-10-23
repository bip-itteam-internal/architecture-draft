> **Status**: ✅ Live PROD 2026-09-27, pertama dijalankan untuk karyawan nyata 2026-10-09 (gagal di tengah tahap apply, tuntas sesudah bip-erp [#2908](https://github.com/bip-itteam-internal/bip-erp/pull/2908) ter-deploy; pelajarannya masuk §2, §4, §5, §7). Kodenya ada di bip-erp [#2106](https://github.com/bip-itteam-internal/bip-erp/pull/2106) (rute ganti-ID di tiap service), bip-erp [#2107](https://github.com/bip-itteam-internal/bip-erp/pull/2107) (koordinator), dan erp-frontend [#1760](https://github.com/bip-itteam-internal/erp-frontend/pull/1760) (tombol). Ketiganya merged. Terverifikasi 06.08 WIB, baca saja: ke-20 biner memuat rute, indeks `kunci_aktif_unik` terbentuk, bundel FE memuat tombol. Keputusannya [[ADR - 0128 Pengangkatan Magang Dijalankan HR dari ERP, Ganti employee_id oleh Tiap Service]].

## Tujuan

Mengangkat karyawan magang (ID `<KODE>-MG-<NNNN>-<MM>-<YY>`) ke PKWT/PKWTT dengan ID reguler baru (`<KODE>-<NNNN>-<MM>-<YY>`, bulan-tahun dari **tanggal diangkat**), lalu memindahkan seluruh data orang itu ke ID baru di semua service. HR menjalankannya sendiri dari halaman Kontrak, tanpa tiket ke IT. Aturan penomoran: [[ADR - 0126 employee_id Diterbitkan Sistem, Magang yang Diangkat Mendapat ID Reguler dengan Migrasi Riwayat]] §1-§4.

## Kapan dipakai

- Karyawan magang diangkat jadi PKWT, PKWT (Evaluasi), atau PKWTT.
- **Bukan** untuk memperbaiki nomor yang salah atau dobel. Itu tetap lewat alat IT (§6), karena pengangkatan selalu memesan nomor reguler baru.

## 1. HR: siapkan kontraknya dulu

1. HRIS → **Kontrak**, cari karyawannya, buka riwayat kontrak.
2. Tambahkan kontrak PKWT/PKWTT lewat **Perpanjang**. ⛔ **Jangan lewat Perbaiki**: Perbaiki menimpa kontrak Magang yang ada, sehingga masa magang hilang dari riwayat dan tanggal diangkat ikut salah. Selama belum ada kontrak PKWT/PKWTT, panel riwayat kontrak hanya menampilkan petunjuk ini.
3. Tanggal mulai kontrak PKWT/PKWTT **pertama** sesudah magang menjadi tanggal diangkat, dan bulan-tahunnya menjadi akhiran ID baru. Contoh: mulai 26 September 2026 menghasilkan akhiran `-09-26`.

## 2. HR: angkat

1. Di panel yang sama muncul tombol **"Angkat dan terbitkan ID reguler"**. Pilih waktu **di luar jam kerja karyawannya**, karena dua hal: loginnya putus sekali, dan sesudah selesai jadwal dasarnya di presensi bisa tertinggal sampai 30 menit sehingga presensinya bisa gagal selama jeda itu (salinan `work_schedule` di attendance baru menyusul pada sinkronisasi berikutnya, tiap menit ke-00 dan ke-30; bip-erp [#2911](https://github.com/bip-itteam-internal/bip-erp/issues/2911)).
2. Baca dialog konfirmasi, lalu tekan Angkat.
3. Panel menampilkan status **berjalan**. Sistem memeriksa semua service dulu (tahap dry). Baru setelah **semua** lolos, sistem mengganti ID di tiap service satu per satu, dengan employee-service paling akhir.
4. **Selesai**: panel menampilkan ID lama → ID baru, dan riwayat kontrak kini terbaca atas ID baru.

## 3. Sesudah selesai

- **Karyawan**: login ulang sekali di MyBharata dengan **username yang sama**, lalu aktifkan ulang PIN dan biometrik. Sesi lama putus karena token login memuat ID lama.
- **Finance**: bila orang itu punya data turunan proyek Accurate (`beban_marketing_orang` di integration, `incentive_opex_accurate` di insentif), Finance menerima tugas di kotak masuk berisi ID lama dan ID baru. Tugas itu hanya dikirim setelah status **selesai**. Nama proyek di Accurate **tidak** diganti otomatis; Finance menggantinya di hari yang sama.
- **Berkas lama** (foto, dokumen) tetap di folder ber-ID lama dan tetap bisa dibuka. Path-nya tersimpan lengkap di dokumen, jadi ini disengaja.

## 4. Bila status GAGAL

Panel menampilkan status **gagal**, pesan galat, dan tombol **Ulangi**.

- **Jangan membuat pengangkatan baru.** Sistem memang menolaknya: selama pengangkatan terakhir berstatus gagal, kelayakan menjawab `sedang_berjalan`. Alasannya, proses yang gagal di tengah tahap apply sudah menulis ID baru di sebagian service. Pengangkatan kedua akan memesan nomor lain dan membelah data orang itu ke dua ID.
- **Ulangi** memakai ID baru yang **sama**:
  - Gagal di tahap **dry**: tidak ada yang ditulis di mana pun, dan Ulangi mengulang pemeriksaan semua service.
  - Gagal di tahap **apply**: Ulangi hanya menjalankan service yang belum selesai, dalam mode lanjutan. Penggantian nilai persis bersifat idempoten, jadi yang sudah pindah tidak tersentuh lagi.
- Tekan Ulangi hanya setelah sebabnya dibereskan (§5). Mengulang tanpa perbaikan hanya menghasilkan galat yang sama.
- **Klik ganda aman.** Tombol Angkat yang ditekan dua kali, atau dari dua tab, hanya menjalankan satu proses. Permintaan kedua ditolak dengan 409 karena satu orang hanya boleh punya satu pengangkatan yang belum tuntas. Hal yang sama berlaku untuk Ulangi. Nomor ID yang sudah dipesan untuk permintaan yang ditolak ikut terbuang, dan itu diterima.
- **employee-service dimulai ulang di tengah proses** (deploy atau crash): saat service naik lagi, pengangkatan yang masih "berjalan" otomatis ditandai **gagal** dengan pesan "proses terputus karena employee-service dimulai ulang". HR cukup menekan Ulangi.

### 4a. Gagal di tahap apply dan perbaikannya tidak bisa naik hari itu juga

Gagal di tahap apply berarti service di awal urutan **sudah ber-ID baru** sementara employee-service (login) masih ber-ID lama. Yang paling terasa adalah attendance, service pertama di urutan: karyawannya masih login dengan ID lama, jadi **riwayat presensinya tampak kosong, jadwalnya jatuh ke bawaan, dan presensinya bisa ditolak**. Tidak ada data yang hilang; datanya utuh di ID baru. Terjadi 2026-10-09 (attendance 200 dokumen dan form-builder 33 dokumen terlanjur ditulis).

Bila sebabnya bisa dibereskan dan di-deploy sebelum orangnya bekerja lagi, cukup Ulangi. Bila tidak:

1. **Ukur dulu** service mana yang benar-benar menulis: `employee_db.employee_pengangkatan`, field `services[]`, yang berstatus `selesai` dengan `jumlah` > 0.
2. **Balikkan service itu ke ID lama** dengan alat §6 (pasangan terbalik, hanya container Mongo service tersebut). Dry dulu, `mongodump` sebelum menulis. Dry akan menolak dengan "ID TUJUAN SUDAH DIPAKAI" karena salinan `work_schedule` di attendance sudah kembali ber-ID lama oleh sinkronisasi; itu salinan, bukan data baru, jadi mode lanjutan sah **setelah** dipastikan tak ada bentrok di indeks unik.
3. **Biarkan** status `selesai` di dokumen pengangkatan apa adanya selama perbaikan belum naik. Dengan begitu Ulangi yang tertekan tak sengaja hanya gagal lagi di service yang sama tanpa menulis apa pun.
4. Sesudah perbaikan ter-deploy dan **tepat sebelum** HR menekan Ulangi, ubah status service yang dibalikkan dari `selesai` ke `lolos_dry` di dokumen pengangkatan. Tanpa langkah ini Ulangi **melewati** service itu dan datanya terbelah ke arah sebaliknya.
5. HR menekan Ulangi. Sesudah selesai, ukur ulang semua database: nol nilai ID lama selain catatan pemetaan.

Langkah 2 dan 4 menulis ke database PROD, jadi dijalankan manusia. Kerangka skrip yang terpakai 2026-10-09 ada di `.task-plans/` workspace IT (`balik-pengangkatan-1004.ps1`), belum di repo mana pun.

## 5. IT: membaca galat

Galat tingkat proses berbentuk `dry ditolak <service>: ...` atau `apply gagal di <service>: ...`. Rincian per service tersimpan di `employee_db.employee_pengangkatan`, field `services[]`.

| Pesan | Artinya | Tindakan |
|---|---|---|
| `URL service belum dikonfigurasi: <daftar>` (POST ditolak **sebelum** nomor dipesan) | env `<SERVICE>_MODULE_URL` kosong di blok `employee-service` | isi env di compose, lalu `docker compose up -d --force-recreate employee-service` (env dibaca saat container **dibuat**, `restart` tak cukup) |
| `tak terjangkau service <x>` | container mati atau URL salah | periksa `docker ps` dan URL-nya, lalu Ulangi |
| `service <x> menolak (status 404)` | image service itu belum memuat rute `POST /internal/employee-id/ganti` | build ulang service itu (perubahan `shared-library` menaikkan **semua** service) |
| `service <x> menolak (status 401)` | kunci gateway tidak cocok. Rute ganti-ID memeriksa `BIP-Gateway-ID` di rantainya sendiri, dan vault-mcp memakai gerbang kunci miliknya sendiri | pastikan `INTERNAL_GATEWAY_KEY` sama di employee-service dan service itu, lalu `--force-recreate` service yang env-nya berubah |
| `gerbang menolak run (...): <koleksi>\|<path>: ...` (422) | ID lama muncul sebagai **potongan teks** di path yang tidak ada di daftar-izin service itu, atau ID tujuan sudah dipakai | periksa isi path tersebut. Potongan yang sah (path berkas, teks notifikasi) masuk ke daftar-izin **service itu** lewat perubahan kode dan PR, bukan dilewati |
| `gerbang menolak dry ...: <n> koleksi besar belum dideklarasikan dan tak terpindai: <koleksi>` (422, sejak 2026-10-09 muncul di tahap **pemeriksaan**, jadi belum ada yang ditulis) | koleksi service itu melewati 50 ribu dokumen dan belum dideklarasikan, sementara sampelnya tak memuat field ber-ID | ukur koleksi itu (sampel besar + struct entity dan penulisnya), lalu deklarasikan di `LargeCollections` pada `services/<service>/ganti_employee_id_route.go` lewat PR: path ber-ID-nya, atau daftar kosong bila memang tanpa ID karyawan (ADR 0128 §6). Deploy service itu, baru Ulangi. Jangan menyalakan `AllowUnscannable` |
| `gerbang menolak apply ...: ... koleksi besar tak terpindai ...` (422, pesan **lama**) | service itu masih menjalankan biner sebelum bip-erp #2908, yang hanya memeriksa saat apply. Service sebelumnya di urutan **sudah ditulis** | deploy service itu dengan kode terbaru, lalu ikuti §4a |
| `masih ada ID lama sesudah apply ...` (422) | ada tulisan baru ber-ID lama selagi proses berjalan | Ulangi (idempoten) setelah sebabnya jelas |

## 6. Pembalikan dan alat IT (interim)

- **Pemetaan lama → baru tersimpan permanen** di `employee_db.employee_pengangkatan` (`employee_id_lama`, `employee_id_baru`). Pembalikan = menjalankan pasangan yang **terbalik** (nilai persis, ID baru unik). Belum ada tombolnya, jadi pembalikan dijalankan IT lewat alat interim.
- **Alat interim**: `jalankan-migrasi-ganti-id.ps1 -Konfig <json> [-Apply]` beserta `migrasi-ganti-id.js`, di folder `.task-plans/` workspace IT (belum ada di repo mana pun). Selalu dry dulu. Di PROD, perintahnya dijalankan **manusia** (aturan tim: menulis ke DB prod bukan tugas agent). Alat ini tetap sah untuk perapian nomor dan pembalikan setelah fitur live.

## 7. Prasyarat deploy (IT)

Urutan: **rute di semua service → koordinator employee-service → frontend**. Frontend terakhir, karena tombolnya memanggil rute yang belum ada.

- Rute ganti-ID ada di image setiap service. Buktinya `docker exec <Container> sh -c "tr '\000' '\n' < /proc/1/exe | LC_ALL=C grep -c -F '/internal/employee-id/ganti'"` bernilai **> 0** untuk tiap service. ⚠️ Pakai `grep -F` (byte-persis): `grep` mode regex di image ini terbukti membalas **0 untuk string yang ada** pada sebagian biner (2026-10-09, Integration-Service dan TikTok-Shop-Service terbaca "belum ter-deploy" padahal sudah), dan kontrol positif `gofiber` tidak menangkapnya. Sertakan satu service yang sengaja belum di-deploy sebagai kontrol negatif. `docker ps` dan `/health` bukan bukti ([[RUN - Deploy Microservices bip-erp]]).
- employee-service dibuat ulang (`--force-recreate`) karena ada env URL service baru.
- vault-mcp dibuat ulang karena ada env `INTERNAL_GATEWAY_KEY`.
- Uji pertama: `GET /api/employee/pengangkatan/kelayakan?employee_id=<ID magang>` lewat gateway harus membalas `layak` beserta `tanggal_diangkat`, bukan 404.

## Terkait

- [[ADR - 0128 Pengangkatan Magang Dijalankan HR dari ERP, Ganti employee_id oleh Tiap Service]] · [[ADR - 0126 employee_id Diterbitkan Sistem, Magang yang Diangkat Mendapat ID Reguler dengan Migrasi Riwayat]]
- [[HRIS - Personalia]] · [[RUN - Deploy Microservices bip-erp]]
