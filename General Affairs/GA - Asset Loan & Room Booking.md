## Deskripsi

*Konsep & **desain** (sisi General Affairs) **peminjaman aset** — mengelola alur **pinjam → pakai → kembali** untuk: booking **ruang meeting**, pinjam **barang/aset bergerak**, dan booking **kendaraan operasional**. Tujuannya agar pemakaian bersama terjadwal (tak bentrok), terlacak (siapa pinjam apa, kapan), dan akuntabel (kondisi/kebersihan saat dikembalikan). Master data asetnya ada di [[GA - Inventory Management]]; dok ini menambahkan alur peminjamannya.*

- **Status**: 🟡 Konsep / Direncanakan — **desain rilis-1 (Booking Ruang) sudah terkunci**, belum ada implementasi kode.
- **Rumah kode (rencana)**: extend service inventory ([[Microservices - Inventory Service]]) — booking = tambahan alur di atas master aset GA. Endpoint detail → [[API - Inventory Service]] (saat sudah dikode).
- **Sumber bisnis**: 2 sheet *"Form Peminjaman Ruangan"* + *"Syarat Dan Ketentuan Peminjaman Ruangan"* (PT Bharata Internasional Pharmaceutical).

## Latar Belakang

- Peminjaman ruang, barang, dan kendaraan saat ini berjalan manual/ad-hoc lewat spreadsheet → rawan **bentrok jadwal**, sulit tahu **siapa memakai apa**, dan kondisi/kebersihan saat kembali tidak tercatat. Spreadsheet **tidak punya kolom status** dan pengecekan bentrok dilakukan manual (rawan human error).
- Pada proses lama, **hanya Team GA yang mengisi form** (GA sebagai gatekeeper). Desain baru menggeser ini ke **self-service + approval GA** (lihat [Keputusan Desain](#keputusan-desain-rilis-1)) — mengurangi beban input GA sekaligus tetap memberi GA kontrol.
- [[GA - Inventory Management]] menyimpan **master aset**, tetapi belum ada **alur pinjam-kembali** terstruktur. Konsep ini melengkapi sisi itu.

## Ruang Lingkup / Cakupan (business view)

- **Booking ruang meeting** — jadwal pemakaian (anti-bentrok), kapasitas/fasilitas, durasi. → **fokus rilis-1**.
- **Pinjam barang/aset bergerak** — mis. proyektor, alat ukur, perkakas; dengan **tanggal kembali** + catatan **kondisi** saat pinjam & kembali. → **fase berikutnya** (memanfaatkan master aset yang sudah ada di [[Microservices - Inventory Service]]).
- **Booking kendaraan operasional** — tujuan, jadwal, peminjam. → **fase berikutnya**. *(Pemeliharaan/servis kendaraan **di luar lingkup** → [[GA - Machine & Utility Maintenance]].)*
- **Alur umum**: ajuan/booking → **approval GA** → pakai → **kembali + cek kondisi/kebersihan** → catat; bila aset rusak/hilang → **eskalasi** ke maintenance ([[GA - Machine & Utility Maintenance]] / [[GA - Building Maintenance]]).
- **Ketersediaan & riwayat**: kalender ketersediaan per ruang/aset; riwayat peminjaman per aset & per peminjam.

## Persona / Pengguna

| Persona | Peran & Divisi | Akses / RBAC | Device |
|---|---|---|---|
| **Peminjam** | Karyawan lintas divisi (HRD, Kyura, Beautyhacks, IT, dll) | Karyawan terautentikasi (tanpa gate GA) — self-request | [[APP - MyBharata]] (mobile) |
| **Team GA** | GA staff / supervisor | `RequireGeneralAffair` (modul `ga`: staff/supervisor/admin) — approve, tolak, selesai, kelola master ruang | [[APP - Web ERP]] (web) |
| **Penanggung jawab** | Kontak yang no. WA-nya dicatat pada peminjaman (bisa = peminjam) | — (referensi kontak, wajib diisi) | — |

- **Peminjam** — *Tujuan*: memesan ruang tanpa harus menghubungi GA manual. *Pain point*: tidak tahu ruang kosong/bentrok. *Aksi utama*: ajukan booking, pantau status.
- **Team GA** — *Tujuan*: kontrol pemakaian ruang tanpa mengetik semua form. *Pain point*: bentrok jadwal & ruang ditinggal kotor. *Aksi utama*: setujui/tolak, verifikasi checklist saat selesai.

## Keputusan Desain (rilis-1)

Desain ini **menetapkan keputusan** atas beberapa **TBD** konsep awal:

1. **Scope rilis-1 = ruang saja.** Device & kendaraan ditunda ke fase berikutnya.
2. **Self-service + approval GA** (bukan lagi GA-only). Peminjam mengajukan sendiri via [[APP - MyBharata]]; GA menyetujui/menolak & mengelola via [[APP - Web ERP]]. *Ini mengubah proses manual lama (GA-only) — disepakati sebagai perbaikan efisiensi.*
3. **Notifikasi lewat MyBharata**, bukan blast WhatsApp. **Nomor WA tetap wajib diisi** sebagai kontak penanggung jawab, tetapi notifikasi status (diajukan/disetujui/ditolak) dikirim via [[Microservices - Notification Service]] (inbox + push FCM) memakai kategori inbox yang sudah dirender MyBharata (`request-created`, `request-approved`, `request-rejected`).
4. **Rumah kode = [[Microservices - Inventory Service]]** (extend), bukan service baru — booking memakai kembali RBAC GA, identitas header gateway, dan berdampingan dengan master aset.

### Status Booking

`Diajukan → Disetujui | Ditolak → Selesai`, plus `Dibatalkan`.

- **Diajukan** — dibuat peminjam.
- **Disetujui / Ditolak** — aksi GA (tolak menyertakan alasan).
- **Selesai** — aksi GA saat pemakaian usai; **mengisi checklist** kelengkapan + kebersihan/kerapihan.
- **Dibatalkan** — oleh peminjam (selagi masih `Diajukan`) atau GA.
- **Berlangsung** — **state turunan** untuk tampilan (Disetujui & waktu-kini dalam rentang booking), **bukan** transisi ber-aksi di rilis-1.

### Aturan Anti-Bentrok

Booking baru **bentrok** bila ada booking lain pada **ruang yang sama** berstatus `Disetujui` dan rentang waktunya **overlap**: `mulaiBaru < selesaiLama && mulaiLama < selesaiBaru`. Banyak pengajuan (`Diajukan`) boleh antre pada slot yang sama; **saat GA menyetujui**, overlap terhadap booking yang sudah `Disetujui` **ditolak**. *(Catatan: inventory-mongo bukan replica set → tanpa multi-document transaction; enforcement pakai re-check saat approve.)*

## Alur Proses (rilis-1)

1. **Ajukan** — peminjam pilih ruang, tanggal & jam mulai/selesai, keperluan, **no. WA** (wajib), keterangan → status `Diajukan`; notifikasi `request-created` ke peminjam.
2. **Review GA** — GA lihat antrean & kalender; **setujui** (cek anti-bentrok) atau **tolak** (alasan) → notifikasi ke peminjam.
3. **Pakai** — peminjam memakai ruang sesuai jam; wajib jaga kebersihan & tidak merusak fasilitas (Syarat & Ketentuan).
4. **Selesai + verifikasi** — GA menandai `Selesai` sambil mengisi **checklist kelengkapan** & **kebersihan/kerapihan**; device (bila ada, fase berikutnya) dikembalikan ke GA.
5. **Eskalasi** — bila ada kerusakan → [[GA - Machine & Utility Maintenance]] / [[GA - Building Maintenance]].

## Rencana Kontrak (belum diimplementasi)

> Ditandai **rencana** — akan menjadi grounded & pindah detailnya ke [[API - Inventory Service]] setelah dikode.

**Master ruang** (`rooms`): `GET /rooms` (semua auth) · `POST/PATCH/DELETE /rooms` (GA). Seed awal: *Ruang Meeting L3*, *Ruang Training L3*.

**Booking** (`room_bookings`):
- `POST /bookings` — self-service (identitas dari header gateway; `pic_phone` wajib).
- `GET /bookings/my` — pengajuan milik peminjam.
- `GET /bookings` · `GET /bookings/:id` · `GET /bookings/calendar` — GA (list/detail/kalender).
- `PATCH /bookings/:id/approve` · `/reject` · `/complete` · `/cancel` — transisi status (guard + anti-bentrok saat approve).

**Data (rencana koleksi):**
- `rooms` — `name`, `location/floor`, `capacity`, `facilities[]`, `is_active`.
- `room_bookings` — `_id` (`RESV-YYYY-nnn`), `room_id`/`room_name`, `requester{employee_id,full_name,department}`, `pic_phone`, `purpose`, `start_at`/`end_at`, `status`, `notes`, `approval{by,at,reason}`, `completion{completeness_ok,cleanliness_ok,notes,by,at}`, `metadata`.

*(Skema final didokumentasikan di [[DB - Data Dictionary]] saat implementasi.)*

## Konsumen Data

- [[GA - Inventory Management]] — status aset (tersedia / sedang dipinjam) & data master aset yang dapat dipinjam (relevan saat fase device).
- [[GA - Machine & Utility Maintenance]] · [[GA - Building Maintenance]] — menerima eskalasi bila aset rusak saat dikembalikan.
- [[APP - MyBharata]] — entry-point peminjam (menu **Peminjaman Ruangan**; sebelumnya *Coming Soon*).
- [[APP - Web ERP]] — konsol GA (approval, kalender, checklist).

## Kendala

- Master aset masih 🟡 (lihat [[GA - Inventory Management]]) — peminjaman **device** (fase berikut) butuh daftar aset yang rapi sebagai fondasi. **Booking ruang tidak bergantung** pada ini (master ruang berdiri sendiri).
- Penjadwalan anti-bentrok tanpa multi-document transaction (inventory-mongo bukan replica set) → andalkan re-check saat approve; race tipis mungkin perlu penjaga tambahan.
- Push FCM butuh device MyBharata terdaftar per `employee_id`; bila tak ada, inbox tetap tampil (notifikasi best-effort — gagal ≠ gagal booking).

## Belum Diputuskan (TBD)

- **Fase device/aset**: kategori aset yang boleh dipinjam; kondisi pinjam vs kembali; durasi maks & sanksi telat.
- **Kendaraan**: dengan sopir atau dikemudikan sendiri; data BBM/odometer; approver.
- **Durasi maksimum** & aturan booking berulang (recurring) untuk ruang.
- **Integrasi kalender eksternal** (mis. Google Calendar) atau internal saja.
- **Master ruang**: apakah GA kelola CRUD penuh di rilis-1 atau cukup seed dulu (CRUD UI menyusul).
- Catatan: menu **"Loan"** di [[APP - MyBharata]] **bukan** peminjaman aset di dok ini (kemungkinan **pinjaman karyawan/kasbon** — sisi HR; perlu konfirmasi).

## Dokumen Terkait

- [[GA - Inventory Management]] — master aset (fondasi peminjaman device)
- [[Microservices - Inventory Service]] — service rumah kode · [[API - Inventory Service]] — kontrak endpoint
- [[Microservices - Notification Service]] — notifikasi inbox/push ke MyBharata
- [[GA - Machine & Utility Maintenance]] · [[GA - Building Maintenance]] — eskalasi kerusakan
- [[APP - MyBharata]] · [[APP - Web ERP]] — entry-point pengguna
- [[GA - Big Pictures]]
