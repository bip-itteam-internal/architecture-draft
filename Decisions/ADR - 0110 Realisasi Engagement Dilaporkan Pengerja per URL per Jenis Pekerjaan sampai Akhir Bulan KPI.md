# ADR - 0110 Realisasi Engagement Dilaporkan Pengerja per URL per Jenis Pekerjaan sampai Akhir Bulan KPI

## Deskripsi

*Jenis pekerjaan dan target dipindah dari tingkat tiket ke tiap target URL, dan pengerja melaporkan angka tercapai (realisasi) per URL per jenis, tetap bisa diperbarui sampai akhir bulan KPI walau Account Specialist sudah menutup tiket. Keputusan ini mewujudkan janji [[ADR - 0058 Tiket Engagement Memakai Koleksi dan State Machine Sendiri]] §1 ("`volume_realisasi` diperbarui per baris saat pengerja melapor") yang rute pelapornya tak pernah dibangun, sehingga metrik KPI Engagement Quantity selalu bernilai 0 tanpa satu pun galat.*

- **Status**: ⚠️ **Kode selesai di branch `feat/engagement-realisasi-per-jenis` (bip-erp dan erp-frontend), belum merge, belum deploy, belum diverifikasi lewat gateway.** Test backend hijau (paket `task-management` seluruhnya, paket `employee` hanya gagal di satu test yang sama-sama gagal di `origin/main`).
- **Tanggal**: 2026-09-21
- **Terkait**: [[Sales - Engagement Team (Modul)]] · [[Microservices - Task Management Service]] · [[API - Task Management Service]] · [[Microservices - Employee Service]] · [[HRIS - Otomasi Skor KPI]] · [[ADR - 0060 Cakupan Keterlihatan Tiket Engagement]] · [[APP - Web ERP]]

## Untuk Manajemen

- **Yang berubah di layar**: form Buat Request tak lagi punya satu kotak centang "Jenis Pekerjaan" untuk seluruh tiket. Tiap URL memilih jenisnya sendiri dan mengisi target per jenis (URL 1 cukup like dan komentar, URL 2 like, share, save, dan komentar). Pengerja membuka detail tiket lalu **Isi Realisasi** per URL per jenis; angkanya bisa diperbarui kapan pun sampai akhir bulan tiket itu ditutup, bahkan sesudah Account Specialist menekan Tutup.
- **Yang berubah di KPI**: Engagement Quantity mulai terisi dari angka yang dilaporkan pengerja. Tiket yang realisasinya **belum dilaporkan tidak dihitung sebagai nol**; ia keluar dari penyebut dan tampil sebagai cakupan ("N dari M tiket ditutup punya target volume dan realisasi yang sudah dilaporkan"). Pengerja yang tak pernah mengisi karenanya tampil "tak terukur" di panel Otomasi KPI, bukan mendapat skor 0.
- **Yang perlu diketahui**: angkanya **klaim pengerja**. Akun boosting adalah akun personal tanpa API, jadi sistem tak punya cara memverifikasinya. Yang tersedia hanya jejak perubahan (siapa mengisi, dari berapa ke berapa) dan Account Specialist yang melihat angkanya saat memverifikasi.
- **Tiket September yang sudah ditutup sebelum rilis** memakai bentuk lama (satu angka per URL, tanpa jenis) dan harus diisi pengerja sebelum 30 September agar terhitung.
- **Besaran kerja**: sedang. Deploy `task-management-service`, lalu `employee-service` (teks saja), lalu frontend. Tanpa env baru, tanpa kategori inbox baru.

## Context

