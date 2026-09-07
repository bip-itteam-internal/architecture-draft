**Status**: 🟡 Daftar task dari `/analisa-kebutuhan` 2026-09-07. Keputusannya di [[ADR - 0081 Insentif Saya Pindah ke MyBharata di Dalam Slip Gaji]]; dok ini papan kerja, bukan arsitektur. Coret item begitu PR-nya merge, dan pindahkan keadaannya ke dok domain lewat `/sync-docs`.

## Kebutuhan yang dijawab

Orang marketing (37 orang dengan baris insentif profit per Agustus 2026) melihat hitungan insentifnya sendiri dan alasannya dari ponsel, di halaman Slip Gaji MyBharata, tanpa nominal sebelum PIN. Dashboard Insentif dan Master Target tetap di web.

## Urutan yang mengikat

Backend dulu (endpoint keanggotaan, aditif), lalu aplikasi (menumpang rombakan Slip Gaji #134 yang sudah di `dev` tetapi belum rilis), lalu rilis store, baru pencabutan menu web setelah adopsi versi terukur. Tidak ada env baru, tidak ada kategori inbox. Prod dijalankan manusia (skill `deploy-bip-erp` §0).

## Task

### M1. Endpoint keanggotaan insentif milik sendiri
- **Repo**: bip-erp, `services/insentive/func.go` (tetangga `/profit-dashboard/saya`, `registerProfitDashboardRoute`), berkas baru untuk handler + test, `API - Insentive Service` di vault.
- **Isi**: `GET /profit-dashboard/saya/keanggotaan` membalas level tempat pemanggil (`BIP-Employee-ID`) menjadi entitas skema profit (`icc`, `leader`, `supervisor`) dari hierarki dan pemetaan toko yang sudah dipakai penyusun baris dashboard, **tanpa angka dan tanpa menghitung dashboard**. Kosong bila bukan anggota. Tanpa gerbang role, sama seperti `/saya`.
- **Test**: fungsi murni pemilihan keanggotaan; satu test lewat Fiber untuk 401 tanpa identitas; kontrol negatif: pemegang role `insentive` tanpa entitas (pola Host Live) → kosong.
- **Verifikasi**: lewat gateway dev sebagai satu Account Specialist dan satu Host Live; bandingkan bentuk respons, bukan status.
- **Dependensi**: tidak ada.

### M2. Kartu Insentif di daftar Slip Gaji + rincian, MyBharata
- **Repo**: my-bharata, `lib/src/features/insentif/` (baru, meniru `features/kpi/`), `features/payroll/presentation/pages/payslip_page.dart` (daftar campuran), `core/routes/payroll/payroll_pages.dart` + `payroll_routes.dart` (rute rincian insentif di balik `PinGuard`), `core/api/url.dart`, `l10n/app_id.arb` + `app_en.arb`, DI (`data_source_injection`, `repository_injection`, `use_case_injection`, `bloc_injection`).
- **Isi**: daftar bulan = gabungan run payroll published dan dua belas bulan terakhir bila anggota (M1); per bulan kartu Slip Gaji dan kartu Insentif tanpa nominal dan tanpa status; tekan kartu → PIN (rute) → rincian: kartu per peran (target, realisasi, pencapaian, tarif, insentif), gugur + alasan, peringatan "angka ini belum final", rincian biaya termasuk `biaya_gaji` berlabel beban perusahaan, status periode final/belum final; bulan tanpa baris → kalimat kosong yang sama dengan web. Label kartu "hitungan insentif, dibayar terpisah". Aplikasi tidak menjumlahkan/membandingkan dengan gaji bersih.
- **Test**: `payroll_routes_guard_test.dart` mencakup rute baru; test daftar tanpa nominal (kontrol negatif: sisipkan nominal → merah); test "tidak ada penjumlahan gaji+insentif"; test kartu Insentif tak tampil bila keanggotaan kosong; test l10n id/en; `quick_access_items_test.dart` tak perlu berubah (tak ada menu baru).
- **Verifikasi**: flavor dev pada perangkat: buka Slip Gaji → dua kartu → PIN muncul saat kartu ditekan, bukan saat halaman dibuka → rincian benar untuk satu Account Specialist dev; Host Live tanpa kartu Insentif.
- **Dependensi**: M1 di dev; #134 sudah di `dev`.

### M3. Rilis aplikasi
- **Repo**: my-bharata; `scripts/update_version.dart <versi> <code+1>` (dua argumen), Codemagic, Play internal → produksi, App Store Connect.
- **Verifikasi**: versi terpasang di satu perangkat produksi membuka kartu Insentif dengan data nyata; adopsi versi dibaca di Play Console sebelum M4.
- **Dependensi**: M2 merge ke `dev`; backend M1 sudah di prod.

### M4. Cabut menu Insentif Saya di web
- **Repo**: erp-frontend, `src/components/layout/sidebar-menus.tsx` (grup Incentive), `insentif-menu.ts`, `insentif-menu.test.ts`, `insentif-portal-keys.test.ts`, locale.
- **Isi**: item menu dihapus dari array seperti #1022; halaman `/finance/incentive/my-incentive` dibiarkan dormant; `proxy.ts` tak berubah.
- **Verifikasi**: `pnpm tsc`, `pnpm lint` berkas yang diubah, `pnpm test` dibanding baseline, `pnpm build`; sidebar Portal Saya tanpa item Insentif Saya; tautan langsung masih membuka halaman.
- **Dependensi**: M3 terpasang luas, jangan mengulang kejadian #1022 yang mencabut menu enam hari sebelum aplikasinya rilis.

### M5. Sinkron dok
- Perbarui [[APP - MyBharata]] (bagian Insentif di Slip Gaji ke ✅), [[APP - Web ERP]] §Incentive, [[Finance - Incentive]] §Siapa yang boleh melihat, [[API - Insentive Service]], [[ADR - 0081 Insentif Saya Pindah ke MyBharata di Dalam Slip Gaji]] (status), regenerasi indeks, push `main` vault.
- **Dependensi**: M1 sampai M4.

## Pengukuran yang membuktikan selesai

Setelah M3 terpasang luas: jumlah pemegang baris insentif profit yang membuka rincian Insentif dari aplikasi dalam satu periode bukan nol (diukur dari log gateway `/profit-dashboard/saya` per `employee_id`, dibedakan `User-Agent` aplikasi), dan pertanyaan "kenapa insentif saya segini" ke Finance berkurang menurut Finance. Angka pembanding hari ini: 37 orang punya baris, jalur satu-satunya web.

## Di luar lingkup, dengan alasan

- **Notifikasi periode final atau gugur**: kategori inbox baru menuntut dua container naik bersama dan deep link inbox aplikasi belum hidup; keputusan produk tersendiri.
- **Insentif Host Live, affiliate, CRM**: skema tanpa sumber angka di sistem; kartu yang selalu kosong lebih menyesatkan daripada tak ada.
- **Penyandingan insentif dengan komponen Bonus payroll**: payroll tidak membaca insentive-service; salinan fakta yang belum diputuskan pemiliknya.
- **PIN pada tiap kartu**: perilaku sesi PIN dibiarkan seperti slip gaji; bila diminta, satu perubahan di `PinSession`.

## Gap dok yang dibetulkan bersama ADR ini

- `APP - MyBharata` masih menyebut rombakan Slip Gaji ber-PIN "belum merged", padahal my-bharata #134 merged ke `dev` 2026-09-01; `main` rilis masih 1.14.5+135.
- `/profit-dashboard/saya` belum tercatat di `API - Insentive Service`.
