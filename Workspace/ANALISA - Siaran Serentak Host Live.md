# ANALISA - Siaran Serentak Host Live

> Papan kerja hasil `/analisa-kebutuhan` 2026-08-30. Keputusannya di
> [[ADR - 0063 Siaran Serentak Dicatat sebagai Sesi Terpisah per Akun]], cara kerjanya di
> [[Microservices - Marketing Analytics Service]] §Siaran serentak di beberapa akun.
> Berkas ini berubah tiap item selesai; ADR dan dok domain yang jadi rujukan tetap.

## Ringkas

Host live menyiarkan serentak dari beberapa perangkat di beberapa akun, dan akunnya bisa
milik toko berbeda. Penyimpanan **sudah** mengizinkannya (index unik parsial hanya atas
`akun_live`), jadi tidak ada migrasi data dan tidak ada perubahan index. Yang dikerjakan:
menampilkan sesi paralel, membetulkan jam yang tergandakan, dan memasang rambu supaya
siaran ganda yang sah tidak dihukum seperti kesalahan input.

**Angka yang mendasari** (prod 2026-08-30): 148 pasangan sesi tumpang tindih beda akun,
seluruhnya lintas toko, 935 jam irisan, puncak 4 akun serentak. `live_shifts` **0 dokumen**.
Akun brand menyumbang Rp 942 juta, 84,8% seluruh GMV live.

## Urutan & dependensi

```
T1 (web: N sesi) ─┐
T2 (mobile: N sesi)┴─> T9 (verifikasi lapangan) ─> T10 (scope individu, HR)
T3 (BE: jam dinding) ─> T5 (FE: konsumsi jam) ─┘
T4 (BE: penanda sah) ─┘
T6, T7, T8 bebas urutan setelah T1/T2
T0 berjalan paralel, non-kode, tidak memblokir apa pun
```

⚠️ **T1 dan T2 dikerjakan lebih dulu.** Selama sesi kedua tak bisa diakhiri, mencatatnya
justru merugikan host lewat ambang 12 jam yang menolkan porsi GMV. Ini prasyarat fitur
bisa dipakai sama sekali, bukan penyempurnaan tampilan.

⚠️ **Deploy BE sebelum FE** untuk T3 dan T4 (kontrak bertambah field). T1/T2 tidak
menunggu BE karena hook web sudah mengembalikan larik dan endpoint sudah mengirim semua.

---

## T0. Bawa asumsi coverage per-brand ke HRD (non-kode, tidak memblokir)

[[ADR - 0006 Swap Jadwal Same-Department]] berdiri di atas asumsi tiap shift host live
wajib berisi 1 Beauty Hacks + 1 Kyura, "bukan satu pool interchangeable", dan ADR itu
menuliskan sendiri bahwa bila HRD menyatakan satu pool maka ia ditinjau ulang dan mungkin
**Superseded**. Satu orang memegang akun BH dan Kyura serentak adalah bukti kuat ke arah
satu pool.

**Keluaran**: jawaban HRD tercatat, lalu ADR 0006 diperbarui atau di-Superseded.
**Bukan** pekerjaan kode, dan ADR 0063 tidak bergantung padanya.

## T1. Web menampilkan SELURUH sesi berjalan milik pemanggil

Ganti pengambilan elemen pertama menjadi daftar; tiap sesi punya kartu, tombol Jeda dan
Akhiri, penghitung durasi, dan peringatan ambang sendiri.

- Hook sudah mengembalikan `LiveShift[]`, jadi tak ada perubahan permintaan jaringan.
- Props panel sesi berjalan masih bertipe tunggal, ikut berubah.
- Test yang ada mengunci bentuk tunggal, ikut diperbarui.

**Selesai bila**: dua sesi berjalan atas satu orang tampil sebagai dua kartu, dan Akhiri
pada kartu kedua benar-benar menutup sesi kedua (bukan yang pertama).

## T2. Mobile menampilkan seluruh sesi berjalan

