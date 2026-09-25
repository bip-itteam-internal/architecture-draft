## Untuk Manajemen

**Apa yang berubah di layar.** Di Dashboard Insentif, Finance mendapat langkah baru di akhir tiap periode: **bekukan dan setujui**. Angka insentif per orang yang sudah disetujui dikunci dan tidak berubah lagi walau data penjualan bergeser sesudahnya. Di slip gaji muncul baris baru bernama **Insentif**, terpisah dari **Bonus**. Baris itu hanya muncul bagi orang yang punya insentif yang sudah disetujui pada periode itu, dan nilainya tidak bisa diketik bebas: sistem menolak angka yang tidak sama dengan yang disetujui Finance. Finance juga mendapat laporan pencocokan: insentif yang sudah disetujui dibandingkan dengan yang sudah terbayar di slip.

**Siapa yang terdampak.** Finance (menyetujui, mencocokkan), HR (tidak lagi mengetik angka insentif dari layar lain), sekitar 37 orang marketing penerima insentif profit (angkanya muncul di slip dengan nama yang jelas), dan Supervisor marketing (tetap menulis target timnya, tetapi tidak lagi menjadi pemberi persetujuan pembayaran insentif timnya).

**Yang tidak dijanjikan.** Pembayaran lewat transfer bank tetap di luar sistem. Hitungan pajak mengikuti cara yang sudah dipakai slip gaji hari ini dan perlakuannya masih menunggu konfirmasi Finance dan HR. Bonus di luar insentif tetap diketik manual seperti sekarang, dan sistem tidak bisa mencegah orang memasukkan insentif ke kolom Bonus; yang disediakan adalah aturan tertulis dan laporan pencocokan yang memperlihatkan selisihnya. Insentif Host Live, affiliate, dan CRM tidak ikut karena belum punya sumber angka di sistem. Pencabutan peran akses "insentive" adalah keputusan terpisah.

**Perkiraan besaran kerja.** Sedang. Backend di dua service (penyimpanan dan persetujuan insentif; komponen dan pemeriksaan di payroll), dua layar web (persetujuan di Dashboard Insentif, kolom Insentif dan pencocokan di Payroll), dan penyesuaian kecil label di aplikasi. Enam task berurutan untuk satu developer backend dan satu developer frontend; satu task lanjutan menunggu payroll ERP menghitung gaji sendiri.

## Deskripsi

*Insentif profit marketing dibayar lewat slip gaji sebagai komponen `Insentif` yang terpisah dari `Bonus`, dan satu-satunya sumber nilainya adalah snapshot hasil insentif per orang per periode yang dikunci lalu disetujui Finance di insentive-service. Payroll menolak baris Insentif yang tidak cocok dengan snapshot yang disetujui, snapshot hanya bisa terbayar satu kali, dan komponen Insentif tidak pernah boleh hidup di master gaji supaya tidak kembali ke beban gaji yang dipakai menghitung profit insentif. Menjawab TBD jalur pembayaran di [[Finance - Proses Insentif]] dan mengamandemen [[ADR - 0081 Insentif Saya Pindah ke MyBharata di Dalam Slip Gaji]] §4.*

- **Status**: 🟡 **Diusulkan**, disetujui pemilik produk 2026-09-25 lewat percakapan `/analisa-kebutuhan`. **T1 (snapshot + persetujuan Finance) di kode, belum merged** per 2026-09-25: branch `feat/insentif-snapshot` bip-erp; kontraknya di [[API - Insentive Service]]. T2 sampai T8 belum. Daftar task: `Workspace/ANALISA - Insentif Dibayar lewat Slip Gaji.md` (papan kerja, bukan dok terbit).
- **Path di repo**: `bip-erp/services/insentive/snapshot_insentif*.go` (baru) · `bip-erp/services/insentive/func.go` (penulis `disetujui` pada target, pemakai `hitungProfitDashboard`) · `bip-erp/shared-library/common/gerbang_insentif.go` (gerbang persetujuan Finance) · `bip-erp/shared-library/models/insentive/models.go` (model snapshot) · `bip-erp/services/payroll/models_component.go` (komponen `Insentif`) · `bip-erp/services/payroll/impor_run.go` (pemeriksaan baris Insentif) · `bip-erp/services/payroll/employee_salary_handlers.go` (penolakan di master) · `bip-erp/services/payroll/run_publish.go` (tanda terbayar) · `erp-frontend/src/app/(main)/finance/incentive/dashboard/page.tsx` · `erp-frontend/src/features/hris/payroll/` (kolom Insentif, pencocokan)
- **Tanggal**: 2026-09-25

