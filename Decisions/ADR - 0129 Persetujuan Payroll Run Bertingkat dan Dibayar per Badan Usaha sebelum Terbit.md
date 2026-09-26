## Untuk Manajemen

**Apa yang berubah di layar.** Run gaji tidak lagi disetujui satu orang dengan satu tombol. Setelah staf HR selesai merekap dan menekan **Ajukan**, run berjalan berurutan ke empat penanda tangan: **Cost Control** (memeriksa potongan, boleh menulis catatan per karyawan), **SPV HRD**, **SPV Finance**, lalu **Direktur**. Tiap penanda tangan melihat run itu di antrean "menunggu tanda tangan Anda" dan mendapat notifikasi saat gilirannya tiba. Setelah Direktur menandatangani, muncul daftar **pembayaran per badan usaha** (PT dan 39 CV): tiap accounting CV menandai CV-nya sudah dibayar. Slip baru bisa **diterbitkan** setelah seluruh badan usaha dalam run itu tercatat lunas. Karyawan yang sudah keluar dan akunnya dinonaktifkan menerima slipnya lewat **email pribadi** yang terdaftar, sebagai PDF yang dikunci kata sandi tanggal lahir.

**Siapa yang terdampak.** Staf HR (merekap dan mengajukan, mengoreksi baris bila ada catatan), Cost Control, SPV HRD, SPV Finance, Direktur dan Corporate Secretary, accounting CV (menandai pembayaran), seluruh karyawan (slip tetap terbit di MyBharata seperti sekarang, hanya waktunya menunggu pembayaran selesai), dan mantan karyawan (menerima slip lewat email).

**Yang tidak dijanjikan.** Transfer bank tetap dilakukan di luar sistem; yang dicatat hanya bahwa badan usaha itu sudah membayar, oleh siapa, dan kapan. Tanda tangan yang sudah diberikan **tidak gugur** bila satu baris dikoreksi sesudahnya; yang disediakan adalah catatan koreksi yang terlihat oleh penanda tangan berikutnya. Urutan penanda tangan tetap (tidak bisa diatur dari layar). Slip yang sudah terbit tidak bisa ditarik kembali. Kata sandi PDF adalah penghalang pembaca sambil lalu, bukan enkripsi kuat. Email kantor tidak ada di sistem, jadi slip dikirim ke email pribadi.

**Perkiraan besaran kerja.** Besar. Satu service backend (payroll) plus izin baru di pustaka bersama, notifikasi baru (dua service naik bersama), perubahan kecil di service insentif, satu layar web (detail run payroll dengan alur tanda tangan dan panel pembayaran), dan konfigurasi paket hak untuk lima jabatan. Tujuh task berurutan; dua di antaranya bisa dikerjakan paralel.

## Deskripsi

*Payroll run disetujui berurutan oleh Cost Control, SPV HRD, SPV Finance, dan Direktur, masing-masing lewat izin tahapnya sendiri, dengan jejak keputusan per tahap. Sesudah tahap terakhir, pembayaran dicatat per badan usaha penggaji di dalam run oleh pemegang CV yang ditugaskan, dan penerbitan slip terkunci sampai seluruh badan usaha dalam run itu lunas. Saat terbit, karyawan yang akunnya nonaktif dikirimi PDF slip terkunci ke email pribadinya. Mengganti persetujuan satu langkah `payroll.approve` yang selama ini menutup setujui sekaligus terbitkan, dan memindahkan tanda insentif terbayar dari [[ADR - 0125 Insentif Profit Dibayar lewat Slip Gaji dari Snapshot yang Disetujui Finance]] ke saat badan usaha karyawan itu lunas.*

