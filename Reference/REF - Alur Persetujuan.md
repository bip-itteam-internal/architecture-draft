## Deskripsi

*Daftar SELURUH alur persetujuan di ERP Bharata beserta siapa yang berwenang memutuskannya. Disusun dari pembacaan rute di seluruh service (2026-08-10), bukan dari dokumen — beberapa gerbang tak terlihat dari daftar rute karena tinggal di dalam handler.*

- **Status**: ✅ Implemented — seluruh baris terverifikasi di kode.
- **Path di repo**: `bip-erp/services/{attendance,payroll,recruitment,procurement,manufacture,insentive,inventory,task-management,hrd-document,employee,integration}` · `bip-erp/shared-library/common/jabatan_direktur.go`
- **Kenapa referensi ini ada**: pertanyaan "persetujuan apa saja yang ada, dan siapa yang boleh" sebelumnya hanya bisa dijawab dengan membaca 11 service satu per satu. Sekali disusun, ia juga memperlihatkan pola yang tak terlihat dari satu alur saja.

## Empat cara gerbang persetujuan ditulis

Yang membuat inventaris ini sulit disusun, dan mudah salah:

1. **Middleware di daftar rute** — `gate(perm, fallback)` atau `common.Require*`. Terlihat langsung saat membaca `routes.go`.
2. **Di dalam handler** — mis. `BolehSetujuiPesanan(position)` di procurement. **Tak terlihat** saat menyapu daftar rute; sapuan pertama dokumen ini salah melaporkannya "tanpa gerbang".
3. **Slot pada dokumennya** — cuti & dinas menyimpan siapa reviewernya di `spv_status`; gerbangnya mencocokkan pemanggil dengan slot itu.
4. **Daftar penunjukan di koleksi tersendiri** (ditambahkan 2026-09-14): Booking Ruang menyimpan penyetuju yang ditunjuk HR di `ga_peminjaman_penyetuju`, satu dokumen per perusahaan, lalu mencocokkan pemanggil dengannya di fungsi transisi murni (`bolehMemutus`, `services/inventory/peminjaman_transisi.go:45-57`). Rute setujui dan tolak hanya bergerbang identitas (`services/inventory/peminjaman_handler.go:55-56`), jadi sapuan rute akan membacanya "tanpa gerbang".

> ⚠️ **Menyapu `routes.go` saja menghasilkan kesimpulan yang salah.** Tiga dari empat cara di atas tak muncul di sana.

## Inventaris

### Berbasis SLOT pada dokumen

| Alur | Service | Penyetuju |
|---|---|---|
| Cuti / izin / sakit | attendance | atasan langsung; **dialihkan ke Direktur** bila pemohonnya supervisor sendiri |
| Perjalanan dinas | attendance | idem |
| Koreksi presensi | attendance | atasan langsung (tanpa pengalihan) |
| Tukar jadwal | attendance | atasan langsung |
| Verifikasi security (cuti per jam) | attendance | posisi Security |

### Berbasis JABATAN

| Alur | Service | Penyetuju |
|---|---|---|
| Pesanan Pembelian ERP | procurement | `common.SetaraDirektur` — Direktur & Corporate Secretary |
| Permintaan Barang ERP | procurement | atasan departemen peminta (dari cakupan supervisi) |
| Inventory — approve handover aset | inventory | atasan departemen **penyerah**, dari `common.SupervisedDepartments`; diperiksa di dalam `ApproveHandover` |

### Berbasis IZIN / PERAN

| Alur | Service | Penyetuju |
|---|---|---|
| Payroll run — approve & publish | payroll | `payroll.approve`; fallback tier `hris: admin` |
| Rekrutmen — setujui penawaran | recruitment | `recruitment.approve` / HR supervisor |
| Rekrutmen — review & tolak job requisition | recruitment | idem |
| Rekrutmen — putuskan hire | recruitment | HR admin **atau** `secretary` supervisor |
| Rekrutmen — keputusan onboarding | recruitment | HR |
| Dokumen HRD — publish | hrd-document | HR |
| Quality — CAPA | employee | approver produksi / gudang |
| WMS — batch record, rekon MO, proposal, Sadewa | manufacture | peran WMS per tab |
| Task Management — approve/reject tugas | task-management | `ticket.triage` / admin space |
| Kotak Adopsi — adopt & reject draft | integration | peran integration |