## Context

**Kebutuhannya bukan "insentif lewat payroll".** Kebutuhannya: setiap rupiah insentif yang dibayar berasal dari angka yang sudah dikunci dan disetujui Finance, dibayar tepat satu kali, tidak diketik ulang, dan bisa ditelusuri dari slip ke hitungannya. Hari ini tidak satu pun terpenuhi, dan masalah terbesarnya di hulu, bukan di payroll.

**Yang ada di kode (`bip-erp` origin/main 2026-09-24):**

- **Insentif profit tidak pernah tersimpan.** `hitungProfitDashboard` menghitung setiap kali dibaca dan hanya menyimpan hasilnya di cache memori 15 menit (`services/insentive/func.go:1264-1296`). Satu-satunya angka bayar per orang adalah `insentif` dan `layak_dibayar` pada baris dashboard (`func.go:1855-1864`). Tidak ada angka yang bisa dikunci.
- **Skema profit tidak punya persetujuan sama sekali.** Field `disetujui` pada target tidak pernah ditulis `true`; satu-satunya penulisnya `$setOnInsert "disetujui": false` (`func.go:546`), sehingga penjaga "target terkunci sesudah hasil disetujui" (`business_rules.go:230-232`) tak pernah menyala.
- **Persetujuan lama `/results` praktis mati.** Approve hanya menerima status `DRAFT` (`main.go:2130`), sedangkan hitungan lama menulis `CALCULATED` atau `DISQUALIFIED` (`func.go:145, 182`). Gerbangnya (`bolehSetujuiInsentif`, `shared-library/common/gerbang_insentif.go:34-43`) meloloskan atasan marketing dan tidak membandingkan penyetuju dengan penerima. Supervisor divisi juga menulis target Leader dan ICC divisinya (`services/insentive/gerbang_target.go`, [[ADR - 0079 Target Profit Satu Pintu di Insentif, KPI Membacanya]] §2), jadi penetap target bisa sekaligus pemberi perintah bayar.
- **Payroll tidak punya masukan pendapatan per periode.** Run bulanan hanya membaca master gaji, konfigurasi, dan absensi (`services/payroll/payroll_calc.go:376-497`). Satu-satunya jalan baris per periode adalah run `import` ([[ADR - 0070 Impor Payroll Run dari Spreadsheet HRD untuk Backfill Riwayat Gaji]]), yang mewajibkan nama baris ada di master komponen (`impor_run.go:204-217`).
- **Flag `taxable` dan `bpjs_base` tidak dibaca hitungan.** Keduanya hanya ditulis CRUD (`component_handlers.go:92-93`). PPh 21 selalu TER atas seluruh pendapatan (`payroll_calc.go:483-484`), dasar BPJS adalah dua field master `UpahBpjsKesehatan`/`UpahBpjsKetenagakerjaan`. Baris pendapatan apa pun menambah bruto bulan itu dan tidak menyentuh dasar BPJS.
- **Beban gaji untuk profit insentif dibaca dari master, bukan dari run.** `GET /employer-cost` merakit ulang slip dari `employee_salary` (`employee_salary_handlers.go:174-246`, `payroll_calc.go:252-275`). Baris run tidak ikut; nilai di `component_values` master ikut. Inilah yang menentukan letak komponen Insentif.
- **Pembukuan sudah memisahkan insentif dari bonus.** Akun Accurate 6102 "Beban Bonus & Insentif Marketing" dan 6202 "THR, Bonus" dibedakan, dan 6102 dikecualikan dari opex insentif karena melingkar ([[ADR - 0033 Beban Operasional Insentif dari Proyek Accurate]], `services/integration/internal/usecase/incentive_opex_accurate.go:45, 54, 57`).
- **Aplikasi sudah siap.** Slip Gaji MyBharata di `dev` merender baris pendapatan secara generik, jadi baris Insentif tampil tanpa perubahan kode. Tabel run di web memakai daftar nama kolom tetap, sehingga baris baru hanya terlihat di total sampai kolomnya ditambah.