`sesiBerjalan` berubah dari objek tunggal menjadi daftar; `milik.first` dibuang; timer
per sesi; kartu beranda merender N kartu.

⚠️ Mesin anti-balapan `_versiSesiBerjalan` dibangun untuk melindungi **satu slot**. Ia
menjawab "payload GET mana yang lebih baru", bukan "sesi mana milik siapa". Begitu slotnya
jamak, mesin itu **dirancang ulang** (versi per koleksi atau per sesi), jangan ditambal.

**Selesai bila**: dua sesi tampil, keduanya bisa dijeda dan diakhiri terpisah, dan
peringatan jam ke-11 muncul untuk masing-masing.

## T3. Jam siaran per orang dihitung sebagai union jendela waktu

Jam siaran seseorang pada suatu periode = union interval seluruh sesinya setelah jeda
dikurangi. Bukan penjumlahan `durasi_efektif_detik`.

- Hidup di **satu fungsi** yang dipakai semua permukaan. Dua salinan akan menyimpang.
- `durasi_efektif_detik` per sesi **tidak berubah artinya** dan tetap dikirim. Ia komponen
  sejajar; yang dilarang adalah menjumlahkannya lintas sesi untuk satu `employee_id`.
- Larangan itu **wajib tertulis di dekat definisi kolomnya**, karena pemanggil berikutnya
  tak punya cara lain mengetahuinya.
- Kaidahnya perluasan dari `gabungSesiKembar` yang sudah ada: rupiah dijumlah, jam tidak.

**Selesai bila**: satu orang dengan tiga sesi paralel 2 jam terbaca 2 jam, dan satu orang
dengan tiga sesi berurutan 2 jam terbaca 6 jam. Kedua arah dikunci test.

## T4. Tumpang tindih lintas akun ditandai SAH, bukan dihukum

- Deteksi yang ada (`shop_id` **dan** `akun_live` sama) **dipertahankan apa adanya**: itu
  tetap kesalahan input dan tetap menolkan porsi.
- Tumpang tindih pada **akun berbeda milik `employee_id` yang sama** mendapat penanda
  **terpisah**, dan porsinya **DILARANG dinolkan**.

⛔ Gerbang terpenting di seluruh daftar ini. Memperluas deteksi yang ada begitu saja akan
menghanguskan GMV dari praktik kerja yang sah, senyap, tepat pada bulan host bekerja
paling keras. Dua keadaan ini wajib bernama beda di data dan berwarna beda di layar.

**Selesai bila**: dua sesi paralel beda akun satu orang menghasilkan porsi GMV **penuh**
di keduanya plus penanda "siaran serentak", sementara dua shift tumpang tindih pada akun
sama tetap menolkan porsi seperti sekarang.

## T5. Frontend berhenti menggandakan jam

Dua tempat, keduanya menjumlahkan `durasi_efektif_detik` per baris tanpa dedup jendela
waktu: kartu metrik halaman host live, dan agregasi performa host di layar tim ICC.

Sekalian betulkan ketidakcocokan yang sudah ada di kartu metrik: pembilang GMV disaring
`ada_data` sementara penyebut jam tidak, sehingga GMV per jam terlalu rendah secara
sistematis. Dengan sesi paralel, jam berlipat sementara GMV tidak, jadi ia makin parah.

**Selesai bila**: GMV per jam seorang host pemegang tiga akun tidak lagi sepertiga dari
nilai sebenarnya.

## T6. Pengingat tidak terkirim berkali-kali

Dedup pengingat berpindah dari per dokumen sesi menjadi **per orang per jenis pengingat**.
Sekarang satu orang dengan dua sesi berjalan menerima dua notifikasi identik.

⚠️ Penulisan penanda memakai `$set` dari salinan lokal, aman **hanya karena penulisnya
satu**. Begitu ada penulis kedua, bentuk itu wajib diganti.

**Deploy**: bila menyentuh kategori inbox, naikkan pengirim **dan** `Notification-Service`
bersama, lalu picu satu notifikasi sungguhan sebagai bukti.

