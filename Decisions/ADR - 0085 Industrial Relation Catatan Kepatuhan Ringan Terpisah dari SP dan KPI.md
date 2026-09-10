## Untuk Manajemen

Menambah menu **Industrial Relation** di workspace HR untuk membina budaya kepatuhan ringan di kantor — hal-hal seperti sepatu, lanyard, dan atribut kerja. Petugas HR/IR yang ditunjuk mencatat temuan secara diskret lewat aplikasi MyBharata saat berkeliling di jam kerja; keesokannya rekapnya tampil per departemen. **Supervisor** melihat rekap timnya, dan **tiap karyawan** melihat catatan dirinya sendiri sehingga tahu apa yang perlu dibenahi.

**Apa yang berubah di layar:** satu menu baru di HR (rekap per departemen + daftar catatan), satu menu baru di MyBharata yang hanya muncul untuk petugas yang ditunjuk, dan satu bagian "catatan kepatuhan saya" untuk tiap karyawan.

**Siapa yang terdampak:** petugas HR/IR (mencatat), supervisor tiap departemen (membaca rekap tim), dan seluruh karyawan (membaca catatan dirinya).

**Apa yang TIDAK dijanjikan:** ini **sinyal pembinaan**, bukan hukuman. Ia **tidak** memotong gaji, **tidak** menerbitkan Surat Peringatan otomatis, dan **tidak** masuk ke skor KPI resmi. Tidak ada notifikasi/pengingat harian pada tahap ini (rekap dibaca saat menu dibuka). Catatan ini juga **tidak** tampil di kalender atau feed lintas modul mana pun, karena isinya bersifat pribadi.

**Perkiraan besaran kerja:** sedang. Sebagian besar bahan sudah ada dan dipakai ulang (mesin rekap per-departemen, gerbang akses tiga-arah, pemilih karyawan & unggah foto di MyBharata). Yang benar-benar baru: satu koleksi data catatan, satu katalog jenis pelanggaran yang bisa diedit HR, satu menu HR, dan satu fitur MyBharata. Perlu rilis backend lebih dulu, lalu web, lalu aplikasi mobile.

## Deskripsi

*Modul Industrial Relation mencatat pelanggaran kepatuhan RINGAN (atribut kerja: sepatu, lanyard, dsb.) sebagai **sinyal pembinaan non-sanksi**, disimpan di entitas terpisah dari Surat Peringatan dan dari `kpi_score`. Ia meminjam POLA rekap per-departemen dari KPI dan gerbang visibilitas tiga-arah dari SP, tetapi sengaja **tidak** memakai data keduanya, supaya "sinyal ≠ sanksi ≠ gaji" menjadi batas struktural, bukan sekadar janji. Menyimpang dari kebiasaan menaruh pelanggaran di [[HRIS - Disciplinary (Surat Peringatan)]], dengan alasan yang dicatat di bawah.*

- **Status**: 🟡 **Diusulkan**, rencana disetujui 2026-09-10, kode belum ada. Artefak kerja: `Workspace/ANALISA - Industrial Relation.md`
- **Path di repo**: `bip-erp/services/employee/industrial_relation*.go` (baru) · `bip-erp/shared-library/models/employee/compliance_note.go` (baru) · `erp-frontend/src/features/hris/industrial-relation/*` (baru) · `erp-frontend/src/app/(main)/hris/industrial-relation/page.tsx` (baru) · `my-bharata/lib/src/features/compliance_note/*` (baru)
- **Tanggal**: 2026-09-10

## Context

Manajemen ingin budaya kepatuhan ringan (sepatu, lanyard, atribut) benar-benar dijalankan, dengan umpan-balik yang low-friction. Kalimat pembuka ("catat pelanggaran diam-diam → muncul besok di departemen") adalah **solusi**; kebutuhan di baliknya adalah **coaching loop**, bukan pengawasan rahasia. Wawancara mengunci empat parameter yang membelokkan arsitektur: akibatnya **sinyal pembinaan** (bukan KPI/gaji/SP), pencatatnya **petugas IR/HR khusus**, yang melihat **supervisor + orangnya sendiri**, dan "besoknya" berarti **cukup tak-real-time** (tanpa penahan waktu khusus).

Grounding ke empat repo menemukan dua tulang punggung yang matang tetapi keduanya salah-satu-ekstrem:

1. **Surat Peringatan (`employee_warning`)** sudah punya bentuk yang mirip: kategori pelanggaran + alasan + tanggal + lampiran + pencabutan, plus gerbang baca tiga-arah (`bolehLihatSP`, `SupervisedDepartmentsStrict`). Tetapi seluruh koleksi itu bermuara pada sanksi: `WarningLevel` hanya `SP1/SP2/SP3` (`shared-library/models/employee/warning.go:20-34`), dan komentarnya menegaskan SP bisa berujung PHK. Tidak ada tingkat di bawah SP. `ViolationCategory` adalah enum Go hardcoded enam nilai (`warning.go:54-80`), tidak data-driven, tanpa CRUD.

