**Status**: 🟡 Daftar task dari `/analisa-kebutuhan` 2026-10-12. Keputusannya di [[ADR - 0172 Token Login Keluar dari Cookie dan Paket Semua Izin Dimekarkan saat Token Terbit]]. Dok ini papan kerja, bukan arsitektur. Coret item begitu PR-nya merge, lalu pindahkan keadaannya ke dok domain lewat `/sync-docs`; jangan menumpuk status di sini.

## Kebutuhan yang dijawab

Akun dengan banyak paket hak terpental ke halaman login Web ERP, karena JWT disimpan di cookie dan browser membuang cookie di atas ±4 KB. Manajemen meminta paket super admin "supaya JWT tak terlalu panjang". Analisa menemukan:
- Penyebabnya penyimpanan token, bukan jumlah izin.
- Penanda super admin di token akan mahal (±120 konsumen) dan berisiko (12 tempat logika terbalik).

Opsi yang dipilih:
- **A**: token keluar dari cookie.
- **C**: paket bawaan Semua Izin dimekarkan saat token terbit, gerbang penetapan tetap staf IT, ditambah larangan memasang ke diri sendiri.

## Urutan deploy yang mengikat

**T1 wajib live di prod sebelum T2 dan T3 naik ke prod.** Paket Semua Izin memperbesar token pemegangnya, jadi tanpa T1 pemegangnya pasti terpental.

Urutan T2 dan T3: BE (employee-service) sebelum FE. Tidak ada env baru. Prod dijalankan manusia (skill `deploy-bip-erp` §0).

## Task

### T0. Ukur ukuran token per akun (baca saja, opsional tapi disarankan)
- **Repo**: bip-erp, alat `banding_token` di employee-service (`services/employee/banding_token.go`). Alat ini menulis JSON `system_roles` + `permissions` per akun, tanpa ukuran.
- **Isi**: hitung panjang token per akun dari keluarannya, lalu sebutkan berapa akun yang melewati 4 KB hari ini. Angka ini mengganti asumsi "jumlah yang terpental" di ADR 0172 §Context.
- **Batas**: baca saja. Tidak ada yang ditulis ke prod.
- **Dependensi**: tidak ada.

### T1. Token Web ERP disimpan di `localStorage` lewat satu modul
- **Repo**: erp-frontend.
- **Isi**:
  - Satu modul sesi-token, satu-satunya penulis, pembaca, dan penghapus JWT.
  - Tujuh pembaca `getCookie("token")` dipindah ke modul itu: `login/page.tsx`, `lib/axios.ts` (dua titik), `use-auth.ts`, `incentive/utils/download.ts`, `use-fetch-advertisers.ts`, `GudangBarangJadiView.tsx`. `use-refresh-auth.ts` adalah kode mati; hapus, jangan dipindah.
  - `proxy.ts` memeriksa cookie penanda kecil, berumur sama dengan `exp`, yang diperbarui saat refresh dan dihapus saat logout atau `redirectToLogin`.
  - Cookie `system_roles` tetap.
  - Alur SSO `redirect_url` di `login/page.tsx:116-130` tetap jalan.
- **Test**:
  - Unit untuk modul sesi-token (tulis, baca, hapus, penanda ikut hilang).
  - Kontrol negatif: kembalikan satu pembaca ke `getCookie("token")`, lalu pastikan ada penjaga (test atau lint) yang merah.
  - Penjaga pemindai sumber: nol `getCookie("token")` tersisa di `src` (pakai `git grep`, bukan ripgrep).
- **Verifikasi**: di dev, login dengan akun bertoken > 4 KB (atau buat dengan memasang banyak paket ke akun uji lokal). Harus tidak terpental, dan refresh token tetap jalan. Ukur `document.cookie` tanpa JWT. Jalankan satu perjalanan utuh sebagai orang (`/wrap` §5d).
- **Dependensi**: tidak ada.
- **Konsekuensi**: pengguna yang sedang login saat rilis keluar sekali. Umumkan sebelum deploy prod.

### T2. Paket bawaan Semua Izin di employee-service
- **Repo**: bip-erp.
- **Isi**:
  - Kunci paket bawaan baru, disinkron tiap start seperti paket bawaan lain (ADR 0164), tidak bisa disunting isinya.
  - Pemekarannya di perakit izin (`hitungIzinEfektif` di jalur `rakitHakToken`): seluruh izin setiap katalog terdaftar kecuali modul `menu`, plus `<modul>.$reach.all`.
  - Penetapan ditolak bila sasaran = pemanggil, atau posisi sasaran = posisi pemanggil. Berlaku di `PATCH /account/permission-sets` dan `PUT .../positions/:positionKey/permission-sets`.
  - Akun pihak luar tetap ditolak.
- **Putuskan di `/plan`**: apakah daftar pemegang izin (`permission_holders.go`) ikut memekarkan Semua Izin. Bila ya, pemegangnya jadi kandidat penyetuju dan penerima notifikasi di setiap modul. ADR 0172 §Consequences mencatat ini sebagai hal yang bisa mengejutkan.
- **Test**:
  - Fungsi murni pemekaran: seluruh katalog, `menu` dikecualikan, reach `all`, dan tak ada duplikat bila digabung paket lain.
  - Test Fiber jalur 403 untuk penetapan ke diri sendiri, dengan kontrol positif: rekan memasangkan → 200.
  - Satu test yang membuktikan penanda `account.$type.external` tidak pernah berdampingan dengan paket ini.
- **Verifikasi**:
  - Lewat gateway di dev: login akun uji pemegang paket, lalu periksa klaim `permissions` memuat izin dari setiap katalog kecuali `menu`.
  - **Ukur panjang token** dan catat di [[CORE - RBAC dan Permission Set]].
  - Pastikan larangan menyetujui pengajuan sendiri tetap menolak.
- **Dependensi**: tidak ada di kode. **Deploy prod setelah T1 live.**

### T3. Layar Hak Akses menampilkan paket Semua Izin
- **Repo**: erp-frontend, `src/app/(main)/it/hak-akses/page.tsx` dan modal permission set.
- **Isi**:
  - Paket tampil di pemilih paket akun dan posisi, dengan keterangan bahwa isinya seluruh katalog kecuali menu terbatas.
  - Tidak bisa disunting dan tidak bisa dihapus.
  - Penolakan "tidak bisa dipasang ke diri sendiri" tampil sebagai pesan dari server, bukan toast generik.
  - Seluruh teks lewat `t()` di `id.ts` dan `en.ts` (ADR 0010).
- **Verifikasi**: perjalanan sebagai staf IT: pasang ke rekan → berhasil; pasang ke diri sendiri → ditolak dengan pesan yang bisa dibaca.
- **Dependensi**: T2 merged (kontrak). Deploy sesudah employee-service.

### T4. Sinkron dok
- `/sync-docs` sesudah T1 dan T2 live:
  - status ADR 0172 → Implemented;
  - ukuran token pemegang Semua Izin di [[CORE - RBAC dan Permission Set]];
  - catatan penyimpanan token di [[APP - Web ERP]] dan [[CORE - SSO Flow]].

## Issue GitHub (dibuat 2026-10-12, Project #15, Backlog)

- Induk: bip-erp#2981 (memuat T0 sebagai checklist)
- T1 `[FE]`: erp-frontend#2315
- T2 `[BE]`: bip-erp#2982
- T3 `[FE]`: erp-frontend#2316

Label `Siap Agent` dipasang manusia **setelah** ADR 0172 berstatus Diterima. `**Pemutus:**` di induk masih TBD.
