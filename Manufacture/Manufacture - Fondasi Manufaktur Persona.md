# Fondasi Manufaktur: Persona & Alur

> Menggambarkan **siapa** yang bekerja di alur manufaktur (produksi, PPIC, gudang bahan dan barang jadi, Quality) dan **bagaimana** pekerjaannya mengalir antar jabatan dan antar service. Dok induk: [[Manufacture - Kajian Fondasi Sistem]].
> **Status**: 🟡 **Konsep / Draft**. Ikut status dok induk. Alur di sini adalah **rancangan target** hasil kajian 2026-10-13 (SOP posisi, matriks KPI, kuesioner pemakai, spreadsheet PPIC, Batch Record kertas), bukan gambaran perilaku kode hari ini. Yang sudah ada di kode dan prod ditandai eksplisit di bagian Arsitektur. Langkah bertanda **TBD n** masih menunggu keputusan nomor n di dok induk.

## Sumber dan cara membaca

- **Alur proses dan alur per jabatan** diturunkan dari [[REF - SOP Bharata 2026 per Posisi]], [[HRIS - Matriks KPI per Departemen]], kuesioner ke 32 pemakai (14 responden), spreadsheet operasional PPIC, dan Batch Record kertas. Rinciannya di Temuan 3 sampai 7 dok induk.
- **Arsitektur** diturunkan dari kode `origin/main` 2026-10-12 dan data prod baca-saja 2026-10-13 (Temuan 1 dan 2 dok induk).
- Dok ini **tidak memuat nama orang**. Persona memakai jabatan; siapa memegang jabatan apa ada di HRIS.
- Diagram ditulis sebagai Mermaid supaya bisa disunting di vault. Versi interaktif (peta Archify) disimpan di luar vault sebagai salinan bertanggal; bila keduanya berbeda, dok ini yang berlaku.

## Aktor (ringkas)

| Persona | Peran & Divisi | Akses / RBAC | Device | Muncul di |
|---|---|---|---|---|
| **SPV Brand** | Marketing, pemesan barang jadi per brand | modul marketing (TBD menu Production Order) | Web ERP | Alur A, Production Order |
| **PPIC** | rencana produksi, MRP, permintaan pengadaan, jadwal | modul manufacture | Web ERP | Alur A dan B |
| **SPV Manufacture** | penyetuju rencana, pengadaan, bahan pengganti, opname; belum punya SOP | modul manufacture | Web ERP | Alur A, B, opname |
| **Procurement** | Leader dan Staff Inventory: PO bahan, ETA, retur pemasok | modul procurement | Web ERP | Alur A |
| **Gudang** | Staf, Admin, Leader Warehouse: terima, karantina, serah ke WIP, opname mingguan | modul manufacture (WMS) | Web ERP | Alur A dan B |
| **QC Assistant** | uji bahan masuk per lot | modul quality | Web ERP | Alur A |
| **Admin Produksi** | permintaan bahan, menyalin Batch Record dari kertas | modul manufacture | Web ERP | Alur B |
| **Leader Produksi** | verifikasi Batch Record | modul manufacture | Web ERP | Alur B |
| **Operator Produksi** | mengisi form kertas di lantai produksi | tidak perlu input ERP (hasil kuesioner) | kertas | Alur B |
| **QC Production** | uji IPC per tahap, ajukan rilis, terbitkan COA | modul quality | Web ERP | Alur B |
| **PJT / Supervisor Quality** | keputusan rilis batch, nasib barang ditolak, CAPA | modul quality (TBD) | Web ERP (kini kertas) | Alur B |
| **Finance** | Supervisor FAT, Accounting, Cost Control: validasi opname, Accurate, HPP | modul finance | Web ERP, Accurate | opname, HPP |
| **Admin Return** | scan retur marketplace ke stok FG | modul manufacture | Web ERP | sudah berjalan di prod |

## Alur A: rencana sampai bahan lulus QC