1. **Metrik `quantity` membaca `volume_realisasi / volume_target`, tetapi `EngagementItem.VolumeRealisasi` tak punya penulis.** Diukur 2026-09-21 dengan `git grep` atas `origin/main` di kedua repo: satu-satunya sentuhannya adalah guard `> 0` di `itemBolehDiubah`, penjumlahan KPI, dan pembacaan tombol di layar. Rasio tiap tiket karenanya selalu 0 dan skor Quantity 0 untuk semua orang. Gejalanya senyap: tak ada galat, angkanya wajar.
2. **ADR 0058 §1 menyatakan koleksi baris target terpisah "karena `volume_realisasi` diperbarui per baris saat pengerja melapor"**, tetapi rute pelapornya tak pernah ditulis. Fase A (2026-09-16) sempat menghapus tampilan "x/y" di detail tiket karena angkanya selalu 0.
3. **Jenis pekerjaan milik tiket, padahal satu tiket memuat URL yang meminta kombinasi berbeda.** `EngagementTicket.JenisPekerjaan` satu daftar untuk semua URL. `EngagementItem.Jenis` (satu string) ada tetapi tak pernah dikirim frontend mana pun. Volume target pun satu angka per URL, tanpa pecahan per jenis, sehingga "500 like tetapi 100 komentar" tak bisa dinyatakan.
4. **Tak ada jalan otomatis.** Akun boosting adalah akun personal tanpa API ([[Sales - Engagement Team (Modul)]] § Kendala); tak ada klien mana pun di `services/` yang menarik statistik konten (integrasi TikTok yang ada seluruhnya TikTok Shop). Klaim pengerja satu-satunya masukan yang mungkin.
5. **KPI menghitung tiket `CLOSED`, dan periodenya dari `closed_at` menurut UTC** (`rentangPeriodeEngagement` memakai `time.Parse("2006-01")`), sedangkan nomor tiket memakai WIB. Skor bulanan dibekukan saat penilaian ([[HRIS - Otomasi Skor KPI]]), biasanya awal bulan berikutnya.

## Decision

1. **Rincian per URL.** `EngagementItem.Rincian` memuat `{jenis, volume_target, volume_realisasi}` per jenis. `VolumeTarget`/`VolumeRealisasi` di baris tetap disimpan sebagai **total baris**, ditulis satu fungsi saja (`terapkanRincian`, `engagement_rincian.go`), sehingga KPI, `sinkronVolumeTiket`, dan item lama tak berubah cara bacanya. Item lama **tidak dimigrasi**: bentuk lama (satu pasang angka datar) tetap terbaca dan diisi dengan satu angka, karena target lama tak bisa dipecah per jenis tanpa mengarang.
2. **`jenis_pekerjaan` dan `volume` tiket diturunkan server dari rincian.** Kiriman klien untuk keduanya diabaikan pada bentuk baru; fakta yang bisa diturunkan tak diketik dua kali. Bentuk lama request buat/sunting tetap diterima **sementara** (jendela deploy), tetapi satu tiket tak boleh mencampur keduanya.
3. **Kosakata jenis divalidasi backend** (sembilan nilai, urutan kanonik): komentar, like, share, posting, review, vote, rating, save, lainnya. Sebelumnya tak divalidasi sama sekali. Daftarnya tinggal di dua tempat (backend dan `ENGAGEMENT_JOB_TYPES` di frontend), sama seperti Jenis Konten dan Jenis Komen.
4. **Realisasi lewat `PUT /engagement/tickets/:id/items/:itemId/realisasi`**, satu baris per permintaan (satu `UpdateOne`, atomik). Baris ber-rincian wajib memuat **seluruh** jenisnya, tepat sekali, angka ≥ 0; baris lama menerima satu angka. Isian **nol adalah isian sah**: yang membedakan "belum dilaporkan" dari "dilaporkan nol" adalah `realisasi_diisi_at`, bukan angkanya. Penulisan memakai filter atas keadaan baris **sebagaimana dibaca**, sehingga sunting target yang terjadi di antara membaca dan menulis membalas `409`, bukan tertimpa senyap.
5. **Yang berwenang: pengerja pemegang tiket, dan admin/supervisor yang tiketnya masuk cakupan keterlihatannya** ([[ADR - 0060 Cakupan Keterlihatan Tiket Engagement]]). Requester **tidak**: ia yang memverifikasi hasil, dan mengisi angka pekerjaan yang ia nilai sendiri menghapus alasan pemisahan peran di ADR 0058. Peran diputuskan sebelum status dan jendela, sehingga yang tak berwenang menerima `403`, bukan `409` yang membocorkan bahwa permintaannya hampir berhasil.
6. **Kapan: selama jendela terbuka.** Tiket yang belum `CLOSED` tak punya jendela. Tiket `CLOSED` terbuka sampai akhir bulan tempat KPI menghitungnya, dan bulan itu diturunkan dari **satu** fungsi (`periodeKPIEngagement`, `kpi_engagement.go`) yang juga menjadi dasar `rentangPeriodeEngagement` dan daftar Pekerjaan Saya, bukan ditulis ulang. Admin/supervisor boleh melewati jendela. `ANTRE` dan `CANCELLED` menolak `409`. `CLOSED` tanpa `closed_at` (data cacat, dilewati KPI) dianggap tertutup.
7. **KPI menghitung tiket "terukur" hanya bila target > 0 dan seluruh baris ber-targetnya sudah dilaporkan** (`volumeTiket.Belum == 0`). Rasio per tiket tetap Σrealisasi / Σtarget lintas jenis, tidak dipotong ke 1. Yang belum dilaporkan menjadi cakupan lewat `Cuplikan.CakupanPersen` yang sudah ada, bukan rasio 0. Kontrak JSON `/kpi/engagement` tak berubah; employee-service hanya memperbarui teks Catatan dan galat metrik `quantity`.
8. **Pekerjaan Saya memuat juga tiket `CLOSED` bulan KPI berjalan**, dan tiap tiket berstatus `DONE_BY_TEAM`/`CLOSED` membawa `realisasi_belum_diisi` (jumlah baris ber-target yang belum dilaporkan). Tanpa ini tiket lenyap dari daftar pengerja begitu ditutup pemohon, dan pengerja tak punya jalan masuk untuk mengisi. Syarat `CLOSED` ditaruh di dalam `$and`, karena kunci `$or` tingkat atas dipakai pencarian `q` dan keduanya akan saling menimpa tanpa galat.
9. **Layar tidak menghitung jendelanya sendiri.** `GET /engagement/tickets/:id` membawa `boleh_isi_realisasi`, dari putusan yang sama dengan `PUT`.
10. **Setiap tulis dicatat di log** (aksi `realisasi`, catatan berisi URL dan jenis dari→ke), karena angka ini menentukan skor KPI orang yang mengisinya sendiri.