- **Status**: 🟡 **Diusulkan**, disetujui pemilik produk 2026-09-26 lewat percakapan `/analisa-kebutuhan`. **P1 (izin per tahap + paket) merged** (bip-erp PR #2095, 2026-09-26), live DEV, prod belum; gerbang rute belum dipindah (P2). Daftar task: `Workspace/ANALISA - Persetujuan Payroll Bertingkat.md` (papan kerja, bukan dok terbit).
- **Path di repo**: `bip-erp/shared-library/common/catalog_payroll.go` (izin per tahap + paket) · `bip-erp/services/payroll/models_payroll_run.go` (tahap, riwayat, pembayaran per badan usaha) · `bip-erp/services/payroll/run_jenjang*.go` (baru) · `bip-erp/services/payroll/run_approve.go` · `bip-erp/services/payroll/run_publish.go` · `bip-erp/services/payroll/payslip_pdf.go` (proteksi kata sandi) · `bip-erp/services/payroll/slip_email*.go` (baru) · `bip-erp/services/payroll/routes.go` · `bip-erp/shared-library/models/notification/models.go` (kategori inbox) · `bip-erp/services/insentive/snapshot_internal.go` (gerbang tandai-terbayar) · `erp-frontend/src/features/hris/payroll/` · `erp-frontend/src/features/direktur/hooks/use-payroll-menunggu.ts`
- **Tanggal**: 2026-09-26

## Context

**Kebutuhannya bukan "tambah tahap persetujuan".** Tiga hal yang hari ini tidak dijamin sistem:

1. **Empat pihak berbeda menandatangani angka gaji yang sama, berurutan, dan tercatat.** Pembuat rekap bukan penyetuju. Di kertas hari ini: staf HR merekap, Cost Control mengecek silang potongan per orang (dan perlu melihat rincian tiap potongan), SPV HRD, SPV Finance, lalu Direktur menandatangani (urutan disampaikan pemilik produk 2026-09-26; versi pertama 2026-09-25 menaruh Direktur di posisi kedua dan sudah dikoreksi).
2. **Slip tidak tampil ke karyawan sebelum uangnya keluar**, padahal pembayaran dilakukan accounting tiap CV sendiri-sendiri. Pemilik produk: semua slip menunggu sampai **seluruh** CV membayar.
3. **Karyawan yang sudah keluar tetap menerima slipnya.** Mereka masih ada di rekap bulan terakhir tetapi tidak bisa login MyBharata lagi.

**Yang ada di kode (`bip-erp` origin/main 2026-09-26):**

- **Satu langkah, satu izin.** Status run hanya `draft`, `approved`, `published` (`services/payroll/models_payroll_run.go:9-13`). Approve (`draft → approved`, `run_approve.go:26-34`) dan publish (`approved → published`, `run_publish.go:30-69`) memakai gerbang yang sama, `gate(common.PermPayrollApprove, isApprover)` (`routes.go:112-113`); izin itu didefinisikan sebagai "keputusan final: approve + publish" (`shared-library/common/catalog_payroll.go:31`). `isApprover` identik `isHRAdmin` (`rbac.go:30`). Tidak ada penjaga pembuat ≠ penyetuju, tidak ada status tolak, tidak ada riwayat selain pasangan `approved_by/at`, `published_by/at` (`models_payroll_run.go:43-48`).
- **Satu run memuat seluruh badan usaha.** Perusahaan hanya ada per baris, sebagai `CompanySnapshot` (`models_payroll_run.go:84`, `models_company.go:29-37`). Tidak ada field perusahaan di level run.
- **Direktur kena 403 di dev** saat approve dan publish. Gerbangnya izin murni (`IzinPayrollEfektifDari`, `catalog_payroll.go:156-168`): Direktur lolos hanya bila JWT-nya memuat `payroll.approve` atau klaimnya sama sekali tanpa izin `payroll.*` dan ia `hris: admin`. Jabatan `SetaraDirektur` (`shared-library/common/jabatan_direktur.go:24-47`) tidak dipakai payroll.
- **Pola jenjang sudah ada di procurement dan dipakai ulang di sini**, bukan dibangun tandingannya: status kasar + `TahapSaatIni` + `JenjangWajib` (`services/procurement/pengajuan_barang.go:19-21, 210-211`), riwayat per tahap (`pengajuan_budget.go:71-77`), gerbang murni per tahap dan antrean yang memakai fungsi yang sama (`pengajuan_barang_gate.go`), penjaga pengaju ≠ penyetuju (`pengajuan_budget_approval_logic.go:23-39`), penerima notifikasi lewat `/internal/permission-holders` (`services/employee/permission_holders.go:52-88`, **tanpa fallback tier**), dan cabang pembayaran CV lewat penugasan pemegang CV (`shared-library/common/cv_penugasan.go:54`).
- **Pemetaan badan usaha payroll ke CV finance sudah ada**: `payroll_company_id` pada entitas CV (`services/finance/akuntansi_cv_entitas.go:39`). [[ADR - 0096 Buku Besar 40 CV Dibangun di ERP dengan FINCON sebagai Spesifikasi]] sudah merencanakan daftar bayar per badan usaha di payroll dan penugasan pemegang CV untuk Junior Accountant.
- **Tidak ada notifikasi payroll sama sekali.** `git grep notification|inbox` di `services/payroll` kosong; `notification.InboxCategories` tidak punya kategori payroll (`shared-library/models/notification/models.go`).
- **Email dengan lampiran sudah bisa.** Notification-service `POST /email/send` lewat Resend, lampiran base64 dan idempotency key (`shared-library/notification/email/email.go:27, 63`; `services/notification/main.go:704, 799-845`), env terpasang di compose prod. Pola "PDF di server → email pribadi → jejak kiriman" sudah dipakai PKWT (`services/employee/contract_pkwt_handler.go:209-337`). PDF slip dibuat di server (`services/payroll/payslip_pdf.go:75, 188`, `go-pdf/fpdf`, belum pernah memakai `SetProtection`).
- **Payroll tidak tahu siapa yang nonaktif.** Sumber kebenaran aktif adalah `system_authentication.is_active` (`shared-library/models/employee/models.go:527`); resign diterapkan cron yang mematikan akun (`services/employee/resign.go:172`). Satu-satunya email karyawan adalah `personal_data.email_address` (`models.go:356`); tidak ada email kantor. Tanggal lahir ada di `personal_data.date_of_birth` (`models.go:350`). Payroll memanggil `/internal/export/all` tetapi hanya membaca lima field (`services/payroll/employee.go:14-22`).
- **Konsumen status run.** Slip karyawan hanya membaca run `published` lewat satu penjaga `findMyPayslipLine` (`run_publish.go:173-196`); MyBharata tidak menyaring status sendiri, jadi status baru tidak mematahkannya. Web: `RunStatus` (`erp-frontend/src/features/hris/payroll/types.ts:188`) dipetakan lewat `Record` sehingga status baru membuat tsc merah (baik), tetapi antrean Direktur menganggap "menunggu" = `draft` (`src/features/direktur/hooks/use-payroll-menunggu.ts:30-37`) sehingga run di tahap antara salah masuk Riwayat. Tombol Setujui dan Terbitkan di web tidak digerbang izin sama sekali; hanya backend yang menolak.

**Data produksi (diukur 2026-09-26, baca-saja).** `payroll_db` memuat dua run: "GAJI BULAN AGUSTUS 2026" (`import`, `published`, 174 baris) dan "Gaji September 2026" (`draft`, 173 baris). **Keduanya memuat karyawan dari 40 badan usaha** (PT Bharata Internasional + 39 CV) dalam satu run. Jadi "lunas per CV" berarti sampai 40 tanda pembayaran per run.

**Gerbang aturan bisnis.** `mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md` tidak mengatur persetujuan gaji, pembayaran, tanggal gajian, maupun penanda tangan (yang menyangkut gaji hanya potongan SP II 25% gaji pokok, `:92`, dan upah skorsing, `:104`). Keputusan ini tidak menyimpangi pasal apa pun.

**Status landasan.** [[HRIS - Payroll]] ⚠️ dan [[Microservices - Payroll Service]] ⚠️ adalah kenyataan (live prod). [[ADR - 0096 Buku Besar 40 CV Dibangun di ERP dengan FINCON sebagai Spesifikasi]] 🟡 dan [[ADR - 0057 Penyetuju Pengajuan Pembelian Ditetapkan per Tahap]] 🟡 masih rencana; keputusan ini meminjam **polanya**, tidak bergantung pada kodenya selesai, kecuali penugasan pemegang CV yang sudah ada di kode.

## Decision

### 1. Jenjang tetap empat tahap, status tetap kasar

Status run menjadi `draft → dalam_persetujuan → approved → published`. Posisi di dalam jenjang disimpan terpisah di `tahap_saat_ini`, dengan urutan tetap di kode: `cost_control`, `spv_hrd`, `spv_finance`, `direksi`. Satu status per tahap ditolak dengan alasan yang sama dengan procurement: jenjangnya sudah disimpan, dan status per tahap memaksa setiap konsumen status ikut berubah tiap kali jenjang berubah. Mesin alur yang bisa dikonfigurasi dari layar ditolak ([[ADR - 0057 Penyetuju Pengajuan Pembelian Ditetapkan per Tahap]] §urutan tetap); mesin persetujuan lintas modul juga ditolak karena baru dua pemakai.

- **Ajukan** (`draft → dalam_persetujuan`, tahap `cost_control`) oleh pemegang `payroll.work`. Run dalam persetujuan tidak bisa dihitung ulang atau dihapus.
- **Setujui tahap** memajukan `tahap_saat_ini`; setujui di tahap `direksi` membawa run ke `approved`.
- **Kembalikan** di tahap mana pun mengembalikan run ke staf HR (`tahap_saat_ini` tetap, status tetap `dalam_persetujuan`, ditandai `dikembalikan`), wajib beralasan.
- Setiap keputusan (ajukan, setujui, kembalikan, koreksi, tandai lunas, terbitkan) masuk `riwayat[]` berisi tahap, pelaku, aksi, alasan, waktu.

### 2. Izin per tahap, bukan satu `payroll.approve`

Izin baru di katalog payroll: `payroll.approve.cost_control`, `payroll.approve.hrd`, `payroll.approve.finance`, `payroll.approve.direksi`, `payroll.bayar` (menandai lunas), `payroll.publish` (menerbitkan). Diberikan lewat paket bernama yang menempel di jabatan ([[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]): Cost Control, SPV HRD, SPV Finance, Direktur dan Corporate Secretary, Junior Accountant pemegang CV, dan staf HR untuk publish. `payroll.approve` lama dipensiunkan setelah paket baru terpasang.

**Fallback tier dan isi paket** (diputuskan 2026-09-26 di `/start-task` P1):
- `payroll.approve.*` dan `payroll.bayar` **tanpa fallback tier sama sekali**, hanya lewat paket: pemegang aslinya (Cost Control, SPV Finance, Direktur, accounting CV) bukan orang HR, jadi tier `hris` memang tak pernah menjangkau mereka.
- `payroll.publish` masuk fallback tier `hris` supervisor dan admin.
- Tier admin dan paket `payroll_admin` berhenti memakai "seluruh katalog" dan menjadi daftar eksplisit tanpa izin tahap. Tanpa itu, menambah izin ke katalog diam-diam memberi HR admin keempat tahap sekaligus.
- Paket tanda tangan (Cost Control, SPV HRD, SPV Finance, Direksi) memuat izin tahapnya **plus `payroll.view`**: penanda tangan memang perlu membaca seluruh run, termasuk rincian potongan per karyawan dan dasar potongan kehadiran.
- Paket **Pembayar CV berisi `payroll.bayar` saja, tanpa `payroll.view`**: accounting CV hanya boleh melihat karyawan CV yang ditugaskan kepadanya, lewat daftar bayar sempit (§4), bukan gaji seluruh 40 badan usaha dan master gaji semua orang.

**Jalan masuk layar.** Izin payroll tidak membuka kategori sidebar mana pun (menu Payroll Run menumpang di kategori HRIS), sehingga SPV Finance, Cost Control, Direktur, dan accounting CV tak melihat menu payroll. Tidak ditambah menu baru dan tidak dibuat alias `payroll → hris` (alias itu membuka seluruh kategori HRIS). Jalan masuknya:
- **Portal → Persetujuan** (antrean terpadu, terbuka untuk semua karyawan) menampilkan run payroll hanya kepada orang yang sedang gilirannya, dengan tahap dan tanda boleh-putus; barisnya membuka detail run.
- **Accounting CV** memakai menu yang sudah ada, **Finance → Accounting CV → CV Ditugaskan**, rumah antrean transfer kas CV: ditambah bagian **Gaji** per CV (run menunggu bayar, daftar bayar sempit, tandai lunas, status "N dari M lunas" tanpa rincian CV lain). Baris antreannya per CV yang ditugaskan.
- Notifikasi inbox (§7) mengarah ke tempat yang sama.

- **Satu orang, satu tanda tangan per run.** Orang yang sudah menyetujui satu tahap ditolak di tahap berikutnya pada run yang sama, walau memegang kedua izin. Pengaju ditolak di semua tahap persetujuan.
- **Gerbang dan antrean memakai fungsi yang sama**, supaya run tak pernah tampil di antrean orang yang lalu ditolak saat menekan tombol.

### 3. Koreksi per baris, tanda tangan tetap berlaku, tapi terlihat

Keputusan pemilik produk: bila satu penanda tangan menemukan angka salah, **hanya baris itu** yang dikoreksi staf HR; tanda tangan yang sudah diberikan tetap berlaku. Pengamannya:

- **Cost Control boleh menulis catatan per baris** (karyawan + potongan yang dipersoalkan) saat mengembalikan. *(Keputusan atas saran analis, 2026-09-26.)*
- Koreksi baris saat run `dalam_persetujuan` dicatat di riwayat sebagai `koreksi` beserta nilai sebelum dan sesudahnya, dan ditampilkan kepada **penanda tangan berikutnya** sebagai "berubah sesudah ditandatangani <tahap>". Penanda tangan sebelumnya diberi notifikasi, tetapi tidak dituntut menandatangani ulang.

### 4. Pembayaran dicatat per badan usaha di dalam run

Setelah run `approved`, run memuat daftar badan usaha yang ada di baris-barisnya (dari `CompanySnapshot.ID`). Tiap badan usaha ditandai **lunas** oleh pemegang `payroll.bayar` yang **ditugaskan pada CV itu** (penugasan pemegang CV yang sudah ada, dipetakan lewat `payroll_company_id`); pemegang izin pengawas boleh semua CV. Tanda lunas mencatat pelaku dan waktu, dan bisa dibatalkan selama run belum terbit. Transfer banknya tetap di luar sistem. Accounting CV membaca **daftar bayar sempit** per CV: hanya karyawan CV itu (nama, gaji bersih, rekening bila tersimpan, total transfer, ekspor), dan untuk badan usaha lain hanya status lunas atau belum, tanpa angka.

**Terbitkan hanya bila seluruh badan usaha dalam run itu lunas** (keputusan pemilik produk: semua menunggu). Publish dilakukan manual oleh pemegang `payroll.publish`, bukan otomatis saat CV terakhir lunas, supaya ada satu titik keputusan yang terlihat.

### 5. Insentif terbayar pindah ke saat lunas

Amandemen [[ADR - 0125 Insentif Profit Dibayar lewat Slip Gaji dari Snapshot yang Disetujui Finance]] §6 dan T4: snapshot insentif ditandai `terbayar` saat **badan usaha karyawan itu** ditandai lunas, bukan saat publish. Gerbang rute internal `tandai-terbayar` di insentive-service mengikuti izin yang baru (`payroll.bayar`), karena hari ini ia memeriksa ulang `payroll.approve` pada identitas yang diteruskan. Mekanisme tanda tertunda dan rute ulang tetap, hanya pemicunya yang pindah. Membatalkan tanda lunas tidak otomatis membatalkan tanda terbayar insentif; kasus itu dicatat sebagai TBD.

### 6. Slip untuk karyawan nonaktif dikirim lewat email

Saat run diterbitkan, baris yang karyawannya berakun nonaktif (`system_authentication.is_active = false`) dikirimi PDF slipnya ke `personal_data.email_address` lewat notification-service. PDF dibuat dengan generator yang sama dengan slip MyBharata dan **dikunci kata sandi tanggal lahir** berformat `DDMMYYYY`; isi email menyebut formatnya, tidak nilainya. *(Keputusan atas saran analis, 2026-09-26.)* Setiap kiriman dicatat (run, karyawan, alamat, waktu, hasil) dan bisa dikirim ulang dari layar run. Karyawan nonaktif tanpa email atau tanpa tanggal lahir **tidak dilewati diam-diam**: mereka didaftar sebagai gagal kirim di layar run. Kegagalan email tidak menggagalkan penerbitan.

### 7. Notifikasi ke penanda tangan berikutnya

Kategori inbox baru untuk payroll: "run menunggu tanda tangan Anda", "run dikembalikan", "run siap dibayar", dan "run terbit". Penerima dihitung dari pemegang izin tahap berikutnya (irisan dengan pemegang CV untuk tahap bayar). Pengiriman best-effort; antrean di layar tetap sumber kebenarannya.

## Consequences

- **Run lama tidak disentuh.** Run `published` tetap; run `draft` yang ada ikut alur baru saat diajukan. Tidak ada migrasi status.
- **Kontrak status berubah, jadi backend naik sebelum web**, dan antrean Direktur di web wajib ikut diubah di rilis yang sama. Tombol di web akhirnya digerbang izin per tahap.
- **Deploy**: kategori inbox baru berarti notification-service dan payroll-service naik bersama; payroll butuh env notifikasi (URL + kunci) sehingga `--force-recreate`; izin baru di pustaka bersama berarti service lain ikut dibangun ulang; insentive-service ikut naik karena gerbangnya berubah.
- **Konfigurasi wajib sebelum dipakai**: paket izin dipasang ke lima jabatan dan penugasan pemegang CV untuk 40 badan usaha. Tanpa itu run tertahan di tahap pertama atau di pembayaran. `permission-holders` tidak memakai fallback tier, jadi notifikasi hanya sampai ke pemegang paket.
- **Penerbitan jadi lebih lambat** menurut desain: sampai 40 tanda lunas per run. Keadaan sebagian (misalnya 38 dari 40 lunas) harus terbaca di layar, bukan disimpulkan.
- **Satu orang yang memegang dua jabatan** (mis. merangkap SPV) hanya bisa menandatangani satu tahap per run; tahap lainnya butuh orang lain.
- **TBD**: perilaku insentif bila tanda lunas dibatalkan; apakah run THR yang kecil boleh memakai jenjang yang sama tanpa pengecualian (asumsi: sama); pengirim email khusus payroll atau memakai pengirim umum.

## Dokumen Terkait

[[HRIS - Payroll]] · [[HRIS - Payroll Persona]] · [[Microservices - Payroll Service]] · [[API - Payroll Service]] · [[Finance - Proses Gaji dan Iuran BPJS]] · [[ADR - 0125 Insentif Profit Dibayar lewat Slip Gaji dari Snapshot yang Disetujui Finance]] · [[ADR - 0096 Buku Besar 40 CV Dibangun di ERP dengan FINCON sebagai Spesifikasi]] · [[ADR - 0057 Penyetuju Pengajuan Pembelian Ditetapkan per Tahap]] · [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] · [[ADR - 0070 Impor Payroll Run dari Spreadsheet HRD untuk Backfill Riwayat Gaji]] · [[REF - Alur Persetujuan]]