```mermaid
flowchart LR
  PO["Production Order<br/>SPV Brand, cek MOQ"] --> RENCANA{"Rencana produksi<br/>PPIC, disetujui SPV"}
  RENCANA -->|disetujui| MRP["Hitung kebutuhan<br/>formula, stok, sedang dipesan"]
  MRP -->|kurang| PENGADAAN["PO pengadaan<br/>Procurement, ETA"]
  PENGADAAN -->|datang| TERIMA[("Terima bahan<br/>Gudang, karantina")]
  TERIMA --> QC{"QC bahan masuk<br/>QC Assistant"}
  QC -->|lulus| STOK[("Stok bahan siap pakai")]
  RENCANA -.->|di bawah MOQ| REVISI["Revisi PO<br/>ubah satu kali"]
  REVISI -.-> PO
  QC -.->|ditolak| RETUR["Retur pemasok<br/>atau potong tagihan"]
```

- Production Order di bawah MOQ dikembalikan untuk revisi satu kali (keputusan MOQ dan aturan ubah PO belum diambil).
- Bahan datang masuk **karantina** sampai QC memutuskan Lulus, Reject, atau Ditolak (TBD 4). Bahan Ditolak tidak pernah masuk stok.
- Kebutuhan bahan memperhitungkan bahan yang sedang dipesan, dibaca dari PO di Procurement.

## Alur B: produksi, rilis, dan pengiriman

```mermaid
flowchart LR
  JADWAL["Jadwal produksi<br/>PPIC, per shift"] --> GERBANG{"Gerbang bahan<br/>lengkap dan lulus QC<br/>TBD 10"}
  GERBANG -->|lengkap| WIP[("Serah ke WIP<br/>Gudang, lot FEFO<br/>TBD 2")]
  WIP --> BATCH["Batch Record<br/>olah, kemas, uji QC"]
  BATCH -->|FG karantina| RILIS{"Keputusan rilis<br/>PJT, maks 24 jam<br/>TBD 3"}
  RILIS -->|lulus| KIRIM["Surat Jalan + COA<br/>Gudang FG<br/>TBD 9"]
  GERBANG -.->|kurang| KURANG["Bahan kurang<br/>pengadaan atau pengganti"]
  KURANG -.->|disetujui SPV + APJ| JADWAL
  RILIS -.->|ditolak| TOLAK["Batch ditolak<br/>alasan, nasib barang, CAPA"]
```

- Batch hanya boleh mulai bila semua bahan formula tersedia dan lulus QC. Penolakan batch yang ditemukan kajian berakar pada bahan pengganti, bukan hasil uji (Temuan 7).
- Admin Produksi menyalin Batch Record dari kertas; QC Production mengisi bagian uji di Batch Record yang sama.
- Barang jadi berstatus **FG karantina** sampai PJT memutuskan; FG tidak dianggap tersedia sebelum rilis.
- Batch ditolak wajib alasan, **nasib barang** (karantina, musnah, rework, lainnya), dan CAPA.

## Arsitektur service

```mermaid
flowchart LR
  FE["erp-frontend<br/>menu per posisi"] -->|HTTPS /api| GW{{"API Gateway<br/>JWT, paket hak"}}
  subgraph PROD["bip-erp di VPS prod (Docker)"]
    GW --> PROC["procurement<br/>pengajuan, PO"]
    GW ==> MANUF["manufacture<br/>Batch Record, stok, lot"]
    GW --> EMP["employee<br/>Quality, KPI"]
    PROC -->|stok dari pengajuan| MANUF
    EMP -->|baca /kpi/*| MANUF
    INTEG["integration<br/>HPP produk"] -->|HPP produk| MANUF
    MANUF --> MDB[("manufacture_db<br/>ledger + outbox")]
    EMP --> EDB[("employee_db<br/>quality_*")]
  end
  MDB -->|push penyesuaian| ACC["Accurate<br/>pembukuan"]
```

