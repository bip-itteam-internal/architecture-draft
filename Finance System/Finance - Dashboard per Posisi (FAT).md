**Status**: 🟢 **Implementasi (FE)** — dashboard keuangan per posisi (FAT) di `erp-frontend`, sebagian besar elemen masih menunggu penyambungan data backend.

## Deskripsi

Menu **Finance** menyediakan **dashboard per posisi** (Finance/Accounting/Tax — "FAT") supaya tiap peran bisa mengambil keputusan **hanya dengan melihat layar**: kartu deviasi + grafik ringkas, bukan tabel mentah. Satu perender data-driven merender dua belas halaman dari deskripsinya, sehingga perbaikan tata letak dikerjakan sekali.

Kode: `erp-frontend/src/features/finance/posisi/`
- `components/halaman-posisi.tsx` — perender generik (kartu/bagan/tabel/peringatan) dari `data/<posisi>.ts`.
- `components/isi-<posisi>.tsx` — isi tiap posisi; yang hook-nya sudah tersambung merender kartu/grafik **nyata** lewat slot `atas`, judulnya didaftarkan ke `elemenDilewati` agar tak dobel dengan panel "menunggu penyambungan".
- `components/bagan/` — pustaka grafik lokal: `BaganBatang`, `BaganBatangHorizontal`, `BaganGaris`, `BaganPersen`, `BaganDonat` (donat komposisi, SVG + legenda). Warna dari token tema `WARNA_SERI` (`var(--fat-*)`), bukan heksa.
- Rute: `app/(main)/finance/posisi/<posisi>/page.tsx` (guard izin di pemanggil). Posisi: `spv`, `ar-staf`, `ar-leader`, `junior-accounting`, `senior-accounting`, `cost-control`, `tax`, `ap`, `cv`.

Hak akses per posisi mengikuti model RBAC yang hak-nya menempel di posisi — lihat [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]].

## Prinsip data (penting)

- **Tidak ada angka palsu.** Elemen yang hook-nya belum dipanggil dirender sebagai panel **"menunggu penyambungan data"** dengan nama hook-nya terlihat — bukan angka nol yang terbaca "tidak ada transaksi". Tiap helper grafik mengembalikan keadaan **kosong** saat datanya `undefined`.
- **Pass/fail hanya untuk target yang sudah tertulis di kode.** Indikator target‑vs‑aktual dipasang di ambang yang memang ada (AR Staf: piutang >14 hari & retur >14 hari, "maks 5%"). Ambang yang masih parameter manusia tanpa master (mis. SPV "beban non‑operasional ≤2%") **sengaja tidak** dijadikan lampu lulus/gagal.
- Sumber angka lintas modul; akuntansi via [[External - Accurate]] (laba rugi, saldo, varians anggaran).

## Grafik & indikator yang sudah hidup

Per pembaruan **2026-08-07** (FE), grafik hidup dari data yang hook‑nya sudah dimuat:

| Posisi | Elemen hidup | Sumber |
|---|---|---|
| Ringkasan Divisi | Aging piutang & Aging utang (donat komposisi); OPEX anggaran vs realisasi (batang) | `useFetchPiutangSummary`, `useAgingUtang`, `useFetchVariansEnamBulan` |
| SPV | Tren AR >60 hari (garis); Beban per kelompok (persen); **Aging piutang** (donat); kotak persetujuan | agregator persetujuan, laba rugi & piutang Accurate |
| AR Staf | Status penyelesaian retur (batang); Belum dicocokkan per kanal (persen); indikator target **Piutang >14 hari** & **Retur >14 hari** (maks 5%) | `useFetchReturnStats`, `useFetchMissingAgregat` |
| AR Leader | Uang tertagih per minggu (batang); **Komposisi piutang per umur** (persen) | `useFetchReceiptMingguan`, `useFetchPiutangSummary` |
| Cost Control | Varians per pos biaya (batang‑horizontal); **Anggaran vs Realisasi per pos** (batang 2 seri) | `useFetchVariansAnggaran` |
| Junior Acc | **Transaksi hari ini vs rata‑rata** (batang) | `useFetchJurnal` |
| AP | Aging utang (batang) | `useAgingUtang` |
| Accounting CV | Penjualan per toko (bilah, 8 teratas) | `useFetchPenjualanToko` |
| Senior Acc | Komposisi aset tetap (donat: nilai buku vs penyusutan) | `useFetchAsetTetap` |
| Tax | Beban per kelompok (donat) | `useFetchLabaRugi` |

Komponen indikator: `components/kartu-indikator-target.tsx` (pil hijau/amber/merah + bar target), status dihitung `lib/status-ambang.ts` (`statusAmbang({nilai,target,arah})` → `sehat|waspada|kritis`). Transform data grafik ada di `lib/bagan-*.ts` (murni, ber‑unit test).

## TBD (menunggu backend)

Masih panel jujur "menunggu penyambungan": AR Leader "hasil penagihan per cara hubung", Junior "koreksi per jenis transaksi", Senior "umur selisih rekonsiliasi", Cost Control "forecast kas" & "penghematan terealisasi", Tax "biaya non‑deductible per penyebab". Butuh endpoint/agregat backend baru sebelum bisa dijadikan grafik.

## Dokumen Terkait

- [[Finance - Big Pictures]] — peta domain Finance System
- [[Finance - Incentive]] — dashboard insentif (menu Finance terkait)
- [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] — model hak akses per posisi
- [[External - Accurate]] — sumber angka akuntansi (laba rugi, varians anggaran)
