**Status**: ⚠️ Diputuskan 2026-08-06 dan **kodenya MERGED ke `main` hari yang sama, pukul 10:14 WIB**: bip-erp PR [#1027](https://github.com/bip-itteam-internal/bip-erp/pull/1027) (merge commit `e4798f61`) dan erp-frontend PR [#818](https://github.com/bip-itteam-internal/erp-frontend/pull/818). Branch `feat/task-space-admin` sudah tidak ada di kedua repo. **Uji lewat gateway (syarat "sekali dijalankan sungguhan") masih BELUM dilakukan**, di dev maupun prod, dan prod belum di-deploy. Sampai uji itu terjadi, dokumen ini menyatakan keputusan yang sudah terpasang di `main`, bukan keadaan produksi.

## Context

Sampai keputusan ini, seluruh wewenang kelola di [[Microservices - Task Management Service]] diturunkan dari **divisi**: supervisor departemen mengurus space departemennya, admin mengurus semuanya. Model itu langsung dari [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]], yang menempelkan hak pada **posisi** dengan cakupan `own`/`division`/`all`.

Yang tidak bisa dinyatakan model tersebut adalah kalimat paling sederhana tentang sebuah desk: **"orang ini yang menerima permintaan di space ini"**. Di lapangan pembagiannya memang begitu; seorang staf memegang antrean satu tim, kadang staf dari departemen lain, sementara supervisornya tak menyentuh triase harian.

Tiga jalan yang tersedia sebelumnya semuanya salah sasaran:

- **Menaikkan tier orangnya jadi supervisor** memberi wewenang atas SELURUH divisi, bukan atas satu space, dan ikut membuka laporan tim seluruh departemen.
- **Menempelkan paket izin di posisinya** menaikkan hak semua pemegang posisi yang sama. ADR 0030 sudah mencatat kasus nyatanya: satu posisi ICC dipegang 40 orang.
- **Mengarang posisi khusus satu orang** mengotori struktur organisasi yang dibaca fitur lain (supervisi, KPI, requisition).

Ada temuan kedua yang memaksa keputusan ini menyentuh gerbangnya sekalian. `approveTask`/`rejectTask` **tidak pernah mengecek divisi maupun space**: gerbangnya hanya izin `ticket.triage` di level rute. Kotak masuk memang tersaring per divisi, tapi penyaringan daftar bukan gerbang — supervisor departemen mana pun bisa menyetujui tiket space departemen lain dengan mengirim id tiketnya langsung ke gateway.

## Decision

**Sebuah space boleh menunjuk admin-nya sendiri, dan hak itu menempel pada OBJEK (space), bukan pada posisi.**

Aturan turunannya:

1. **Wewenangnya sebatas space itu**: menerima permintaan masuk (approve/reject), meninjau `Testing → Done`, menugaskan dan membetulkan atribut tiket, melihat laporan tim space tersebut, dan mengubah pengaturan space. Di luar space itu, ia staf biasa.

2. **Kandidatnya karyawan mana pun**, termasuk dari departemen lain. Yang memegang antrean sebuah tim tak selalu orang tim itu.

3. **Membuat dan menghapus space tetap milik supervisor divisi dan admin.** Space baru lahir untuk sebuah divisi dan belum punya admin yang bisa menunjuk dirinya; menghapus space menyeret seluruh riwayat tiket di dalamnya, dan itu bukan keputusan yang pantas ditanggung orang yang wewenangnya berasal dari space itu sendiri.

4. **Daftar admin disimpan di dokumen space, bukan di klaim JWT.** Konsekuensinya disengaja dan menguntungkan: perubahan berlaku **seketika**, tidak menunggu login ulang seperti `permission_sets` dan `supervised_departments` yang ikut token 72 jam.