### Berbasis PENUNJUKAN (daftar yang disimpan)

| Alur | Service | Penyetuju |
|---|---|---|
| Booking Ruang: setujui & tolak | inventory | siapa pun di daftar penyetuju yang ditunjuk supervisor atau admin HRIS/IT untuk perusahaan booking itu, satu daftar untuk semua ruang; **bukan** atasan pemohon dan **bukan** izin (katalog `ga` sengaja tanpa `ga.approve`, `services/inventory/peminjaman_model.go:30-32`) |

Rincian Booking Ruang (dipetakan 2026-09-14 dari `services/inventory/peminjaman_{transisi,setujui,handler,pengajuan,bentrok,notify}.go`):

- **Satu tahap.** `DIAJUKAN` → `DISETUJUI` atau `DITOLAK`, plus `DIBATALKAN` oleh pemohon (diagram status di `peminjaman_model.go:17-24`). Tak ada urutan antar-penyetuju: satu nama di daftar cukup (`Memuat`, `peminjaman_model.go:164-177`). Tolak wajib beralasan, maksimal 500 karakter (`ValidasiAlasanPeminjaman`, `peminjaman_model.go:248-258`).
- **Penyetuju tak boleh memutus booking miliknya sendiri**, sekalipun ia ditunjuk: 403 (`bolehMemutus`, `peminjaman_transisi.go:45-57`). Antrean `GET /peminjaman/perlu-aksi` tak memuat booking milik pembacanya (`peminjaman_handler.go:265-271`), dan kabar perlu-aksi tak dikirim ke pemohon yang juga penyetuju (`penerimaPerluAksi`, `peminjaman_notify.go:64-78`).
- **Lingkup perusahaan.** Daftar penyetuju dibaca dari perusahaan booking; penyetuju dari perusahaan lain menerima 404, bukan 403 (`bolehLihatPeminjaman`, `peminjaman_pengajuan.go:106-125`).
- **Pengajuan ditolak 422 bila daftar penyetuju perusahaan kosong** (`peminjaman_pengajuan.go:43-45`); form sudah diberi tahu lewat `ada_penyetuju` sebelum diisi (`peminjaman_handler.go:153-155`).
- **Pemeriksaan saat menyetujui, berurutan** (`SetujuiPeminjaman`, `peminjaman_setujui.go:11-20`, `:54-148`):
  1. status masih `DIAJUKAN` (409), pemanggil ditunjuk dan bukan pemohon (403), jam selesai belum lewat (409) (`TentukanSetujui`, `peminjaman_transisi.go:21-32`);
  2. ruang dibaca **ulang**: ruang yang sudah dinonaktifkan atau jadwal yang kini di luar jam operasional ruang ditolak 409, dengan pesan yang menyuruh penyetuju menolak booking itu (`ValidasiRuangSaatSetujui`, `peminjaman_bentrok.go:165-184`). Booking yang **sudah** disetujui tidak ikut dibatalkan oleh perubahan ruang itu;
  3. kunci sewa per ruang 15 detik; gagal mendapat kunci dibalas 409 "sedang diproses penyetuju lain" (`peminjaman_kunci.go:36`, `peminjaman_setujui.go:69-75`);
  4. bentrok dengan booking `DISETUJUI` di ruang yang sama dibalas 409 (`peminjaman_setujui.go:84-90`);
  5. tulis berpenjaga status **dan** jadwal, sehingga pengubahan jam oleh pemohon di sela cek dan tulis membuat persetujuan kalah 409 (`peminjaman_setujui.go:92-102`, `filterPenjagaPeminjaman` di `peminjaman_repo.go:92-100`);
  6. cek ulang bentrok: yang bertumpuk dikembalikan ke `DIAJUKAN` dan dibalas 409; cek ulang yang **gagal dibaca** juga dikembalikan ke `DIAJUKAN` dan dibalas 503, gagal-tertutup (`peminjaman_setujui.go:104-119`).
