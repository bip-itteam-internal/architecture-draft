# ANALISA - Ambil Alih Sesi Live Host

> Papan kerja hasil `/analisa-kebutuhan` 2026-09-11. Keputusannya di
> [[ADR - 0088 Ambil Alih Sesi Live oleh Host Terjadwal dan Tutup Otomatis Akhir Shift]], cara kerjanya di
> [[Microservices - Marketing Analytics Service]] §Ambil alih & tutup otomatis akhir shift.
> Berkas ini berubah tiap item selesai; ADR dan dok domain yang jadi rujukan tetap.

## Ringkas

Yang diminta: tombol "ambil alih" sesi live. Kebutuhan sebenarnya: **siaran host berikutnya
tetap tercatat atas namanya walau sesi sebelumnya ditinggal terbuka**. Istirahat bolak-balik
tidak dibangun terpisah, karena sudah berjalan lewat Akhiri lalu Mulai dengan atribusi yang
benar.

Dua jalan ditambahkan: **tutup otomatis di jam berakhir shift + 60 menit** dan **ambil alih
oleh host yang jadwalnya sedang berjalan**. Keputusan 2026-08-30 (leader tak boleh
menghentikan sesi orang lain) tetap berlaku, kecuali satu pengecualian sempit itu.

**Angka yang mendasari** (prod 2026-09-11, 58 sesi 9 sampai 11 Sep): 40 pergantian host pada
akun yang sama. Bila pemegang lupa dan jalannya hanya tutup otomatis, host berikutnya tertahan
median 239 menit (maksimum 450). Aturan +60 memotong 0 dari 45 sesi sah (molor terbesar
2,8 menit).

## Urutan & dependensi

```
T1 (BE: tutup otomatis +60) ────────────────────────────┐
T2 (BE: ambil alih) ─┬─> T3 (web: tombol + riwayat) ────┼─> T5 (verifikasi lapangan)
                     └─> T4 (MyBharata: tombol + rilis) ┘
brief celah 1 web ─────> T3      brief celah 1 mobile ──> T4
T0 (HR: jadwal) paralel, non-kode, wajib selesai sebelum T5
```

⚠️ **T1 berdiri sendiri dan naik lebih dulu.** Ia kecil, tanpa env baru, dan sendirian sudah
mencegah kejadian 10 ke 11 September.

⚠️ **Deploy BE sebelum klien** untuk T2 (kontrak bertambah). T3 dan T4 juga menunggu brief
celah 1 masing-masing, karena tombol Ambil alih tinggal di layar penolakan yang dibangun brief itu.

---

## T0. Betulkan jadwal host yang tak cocok dengan jam kerjanya (HR, non-kode)

Host `BIP-0203-08-25` terjadwal 16:00 sampai 24:00 tetapi siaran sekitar 12:00 sampai 20:00;
10 sesinya tervonis luar shift, dan absensinya 8 sampai 10 Sep tercatat Tanpa Keterangan.
Sesudah ADR 0088, jadwal yang salah bukan lagi sekadar label: host itu **tidak bisa
mengambil alih**, dan sesinya **tidak tertutup otomatis**.

**Keluaran**: jadwalnya dibetulkan pengelola jadwal Host Live
([[ADR - 0072 Kewenangan Jadwal Host Live sebagai Izin yang Ditugaskan]]), dan sesi
berikutnya tervonis `dalam_shift`. Bukan pekerjaan kode.

## T1. BE: tutup otomatis di jam berakhir shift + 60 menit

- Sesi berjalan yang melewati jam berakhir shift + 60 menit ditutup dengan `selesai` **tepat
  di batas itu** (bukan jam tik), `ditutup_otomatis: true`, alasan `shift_berakhir`.
- Aturan clock-out yang ada tetap dan menang bila lebih awal.
- Jam berakhir = yang **paling akhir** di antara host `dalam_shift`. Sekarang diambil dari host
  pertama (`live_shift_handler.go:294-308`); pengingat `shift_usai` ikut memakai nilai yang sama.
- Sesi tanpa jam berakhir tidak disentuh.
- Host diberi tahu lewat kategori `reminder` yang sudah ada.
- Tik dan jalur lazy `GET /berjalan` memakai **satu** fungsi keputusan; jangan dua salinan.

**Selesai bila** (test): sesi dalam shift yang lewat +60 tertutup tepat di +60; clock-out lebih
awal tetap menang; sesi tanpa jam berakhir tetap terbuka; co-host beda shift memakai jam paling
akhir; notifikasi terkirim sekali walau tik berulang.

**Deploy**: `marketing-analytics-service` saja, tanpa env baru. ⚠️ Tik pertama langsung menutup
sesi berjalan yang sudah lewat +60, jadi periksa sesi berjalan sebelum deploy.

**Mulai**: `jalankan /start-task Tutup otomatis Sesi Live Host di jam berakhir shift + 60 menit (ADR 0088 §1)`

## T2. BE: ambil alih oleh host terjadwal

- Permintaan membawa **id sesi yang ditampilkan** di layar penolakan; bila pemegangnya sudah
  berganti, jawabannya 409 baru.
