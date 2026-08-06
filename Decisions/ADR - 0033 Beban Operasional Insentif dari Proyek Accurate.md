# ADR - 0033 Beban Operasional Insentif dari Proyek Accurate

**Status**: ✅ **Accepted** — 2026-08-02. Terkait: [[ADR - 0001 Akuntansi via Accurate]], [[ADR - 0002 Database-per-Service]].

## Context

Rumus insentif profit-based (lihat [[Finance - Incentive]]) memakai **Biaya Operasional** sebagai pengurang terakhir:

```
Profit = Uang Cair − HPP − Beban Iklan − Biaya Operasional
```

Sampai Agustus 2026 angka itu **diketik manual** per entitas, dan selama kosong seluruh baris menolak dinyatakan siap dibayar. Tim finance kemudian membuat **74 proyek di Accurate** — 62 berkode **employee id** (`BIP-0166-06-25` = Burhanuddin Yusuf Fanani) dan 12 proyek merek/umum (BIP-BH, BIP-KY+GB, 001 Umum, dst) — sebagai tempat membukukan beban operasional **di luar gaji**.

Kode proyeknya identik dengan `employee_id` yang dipakai payroll dan baris insentif, jadi penyambungan per orang bisa **eksak tanpa pencocokan nama**.

## Decision

**Biaya operasional insentif dirakit dari dua sumber, dipisah tegas menurut jenisnya:**

| Komponen | Sumber | Catatan |
|---|---|---|
| Beban karyawan | [[Microservices - Payroll Service]] `GET /employer-cost` | bruto + iuran BPJS pemberi kerja, **bukan** gaji bersih |
| Beban non-gaji | [[External - Accurate]] `glaccount/get-balance.do` per **proyek** | akun induk `6000` dikurangi daftar kecualian |

Tiga aturan yang mengikat:

1. **Parameter filternya WAJIB `projectNo`, bukan `projectName`.** Diukur ke Accurate produksi 2026-08-02: `projectName=Aan Budiyanto` dibalas `s=true` dengan saldo **Rp5.045.786.448 — persis total seluruh perusahaan**, alias diabaikan diam-diam. `projectNo` yang ngawur ditolak dengan pesan eksplisit. Ini jebakan yang sama dengan `departmentName` pada `get-pl-account-amount.do`, cuma pindah parameter; dikunci test.

2. **Akun induk `6000` tidak boleh dipakai mentah-mentah.** Ia menjumlahkan anaknya, dan sebagian besar anaknya **sudah dikurangkan di tempat lain** pada rumus ini. Terukur Juli 2026: dari Rp5.045.786.449, sebanyak **Rp4.467.066.110 (88,5%)** dobel. Sisa yang benar-benar baru Rp578.720.339.

3. **Salinan lokal 12 jam** (`incentive_opex_accurate` di `integration_db`) + tombol Segarkan. Satu proyek butuh 15 panggilan (induk + 14 kecualian); tanpa salinan, membuka satu dashboard berarti ratusan panggilan.

### Akun yang dikecualikan

| Akun | Sebab |
|---|---|
| 6101, 6201 (Gaji Sales & Marketing, Gaji Adum) | sudah dihitung dari payroll |
| 6202 (THR, Bonus, Tunjangan Lain) | ranah payroll & bersiklus tahunan — ⚠️ perlu konfirmasi finance |
| 6204, 6205 (Asuransi Kesehatan/Ketenagakerjaan) | diduga iuran BPJS pemberi kerja yang sudah dari payroll — ⚠️ perlu konfirmasi finance |
| 6102 (Bonus & Insentif Marketing) | **melingkar** — insentif menurunkan profit yang menentukan insentif |
| 6107, 6108 (Iklan, Pajak Iklan) | sudah dikurangkan dari GMV Max & GMS |
| 6112–6115, 6121, 6122 (Admin/Afiliasi/Ongkir/Refund/PPh22/Asuransi E-Commerce) | sudah terpotong di dalam uang cair |

Daftar beserta alasan tiap akun ada di `integration/internal/usecase/incentive_opex_accurate.go` dan **ikut dikirim ke layar** lewat `GET /profit/incentive/opex` — keputusan ini perlu bisa diperiksa finance tanpa membaca kode.

## Consequences

**Yang membaik**

- Biaya operasional punya sumber otomatis dan **dapat direkonsiliasi**: `Bersih = Induk − Dikecualikan`, dua-duanya disimpan dan ditampilkan, jadi selisih terhadap pembukuan selalu bisa dijelaskan.
- Konsisten dengan [[ADR - 0001 Akuntansi via Accurate]] — Accurate tetap sumber kebenaran pembukuan; ERP hanya membaca.
- Pemisahan gaji/non-gaji membuat kegagalan salah satu sumber tak menjatuhkan yang lain, dan pesan peringatannya menunjuk ke tempat yang benar (Payroll vs Accurate).

**Yang harus diterima**

- **Datanya belum ada.** Per 2026-08-02 baru **6 dari 62** proyek karyawan yang punya beban sepanjang 2026; uangnya masih dibukukan di proyek merek (BIP-BH Rp29,98 M, BIP-KY+GB Rp12,73 M, 001 Umum Rp3,74 M). Dashboard akan tampak sebagian besar kosong — itu keadaan data, bukan bug, dan Panel Kelengkapan di [[APP - Web ERP]] memang dibuat untuk menunjukkannya.
- **Beban proyek merek belum dibebankan ke siapa pun.** Kalau nanti diputuskan ikut, perlu aturan pembagian — `AlokasiProRata` (metode sisa-terbesar, hasil bagi dijamin kembali sama persis dengan totalnya) sudah tersedia di service insentif.
- **Tiga akun dikecualikan secara konservatif** (6202, 6204, 6205). Bila ternyata bukan bagian payroll, biaya tercatat terlalu kecil → profit dan insentif terbayar lebih besar dari seharusnya. Menunggu konfirmasi finance.
- Menambah ketergantungan runtime insentif → integration → Accurate. Kegagalannya ditangani sebagai peringatan baris, bukan kegagalan dashboard.

## Dokumen Terkait

- [[Finance - Incentive]] · [[Microservices - Insentive Service]] · [[Microservices - Integration Service]] · [[Microservices - Payroll Service]]
- [[External - Accurate]] · [[API - Integration Service]]