- **Ditolak otomatis** hanya dalam satu keadaan: begitu satu booking disetujui, pengajuan `DIAJUKAN` lain di ruang yang sama yang jamnya bertumpuk ditolak server (riwayat `tolak_otomatis` oleh `sistem`, alasan menyebut nomor booking yang disetujui), dan pemohonnya dikabari dengan judul yang berbeda dari penolakan manual (`peminjaman_setujui.go:125-146`, `PilihTolakOtomatis` di `peminjaman_bentrok.go:51-67`, `peminjaman_notify.go:109-113`). Penolakan otomatis yang gagal tersimpan hanya dicatat di log dan tak membatalkan persetujuannya; bila antrean bertumpuk tak terbaca, tolak otomatis dilewati dan pengajuan yang tertinggal kelak ditahan cek bentrok saat hendak disetujui (`peminjaman_setujui.go:125-130`, `:139-141`).
- **Tak ada kedaluwarsa otomatis.** Pengajuan yang jam selesainya lewat tetap `DIAJUKAN`: tak bisa disetujui lagi (409) dan tak ditagihkan di antrean (`peminjaman_transisi.go:28-30`, `peminjaman_handler.go:255-261`). Penulis status `DITOLAK` di kode hanya handler tolak dan tolak otomatis di atas.
- **Pengubahan oleh pemohon.** Memindah ruang atau jam booking yang sudah disetujui mengembalikannya ke `DIAJUKAN`, melepas slot lamanya, dan mengabari penyetuju lagi; mengubah isian (nomor WA, keperluan, keterangan) mempertahankan status (`TentukanUbah`, `peminjaman_transisi.go:82-111`; `statusSesudahUbah`, `peminjaman_pengajuan.go:269-278`; `peminjaman_handler.go:579-583`).
- **Yang menunjuk penyetuju**: supervisor atau admin HRIS/IT lewat `PUT /peminjaman/penyetuju` (`peminjaman_handler.go:50`, `shared-library/common/roles.go:300-303`), divalidasi ke karyawan aktif lewat employee-service dan gagal-tertutup saat daftar karyawan tak terbaca. Rincian kepemilikan datanya di [[REF - Kepemilikan Data]].

### Ditutup 2026-08-10

| Alur | Service | Penyetuju sekarang |
|---|---|---|
| Insentif — approve / unapprove hasil, termasuk bulk | insentive | `common.RequireInsentiveApprover` — `finance`, atasan marketing (supervisor / adv_leader / adv_marketplace / adv_meta), IT supervisor |

Keempat rutenya sebelumnya tak punya gerbang APA PUN — bukan di middleware, bukan pula di handler. Daftar yang berhak diturunkan dari niat yang sudah ada di frontend: menu Dashboard Insentif, tempat seluruh tombolnya hidup, hanya tampil untuk `finance` atau atasan marketing.

Yang paling penting ditutup, dan dikunci uji: peran insentif **operasional** — ICC, host live, CRM, affiliate. Merekalah yang hasilnya sedang dinilai; membiarkan mereka menyetujui berarti membiarkan penilaian diputuskan oleh yang dinilai.

⚠️ Halaman dashboard-nya sendiri masih lebih longgar daripada menunya (meloloskan peran insentif apa pun), jadi staf operasional yang membuka URL langsung tetap melihat layarnya — tombolnya kini balas 403 alih-alih diam-diam berhasil. Menyamakan gerbang halaman dengan menunya adalah rapikan tersendiri.

> **KOREKSI.** Versi pertama dokumen ini menyebut **Inventory — approve handover** juga tanpa gerbang. Keliru: otorisasinya ADA, di dalam `ApproveHandover` (`services/inventory/controller.go`), memeriksa bahwa pemanggil menaungi departemen penyerah lewat `common.SupervisedDepartments` dan membalas 403 bila tidak.
>
> Ini kesalahan yang SAMA dengan yang sudah diperingatkan di bagian atas dokumen ini — menyapu daftar rute lalu menyimpulkan "tanpa gerbang" — dan ia terulang setelah peringatannya ditulis. Bukti bahwa peringatan itu memang perlu ada, dan bahwa satu-satunya pemeriksaan yang sah adalah **membaca handler-nya**.

