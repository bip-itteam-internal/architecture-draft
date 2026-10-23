# ADR - 0196 Pelatihan Bisa Dipakai Penuh dari MyBharata, Soal Beragam, Buka Ulang Pre-test, dan Kelas Berulang

> **Status**: 🟢 Diterima, 2026-10-21, oleh irfanarfianto. Pemutus: irfanarfianto. Butir 1-4 dan 7 dipilih Pemutus langsung. Butir 5, 6, dan 8-10 diputuskan orkestrator atas mandat Pemutus ("cari tahu sendiri, jangan tanya saya; bisa dipakai besok"), dengan dasar kode dan pola yang sudah ada; alasannya tertulis per butir supaya bisa ditinjau. Melanjutkan [[HRIS - Training Program]] § Alur Ujian E-Learning (keputusan pemilik proses 2026-09-16) dan [[ADR - 0102 Kesesuaian Materi Dinilai Peserta dan Dampak Pelatihan dari Kenaikan Skor KPI]]. Izin trainer mengikuti pola [[ADR - 0192 Menu MyBharata Digerbang Izin dari Klaim Token seperti Web]].

## Untuk Manajemen

**Apa yang berubah.**
- Peserta bisa menjalani seluruh pelatihan dari HP:
  - menandai hadir;
  - memberi tahu berhalangan;
  - menilai trainer dan materi;
  - mengerjakan pre-test dan post-test.
- Soal ujian tidak lagi hanya pilihan ganda satu jawaban. Ada juga benar/salah, pilihan ganda dengan beberapa jawaban, dan essay yang dinilai HR atau trainer.
- Trainer yang diberi izin boleh menyusun soal untuk semua materi.
- Peserta yang terlewat pre-test tidak lagi buntu: HR bisa membuka ulang pre-test untuk orang itu.
- Pelatihan rutin (mingguan, bulanan, atau tiap beberapa bulan) cukup dibuat sekali. Sistem membuat kelas-kelas berikutnya sendiri.
- Status kelas berganti sendiri sesuai jadwal: Terjadwal → Berlangsung → Selesai. HR tidak perlu lagi menekan "Selesai" supaya post-test dan penilaian terbuka.

**Yang tidak berubah.** Aturan lulus tetap sama: nilai post-test harus lebih tinggi dari pre-test. Sertifikat dan KPI pelatihan tetap mengikuti aturan yang sudah berjalan.

## Context

Diukur 2026-10-21 (riset read-only bip-erp `origin/main` fd63a742, erp-frontend `origin/main` 54dc9436e, mybharata `origin/dev` fda3a903):

- **Sudah ada:**
  - presensi tombol (`POST /me/trainings/:id/attendance`, dengan saklar `attendance_open` yang bawaannya **mati**);
  - penilaian trainer 4 aspek + kesesuaian materi 1-10 (`evaluation.go`);
  - pre/post-test pilihan ganda satu jawaban (`models_course.go:83-89`, `skoring.go`, `me_posttest.go`);
  - layar peserta di MyBharata `dev`.
- **Belum ada:**
  - izin tidak hadir (peserta hanya `Attended bool`);
  - soal benar/salah, multi-jawaban, dan essay;
  - izin khusus trainer (bank soal digerbang `training.manage`, `course.go:284,302`);
  - buka ulang pre-test (pre ditolak bila kelas `Completed`, `skoring.go:125-127`; void tidak menolong);
  - kelas berulang (tidak ada recurrence maupun cron di learning-service);
  - tombol hadir di web peserta;
  - menu "Pelatihan Saya" di sidebar web (dicabut sengaja).
- **Sumber kebingungan yang terukur:**
  - presensi mandiri mati sampai HR menyalakannya;
  - evaluasi dan post-test menunggu HR mengubah status ke Selesai secara manual, dan detik yang sama menutup pre-test;
  - pre-test terlewat = buntu permanen;
  - post-test tinggal di "Riwayat".

