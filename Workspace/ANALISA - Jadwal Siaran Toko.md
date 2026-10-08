# ANALISA - Jadwal Siaran Toko

> ⛔ **Menunggu ADR "Jadwal Siaran Toko Disusun Leader Marketing, Sesi Live yang Tak Sesuai Jadwal Ditolak" Diterima: sebelum itu ANALISA ini BUKAN keputusan yang bisa ditunjuk `/brief`.**

- **ADR**: [[ADR - 0157 Jadwal Siaran Toko Disusun Leader Marketing, Sesi Live yang Tak Sesuai Jadwal Ditolak]]
- **Dok domain**: [[Microservices - Marketing Analytics Service]] § Jadwal Siaran Toko · [[API - Marketing Analytics Service]] · [[APP - Web ERP]] · [[Microservices - Calendar Service]] · [[REF - Kepemilikan Data]]
- **Pemutus**: `irfanarfianto`
- **Dibuat**: 2026-10-08, hasil `/analisa-kebutuhan`; direvisi hari yang sama (tiga kebijakan jadi pengaturan, wewenang jadi izin dengan leader sebagai bawaan)
- **Ukuran**: **Besar**. Dua repo harus berubah (`bip-erp`, `erp-frontend`), dan `bip-erp` butuh empat PR.
	- `erp-frontend` dihitung karena layar pengisinya belum ada (tidak ada pemanggil `live-shifts/akun` maupun layar akun ke toko di `origin/main`).
	- Halaman Kalender di `erp-frontend` **tidak** dihitung: ia merender feed baru secara generik (`src/features/calendar/components/month-view.tsx:62` dan `agenda-list.tsx:129` memakai `deep_link` item apa adanya).
	- `my-bharata` **tidak** dihitung: pemilik produk memutuskan aplikasi tidak diubah; penolakan dan pengingat sampai ke host lewat inbox yang sudah ada.

## Kebutuhan

Yang diminta: jadwal siaran toko. Kebutuhannya: GMV tiap sesi live masuk ke host yang benar tanpa bergantung pada tiap host menebak toko, dan salah catat ketahuan sendiri.

## Urutan

