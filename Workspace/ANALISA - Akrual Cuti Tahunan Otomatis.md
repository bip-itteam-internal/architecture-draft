# ANALISA - Akrual Cuti Tahunan Otomatis

Daftar task hasil `/analisa-kebutuhan` 2026-08-29. Keputusan arsitekturalnya di [[ADR - 0061 Jatah Cuti Tahunan Terbit Otomatis di Ulang Tahun Kontrak]]; cara kerja domainnya di [[HRIS - Leave Request]] §Kuota Cuti Tahunan.

**Dibuat**: 2026-08-29 · **Status**: siap dikerjakan, tiga TBD ditandai ⛔ di §2.

---

## 0. Masalah yang diselesaikan

Satu akar: **tidak ada apa pun yang menerbitkan hak cuti**. Angkanya diketik HR per orang, dan ingatan itu meleset ke dua arah.

| # | Cacat | Bukti |
|---|---|---|
| A | 15 karyawan bermasa kerja >12 bulan berkuota 0, dan karenanya **tidak bisa mengajukan cuti sama sekali** | attendance menolak 400 `VACATION_QUOTA_UNSET` saat `Quota == 0` |
| B | 23 karyawan sudah berkuota padahal belum genap 12 bulan | tak ada gerbang kelayakan di mana pun |
| C | Sisa cuti hangus setahun lebih cepat dari Pasal 15 | `cronResetAnnualLeave` menyetel `used = 0` tanpa memindahkan sisa |
| D | Pemotongan menghitung hari kalender, jatahnya hari kerja | `decrementVacationQuota` merangkai tanggal dengan `AddDate(0,0,1)` tanpa menyaring hari non-kerja |
| E | 2 karyawan bermasa kerja ≥5 tahun tak pernah menerima tambahan 2 hari | tangga senioritas tak ada di kode |

⛔ **Jebakan yang menggagalkan rancangan naif**: `work_data.join_date` bertipe campur (89 `string`, 91 `date` dari 180 karyawan aktif). Cron yang menyaring `join_date` dengan cara biasa **melewati separuh karyawan tanpa satu pun galat**, dan hasilnya terlihat persis seperti cron yang bekerja. Sensus pertama saat analisa ini disusun jatuh ke lubang itu dan menjawab 7 padahal 15.

---

## 1. Urutan kerja

Nomor dalam kurung = prasyarat. Tiap item cukup jelas untuk langsung dilempar ke `/start-task`.

### Gelombang 1 — fondasi data

**T1. Normalisasi `work_data.join_date` jadi tipe `date`.** Skrip dua fase (dry run wajib, `mongodump` dulu, gerbang yang menolak melanjutkan bila jumlahnya di luar dugaan), mengikuti kerangka `.task-plans/jalankan-migrasi-elt.ps1`. Menulis DB produksi, jadi **disiapkan agent, dijalankan manusia**. Kunci hasilnya dengan test yang membaca `$type`, bukan sekadar mencocokkan nilai.
*Prasyarat: tidak ada. Bisa dikerjakan paralel dengan T2.*

**T2. Koleksi `vacation_ledger` + model + indeks.** Satu dokumen per kejadian (`terbit`, `pakai`, `hangus`, `koreksi`) dengan `employee_id`, `company_id`, `periode`, `hari`, `pada`, `kedaluwarsa`, `ref`, `alasan`, `metadata`. Indeks unik atas (`employee_id`, `periode`, `jenis="terbit"`) yang menjadi penjaga idempotensi cron. ⚠️ Indeks unik atas field ber-`omitempty` wajib memakai `partialFilterExpression`.
*Prasyarat: tidak ada.*

### Gelombang 2 — mesin akrual

**T3. Resolver patokan.** Fungsi tunggal yang mengembalikan tanggal patokan plus alasannya: `start_date` kontrak paling awal bertipe `PKWT`/`PKWTT` dari `employee_contract`, disilangkan `join_date`. Selisih >30 hari dan "tanpa kontrak" mengembalikan status **perlu diperiksa**, bukan tanggal. Satu tempat saja, dipakai cron maupun layar.
*Prasyarat: T1, T2.*

**T4. Cron akrual harian.** Menggantikan `cronResetAnnualLeave`. Untuk tiap karyawan aktif: saring status `Magang`/`PKWT (Evaluasi)`, ambil patokan dari T3, lewati bila hari ini bukan ulang tahun patokan atau umur <1 tahun, lalu tulis entri `terbit` (5 hari, atau 7 bila masa kerja ≥5 tahun) dan `hangus` untuk periode yang lewat tenggat. Idempoten lewat indeks T2.
*Prasyarat: T3.*