- Gerbang: lolos `RequireLiveShiftUser`, penekan termasuk host sesi baru, jadwalnya
  `dalam_shift` saat itu (resolusi jadwal yang sama dengan Mulai). Resolusi gagal atau
  `tak_diketahui` ditolak dengan pesan yang menyebut sebabnya.
- Sesi lama: `selesai` = sekarang, jeda terbuka ikut ditutup, filter `selesai: null` (yang kalah
  balapan menerima 409), jejak siapa yang mengakhiri dan alasan `ambil_alih`.
- Sesi baru dimulai pada instan yang sama (bersentuhan tepat, bukan tumpang tindih).
- Pemberitahuan ke seluruh host sesi lama dan atasan langsung mereka; best-effort, kegagalan
  mencari atasan tidak menggagalkan ambil alih.
- `bolehKelolaSesi` **tidak** diubah.

⚠️ Dua tulisan, bukan satu transaksi: bila sesi lama sudah tertutup tetapi sesi baru kalah
balapan dari host lain, penekan menerima 409 yang menyebut pemegang barunya. Keadaan itu sah,
tapi wajib dikunci test dan tidak boleh berbunyi 500.

**Selesai bila** (test, dan sekali lewat gateway): host terjadwal lolos; host luar shift,
`tak_diketahui`, dan resolusi gagal ditolak; penekan yang bukan host sesi baru ditolak; id sesi
basi ditolak 409; dua pengambil alih bersamaan menghasilkan satu pemenang; `selesai` sesi lama
sama dengan `mulai` sesi baru; leader tetap 403 di `PATCH /:id/selesai`.

**Deploy**: BE sebelum web dan MyBharata. Env baru untuk mencari atasan di employee-service
berarti `up -d --force-recreate marketing-analytics-service`, bukan restart.

**Mulai**: `jalankan /start-task Ambil alih sesi Sesi Live Host oleh host terjadwal (ADR 0088 §2)`

## T3. Web: tombol Ambil alih + label riwayat

**Prasyarat**: brief `.task-plans/briefs/2026-09-11-pemegang-akun-409-web.md` (menyebut pemegang
di penolakan) sudah merged, dan T2 sudah ter-deploy.

- Tombol per akun yang bentrok di dialog Mulai (dialognya bisa memulai beberapa akun sekaligus).
- Konfirmasi wajib menyebut akun dan nama pemegang, karena aksinya tak bisa dibatalkan.
- Penolakan jadwal menampilkan pesan server apa adanya.
- Riwayat: "Diambil alih oleh X pukul HH:MM" dan "Ditutup otomatis: shift berakhir".
- i18n id + en, jam diformat di render dengan `intlLocale(lang)`, tanpa prop baru di komponen shared.

**Mulai**: `jalankan /start-task Tombol Ambil alih dan label riwayat Sesi Live Host di web (ADR 0088)`

## T4. MyBharata: tombol Ambil alih + label riwayat + rilis

**Prasyarat**: brief `.task-plans/briefs/2026-09-11-pemegang-akun-409-mybharata.md` sudah merged,
dan T2 sudah ter-deploy.

Isinya sama dengan T3. PR ke `dev`. Rilis menaikkan version name **dan** code
(`update_version.dart` dua argumen).

**Mulai**: `jalankan /start-task Tombol Ambil alih dan label riwayat Sesi Live Host di MyBharata (ADR 0088)`

## T5. Verifikasi lapangan

Di DEV dengan dua akun host, lalu sekali di prod sesudah deploy:

1. Host A Mulai di akun X. Host B (terjadwal) menekan Mulai di akun X dari HP, melihat nama A,
   lalu menekan Ambil alih.
2. A menerima pemberitahuan; riwayat A berbunyi "Diambil alih oleh B"; `selesai` A sama dengan
   `mulai` B.
3. Sesudah sync TikTok, GMV terbagi per potongan waktu dan tak satu pun sesi `perlu_koreksi`.
4. Satu sesi yang dibiarkan lewat jam berakhir + 60 menit tertutup sendiri dengan alasan
   `shift_berakhir`.

Lewat gateway, bukan panggilan lokal. Test hijau bukan bukti fiturnya bisa dipakai.

## T6. Dok menyertai tiap item

Tiap item yang naik memperbarui [[Microservices - Marketing Analytics Service]] (§Ambil alih &
tutup otomatis akhir shift dari 🟡 ke ✅), [[API - Marketing Analytics Service]] (rute atau
parameter baru), dan status ADR 0088.

---

## Di luar lingkup, sengaja

- **Koreksi `perlu_koreksi` lewat layar.** Tetap skrip tulis DB yang dijalankan manusia, sampai
  ada keputusan siapa berwenang menyetujui koreksi atribusi.
- **Batas keras untuk sesi tanpa jadwal** (mis. tutup paksa di jam ke-12). Butuh keputusan
  tersendiri.
- **Leader mengakhiri sesi orang lain.** Keputusan 2026-08-30 tetap.
- **Persetujuan host lama sebelum ambil alih.** Yang meninggalkan sesi justru orang yang tak bisa
  dihubungi.

## Terkait di luar papan ini (insiden 2026-09-11)

- Brief celah 1 (dua berkas di T3 dan T4) siap untuk `/kerjakan`.
- Skrip pindah toko carevolution (`.task-plans/2026-09-11-pindah-toko-carevolution.ps1`) belum
  dijalankan.
