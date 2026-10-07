# ADR - 0154 KONSUMSI Dibelikan Procurement seperti Raw Material, Bukan Permintaan Uang

> **Status**: 🟢 **Diterima**, 2026-10-05, oleh pengguna Tech Development dalam sesi kerja. **Diperbarui 2026-10-06**: rancangan lengkapnya kini hidup di spec pembelian (lihat Deskripsi). ADR ini sengaja dipangkas jadi **penunjuk** plus satu keputusan yang tidak tertulis di spec (§2), supaya alur pembelian tidak punya dua sumber kebenaran.

%% Vault ini PUBLIK. Nama orang dan employee_id tidak ditulis; yang disebut hanya angka agregat, departemen, dan posisi. %%

## Untuk Manajemen

**Yang diputuskan.** Konsumsi (pantry, jamuan, konsumsi rapat) diperlakukan sebagai **pembelian barang** seperti Raw Material, bukan permintaan uang seperti Dana: pengaju HRGA menyebut barang dan jumlahnya, Procurement mengisi harga dan pemasok, Finance dan Direktur menyetujui atas harga itu, lalu Gudang GA memeriksa dan menerima barangnya ke stok konsumsi GA. Tetap hanya HRGA yang mengajukan, tetap dibayar PT Bharata.

**Satu pengecualian dari rancangan.** Bila pengajunya supervisor HRGA sendiri, tahap atasan **dilewati** (bukan "selalu ada"), karena di produksi hanya satu orang yang menaungi HRGA dan ia tak boleh menyetujui pengajuannya sendiri.

## Deskripsi

*Penunjuk ke rancangan pembelian Barang Umum, Raw Material, dan Konsumsi. Menggantikan bagian "rantai identik DANA" di [[ADR - 0090 KONSUMSI Eskalasi ke Direktur di Ambang Berbagi, Bukan Kebal]]; ambang Direktur berbagi (Rp 5 juta, inklusif) dari ADR itu tetap, kini dihitung dari harga Procurement.*

- **Tanggal**: 2026-10-05, diperbarui 2026-10-06
- **Sumber kebenaran rancangan**: spec `docs/superpowers/specs/2026-10-05-pembelian-umum-rm-konsumsi-design.md` di repo kode bip-erp (PR `bip-erp#2617`, versi termin `bip-erp#2633`), beserta mockup HTML di folder yang sama. Pembagian kerja: induk `bip-erp#2616` (19 sub-issue). Issue tipe: `bip-erp#2595` (Raw Material), `#2596` (Barang Umum), `#2597` (Konsumsi).
- **Yang TIDAK lagi diatur di sini**: jenjang per metode bayar, termin uang muka, barang tiba, QC dan penerimaan per kedatangan, faktur, pelunasan, kelebihan bayar, izin dan paket gudang. Semuanya di spec. Isi versi 2026-10-05 ADR ini yang mengatur hal-hal itu (§1, §3 sampai §7 lama) **dicabut**; bila bertentangan dengan spec, spec yang menang.
- **Hubungan dengan dok lain**:
  - [[ADR - 0090 KONSUMSI Eskalasi ke Direktur di Ambang Berbagi, Bukan Kebal]]: §1 dan §4 digantikan; §2 (ambang berbagi) tetap.
  - [[ADR - 0055 Pengajuan Pembelian Empat Tipe Menggantikan Pengajuan Budget]] · [[ADR - 0057 Penyetuju Pengajuan Pembelian Ditetapkan per Tahap]]

## Context

**Data PROD 2026-10-05 (baca-saja).**

- Koleksi `pengajuan_barang`: **0 dokumen KONSUMSI** (juga 0 UMUM dan 0 RAWMATERIAL; yang ada DANA 87, IKLAN 18). Tak ada dokumen Konsumsi berjalan yang terdampak perpindahan alur.
- Master departemen: `General Affair` ber-`supervised_by` `Human Resource`; `Human Resource` tak punya induk. Hanya **satu** karyawan ber-`is_supervisor` di kedua departemen itu (posisi HRD Supervisor), sehingga ia satu-satunya yang menaungi HRGA lewat klaim `supervised_departments`.

**Mekanisme yang relevan (kode `origin/main` bip-erp 2026-10-05).** Tahap `pb_spv_divisi` ditentukan **hubungan organisasi**, bukan izin (`tahapBerbasisHubungan`), dan masuk `tahapKeputusanPengaju` sehingga pengaju dilarang menindaknya sendiri. `JenjangUntukTipeBarang` menyisipkannya hanya bila pengaju **tidak** menaungi departemennya.

## Decision

### §2. Atasan Konsumsi dilewati bila pengajunya supervisor HRGA

Rancangan awal (spec "Hal terbuka 1", dan butir "atasan Konsumsi selalu" di sub-issue BE-3 `bip-erp#2620`) meminta `pb_spv_divisi` **selalu** disisipkan untuk Konsumsi, seperti `pb_spv_manufactur` untuk Raw Material. **Ditolak** untuk Konsumsi: dengan satu-satunya penaung HRGA sebagai pengaju, tahap itu tak punya penyetuju sah, dan dokumennya mandek permanen dengan pesan "tidak berwenang menindak tahap ini".

Aturannya tetap seperti hari ini: `pb_spv_divisi` disisipkan **hanya bila pengaju bukan supervisor** departemennya. Pengawasan atas pengajuan supervisor HRGA tetap ada di tahap sesudahnya: Procurement (harga), Cost Control, SPV Finance, dan Direktur bila ≥ ambang.

Alternatif yang ditimbang dan tidak dipilih: Direktur menggantikan tahap atasan (menambah persetujuan Direktur berapa pun nominalnya); pemegang paket Budget: Kepala Divisi (perlu penugasan baru yang belum ada pemiliknya).

## Consequences

- Pengajuan Konsumsi oleh supervisor HRGA melewati satu mata persetujuan dibanding pengajuan stafnya. Diterima sadar; mata berikutnya tetap empat lapis.
- Bila kelak ada penaung HRGA kedua (atau HRGA mendapat departemen induk), keputusan ini layak ditinjau ulang: "selalu ada" menjadi mungkin tanpa membuat dokumen mandek.
- Raw Material punya kasus serupa (pengaju yang juga SPV Manufaktur), tetapi diputus terpisah di spec; ADR ini tidak mengaturnya.
