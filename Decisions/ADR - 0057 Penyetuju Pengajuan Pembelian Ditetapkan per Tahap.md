## Deskripsi

*Penyetuju tiap tahap Pengajuan Pembelian ditetapkan dari layar master, dan penunjukan itu MENYEMPITKAN himpunan yang sudah dibuka RBAC, tidak pernah memberi hak. Menyimpang dari [[ADR - 0055 Pengajuan Pembelian Empat Tipe Menggantikan Pengajuan Budget]] §7 yang menolak matriks terkelola terpisah, dengan alasan yang dicatat di bawah.*

- **Status**: 🟡 **Diusulkan**, rencana disetujui 2026-08-27, kode belum ada. Artefak rencana: `.task-plans/2026-08-27-pembelian-penyetuju-tahap.md`
- **Path di repo**: `bip-erp/services/procurement/pengajuan_pembelian_penyetuju*.go` (baru) · `bip-erp/services/employee/permission_holders.go` (baru) · `erp-frontend/src/features/procurement/pembelian/components/pengaturan-penyetuju.tsx` (baru)
- **Tanggal**: 2026-08-27

## Context

[[ADR - 0055 Pengajuan Pembelian Empat Tipe Menggantikan Pengajuan Budget]] §7 memutuskan bahwa wewenang tiap tahap ditentukan izin RBAC per tipe, dan menolak "matriks tipe x departemen yang dikelola terpisah" dengan alasan bahwa matriks semacam itu menjadi sumber kebenaran kedua di samping RBAC. Keputusan itu benar untuk pertanyaan yang dijawabnya, yaitu *siapa yang BOLEH*.

Yang tidak dijawabnya adalah pertanyaan operasional: *siapa yang MENGERJAKAN tahap ini*. Perbedaannya baru terasa setelah modulnya dipakai:

1. **Notifikasi tidak punya alamat.** Rantai delapan tahap berjalan tanpa satu pun pemberitahuan kecuali `pembelian-qc-gagal`. Untuk mengirimkannya, sistem harus tahu ke siapa, dan RBAC hanya bisa menjawab "siapa saja yang memegang izin ini", bukan "siapa yang bertanggung jawab".
2. **Menurunkan penerima dari atasan departemen salah sasaran.** Tahap `procurement_beli`, `ap`, `qc`, `terima_ga`, dan `terima_rm` dikerjakan STAF, bukan atasan. Resolver atasan yang dipakai [[REF - Alur Persetujuan]] cocok untuk `spv_divisi`, tetapi mengirim pekerjaan gudang ke supervisornya berarti loop yang tidak pernah tertutup.
3. **Pemilik proses memintanya eksplisit** (2026-08-27): penyetuju tiap tahap harus dapat ditetapkan dari layar, dan orangnya tidak harus ber-`is_supervisor`.

Pemeriksaan kode untuk keputusan ini menemukan bahwa bahannya sudah lengkap dan tidak ada izin baru yang perlu dibuat: `shared-library/common/catalog_budget.go` sudah memuat izin per tahap (`budget.approve.atasan`, `.finance`, `.direksi`, `.procurement`, `budget.approve.pembayaran`, `budget.ap.bayar`, `budget.qc.periksa`, `budget.terima.ga`, `budget.terima.rm`) dan `budget.master.save` untuk pengelola masternya.

Yang belum ada: **cara membaca izin orang lain**. `izinKaryawan` di employee-service hanya dipanggil di empat jalur penerbitan token, tidak pernah sebagai pembacaan.

## Decision

### 1. Penunjukan menyempitkan, tidak pernah memberi hak

Boleh menindak sebuah tahap = **memegang izin RBAC tahap itu DAN termasuk yang ditunjuk**. Karena izin tetap menjadi prasyarat, penunjukan secara struktural tidak dapat melahirkan kebocoran hak: ia hanya mengecilkan himpunan yang sudah dibuka RBAC. Inilah yang membedakannya dari matriks yang ditolak ADR-0055 §7, yang akan menjadi sumber wewenang **sejajar**.

