> **Status**: 🟡 Konsep (disusun 2026-09-27 dari kode di PR bip-erp #2103, #2105, dan PR P4+P5; **belum pernah dijalankan di prod**). Keputusannya [[ADR - 0129 Persetujuan Payroll Run Bertingkat dan Dibayar per Badan Usaha sebelum Terbit]], papan kerjanya [[ANALISA - Persetujuan Payroll Bertingkat]]. Prosedur deploy umumnya tetap di [[RUN - Deploy Microservices bip-erp]]; dok ini hanya menambahkan yang khusus fitur ini.

## Tujuan

Mengalihkan payroll run di PROD dari alur lama (satu tombol setujui, lalu publish) ke alur bertingkat ADR 0129:

```
susun (HR) -> Cost Control -> SPV HRD -> SPV Finance -> Direksi -> lunas per badan usaha -> terbit
```

Alur bertingkat dikendalikan satu flag, **`PAYROLL_JENJANG_AKTIF`**, di blok `payroll-service` compose. Selama flag bernilai `"false"`, perilaku payroll **persis alur lama**: tidak ada tahap, notifikasi, maupun email slip. Karena itu kode boleh di-deploy jauh lebih awal daripada flag dinyalakan, dan runbook ini terbagi dua fase yang berdiri sendiri.

⛔ **Deploy PROD dan tulis DB PROD dijalankan MANUSIA** (§ Konvensi git & rilis di ingatan tim). Agent menyiapkan perintah dan membaca keadaan saja.

## Prasyarat

- Tumpukan PR bip-erp sudah merged ke `main` **berurutan**: #2103 (P2 jenjang), lalu #2105 (P3 bayar per badan usaha), lalu PR P4+P5 (notifikasi + email slip). P1 (#2095) sudah merged lebih dulu.
- PR erp-frontend untuk layar tanda tangan dan bagian Gaji di CV Ditugaskan (P6) sudah merged. FE **di-deploy sesudah** BE.
- `.env` prod sudah memuat `EMPLOYEE_SERVICE_KEY`, `FINANCE_SERVICE_KEY`, dan `NOTIFICATION_SERVICE_KEY`. Ketiganya sudah dipakai service lain di compose `main`, jadi **tidak ada variabel `.env` baru**. Periksa isinya tidak kosong (nilai kosong di dua sisi terlihat "sama" padahal sama-sama mati):
  ```
  for k in EMPLOYEE_SERVICE_KEY FINANCE_SERVICE_KEY NOTIFICATION_SERVICE_KEY; do printf '%s ' $k; grep -E "^$k=.+" .env | wc -l; done
  ```
  Tiap baris harus `1`.

---

## Fase 1: deploy kode dengan flag MATI

Tujuannya kode naik tanpa mengubah apa pun yang dilihat orang. Di akhir fase ini semua orang tetap memakai alur lama.

### 1a. Container dan urutan

| Urutan | Container | Kenapa ikut |
|---|---|---|
| 1 | `notification-service` | Empat kategori inbox baru (`payroll-tanda-tangan`, `payroll-dikembalikan`, `payroll-siap-bayar`, `payslip`) ada di daftar-izin terkompilasi, plus aturan `web_route` untuk `/payroll/runs/<id>` dan `/payslip`. Pengirim yang naik lebih dulu akan ditolak `400` diam-diam |
| 2 | `employee-service` | Paket izin baru (`payroll_ttd_*`, `payroll_pembayar_cv`, `payroll_pembayar_semua`, `payroll_penerbit`) disisipkan saat start; rute `GET /payroll/rekening-karyawan` dan `GET /payroll/kontak-slip`; antrean Portal Persetujuan per tahap |
| 3 | `finance-service` | Rute `GET /internal/cv/pemegang-badan-usaha` yang dibaca payroll untuk tahu siapa boleh menandai lunas tiap badan usaha |
| 4 | `insentive-service` | Gerbang tandai-terbayar menerima izin bayar baru |
| 5 | `payroll-service` | Jenjang, bayar per badan usaha, notifikasi, email slip. Env baru di blok compose-nya, jadi **wajib `--force-recreate`**, bukan `restart` |
| 6 | frontend | Sesudah kelima BE di atas |

Perintah per container mengikuti [[RUN - Deploy Microservices bip-erp]] (dengan `--no-deps`). Untuk `payroll-service`:

```
docker compose up -d --build --force-recreate --no-deps payroll-service
```

⚠️ **Sadari efek samping start employee-service.** Rutin `selaraskanIzinPaketDefault` menambahkan (`$addToSet`) izin katalog ke paket default yang **sudah tersimpan**, tanpa metadata. Artinya paket lama seperti `payroll_admin` ikut menerima izin baru saat start pertama. Ini disengaja dan terbukti di oplog dev; jangan kaget melihat paket lama berubah.

### 1b. Gerbang verifikasi fase 1

`docker ps` sehat dan `/health` hijau **bukan bukti**. Berurutan:

1. **Biner memuat kode baru**, satu string unik per container:
   ```
   docker exec Notification-Service sh -c 'strings /service | grep -c payroll-tanda-tangan'
   docker exec Employee-Service     sh -c 'strings /service | grep -c kontak-slip'
   docker exec Finance-Service      sh -c 'strings /service | grep -c pemegang-badan-usaha'
   docker exec Payroll-Service      sh -c 'strings /service | grep -c PAYROLL_JENJANG_AKTIF'
   ```
   Semua harus `> 0`. Nama container dan path biner ikut compose; bila berbeda, sesuaikan, jangan dilewati.
2. **Flag benar-benar mati**:
   ```
   docker exec Payroll-Service printenv PAYROLL_JENJANG_AKTIF
   ```
   Harus `false`.
3. **Paket baru tersisip** (baca saja):
   ```
   db.master_permission_set.find({key: /^payroll_(ttd_|pembayar_|penerbit)/}, {key:1, permissions:1})
   ```
   Harus **tujuh** paket.
4. **Alur lama tetap jalan**: seorang penyetuju payroll lama membuka satu run draft lewat layar dan melihat tombol setujui seperti biasa. Kalau tombolnya hilang, flag tidak benar-benar mati atau FE naik lebih dulu daripada BE.

---

## Fase 2: pasang paket ke jabatan

Paket yang sudah tersisip belum menempel ke siapa pun. Skrip berikut memasangnya ke **item posisi** di `master_department` BIP. Ini tulis prod, jadi **dijalankan manusia**.

Skrip: `.task-plans/2026-09-27-pasang-paket-payroll-bertingkat-prod.ps1` (beserta `.js` pendampingnya) di akar workspace `erp/`. Skrip ini **tidak** ada di repo mana pun; ia disiapkan untuk sekali jalan.

| Departemen / jabatan (`position_key`) | Paket |
|---|---|
| Finance / `cost_control` | `payroll_ttd_cost_control` |
| Human Resource / `hrd_supervisor` | `payroll_ttd_hrd` |
| Finance / `finance_supervisor` | `payroll_ttd_finance` |
| Kesekretariatan / `direktur` | `payroll_ttd_direksi` |
| Kesekretariatan / `corporate_secretary` | `payroll_ttd_direksi` |
| Finance / `accounting_cv` | `payroll_pembayar_cv` |
| Finance / `senior_accountant` | `payroll_pembayar_semua` |
| Human Resource / `personalia` | `payroll_penerbit` |

Kenapa `senior_accountant` memegang `payroll_pembayar_semua`: badan usaha PT Bharata **tidak punya CV**, jadi tak ada `accounting_cv` yang ditugaskan padanya. Tanpa satu pemegang bayar-semua, baris PT tak bisa ditandai lunas dan terbit macet selamanya. Diukur prod 2026-09-27: 40 dari 40 CV sudah terpetakan dan berpemegang.

Berurutan:

```
.\2026-09-27-pasang-paket-payroll-bertingkat-prod.ps1 -Mode cek
.\2026-09-27-pasang-paket-payroll-bertingkat-prod.ps1 -Mode terapkan
```

- Mode `cek` tidak menulis apa pun, dan keluarannya **otomatis disimpan sebagai berkas cadangan**. Mode `terapkan` menolak jalan bila cadangan itu belum ada.
- Skrip **menolak** jalan bila tujuh paket belum tersisip (fase 1 belum selesai) atau bila salah satu jabatan sasaran tidak tepat satu item posisi.
- Jalan pulang: `-Mode balik -Cadangan <berkas cadangan dari mode cek>`.

Sesudahnya, **klaim izin terbit saat login**: pemegang jabatan harus login ulang (atau menunggu token kedaluwarsa, 72 jam) sebelum tombol tahapnya muncul.

⚠️ Paket lama (`payroll_penyetuju`, `payroll_admin`, `payroll_pelaksana`, `payroll_lihat`) **sengaja tidak disentuh** di fase ini. Selama flag mati, alur lama memakainya.

---

## Fase 3: nyalakan flag

Lakukan di **awal siklus payroll**, saat tidak ada run yang sedang dalam proses setujui. Run yang sudah `approved` di bawah alur lama tetap bisa diterbitkan dengan jalur lama; jangan menyalakan flag di tengah run yang separuh jalan.

Compose membaca flag dari `.env` dengan bawaan `false` (`"${PAYROLL_JENJANG_AKTIF:-false}"`, bip-erp PR `fix/payroll-flag-jenjang-env`). ⚠️ Jangan menyunting nilai di `docker-compose.dev.yml`: VM dev pun membangun dari `docker-compose.yml`, jadi berkas `.dev.yml` tidak dibaca siapa pun di sana.

1. Pastikan frontend yang memuat layar jenjang (erp-frontend #1761) **sudah naik** di lingkungan itu. Flag hidup dengan layar lama membuat tak seorang pun bisa menyetujui gaji.
2. Tambahkan satu baris ke `.env` server:
   ```
   PAYROLL_JENJANG_AKTIF=true
   ```
3. Buat ulang container dan buktikan:
   ```
   docker compose up -d --force-recreate --no-deps payroll-service
   docker exec Payroll-Service printenv PAYROLL_JENJANG_AKTIF
   ```
   Harus `true`. `restart` **tidak cukup**, karena env dibaca saat container dibuat. Catat tanggal dan orang yang menyalakannya di papan [[ANALISA - Persetujuan Payroll Bertingkat]], karena perubahan `.env` tidak meninggalkan jejak git.

### 3a. Gerbang verifikasi fase 3: satu perjalanan utuh sebagai orang

`curl` ke endpoint tidak menggantikan ini. Pakai satu run nyata di awal siklus:

1. HR staff menyusun run dan menekan **Ajukan**. Cost Control **menerima notifikasi inbox** "menunggu tanda tangan", dan barisnya muncul di **Portal → Persetujuan** dan bisa diklik sampai ke layar run.
2. Cost Control membuka rincian potongan, menambah satu catatan per baris, lalu **Setujui**. SPV HRD menerima notifikasi.
3. Uji jalur kembali sekali: satu tahap menekan **Kembalikan** beralasan. Penyusun menerima notifikasi "dikembalikan", mengoreksi **hanya baris itu**, dan mengajukan ulang. Run melanjutkan dari tahap yang mengembalikan, dan tanda tangan sebelumnya tetap berlaku.
4. SPV Finance, lalu Direksi menyetujui. Tiap pemegang `payroll.bayar` menerima notifikasi "siap dibayar" untuk CV yang ditugaskan padanya.
5. Accounting CV membuka **Finance → Accounting CV → CV Ditugaskan → Gaji**, mengunduh daftar bayar, lalu menandai **lunas**. Baris PT ditandai lunas oleh pemegang bayar-semua.
6. Setelah seluruh badan usaha lunas, penerbit menekan **Terbitkan**. Karyawan aktif menerima notifikasi slip; karyawan nonaktif dikirimi **email berlampiran PDF terkunci** (sandi tanggal lahir `DDMMYYYY`).
7. Periksa kiriman email di `GET /api/payroll/payroll-runs/<id>/slip-email`. Baris berstatus gagal (tanpa email atau tanggal lahir) dibereskan datanya, lalu dikirim ulang lewat `POST .../slip-email/<employeeId>/kirim-ulang`.

**Angka nol diperlakukan sebagai pertanyaan.** Nol notifikasi terkirim di langkah 1, atau nol email di langkah 6 padahal ada karyawan nonaktif di run, berarti rantainya putus, bukan kabar baik.

### 3b. Mematikan kembali

Bila alur bertingkat bermasalah, hapus baris itu dari `.env` (atau ubah ke `false`) lalu `--force-recreate` yang sama. Run yang sedang `dalam_persetujuan` **tidak otomatis kembali** ke alur lama; periksa statusnya satu per satu sebelum mematikan.

---

## Sesudah terbukti: P10, cabut paket lama

Langkah terpisah, **setelah paling sedikit satu run terbit lewat alur bertingkat**. Skripnya `.task-plans/2026-09-27-p10-cabut-paket-lama-prod.ps1` (cek/terapkan/balik, dijalankan manusia). Mode `terapkan` **menolak jalan** sampai tiga syarat terpenuhi: `PAYROLL_JENJANG_AKTIF=true`, paket tahap P7 terpasang (HRD Supervisor memegang `payroll_ttd_hrd`), dan minimal satu run `published` yang riwayatnya memuat tanda tangan tahap Direksi. Sebelum itu paket lama adalah satu-satunya jalan menyetujui gaji.

Susunan akhirnya (ADR 0129 §8):

| Jabatan | Paket sesudah | Izin |
|---|---|---|
| Personalia | `payroll_pelaksana`, `payroll_penerbit`, `payroll_pengaturan` (baru) | lihat, master gaji, susun, terbitkan, pengaturan; **tanpa** setujui lama |
| HRD Supervisor | `payroll_ttd_hrd`, `payroll_ubah_master_gaji` (baru); `payroll_pengaturan` hanya dengan `-SpvHrdPengaturan` | lihat, tanda tangan tahap 2, master gaji |

Paket `payroll_*` yang menempel **langsung di akun** pemegangnya (diukur prod 2026-09-27: Gilang BIP-0187-08-25 dan Seno BIP-0222-11-25) ikut dibersihkan, supaya hak hanya datang dari jabatan.

⚠️ Jalankan `-Mode cek` **tepat sebelum** `terapkan` dan simpan cadangan itu untuk `balik`. Cadangan lama mencerminkan keadaan saat dibuat, bukan saat diterapkan.
## Kemudian

Langkah terpisah, **bukan** bagian runbook ini: mencabut `payroll.approve` lama dari paket `payroll_penyetuju` setelah alur baru berjalan paling sedikit satu siklus penuh di prod. Dicatat di papan [[ANALISA - Persetujuan Payroll Bertingkat]].