**Data produksi (diukur 2026-09-25, baca-saja).** `payroll_db` memuat **satu** run sepanjang masa: bertipe `import`, "GAJI BULAN AGUSTUS 2026", periode 2026-07, dibayar 2026-09-01, 174 baris. Hanya satu baris memuat `Bonus` (Kyura Supervisor, Rp9.379.908); tidak ada satu pun dari 180 master gaji yang memegang nilai Bonus. `insentive_db`: 71 target (Agustus 33, September 38) seluruhnya `disetujui: false`; `incentive_results` 6 dokumen DRAFT skema lama. Artinya jalur yang hari ini dipakai: HR mengetik angka insentif ke kolom Bonus di sheet gaji HRD, lalu sheet itu diimpor. Apakah Bonus Juli itu insentif atau bonus lain **tidak bisa dijawab data**, karena keduanya tercampur dalam satu kolom. Dari 78 pemegang peran insentif, hanya satu yang punya Bonus di slip Juli; sisanya dibayar di luar slip atau belum dibayar (**asumsi**, dikonfirmasi Finance).

**Gerbang aturan bisnis.** `mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md` tidak menyebut insentif, bonus, PPh 21, dasar BPJS, maupun tanggal tutup payroll. Otoritas angka insentif tetap SK Direktur 010 dan 011/2026 ([[Finance - Incentive]]).

**Status landasan.** [[ADR - 0081 Insentif Saya Pindah ke MyBharata di Dalam Slip Gaji]] masih 🟡 (M1 live, M2 sampai M5 belum), dan §4-nya menetapkan insentif "dibayar terpisah" dari slip. Keputusan ini mengubah fakta itu, jadi §4 diamandemen di sini. [[ADR - 0070 Impor Payroll Run dari Spreadsheet HRD untuk Backfill Riwayat Gaji]] ✅ dan [[ADR - 0079 Target Profit Satu Pintu di Insentif, KPI Membacanya]] ✅ adalah kenyataan; engine payroll yang menghitung gaji sendiri **ada di kode tetapi belum dipakai di prod**.

## Decision

### 1. Insentif profit dibayar lewat slip gaji, komponen `Insentif` terpisah dari `Bonus`

Payroll mendapat komponen pendapatan baru bernama **`Insentif`**. `Bonus` tetap untuk bonus lain (kebijakan Direksi, prestasi) dan tetap diketik manual. Pemisahan ini mengikuti pembukuan yang sudah membedakan akun 6102 dan 6202, dan membuat slip bisa ditelusuri ke hitungannya.

Aturan tertulis yang mengikat: **insentif profit wajib dibayar lewat komponen `Insentif`, tidak lewat `Bonus`.** Sistem tidak bisa menegakkannya terhadap `Bonus` yang memang bebas; penangkalnya laporan pencocokan di §6.

### 2. Snapshot hasil insentif adalah satu-satunya sumber angka bayar

Insentive-service menyimpan **snapshot** per (karyawan, periode, level): target, realisasi, pencapaian, tarif, insentif, status gugur beserta alasannya, dan `layak_dibayar`, persis seperti baris dashboard saat dibekukan. Snapshot dibuat oleh Finance lewat aksi **bekukan periode**, dan hanya untuk periode yang sudah final (lewat akhir tanggal 25 bulan berikutnya, `PeriodeInsentif`). Sesudah dibekukan, perubahan data penjualan tidak mengubah snapshot.

Seseorang yang dinilai di dua level (Leader yang juga punya toko) punya dua snapshot, dan keduanya dibayar sebagai dua baris `Insentif` atau satu baris berjumlah; pilihannya diputuskan di `/plan`, dengan syarat tiap baris tetap membawa rujukan snapshot-nya.

Koreksi sebelum dibayar = batalkan snapshot orang itu lalu bekukan ulang, dengan alasan tertulis. Snapshot yang sudah terbayar **tidak bisa** dibatalkan; koreksinya jadi penyesuaian di periode berikutnya.

### 3. Penyetuju akhir adalah Finance, dan tidak seorang pun menyetujui insentifnya sendiri