## Consequences

**Diterima:**

- **Angka realisasi adalah klaim yang tak terverifikasi.** Pengerja bisa menggelembungkan skornya sendiri. Penjaganya cuma jejak log dan Account Specialist yang melihat angkanya saat verifikasi. Bukti (lampiran) tetap TBD: `attachments` tak punya rute pengisi sejak syarat buktinya dilonggarkan, dan metrik `reporting` karenanya terstruktur nol.
- **Jendela isi memakai bulan UTC milik KPI, bukan WIB.** Tiket yang ditutup 31 Agustus 20:00 UTC (1 September 03:00 WIB) terhitung Agustus dan jendelanya berakhir 31 Agustus 23:59:59 UTC, tujuh jam sebelum akhir bulan menurut jam dinding WIB. Memakai WIB di jendela saja akan menerima isian yang oleh KPI dihitung di bulan lain, tanpa galat; memperbaiki atribusi KPI ke WIB adalah keputusan tersendiri.
- **Tiket lama tanpa rincian diisi dengan satu angka**, dan yang belum diisi sampai akhir bulan menjadi cakupan, bukan skor.
- **Total baris disimpan, bukan dihitung ulang**, sehingga satu angka hidup di dua tempat (total dan Σ rincian). Ditahan oleh satu penulis (`terapkanRincian`) dan test yang mengunci invariannya.
- **Tak ada pemberitahuan.** Pengerja yang tak mengisi hanya melihat badge di daftar; kategori inbox baru berarti dua container naik dan tak diminta.
- **Deploy BE sebelum FE.** Frontend baru memanggil rute yang belum ada bila lebih dulu naik.

**Dibuka kembali dari keputusan sebelumnya:**

- ADR 0058 §1 dan [[Sales - Engagement Team (Modul)]] bagian "Cacat yang Diketahui" tak lagi berlaku untuk `volume_realisasi`: field itu kini punya penulis.

## Belum Diputuskan (TBD)

- Apakah menandai tiket **Selesai** mensyaratkan realisasi sudah dilaporkan (sekarang tidak: pengerja sengaja boleh mengisi sesudahnya).
- Apakah atribusi periode KPI (`closed_at` menurut UTC) diselaraskan ke WIB.
- Apakah ada jalur bukti (lampiran) untuk realisasi.
- Kapan jalur bentuk lama pada request buat/sunting dihapus (setelah frontend baru stabil).
