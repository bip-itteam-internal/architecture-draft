# ADR - 0142 Pengisi Penilaian dan Survei Selalu Anonim, IT Membuka Identitas lewat Jalur Audit Bercatatan

> **Status**: 🟢 **Diterima**, 2026-09-29, nol kode. Linear: BHA-360. Arah diputuskan user (Tech Development): pengisi form bertipe penilaian karyawan dan survei disembunyikan, kecuali IT. Rincian pelaksanaan (§Decision butir 2 sampai 4) adalah usulan penulis yang disetujui bersamaan ("buat sekalian"); butir yang masih boleh diubah tanpa ADR baru ditandai di §Pertanyaan terbuka. Nomor 0142 diklaim saat push; bila sudah terpakai, geser ke nomor bebas berikutnya.

%% Status di blockquote atas supaya terbaca VAULT-INDEX.json (15 baris pertama), pola sama dengan ADR 0136 sampai 0141. %%

%% Vault ini PUBLIK. Nama orang dan employee_id tidak ditulis; yang disebut hanya tipe form, departemen pemilik, dan angka agregat. %%

## Untuk Manajemen

**Masalahnya dalam satu kalimat.** Kerahasiaan pengisi form hari ini bergantung pada **satu saklar yang harus diingat pembuat form**, bawaannya mati, sehingga di prod seluruh survei (7 form, 3 di antaranya sedang berjalan) dan satu form penilaian menampilkan nama pengisinya ke siapa pun yang bisa membuka hasil form.

**Yang diputuskan.** Untuk dua tipe form, **penilaian karyawan** dan **survei**, identitas pengisi **selalu** disembunyikan dari pengelola form, dan pembuat form tidak bisa mematikannya. **Tim IT** tetap bisa membuka identitas satu jawaban, tetapi hanya lewat aksi audit yang wajib diberi alasan dan tercatat (siapa, kapan, form dan jawaban mana). Pengisi diberi tahu dengan jujur bahwa identitasnya tidak terlihat oleh pengelola form, tetapi bisa dibuka tim IT untuk audit.

**Yang tidak dijanjikan.** Ini bukan anonimitas mutlak: database tetap menyimpan siapa mengisi apa (supaya satu orang tidak mengisi dua kali dan penyalahgunaan bisa ditelusuri). Tipe form lain (checklist, kaizen, laporan) tidak berubah, karena di sana identitas pengisi memang bagian dari pekerjaannya.

## Deskripsi

*Menjadikan anonimitas pengisi sebagai sifat **tipe** form `evaluation` dan `survey`, bukan saklar per form, dan menambah satu jalan baca identitas yang sempit, bercatatan, dan khusus IT. Mekanisme penyembunyian yang sudah ada (`anonimAktif`) dipertahankan sebagai satu pintu; yang berubah hanya apa yang membuatnya menyala dan siapa yang boleh melewatinya.*

- **Tanggal**: 2026-09-29
- **Diukur ke**: bip-erp `origin/main` (`services/form-builder`), erp-frontend `origin/main` (`src/features/form-builder`), mybharata-app `origin/dev` (`lib/src/features/form`); data PROD baca-saja 2026-09-29.
- **Hubungan dengan dok lain**:
  - [[Microservices - Form Builder Service]] §Kerahasiaan meluas ke form tanpa sasaran: mekanisme `subject.anonymous` / `settings.anonymous` dan penentu tunggal `anonimAktif` yang dipertahankan ADR ini. Butir "mencabutnya setelah ada jawaban dibalas 409" tetap berlaku dan kini ditambah: untuk dua tipe ini mencabutnya ditolak kapan pun.
  - [[ADR - 0141 Potret Sasaran Penilaian Form Berulang Diambil Ulang tiap Periode, Beku di Dalam Periode]]: sama-sama menyangkut form penilaian, tidak saling bergantung.
  - [[ADR - 0121 Jadwal Ruang Publik Menyertakan Nama dan Divisi Pemohon]]: contoh keputusan sebaliknya (identitas sengaja ditampilkan) untuk konteks yang bukan penilaian.

## Context

**Mekanisme yang ada (terverifikasi di kode).**

- Dua saklar, sengaja tidak di-OR: form bersasaran penilaian membaca `subject.anonymous`, form tanpa sasaran membaca `settings.anonymous`. Satu penentu `anonimAktif(form)` di `anonim.go`; validasi `validateAnonim` menolak form bersasaran yang memasang `settings.anonymous`.
- Saat aktif, identitas penilai dikosongkan di tiga jalur baca: daftar jawaban (`GET /forms/:id/responses`, `anonymizeResponses`), export CSV (`buildCSV`), dan detail tim layanan. Yang **dinilai** tetap utuh.
- Identitas tetap tersimpan di database.
- Pembaca hasil form: grup rute `/forms` bergerbang `requireFormManager` (modul `it` / `ga`, atau izin `formbuilder.view` dari paket posisi).
- Mencabut anonimitas setelah ada jawaban sudah ditolak (`anonimDicabut`, 409); FE mengunci saklarnya bila tak berhak mencabut.