## ✅ T7. Dialog Mulai memilih beberapa akun sekaligus — SELESAI di branch, belum merged

Dikerjakan 2026-08-30 di `erp-frontend` branch `feat/live-shift-mulai-multi-akun`
(4 commit). Toko dan akun sama-sama combobox ber-search multi-pilih; satu tekan
menerbitkan N sesi. Rencana: `.task-plans/2026-08-30-live-shift-mulai-multi-akun.md`.
Cara kerjanya di [[Microservices - Marketing Analytics Service]] §Memulai beberapa akun
sekaligus.

⚠️ **Belum bisa dilihat siapa pun sampai T1 tayang**: backend T1 sudah merged tapi belum
di-deploy, dan tanpa itu penyaringan kepemilikan serta `boleh_kelola` belum berlaku.

Satu jebakan yang ditemukan saat mengerjakannya dan belum tercatat di mana pun sebelumnya:
**nama akun berulang antar toko** (`hexativ` akun teratas di tiga toko), jadi opsi akun
wajib berkunci `shop_id` + akun. Ini berlaku untuk klien mana pun, termasuk T14 nanti.

Satu tindakan menerbitkan N sesi. Kemudahan tampilan, **bukan** perubahan kontrak.

- Komponen multi-select sudah ada di kedua klien, jangan bikin baru.
- Akun berasal dari beberapa toko, jadi daftar akun tak lagi boleh disimpan sebagai satu
  daftar global yang tertimpa tiap ganti toko.
- Kegagalan sebagian (3 diminta, 2 berhasil) wajib punya perlakuan eksplisit, jangan
  dibiarkan sebagian jadi tanpa pemberitahuan.

## T8. Mobile memakai pemilih toko, bukan ketik tangan

Konstanta endpoint daftar toko **sudah ada dan nol pemakai** di repo mobile; web sudah
memakainya. Sekarang `shop_id` diketik tangan, dan salah ketik menghasilkan 200 kosong
lalu sesi tersimpan ke toko yang tak bisa dijodohkan, sehingga **GMV hilang selamanya**.
Risikonya naik begitu satu orang memakai beberapa toko sekaligus.

## T9. Verifikasi lapangan dengan host sungguhan

⛔ Fitur ini **0 dokumen di produksi** sejak live. Test hijau bukan bukti bisa dipakai.

Satu host menjalani satu shift penuh: Mulai di dua akun, Jeda salah satu, Akhiri
keduanya, lalu periksa dokumen lahir, jam dinding benar, porsi GMV muncul setelah sync,
dan pengingat datang sekali bukan dua kali. Lewat gateway, bukan panggilan lokal.

## T10. Nyalakan scope `individu` (HR, setelah T9)

Scope `individu` sudah terdaftar; menyalakannya cukup lewat template, **tanpa deploy**.

⛔ **Target di template WAJIB ikut diubah pada saat yang sama.** Angka per orang jauh
lebih kecil daripada angka tim yang selama ini dilihat; tanpa penyesuaian, seluruh host
mendadak tercatat gagal tanpa ada yang berubah pada kinerjanya.

⚠️ Lakukan di **batas periode**, karena skor yang sudah dibekukan tidak dihitung ulang
([[ADR - 0048 Skor KPI Otomatis Penuh Dibekukan Sistem]]).

---

## Sisa dari `/review` T1 (2026-08-30), belum dikerjakan

Ketiganya muncul saat review T1, tidak memblokir T1 naik, dan sengaja dipisah supaya
PR-nya tetap bisa direview. Yang KRITIS dari review itu (riwayat tak tersaring, sesi
terkunci permanen, galat Jeda/Akhiri yang senyap) sudah ditutup di dalam T1.

### T11. Normalisasi `employee_id` di titik SIMPAN, bukan titik baca

