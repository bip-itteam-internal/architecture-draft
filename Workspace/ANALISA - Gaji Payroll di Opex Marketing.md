**Status**: 🟡 Papan kerja 2026-09-29, disusun dari investigasi keluhan user Finance. Aturan beban gaji insentif ada di [[ADR - 0033 Beban Operasional Insentif dari Proyek Accurate]]; dok ini **bukan** keputusan baru, melainkan temuan + pertanyaan terbuka + dua task yang siap diambil developer lain. **T1 dan T2 ditahan sampai Finance menjawab P1.** Coret item begitu PR-nya merge, pindahkan keadaannya ke dok domain lewat `/sync-docs`.

> ⛔ Repo vault ini **publik**. Jangan menambahkan nama karyawan, employee_id, atau nominal gaji per orang ke dok ini. Rincian per orang diserahkan ke PIC HRD/Finance lewat kanal internal.

## Masalah

User Finance membuka `/finance/anggaran?tab=marketing` dan membaca baris **"Gaji (Payroll)"** per orang sebagai gaji di slip. Angka di layar selalu lebih besar dari slip (±7% di atas bruto untuk karyawan dengan dasar upah BPJS setara gaji), sehingga datanya dikira salah. Angkanya **benar untuk tempat asalnya**, tapi disajikan di tempat dan dengan label yang menyesatkan.

## Temuan (grounded, diperiksa 2026-09-28/29)

### Dari mana angka itu

- Tab Marketing merender `PanelOpexManual` → `KartuGajiIcc` dan `BreakdownPerUser` (erp-frontend `src/features/finance/opex-manual/components/`). Keduanya memanggil `useProfitDashboard(periode, "icc")` = `GET /api/insentive/profit-dashboard`, field `biaya_gaji`.
- `biaya_gaji` dirakit insentive-service (`services/insentive/func.go`, struct baris sekitar baris 1156) dari payroll `GET /employer-cost` (`services/payroll/employee_salary_handlers.go`, `BiayaPemberiKerja` di `payroll_calc.go`) = **bruto + iuran BPJS pemberi kerja**. Payroll sudah mengirim `bruto` dan `iuran_bpjs_perusahaan` terpisah; insentive-service meleburnya jadi satu angka.
- **Tidak ada yang disimpan.** Angka dihitung ulang tiap halaman dibuka dari master gaji (`payroll_db.employee_salary`) + kehadiran periode itu. Koleksi input manual `incentive_opex` dan `incentive_snapshots` di prod kosong (diukur 2026-09-28). Mengubah master gaji mengubah angka bulan lalu di layar.
- Periode kehadiran `YYYY-MM` di `/employer-cost` = tanggal 26 bulan sebelumnya s.d. 25 bulan itu (attendance `/payroll-supplement`), **sama** dengan periode run payroll bulan yang sama. Tidak ada pergeseran periode.
- Iuran BPJS perusahaan = Σ program yang diikuti (`employee_salary.bpjs_enrollment`) × dasar upah (`upah_bpjs_kesehatan` / `upah_bpjs_ketenagakerjaan`, dipotong `salary_cap`) × `company_rate` di `payroll_config.bpjs` (Kesehatan 4%, JHT 3,7%, JP 2%, JKK 0,24%, JKM 0,3% per 2026-09-28). Fungsi: `bpjsCompanyTotal` (`payroll_calc.go`). **Hitungan, bukan realisasi setoran.**
- Baris gaji **tidak ikut dijumlah** ke Total Realisasi / Varians Opex Marketing (sengaja, lihat docstring `kartu-gaji-icc.tsx`), jadi angka anggaran tidak tercemar. Yang rusak adalah pemahaman pembacanya.
- Penjelasan "Gaji bruto + BPJS pemberi kerja" hanya ada sebagai atribut `title` (`finance.opexManual.breakdownPerUserGajiHint`), tak terlihat tanpa hover dan tak muncul di HP.

### Siapa dan kapan

