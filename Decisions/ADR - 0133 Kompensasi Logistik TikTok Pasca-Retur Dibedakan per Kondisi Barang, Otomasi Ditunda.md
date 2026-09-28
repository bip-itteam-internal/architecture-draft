# ADR - 0133 Kompensasi Logistik TikTok Pasca-Retur Dibedakan per Kondisi Barang, Otomasi Ditunda

> **Status**: 🟡 **Diusulkan** — SOP disepakati untuk sementara, otomasi ditunda (kode belum ada). 2026-09-28.

%% Status ditulis DI SINI sebagai blockquote, bukan sebagai bullet di ## Deskripsi seperti
kebanyakan ADR — pola yang sama dengan ADR 0120/0124: ## Untuk Manajemen mendorong bagian
Deskripsi melewati baris yang dibaca VAULT-INDEX.json, sehingga status tak terbaca bila
ditulis di sana. Satu tempat saja — jangan tambahkan bullet Status di ## Deskripsi. %%

## Untuk Manajemen

**Apa yang berubah di layar.** Tidak ada. Ini keputusan SOP untuk tim finance/accounting yang
mengoreksi retur TikTok secara manual di Accurate — bukan perubahan sistem.

**Siapa yang terdampak.** Tim finance/accounting yang mengoreksi retur TikTok di Accurate secara
manual. Tim gudang (input kondisi retur di Gudang Barang Jadi) **tidak** berubah cara kerjanya —
data kondisi barang yang mereka input sudah ada dan sudah cukup.

**Apa yang TIDAK dijanjikan.** Tidak ada otomasi sekarang. Sistem tidak menghapus dokumen retur
atau memindahkan kompensasi secara otomatis — semuanya tetap dikerjakan manual sampai ada
keputusan lanjutan (lihat §Decision 3, pemicu untuk membangun). Kasus dokumen retur yang berisi
CAMPURAN kondisi barang (sebagian reject, sebagian reuse/rework dalam satu dokumen) **belum
terjawab** — dicatat sebagai pertanyaan terbuka ke finance, bukan diasumsikan.

**Perkiraan besaran kerja.** Nol untuk sekarang (dokumentasi SOP saja). Populasi yang terdampak
kecil: **16 order** sepanjang riwayat data yang terukur (28 September 2026), dari 458 kompensasi
logistik dan 8.647 retur terkirim total — lihat §Context untuk cara ukurnya.

## Deskripsi

*Kompensasi logistik TikTok yang turun SETELAH retur pesanan sudah dibukukan di Accurate perlu
perlakuan berbeda tergantung kondisi fisik barangnya — reject (rusak/hilang total) berarti retur
yang sudah tercatat itu sebenarnya keliru dan harus dikoreksi, sementara reuse/rework (barang
beneran kembali) berarti retur tetap sah dan hanya kompensasinya yang perlu dipisah. Keputusan ini
menetapkan ATURANNYA sebagai SOP manual dulu — populasi historisnya kecil (16 order), sehingga
kerja lintas-service untuk mengotomasinya belum sepadan sekarang.*

- **Path di repo** (bila kelak diotomasi — lihat §Decision 3, **TERTUNDA**, bukan dikerjakan sekarang):
  `bip-erp/services/integration/internal/usecase/kompensasi_tiktok.go` (pola pemisahan kompensasi
  ADR-0119, diperluas) · `bip-erp/services/integration/internal/usecase/accurate_rts_usecase.go`
  (`DeleteSalesReturn` — SUDAH ADA & teruji prod, dipakai ulang) ·
  `bip-erp/services/manufacture/` (koreksi stok WMS, **baru**)
- **Tanggal**: 2026-09-28

## Context

### Asalnya dari revisi tertulis finance, dan Kasus 1-nya sudah ditangani ADR lain

Finance mengajukan dokumen "Revisi Sistem Income" (Shopee ongkir + TikTok kompensasi, dua
kasus). Kasus 1 (payout>0, TANPA retur, kompensasi susulan → Pendapatan Lain-lain) **sudah persis
sama** dengan [[ADR - 0119 Kompensasi TikTok Dipisah Menurut Sudah atau Belum Ada Uang Masuk]] dan
sudah LIVE di prod (kv `tiktok-kompensasi-cutover-date` terisi 2026-09-01, diverifikasi langsung ke
dokumen Accurate). ADR ini HANYA membahas **Kasus 2**: pesanan cair normal → retur sudah tercatat
di Accurate (income sudah berkurang) → belakangan turun kompensasi LOGISTIK atas order yang sama.

Ditanyakan ke finance dengan jelas (2026-09-27/28), dan jawabannya BUKAN aturan tunggal —
tergantung kondisi barang hasil scan gudang:

> *"Kalo retur balik dengan kondisi barang 'reject' returnya dihapus, tapi kalo kembali dengan
> kondisi barang 'reuse/rework' berarti returnya ngga dihapus, tapi kompensasinya masuk ke
> pendapatan lain-lain."*

### Yang sudah ada — ini bukan bangun dari nol

- **Pemisahan kompensasi ke Pendapatan Lain-lain** (ADR-0119, live) — `kompensasiJadiPendapatanLain`,
  `pisahkanKompensasiPayoutPositif`, kv akun `other-income`, gerbang tanggal cutover
  (`kompensasi_tiktok.go`). Mekanismenya SIAP dipakai ulang untuk sisi reuse/rework, tinggal
  dilepas dari syarat "TANPA retur" untuk sub-populasi ini.
- **`DeleteSalesReturn`** (`accurate_client.go:1865`) — client Accurate untuk hapus dokumen Retur
  Penjualan. **Sudah ada, sudah teruji di prod**, dipakai di banyak jalur rebuild-dokumen retur
  (`accurate_rts_usecase.go` baris 4425, 5851, 7109, 7172 — rebuild grup, koreksi FAKE ORDER,
  pindah member antar-grup). Bukan capability baru yang berisiko.
- **`ReturnWarehouseItem.QtyReuse/QtyRework/QtyReject`** (`accurate_daily_return.go:41-77`) — data
  kondisi barang per SKU SUDAH ditangkap dari form "Input Masuk Return Dari Ekspedisi" (Gudang
  Barang Jadi) sejak lama. Pembeda yang diminta finance itu datanya sudah ada, bukan field baru.
- **`tt_statement_adjustments.type = "LOGISTICS_REIMBURSEMENT"`** — sudah tersinkron dari TikTok,
  jadi penanda "ini kompensasi logistik" — tapi TIDAK bisa dipakai sendirian sebagai pembeda
  (lihat pengukuran di bawah): tipe yang sama juga muncul untuk populasi [[ADR - 0056 Penyesuaian
  Statement TikTok Menambah Payout Order]] (order CANCELLED, payout≈0, TIDAK ada retur).
  Pembedanya harus JOIN ke ada-tidaknya dokumen retur yang sudah SENT untuk order itu.

### Populasi terukur (prod, 2026-09-28, baca-saja)

| Ukuran | Jumlah |
|---|---|
| Total penyesuaian `LOGISTICS_REIMBURSEMENT` | 458 |
| Order unik dengan penyesuaian itu | 458 |
| **Dari situ, order yang SUDAH punya retur `SENT`** (populasi Kasus 2 sebenarnya) | **16** |
| Total dokumen retur `SENT` (konteks pembanding) | 8.647 |

Query: `tt_statement_adjustments` (`type="LOGISTICS_REIMBURSEMENT"`) di-JOIN manual ke
`accurate_daily_returns` (`members.order_id` cocok, `last_status="SENT"`). 16 dari 458 (3,5%),
dan 16 dari 8.647 retur (0,18%) — **jarang, tapi nyata dan konsisten muncul** (bukan kejadian
sekali).

### Konflik dengan DUA keputusan lama — wajib disadari, bukan ditambal diam-diam

1. ⚠️ **[[ADR - 0119 Kompensasi TikTok Dipisah Menurut Sudah atau Belum Ada Uang Masuk]] §Decision 1
   (live prod)** menetapkan SEBALIKNYA untuk kombinasi "payout>0 DAN ada Retur Penjualan":
   kompensasi tetap **melunasi faktur** (income biasa), dokumen retur **tidak disentuh**. Alasan
   ADR-0119 saat itu: *"returnya yang membalik penjualan, kompensasi cuma menggantikan refund yang
   keluar"* — benar untuk kompensasi GENERIK, tapi finance sekarang membedakan lagi berdasarkan
   JENIS kompensasi (logistik) dan KONDISI barang. ADR ini **mengamandemen ADR-0119** khusus untuk
   sub-populasi sempit: ada retur **DAN** kompensasinya `LOGISTICS_REIMBURSEMENT`. Populasi "ada
   retur" pada umumnya (kompensasi bukan logistik, atau bukan LOGISTICS_REIMBURSEMENT) **TIDAK
   berubah** — tetap ikut ADR-0119 apa adanya.