**T5. Ringkasan ke `work_data.vacation`.** Hitung `quota`, `used`, `remaining`, `available`, `history` dari ledger dan tulis sebagai salinan. **Hanya modul cuti yang boleh menulis field itu**, dikunci test pemindai sumber berdaftar-izin per berkas, mengikuti pola `cakupanDepartemenKPI` di service yang sama.
*Prasyarat: T2, T4.*

### Gelombang 3 — konsumen

**T6. Pemotongan dihitung hari kerja.** Ubah `decrementVacationQuota` agar menyaring Minggu, `Libur Nasional`, dan `Cuti Bersama` dari `company_holiday`, lalu tulis entri `pakai` ber-`ref: leave_request_id`. Ini menyentuh attendance-service.
*Prasyarat: T2.*

**T7. Koreksi HR jadi entri ledger.** `POST /vacation/quota` berhenti menimpa dan mulai menambah baris `koreksi` beserta pelakunya dan alasannya. Bentuk request tetap sama supaya layar lama tidak patah.
*Prasyarat: T2, T5.*

**T8. Layar Kelola Cuti.** Tambah kolom tanggal patokan beserta asalnya, periode berjalan, kapan sisa hangus, dan penanda merah untuk karyawan yang patokannya perlu diperiksa. Ikuti struktur tabel HRIS (`/migrasi-tabel-hris`); teks baru wajib lewat `react-i18next` di `id.ts` **dan** `en.ts`.
*Prasyarat: T3, T5.*

### Gelombang 4 — rilis

**T9. Backfill periode berjalan.** Terbitkan satu entri untuk 15 karyawan yang ulang tahun patokannya sudah lewat. **Tidak** menerbitkan mundur ke periode sebelumnya. Dry run dulu, dijalankan manusia.
*Prasyarat: T4, T5.*

**T10. Verifikasi lewat gateway.** Satu perjalanan utuh sebagai orang: karyawan membuka Sisa Cuti di MyBharata, mengajukan cuti yang melewati hari Minggu, disetujui SPV lalu HR, dan sisanya berkurang sesuai hari kerja. `curl` ke endpoint **tidak** menggantikan ini.
*Prasyarat: seluruhnya.*

---

## 2. TBD yang harus dijawab manusia ⛔

**TBD-1. Lima karyawan dengan kontrak yang tidak nyambung dengan `join_date`.** Salah satunya ber-`join_date` 2024-05-15 dengan kontrak tunggal mulai 2026-07-24, selisih 26 bulan. Mana yang benar menentukan hak orangnya, dan sistem tidak punya cara mengetahuinya. T3 melaporkan mereka; HR yang memutuskan. Daftarnya keluar dari skrip sensus di §4.

**TBD-2. Dua akun aktif tanpa `work_data` sama sekali.** Tidak tersentuh akrual apa pun dan tidak muncul di laporan mana pun. Perlu diputuskan apakah akunnya memang sah.

**TBD-3. Satu karyawan ber-`used: 9` padahal kuota 5, dan satu ber-kuota 4.** Belum ditelusuri. Perlu diketahui sebelum T9 supaya backfill tidak membekukan keadaan yang salah.

---

## 3. Yang belum diverifikasi, jangan diklaim

- Aturan "pengajuan minimal 5 hari kerja sebelumnya" (Pasal 15) belum dicek apakah ada di kode.
- Kewajiban memakai minimal 1 hari cuti tiap bulan: **tidak ada** mekanismenya, dan sengaja di luar lingkup ADR 0061.
- Aturan Izin lebih dari 2 hari yang memotong cuti tahunan: **tidak ada** di kode, di luar lingkup.

---

## 4. Alat bantu

Skrip sensus read-only yang dipakai menyusun analisa ini ada di scratchpad sesi (`sensus-kuota-cuti.ps1` + `.sh`, plus `koreksi-sensus-cuti.sh` yang mengonversi `join_date` lebih dulu). Bila hilang, isinya dapat disusun ulang dari angka di [[ADR - 0061 Jatah Cuti Tahunan Terbit Otomatis di Ulang Tahun Kontrak]] §Context. Menulis DB produksi diblokir untuk agent; siapkan `.ps1` untuk dijalankan manusia.

---

## 5. Konsekuensi deploy

- **Backend sebelum frontend.** employee-service dan attendance-service naik **bersama**, karena gerbang kuota membaca bentuk yang berubah.
- **MyBharata tidak perlu rilis** selama `quota`, `used`, `remaining`, `history` tetap dikirim. Ini alasan salinan ringkas dipertahankan.
- Tidak ada env baru, tidak ada kategori inbox baru. Bila kelak diputuskan mengirim notifikasi "jatah cuti Anda terbit", pengirim dan notification-service wajib naik bersama.
- Deploy produksi disiapkan agent, **dijalankan manusia**.
