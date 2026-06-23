## Deskripsi

*Konsep (sisi General Affairs) **peminjaman aset** — mengelola alur **pinjam → pakai → kembali** untuk: booking **ruang meeting**, pinjam **barang/aset bergerak**, dan booking **kendaraan operasional**. Tujuannya agar pemakaian bersama terjadwal (tak bentrok), terlacak (siapa pinjam apa, kapan), dan akuntabel (kondisi aset saat dikembalikan). Master data asetnya ada di [[GA - Inventory Management]]; dok ini menambahkan alur peminjamannya.*

- **Status**: 🟡 Konsep / Direncanakan (belum ada implementasi)

## Latar Belakang

- Peminjaman ruang, barang, dan kendaraan saat ini berjalan manual/ad-hoc → rawan **bentrok jadwal**, sulit tahu **siapa memakai apa**, dan kondisi aset saat kembali tidak tercatat.
- [[GA - Inventory Management]] menyimpan **master aset**, tetapi belum ada **alur pinjam-kembali** terstruktur. Konsep ini melengkapi sisi itu.

## Ruang Lingkup / Cakupan (business view)

- **Booking ruang meeting** — jadwal pemakaian (anti-bentrok), kapasitas/fasilitas, durasi.
- **Pinjam barang/aset bergerak** — mis. proyektor, alat ukur, perkakas; dengan **tanggal kembali** + catatan **kondisi** saat pinjam & kembali.
- **Booking kendaraan operasional** — tujuan, jadwal, peminjam. *(Pemeliharaan/servis kendaraan **di luar lingkup** → [[GA - Machine & Utility Maintenance]].)*
- **Alur umum**: ajuan/booking → (approval bila perlu) → pakai → **kembali + cek kondisi** → catat; bila aset rusak/hilang → **eskalasi** ke maintenance ([[GA - Machine & Utility Maintenance]] / [[GA - Building Maintenance]]).
- **Ketersediaan & riwayat**: kalender ketersediaan per aset; riwayat peminjaman per aset & per peminjam.

## Konsumen Data

- [[GA - Inventory Management]] — status aset (tersedia / sedang dipinjam) & data master aset yang dapat dipinjam
- [[GA - Machine & Utility Maintenance]] · [[GA - Building Maintenance]] — menerima eskalasi bila aset rusak saat dikembalikan
- [[APP - Mobile Application]] — entry-point pengguna (menu **Meeting Room** & **Vehicle**, saat ini masih *Coming Soon*)

## Kendala

- Master aset masih 🟡 (lihat [[GA - Inventory Management]]) — peminjaman butuh daftar aset yang rapi sebagai fondasi.
- Penjadwalan anti-bentrok (ruang & kendaraan) perlu mekanisme kalender.

## Belum Diputuskan (TBD)

- Aset apa saja yang boleh dipinjam (kategori/daftar)?
- **Self-service** (pinjam langsung) vs perlu **approval** (atasan/GA)? Untuk aset/kendaraan tertentu mungkin beda.
- Durasi maksimum peminjaman + sanksi/penanganan bila telat kembali?
- Kendaraan: dengan **sopir** atau boleh dikemudikan sendiri? Perlu data BBM/odometer?
- Integrasi kalender (mis. Google Calendar) atau internal saja?
- Pemilik proses & approver (GA sepenuhnya, atau melibatkan sekretariat/atasan)?
- Catatan: menu **"Loan"** di [[APP - Mobile Application]] **bukan** peminjaman aset di dok ini (kemungkinan **pinjaman karyawan/kasbon** — sisi HR; perlu konfirmasi).

## Dokumen Terkait

- [[GA - Inventory Management]] — master aset (fondasi peminjaman)
- [[GA - Machine & Utility Maintenance]] · [[GA - Building Maintenance]] — eskalasi kerusakan
- [[APP - Mobile Application]] — entry-point (Meeting Room / Vehicle)
- [[GA - Big Pictures]]