## Decision

1. **Trainer penyusun soal lewat izin baru** `training.soal` (paket hak "Penyusun Soal Pelatihan"). Pemegangnya boleh membuat dan mengubah bank soal **semua materi** dan menilai essay. HR (`training.manage`) tetap bisa semuanya. Gerbangnya "manage ATAU soal".
2. **Jenis soal**: `single` (yang ada), `true_false`, `multi`, dan `essay`.
   - `multi` bernilai penuh hanya bila himpunan jawaban **persis** sama dengan kunci; tidak ada nilai parsial.
   - `true_false` adalah pilihan tunggal dengan dua opsi tetap.
   - Soal lama tanpa `type` dibaca sebagai `single`, jadi tidak ada migrasi data.
3. **Essay dinilai manual** oleh pemegang `training.manage` atau `training.soal`.
   - Percobaan yang memuat essay berstatus **Menunggu penilaian**. Skor, kelulusan, dan sertifikat baru dihitung sesudah semua essay dinilai.
   - Pre-test yang memuat essay baru menjadi pembanding sesudah dinilai. Selama menunggu, post-test tetap boleh dikerjakan, tetapi kelulusannya ikut menunggu.
4. **HR membuka ulang pre-test per peserta** (izin `training.work`). Tindakan ini tercatat: siapa, kapan, dan alasannya.
   - Pre-test lama yang terkirim di-void.
   - Peserta lalu boleh pre-test walau kelas sudah Selesai, kemudian post-test.
   - Ini menjawab TBD [[HRIS - Training Program]] :95.
5. **Berhalangan hadir.** Peserta bisa mengirim "Berhalangan" dengan alasan (wajib) sampai kelas selesai.
   - Kehadiran peserta menjadi `hadir | berhalangan | tidak_hadir` (tidak hadir = bawaan bila tidak keduanya).
   - HR tetap bisa mengoreksi.
   - Berhalangan **bukan** presensi kerja dan tidak menyentuh attendance-service. *Alasan:* peserta hari ini hanya punya `Attended bool`, sehingga "tidak datang" tidak bisa dibedakan dari "sudah memberi tahu".
6. **Penilaian materi diperluas**: selain kesesuaian 1-10 (ADR 0102, tidak berubah), peserta menilai **kejelasan** dan **kegunaan** materi (1-5). Keduanya dikirim bersama penilaian trainer, opsional, dan agregatnya tampil di HR. *Alasan:* satu angka kesesuaian tidak cukup untuk "menilai materi"; dua aspek ini adalah inti evaluasi reaksi peserta yang lazim (Kirkpatrick level 1).
7. **Kelas berulang (seri).** HR membuat seri:
   - isinya templat kelas (jenis, materi, trainer, lokasi, jam, kuota, dan peserta bawaan opsional) dan pola (`mingguan` dengan hari, `bulanan` dengan tanggal, `interval` N bulan), dengan tanggal mulai dan akhir opsional;
   - cron learning-service membuat kelas untuk kejadian berikutnya secara idempoten (kunci unik seri + tanggal kejadian), meniru pola `form-builder` (`models_period.go`, `cron.go`, `period_store.go`);
   - kelas hasil seri adalah kelas biasa: pre/post-test, kuota, sertifikat, dan presensi tetap per kelas, dan HR boleh mengubah tiap kelas;
   - menghentikan seri tidak menghapus kelas yang sudah dibuat.