- Persetujuan akhir yang membuat snapshot boleh dibayar dipegang **Finance**. Hak menyetujuinya diberikan lewat izin di paket RBAC Finance ([[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]), bukan lewat peran `insentive`. Sebagaimana dikodekan di T1: izin `finance.insentif.approve` (paket `finance_insentif_setujui`), dengan fallback tier `finance` supervisor/admin; membekukan cukup `finance.insentif.freeze` (staf pun boleh).
- **Direktur boleh menyetujui** (keputusan pemilik produk 2026-09-25, saat review T1). Ia lolos lewat `finance: supervisor` turunan jabatan, sejalan dengan [[ADR - 0079 Target Profit Satu Pintu di Insentif, KPI Membacanya]] yang menempatkan Direktur bersama Finance untuk target level supervisor. Aturan "bukan penerima snapshot itu" tetap berlaku untuknya.
- Penyetuju ditolak bila ia penerima snapshot itu, termasuk staf Finance.
- **Atasan marketing tidak lagi menjadi penyetuju akhir.** Apakah Supervisor memberi persetujuan pertama (tahap pemeriksaan tanpa efek bayar) **TBD konfirmasi Finance**. Rancangan wajib bekerja dengan satu tahap Finance saja.
- Begitu satu periode disetujui, target periode itu terkunci: `disetujui` pada target akhirnya ditulis, dan penjaga yang sudah ada di `BolehUbahTarget` mulai berlaku.

### 4. Komponen `Insentif` tidak pernah hidup di master gaji

Mengisi `Insentif` pada `component_values` master **ditolak**. Dua alasannya: nilai master terulang setiap bulan, dan nilai master masuk ke `/employer-cost` sehingga insentif ikut menjadi beban gaji yang mengurangi profit insentif (melingkar, kelas yang sama dengan akun 6102 di ADR 0033). Insentif hanya masuk sebagai **baris per periode di run**. Aturan "`/employer-cost` tidak memuat insentif" dikunci test.

### 5. Hanya penerima dengan snapshot yang disetujui yang mendapat baris

| Keadaan pada periode itu | Di slip |
|---|---|
| Snapshot disetujui, nilai > 0 | Baris `Insentif` sebesar snapshot |
| Snapshot gugur atau nilai 0 | Tidak ada baris; tetap tercatat di pencocokan beserta alasannya |
| Bukan penerima insentif profit | Tidak ada baris, termasuk tanpa baris Rp0 |
| Snapshot belum disetujui saat run ditutup | Tidak ada baris; ikut run berikutnya, tidak hangus |

Siapa penerima ditentukan insentive-service dari hierarki HRIS dan pemetaan toko (`SusunEntitas`), **bukan** dari peran `insentive` (78 pemegang peran, hanya 37 berbaris profit per Agustus 2026) dan bukan dari daftar di payroll.

### 6. Masuk ke payroll: jembatan sekarang, tarikan langsung nanti

**Jembatan (mengikat sekarang).** Selama gaji dihitung di sheet HRD dan masuk lewat run `import`:

- Finance mengekspor snapshot yang disetujui dalam bentuk yang langsung dipakai sheet HRD (kolom `Insentif` per karyawan beserta rujukan snapshot).
- Impor payroll menerima baris `Insentif` **hanya bila** nilainya sama dengan snapshot yang disetujui untuk karyawan itu, dan snapshot itu belum terbayar. Tidak cocok berarti ditolak dengan pesan yang menyebut selisihnya.
- Baris run menyimpan rujukan snapshot (id hulu di hilir). Saat run di-*publish*, snapshot yang dirujuk ditandai **terbayar di run X**, idempoten, dan satu snapshot hanya bisa terbayar sekali.
- Finance mendapat pencocokan per periode: disetujui, terbayar, belum terbayar, dan (sebagai tanda bahaya) Bonus di slip penerima insentif pada periode yang sama.

**Tarikan langsung (TBD).** Bila engine payroll kelak menghitung gaji sendiri, run bulanan menarik snapshot yang disetujui sebagai baris `Insentif` dengan aturan yang sama. Waktunya bergantung pada rencana pemakaian engine payroll, yang belum ada.

### 7. Pajak dan BPJS

Baris `Insentif` menambah bruto bulan diterimanya dan ikut PPh 21 TER seperti pendapatan lain; ia tidak mengubah dasar upah BPJS karena dasar itu field master tersendiri. Itu perilaku engine hari ini, tanpa perubahan kode. **TBD konfirmasi Finance dan HR** bahwa perlakuan ini benar. Karena flag `taxable`/`bpjs_base` tidak dibaca hitungan, mengubah flag itu **tidak** mengubah pajak; perbedaan perlakuan, bila diputuskan, menuntut perubahan engine dan keputusan tersendiri.

### 8. Waktu bayar

Insentif periode N final akhir tanggal 25 bulan N+1, lalu dibekukan dan disetujui Finance, lalu dibayar pada run pertama yang dibuat sesudah persetujuan itu. Tanggal tutup payroll tidak diatur di mana pun (**TBD**); aturan "run pertama sesudah persetujuan" berlaku apa pun tanggalnya.

### 9. Amandemen ADR 0081 §4

Kalimat "Kartu Insentif berlabel hitungan yang dibayar terpisah" dan "Tidak menyandingkan insentif dengan komponen Bonus payroll" diganti: kartu Insentif tetap rincian hitungan, dan bila snapshot periode itu sudah terbayar, kartu boleh menyebut **"dibayarkan melalui slip gaji \<bulan run\>"** dari tanda terbayar di snapshot, bukan dari mencocokkan angka di aplikasi. Aplikasi tetap tidak menjumlahkan insentif dengan gaji bersih.

## Consequences

### Yang membaik

- Angka yang dibayar sama dengan angka yang disetujui, dan tidak berubah sesudahnya.
- HR tidak lagi mengetik angka insentif dari layar lain; salah ketik ditolak saat impor.
- Satu snapshot tidak bisa dibayar dua kali, dan insentif yang belum terbayar terlihat.
- Penetap target tidak lagi menjadi pemberi perintah bayar timnya.
- Slip memisahkan insentif dari bonus seperti pembukuan memisahkannya.
- Penjaga target terkunci di [[ADR - 0079 Target Profit Satu Pintu di Insentif, KPI Membacanya]] akhirnya menyala.

### Yang memburuk atau tetap terbuka

- Finance mendapat langkah kerja baru tiap periode (bekukan, setujui, ekspor, cocokkan).
- Payroll mulai bergantung pada insentive-service saat impor dan publish; insentive-service mati berarti impor yang memuat baris Insentif ditolak (gagal-tertutup, disengaja).
- Jembatan lewat sheet masih punya satu langkah manusia (menyalin kolom ekspor ke sheet); yang dijamin adalah bahwa salah salin ditolak, bukan bahwa langkahnya hilang.
- `Bonus` tetap celah: insentif yang sengaja dimasukkan ke Bonus lolos, dan hanya terlihat di pencocokan.
- Perlakuan PPh 21, dasar BPJS, tahap persetujuan Supervisor, dan tanggal tutup payroll masih TBD.

### Yang sengaja tidak dilakukan

- **Tidak membuat tipe run baru `insentif`** (pola THR). Menambah jenis run yang harus dikenali penjaga duplikat periode dan layar run, sementara engine belum dipakai di prod; jembatan impor sudah cukup, dan tarikan langsung kelak memakai run bulanan.
- **Tidak menghidupkan kembali persetujuan `/results` skema lama.** Skema KPI-multiplier sudah dicabut; rute dan gerbangnya dibereskan sebagai task terpisah.
- **Tidak mengatur transfer bank.** Payroll memang "tanpa pembayaran/transfer" ([[Microservices - Payroll Service]]).
- **Tidak mencabut peran `insentive` di sini.** Keputusan terpisah; di sini cukup bahwa persetujuan dan penerima tidak lagi bergantung padanya.

## Dokumen Terkait

- [[Finance - Proses Insentif]] · [[Finance - Incentive]] · [[Finance - Proses Gaji dan Iuran BPJS]] · [[Finance - Proses Pajak]] · [[Finance - Kalender dan Rantai Tenggat]]
- [[Microservices - Insentive Service]] · [[Microservices - Payroll Service]] · [[API - Insentive Service]] · [[HRIS - Payroll]] · [[HRIS - Payroll Persona]]
- [[ADR - 0081 Insentif Saya Pindah ke MyBharata di Dalam Slip Gaji]] · [[ADR - 0079 Target Profit Satu Pintu di Insentif, KPI Membacanya]] · [[ADR - 0070 Impor Payroll Run dari Spreadsheet HRD untuk Backfill Riwayat Gaji]] · [[ADR - 0033 Beban Operasional Insentif dari Proyek Accurate]] · [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]