## Wewenang setingkat Direktur

Satu-satunya wewenang di ERP ini yang diperiksa lewat **nama jabatan**, bukan peran maupun izin. Ia dipakai tiga tempat, dan sampai 2026-08-10 masing-masing menuliskan daftarnya sendiri:

| Tempat | Untuk |
|---|---|
| `services/attendance` | slot cuti & dinas yang dialihkan ke "Direktur" |
| `services/procurement` | `PosisiApproverPO` — persetujuan Pesanan Pembelian |
| `erp-frontend` | cerminan yang kedua, untuk menyaring menunya |

Ketiganya kini menunjuk **`common.SetaraDirektur`** (`shared-library/common/jabatan_direktur.go`), berisi **Direktur** dan **Corporate Secretary** — keduanya berwenang sama (keputusan organisasi 2026-08-10).

⚠️ **Kenapa satu sumber penting di sini melebihi kerapian.** Daftar yang terlewat di salah satu tempat tak bergejala: orangnya **melihat** antrean — sebab daftarnya juga mencocokkan nama DEPARTEMEN — lalu **ditolak saat memutus**. Antrean berisi, tombolnya balas 403, dan tak ada satu pun pesan yang menjelaskan sebabnya.

⚠️ **Melihat ≠ memutuskan, dan itu disengaja.** Seluruh staf Kesekretariatan (Personal Assistant, Graphic Design, Video Editor) ikut melihat antrean persetujuan Direktur karena pencocokan departemen. Yang boleh memutus hanya dua jabatan di atas; ketiganya dikunci uji sebagai kasus yang harus tetap tertutup. Mempersempit daftarnya adalah keputusan yang belum diambil.

## Belum Diimplementasikan / Catatan

- **Tak ada lagi alur persetujuan tanpa gerbang** sejak 2026-08-10. Satu-satunya yang benar-benar terbuka (insentif) sudah ditutup; klaim kedua (inventory) ternyata salah baca.
- **Payroll: niat vs kenyataan.** Komentar di `services/payroll/rbac.go` menulis `isApprover` = "persetujuan final payroll run (Direktur)", tapi isinya `isHRAdmin`. Selama Direktur tak punya paket payroll, HR admin-lah yang menyetujui atas namanya. Ditutup 2026-08-10 dengan memasang paket `payroll_penyetuju` ke jabatannya — **tanpa mengubah gerbang**, sebab `gate()` mendahulukan izin dari klaim.
- **Persetujuan Pesanan & Permintaan tak punya pintu masuk dari navigasi.** Menunya dicabut dari Portal Saya; halamannya (`/persetujuan/pesanan-pembelian`, `/persetujuan/permintaan-barang`) dibiarkan dormant dan hanya bisa dibuka lewat URL langsung. Sejak 2026-08-10 KEDUANYA punya pintu lewat [[APP - Web ERP]] (Ruang Direktur). Menunya di Portal Saya tetap dicabut — pencabutan itu keputusan terpisah dan tidak dibatalkan; yang dikembalikan hanya jalur bagi yang berwenang memutus.
- ⚠️ **Wewenang memutus tanpa kemampuan melihat adalah kelas cacat yang berulang di ERP ini**, dan yang membuatnya sulit ditemukan: gejalanya "tak ada apa-apa", bukan penolakan. Tiga contoh sejauh ini, ketiganya baru ketahuan saat antreannya ditampilkan di satu layar:

	| Alur | Berwenang | Tapi daftarnya |
	|---|---|---|
	| Cuti & dinas | Direktur (dari slot) | tak punya layar sama sekali sampai 2026-08-10 |
	| Pesanan Pembelian | Direktur (`SetaraDirektur`) | menunya dicabut, halamannya dormant |
	| Job requisition | pemegang `recruitment.approve` | `listRequisitions` menyaring ke pengaju sendiri kecuali tier `hris` — Direktur selalu menerima daftar KOSONG |

	Yang ketiga ditutup 2026-08-10: syaratnya kini `isHR` **atau** memegang `recruitment.view` (union, jadi pemegang tier tak kehilangan apa pun).