2. ⛔ **Keputusan 22 Juli 2026** (`Workspace/Inbox/2026-07-17 Temuan - Reject retur menambah stok FG.md`,
   dikutip ulang di [[ADR - 0124 Input Retur Gudang Diukur Komposisinya Dulu, Lalu Konfirmasi
   Massal Hanya untuk Baris Cocok]] §Context) dan [[ADR - 0025 Log Sumber vs Input WMS + Stempel
   Penginput]] Decision #8 menetapkan **ketiga kondisi (Reuse/Rework/Reject) SENGAJA diperlakukan
   SAMA** — sama-sama menambah stok WMS, kondisi murni keterangan dashboard, TIDAK memengaruhi
   pembukuan. Reject sempat dicoba dikecualikan dari nambah-stok, **dibalik lagi** karena membuat
   WMS dan Accurate berselisih permanen (Accurate membukukan ketiganya sebagai `RETURNED`).
   Kalimat penutup temuan itu eksplisit: *"Jangan 'memperbaiki' ini balik ke scrap — itu keputusan
   sadar, bukan bug."*

   Dikonfirmasi ke finance: kalau dokumen retur Accurate dihapus untuk kasus reject, **stok WMS
   ikut dikoreksi/dikurangi** (bukan dibiarkan seperti biasa) — supaya WMS dan Accurate tidak
   kembali berselisih untuk order-order ini. ADR ini **mengamandemen** keputusan 22 Juli itu,
   **HANYA** untuk sub-populasi sempit (reject **DAN** dapat kompensasi logistik menyusul,
   ~16 order historis) — bukan retur reject pada umumnya, yang tetap ikut aturan lama (tetap
   menambah stok, tidak dikoreksi).

   [[ADR - 0124 Input Retur Gudang Diukur Komposisinya Dulu, Lalu Konfirmasi Massal Hanya untuk
   Baris Cocok]] (2026-09-24, 🟡 Diusulkan) secara eksplisit mencatat "mengubah arti tiga kondisi"
   sebagai batas yang SENGAJA tidak dilewati di ADR itu. ADR ini adalah amandemen SEMPIT atas batas
   itu, bukan pembatalannya — ADR-0124 tetap berlaku penuh untuk konfirmasi massal gudang.

### Pertanyaan terbuka ke finance — BELUM terjawab, jangan diasumsikan

Satu dokumen Retur Penjualan Accurate adalah GRUP (bisa berisi beberapa order/SKU sekaligus,
digabung per faktur+tanggal+jenis — [[ADR - 0016 Retur Grouped per Faktur + Tanggal Retur]]).
**Belum ada jawaban**: kalau SATU dokumen berisi campuran kondisi (sebagian SKU reject, sebagian
reuse/rework), apakah SELURUH dokumen dihapus, atau hanya baris/order yang reject yang dikeluarkan
dari grup? Ini wajib dijawab SEBELUM otomasi dibangun (lihat §Decision 3) — jangan ditebak.

### Cara manual sekarang

Finance mengoreksi kasus ini secara ad-hoc lewat jurnal manual di Accurate saat ketemu — belum ada
SOP tertulis, belum ada penanda sistematis untuk mengenali order mana yang termasuk populasi ini.

## Decision

### 1. Aturannya ditetapkan, tapi DIKERJAKAN MANUAL — tidak ada otomasi sekarang

Untuk order yang (a) sudah punya dokumen Retur Penjualan berstatus SENT di Accurate, DAN (b)
belakangan menerima penyesuaian TikTok bertipe `LOGISTICS_REIMBURSEMENT` atas order yang sama:

| Kondisi barang (dari scan gudang) | Perlakuan |
|---|---|
| **Reject** | Dokumen Retur Penjualan yang sudah terkirim **dihapus**, DAN stok WMS yang sempat bertambah karena qty reject itu **dikoreksi/dikurangi**. |
| **Reuse / Rework** | Dokumen Retur Penjualan **tetap ada, tidak disentuh**. Kompensasi logistiknya dicatat sebagai **Pendapatan Lain-lain**, nilai bayar (paymentAmount) 0 — pola sama persis ADR-0119 Kasus 1. |
| **Campuran dalam satu dokumen** | 🔴 **Belum diputuskan** — pertanyaan terbuka ke finance (lihat §Context). Sampai terjawab, kasus campuran ditangani manual kasus-per-kasus, jangan diasumsikan otomatis. |

Untuk SEKARANG, tabel ini adalah **SOP manual** bagi finance/accounting — bukan spesifikasi kode.
Tidak ada handler, job, atau field baru yang dibangun oleh ADR ini.

### 2. Kenapa SOP dulu, bukan langsung otomasi (Opsi C dipilih atas Opsi A/B)

Tiga opsi dipertimbangkan:

- **Opsi A** — bangun penuh (integration-service untuk Accurate + manufacture-service untuk
  koreksi stok WMS). Paling sesuai permintaan, tapi lintas 2 service dan mengamandemen 2 keputusan
  lama sekaligus (§Context) — kerja besar untuk populasi 16 order historis.