Konsekuensinya, layar pengaturan ini tidak boleh dipakai sebagai jalur pemberian hak. Pemberian izin tetap milik IT lewat permission set ([[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]).

### 2. Tiga aturan jatuh-balik supaya tidak ada dokumen yang mandek

- Tahap **tanpa penunjukan** jatuh ke seluruh pemegang izin, yaitu perilaku sebelum keputusan ini. Layar yang belum diisi tidak boleh mematikan rantai.
- Tahap **`spv_divisi`** tidak ditunjuk sama sekali. Ia per departemen pengaju, jadi jawabannya tetap datang dari resolver atasan employee-service, dan dengan sendirinya mengikuti layar Pengaturan > Organisasi > Penyetuju Pengajuan di HRIS.
- **Supervisor IT** tetap lolos lewat `superAksesIT` yang sudah ada di service ini. Jalan darurat tidak dibuat baru.

### 3. Gerbang dan antrean WAJIB memakai fungsi yang sama

Penyempitan hidup di satu fungsi, dan fungsi itu dipakai oleh `pastikanBolehMenindakTahap` maupun `tahapYangBolehDitindak`. Bila keduanya menjadi dua salinan, hasilnya adalah kelas cacat yang [[REF - Alur Persetujuan]] catat tiga kali: orang melihat antreannya berisi lalu ditolak saat menekan tombol, tanpa satu pun pesan yang menyebut sebabnya. Dikunci satu test yang memeriksa kedua sisi sekaligus.

### 4. Pemilih hanya menawarkan pemegang izin

Employee-service mendapat `GET /internal/permission-holders?permission=<izin>&company_id=<key>`, dijawab dari `izinKaryawan` dan `positionSetKeys` yang sudah ada. Ia **membaca** RBAC aslinya, bukan menyalinnya.

Tanpa endpoint ini, layar pengaturan akan membiarkan seseorang menunjuk orang yang tak berizin, dan tahap itu lalu tidak dapat ditindak siapa pun karena irisan izin dan penunjukan menjadi himpunan kosong. Kegagalannya senyap: dokumen berhenti tanpa galat.

Prefix `/internal/` bukan batas keamanan ([[ADR - 0031 Prefix internal Bukan Batas Keamanan]]), jadi rute ini memeriksa identitas pemanggil sendiri dan membatasi hasil ke perusahaan pemanggil, mengikuti pola `/internal/department-approver`.

### 5. Penunjukan boleh lebih dari satu orang

Tahap gudang dan AP dikerjakan bergantian. Daftar berisi beberapa orang, dan seluruhnya menerima notifikasi.

### 6. Penunjukan diperiksa di SERVER, dan gagal-tertutup

Menunjuk orang yang tak memegang izin tahapnya membuat irisan "berizin DAN ditunjuk" kosong, sehingga tahap itu tak dapat ditindak siapa pun: dokumen berhenti tanpa satu pun galat, dan gejalanya "kok tak ada yang memproses", bukan penolakan. Penyaring di layar tidak cukup, sebab penyaring di layar bukan gerbang.

`PUT /pengajuan-pembelian/penyetuju/:tahap` karena itu memeriksa tiap `employee_id` terhadap daftar pemegang izin tahap itu, dan menyebut siapa yang ditolak. Bila daftarnya tak dapat dibaca, penunjukannya **ditolak**: menyimpannya tanpa bisa memeriksa berarti mempertaruhkan tahap yang mandek demi satu penyimpanan yang bisa diulang semenit kemudian.

Mengosongkan penunjukan sengaja **tidak** menuntut pemeriksaan apa pun. Daftar kosong berarti mengembalikan tahap itu ke seluruh pemegang izin, dan itu selalu sah; menuntut employee-service hidup untuk itu berarti jalan mundur ikut tertutup justru saat ada yang bermasalah.

### 7. Rute pemegang izin digerbang keanggotaan MODUL

`GET /internal/permission-holders` menjawab siapa memegang wewenang apa, termasuk siapa yang berhak menyetujui pengeluaran setingkat Direktur. Tak satu pun rute lain menjawab itu, termasuk direktori karyawan yang memang terbuka bagi tiap akun.

Pemanggilnya karena itu wajib memegang setidaknya **satu izin dari modul yang sama** dengan izin yang ditanyakan. Menuntutnya memegang izin YANG DITANYAKAN tidak bisa: yang membuka layar pengaturan adalah pengelola master, dan ia justru bukan orang yang mengerjakan tahapnya. Modul dibaca dari prefiks izin dan daftarnya dari katalog yang sudah terdaftar, jadi tak ada daftar-izin baru yang lahir. Prefiks tanpa katalog **menutup** rutenya.

### 8. Penyempitan gagal-TERBUKA saat penunjukan tak terbaca

Berlawanan arah dengan §6, dan itu disengaja. Bila penunjukan tak dapat dibaca saat seseorang menindak atau membuka antreannya, yang berlaku adalah daftar tahap yang izinnya memang ia pegang, yaitu perilaku sebelum ADR ini. Penyempitan tak pernah melampaui RBAC, sehingga kehilangannya tak dapat membocorkan hak apa pun; sebaliknya, gagal-tertutup di titik itu memadamkan seluruh antrean dan seluruh tombol persetujuan sekaligus hanya karena satu blip Mongo. Kegagalannya di-log dan dikunci uji.

## Consequences

### Yang membaik

- Notifikasi tiap perpindahan tahap punya alamat yang benar, termasuk untuk tahap yang pelakunya staf.
- Perubahan penanggung jawab (rotasi staf gudang, pergantian AP) tidak lagi menuntut deploy maupun perubahan permission set.
- Antrean "Perlu Aksi Saya" menyempit ke orang yang memang ditugaskan, sehingga daftarnya berarti.

### Yang memburuk atau tetap terbuka

- ⚠️ **Ada dua tempat yang menentukan siapa menindak apa**: permission set (IT) dan penunjukan tahap (pengelola master budget). Keduanya sengaja tidak sejajar, tetapi orang yang bingung "kenapa saya tidak bisa menyetujui" kini punya dua tempat untuk diperiksa. Layar pengaturan wajib menampilkan keduanya sekaligus.
- **Penunjukan ke orang yang kemudian resign** tidak terdeteksi otomatis oleh gerbang, karena gerbang sengaja tidak memanggil employee-service (jalur kritis tidak boleh ikut jatuh saat service lain mati). Yang menahannya adalah penandaan di layar pengaturan.
- **Urutan tahap tetap di kode.** Yang dapat diatur adalah siapa orangnya, bukan lewat siapa saja. Mesin alur yang bisa dikonfigurasi tetap ditolak sampai ada tiga pemakai nyata, sesuai alasan yang sama di ADR-0055.
- Menambah endpoint pembacaan izin berarti **employee-service ikut naik** pada deploy modul ini.

### Yang sengaja tidak dilakukan

- **Penunjukan tidak menggantikan izin.** Membiarkan siapa pun ditunjuk tanpa izin akan menjadikan layar yang dipegang non-IT sebagai jalur pemberian hak, persis yang layar Penyetuju Pengajuan di HRIS sengaja hindari, dan pemisahan izin per tipe kehilangan artinya.
- **Antrean tidak dibiarkan lebar sementara gerbang menyempit.** Kombinasi itu justru melahirkan kelas cacat yang keputusan ini hendak tutup.

## Dokumen Terkait

- [[ADR - 0055 Pengajuan Pembelian Empat Tipe Menggantikan Pengajuan Budget]] yang keputusan ini simpangi di §7
- [[REF - Alur Persetujuan]] tentang siapa yang berwenang memutuskan, dan kelas cacat "wewenang memutus tanpa kemampuan melihat"
- [[CORE - RBAC dan Permission Set]] · [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] · [[ADR - 0031 Prefix internal Bukan Batas Keamanan]]
- [[ADR - 0050 Notifikasi Inbox Mendorong Push ke Browser dan Ponsel Sekaligus]] yang menentukan bahwa satu panggilan inbox sudah mendorong dua kanal
- [[Microservices - Procurement Service]] · [[Microservices - Employee Service]] · [[Microservices - Notification Service]]
