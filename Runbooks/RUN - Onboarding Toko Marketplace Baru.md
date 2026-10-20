> **Status**: 🟡 Draft, 2026-10-20. Disusun dari kode `origin/main` dan dok vault; urutan lengkapnya belum pernah dijalankan ujung ke ujung sebagai satu prosedur.

## Tujuan

Memastikan toko marketplace baru (Shopee, TikTok Shop, Lazada) milik Marketing benar-benar masuk ERP: order tertarik, omzet masuk divisi yang benar, pemegang tokonya bisa melihatnya, dokumen Accurate terkirim, dan laba dihitung dengan HPP.

## Kapan dipakai

- Brand membuka toko baru di marketplace.
- Toko lama pindah kepemilikan ke divisi lain (langkah 2 dan 3 saja).
- Toko tampil "belum dipetakan" di ICC Management, atau omzet toko tak muncul di laporan divisi.

## Prasyarat

| Pihak | Yang dibutuhkan |
|---|---|
| Tim integration | Peran modul `integration` (staff ke atas). Sejak 2026-10-20 menghubungkan toko **baru** hanya bisa dilakukan peran ini; pemegang toko dengan izin `akuntoko.oauth.work` hanya bisa **menyambung ulang** toko yang sudah pernah terhubung ([[Marketing - ICC Account Manager Mapping]]). |
| SPV / leader marketing | Lolos gerbang penugasan toko di ICC Management (SPV Kyura/Beautyhacks, `insentive:adv_leader`, atau IT). |
| Tim integration / finance | Akses Config Accurate dan Mapping SKU di menu Integration. |
| Penjual | Login Seller Center toko itu (untuk layar persetujuan OAuth platform). |

## Langkah

Urutan wajib: **1 → (2, 3) → (4, 5)**. Langkah 4 dan 5 boleh paralel dengan 2 dan 3.

1. **Hubungkan toko (OAuth)**. Oleh tim integration, di menu **Integration → Setting → OAuth**, tab channel-nya, lalu tombol sambungkan. Login dengan akun Seller Center toko itu di layar platform.
   - TikTok Shop: sesudah tersambung, backfill order awal jalan otomatis.
   - Hasil yang diharapkan: toko muncul di daftar akun terhubung dengan status sinkron, dan order mulai masuk.
2. **Klaim kepemilikan toko ke departemen**. Oleh SPV/leader marketing di **ICC Management → tab Kepemilikan Toko**. Toko yang baru tersambung tampil sebagai belum dipetakan, dengan penanda untuk 72 jam pertama. Assign ke departemennya (Beautyhacks / Kyura). Satu toko hanya milik satu departemen. Memindahkan toko yang sudah dimiliki departemen lain butuh konfirmasi pindah, karena omzet dan skor dua supervisor ikut berpindah. Rincian aturan: [[API - Integration Service]] §Kepemilikan Toko per Departemen, keputusan [[ADR - 0045 Identitas Tim Tunggal dan Peta Kepemilikan Marketing]].
3. **Petakan pemegang toko**. Oleh SPV/leader marketing di **ICC Management**: assign toko (dan akun iklannya bila ada) ke Account Specialist / Marketplace Advertiser yang memegangnya. Pemetaan ini yang menentukan "toko milik" bagi analitik, ulasan, KPI/insentif, dan Koneksi Toko. Lihat [[Marketing - ICC Account Manager Mapping]].
4. **Daftarkan toko di Config Accurate**. Oleh tim integration/finance di **Integration → Master Data → Config Accurate**. Tanpa ini, faktur, retur, dan penerimaan toko itu gagal dikirim ke Accurate dengan galat `accurate shop not found, please configure accurate shop setting`.
5. **Lengkapi Mapping SKU**. Oleh tim integration di **Integration → Master Data → Mapping SKU**, untuk produk yang dijual toko itu. SKU tanpa mapping dilaporkan sebagai `unmapped_skus` / `missing_hpp`, dan laba toko tampak lebih besar dari kenyataan karena HPP-nya nol ([[Microservices - Integration Service]]).

## Verifikasi

- **Langkah 2**: toko tidak lagi tampil di daftar belum dipetakan di tab Kepemilikan Toko.
- **Langkah 3**: buka **Lihat sebagai** pemegang toko (khusus IT). Toko itu tampil di Profit per Toko dan di Koneksi Toko miliknya.
- **Langkah 4**: di **Integrasi Accurate → Auto-Sync**, faktur hari kirim pertama toko itu berstatus terkirim, bukan gagal.
- **Langkah 5**: daftar SKU tanpa mapping untuk toko itu kosong di layar Gross Profit / laporan profit.

## Bila gagal / Rollback

- **Toko Lazada tidak pernah muncul di daftar belum dipetakan.** Laporan itu baru mencakup Shopee dan TikTok, jadi toko Lazada wajib diklaim manual. Kalau tidak, omzetnya hilang dari laporan divisi tanpa peringatan.
- **Toko TikTok baru di akun seller yang sudah terhubung** disambungkan dengan login seller yang sama, sehingga sistem memperlakukannya sebagai sambung ulang. Ada bug laten di jalur ini: toko-toko di akun itu bisa tercatat menunjuk kredensial yang tak ada, dan backfill awal gagal. Sesudah menyambungkan, minta tim IT memeriksa bahwa toko di akun itu masih menunjuk kredensial yang ada.
- **Salah klaim departemen**: klaim ulang dengan opsi pindah. Melepas kepemilikan sepenuhnya hanya bisa dilakukan admin integration.
- **Salah pemetaan pemegang**: ubah assign di ICC Management. Pemegang yang lama dan yang baru perlu login ulang supaya cakupan tokonya ikut berubah.

## Dokumen Terkait

- [[API - Integration Service]]
- [[Microservices - Integration Service]]
- [[Microservices - Marketing Analytics Service]]
- [[Marketing - ICC Account Manager Mapping]]
- [[ADR - 0045 Identitas Tim Tunggal dan Peta Kepemilikan Marketing]]
- [[ADR - 0149 Sidebar Satu Daftar Urusan, Menu Digerbang Izin Posisi, Beranda Ruang Kerja Posisi]]
- [[APP - Web ERP]]