`keShiftHost` menyalin `EmployeeID` mentah; `validasiHost` hanya men-trim untuk
*menilai*, bukan menormalkan. Akibatnya nilai tersimpan bisa `" BIP-77"`. Predikat
kepemilikan men-trim sehingga orang itu tetap pemilik di `/berjalan`, tetapi filter
Mongo memakai kesetaraan eksak sehingga ia **tak terlihat** oleh audit leader
`?host=<id>`. Arahnya tidak meloloskan siapa pun ke sesi orang lain, tapi ia membuat
"definisi pemilik" punya dua bentuk.

**Selesai bila**: nilai tersimpan selalu ter-trim, dan ada test yang mengirim
employee_id ber-spasi lalu membuktikan audit `?host=` menemukannya.

### T12. Tombol Mulai tidak boleh jatuh di bawah lipatan

Tombolnya dirender SESUDAH seluruh daftar sesi. Untuk leader yang melihat sesi seluruh
tim, daftar itu bisa belasan blok. Sebelumnya kartunya selalu satu, jadi ini baru.
Kandidat: pindah ke baris aksi di `CardHeader` supaya posisinya tak bergantung panjang
daftar.

### T13. Bedakan "gagal dimuat" dari "belum ada sesi"

⚠️ **Pra-eksisting, bukan dari T1**, tetapi taruhannya naik. Halaman tak pernah membaca
`isError`; saat query gagal, panel menampilkan "Belum ada sesi berjalan" **plus tombol
Mulai**. Host yang sesinya sedang berjalan diberi tahu tidak ada, lalu ditawari memulai
sesi baru yang berakhir 409. Persis kelas galat yang komentar cabang memuat di komponen
itu sendiri larang: nol yang belum terbukti tak boleh terbaca sebagai fakta bisnis.

---

## Utang MyBharata (diminta user 2026-08-30: "nanti di mobile juga diperbaiki")

Mobile tertinggal di **tiga** hal, bukan satu. Ketiganya sudah tercatat terpisah di atas
atau di bawah; dikumpulkan di sini supaya tak ada yang lolos saat mobile digarap.

1. **T2 — menampilkan seluruh sesi berjalan.** `sesiBerjalan` masih objek tunggal dan
   bloc mengambil `milik.first`, jadi sesi kedua tak punya kartu, tak punya timer, dan
   tak punya peringatan jam ke-11. ⚠️ Mesin anti-balapan `_versiSesiBerjalan` dibangun
   untuk melindungi SATU slot; begitu slotnya jamak ia dirancang ulang, bukan ditambal.
2. **T8 — pemilih toko.** `shop_id` masih diketik tangan padahal konstanta endpoint
   daftar toko sudah ada dan nol pemakai. Salah ketik menghasilkan 200 kosong lalu sesi
   tersimpan ke toko yang tak bisa dijodohkan, dan **GMV-nya hilang selamanya**.
3. **T14 (baru) — padanan T7: memilih beberapa akun sekaligus.** Web mendapatkannya di
   T7; mobile masih satu akun per dialog. Perlu memutuskan lebih dulu apakah pola
   combobox ber-search web bisa ditiru, karena `CustomSelectBottomSheet` di mobile
   radio/single-select dan satu-satunya multi-select yang ada (`AssigneeSelectSheet`)
   tinggal di `features/task/`, bukan di `core/widgets/`.

⚠️ Urutannya: **T2 lebih dulu**. Memberi mobile kemampuan memulai banyak akun sementara
sesi keduanya tak bisa diakhiri justru memperbesar kerusakan yang T1 perbaiki di web.

---

## Di luar lingkup, sengaja

- **Pengelompokan sesi jadi "blok siaran" tersimpan.** Union jendela waktu sudah menjawab
  pertanyaan jam tanpa menyimpan fakta yang bisa menyimpang. Tunggu pemakai ketiga.
- **Perhitungan dan pembayaran insentif.** Peraturan Perusahaan diam soal insentif Host
  Live, jadi itu keputusan produk tersendiri yang butuh dasar tertulis lebih dulu.
- **`laba_kotor` per sesi.** Masih selalu 0, TBD lama, tidak disentuh di sini.