| Keadaan | Isi |
|---|---|
| ✅ Sudah ada di kode dan prod | rute Batch Record, cycle count, lot, K3/GMP, dan modul Quality; push gerakan stok ke Accurate menyala, tarik stok dari Accurate tiap 6 jam |
| ✅ Satu-satunya alur yang dipakai | scan retur marketplace (Gudang FG) |
| 🟡 Dirapikan di fondasi | satu Batch Record dan satu keputusan rilis; satu gerbang QC bahan masuk; satu jalur penyesuaian stok; PO bahan hanya di procurement (Temuan 2) |
| 🟡 Baru | menu per posisi mengikuti [[ADR - 0149 Sidebar Satu Daftar Urusan, Menu Digerbang Izin Posisi, Beranda Ruang Kerja Posisi]], gerbang ketersediaan bahan, COA keluar, dashboard jembatan dari spreadsheet PPIC |

## Alur per jabatan

Setiap diagram memisahkan pekerjaan jabatan itu sendiri dari pihak lain atau sistem yang ia ajak bertukar (garis putus-putus = kertas atau di luar ERP).

### Gudang (Staf, Admin, Leader Warehouse)

```mermaid
flowchart LR
  TERIMA["Terima bahan<br/>cek SJ dan COA"] --> KAR[("Label karantina<br/>lot, ED, qty fisik")]
  KAR -->|periksa| QCA(["QC Assistant"])
  QCA -->|lulus| SIMPAN[("Simpan bahan lulus<br/>kartu stok otomatis")]
  ADM(["Admin Produksi"]) -->|permintaan disetujui| SERAH["Serah ke WIP<br/>lot FEFO"]
  SIMPAN --> SERAH
  SERAH --> OPNAME["Opname mingguan<br/>hitung fisik, BA"]
  OPNAME -->|selisih| SPVF(["SPV Manufacture + Finance"])
```

- Kartu stok kosmetik dan obat tradisional dicetak dari sistem untuk BPOM (TBD 5).

### Admin dan Leader Produksi

```mermaid
flowchart LR
  JADWAL["Lihat jadwal<br/>batch per shift"] --> MINTA["Permintaan bahan<br/>dihitung dari formula"]
  MINTA -->|ajukan| PPIC(["PPIC"])
  PPIC -->|bahan di WIP| KERTAS["Form kertas<br/>di lantai produksi"]
  KERTAS -.-> INPUT["Input Batch Record<br/>Admin salin kertas"]
  INPUT --> VERIF{"Verifikasi<br/>Leader, paraf digital"}
  VERIF -->|lengkap| QCP(["QC Production"])
```

- Penyimpangan dihitung sistem dari selisih formula, penggantian bahan, dan rekonsiliasi, bukan diisi tangan.

### Operator Produksi

```mermaid
flowchart LR
  CEK["Cek pra-operasi<br/>mesin, APD"] -.-> KERJA["Isi form kertas<br/>pengolahan, kemas"]
  KERJA -.->|serahkan| LEAD(["Leader Produksi"])
  LEAD --> ADM(["Admin Produksi<br/>salin ke ERP"])
  KERJA -->|gangguan| LAPOR["Lapor kerusakan mesin<br/>fase berikut"]
  LAPOR --> TEK(["Teknisi<br/>departemen TBD"])
  KPI["Lihat KPI<br/>skor bulanan"]
```

- Operator tidak menginput Batch Record; menu ERP-nya Beranda, KPI, dan lapor kerusakan mesin (fase berikut).

### QC Assistant

```mermaid
flowchart LR
  GUD(["Gudang<br/>lot di karantina"]) -->|lapor datang| ANTRE["Antrean lot"]
  ANTRE -.-> SAMPEL["Ambil sampel<br/>sesuai jenis bahan"]
  SAMPEL --> UJI["Catat pengujian<br/>lembar uji bahan"]
  UJI --> PUTUS{"Putuskan<br/>lulus, reject, ditolak"}
  PUTUS -->|lulus| SIMPAN(["Gudang<br/>simpan bahan lulus"])
  PUTUS -.->|ditolak| RETUR(["Procurement<br/>retur bahan"])
  PUTUS --> LAPOR["Laporan QC<br/>ke Supervisor Quality"]
```