5. **Satu pintu keputusan** (`canActOnSpace` di `services/task-management/space_admin.go`): admin space menang lebih dulu tanpa menuntut izin katalog; selain itu izin katalog DAN cakupan divisi harus terpenuhi **bersama**. Syarat kedua itulah yang menutup lubang approve lintas divisi di §Context.

6. **Gerbang rute hanya membuka pintu, handler yang memutuskan objeknya.** `gateOrSpaceAdmin` meloloskan pemegang izin ATAU admin di space mana pun, karena di level rute id tugasnya belum dibaca; `canActOnSpace` di dalam handler yang menentukan space tertentu. Tanpa pembagian ini, admin space bertier staf ditolak 403 sebelum handler sempat melihat space mana yang ia tuju.

7. **Notifikasi aditif.** Permintaan baru dan eskalasi SLA response menyapa admin space **di samping** supervisor divisi, bukan menggantikannya. Admin space yang cuti tak boleh membuat permintaan menggantung tanpa ada yang tahu.

8. **Yang wewenangnya berasal dari daftar admin tak boleh mengosongkan daftar itu.** Supervisor divisi boleh, sebab ia tetap punya jalan masuk lewat divisi. Setiap perubahan daftar ditulis sebagai audit yang menempel pada space (`space_admins`).

## Consequences

**Konsekuensi yang diterima:**

- **Ini sumbu KEEMPAT di luar tiga sumbu ADR 0030** (modul × tingkat × cakupan). Hak per-objek tak bisa dilihat di layar Siapa Boleh Apa, yang membaca posisi dan paket. Siapa memegang space mana hanya terbaca di halaman space itu sendiri dan di audit trail.
- **Godaan menyalin pola ini ke modul lain akan muncul.** Batasnya perlu dijaga sadar: hak per-objek dibenarkan ketika objeknya memang punya pemilik operasional harian yang berbeda dari hierarki organisasi. Kalau yang dibutuhkan sebenarnya "posisi X boleh Y", itu tetap urusan ADR 0030.
- **Perubahan perilaku yang disengaja**: supervisor divisi lain kehilangan kemampuan menyetujui tiket di luar cakupannya. Tak ada alur nyata yang hilang (kotak masuknya memang sudah tersaring per divisi), tapi siapa pun yang selama ini memanfaatkannya lewat API akan mulai menerima 403.
- **Satu kueri Mongo tambahan per request** pada rute yang digerbang `gateOrSpaceAdmin`, hanya untuk yang tidak lolos lewat izin. Jumlah space kecil; bila membengkak, tambahkan index `{admins: 1}`.
- **Admin space bisa menambah admin lain**, termasuk memperluas lingkaran itu tanpa persetujuan supervisor. Diputuskan sadar oleh pemilik keputusan setelah risikonya disampaikan, dengan dua penekan: seluruh perubahan masuk audit trail, dan daftar tak bisa dikosongkan olehnya sendiri.

**Yang belum diputuskan (TBD):**

- **Batas atas jumlah admin per space** belum ada. Sepuluh admin di satu space berarti sepuluh orang menerima tiap notifikasi permintaan baru.
- **Peninjauan berkala** siapa saja yang memegang space belum punya tempat: tak ada layar yang menjawab "daftar semua orang yang memegang space mana pun" selain menyusurinya satu per satu.
- **Hubungannya dengan `Space.OwnerID`** yang sudah ada di model tapi tak pernah dipakai. Field itu sengaja TIDAK dipakai di sini (tunggal dan bertipe ObjectID, sedangkan yang dibutuhkan daftar employee_id), jadi ia tetap yatim.

## Terkait

- [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] (model yang disimpangi di sini) · [[ADR - 0031 Prefix internal Bukan Batas Keamanan]]
- [[Microservices - Task Management Service]] (implementasi) · [[API - Task Management Service]] (kontrak)
- [[CORE - RBAC dan Permission Set]] (katalog izin modul `ticket`) · [[APP - Web ERP]] (layar Kelola Space & tab Tugas Tim)