8. **Status kelas berganti otomatis** oleh cron yang sama: Terjadwal → Berlangsung saat jendela mulai, Berlangsung → Selesai saat jendela berakhir (WIB). Kelas Batal tidak disentuh, dan HR tetap boleh mengubah status manual. *Alasan:* semua tahap pasca-kelas (evaluasi, post-test, sertifikat) menunggu status Selesai yang hari ini hanya berubah bila HR ingat; data prod per 2026-09-21 menunjukkan modul nyaris tak dipakai.
9. **Presensi mandiri bawaannya terbuka di jendela kelas.** Saklar `attendance_open` tetap ada untuk HR yang ingin mematikannya. *Alasan:* bawaan mati membuat tombol hadir tampil sebagai teks alasan bagi hampir semua peserta.
10. **Web peserta disetarakan dengan mobile** ⚠️ *dikoreksi, lihat § Amandemen 2026-10-22: menu sidebarnya dicabut lagi.* Layar `/hris/pelatihan-saya` punya tombol hadir dan berhalangan, dan pre-test/post-test tampil di kartu yang sama. Tampilan peserta di kedua klien mengikuti satu urutan langkah:
    1. Hadir/Berhalangan
    2. Pre-test
    3. (kelas berlangsung)
    4. Post-test
    5. Nilai trainer & materi
    6. Sertifikat

    Tiap langkah menyebut keadaannya dengan kalimat: terbuka, terkunci karena apa, atau selesai.

## Amandemen

### 2026-10-22: Menu "Pelatihan Saya" tidak di sidebar web

Diputuskan pemilik produk (irfanarfianto): urusan karyawan atas dirinya sendiri tempatnya **MyBharata**, jadi menu "Pelatihan Saya" **tidak** ada di sidebar web. Bagian butir 10 yang mengembalikan menu itu adalah keputusan orkestrator, bukan Pemutus, dan dibatalkan (erp-frontend, PR pencabutan menu sesudah #2719).

- Rute `/hris/pelatihan-saya` dan layar langkahnya tetap hidup tanpa menu (pola "Interview Saya"), supaya tautan langsung tidak patah.
- Kunci i18n `sidebar.pelatihan_saya` dibuang; test penjaga self-service melarangnya hidup kembali.
- Pelajaran: menu self-service karyawan tidak dikembalikan ke web tanpa keputusan Pemutus, walau layarnya setara.

## Alternatif yang Ditolak

- **Hanya HR menyusun soal / trainer per materi yang diajar.** Pemutus memilih semua materi lewat izin.
- **Nilai parsial multi-jawaban.** Ditolak: lebih rumit dan bisa diakali.
- **Essay tidak memengaruhi nilai.** Ditolak Pemutus.
- **Pre-test tak wajib dengan ambang tetap.** Ditolak: mengubah aturan lulus yang sudah berjalan.
- **Hanya tombol "salin kelas" untuk pelatihan rutin.** Ditolak Pemutus; yang dipilih seri otomatis.
- **Status kelas tetap manual.** Ditolak (butir 8).

## Consequences

- Model `Question`, `Answer`, dan `QuizAttempt` bertambah field. Semua pembaca percobaan harus menyaring status Menunggu penilaian: KPI pelatihan, sertifikat, ekspor CSV, dan penanda layar.
- learning-service mendapat cron pertamanya (WIB), untuk seri dan status otomatis.
- Kehadiran peserta berubah dari `bool` menjadi tiga keadaan. Klien lama yang membaca `attended` tetap jalan karena `attended` dipertahankan (= hadir).
- Katalog izin bertambah `training.soal`.
- MyBharata wajib rilis (version name dan code naik) supaya fitur ini sampai ke peserta.

## Terkait

- [[HRIS - Training Program]] · [[API - Learning Service]] · [[Microservices - Learning Service]]
- [[ADR - 0102 Kesesuaian Materi Dinilai Peserta dan Dampak Pelatihan dari Kenaikan Skor KPI]] · [[ADR - 0109 Penyelenggara Pelatihan Internal atau Eksternal dengan Master Vendor Milik HR dan Bank Sertifikat Dua Sumber]] · [[ADR - 0115 Spreadsheet People and Development Belum Dipindah ke ERP, KPI Ganda Diselesaikan Lebih Dulu]] · [[ADR - 0192 Menu MyBharata Digerbang Izin dari Klaim Token seperti Web]]
