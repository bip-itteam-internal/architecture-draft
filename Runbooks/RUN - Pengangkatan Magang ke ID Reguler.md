> **Status**: ⚠️ Live PROD 2026-09-27, belum pernah dijalankan untuk karyawan nyata. Kodenya ada di bip-erp [#2106](https://github.com/bip-itteam-internal/bip-erp/pull/2106) (rute ganti-ID di tiap service), bip-erp [#2107](https://github.com/bip-itteam-internal/bip-erp/pull/2107) (koordinator), dan erp-frontend [#1760](https://github.com/bip-itteam-internal/erp-frontend/pull/1760) (tombol). Ketiganya merged. Terverifikasi 06.08 WIB, baca saja: ke-20 biner memuat rute, indeks `kunci_aktif_unik` terbentuk, bundel FE memuat tombol. Keputusannya [[ADR - 0128 Pengangkatan Magang Dijalankan HR dari ERP, Ganti employee_id oleh Tiap Service]].

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

1. Di panel yang sama muncul tombol **"Angkat dan terbitkan ID reguler"**. Pilih waktu yang tidak mengganggu karyawannya, karena loginnya akan putus sekali.
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

## 5. IT: membaca galat

Galat tingkat proses berbentuk `dry ditolak <service>: ...` atau `apply gagal di <service>: ...`. Rincian per service tersimpan di `employee_db.employee_pengangkatan`, field `services[]`.

| Pesan | Artinya | Tindakan |
|---|---|---|
| `URL service belum dikonfigurasi: <daftar>` (POST ditolak **sebelum** nomor dipesan) | env `<SERVICE>_MODULE_URL` kosong di blok `employee-service` | isi env di compose, lalu `docker compose up -d --force-recreate employee-service` (env dibaca saat container **dibuat**, `restart` tak cukup) |
| `tak terjangkau service <x>` | container mati atau URL salah | periksa `docker ps` dan URL-nya, lalu Ulangi |
| `service <x> menolak (status 404)` | image service itu belum memuat rute `POST /internal/employee-id/ganti` | build ulang service itu (perubahan `shared-library` menaikkan **semua** service) |
| `service <x> menolak (status 401)` | kunci gateway tidak cocok. Rute ganti-ID memeriksa `BIP-Gateway-ID` di rantainya sendiri, dan vault-mcp memakai gerbang kunci miliknya sendiri | pastikan `INTERNAL_GATEWAY_KEY` sama di employee-service dan service itu, lalu `--force-recreate` service yang env-nya berubah |
| `gerbang menolak run (...): <koleksi>\|<path>: ...` (422) | ID lama muncul sebagai **potongan teks** di path yang tidak ada di daftar-izin service itu, atau ID tujuan sudah dipakai | periksa isi path tersebut. Potongan yang sah (path berkas, teks notifikasi) masuk ke daftar-izin **service itu** lewat perubahan kode dan PR, bukan dilewati |
| `... koleksi besar tak terpindai ...` (422) | koleksi di atas 50 ribu dokumen yang sampelnya tak memuat field ber-ID | pemindaian manual dengan alat §6 untuk koleksi itu, lalu putuskan. Jangan menyalakan `AllowUnscannable` tanpa bukti |
| `masih ada ID lama sesudah apply ...` (422) | ada tulisan baru ber-ID lama selagi proses berjalan | Ulangi (idempoten) setelah sebabnya jelas |

## 6. Pembalikan dan alat IT (interim)

- **Pemetaan lama → baru tersimpan permanen** di `employee_db.employee_pengangkatan` (`employee_id_lama`, `employee_id_baru`). Pembalikan = menjalankan pasangan yang **terbalik** (nilai persis, ID baru unik). Belum ada tombolnya, jadi pembalikan dijalankan IT lewat alat interim.
- **Alat interim**: `jalankan-migrasi-ganti-id.ps1 -Konfig <json> [-Apply]` beserta `migrasi-ganti-id.js`, di folder `.task-plans/` workspace IT (belum ada di repo mana pun). Selalu dry dulu. Di PROD, perintahnya dijalankan **manusia** (aturan tim: menulis ke DB prod bukan tugas agent). Alat ini tetap sah untuk perapian nomor dan pembalikan setelah fitur live.

## 7. Prasyarat deploy (IT)

Urutan: **rute di semua service → koordinator employee-service → frontend**. Frontend terakhir, karena tombolnya memanggil rute yang belum ada.

- Rute ganti-ID ada di image setiap service. Buktinya `docker exec <Container> sh -c "strings /service | grep -c /internal/employee-id/ganti"` bernilai **> 0** untuk tiap service. `docker ps` dan `/health` bukan bukti ([[RUN - Deploy Microservices bip-erp]]).
- employee-service dibuat ulang (`--force-recreate`) karena ada env URL service baru.
- vault-mcp dibuat ulang karena ada env `INTERNAL_GATEWAY_KEY`.
- Uji pertama: `GET /api/employee/pengangkatan/kelayakan?employee_id=<ID magang>` lewat gateway harus membalas `layak` beserta `tanggal_diangkat`, bukan 404.

## Terkait

- [[ADR - 0128 Pengangkatan Magang Dijalankan HR dari ERP, Ganti employee_id oleh Tiap Service]] · [[ADR - 0126 employee_id Diterbitkan Sistem, Magang yang Diangkat Mendapat ID Reguler dengan Migrasi Riwayat]]
- [[HRIS - Personalia]] · [[RUN - Deploy Microservices bip-erp]]