- **Opsi B** — otomasi sisi Accurate saja, stok WMS tidak disentuh. **Ditolak**: membuka lagi
  selisih WMS-vs-Accurate untuk populasi ini — persis kelas masalah yang membuat keputusan 22 Juli
  dibalik dulu.
- **Opsi C (dipilih)** — SOP tertulis dulu, populasi historisnya diukur ulang berkala, otomasi
  ditinjau lagi kalau volumenya naik atau ada permintaan eksplisit. Kerja lintas-service untuk 16
  kasus (dalam rentang data yang bisa diukur, bukan per-hari) belum sepadan sekarang, dan menulis
  SOP tertulis tetap menutup risiko inkonsistensi antar staff finance yang menangani manual.

### 3. Pemicu untuk meninjau ulang otomasi (Opsi A)

ADR ini TIDAK menutup pintu otomasi — ia menundanya sampai salah satu dari:

- Populasi bertambah signifikan dari 16 order (ukur ulang dengan query §Context tiap kali ADR ini
  dirujuk kembali).
- Pertanyaan terbuka soal dokumen campuran (§Context) sudah terjawab finance.
- Ada permintaan eksplisit untuk membangun, lepas dari angka volume.

Bila salah satunya terpenuhi, task berikutnya adalah `/start-task` dengan ADR ini sebagai rujukan
keputusan (lewati `/analisa-kebutuhan` — sudah diputuskan di sini), BUKAN menulis ADR baru.

## Consequences

**Yang didapat**

- Finance punya SOP tertulis dan konsisten untuk kasus yang selama ini ditangani ad-hoc per orang.
- Dasar keputusan tertulis siap dipakai kapan pun otomasi dianggap sepadan, tanpa perlu
  `/analisa-kebutuhan` ulang.
- Batas amandemen atas ADR-0119 dan keputusan 22 Juli dinyatakan eksplisit dan SEMPIT — tidak
  membuka celah salah paham bahwa aturan lama untuk populasi umum ikut berubah.

**Yang dibayar**

- Tetap kerja manual — tidak ada pengurangan beban finance sekarang.
- Risiko inkonsistensi antar staff tetap ada sampai SOP ini benar-benar diikuti (tidak ada gerbang
  sistem yang memaksanya).
- Kasus dokumen campuran kondisi tetap tanpa jawaban sampai finance mengonfirmasi — ditangani
  manual kasus-per-kasus sementara itu.

**Batas yang sengaja tidak dilewati**

Tidak membangun otomasi apa pun sekarang. Tidak mengubah [[ADR - 0025 Log Sumber vs Input WMS +
Stempel Penginput]] Decision #8 maupun [[ADR - 0124 Input Retur Gudang Diukur Komposisinya Dulu,
Lalu Konfirmasi Massal Hanya untuk Baris Cocok]] untuk populasi retur pada umumnya — amandemen di
sini sempit dan bersyarat (reject **dan** kompensasi logistik menyusul saja). Tidak menjawab kasus
dokumen retur campuran kondisi.

**Konsekuensi deploy**

Tidak ada. ADR ini murni dokumentasi SOP, tanpa kode, tanpa env baru, tanpa deploy.

## Dokumen Terkait

- [[ADR - 0119 Kompensasi TikTok Dipisah Menurut Sudah atau Belum Ada Uang Masuk]] — aturan Kasus
  1 (live), dan bagian yang diamandemen sempit oleh ADR ini
- [[ADR - 0056 Penyesuaian Statement TikTok Menambah Payout Order]] — asal istilah
  `LOGISTICS_REIMBURSEMENT`, populasi order CANCELLED (payout≈0, tanpa retur — tidak tersentuh ADR ini)
- [[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]] — Decision #8, asal aturan "tiga
  kondisi sama-sama menambah stok"
- [[ADR - 0124 Input Retur Gudang Diukur Komposisinya Dulu, Lalu Konfirmasi Massal Hanya untuk
  Baris Cocok]] — konteks terbaru kondisi Reuse/Rework/Reject, batas yang sengaja tidak dilewati
- [[ADR - 0016 Retur Grouped per Faktur + Tanggal Retur]] — dasar kenapa dokumen retur bisa berisi
  banyak order/SKU (sumber pertanyaan terbuka dokumen campuran)
- [[ADR - 0024 Retur Gerbang Payout + Tanggal per-Solution]] — mekanisme gerbang payout retur yang
  berdekatan konsepnya
- [[Finance - Proses Retur dan Piutang Marketplace]] — dok domain yang diperbarui bersamaan