2. **KPI (`kpi_score` + registry sumber)** punya mesin agregasi per-departemen yang persis pola "rekap H+1" yang diminta (`services/employee/kpi_ringkasan_departemen.go`, pemanasan di `kpi_ringkasan_hangatkan.go`), dan preseden "sinyal perilaku dari data mentah" di `SumberKedisiplinanAbsensi` (`kpi_sumber_kedisiplinan.go`). Tetapi ia menghasilkan **skor resmi**, dan [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]] menetapkan `kpi_score` hanya boleh ditulis lewat satu pintu bergerbang. Memakainya berarti pelanggaran ringan menjadi KPI resmi — bertentangan dengan syarat.

Yang **belum ada di mana pun** (dibuktikan `git grep`): entitas "pelanggaran ringan / observasi non-sanksi", master katalog jenis pelanggaran (tak ada `MasterViolation` di `shared-library/models/employee/models.go`), dan kanal input dari MyBharata untuk petugas HR/IR.

Dua fakta lingkungan ikut membentuk keputusan:

- **Atribut kerja tidak punya dasar sanksi resmi.** `mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md` (sumber kebenaran logika bisnis yang menang atas perilaku sistem) **tidak** memuat pasal apa pun tentang sepatu/lanyard/seragam. Jadi catatan atribut coaching-only **tak bertabrakan** dengan tabel sanksi mana pun — tetapi juga berarti ia kategori baru yang belum bersandar pada Peraturan Perusahaan. Ini justru menguatkan pilihan "sinyal, bukan sanksi".
- **Data pelanggaran ini sensitif.** SP sengaja **tidak** didaftarkan ke [[Microservices - Calendar Service]] karena tidak lolos prinsip tiga-lapis (data pribadi orang lain tak boleh muncul, sekalipun pemanggilnya supervisor). Catatan kepatuhan menghadapi gerbang privasi yang sama.

Pemilik alami sudah ada: jabatan **Culture & Industrial** (HR org-dev), dan [[ADR - 0084 Kehadiran Program Culture via Scan Menggantikan Feedback, plus Master Program]] sudah menetapkan pola "officer mencatat lewat MyBharata saat jam kerja".

## Decision

### 1. Entitas terpisah, bukan tumpangan

Catatan kepatuhan ringan hidup di koleksi baru (`compliance_note`), **bukan** `employee_warning` dan **bukan** `kpi_score`. Alasannya bukan selera: menaruh catatan pembinaan di `employee_warning` mencampur "sinyal" dengan "sanksi bisa-PHK" dalam satu riwayat, persis kelas cacat "satu fakta dua makna" yang berulang di repo ini; menaruhnya di `kpi_score` menjadikannya KPI resmi yang menyentuh gaji. Pemisahan koleksi membuat batas "sinyal ≠ sanksi ≠ gaji" **struktural**, sehingga tak bisa bocor karena satu perubahan kode yang lalai.

### 2. Bukan KPI, bukan SP, bukan gaji — dinyatakan tegas

Modul ini **tidak** menulis `kpi_score`, **tidak** membuat `employee_warning`, dan **tidak** dibaca payroll. Bila kelak diputuskan sebuah pelanggaran ringan yang berulang perlu naik menjadi SP, itu tetap keputusan **manusia** lewat modul SP yang ada (HR menerbitkan, sistem paling jauh mengusulkan) — bukan eskalasi otomatis dari modul ini. Keputusan itu, bila diambil, menuntut ADR tersendiri.

### 3. Jenis pelanggaran = master data, bukan enum

Katalog jenis (sepatu, lanyard, atribut, dsb.) disimpan sebagai **master data** yang bisa ditambah/ubah HR, bukan enum Go hardcoded seperti `ViolationCategory`. Alasannya: daftar ini akan berubah (atribut baru, kebijakan baru) tanpa menuntut deploy, dan sifatnya memang data referensi, bukan aturan sistem. Penulisan katalog digerbang keanggotaan modul HR.

### 4. Pencatat hanya petugas IR/HR yang ditunjuk; ditegakkan di server

Menu pencatatan di MyBharata hanya muncul untuk petugas yang ditunjuk, dan pemunculan menu **bukan** gerbang. `POST` catatan diperiksa di server terhadap wewenang pencatat (mengikuti pola `gateHris`/keanggotaan modul HR). Penyaring di layar bukan gerbang.

### 5. Visibilitas tiga-arah, gerbang tulis tanpa fallback