- Keputusan langsung mengubah status stok lot. Bahan ditolak diberi label merah, dipisah, dan dikonfirmasi Supervisor Quality.

### QC Production

```mermaid
flowchart LR
  PROD(["Produksi<br/>batch berjalan"]) --> IPC["Uji IPC per tahap<br/>mixing, filling, kemas"]
  IPC --> CATAT["Isi bagian uji<br/>di Batch Record"]
  CATAT --> SPEK["Spesifikasi produk<br/>pH, warna, netto"]
  SPEK --> AJU["Ajukan rilis"]
  AJU --> PJT(["PJT<br/>keputusan rilis"])
  PJT -->|lulus| COA["Terbitkan COA<br/>TBD 9"]
  COA --> FG(["Gudang FG<br/>Surat Jalan + COA"])
```

- Bagian spesifikasi produk (Temuan 6) dikerjakan M-03: master per produk ditulis QA/PJT, disalin ke Batch Record, hasil diisi QC (PR bip-erp#3084, belum merged + erp-frontend#2417). Ia menjadi isi utama COA keluar (M-21).

### PJT dan Supervisor Quality

```mermaid
flowchart LR
  QCP(["QC Production<br/>ajukan rilis"]) --> ANTRI["Antrean rilis<br/>batch FG karantina"]
  ANTRI --> TINJAU["Tinjau batch<br/>uji dan penyimpangan"]
  TINJAU --> PUTUS{"Keputusan rilis<br/>maks 24 jam"}
  PUTUS -->|lulus| FG(["Gudang FG<br/>FG jadi tersedia"])
  PUTUS -.->|ditolak| NASIB{"Nasib barang<br/>karantina, musnah, rework"}
  NASIB --> CAPA["CAPA<br/>dari penyimpangan"]
```

- Satu keputusan rilis per batch, di Batch Record (TBD 3). Penggantian bahan disetujui bersama SPV Manufacture (TBD 10).

### PPIC

```mermaid
flowchart LR
  MKT(["SPV Brand<br/>Production Order"]) --> TERIMA["Terima PO<br/>cek MOQ"]
  TERIMA --> RENCANA["Susun rencana<br/>per minggu"]
  RENCANA -->|ajukan| SPV(["SPV Manufacture"])
  SPV -->|disetujui| MRP["Hitung kebutuhan<br/>formula, stok, sedang dipesan"]
  MRP --> AJU["Ajukan pengadaan<br/>bahan kurang"]
  AJU -->|permintaan| PROC(["Procurement<br/>PO dan ETA"])
  PROC -->|ETA| JADWAL["Jadwal produksi<br/>per shift"]
  JADWAL --> SETUJU{"Setujui permintaan bahan<br/>ke WIP"}
  SETUJU --> GUD(["Gudang<br/>serah ke WIP"])
```

- Tab Rencana, MRP, safety stock, dan permintaan pengadaan di spreadsheet PPIC dipindah bertahap ke ERP (Temuan 4, TBD 7).

### SPV Manufacture

```mermaid
flowchart LR
  BERANDA["Beranda ringkas<br/>realisasi, akurasi stok, waktu rilis"] --> RENCANA{"Setujui rencana"}
  PPIC(["PPIC"]) --> RENCANA
  RENCANA --> PENGADAAN{"Setujui pengadaan"}
  PENGADAAN --> GANTI{"Bahan pengganti<br/>bersama APJ"}
  LEAD(["Leader Produksi<br/>bahan kurang"]) --> GANTI
  GANTI --> OPNAME{"Setujui opname<br/>selisih stok"}
  OPNAME -->|lanjut| FIN(["Finance<br/>validasi, Accurate"])
  OPNAME --> KPI["KPI tim<br/>otomatis dari data"]
```

- Semua persetujuan masuk satu menu Persetujuan. Posisi ini belum punya SOP (TBD 8).

### Procurement (Leader, Staff Inventory)

```mermaid
flowchart LR
  PPIC(["PPIC<br/>permintaan pengadaan"]) --> TERIMA["Terima permintaan"]
  TERIMA --> PO["Terbitkan PO<br/>ke pemasok"]
  PO --> ETA["Pantau ETA<br/>PPIC ikut melihat"]
  ETA -->|barang tiba| GQ(["Gudang + QC<br/>terima dan periksa"])
  GQ -.->|ditolak| RETUR["Retur pemasok"]
  RETUR --> VENDOR["Evaluasi vendor<br/>dari hasil QC"]
  RETUR --> FIN(["Finance<br/>potong tagihan"])
```

- PO bahan hanya dibuat di [[Microservices - Procurement Service]]; status dan ETA-nya dibaca PPIC sebagai bahan sedang dipesan.

### Finance (Supervisor FAT, Accounting, Cost Control)

```mermaid
flowchart LR
  SPV(["SPV Manufacture<br/>setujui penyesuaian"]) --> VALID{"Validasi opname<br/>TBD 1"}
  VALID --> KIRIM["Kirim ke Accurate<br/>penyesuaian otomatis"]
  KIRIM --> ACC(["Accurate"])
  KIRIM -->|periode| MUTASI["Mutasi persediaan<br/>7 kategori"]
  MUTASI --> AKURASI["Fisik vs Accurate<br/>akurasi stok"]
  AKURASI --> HPP["HPP per batch<br/>TBD 6"]
```

### SPV Brand (Marketing)

```mermaid
flowchart LR
  CEK["Cek ketersediaan<br/>stok FG rilis"] --> AJU["Ajukan Production Order<br/>minimal MOQ"]
  AJU -.->|perlu revisi| UBAH["Ubah sekali<br/>sebelum dikunci"]
  UBAH --> PPIC(["PPIC<br/>terima, jadwalkan"])
  AJU --> PPIC
  PPIC -->|dikunci| PANTAU["Pantau status<br/>jadwal sampai rilis"]
  PANTAU -->|produksi selesai| QC(["QC + PJT<br/>rilis batch"])
  QC -->|lulus| SIAP[("Barang siap kirim<br/>stok FG bertambah")]
```

- Hanya produk brand sendiri yang terlihat. Saat ini MO Barang Jadi punya satu koleksi dengan tiga rute (Temuan 2 nomor 8).

### Admin Return (sudah berjalan)

```mermaid
flowchart LR
  MP(["Marketplace<br/>resi tersinkron"]) --> SCAN["Scan resi retur"]
  SCAN --> CEK{"Cek kondisi"}
  CEK -->|baik| MASUK[("Masuk stok FG")]
  CEK -->|rusak atau kedobel| PISAH[("Dipisah")]
  MASUK -->|push| ACC(["Accurate"])
```

- Satu-satunya alur manufaktur yang aktif di prod (Temuan 1). Penataan fondasi tidak mengubahnya.

## Skenario Gagal

- Production Order di bawah MOQ → dikembalikan ke SPV Brand untuk revisi satu kali.
- Bahan ditolak QC → tidak masuk stok, diretur Procurement atau dipotong dari tagihan.
- Bahan formula kurang saat jadwal tiba → batch tidak boleh mulai; ajukan pengadaan atau bahan pengganti yang disetujui SPV Manufacture dan APJ, dan penggantian tercatat sebagai penyimpangan.
- Batch ditolak PJT → FG tetap karantina, wajib alasan, nasib barang, dan CAPA.
- Selisih opname → penyesuaian disetujui SPV Manufacture lalu divalidasi Finance sebelum dikirim ke Accurate.

## Dokumen Terkait

- [[Manufacture - Kajian Fondasi Sistem]] · [[Manufacture - Rancangan Menu per Posisi]] · [[Manufacture - Dashboard per Posisi]] · [[Manufacture - Dokumen Produksi Batch]] · [[Manufacture - Stock & Material Management]]
- [[Microservices - Manufacture Service]] · [[API - Manufacture Service]] · [[Microservices - Procurement Service]]
- [[QA - Quality Operasional (CAPA, Incoming, Batch Release)]] · [[Finance - FAT Persona]] · [[REF - SOP Bharata 2026 per Posisi]]