**Keadaan PROD 2026-09-29.**

| Tipe | Status | Anonim | Form |
|---|---|---|---|
| penilaian (`evaluation`) | published | ya | 2 |
| penilaian | closed | ya | 3 |
| penilaian | closed | tidak | 1 |
| survei (`survey`) | published | tidak | 3 |
| survei | closed | tidak | 4 |

Pemilik form di prod: General Affair, Human Resource, Tech Development. Akun aktif pemegang modul `it`: 9, semuanya tingkat supervisor.

**Celah pemberitahuan.** MyBharata menampilkan pemberitahuan anonim hanya untuk penilaian ("Identitas Anda sebagai penilai tidak ditampilkan pada hasilnya", `evaluationAnonymousNotice`); survei anonim tidak memberi tahu pengisinya sama sekali.

**Kenapa saklar per form tidak cukup.** Bawaannya mati dan bobot keputusannya jatuh ke pembuat form, yang tidak menanggung akibatnya: penilai sejawat dan responden survei yang menanggungnya. Hasilnya terukur di tabel atas: semua survei terbuka.

## Decision

1. **Anonimitas mengikuti tipe.** Form bertipe `evaluation` dan `survey` (termasuk dokumen lama yang `form_type`-nya kosong, yang oleh service sudah diperlakukan sebagai `survey`) **selalu** anonim. `anonimAktif` menjawab `true` untuk dua tipe itu tanpa membaca saklarnya; untuk tipe lain perilakunya tidak berubah. Validasi menolak penyimpanan form dua tipe itu dengan anonimitas mati, supaya dokumen tidak bisa menyimpan keadaan yang berbohong tentang perilakunya.
2. **Berlaku mundur, tanpa menulis ulang dokumen.** Karena ditentukan di `anonimAktif`, form lama (termasuk 3 survei yang sedang berjalan) ikut tersembunyi begitu service baru naik. Arahnya makin tertutup, jadi tidak ada janji lama yang dilanggar.
3. **IT membuka identitas lewat jalur audit, bukan di layar hasil biasa.** Layar hasil, analitik, dan export untuk dua tipe ini tetap anonim **juga bagi IT**. Pemegang modul `it` (tingkat supervisor atau admin, §Pertanyaan terbuka) mendapat satu aksi terpisah "Lihat identitas" per jawaban, yang:
   - wajib menyertakan alasan tertulis;
   - mencatat siapa, kapan, form, jawaban, dan alasannya ke catatan audit yang tidak bisa disunting dari UI;
   - hanya mengembalikan identitas jawaban yang diminta, bukan seluruh daftar.

   Alasan tidak menampilkannya langsung ke IT di layar hasil: tim IT juga pemilik dan pengelola form (5 form di prod dimiliki Tech Development), jadi pengecualian di layar hasil membuat form milik IT tidak anonim sama sekali bagi pemiliknya sendiri, dan tak ada jejak siapa melihat apa.
4. **Pemberitahuan ke pengisi dibuat jujur dan berlaku untuk kedua tipe**: identitas tidak terlihat oleh pengelola form; tim IT dapat membukanya untuk keperluan audit. Kalimat lama ("tidak ditampilkan pada hasilnya") tetap benar tapi menyembunyikan jalur IT, jadi diganti.

## Konsekuensi

- Pengelola form (GA, HR, dan IT sebagai pengelola) kehilangan kemampuan melihat siapa mengisi survei. Tindak lanjut per orang ("orang ini memberi nilai rendah, tanyai dia") tidak lagi bisa dilakukan dari layar hasil; itu memang tujuannya.
- Daftar **siapa yang belum mengisi** (kepatuhan, gerbang presensi) tidak termasuk identitas jawaban dan tidak berubah: yang disembunyikan adalah kaitan orang dengan isi jawabannya, bukan fakta seseorang sudah mengisi.
- Pada form dengan sangat sedikit pengisi, anonimitas tetap bisa ditebak dari konteks (mis. satu-satunya pengisi dari satu departemen). Tidak ditangani ADR ini.
- Urutan deploy: form-builder (BE) lebih dulu, lalu erp-frontend dan MyBharata. FE lama yang masih menampilkan saklar tetap aman karena BE yang memutuskan.

## Pertanyaan terbuka

- **Cakupan "IT"**: default ADR ini pemegang modul `it` tingkat **supervisor atau admin**, gerbang yang sama dengan penetapan aturan tipe form (`requireTypeRulesAdmin`, di luar grup `/forms` karena IT membaca form milik departemen lain). Hari ini 9 akun, seluruhnya supervisor; `it:staff` tidak termasuk. Menyempitkannya ke izin khusus di paket posisi boleh dilakukan tanpa ADR baru, asal jalurnya tetap bercatatan.
- **Siapa yang membaca catatan audit** (mis. HR atau manajemen, untuk mengawasi IT). Belum diputuskan; sampai diputuskan catatan hanya bisa dibaca lewat database.

## Tindak lanjut

- BHA-360: pecahan kerja BE (form-builder), FE (erp-frontend), MyBharata.
