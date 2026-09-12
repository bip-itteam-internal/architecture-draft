# Finance FAT: Persona & Alur

> Menggambarkan **siapa** yang bekerja di divisi Finance, Accounting, dan Tax (FAT) dan **bagaimana** pekerjaannya mengalir antar posisi. Layar per posisi: [[Finance - Dashboard per Posisi (FAT)]]; peta domain: [[Finance - Big Pictures]]; dasar penilaian: [[HRIS - Matriks KPI per Departemen]].
> **Status**: ⚠️ **Implemented (ada catatan)**. Ikut status dok induk [[Finance - Dashboard per Posisi (FAT)]]: layar per posisi dan alur uang di kode sudah ada, tetapi akses nyata di produksi belum cocok dengan rancangannya (Account Payable dan Tax Officer tanpa akses ke layar kerjanya), dan modul Pajak serta alur pembayaran AP belum pernah dipakai. Seluruh angka dan akses **diukur prod 2026-09-12**; ukur ulang sebelum dipakai mengambil keputusan.

## Sumber dan cara membaca

- **Peran dan tujuan** diambil dari deskripsi dashboard per posisi `erp-frontend/src/features/finance/posisi/data/<posisi>.ts` (field `judul`, `subJudul`, `grade`, `melaporKe`). Field `jumlahOrang` di sana **statis** dan tidak mengikuti produksi (mis. AR Staf tertulis 2, prod 4; Junior Accounting tertulis 1, prod 7).
- **Jumlah orang dan akses** dari produksi: `work_data` + `system_authentication` (paket per akun, `system_roles`) + `master_department.position_items[].permission_sets` (paket per posisi). Paket posisi dan paket akun digabung saat login ([[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]). Akun tanpa paket finance jatuh ke tier `system_roles.finance`: admin semua izin, supervisor semua kecuali `finance.profit.view`, staff hanya `finance.ar.view`, `finance.ap.view`, `finance.accounting.view`, dan tanpa tier sama sekali tidak mendapat izin finance apa pun (`bip-erp/shared-library/common/catalog_finance.go:65-88`).
- **Alur** dari kode `bip-erp` dan `erp-frontend` di `origin/main` 2026-09-12.
- Dok ini tidak memuat nama orang maupun `employee_id`.

## Aktor (ringkas)

| Persona | Peran & Divisi | Akses / RBAC (prod 2026-09-12) | Device | Muncul di |
|---|---|---|---|---|
| **Supervisor FAT** | Finance Supervisor, 1 orang, melapor ke Direktur | Dari posisi: `finance_admin`, `procurement_admin`, `menu_finance_insentif`. Dari akun: 15 paket budget (pemohon, atasan, finance, direksi, GA, procurement, AP, QC, gudang). `system_roles` finance, integration, it, manufacture, warehouse = supervisor | Web ERP | Persetujuan uang keluar, tenggat pajak, target insentif level SPV, penilai terakhir KPI tim |
| **Senior Accountant** | Senior Accountant, 1 orang, melapor ke Supervisor FAT | 39 paket akun: seluruh `finance_*`, seluruh `budget_*` termasuk `budget_senior_accounting`, seluruh `kaskecil_*`, `procurement_admin`, `kpi_semua`, `ga_admin`, `jadwal_penjadwal_hostlive`. `system_roles` finance, integration, marketing = supervisor | Web ERP, Accurate | Review bukti transfer AP, laporan keuangan, GL, aset tetap |
| **Junior Accountant** | Junior Accountant, 7 orang, melapor ke Senior Accounting | 5 dari 7 **tanpa** `system_roles` dan tanpa paket; 1 `finance:admin`; 1 `ticket:supervisor` | Accurate (utama) | Pencatatan transaksi harian (template KPI Accounting CV atau Accounting PT) |
| **AR Leader** | Posisi di master; per prod tak ada pemegang aktif bernama "AR Leader" | Satu akun berposisi "AR Staff" memakai `position_key` `ar_leader` | Web ERP | Pengawasan umur piutang |
| **AR Staff** | AR Staff, 4 orang, melapor ke AR Leader. Peran nyata: piutang, retur, sales admin | Tier `finance` staff (3) atau supervisor (1), tanpa paket finance | Web ERP | Bridging Accurate, koreksi, rekonsiliasi uang masuk |
| **Account Payable** | Account Payable, 1 orang, melapor ke Supervisor FAT | **Tanpa `system_roles` dan tanpa paket** | Web ERP (dirancang) | Transfer pengajuan barang, bukti transfer, tagihan pemasok |
| **Cost Control** | Cost Control, 1 orang, melapor ke Supervisor FAT | `finance:staff` + 7 paket kas kecil (staf, PIC, atasan, GA, finance, direksi, pengawas) | Web ERP | Anggaran OPEX, forecast kas, kas kecil, rekomendasi efisiensi |
| **Tax Officer** | Tax Staff, 1 orang (masuk Mei 2026), melapor ke Supervisor FAT | **Tanpa `system_roles` dan tanpa paket** | Web ERP (dirancang) | Tax Control (kewajiban pajak per masa) |
| **Pemohon** | Karyawan divisi mana pun | Paket `budget_pemohon_*` (reach `own`) | Web ERP | Membuka pengajuan barang |
| **Atasan divisi / SPV Manufaktur** | Supervisor departemen pengaju | Diturunkan dari hubungan organisasi, bukan izin (tahap `pb_spv_divisi`, `pb_spv_manufactur`) | Web ERP | Tahap pertama pengajuan barang |
| **Procurement, GA, QC** | Divisi Procurement, General Affair, Quality | `budget.approve.procurement`, `budget.cek.stok`, `budget.terima.ga`, `budget.qc.periksa`, `budget.terima.rm` | Web ERP | Beli dan isi harga, cek stok, pemeriksaan, penerimaan barang |
| **Direktur** | Kesekretariatan | `budget.approve.direksi` | Web ERP | Pengajuan bernominal di atas ambang; penerima temuan audit internal |
| **Internal Audit** | Kesekretariatan | Pengisi ceklis KPI (form-builder); auditor = pemegang `audit.tinjau` + `audit.temuan.terbitkan` | Web ERP, aplikasi audit | Ceklis laporan Senior Accountant, kertas kerja audit bulanan |
| **SPV Marketing** | Divisi marketing | Dikenali dari hierarki HRIS, bukan izin | Web ERP | Target profit insentif level ICC dan leader divisinya |

## Persona detail

### Supervisor FAT: penjaga kas
- **Peran & Divisi**: Finance Supervisor, grade SUPERVISOR, melapor ke Direktur (`erp-frontend/src/features/finance/posisi/data/spv.ts:12-19`). Di dashboard, supervisor melihat semua tab posisi (`erp-frontend/src/features/finance/posisi/lib/tab-untuk-posisi.ts:84-100`).
- **Akses / RBAC**: lihat tabel Aktor. Paket posisi `finance_admin` memberi seluruh izin finance termasuk `finance.pajak.tenggat`.
- **Device**: Web ERP.
- **Tujuan**: "Menjaga kas: piutang tertagih, biaya di dalam anggaran, forecast dipercaya" (`spv.ts:13`).
- **Pain point**: kotak persetujuan di dashboard hanya memuat proposal dan aksi Sadewa manufaktur serta hasil insentif berstatus DRAFT (`bip-erp/services/integration/internal/interface/http/persetujuan_handler.go:16-19`), sehingga pengajuan barang yang menunggu persetujuannya tidak tampil di sana. Skor KPI-nya memakai skor tim, jadi tak bisa final sebelum anggota dinilai (urutannya anggota, leader, lalu supervisor; lihat [[HRIS - Matriks KPI per Departemen]]).
- **Aksi utama**: menyetujui tahap `pb_spv_finance` (izin `budget.approve.finance`) dan `pb_finance_setujui_bayar` (`budget.approve.pembayaran`) pada pengajuan barang (`bip-erp/services/procurement/pengajuan_barang_gate.go:41-55`); menggeser tenggat kewajiban pajak; menetapkan target profit level supervisor ([[ADR - 0079 Target Profit Satu Pintu di Insentif, KPI Membacanya]]); menilai KPI tim. ⚠️ Di prod (diukur 2026-09-12) seluruh nilai manual Finance April sampai Juli 2026 diketik akun HR, bukan Supervisor; apakah Supervisor menilai di luar sistem **TBD** (lihat subbagian "Siapa menilai" di [[HRIS - Matriks KPI per Departemen]]).
- **KPI**: "KPI Supervisor Finance", 5 metrik, kelimanya otomatis. Agustus 2026 bernilai 36,8 (Juli 79,7, dinilai manual).
- ⚠️ **Catatan akses**: satu akun memegang paket untuk hampir semua tahap persetujuan budget (atasan, finance, direksi, GA, procurement, AP, QC, gudang). Di prod baru ada 1 pengajuan barang dan 0 dokumen pembayaran, jadi belum jelas apakah ini penataan masa uji. Pemisahan tugas perlu diputuskan sebelum alur dipakai penuh (**TBD**).

### Senior Accountant: penutup buku dan pemeriksa bukti
- **Peran & Divisi**: Senior Accounting, melapor ke Supervisor FAT (`erp-frontend/src/features/finance/posisi/data/senior-acc.ts:16-23`).
- **Akses / RBAC**: lihat tabel Aktor. Satu-satunya pemegang `budget.bukti.review` di Finance.
- **Device**: Web ERP; pembukuan di Accurate ([[ADR - 0001 Akuntansi via Accurate]]).
- **Tujuan**: "Tutup buku tepat waktu, rekonsiliasi bersih, dan analisa yang dipakai"; ukurannya "laporan yang tidak perlu dikoreksi" (`senior-acc.ts:17-19`).
- **Pain point**: progres tutup buku dan rekonsiliasi bank terhadap GL belum punya data di sistem (panel "menunggu penyambungan" di dashboard). Antrean review bukti transfer tidak tampil di dashboard posisinya.
- **Aksi utama**: memeriksa bukti transfer yang diunggah AP, menyetujui atau menolaknya beserta alasan (rute di `bip-erp/services/procurement/main.go:1146-1150`); menyusun laporan keuangan (`/finance/accounting`) dan jurnal (`/finance/gl`); memantau aset tetap.
- **KPI**: dua template aktif sekaligus. "KPI SENIOR ACCOUNTING UPDATE" (3 metrik ceklis, dinilai tanggal 1 sampai 5 oleh Internal Audit untuk laporan dan Supervisor FAT untuk arsip, `bip-erp/services/employee/kpi_sumber_ceklis.go:16-39`) dan template lama 8 metrik manual. Skor terakhir Juli 2026 65,0 (template lama).
- ⚠️ **Catatan akses**: akun ini juga memegang paket di luar ranah akuntansi (GA admin, penjadwal Host Live). Perlu ditinjau (**TBD**).

### Junior Accountant: pencatat harian
- **Peran & Divisi**: Junior Accounting, melapor ke Senior Accounting (`erp-frontend/src/features/finance/posisi/data/junior-acc.ts:18-23`). Prod 7 orang dengan dua template KPI: Accounting CV (pembukuan entitas CV) dan Accounting PT.
- **Akses / RBAC**: 5 dari 7 tanpa tier dan tanpa paket, sehingga tidak bisa membuka `/finance` maupun dashboard posisinya.
- **Device**: Accurate. Tab dashboard "Accounting CV" (`data/acc-cv.ts:15-21`) sengaja tak dipetakan ke posisi mana pun karena tak punya pemegang di prod (`tab-untuk-posisi.ts:38-39`). Pembukuan 40 CV grup juga berjalan di aplikasi luar ERP [[APP - Buku Besar Konsolidasi CV FINCON]]; pemetaan pemakainya ke posisi belum ada (**TBD**).
- **Tujuan**: "Pencatatan harian: lengkap, tepat waktu, tanpa dikoreksi"; dinilai dari kecepatan dan kebersihan input, bukan jumlah baris (`junior-acc.ts:19-20`).
- **Pain point**: belum ada alur maker-checker (siapa memeriksa input, apa yang terjadi pada input yang ditolak), sehingga metrik "dikoreksi" tak bisa dihitung.
- **Aksi utama**: mencatat transaksi di Accurate; di ERP melihat KPI Saya.
- **KPI**: seluruh metrik manual. April sampai Juli 2026, 6 sampai 7 orang bernilai 100 (atau 98,2 sampai 100) setiap bulan pada Accounting CV: metriknya belum membedakan kinerja. Nilainya diketik akun HR tanpa catatan maupun bukti (`kpi_evidence` 0 dokumen), dan pencatatan harian mereka di Accurate tidak meninggalkan jejak pembuat di ERP (lihat subbagian "Siapa menilai" di [[HRIS - Matriks KPI per Departemen]]).

### AR Leader: pengejar piutang macet
- **Peran & Divisi**: AR Leader, grade LEADER, melapor ke Supervisor FAT (`erp-frontend/src/features/finance/posisi/data/ar-leader.ts:12-18`).
- **Akses / RBAC**: per prod tak ada pemegang aktif bernama "AR Leader". Satu akun berposisi "AR Staff" memakai `position_key` `ar_leader` dan dinilai template "KPI AR Leader" pada Juni dan Juli 2026; template itu diarsip 25 Agustus 2026. Peran dibaca dari nama posisi, paket dari `position_key`, jadi keduanya kini tidak sejalan (**TBD** rapikan).
- **Device**: Web ERP.
- **Tujuan**: "Mengejar uang yang tertahan di pelanggan" (`ar-leader.ts:13`).
- **Pain point**: janji bayar, lewat janji, dan hasil per cara hubung dicatat di luar sistem karena belum ada log kontak.
- **Aksi utama**: memantau porsi piutang di atas 60 dan 90 hari serta uang tertagih per minggu.

### AR Staff: antrean penagihan dan pencatatan uang masuk
- **Peran & Divisi**: AR Staf, melapor ke AR Leader (`erp-frontend/src/features/finance/posisi/data/ar-staf.ts:15-21`). Tiga peran nyata di prod tercermin dari templatenya: piutang, retur, dan sales admin.
- **Akses / RBAC**: tier `finance` staff cukup untuk `/finance`, `/finance/ar`, dan dashboard posisinya.
- **Device**: Web ERP.
- **Tujuan**: "Antrean penagihan harian dan pencatatan uang masuk" (`ar-staf.ts:16`).
- **Pain point**: faktur, retur, dan penerimaan kini ditarik otomatis dari marketplace ke Accurate ([[Microservices - Integration Service]]), jadi pekerjaannya bergeser ke menangani yang gagal dan memastikan tuntas sebelum tanggal 3 bulan berikutnya (bunyi KPI pencatatan). Status "sudah dihubungi" belum tercatat di sistem.
- **Aksi utama**: mengulang faktur, penerimaan, atau retur yang gagal sinkron; mengimpor koreksi; mengonfirmasi retur gudang; mengecek uang masuk yang belum dicocokkan.
- **KPI**: "AR Staff 2026" (3 metrik otomatis: porsi piutang di atas 60, 14, dan 90 hari) bernilai 22,7 pada Agustus 2026; "KPI AR Retur" 2 dari 4 metrik otomatis; "KPI Sales Admin" 1 dari 4.

### Account Payable: pembayar
- **Peran & Divisi**: Accounting Payable, melapor ke Supervisor FAT (`erp-frontend/src/features/finance/posisi/data/ap.ts:12-18`).
- **Akses / RBAC**: **tanpa tier dan tanpa paket di prod**. Akibatnya tidak bisa membuka `/finance/ap` maupun dashboard posisinya, tidak memegang `budget.ap.bayar` untuk tahap `pb_ap_transfer`, dan tidak menerima pengingat jatuh tempo faktur, yang dikirim ke setiap pemegang `budget.ap.bayar` (`bip-erp/services/procurement/jatuh_tempo_pengingat.go:109-118`). Di Finance, pemegang izin itu hanya Supervisor FAT dan Senior Accountant.
- **Device**: Web ERP (dirancang).
- **Tujuan**: "Membayar yang benar, pada waktu yang paling menguntungkan" (`ap.ts:13`).
- **Pain point**: antrean "perlu dibayar" tidak tampil di dashboard AP. Dokumen pembayaran berstatus PENDING tidak punya notifikasi (tak ada kategori inbox di berkas `pembayaran*.go`).
- **Aksi utama (dirancang kode)**: mentransfer pada tahap `pb_ap_transfer`; mengunggah bukti transfer; menerbitkan faktur pembelian dari hasil QC (izin `budget.ap.bayar`, `bip-erp/services/procurement/pengajuan_barang_gate.go:382-387`); lalu, untuk pengajuan yang punya faktur (UMUM dan RAWMATERIAL), mengirim dokumen pembayaran PENDING ke Accurate secara manual. Pengiriman manual itu **disengaja**: jalurnya menarik sisa utang terkini dari Accurate lebih dulu sebagai penjaga kelebihan bayar (`bip-erp/services/procurement/pembayaran_kirim.go:12-29`), dan rute itu menolak pembayaran tanpa faktur (`:116`), sehingga tipe uang (DANA, IKLAN, KONSUMSI) dibukukan lewat jurnal umum. Rincian alurnya di [[Microservices - Procurement Service]].
- **KPI**: template aktif 6 metrik manual (Juli 2026 bernilai 100). Konektor `realisasi_ap` (bayar paling lama 30 menit sesudah disetujui, nominal persis, bukti terunggah; `bip-erp/services/employee/kpi_sumber_realisasi_ap.go:16-37`, ambang di `bip-erp/services/procurement/kpi_realisasi_ap.go:114-120`) sudah ada di kode tetapi belum dipasang, dan datanya kosong (koleksi pembayaran 0).

### Cost Control: pemburu pemborosan
- **Peran & Divisi**: Cost Control, melapor ke Supervisor FAT (`erp-frontend/src/features/finance/posisi/data/cost-control.ts:17-23`).
- **Akses / RBAC**: `finance:staff` ditambah seluruh paket kas kecil, termasuk tahap finance dan direksi.
- **Device**: Web ERP.
- **Tujuan**: "Menemukan pemborosan dan membuktikan penghematannya dalam rupiah"; ukurannya rupiah yang benar-benar berhenti keluar, bukan jumlah rekomendasi (`cost-control.ts:18-20`).
- **Pain point**: rekomendasi efisiensi belum dipakai (0 dokumen di prod) dan belum punya siklus penanggung jawab serta status; register penghematan belum ada.
- **Aksi utama**: membandingkan anggaran OPEX dengan realisasi (233 baris anggaran di prod); memantau akurasi forecast kas mingguan; memverifikasi transaksi kas kecil lalu menjurnalnya ([[Finance - Kas Kecil dan Pengajuan Budget]]; 69 transaksi di prod, terakhir 26 Agustus 2026).
- **KPI**: 7 metrik, 2 otomatis (`varians_anggaran`, `forecast_kas`). Juli 2026 bernilai 92,0.

### Tax Officer: penjaga kepatuhan pajak
- **Peran & Divisi**: Tax Officer (posisi prod "Tax Staff"), melapor ke Supervisor FAT (`erp-frontend/src/features/finance/posisi/data/tax.ts:20-26`).
- **Akses / RBAC**: **tanpa tier dan tanpa paket di prod**. Tidak bisa membuka Tax Control `/finance/pajak` (butuh `finance.pajak.view`, dan tier staff pun tidak memberinya) dan tidak menerima pengingat jatuh tempo pajak, yang dikirim ke pemegang `finance.pajak.kelola` (`bip-erp/services/finance/pajak_notify.go:282-286`). Paket yang dirancang untuk posisi ini, `finance_pajak` (lihat dan kelola, tanpa menggeser tenggat), sudah ada tetapi belum dipasang.
- **Device**: Web ERP (dirancang).
- **Tujuan**: "Patuh tanpa membayar lebih dari yang seharusnya" (`tax.ts:21`).
- **Pain point**: modul pajak di prod masih kosong (master jenis pajak 0, kewajiban 0; seed master belum pernah dijalankan). Dashboard Tax tidak menaut ke Tax Control. Rekonsiliasi pajak, biaya non-deductible, dan temuan pajak belum punya data.
- **Aksi utama (dirancang kode)**: mencatat pelaporan SPT per masa lalu mengunggah BPE dan bukti bayar; tenggat hanya bisa digeser pemegang `finance.pajak.tenggat`. Rincian di [[API - Finance Service]] dan [[Finance - Rancangan Finance Service]].
- **KPI**: 8 metrik manual (Juli 2026 bernilai 90,0). Konektor `kinerja_tax` (pelaporan tepat waktu, dokumen terarsip; `bip-erp/services/employee/kpi_sumber_tax.go:12-31`) sudah ada tetapi belum dipasang, dan tak akan berangka sebelum kewajiban pajak tercatat.

## Alur

### 1. Uang keluar: pengajuan barang lima tipe

Sumber: `bip-erp/services/procurement/pengajuan_barang_jenjang.go:89-111` (pengecualian Direktur dan tipe yang lewat Procurement), `:160-247` (rantai tahap), `pengajuan_barang_gate.go:41-55` (izin per tahap).

```
Pemohon
 ├ UMUM        : GA cek stok ── stok cukup: GA serahkan barang, SELESAI tanpa uang
 │                          └─ stok habis: [atasan divisi] ─┐
 ├ RAWMATERIAL : SPV Manufaktur ────────────────────────────┤
 │                                                          ▼
 │                                    Procurement: beli dan isi harga
 │                                                          │
 └ IKLAN / DANA / KONSUMSI : [atasan divisi bila pengaju bukan SPV]
                                                            │
                                                            ▼
Supervisor FAT: setujui                                   (pb_spv_finance)
  ▼
[Direktur, bila nominal >= ambang; IKLAN dan KONSUMSI tidak pernah ke Direktur]
  ▼
Supervisor FAT: setujui bayar                             (pb_finance_setujui_bayar)
  ▼
Account Payable: transfer ─► dokumen pembayaran PENDING ─► AP kirim manual ke Accurate
  │ unggah bukti transfer                                   (pb_ap_transfer)
  ▼
Senior Accountant: review bukti ─ setuju: kabar ke pemohon
                                └ tolak : kabar ke AP, unggah ulang
  ▼
UMUM: QC gudang GA ─► terima GA          RAWMATERIAL: QC ─► terima gudang RM
```

Pembukuan ke Accurate: UMUM dan RAWMATERIAL lewat faktur pembelian yang diterbitkan AP dari hasil QC, lalu pembayarannya dikirim manual; IKLAN, DANA, dan KONSUMSI lewat jurnal umum. Rinciannya di [[Microservices - Procurement Service]].

Ambang Direktur bernilai nol berarti parameternya belum diatur, dan tahap Direktur **tidak disisipkan** (`pengajuan_barang_jenjang.go:154-157`).

### 2. Uang masuk: marketplace

```
Marketplace (Shopee, TikTok, Lazada)
  ▼  job terjadwal integration-service: faktur harian, retur, penerimaan, rekonsiliasi income
Accurate
  ▼
AR Staff: tangani yang gagal sinkron, impor koreksi, konfirmasi retur gudang, cek uang masuk belum dicocokkan
  ▼
AR Leader: kejar porsi piutang di atas 60 dan 90 hari (log kontak dan janji bayar di luar sistem)
  ▼
Supervisor FAT: pantau piutang di atas 60 hari kurang dari 5% dari total AR
```

Rincian job dan rute di [[Microservices - Integration Service]].

### 3. Tutup buku dan kontrol

```
Junior Accountant: catat transaksi harian di Accurate
  ▼
Senior Accountant: rekonsiliasi dan laporan keuangan (KPI: tepat waktu paling lambat tanggal 5)
  ▼  tanggal 1-5 : Internal Audit mengisi ceklis laporan, Supervisor FAT mengisi ceklis arsip AP
  ▼  tanggal 6 pukul 01:00 WIB : periode audit internal bulan lalu dibuka otomatis
Auditor internal: tarik data, tinjau baris, terbitkan temuan ─► Direktur
Cost Control: anggaran OPEX vs realisasi, akurasi forecast kas mingguan ─► Supervisor FAT
```

Sumber: `bip-erp/services/employee/kpi_sumber_ceklis.go:16-39`; `bip-erp/services/finance/audit_kertas_kerja.go:133-135`. Proses audit: [[Finance - Audit Internal]], aplikasinya [[APP - Audit Internal]].

### 4. Kas kecil

```
PIC unit kas (kaskecil.transaksi.save): catat pengeluaran dan unggah bukti
  ▼
Finance (kaskecil.approve.finance; di prod dipegang Cost Control dan Senior Accountant):
  tetapkan akun beban, cek cost center, verifikasi
  ▼
Jurnal ke Accurate lewat outbox ─► awal bulan: alokasi akun 2205 ke beban per CV
```

Aturan bisnis dan batasnya di [[Finance - Kas Kecil dan Pengajuan Budget]].

### 5. Pajak

```
Penjadwal finance-service menerbitkan kewajiban masa baru
  (atau manual oleh pemegang finance.pajak.tenggat)
  ▼
H-7 dan H-3 pukul 08:00 WIB: pengingat ke pemegang finance.pajak.kelola
  ▼
Tax Officer: catat pelaporan, unggah BPE dan bukti bayar
  ▼
Supervisor FAT: geser tenggat bila perlu ─► KPI kinerja_tax (belum dipasang)
```

Sumber: `bip-erp/services/finance/pajak_notify.go:21,44`; `pajak_jadwal.go:92-96`.

### 6. Insentif

```
SPV Marketing: target profit ICC dan leader divisinya
Finance / IT / Direktur: target level supervisor dan master beban
  ▼  dihitung otomatis dari data marketplace, HPP, payroll, dan Accurate
Dashboard Insentif (paket menu_finance_insentif; di Finance dipegang Supervisor FAT dan Senior Accountant)
  ▼
Karyawan: insentif sendiri di slip gaji MyBharata
```

Rincian: [[Finance - Incentive]], [[ADR - 0079 Target Profit Satu Pintu di Insentif, KPI Membacanya]], [[ADR - 0081 Insentif Saya Pindah ke MyBharata di Dalam Slip Gaji]]. Pemegang paket menu di luar Finance tidak diukur.

## Skenario Gagal

- **Akun tanpa tier dan tanpa paket finance** (Account Payable, Tax Officer, 5 Junior Accountant) → tertolak di `/finance` dan tab posisinya. Gejalanya layar tertolak, bukan pesan yang menyebut paket. ⚠️ Memasang **satu** paket finance ke akun yang selama ini hidup dari tier akan mematikan fallback tier-nya, karena begitu token membawa izin finance apa pun tier lama berhenti berlaku (`bip-erp/shared-library/common/catalog_finance.go:79-84`). Pasang paket yang menyamai hak tier lamanya sekaligus.
- **Kewajiban pajak jatuh tempo tanpa pemegang `finance.pajak.kelola`** di perusahaan itu → pengingat hanya masuk log, tak sampai ke siapa pun (`bip-erp/services/finance/pajak_notify.go:287-293`).
- **Pengingat jatuh tempo faktur** dikirim ke semua pemegang `budget.ap.bayar` (`jatuh_tempo_pengingat.go:110`) → di prod jatuh ke Supervisor FAT dan Senior Accountant, bukan ke Account Payable.
- **Bukti transfer ditolak** → AP pengunggah dikabari dengan kategori inbox "perlu review". Ini **disengaja** agar tak perlu kategori ketiga (`bip-erp/services/procurement/bukti_transfer_handler.go:476-480`). Bila pengunggahnya tak diketahui, kabar penolakan tidak terkirim dan hanya masuk log (`:481-484`).
- **Dokumen pembayaran PENDING** tidak terkirim ke Accurate sampai AP menekan kirim; pengirimnya sengaja manusia (`pembayaran_kirim.go:25-29`), dan tak ada notifikasi yang mengingatkannya. Rute kirim itu hanya menerima pembayaran yang punya faktur (`:116`); pembayaran tipe uang tetap PENDING di ERP dan pembukuannya lewat jurnal umum, yang tidak terbit selama kill switch `ACCURATE_KAS_PUSH` mati (keadaan bawaan, `bip-erp/services/procurement/kas_jurnal_handler.go:28-37`).
- **Pengajuan budget** berhenti di status DISETUJUI; pencairan dan penjurnalan ke Accurate di luar cakupan modul itu (`bip-erp/services/procurement/main.go:754-758`). Kas kecil, pengajuan budget, dan pengiriman pembayaran tidak mengirim notifikasi apa pun.
- **Parameter ambang Direktur belum diatur** (nol) → pengajuan bernominal besar tidak melewati Direktur (`pengajuan_barang_jenjang.go:154-157`).
- **Kertas kerja audit** punya status `terbit` yang dideklarasikan tetapi tak punya rute penulisnya (`bip-erp/services/finance/audit_kertas_kerja.go:26,289`), jadi periode audit belum bisa ditutup dari sistem.

## Dokumen Terkait

- [[Finance - Dashboard per Posisi (FAT)]] · [[Finance - Big Pictures]] · [[HRIS - Matriks KPI per Departemen]]
- [[Finance - Kas Kecil dan Pengajuan Budget]] · [[Microservices - Procurement Service]] · [[API - Procurement Service]]
- [[API - Finance Service]] · [[Finance - Rancangan Finance Service]] · [[Finance - Audit Internal]] · [[APP - Audit Internal]]
- [[Microservices - Integration Service]] · [[Finance - Incentive]] · [[Microservices - Insentive Service]]
- [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] · [[ADR - 0001 Akuntansi via Accurate]] · [[CORE - RBAC dan Permission Set]]
- [[HRIS - Payroll Persona]] (contoh format persona lintas aktor)
