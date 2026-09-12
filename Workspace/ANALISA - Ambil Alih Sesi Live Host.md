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
oleh host yang jadwalnya sedang berjalan**, dengan persetujuan pemegang berbatas 30 detik (diam
berarti setuju; revisi 2026-09-11). Keputusan 2026-08-30 (leader tak boleh
menghentikan sesi orang lain) tetap berlaku, kecuali satu pengecualian sempit itu.

**Angka yang mendasari** (prod 2026-09-11, 58 sesi 9 sampai 11 Sep): 40 pergantian host pada
akun yang sama. Bila pemegang lupa dan jalannya hanya tutup otomatis, host berikutnya tertahan
median 239 menit (maksimum 450). Aturan +60 memotong 0 dari 45 sesi sah (molor terbesar
2,8 menit).

**Keadaan 2026-09-12 09:34 WIB**: T1 di PROD, belum pernah terpicu. T2 di PROD sejak 08:55 WIB (bip-erp #1855,
DEV terverifikasi lewat gateway). T4 merged ke `dev` (my-bharata #143), rilis 1.17.0+161 belum diverifikasi. T3 batal.
Sisa: rilis MyBharata, T5, dan T0 (HR). Rencana `.task-plans/2026-09-11-ambil-alih-sesi-live.md`.

## Urutan & dependensi

```
T1 (BE: tutup otomatis +60) ────────────────────────────┐
T2 (BE: ambil alih) ─┬─> T3 (web: BATAL, ADR 0091) ─────┼─> T5 (verifikasi lapangan)
                     └─> T4 (MyBharata: tombol + rilis) ┘
brief celah 1 mobile dilebur ke T4; brief celah 1 web gugur bersama T3
T0 (HR: jadwal) paralel, non-kode, wajib selesai sebelum T5
```

⚠️ **T1 berdiri sendiri dan naik lebih dulu.** Ia kecil, tanpa env baru, dan sendirian sudah
mencegah kejadian 10 ke 11 September.

⚠️ **Deploy BE sebelum klien** untuk T2 (kontrak bertambah). Tombol Ambil alih tinggal di layar
penolakan yang semula dibangun brief celah 1; untuk mobile brief itu dikerjakan di dalam T4.

---

## T0. Betulkan jadwal host yang tak cocok dengan jam kerjanya (HR, non-kode)

Host `BIP-0203-08-25` terjadwal 16:00 sampai 24:00 tetapi siaran sekitar 12:00 sampai 20:00;
10 sesinya tervonis luar shift, dan absensinya 8 sampai 10 Sep tercatat Tanpa Keterangan.
Sesudah ADR 0088, jadwal yang salah bukan lagi sekadar label: host itu **tidak bisa
mengambil alih**, dan sesinya **tidak tertutup otomatis**.

**Keluaran**: jadwalnya dibetulkan pengelola jadwal Host Live
([[ADR - 0072 Kewenangan Jadwal Host Live sebagai Izin yang Ditugaskan]]), dan sesi
berikutnya tervonis `dalam_shift`. Bukan pekerjaan kode.

**Status 2026-09-12**: belum terlihat dibetulkan. Pada 11 Sep host itu punya 6 sesi `luar_shift` dan 1
`dalam_shift`, dan jam berakhir shift yang tercatat di sesinya masih 24:00 WIB.

## T1. BE: tutup otomatis di jam berakhir shift + 60 menit

**Status 2026-09-11**: merged ke `main` (bip-erp #1847 pukul 16:21 WIB, erp-frontend #1539
pukul 16:32 WIB) dan **di PROD** (`marketing-analytics-service` 16:55 WIB, `frontend-hris`
16:59 WIB). Deploy prod dijalankan agent atas penegasan eksplisit user, menyimpang dari aturan
tim bahwa prod dijalankan manusia. Gerbang biner dan bundel lolos; saat naik 0 dari 4 sesi
berjalan tertutup. Rencana `.task-plans/2026-09-11-tutup-otomatis-akhir-shift.md`. Per 2026-09-12
09:34 WIB belum pernah terpicu: tak satu pun sesi ditutup otomatis sejak deploy, dan kelima sesi yang dimulai
sesudahnya diakhiri host paling lambat semenit sesudah jam berakhir shift. Sisa: bukti perilaku pertama,
verifikasi DEV lewat gateway, dan daftar verifikasi pasca-merge di badan kedua PR.

- Sesi berjalan yang melewati jam berakhir shift + 60 menit ditutup dengan `selesai` **tepat
  di batas itu** (bukan jam tik), `ditutup_otomatis: true`, alasan `shift_berakhir`.
- Aturan clock-out yang ada tetap dan menang bila lebih awal.
- Jam berakhir = yang **paling akhir** di antara host `dalam_shift`. Sekarang diambil dari host
  pertama (`live_shift_handler.go:294-308`); pengingat `shift_usai` ikut memakai nilai yang sama.
- Sesi tanpa jam berakhir tidak disentuh.
- Host diberi tahu lewat kategori `reminder` yang sudah ada.
- Teks pengingat `shift_usai` (jam berakhir + 30 menit) menyebut jam tutup otomatisnya.
- **Web (erp-frontend)**: badge riwayat membaca alasan selesai ("shift berakhir" / "clock-out");
  sesi lama tanpa alasan tetap memakai teks sekarang. Sekarang badge berbunyi "Ditutup otomatis
  (clock-out)" untuk setiap penutupan otomatis (`tabel-riwayat-live.tsx:121-125`). ⛔ Badge web ini
  ikut hilang saat halaman web Sesi Live Host dihapus 2026-09-11
  ([[ADR - 0091 Pencatatan Sesi Live Host Hanya di MyBharata, Halaman Web Dihapus]]).
- Tik dan jalur lazy `GET /berjalan` memakai **satu** fungsi keputusan; jangan dua salinan.

**Selesai bila** (test): sesi dalam shift yang lewat +60 tertutup tepat di +60; clock-out lebih
awal tetap menang; sesi tanpa jam berakhir tetap terbuka; co-host beda shift memakai jam paling
akhir; notifikasi terkirim sekali walau tik berulang.

**Deploy**: `marketing-analytics-service` dulu, lalu `erp-frontend` (badge riwayat), tanpa env
baru. ⚠️ Tik pertama langsung menutup
sesi berjalan yang sudah lewat +60, jadi periksa sesi berjalan sebelum deploy.

**Mulai**: `jalankan /start-task Tutup otomatis Sesi Live Host di jam berakhir shift + 60 menit (ADR 0088 §1)`

## T2. BE: ambil alih oleh host terjadwal

**Status 2026-09-12**: merged 07:31 WIB (bip-erp #1855, 7 commit `c2ba308a..b8b2e8c8`) dan **di PROD sejak
08:55 WIB**. Deploy PROD pertama (07:32 WIB) membangun checkout yang ditarik 19 detik sebelum merge, jadi
biner sempat tanpa rute ini; ketahuan dari gerbang nama fungsi. Review menemukan satu cacat kritis yang sudah diperbaiki:
eksekusi menulis ulang `jeda` dari snapshot yang dibaca sebelum panggilan attendance, sehingga
Jeda/Lanjutkan yang ditekan pemegang di celah itu tertimpa; kini bersyarat posisional seperti
tutup otomatis. Keputusan perencanaan: permintaan disimpan di dokumen sesi lama; pemegang tahu
lewat `GET /live-shifts/ambil-alih/menunggu` yang dipoll 3 detik; eksekusi karena diam dipicu
pembacaan status oleh peminta dengan tenggang 20 detik sesudah batas; pemberitahuan atasan
ditunda. DEV terverifikasi lewat gateway 08:02 WIB (`/menunggu` 200, status sesi karangan 404 dari handler);
PROD lewat biner dan `/menunggu` 200 dari dalam container. Alur utuh belum dijalankan (butuh satu baris
`department_shops` di Mongo DEV dan dua akun uji yang jadwalnya sedang berjalan).

- Permintaan membawa **id sesi yang ditampilkan** di layar penolakan; bila pemegangnya sudah
  berganti, jawabannya 409 baru.
- Gerbang: lolos `RequireLiveShiftUser`, penekan termasuk host sesi baru, jadwalnya
  `dalam_shift` saat itu (resolusi jadwal yang sama dengan Mulai). Resolusi gagal atau
  `tak_diketahui` ditolak dengan pesan yang menyebut sebabnya.
- Yang lolos jadi **permintaan yang menunggu**, satu per sesi, batas 30 detik menurut jam
  server. Permintaan kedua selama yang pertama menunggu dijawab 409.
- Pemegang: notifikasi (kategori `reminder`) plus data yang cukup bagi MyBharata untuk
  menampilkan jendela persetujuan (siapa, jadwal, akun, sisa waktu). Setujui dan Tolak hanya
  boleh dari host sesi lama.
- Setujui = eksekusi seketika; Tolak = gugur, peminta diberi tahu siapa yang menolak; tak
  dijawab 30 detik = eksekusi, **hanya bila peminta masih menunggu**.
- Eksekusi: gerbang diperiksa ulang; sesi lama `selesai` = detik eksekusi, jeda terbuka ikut
  ditutup, filter `selesai: null` (yang kalah balapan menerima 409); jejak siapa yang
  mengakhiri, alasan `ambil_alih`, dan cara persetujuan; sesi baru dimulai pada instan yang sama.
- Pemberitahuan sesudah eksekusi ke seluruh host sesi lama; best-effort. Pemberitahuan ke
  atasan langsung **ditunda** (keputusan 2026-09-11, revisi ADR 0088 §5): resolver atasan per
  karyawan belum ada.
- `bolehKelolaSesi` **tidak** diubah.

⚠️ Dua tulisan, bukan satu transaksi: bila sesi lama sudah tertutup tetapi sesi baru kalah
balapan dari host lain, penekan menerima 409 yang menyebut pemegang barunya. Keadaan itu sah,
tapi wajib dikunci test dan tidak boleh berbunyi 500.

**Selesai bila** (test, dan sekali lewat gateway): host terjadwal lolos; host luar shift,
`tak_diketahui`, dan resolusi gagal ditolak; penekan yang bukan host sesi baru ditolak; id sesi
basi ditolak 409; permintaan kedua saat yang pertama menunggu ditolak 409; Setujui menjalankan
seketika, Tolak menggugurkan, diam 30 detik menjalankan; peminta yang sudah pergi tidak dimulai
sesinya; pemegang yang menekan Akhiri selagi menunggu tidak menghasilkan 500; `selesai` sesi
lama sama dengan `mulai` sesi baru; leader tetap 403 di `PATCH /:id/selesai`.

**Deploy**: BE sebelum MyBharata (tombol web batal, lihat T3). Tanpa env baru sejak pemberitahuan
atasan ditunda, dan tanpa kategori inbox baru: cukup `marketing-analytics-service`.

**Mulai**: `jalankan /start-task Ambil alih sesi Sesi Live Host oleh host terjadwal (ADR 0088 §2)`

## ⛔ T3. Web: tombol Ambil alih + label riwayat (BATAL 2026-09-11)

Halaman web Sesi Live Host dihapus
([[ADR - 0091 Pencatatan Sesi Live Host Hanya di MyBharata, Halaman Web Dihapus]]), jadi tombol dan
label riwayat versi web tidak dibangun, dan brief `.task-plans/briefs/2026-09-11-pemegang-akun-409-web.md`
ikut tak relevan. Rincian di bawah dibiarkan sebagai catatan.

**Prasyarat**: brief `.task-plans/briefs/2026-09-11-pemegang-akun-409-web.md` (menyebut pemegang
di penolakan) sudah merged, dan T2 sudah ter-deploy.

- Tombol per akun yang bentrok di dialog Mulai (dialognya bisa memulai beberapa akun sekaligus).
- Sesudah Ambil alih ditekan: keadaan menunggu dengan hitungan mundur 30 detik, lalu hasilnya
  (berhasil, atau ditolak oleh siapa). Persetujuan pemegang tidak dari web (lihat T4).
- Konfirmasi wajib menyebut akun dan nama pemegang, karena aksinya tak bisa dibatalkan.
- Penolakan jadwal menampilkan pesan server apa adanya.
- Riwayat: "Diambil alih oleh X pukul HH:MM" dan "Ditutup otomatis: shift berakhir".
- i18n id + en, jam diformat di render dengan `intlLocale(lang)`, tanpa prop baru di komponen shared.

**Mulai**: `jalankan /start-task Tombol Ambil alih dan label riwayat Sesi Live Host di web (ADR 0088)`

## T4. MyBharata: tombol Ambil alih + label riwayat + rilis

**Status 2026-09-12**: merged ke `dev` 07:34 WIB (my-bharata #143, versi 1.17.0+161); **rilis ke host belum
diverifikasi**, dan backend PROD yang jadi prasyaratnya sudah naik 08:55 WIB. Suite `test/features/live_shift/` 311
test hijau. Brief celah 1 mobile (`.task-plans/briefs/2026-09-11-pemegang-akun-409-mybharata.md`)
dilebur ke sini, tidak dikerjakan sebagai brief terpisah. Review menghasilkan dua perbaikan: host
yang dicatat untuk ambil alih kini diambil dari pilihan co-host yang sedang tampil, dan
konfirmasi Ambil alih tidak menyebut angka detik (keputusan user; batasnya milik server).
Penyimpangan sadar dari rencana: galat Setujui/Tolak tampil di dalam jendela karena snackbar
tertutup sheet modal. Ketuk notifikasi membuka Sesi Live **tidak** dikerjakan (push ponsel
tanpa `data`, ADR 0050 §4). Rinciannya di [[APP - MyBharata]] §Sesi Live Host.

**Prasyarat**: T2 sudah ter-deploy.

Sisi **peminta** sama dengan T3: tombol, konfirmasi, keadaan menunggu dengan hitungan mundur,
label riwayat.

Sisi **pemegang**: notifikasi dan **`CustomBottomSheet` yang muncul otomatis** di halaman Sesi
Live yang sedang terbuka, berisi siapa yang meminta (nama, jadwal, akun), tombol Setujui dan
Tolak, dan hitungan mundur; tertutup sendiri saat 30 detik habis. Halaman mengetahui permintaan
lewat baca ulang berkala tiap 3 detik selama halaman terbuka dan aplikasi di depan (diputuskan
saat perencanaan). Jebakan yang sudah tercatat: `CustomBottomSheet` wajib ditutup dengan
`context` miliknya sendiri, karena `Navigator.pop` dengan context halaman menutup HALAMAN.

PR ke `dev`. Rilis menaikkan version name **dan** code (`update_version.dart` dua argumen).

**Mulai**: `jalankan /start-task Tombol Ambil alih dan label riwayat Sesi Live Host di MyBharata (ADR 0088)`

## T5. Verifikasi lapangan

Di DEV dengan dua akun host, lalu sekali di prod sesudah deploy:

1. Host A Mulai di akun X. Host B (terjadwal) menekan Mulai di akun X dari HP, melihat nama A,
   lalu menekan Ambil alih.
2. Di HP A (halaman Sesi Live terbuka) jendela persetujuan muncul sendiri dengan nama B. A menekan
   Tolak, dan B melihat "ditolak oleh A". Diulang dengan A diam: sesudah 30 detik jendelanya
   tertutup dan ambil alih berjalan.
3. Riwayat A berbunyi "Diambil alih oleh B"; `selesai` A sama dengan `mulai` B.
4. Sesudah sync TikTok, GMV terbagi per potongan waktu dan tak satu pun sesi `perlu_koreksi`.
5. Satu sesi yang dibiarkan lewat jam berakhir + 60 menit tertutup sendiri dengan alasan
   `shift_berakhir`, dan riwayat MyBharata menyebut "shift berakhir" sesudah T4, bukan "clock-out"
   (riwayat web sudah dihapus).

Lewat gateway, bukan panggilan lokal. Test hijau bukan bukti fiturnya bisa dipakai.

## T6. Dok menyertai tiap item

Tiap item yang naik memperbarui [[Microservices - Marketing Analytics Service]] (§Ambil alih &
tutup otomatis akhir shift dari 🟡 ke ✅), [[API - Marketing Analytics Service]] (rute atau
parameter baru), dan status ADR 0088.

**Status 2026-09-12**: keempat dok itu dan [[APP - MyBharata]] sudah memuat T2 dan T4 dengan
status per 2026-09-12 09:34 WIB: T2 di PROD, T4 merged ke `dev`. Yang masih harus diperbarui: rilis
MyBharata dan hasil T5.

---

## Di luar lingkup, sengaja

- **Koreksi `perlu_koreksi` lewat layar.** Tetap skrip tulis DB yang dijalankan manusia, sampai
  ada keputusan siapa berwenang menyetujui koreksi atribusi.
- **Batas keras untuk sesi tanpa jadwal** (mis. tutup paksa di jam ke-12). Butuh keputusan
  tersendiri.
- **Leader mengakhiri sesi orang lain.** Keputusan 2026-08-30 tetap.
- **Persetujuan tanpa batas waktu, dan persetujuan dari web.** Yang meninggalkan sesi justru orang
  yang tak bisa dihubungi, jadi diam berarti setuju sesudah 30 detik; jendela persetujuan hanya di
  MyBharata.
- **Pemberitahuan ke atasan host lama.** Ditunda (keputusan 2026-09-11): resolver atasan per
  karyawan belum ada.
- **Ketuk notifikasi membuka halaman Sesi Live.** Butuh `data` di push ponsel dan mengubah
  perilaku ketuk seluruh kategori (ADR 0050 §4).

## Terkait di luar papan ini (insiden 2026-09-11)

- Brief celah 1 mobile dilebur ke T4; brief celah 1 web gugur bersama T3.
- Skrip pindah toko carevolution (`.task-plans/2026-09-11-pindah-toko-carevolution.ps1`) sudah
  dijalankan 2026-09-12 08:21 WIB: 8 sesi `carevolution.hub` dipindah dari Beautyhacks.co ke Beautyhacks.store dan
  penjualannya kini terpasang ke sesi host (cadangan di `.task-plans/backup/`). Akar salah pilihnya, pemilih akun
  tanpa batas waktu (`GET /live-shifts/akun`), belum dibetulkan.