| Apa | Siapa | Kapan | Jejak |
|---|---|---|---|
| Beban gaji insentif = bruto + BPJS pemberi kerja (`/employer-cost`) | Fahrur | 2026-08-02 | bip-erp commit `394e6109`, masuk lewat PR [#906](https://github.com/bip-itteam-internal/bip-erp/pull/906) (branch `fix/returAnomaly`, nama branch tak menggambarkan isinya); ADR 0033 ditulis hari yang sama |
| Angka itu dipakai ulang di tab Opex Marketing dengan label "Gaji (Payroll)" | bagusizzan | 2026-08-21 | erp-frontend commit `593684c9f` (Breakdown per PIC) dan `e7e14a767` (kartu Beban Gaji ICC), "tanpa perubahan backend, endpoint yang sudah ada" |

Kode menyebut alasannya "keputusan client 2026-08-02" (`payroll_calc.go`), tanpa nama pemutus. ADR 0033 juga tidak mencatatnya.

### Kenapa angkanya tak bisa dicocokkan ke Accurate

- Halaman Anggaran membandingkan dengan Accurate, dan daftar akun opex-nya memuat 6101 *Beban Gaji Sales & Marketing* (`services/integration/internal/usecase/opex_daftar.go`). 6101 berisi gaji **tanpa** BPJS perusahaan.
- BPJS perusahaan di Accurate dibukukan ke **6204 / 6205, departemen UMUM**, tidak dibagi ke divisi marketing. Kedua akun itu dikecualikan dari opex insentif karena diduga sama dengan iuran dari payroll (ADR 0033, masih "perlu konfirmasi finance").
- Akibatnya satu halaman memuat dua "gaji marketing" dengan dasar berbeda. Ini kelas "reuse yang salah lebih mahal daripada duplikasi" di ingatan tim.

### Temuan sampingan (data, bukan kode)

- Sebagian kecil karyawan marketing punya master gaji ERP yang berbeda dari sheet gaji HRD (komponen tunjangan kosong, salah isi, atau belum punya master). Karena opex insentif membaca master, datanya ikut meleset. Daftar per orang sudah diserahkan ke PIC HRD di luar vault.
- Tunjangan Makan: master memuat nilai penuh, sheet HRD memuat nilai setelah hari tidak hadir. `/employer-cost` memakai nilai master di bruto, potongan uang makan tercatat sebagai potongan, sehingga beban opex sedikit di atas realisasi (puluhan ribu per orang).

## Pertanyaan terbuka (dijawab Finance / pemilik produk sebelum T1/T2)

- **P1.** Apakah gaji perlu tampil di tab Opex Marketing sama sekali? Pilihan: (a) tampil dipecah jadi gaji bruto + BPJS perusahaan + total "Beban gaji perusahaan" (rekomendasi, dipilih user 2026-09-28, menunggu konfirmasi Finance); (b) bruto saja, sebanding 6101; (c) dihapus dari tab ini, tetap di dashboard insentif. Jawaban (b) atau (c) mengubah isi T2 dan mungkin menghapus T1.
- **P2.** Konfirmasi isi akun 6204/6205: benar iuran BPJS pemberi kerja? Bila tidak, beban itu hilang dari opex insentif (ADR 0033).
- **P3.** Siapa "client" yang memutuskan 2026-08-02? Tanya Fahrur, lalu catat di ADR 0033.
- **P4.** Uang makan di beban opex: pakai nilai master (sekarang) atau nilai setelah kehadiran? Bila berubah, itu perubahan rumus `/employer-cost`, perlu ADR, dan di luar T1/T2.

## Urutan deploy

T1 (bip-erp, insentive-service) naik lebih dulu, baru T2 (erp-frontend). T2 wajib aman bila field baru belum ada. Tak ada env baru. Prod dijalankan manusia (skill `deploy-bip-erp` §0).

## Kontrak T1 ↔ T2

```
GET /profit-dashboard?periode=YYYY-MM&level=<icc|leader|spv|...>   (insentive-service; FE: /api/insentive/profit-dashboard)
Respons TIDAK berubah kecuali tiap objek di data.rows[] boleh membawa DUA field baru:

  "biaya_gaji_bruto":           number   // bagian bruto dari biaya_gaji (payroll slip.Gross)
  "biaya_gaji_bpjs_perusahaan": number   // bagian iuran BPJS pemberi kerja dari biaya_gaji

Aturan:
- Keduanya HADIR BERSAMA atau ABSEN BERSAMA (omitempty via pointer; tak pernah 0 sebagai pengganti "tak diketahui").
- Hadir hanya bila SELURUH beban gaji baris itu bersumber payroll (sumber_gaji == "payroll", termasuk seluruh anggota rollup).
- Bila hadir: biaya_gaji_bruto + biaya_gaji_bpjs_perusahaan == biaya_gaji (toleransi pembulatan sen < 1 rupiah).
- Field lama (biaya_gaji, sumber_gaji, biaya_operasi, dst.) tidak berubah nama, tipe, maupun nilai.
```

## Task

### T1. Baris profit-dashboard membawa pecahan gaji bruto dan BPJS perusahaan
- **Status**: ⏸ ditahan, menunggu P1.
- **Repo**: bip-erp, `services/insentive/func.go` (struct baris ~1156, pengisian `BiayaGaji` ~1915, rollup anggota ~1886, `ambilBiayaKaryawan` ~2311), `services/insentive/business_rules.go` (`SusunBiayaOperasi`, `BiayaOperasiBaris`).
- **Isi**: teruskan `bruto` dan `iuran_bpjs_perusahaan` yang sudah dibalas payroll sampai ke baris dashboard sesuai Kontrak. `biaya_gaji`, `biaya_operasi`, dan rumus profit **tidak berubah**. Sumber gaji manual (`IncentiveOpex.Gaji`) tak punya pecahan: key absen, jangan mengarang.
- **Kriteria lolos**:
  - Test Go: baris bersumber payroll membawa kedua field dan jumlahnya sama persis dengan `biaya_gaji`; fixture bruto ≠ iuran.
  - Test Go: baris bersumber manual atau tanpa gaji tidak membawa kedua key (absen, bukan 0).
  - Test Go: rollup Leader/SPV menjumlah pecahan anggota, dan absen bila satu saja anggota manual/tanpa gaji.
  - Test lama `biaya_gaji` / `SusunBiayaOperasi` / profit hijau tanpa diubah ekspektasinya.
  - Satu `GET` lewat gateway dev: bentuk respons memuat kedua field pada baris `sumber_gaji: "payroll"`.
- **Batas**: jangan ubah `/employer-cost`, gerbang menu `/profit-dashboard`, maupun snapshot insentif (sengaja tanpa rincian gaji, `shared-library/models/insentive/models.go`).
- **Verifikasi**: `go test ./services/insentive/...` dan `go build` lewat antrean (`antre.ps1`).

### T2. Tab Opex Marketing menampilkan gaji bruto, BPJS perusahaan, dan beban gaji perusahaan
- **Status**: ⏸ ditahan, menunggu P1 (isi di bawah untuk jawaban (a)).
- **Repo**: erp-frontend, `src/features/finance/opex-manual/components/breakdown-per-user.tsx`, `kartu-gaji-icc.tsx`, `lib/breakdown-per-user.ts`, `lib/gaji-icc.ts`, tipe `src/features/finance/incentive/profit/types.ts`, `src/i18n/locales/{id,en}.ts`.
- **Isi**: per orang tampil Gaji bruto (sebanding 6101 Accurate), BPJS perusahaan (Accurate: 6204/6205 UMUM), dan total berlabel "Beban gaji perusahaan"; keterangan terlihat sebagai teks, bukan `title`. Baris tanpa pecahan menampilkan total saja. Kartu agregat menampilkan pecahan hanya bila semua baris terisi membawanya. Gaji tetap **tidak** ikut total Opex Marketing; gerbang `systemRoles.finance` tetap.
- **Kriteria lolos**:
  - Test komponen: tiga nilai tampil bila field ada; hanya total bila absen, tanpa 0 karangan.
  - Test kartu: total tetap = Σ `biaya_gaji` baris terisi.
  - Kunci i18n baru di `id.ts` dan `en.ts`; label lama "Gaji (Payroll)" tak lagi jadi label satu-satunya.
  - Orang: user Finance membuka rincian satu ICC dan bisa mencocokkan gaji bruto ke slip atau 6101 tanpa bertanya.
- **Batas**: jangan menambah prop ke komponen shared; jangan menghitung pecahan di FE; layar insentif lain yang memakai `biaya_gaji` (`editor-opex.tsx`, `rincian-realisasi.tsx`) di luar lingkup.
- **Verifikasi**: `pnpm tsc --noEmit`, `pnpm lint`, `pnpm test` (dibanding baseline yang terpasang), `pnpm build` lewat antrean.
- **Dependensi**: kontrak di atas; deploy setelah T1.

## Dokumen terkait

- [[ADR - 0033 Beban Operasional Insentif dari Proyek Accurate]] · [[Finance - Incentive]] · [[Microservices - Insentive Service]] · [[Microservices - Payroll Service]]
