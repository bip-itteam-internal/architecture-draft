## Untuk Manajemen

Layar **Jadwal Ruang** di MyBharata memperlihatkan ruang mana terpakai jam berapa, tetapi sengaja tidak menyebut siapa pemesannya. Akibatnya orang yang melihat ruang yang ia butuhkan sudah terisi tidak punya cara menindaklanjuti di dalam aplikasi: ia harus bertanya ke GA atau menebak sendiri. Pemilik produk (2026-09-22) memutuskan jadwal kini **menyebut nama dan divisi pemesan**, supaya orang bisa langsung menghubunginya untuk bertukar jam.

**Terdampak**: seluruh karyawan, karena layar ini memang dibaca semua orang tanpa izin modul apa pun. **Yang TIDAK ikut dibuka**: keperluan rapat, nomor WhatsApp, nomor booking, jabatan, dan riwayat keputusan; kelimanya tetap hanya untuk pemegang izin **GA: Lihat**. Jam kosong yang dipilih saat mengisi form (`/peminjaman/slot`) juga tetap sepenuhnya anonim. **Besaran kerja**: kecil; datanya sudah tersimpan, yang berubah hanya apa yang ikut dikirim.

**Konsekuensi yang diterima sadar**: nama dan divisi pemesan setiap ruang kini terlihat oleh seluruh karyawan perusahaan yang sama. Ini pelonggaran privasi yang nyata dan disebutkan terbuka kepada pemilik produk sebelum diputuskan, bukan efek samping yang baru ketahuan kemudian.

## Deskripsi

*Amandemen [[ADR - 0094 Booking Ruang lewat MyBharata, Penyetuju Ditunjuk HR, Satu Sumber Ruang Kantor]] §7: `GET /peminjaman/jadwal` yang dibaca seluruh karyawan kini memancarkan `pemohon_nama` dan `divisi` selain ruang, tanggal, dan jam. Batas `ga.view` tidak dihapus, hanya digeser: keperluan, nomor WA, nomor booking, posisi, dan riwayat keputusan tetap di baliknya. `GET /peminjaman/slot` tidak berubah. Keputusan lain ADR 0094 tetap berlaku.*

- **Status**: 🟡 **Diterima, belum di prod**. Kode bip-erp branch `feat/jadwal-ruang-identitas`, layar MyBharata branch `feat/jadwal-ruang-tampilan`. Status yang bergerak (PR, deploy) sengaja tidak dicatat di sini; ukur ulang dengan `gh pr list` dan `docker images` saat dibutuhkan.
- **Path di repo**:
  - `bip-erp/services/inventory/peminjaman_slot.go` (struct `JadwalTerpakai`, `jadwalTerpakaiDari`)
  - `bip-erp/services/inventory/peminjaman_handler.go` (`handleJadwalRuang`)
  - `bip-erp/services/inventory/peminjaman_jadwal_publik_test.go` (test pematok)
  - `mybharata-app/lib/src/features/room_booking/` (entity, model, dan layar Jadwal Ruang)
- **Tanggal**: 2026-09-22

## Context

- [[ADR - 0094 Booking Ruang lewat MyBharata, Penyetuju Ditunjuk HR, Satu Sumber Ruang Kantor]] §7 menetapkan jadwal seluruh perusahaan **beserta identitas pemohon** milik pemegang `ga.view`, dan catatan 2026-09-22 di dalamnya menyatakan `GET /peminjaman/jadwal` memancarkan ruang, tanggal, dan jam saja. Keterbukaan rute itu disetarakan dengan `GET /peminjaman/slot` justru **karena** tak beridentitas.
- Identitas pemohon (`pemohon_nama`, `divisi`, `posisi`) **sudah tersimpan** di `ga_peminjaman`, dibekukan dari stempel gateway saat booking diajukan (`peminjaman_pengajuan.go`, dipetakan di [[REF - Kepemilikan Data]] §Salinan). Jadi keputusan ini tidak menambah fakta baru dan tidak memanggil employee-service; yang berubah hanya apa yang ikut terkirim.
- Dua test mematok ketiadaan identitas: `TestJadwalTerpakaiTanpaIdentitas` (daftar field persis) dan `TestJadwalRuangTerbukaTanpaIzinGaView` (memindai badan respons mentah, termasuk kata `divisi`). Keduanya sengaja dibuat supaya penambahan field identitas jadi merah, bukan bocor diam-diam.
- **Alur pengguna yang terputus** (`plan-checklist.md` §1b): ia melihat ruang terpakai, dan langkah berikutnya, yaitu menanyakan ke pemesannya, hidup **di luar aplikasi tanpa satu pun tautan atau petunjuk**. Ini bentuk putus "langkah berikutnya di modul lain tanpa tautan", dengan kasus ekstrem: modul berikutnya bukan modul mana pun.
- Prinsip tiga lapis kalender ([[Microservices - Calendar Service]]) melarang data pribadi orang lain masuk kalender. Jadwal ruang **bukan** kalender: ia bukan agenda pribadi siapa pun melainkan keadaan sumber daya bersama milik kantor, dan ia tidak didaftarkan sebagai feed. Booking di kalender terpusat tetap hanya milik pembacanya sendiri, dan itu tidak berubah.

## Decision

### 1. Nama dan divisi ikut, sisanya tidak

`JadwalTerpakai` menjadi enam field: `sumber_id`, `sumber_nama`, `mulai_at`, `selesai_at`, `pemohon_nama`, `divisi`. Yang **tetap** di balik `ga.view` lewat `GET /peminjaman`: `keperluan`, `no_wa`, `nomor`, `posisi`, dan `riwayat`.