| Urutan | Issue | Repo | Menunggu |
|---|---|---|---|
| Induk | [bip-erp#2790](https://github.com/bip-itteam-internal/bip-erp/issues/2790) | `bip-erp` | tanpa PR sendiri |
| 1 | [bip-erp#2791](https://github.com/bip-itteam-internal/bip-erp/issues/2791) [BE] bagian 1/4 | `bip-erp` | ADR Diterima |
| 2 | [bip-erp#2792](https://github.com/bip-itteam-internal/bip-erp/issues/2792) [BE] bagian 2/4 | `bip-erp` | #2791 |
| 3 | [bip-erp#2793](https://github.com/bip-itteam-internal/bip-erp/issues/2793) [BE] bagian 3/4 | `bip-erp` | #2791 |
| 4 | [bip-erp#2794](https://github.com/bip-itteam-internal/bip-erp/issues/2794) [BE] bagian 4/4 | `bip-erp` | #2791 |
| 5 | [erp-frontend#2184](https://github.com/bip-itteam-internal/erp-frontend/issues/2184) [FE] | `erp-frontend` | #2791 ada di DEV |

Bagian 2, 3, dan 4 saling bebas sesudah bagian 1. Deploy backend sebelum frontend; `calendar-service` dibuat ulang saat bagian 4 naik; employee-service ikut dibangun ulang saat bagian 1 naik (izin baru di katalog).

⚠️ **Sesudah semuanya di PROD, fitur ini belum menolak siapa pun**: mode bawaannya `catat`. Penyalaan `tolak` per departemen oleh leadernya adalah langkah tersendiri, dicatat di issue induk.

## Yang diputuskan pemilik produk (2026-10-08)

1. Pengingat sebelum shift berisi seluruh jadwal siaran hari itu untuk toko-toko host, bukan akun milik host itu saja.
2. Tanggal atau toko yang belum dijadwalkan: host memilih bebas seperti sekarang (kecuali departemennya memilih mode `wajib`).
3. Sesudah terkunci, penyusun masih bisa mengubah jadwal hari itu dengan alasan tercatat.
4. Saat kunci bawaan pukul 00.00 WIB hari D, bisa dimajukan lewat pengaturan.
5. Agenda siaran di kalender tampil untuk host live dan leader departemen pemilik toko.
6. Tiga kebijakan jadi pengaturan per departemen, supaya menggesernya tidak menuntut perubahan kode: mode penegakan, saat kunci, menit pengingat.
7. Wewenang mengisi adalah izin `jadwal.siaran.manage`; leader marketing lolos tanpa dipasangi apa pun.

## Yang sengaja tidak dikerjakan

- Perubahan MyBharata, termasuk perbaikan `_mapMulaiError` supaya pesan server terbaca.
- Penugasan host ke akun (menutup salah akun sepenuhnya).
- Layar pembetulan sesi yang telanjur salah.
- Satu akun untuk dua toko pada tanggal yang sama (terukur 1 dari 160 hari-akun, dan bergantian).

---

# Draf issue

## Induk - bip-erp#2790 - Jadwal Siaran Toko: sesi live dicocokkan dengan jadwal akun per toko

- **Repo tujuan**: `bip-erp`
- **Issue**: https://github.com/bip-itteam-internal/bip-erp/issues/2790
- **Label `Siap Agent`**: belum dipasang; dipasang manusia sesudah ADR Diterima

**Pemutus:** @irfanarfianto
**PIC:** belum ditetapkan

> Issue **induk**, tanpa PR sendiri. Pekerjaannya ada di sub-issue: empat bagian `[BE]` di repo ini dan satu `[FE]` di `erp-frontend`. MyBharata sengaja tidak diubah.

### Masalah

Penjualan sesi live dijodohkan saat dibaca ke siaran TikTok lewat toko, akun, channel, dan waktu (`services/marketing-analytics/live_shift_penjualan.go`, `jodohkanSesiDenganPorsi`). Sesi yang dicatat host dengan toko atau akun yang keliru tidak pernah terjodoh: layar menulis "belum ada data penjualan" selamanya, tanpa galat, dan angka itu dasar KPI live per orang.

Sistem tidak punya tempat menyimpan "akun ini siaran untuk toko itu". Penjaga yang ada (`live_shift_akun_toko.go`, jendela 14 hari) menebaknya dari riwayat, sehingga akun yang sedang pindah toko lolos di dua toko sekaligus.

### Keputusan

ADR **"Jadwal Siaran Toko Disusun Leader Marketing, Sesi Live yang Tak Sesuai Jadwal Ditolak"** (vault `architecture-draft`, folder `Decisions`, nomor 0157). Layak `Siap Agent` sesudah ADR itu berstatus Diterima.

Bentuk singkatnya:
- Pemegang izin `jadwal.siaran.manage` atau leader marketing mengisi per tanggal akun live mana siaran untuk toko mana (satu toko banyak akun, satu akun satu toko per tanggal); bebas diubah sampai saat kunci, sesudahnya wajib beralasan, tanggal lampau terkunci.
- Tiga kebijakan disimpan sebagai pengaturan per departemen, bukan konstanta: mode penegakan (`catat` bawaan · `tolak` · `wajib`), saat kunci, dan menit pengingat. Pada `tolak`, Mulai dan ambil alih yang bertentangan dengan jadwal ditolak 400 dengan pesan yang menyebut pilihan yang benar, dan pesannya dikirim ke inbox host.
- Host diingatkan sebelum shift; penyusun jadwal dikabari sesudah sync bila ada sesi salah toko; jadwal tampil di Kalender web ERP.

### Yang harus benar

- [ ] Kelima sub-issue selesai dan merged.
- [ ] Di DEV, lewat gateway, mode `catat` (bawaan): leader menjadwalkan satu akun untuk toko A pada hari ini, lalu Mulai dengan akun itu di toko B berhasil 201 dan sesinya membawa `selisih_jadwal`.
- [ ] Di DEV, sesudah mode diganti ke `tolak` dari layar: permintaan yang sama dibalas 400 yang menyebut toko A, dan inbox pemanggil menerima pesan yang sama. Tidak ada deploy di antara kedua langkah.
- [ ] Di DEV: Mulai dengan akun dan toko yang sesuai jadwal berhasil 201.
- [ ] ⚠️ Sesudah PROD: mode tiap departemen yang memakai jadwal **diganti ke `tolak` oleh leadernya**, dan tanggal penggantiannya ditulis di komentar issue ini. Selama masih `catat`, salah toko tetap lolos dan issue ini belum boleh dianggap terpakai.
- [ ] Di DEV: agenda jadwal siaran tampil di `/calendar` untuk host live departemen pemilik toko dan tidak tampil untuk orang di luar departemen itu.

### Di luar cakupan

- Perubahan apa pun di MyBharata (`my-bharata`).
- Penugasan host ke akun per slot.
- Layar pembetulan sesi yang telanjur salah toko atau salah akun.
- Kategori inbox baru.

### Data / bukti pendukung

Diukur PROD 2026-10-08, `marketing_analytics_db`, 1 September sampai 8 Oktober 2026, 785 sesi TikTok:
- 10 sesi salah toko, seluruhnya akun `carevolution.hub` antara `Beautyhacks.co` (`7495537354419308702`) dan `Beautyhacks.store` (`7495537364189547259`). Pada 4 Oktober tiga host memilih toko berbeda untuk satu siaran yang sama.
- 5 sesi salah akun dengan bukti kuat, porsi GMV sekitar Rp 5 juta; salah toko sekitar Rp 1,3 juta.
- Sync `sync-live-sessions` jalan tiap 48 jam pukul 03.00 WIB, jendela 14 hari (`penjadwal.go:50`, `:71`).

### Prasyarat

ADR di atas berstatus Diterima.

## 1 - bip-erp#2791 - [BE] bagian 1/4: jadwal siaran toko (simpan, baca, kunci H-1, wewenang leader)

- **Repo tujuan**: `bip-erp`
- **Issue**: https://github.com/bip-itteam-internal/bip-erp/issues/2791
- **Label `Siap Agent`**: belum dipasang; dipasang manusia sesudah ADR Diterima

**Pemutus:** @irfanarfianto
**PIC:** belum ditetapkan

> Bagian 1/4 backend. Bagian 2, 3, 4 dan sub-issue `[FE]` menunggu yang ini.

### Masalah

Tidak ada tempat menyimpan "akun live ini siaran untuk toko itu pada tanggal ini". Dibuktikan `git grep` atas `origin/main` 2026-10-08: tidak ada koleksi maupun rute jadwal siaran di `services` dan `shared-library`; Jadwal Host Live di attendance hanya memuat orang dan jam shift.

### Keputusan

ADR **"Jadwal Siaran Toko Disusun Leader Marketing, Sesi Live yang Tak Sesuai Jadwal Ditolak"** §1, §2, §5, §10. Layak `Siap Agent` sesudah ADR itu berstatus Diterima.

- Koleksi `jadwal_siaran_toko` di marketing-analytics: satu dokumen per `(tanggal WIB, channel, shop_id, akun_live)`; satu akun hanya satu toko per tanggal.
- Tanggal D bebas ditulis sebelum saat kunci (bawaan 00.00 WIB tanggal D, bisa dimajukan lewat pengaturan); sesudahnya wajib `alasan` dan berjejak; tanggal lampau ditolak.
- Penulis: pemegang izin baru `jadwal.siaran.manage` **atau** leader marketing; yang bukan IT hanya untuk toko departemennya. Tiga kebijakan (mode, saat kunci, menit pengingat) disimpan sebagai pengaturan per departemen, bukan konstanta.

### Yang harus benar

- [ ] Koleksi `jadwal_siaran_toko` dengan field `tanggal` (`YYYY-MM-DD`, WIB), `channel`, `shop_id`, `akun_live`, `departemen`, `dibuat_oleh`, `dibuat_pada`, `diubah_oleh`, `diubah_pada`. Index unik `(tanggal, channel, akun_live)` dan index baca `(tanggal, shop_id)`, didaftarkan di `index.go`.
- [ ] `GET /jadwal-siaran?dari&sampai[&shop_id]`: rentang memakai `bacaRentangHariWIB` (wajib, maksimal 92 hari, 400 bila tidak sah). Mengembalikan `{"rows": [...]}`, `rows` tidak pernah `null`. Tiap baris memuat `tanggal`, `channel`, `shop_id`, `shop_name`, `akun_live`, `terkunci` (`true` bila tanggal itu hari ini atau lampau menurut WIB).
- [ ] Baca disaring ke toko yang `department_shops.department`-nya sama dengan header `common.Header.Department` pemanggil; supervisor IT melihat semua. Gerbang baca: memegang `jadwal.siaran.manage`, **atau** `common.IsMarketingLeader`, **atau** lolos `common.RequireLiveShiftUser`; selain itu 403.
- [ ] `PUT /jadwal-siaran/:tanggal/toko/:shop_id` dengan body `{"akun_live": ["..."], "alasan": "..."}` mengganti seluruh daftar akun toko itu pada tanggal itu. Daftar kosong menghapus jadwal toko pada tanggal itu. Akun yang berulang di body disimpan sekali.
- [ ] `channel` dan `departemen` distempel server dari `department_shops` (sumber yang sama dengan `channelUntukToko`): toko belum terpetakan 400, master tak terbaca 503. Keduanya tidak diterima dari body.
- [ ] Tiap `akun_live` lolos `segmenAmanPath`; akun yang belum pernah ada di `mart_live_sessions` tetap diterima.
- [ ] Tanggal lampau (WIB) dibalas 400 dan tidak menulis apa pun.
- [ ] Saat kunci tanggal D = 00.00 WIB tanggal D dikurangi `kunci_menit_sebelum_hari` milik departemen toko itu. Sesudah saat kunci, tulis tanpa `alasan` (kosong sesudah di-trim) dibalas 400. Dengan `alasan`, perubahan tersimpan dan tepat satu dokumen masuk `jadwal_siaran_toko_jejak` berisi tanggal, toko, isi sebelum, isi sesudah, alasan, pelaku, dan waktu.
- [ ] Sebelum saat kunci, tulis tersimpan tanpa `alasan` dan tanpa dokumen jejak.
- [ ] `terkunci` di balasan `GET /jadwal-siaran` dihitung dari saat kunci yang sama (satu fungsi), bukan dari perbandingan tanggal terpisah.
- [ ] Izin baru `jadwal.siaran.manage` didaftarkan di katalog modul `jadwal` (`shared-library/common/catalog_jadwal.go`) dan di **setiap** tempat lain yang memuat `jadwal.hostlive.manage` sebagai entri katalog (cari dengan `git grep`), dengan label dan deskripsi sendiri.
- [ ] Gerbang tulis: memegang `jadwal.siaran.manage` **atau** `common.IsMarketingLeader`. Ada test bahwa pemegang izin tanpa peran leader lolos, leader tanpa izin lolos, dan orang tanpa keduanya dibalas 403.
- [ ] Pemanggil bukan supervisor IT yang menulis toko di luar departemennya dibalas 403, siapa pun dia.
- [ ] Koleksi `jadwal_siaran_pengaturan`, satu dokumen per `departemen` (index unik), field `mode`, `kunci_menit_sebelum_hari`, `menit_pengingat`, `diubah_oleh`, `diubah_pada`.
- [ ] Satu fungsi pembaca pengaturan mengembalikan nilai bawaan bila dokumen belum ada: `mode` = `catat`, `kunci_menit_sebelum_hari` = 0, `menit_pengingat` = 10. Bila pengaturan gagal dibaca, nilai bawaan dipakai dan dicatat di log.
- [ ] `GET /jadwal-siaran/pengaturan` mengembalikan ketiga nilai untuk departemen pemanggil, ditambah `selisih_7_hari` (jumlah `live_shifts` tujuh hari terakhir di toko departemen itu yang punya `selisih_jadwal`; 0 bila field itu belum pernah ditulis). Gerbang sama dengan `GET /jadwal-siaran`.
- [ ] `PUT /jadwal-siaran/pengaturan` menyimpan ketiga nilai untuk departemen pemanggil, gerbang sama dengan tulis jadwal. Ditolak 400: `mode` di luar `catat`/`tolak`/`wajib`; `kunci_menit_sebelum_hari` di luar 0 sampai 1.440; `menit_pengingat` di luar 5 sampai 120 atau bukan kelipatan 5. Tiap perubahan menulis satu dokumen jejak berisi nilai sebelum dan sesudah.
- [ ] `/jadwal-siaran/pengaturan` didaftarkan **sebelum** rute ber-parameter di prefiks yang sama, dan ada test bahwa `GET /jadwal-siaran/pengaturan` membalas bentuk pengaturan, bukan daftar jadwal.
- [ ] Akun yang pada tanggal dan channel itu sudah dijadwalkan untuk toko lain dibalas 409 dengan pesan yang menyebut **nama** toko itu (`namaTokoUntukPesan`), dan tidak ada baris yang berubah.
- [ ] Identitas penulis dari header gateway, tidak dari body.
- [ ] Rute didaftarkan tanpa prefiks modul (gateway membuang `/api/marketing-analytics`), dan rute literal didaftarkan sebelum saudara ber-parameter.
- [ ] `mongodb.DB == nil` menghasilkan galat terbaca, bukan panik.
- [ ] Ada test `app.Test(httptest.NewRequest(...))` untuk tiap balasan 400, 403, dan 409 di atas, dan test fungsi murni untuk saat kunci: kemarin, hari ini, besok, dengan zona WIB, untuk `kunci_menit_sebelum_hari` 0 dan 420.

**Deploy:** izin baru masuk katalog di `shared-library`, jadi employee-service ikut dibangun ulang bersama marketing-analytics-service.

### Di luar cakupan

- Penjaga saat Mulai dan ambil alih (bagian 2/4).
- Pengingat ke host dan pemeriksaan sesudah sync (bagian 3/4).
- Feed kalender (bagian 4/4).
- Layar web (`erp-frontend`).

### Data / bukti pendukung

- Pola gerbang izin berdampingan dengan peran yang sudah ada: `gerbangRuteKelolaJadwal` di `services/attendance/hostlive_gate.go:54-82`; konstanta izin `jadwal.hostlive.manage` di `shared-library/common/catalog_jadwal.go:48`.
- Sumber toko per departemen: `departmentShopDoc{department, channel, shop_id, shop_name}` (`services/marketing-analytics/kpi_live.go:557-562`).
- Cara menyaring per departemen pemanggil yang sudah ada: `tokoDepartemenSesi` dan `c.Get(common.Header.Department)` (`live_support_sesi.go:147-170`).
- Dua toko berbeda bernama identik `Beautyhack's` (`401556928228` dan `7494710464840632749`), jadi semua kunci wajib `shop_id`, tidak pernah nama.

### Prasyarat

ADR di atas berstatus Diterima. Tidak ada issue lain.

## 2 - bip-erp#2792 - [BE] bagian 2/4: Mulai dan ambil alih sesi live dicocokkan dengan jadwal siaran, penolakan dikirim ke inbox host

- **Repo tujuan**: `bip-erp`
- **Issue**: https://github.com/bip-itteam-internal/bip-erp/issues/2792
- **Label `Siap Agent`**: belum dipasang; dipasang manusia sesudah ADR Diterima

**Pemutus:** @irfanarfianto
**PIC:** belum ditetapkan

> Bagian 2/4 backend, sesudah bagian 1/4.

### Masalah

`POST /live-shifts` dan `POST /live-shifts/:id/ambil-alih` menerima toko dan akun pilihan host. Penjaga yang ada (`akunMilikToko`, `services/marketing-analytics/live_shift_akun_toko.go`) berpijak pada riwayat siaran 14 hari, sehingga akun yang sedang pindah toko lolos di dua toko. Diukur PROD 2026-10-08: 10 sesi salah toko antara 1 September dan 8 Oktober lolos lewat sini.

MyBharata (`origin/dev`) tidak menampilkan pesan 400 dari server saat Mulai: `_mapMulaiError` memakai reason phrase HTTP, bukan `data.error`. Aplikasi itu diputuskan tidak diubah.

### Keputusan

ADR **"Jadwal Siaran Toko Disusun Leader Marketing, Sesi Live yang Tak Sesuai Jadwal Ditolak"** §3, §4, §10. Layak `Siap Agent` sesudah ADR itu berstatus Diterima.

- Mulai dan ambil alih dicocokkan dengan `jadwal_siaran_toko` pada tanggal WIB saat permintaan tiba.
- Akibatnya ditentukan `mode` milik departemen toko yang dipilih: `catat` (bawaan) hanya menulis selisih ke sesi; `tolak` menolak yang bertentangan dengan jadwal; `wajib` juga menolak toko tanpa jadwal.
- Saat menolak, pesan yang menyebut pilihan yang benar dikirim juga ke inbox pemanggil, kategori `reminder`.

### Yang harus benar

**Keputusan penjaga** (satu fungsi murni, hasilnya salah satu dari: `sesuai`, `toko_beda`, `akun_tak_terjadwal`, `toko_tanpa_jadwal`, `jadwal_tak_terbaca`):

- [ ] `sesuai`: akun punya baris jadwal hari itu dan tokonya sama dengan `shop_id` di body.
- [ ] `toko_beda`: akun punya baris jadwal hari itu dengan toko lain.
- [ ] `akun_tak_terjadwal`: akun tidak dijadwalkan hari itu, toko yang dipilih punya minimal satu baris jadwal hari itu.
- [ ] `toko_tanpa_jadwal`: akun tidak dijadwalkan dan toko yang dipilih tidak punya jadwal hari itu.
- [ ] `jadwal_tak_terbaca`: pembacaan jadwal gagal. Selalu berakibat perilaku sekarang (`akunMilikToko`) plus satu baris log yang menyebut akun dan toko, pada mode apa pun. Tidak pernah 5xx karena jadwal.

**Akibat per mode** (mode dari pembaca pengaturan bagian 1/4, untuk departemen pemilik toko yang dipilih):

| Hasil | `catat` | `tolak` | `wajib` |
|---|---|---|---|
| `sesuai` | lanjut, `akunMilikToko` **tidak** dijalankan | sama | sama |
| `toko_beda` | lanjut ke `akunMilikToko`; sesi yang lahir membawa `selisih_jadwal` | 400 | 400 |
| `akun_tak_terjadwal` | lanjut ke `akunMilikToko`; sesi yang lahir membawa `selisih_jadwal` | 400 | 400 |
| `toko_tanpa_jadwal` | lanjut ke `akunMilikToko` | lanjut ke `akunMilikToko` | 400 |

- [ ] Tabel di atas terpenuhi untuk kedua belas selnya, diuji sebagai fungsi murni.
- [ ] Pesan 400 `toko_beda`: `{"error": "Akun <akun> hari ini dijadwalkan untuk toko <nama toko jadwal>, bukan <nama toko dipilih>. Pilih toko <nama toko jadwal> lalu ulangi."}`.
- [ ] Pesan 400 `akun_tak_terjadwal`: `{"error": "Akun <akun> tidak dijadwalkan hari ini. Jadwal toko <nama toko> hari ini: <akun, akun>. Hubungi leader bila jadwalnya perlu diubah."}`.
- [ ] Pesan 400 `toko_tanpa_jadwal` (hanya mode `wajib`): `{"error": "Toko <nama toko> belum punya jadwal siaran hari ini. Hubungi leader."}`.
- [ ] `live_shifts.selisih_jadwal` berbentuk `{jenis, shop_id_jadwal}`: `jenis` = `toko_beda` atau `akun_tak_terjadwal`; `shop_id_jadwal` diisi hanya untuk `toko_beda`. Field tidak ditulis sama sekali bila tidak ada selisih (pointer, pola `kesiapan`), dan distempel server, tidak diterima dari body.
- [ ] `konfirmasi_toko: true` tidak melewati penolakan jadwal mana pun.
- [ ] Nama toko di pesan dari `namaTokoUntukPesan`; bila nama tak tersedia jatuh ke `shop_id`.
- [ ] Penjaga berjalan sesudah `channelUntukToko` dan sebelum penjaga sesi ganda (409), di `handleShiftMulai` dan di handler ambil alih, lewat **satu fungsi** yang sama. Ada test yang memeriksa kedua jalur.
- [ ] Tanggal yang dipakai tanggal WIB (`zonaWIB`) saat permintaan tiba; ada test untuk permintaan pukul 23.59 dan 00.01 WIB.
- [ ] Saat menolak karena jadwal, pesan `error` yang sama dikirim ke inbox pemanggil (header identitas gateway) lewat `kirimInbox`, kategori `"reminder"`, judul "Sesi live tidak dimulai". Gagal kirim tidak mengubah balasan 400. Mode `catat` tidak mengirim inbox.
- [ ] Penolakan dengan pemanggil, akun, dan toko yang sama dalam dua menit tidak mengirim inbox kedua.
- [ ] Bentuk body permintaan tidak berubah; klien yang ada tetap bekerja untuk pilihan yang sesuai jadwal.
- [ ] Ada minimal satu test `app.Test` yang menghasilkan 400 jadwal pada mode `tolak`, dan satu yang menghasilkan 201 ber-`selisih_jadwal` pada mode `catat` untuk permintaan yang sama.

### Di luar cakupan

- Perubahan di MyBharata.
- Mengisi `shop_id` dari jadwal (server hanya menolak atau mencatat, tidak mengganti pilihan host).
- Kategori inbox baru.
- Penjaga salah akun yang memeriksa siapa host-nya.
- Layar untuk mengubah mode (sub-issue `[FE]`); rute pengaturannya ada di bagian 1/4.

### Data / bukti pendukung

- Titik sisip: `akunMilikToko` dipanggil di `live_shift_handler.go:515` dan `live_shift_ambil_alih.go:259` (`origin/main` @ `20a3a71`).
- Pengirim inbox: `kirimInbox(employeeID, judul, isi, kategori, rute)` di `live_shift_pengingat.go:143`; kategori `reminder` sudah terdaftar (`:111-130`).
- Field sesi yang distempel server dan tidak ditulis saat nil: `live_shifts.kesiapan` (`live_shift_entity.go`).
- Kasus nyata untuk fixture: akun `carevolution.hub`, toko `7495537354419308702` (Beautyhacks.co) dan `7495537364189547259` (Beautyhacks.store).

### Prasyarat

Bagian 1/4 merged (koleksi `jadwal_siaran_toko`, pembaca jadwal, dan pembaca pengaturan).

## 3 - bip-erp#2793 - [BE] bagian 3/4: pengingat jadwal siaran sebelum shift dan kabar sesi salah toko sesudah sync

- **Repo tujuan**: `bip-erp`
- **Issue**: https://github.com/bip-itteam-internal/bip-erp/issues/2793
- **Label `Siap Agent`**: belum dipasang; dipasang manusia sesudah ADR Diterima

**Pemutus:** @irfanarfianto
**PIC:** belum ditetapkan

> Bagian 3/4 backend, sesudah bagian 1/4.

### Masalah

Host tidak diberi tahu jadwal siaran hari itu, dan jadwal yang keliru (atau sesi yang lolos pada tanggal tanpa jadwal) baru ketahuan lewat pengecekan manual. Diukur PROD 2026-10-08: sesi salah toko antara 1 September dan 8 Oktober ditemukan seluruhnya dengan kueri manual, berminggu-minggu sesudah terjadi. `shift_tak_terjodoh` hanya angka pasif di respons; tidak ada notifikasi (`git grep` atas `origin/main`: tidak ada pengiriman inbox untuk sesi tak terjodoh).

### Keputusan

ADR **"Jadwal Siaran Toko Disusun Leader Marketing, Sesi Live yang Tak Sesuai Jadwal Ditolak"** §6, §7, §10. Layak `Siap Agent` sesudah ADR itu berstatus Diterima.

- Sebelum jam mulai shift-nya (bawaan sepuluh menit, diatur per departemen), host menerima satu inbox `reminder` berisi jadwal siaran hari itu.
- Sesudah `sync-live-sessions` sukses, tiap sesi salah toko dikabarkan sekali ke penyusun jadwal toko itu.
- Tidak ada kategori inbox baru.

### Yang harus benar

**Pengingat sebelum shift**

- [ ] Tik latar berselang lima menit, dipasang di `main.go` dengan pola `jalankanTutupOtomatis`; `mongodb.DB == nil` tidak memanik.
- [ ] Daftar host = `employee_id` berbeda pada `live_shifts.host[]` dengan `mulai` dalam 30 hari terakhir.
- [ ] Jam mulai shift hari ini dari `GET /internal/jadwal-resolusi` attendance, maksimal 100 id per panggilan. Host yang `off_duty`, tak ditemukan, atau gagal diresolusi dilewati tanpa galat.
- [ ] Inbox dikirim bila jam mulai shift berada dalam `menit_pengingat` ke depan dari saat tik. `menit_pengingat` dibaca dari pembaca pengaturan bagian 1/4 untuk departemen toko-toko host; bila host punya toko di lebih dari satu departemen, dipakai nilai terbesar. Tidak ada angka menit yang ditanam di kode selain nilai bawaan milik pembaca pengaturan.
- [ ] Ada test bahwa mengubah `menit_pengingat` dari 10 ke 30 menggeser saat kirim tanpa perubahan kode lain.
- [ ] Toko untuk seorang host = toko-toko milik departemen (menurut `department_shops`) dari toko tempat ia bersiaran dalam 30 hari terakhir.
- [ ] Isi inbox: judul "Jadwal siaran hari ini", isi satu baris per toko berbentuk "<nama toko>: <akun, akun>", terurut nama toko, hanya toko yang punya jadwal hari itu.
- [ ] Tidak ada jadwal hari itu untuk toko-toko host: tidak ada inbox.
- [ ] Sekali per host per tanggal WIB, dijaga penanda tersimpan (koleksi `jadwal_siaran_pengingat`, unik `(tanggal, employee_id)`), sehingga service yang restart tidak mengirim ulang.
- [ ] Kategori `"reminder"`.

**Kabar sesi salah toko sesudah sync**

- [ ] Dijalankan di akhir `liveSessionsJob.JalankanJendela` hanya bila sync sukses penuh.
- [ ] Sesi yang diperiksa: `selesai` terisi, `mulai` di dalam jendela sync, channel TikTok, belum punya `notif_salah_toko_pada`.
- [ ] Sebuah sesi dikabarkan bila tidak ada siaran `mart_live_sessions` berakun sama di tokonya yang beririsan waktu, **dan** ada siaran berakun sama di toko lain yang beririsan waktu. Aturan irisan dan penolakan sesi menggantung sama dengan `jodohkanSesiDenganPorsi`.
- [ ] Sesi yang tak terjodoh tanpa siaran di toko mana pun tidak dikabarkan.
- [ ] Penerima: `diubah_oleh` jadwal toko tercatat pada tanggal sesi; bila tak ada, `diubah_oleh` jadwal terbaru toko itu; bila tak pernah ada, tidak dikirim dan dicatat satu baris log.
- [ ] Isi inbox menyebut akun, tanggal dan jam mulai sesi (WIB), nama toko yang dicatat, dan nama toko tempat siarannya tercatat di TikTok.
- [ ] Sesudah terkirim, `notif_salah_toko_pada` diisi lewat `PerbaruiSebagianDenganFilter`; sync berikutnya tidak mengabarkan sesi yang sama.
- [ ] Kegagalan pemeriksaan tidak menggagalkan job sync dan tidak mengubah `sync_state`.
- [ ] Deteksi diuji sebagai fungsi murni dengan empat fixture: terjodoh (tidak dikabarkan), tak terjodoh dengan siaran di toko lain (dikabarkan), tak terjodoh tanpa siaran (tidak), sudah bertanda (tidak).
- [ ] `notify_category_test.go` tetap hijau tanpa menambah kategori.

### Di luar cakupan

- Kabar untuk sesi salah **akun** (buktinya tidak pasti).
- Membetulkan sesi secara otomatis.
- Mengubah frekuensi sync.
- Perubahan di attendance-service, employee-service, notification-service, dan MyBharata.

### Data / bukti pendukung

- Sync: tiap 48 jam pukul 03.00 WIB, jendela 14 hari (`penjadwal.go:50`, `:71`, `:73`); akhir job di `sync_live_sessions.go:139-147`.
- Resolusi jadwal: `live_shift_jadwal.go:231-241` (timeout 3 detik), field `employee_id, schedule_id, start, end, off_duty, ditemukan` (`:16-27`).
- Diukur PROD 2026-10-08 sebelum pembetulan manual: kueri deteksi dengan aturan di atas menemukan 10 sesi (seluruhnya `carevolution.hub`); sesudah pembetulan 0.
- Shift host live bisa melintasi tengah malam, sehingga resolusi sesi live memeriksa hari ini dan kemarin (`live_shift_jadwal.go:304-323`).

### Prasyarat

Bagian 1/4 merged.

## 4 - bip-erp#2794 - [BE] bagian 4/4: jadwal siaran toko masuk kalender terpusat

- **Repo tujuan**: `bip-erp`
- **Issue**: https://github.com/bip-itteam-internal/bip-erp/issues/2794
- **Label `Siap Agent`**: belum dipasang; dipasang manusia sesudah ADR Diterima

**Pemutus:** @irfanarfianto
**PIC:** belum ditetapkan

> Bagian 4/4 backend, sesudah bagian 1/4.

### Masalah

Host perlu melihat jadwal siaran, dan MyBharata tidak diubah. Aturan tim mewajibkan fitur bertanggal mendaftarkan feed ke calendar-service, bukan membuat halaman kalender sendiri. Marketing-analytics belum menjadi sumber kalender: `providerRegistry` (`services/calendar/providers.go:33-49`) tidak memuatnya, dan service itu tidak punya rute `calendar-feed` (`git grep` atas `origin/main` 2026-10-08).

### Keputusan

ADR **"Jadwal Siaran Toko Disusun Leader Marketing, Sesi Live yang Tak Sesuai Jadwal Ditolak"** §8. Layak `Siap Agent` sesudah ADR itu berstatus Diterima.

- Marketing-analytics menyediakan `GET /internal/calendar-feed?from&to` ber-`kind: jadwal_siaran`, satu item per tanggal per toko, seharian.
- Item hanya untuk pemakai sesi live dan leader marketing, dan hanya toko departemen pemanggil.
- Halaman kalender di frontend tidak berubah.

### Yang harus benar

- [ ] `providerRegistry` mendapat satu baris: `Key: "marketing-analytics"`, `Label: "Jadwal Siaran"`, `EnvVar: common.Env.MarketingAnalyticsModuleURL`.
- [ ] Blok `calendar-service` di `docker-compose.yml` mendapat `MARKETING_ANALYTICS_MODULE_URL`, tanpa kunci YAML ganda (gerbang compose pre-push lolos).
- [ ] URL sumber kosong membuat provider dilewati, bukan panik (perilaku registry sekarang; tidak lewat `ValidateInternalURL`).
- [ ] `GET /internal/calendar-feed?from&to` di marketing-analytics mengembalikan item berbentuk sama dengan feed lain (lihat dok vault "Microservices - Calendar Service" § Bentuk item).
- [ ] Satu item per `(tanggal, shop_id)` yang punya jadwal dalam rentang: `id` = `marketing-analytics:jadwal_siaran:<tanggal>:<shop_id>`, `kind` = `jadwal_siaran`, `all_day` = `true`, judul "Siaran <nama toko>: <akun, akun>" dengan akun terurut, `deep_link` = `/marketing/jadwal-siaran-toko?tanggal=<tanggal>`.
- [ ] Identitas pemanggil diperiksa di handler; tanpa identitas ditolak. `/internal/` tetap diteruskan gateway dari internet, jadi tidak boleh diperlakukan privat.
- [ ] Pemanggil yang bukan leader marketing dan tidak lolos `RequireLiveShiftUser` menerima nol item (bukan galat).
- [ ] Pemanggil hanya menerima toko yang `department_shops.department`-nya sama dengan departemennya; supervisor IT menerima semua.
- [ ] Ada test yang mengunci: orang di luar departemen menerima nol item, dan host live departemen pemilik toko menerima itemnya.
- [ ] `department_shops` gagal dibaca: feed mengembalikan galat yang terbaca, bukan daftar kosong.

### Di luar cakupan

- Perubahan `erp-frontend` (kalender merender feed baru secara generik: `src/features/calendar/components/month-view.tsx:62` dan `agenda-list.tsx:129` memakai `deep_link` item apa adanya).
- Kalender di MyBharata.
- Jam siaran per akun (jadwal hanya per tanggal).

### Data / bukti pendukung

- `MARKETING_ANALYTICS_MODULE_URL` sudah ada di blok `api-gateway` (`docker-compose.yml:145`) dan `employee-service` (`:292`); blok `calendar-service` mulai `:1857` belum memuatnya.
- `common.Env.MarketingAnalyticsModuleURL` sudah ada (`shared-library/common/env.go:111`, `:198`).
- Insiden yang melatari aturan visibilitas: feed cuti dan akhir kontrak pernah memakai RBAC modul asal sehingga supervisor melihat data seluruh karyawan (bip-erp #1047).

### Prasyarat

Bagian 1/4 merged.

**Deploy:** `calendar-service` wajib `docker compose up -d --force-recreate calendar-service` (env dibaca saat container dibuat), dan `marketing-analytics-service` naik lebih dulu.

## 5 - erp-frontend#2184 - [FE] Menu Jadwal Siaran Toko untuk leader marketing

- **Repo tujuan**: `erp-frontend`
- **Issue**: https://github.com/bip-itteam-internal/erp-frontend/issues/2184
- **Label `Siap Agent`**: belum dipasang; dipasang manusia sesudah ADR Diterima

**Pemutus:** @irfanarfianto
**PIC:** belum ditetapkan

### Masalah

Leader marketing tidak punya layar untuk menetapkan akun live mana siaran untuk toko mana. Di `origin/main` 2026-10-08 tidak ada layar yang mengelola pasangan akun live dan toko: Jadwal Host Live (`src/features/marketing/jadwal-host-live/`) hanya memuat orang dan pola shift, dan satu-satunya pembaca `akun_live` di frontend adalah Monitoring Sesi Live yang hanya baca.

### Keputusan

ADR **"Jadwal Siaran Toko Disusun Leader Marketing, Sesi Live yang Tak Sesuai Jadwal Ditolak"** §1, §2, §5, §8, §10 (vault `architecture-draft`). Layak `Siap Agent` sesudah ADR itu berstatus Diterima.

- Menu baru Jadwal Siaran Toko di `/marketing/jadwal-siaran-toko`: per tanggal, toko mana disiarkan akun mana. Satu toko boleh banyak akun.
- Pemegang izin `jadwal.siaran.manage` atau leader marketing menyunting; host live hanya melihat. Backend penentu.
- Di halaman yang sama: tiga pengaturan per departemen (mode penegakan, saat kunci, menit pengingat). Jadwal yang sudah terkunci wajib alasan; tanggal lampau hanya baca.

### Yang harus benar

- [ ] Rute `/marketing/jadwal-siaran-toko`, menu "Jadwal Siaran Toko" di induk Live Support kategori MARKETING, tampil untuk pemegang izin `jadwal.siaran.manage`, leader marketing, dan host live. Izin baru didaftarkan di konstanta izin frontend di samping `jadwal.hostlive.manage` (`src/features/marketing-analytics/constants/izin.ts`), dan pemegang izin yang tidak punya peran marketing tetap melihat menunya.
- [ ] Rentang tanggal bawaan hari ini sampai enam hari ke depan, bisa digeser; data dari `GET /jadwal-siaran?dari&sampai`.
- [ ] Tampilan: satu baris per toko departemen pemanggil, satu kolom per tanggal, tiap sel menampilkan akun yang dijadwalkan. Toko dibedakan dengan `shop_id` sebagai kunci, bukan nama (dua toko bernama `Beautyhack's`).
- [ ] Leader membuka sel untuk menyunting lewat `Sheet` berangka tiga (header tetap, badan menggulir ber-padding, footer aksi). Akun dipilih jamak dari `GET /live-shifts/akun?shop_id=` dan bisa diketik untuk akun yang belum ada di daftar.
- [ ] Menyimpan lewat `PUT /jadwal-siaran/:tanggal/toko/:shop_id`; berhasil memberi umpan balik dan memperbarui sel tanpa muat ulang halaman.
- [ ] Sel yang `terkunci` tetapi belum lampau menampilkan kolom alasan yang wajib diisi sebelum tombol simpan aktif.
- [ ] Sel tanggal lampau dan seluruh sel bagi pemakai yang bukan penyunting hanya baca: tidak ada tombol sunting. Penyunting = pemegang izin `jadwal.siaran.manage` atau leader marketing; backend penentu.
- [ ] Balasan 400, 403, dan 409 dari server menampilkan pesan `error` dari server apa adanya (409 menyebut toko tempat akun itu sudah dijadwalkan).
- [ ] Aksi "Salin dari hari sebelumnya" pada sebuah tanggal mengisi tiap toko dengan jadwal tanggal sebelumnya lewat pemanggilan `PUT` per toko; toko yang gagal disebut namanya, yang berhasil tetap tersimpan.
- [ ] Halaman menampilkan **mode yang sedang berlaku** (`catat` · `tolak` · `wajib`) dengan label yang menjelaskan akibatnya, dan saat mode `catat` menampilkan `selisih_7_hari` dari `GET /jadwal-siaran/pengaturan` ("N sesi dalam 7 hari terakhir tidak sesuai jadwal"), supaya leader tahu penolakan belum menyala.
- [ ] Penyunting dapat mengubah tiga pengaturan lewat `PUT /jadwal-siaran/pengaturan`: mode, saat kunci, dan menit pengingat. Saat kunci diisi sebagai "hari-H" atau "H-1" ditambah jam, lalu dikirim sebagai `kunci_menit_sebelum_hari` (H-1 pukul 17.00 = 420); menit pengingat pilihan kelipatan 5 dari 5 sampai 120.
- [ ] Mengganti mode ke `tolak` atau `wajib` meminta konfirmasi yang menyebut akibatnya bagi host.
- [ ] Bagi pemakai yang bukan penyunting, pengaturan hanya baca.
- [ ] Sel dianggap terkunci dari field `terkunci` milik server, bukan dari perbandingan tanggal di frontend.
- [ ] `?tanggal=YYYY-MM-DD` di URL membuat rentang dimulai dari tanggal itu (tautan dari Kalender). `useSearchParams` berada di dalam `Suspense`.
- [ ] Lima keadaan layar ada: memuat (`Skeleton`, bukan spinner), kosong, galat, sebagian, penuh.
- [ ] Semua teks lewat `t("marketing.jadwalSiaran.*")` di `id.ts` dan `en.ts`; tanggal diformat di render dengan `intlLocale(lang)`.
- [ ] Tidak menambah padding halaman (`Container` sudah memasangnya), tidak menambah prop ke komponen shared, tidak membuat komponen tiruan.
- [ ] `pnpm tsc --noEmit`, `pnpm lint`, `pnpm build` lolos; `pnpm test` tidak menambah kegagalan dibanding baseline yang terpasang.
- [ ] Ada uji untuk: sel hari ini tidak bisa disimpan tanpa alasan, sel lampau tidak punya tombol sunting, dan pesan 409 dari server tampil.

### Di luar cakupan

- Halaman Kalender (`/calendar`): tidak diubah; agenda jadwal siaran datang dari backend.
- Monitoring Sesi Live dan Jadwal Host Live.
- Perubahan di MyBharata.
- Penugasan host ke akun.

### Data / bukti pendukung

- Pola layar terdekat yang sudah ada: Penugasan Live Support (`src/features/marketing/live-support-penugasan/`, `MainTable` + `Sheet`) dan Jadwal Host Live (`src/features/marketing/jadwal-host-live/components/halaman-jadwal-host-live.tsx`).
- `Sheet` yang benar strukturnya: `sheet-rincian-sesi.tsx` di `src/features/marketing/live-support-sesi/components/`.
- Belum ada pemanggil `live-shifts/akun` di frontend; hook-nya dibuat lokal di fitur ini.

### Prasyarat

Sub-issue `[BE] bagian 1/4` (rute `/jadwal-siaran`) merged dan ada di DEV.

**Deploy:** sesudah backend bagian 1/4. Merged lebih dulu boleh, deploy lebih dulu tidak.