- **Persetujuan PO di Accurate tak bisa ditindaklanjuti dari ERP.** ERP menyimpan salinan pesanan Accurate (`status_name: "Diajukan"`), tapi Accurate hanya menyediakan `save.do` — tak ada endpoint approval. Alur yang bisa diputus dari ERP adalah `pesanan_erp`, yang terpisah dari cermin itu.

- **Booking Ruang: wewenang memutus sudah ada di server, layar untuk memutus belum.** Web ERP sengaja tanpa tombol setujui dan tolak: halaman Ruang & Booking hanya menulis master ruang dan daftar penyetuju (`erp-frontend/src/features/ga/peminjaman/hooks/use-ruang.ts:37`, `:60`; `use-penyetuju-peminjaman.ts:43`), dan detail booking memberi tahu penyetuju bahwa keputusannya diambil lewat menu Pengajuan MyBharata (`erp-frontend/src/features/ga/peminjaman/components/peminjaman-detail-sheet.tsx:57-64`, teks `ga.peminjaman.detail.setujuiLewatMyBharata`). Layar MyBharata untuk mengajukan dan memutus **direncanakan** (irisan 2 [[ADR - 0094 Booking Ruang lewat MyBharata, Penyetuju Ditunjuk HR, Satu Sumber Ruang Kantor]]); sampai itu, antrean `GET /peminjaman/perlu-aksi` dan aksi setujui atau tolak hanya terjangkau lewat API. Kelasnya sama dengan "wewenang memutus tanpa kemampuan melihat" di atas, bedanya yang ini diketahui dan dijadwalkan.
- **Booking Ruang: dua keadaan yang membuat pengajuan menunggu orang yang tak bisa memutus.** (1) Pemohon yang menjadi satu-satunya penyetuju di daftar: pengajuannya lolos (daftar tak kosong), ia sendiri ditolak memutus, dan tak ada penerima kabar lain, jadi keadaannya hanya tercatat di log (`services/inventory/peminjaman_notify.go:128-134`, `peminjaman_transisi.go:53-55`). (2) Penyetuju yang resign atau pindah perusahaan tetap tercatat dan tetap dikabari, karena penunjukan hanya diperiksa saat disimpan; yang pindah perusahaan menerima 404 atas booking perusahaan lamanya (`peminjaman_pengajuan.go:121-123`). Bila seluruh daftar dalam keadaan itu, antreannya menggantung. Layar HR menandai penyetuju tak aktif tetapi tidak membersihkannya (`erp-frontend/src/features/ga/peminjaman/components/penyetuju-peminjaman-manager.tsx:125-133`).

## Dokumen Terkait

- [[ADR - 0094 Booking Ruang lewat MyBharata, Penyetuju Ditunjuk HR, Satu Sumber Ruang Kantor]] (Booking Ruang) · [[Microservices - Inventory Service]]
- [[REF - Rantai Pengajuan Lintas Modul]] — **sumbu berbeda, dipakai bersama.** Dokumen ini menjawab *siapa yang berwenang memutuskan*; yang itu menjawab *rantai bisnis mana yang terpecah jadi beberapa pengajuan terpisah, dan di titik mana ia putus*. Inventaris di sini disusun per-mekanisme-gerbang, di sana per-alur-bisnis.
- [[CORE - RBAC dan Permission Set]] · [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]
- [[ADR - 0043 Peran Sistem Diturunkan dari Jabatan]] · [[ADR - 0031 Prefix internal Bukan Batas Keamanan]]
- [[APP - Web ERP]] (Ruang Direktur) · [[Microservices - Payroll Service]] · [[Microservices - Recruitment Service]] · [[Microservices - Procurement Service]] · [[Microservices - Manufacture Service]]