Baca catatan mengikuti pola SP: **petugas IR/HR** se-perusahaan, **karyawan** atas dirinya sendiri, **atasan** atas anggota departemennya. Cakupan atasan WAJIB memakai `SupervisedDepartmentsStrict` (tanpa fallback `BIP-Department`), supaya rekan sedepartemen tak saling melihat catatan. Filter per-departemen WAJIB lewat `ResolveDepartmentFilter` + `ExpandToDepartmentGroup` (gotcha HRGA — label grup tak pernah cocok dengan `work_data.department` siapa pun).

### 6. Rekap per-departemen dihitung saat baca, meminjam pola KPI

Rekap "muncul besoknya" tidak menuntut cron. Ia dihitung saat menu dibuka, meniru `kpi_ringkasan_departemen.go` (agregasi per-departemen dengan pra-hitung/pemanasan), tetapi atas koleksi `compliance_note`, bukan `kpi_score`. "Besoknya" cukup dijamin oleh cara membaca (rekap harian menampilkan tanggal-tanggal yang sudah lewat), bukan penahan waktu khusus.

### 7. Sensitif — tidak masuk kalender atau feed lintas modul

Mengikuti preseden SP, catatan ini **tidak** didaftarkan ke [[Microservices - Calendar Service]] maupun feed lintas modul lain. "Boleh diakses" bukan "layak muncul di tempat lain".

### 8. Catatan boleh hangus, dan `Reason`/bukti dianjurkan wajib

Agar catatan tak menumpuk selamanya dan tetap bersifat pembinaan, status "aktif/hangus" sebaiknya **diturunkan saat baca** dari sebuah masa berlaku (pola `WarningStatus` yang tak menyimpan status). `Reason` dan/atau foto bukti sebaiknya wajib, sebagai rem penyalahgunaan pencatatan diskret.

## Consequences

### Yang membaik

- Budaya kepatuhan ringan punya kanal umpan-balik tanpa harus melewati jalur sanksi berat.
- Supervisor dan karyawan melihat hal yang sama (rekap tim / catatan diri), sehingga perbaikan bisa langsung.
- Riwayat SP dan skor KPI tetap bersih dari catatan pembinaan.

### Yang memburuk atau tetap terbuka

- ⚠️ **Kategori pelanggaran atribut belum bersandar pada Peraturan Perusahaan.** Ia sah sebagai pembinaan, tetapi bila kelak dituntut jadi dasar sanksi, perlu pasal PP dan ADR baru.
- **Pencatatan diskret atas rekan kerja membawa bobot privasi.** Ditahan oleh: pencatat terbatas & tercatat, orangnya selalu bisa melihat catatan dirinya, `Reason`/bukti dianjurkan wajib, dan tidak ada penyebaran lintas modul. Bila salah satu rem itu dilepas, isunya kembali.
- **Tiga permukaan harus dijaga selaras** (BE, Web, MyBharata). Perubahan kontrak menuntut BE lebih dulu.

### Yang sengaja tidak dilakukan

- **Tidak ada eskalasi otomatis ke SP.** Naik ke SP tetap keputusan manusia lewat modul SP.
- **Tidak masuk KPI resmi.** Tidak menulis `kpi_score`; menjadikannya sumber KPI ditolak karena bertentangan dengan sifat "sinyal".
- **Tidak ada notifikasi/pengingat harian** pada irisan pertama. Karena coaching-only + non-real-time, rekap cukup dibaca saat menu dibuka. Menambahkannya berarti kategori inbox baru (deploy notification-service + service pengirim bersama) dan ADR/revisi tersendiri.
- **Mesin alur yang bisa dikonfigurasi** dan katalog yang generik lintas-perusahaan ditolak sampai ada pemakai nyata ketiga.

## Dokumen Terkait

- [[HRIS - Industrial Relation]] — cara kerja modulnya (dok domain); daftar task di `Workspace/ANALISA - Industrial Relation.md`
- [[HRIS - Disciplinary (Surat Peringatan)]] — jalur sanksi yang keputusan ini sengaja jauhi; sumber pola visibilitas tiga-arah
- [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]] — kenapa modul ini tak menulis `kpi_score`
- [[HRIS - Key Performance Index]] — sumber pola rekap per-departemen (dipinjam polanya, bukan datanya)
- [[HRIS - Conflict Management]] — tetangga fungsi "Industrial Relation" (kasus/perselisihan), masih konsep
- [[ADR - 0084 Kehadiran Program Culture via Scan Menggantikan Feedback, plus Master Program]] — pola officer mencatat via MyBharata saat jam kerja
- [[Microservices - Calendar Service]] — prinsip tiga-lapis; kenapa catatan sensitif tak masuk feed
- [[HRIS - Kepatuhan Peraturan Perusahaan]] — kenapa atribut belum bersandar pada PP
- [[Microservices - Employee Service]] · [[APP - MyBharata]] · [[APP - Web ERP]]