Batasnya ditarik di "cukup untuk menghubungi orangnya". Nomor WA tidak ikut karena nama dan divisi sudah cukup untuk menemukan orangnya lewat kanal internal, sementara nomor pribadi yang tersebar tak bisa ditarik kembali. Keperluan tidak ikut karena isi rapat bukan urusan orang yang sekadar mencari ruang kosong.

### 2. `pemohon_nama` dan `divisi` wajib `omitempty`

Booking yang dibuat sebelum identitas dibekukan tak mengisi keduanya. Keynya harus **hilang**, bukan terbit sebagai string kosong: klien merakit baris `Nama · Divisi`, dan nilai kosong yang terkirim membuat layar menggambar pemisah menggantung tanpa satu pun galat. Dipatok `TestJadwalRuangBookingLamaTanpaIdentitasTakMemancarkanKeyKosong`.

### 3. `GET /peminjaman/slot` tidak ikut digeser

Slot dibaca saat **memilih jam**, oleh orang yang belum tentu punya urusan dengan pemesan mana pun, dan ia dipanggil untuk tiap ruang dan tiap tanggal yang dilihat. Membukanya berarti memaparkan identitas jauh lebih luas daripada yang dibutuhkan keputusan ini. `TestSlotRuangTanpaIdentitas` tetap berlaku apa adanya.

### 4. Test pematok diperlebar, bukan dibuang

`TestJadwalTerpakaiTanpaIdentitas` menjadi `TestJadwalTerpakaiHanyaNamaDanDivisi` dan tetap mematok daftar field **persis**, sehingga field identitas **berikutnya** tetap merah.

⛔ `TestJadwalRuangTerbukaTanpaIzinGaView` mendapat **assertion positif** bahwa nama dan divisi benar-benar terkirim. Tanpa itu, melepas kata sapu `pemohon` dan `divisi` dari pemeriksaan kebocoran membuat test tak lagi bisa membedakan "identitasnya sengaja dikirim" dari "identitasnya tak pernah terisi": handler yang berhenti mengisinya akan tetap **hijau**. Pemeriksaan kebocoran juga diperkuat dengan nilai, bukan hanya nama key (`PJR-`, nomor WA fixture, teks keperluan fixture, jabatan fixture).

## Consequences

### Yang membaik

- Orang yang melihat ruang terpakai tahu harus menghubungi siapa, di layar tempat ia menyadarinya. Alurnya selesai di dalam aplikasi.
- Nol perubahan data: tak ada koleksi, field, indeks, env, maupun kategori inbox baru. Hanya `inventory-service` yang naik.
- Nama dan divisi berasal dari snapshot beku, jadi jadwal menyebut divisi **saat ia memesan**, bukan divisinya sekarang. Orang yang pindah divisi tidak membuat jadwal lama jadi salah.

### Yang memburuk atau diterima sadar

- **Nama dan divisi pemesan setiap ruang kini terlihat seluruh karyawan satu perusahaan.** Ini pelonggaran privasi nyata, diputuskan pemilik produk 2026-09-22 setelah disebutkan terbuka. Pilihan yang ditolak: hanya menampilkan identitas untuk booking milik pembaca sendiri (lebih ketat, tetapi tak menyelesaikan masalah aslinya, karena yang perlu dihubungi justru pemesan **lain**).
- **Penyaringan perusahaan jadi satu-satunya batas yang tersisa** di rute ini. Ia sudah ada (`common.CompanyID` di filter) dan dipatok `TestJadwalRuangMeneruskanSaringan`, tetapi sekarang menanggung beban lebih besar daripada sebelumnya.
- **Klien lama tetap aman**: field baru diabaikan pengurai lama. Sebaliknya aplikasi baru di atas backend lama hanya kehilangan barisnya, tanpa galat. Karena itu urutannya tetap **BE sebelum FE**.
- **Description paket izin GA tidak diperbarui**, karena `ga.view` tidak dilonggarkan: yang berubah endpoint publiknya, bukan isi paket izin.

### Yang sengaja tidak dilakukan

- **Nomor WA di jadwal publik**: tidak diminta, dan nomor pribadi yang tersebar tak bisa ditarik kembali.
- **Keperluan di jadwal publik**: isi rapat bukan urusan orang yang mencari ruang kosong.
- **Membuka `/peminjaman/slot`**: dipanggil jauh lebih sering dan oleh pembaca yang belum tentu berkepentingan; paparannya tak sebanding.
- **Tombol hubungi langsung (chat atau telepon) dari kartu jadwal**: butuh kanal kontak yang belum diputuskan, dan menambahkannya menyeret nomor WA kembali masuk.

## Dokumen Terkait

- [[ADR - 0094 Booking Ruang lewat MyBharata, Penyetuju Ditunjuk HR, Satu Sumber Ruang Kantor]]: ADR yang diamandemen (§7)
- [[ADR - 0095 Pengajuan dan Persetujuan Booking Ruang Juga Lewat Web]]: amandemen §2 ADR yang sama
- [[API - Inventory Service]]: kontrak `GET /peminjaman/jadwal`
- [[REF - Kepemilikan Data]]: pemilik fakta identitas pemohon dan sifat snapshot-nya
- [[APP - MyBharata]]: layar Jadwal Ruang
- [[Microservices - Calendar Service]]: prinsip tiga lapis, dan kenapa jadwal ruang bukan kalender
