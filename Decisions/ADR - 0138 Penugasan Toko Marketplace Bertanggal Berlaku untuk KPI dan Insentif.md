# ADR - 0138 Penugasan Toko Marketplace Bertanggal Berlaku untuk KPI dan Insentif

> **Status**: 🟡 **Diusulkan**, 2026-09-29, BELUM diputuskan dan nol kode. Pengambil keputusan: **TBD** (manajemen marketing bersama Finance dan tim IT; lihat §Pertanyaan terbuka, butir 1). Dok ini memetakan masalah, opsi, dan usulan penulis; ia tidak menetapkan apa pun sampai bagian §Decision diisi orang yang berwenang. Nomor 0138 diklaim saat push; bila sudah terpakai, geser ke nomor bebas berikutnya.

%% Status di blockquote atas supaya terbaca VAULT-INDEX.json (15 baris pertama), pola sama dengan ADR 0136 dan 0137. %%

%% Vault ini PUBLIK. Nama orang sengaja tidak ditulis; yang disebut hanya nama toko, tanggal, dan angka agregat. %%

## Untuk Manajemen

**Masalahnya dalam satu kalimat.** Data penjualan toko yang di-banned marketplace di tengah bulan **tidak hilang**, tetapi sistem hanya tahu "toko ini dipegang siapa **sekarang**", sehingga begitu pemegangnya diganti atau toko dilepas sebelum skor bulan itu dibekukan, omzet bulan itu dinilai ke orang yang salah atau lenyap dari skor, tanpa satu pun galat.

**Yang perlu diputuskan.** (1) Apakah penugasan toko ke orang dicatat **bertanggal berlaku** (mulai dan berakhir), sehingga KPI dan insentif selalu menilai toko dengan pemegang yang berlaku saat penjualan terjadi. (2) Apakah toko yang di-banned di tengah bulan **menurunkan target** pemegangnya bulan itu. (3) Siapa yang berhak menetapkan penugasan beserta tanggalnya.

**Yang tidak dijanjikan.** Pemegang toko untuk bulan-bulan yang sudah lewat tidak bisa dipulihkan sepenuhnya, karena riwayatnya memang tidak pernah dicatat (contoh nyata: toko Nawacitra, lihat §Context). Settlement dan retur susulan dari toko yang sudah berhenti disinkron tidak akan pernah datang; yang bisa dijanjikan hanyalah angkanya **ditandai** tidak lengkap, bukan dilengkapi. Sampai keputusan diambil, yang menjaga angka adalah aturan operasional (Opsi B), bukan kode.

## Deskripsi

*Usulan untuk mengubah penugasan toko marketplace ke orang (hari ini `icc_account_mappings`, satu baris tanpa tanggal yang ditimpa di tempat) menjadi penugasan bertanggal berlaku yang ditambah baris, bukan ditimpa, dan dibaca per periode oleh semua sumber KPI dan insentif yang menilai orang dari toko yang dipegangnya. Pemicunya pertanyaan bisnis tentang toko yang di-banned di tengah periode KPI; akar masalahnya ternyata atribusi, bukan kehilangan data. Enam opsi dibandingkan; usulan penulis ditandai jelas sebagai usulan.*

- **Tanggal**: 2026-09-29
- **Diukur ke**: bip-erp `origin/main` `09b0419b` (setara biner prod `bc8d37e4`) untuk temuan awal, diverifikasi ulang ke `origin/main` `eed8cf63` untuk klaim kode di dok ini; data PROD baca-saja 2026-09-29.
- **Hubungan dengan ADR lain**:
  - [[ADR - 0052 Status Sinkron per Toko]]: sumber tanggal banned (`shop_status_histories`) dan alasan sinkron berhenti; ADR ini **memakai**, tidak mengubah.
  - [[ADR - 0045 Identitas Tim Tunggal dan Peta Kepemilikan Marketing]] keputusan 3 dan 4: bila diputuskan sesuai usulan, **mengamandemen** keputusan 4 dari "satu toko satu pemegang aktif" menjadi "satu toko satu pemegang **per rentang tanggal**". Pemisahan kepemilikan divisi (`department_shops`) dari penugasan orang tetap.
  - [[ADR - 0079 Target Profit Satu Pintu di Insentif, KPI Membacanya]] §8: dua jendela realisasi (insentif vs KPI `mode=bergeser`) **tidak diubah**; karena itu Opsi D bentrok dengannya.
  - [[ADR - 0125 Insentif Profit Dibayar lewat Slip Gaji dari Snapshot yang Disetujui Finance]]: snapshot insentif mengunci **hasil** per orang, bukan pemetaan; ia tidak dibaca KPI dan tidak menjawab masalah ini sendirian (lihat Opsi D).
  - [[ADR - 0048 Skor KPI Otomatis Penuh Dibekukan Sistem]]: pembekuan skor yang jendela waktunya menentukan kapan mapping yang ditimpa berhenti merusak; Opsi C memperkuatnya.
  - [[ADR - 0086 Metrik Live Lintas Channel Digabung Satu Angka, Rincian Tetap per Channel]]: sumber `kinerja_live` memetakan toko lewat `department_shops`, yang punya kelas masalah yang sama (tanpa tanggal, hapus keras).

## Context

### Pertanyaan bisnisnya

Sepuluh toko TikTok dinonaktifkan pada 2026-08-24 sampai 2026-08-27 (sembilan otomatis pada 08-27 lewat auto-disable ADR 0052 Tahap 2, Rainbow Care manual pada 08-24). Pertanyaannya: bagaimana KPI dan insentif pemegang toko-toko itu untuk bulan Agustus, dan bulan-bulan sesudahnya?

### Datanya tidak hilang

- KPI marketing **tidak memanggil API marketplace** saat menghitung. Ia membaca salinan lokal: `mart_profit_attribution`, `transaction_orders`, `mart_live_sessions`, `mart_cs_sla_daily`, `affiliate_orders`.
- Toko yang DISABLED hanya **berhenti disinkron** (ADR 0052 keputusan 2 dan 6: "Disable ≠ Revoke"). Tak ada penghapusan order per toko; penghapusan toko hanya menyentuh dokumen toko, bukan transaksinya. Mart dibangun ulang dari `transaction_orders` dalam jendela 7 hari, jadi baris yang sudah ada tetap ada.
- Terukur PROD: order Agustus toko yang dinonaktifkan utuh, antara lain **Nawacitra 242 order** (mart Rp10,86 jt), **By efcare 101** (Rp7,9 jt), **Wistara Lumaya 23**, **BHS skinny 22**. Toko Shopee (9) dan Lazada (3) seluruhnya aktif.
- Skor yang sudah dibekukan menyimpan nilai **beserta rinciannya** di `kpi_score` (PROD: 692 dokumen periode 2026-03 sampai 2026-08, satu per karyawan per periode).

### Akar masalahnya atribusi

Pertanyaan "toko ini milik siapa" dijawab oleh koleksi yang **tidak punya tanggal berlaku**, **ditimpa di tempat**, dan **dibaca dalam keadaan saat ini**:

| Koleksi | Bentuk | Dipakai oleh |
|---|---|---|
| `icc_account_mappings` (integration) | `employee_id`, `tiktok/shopee/lazada_shop_id`, `team`, `is_active`, `notes`, `created_*`/`updated_*`; tanpa tanggal berlaku | KPI `kinerja_toko` (marketing-analytics), realisasi insentif profit dan KPI `insentif_profit` (lewat `ListIccShopOwners` di integration) |
| `department_shops` (integration) | satu toko satu departemen, tanpa tanggal, hapus keras | KPI `kinerja_live` |
| `team_shops` | `deleted_at` tanpa tanggal mulai | sudah dipensiunkan (ADR 0045), dicatat untuk kelengkapan |
| `cs_shop_mappings` | `is_active` | KPI `sla_chat_cs` |

Diverifikasi ulang di kode (`origin/main` `eed8cf63`):

- Pembaruan mapping ICC memakai `UpdateOne` dengan `$set` yang boleh mengganti `employee_id`, `employee_name`, dan id toko ketiga channel **di dokumen yang sama**; hapus adalah `DeleteOne` (hanya untuk mapping yang sudah nonaktif). Tidak ada riwayat.
- Pembaca di marketing-analytics menyaring bawaan `{"is_active": true}`; `ListIccShopOwners` di integration juga membaca `{"is_active": true}` tanpa parameter periode.
- `department_shops` dihapus lewat `DeleteOne` per `(channel, shop_id)`.
- `/kpi/kinerja-toko` membalas **400** "belum dipetakan ke toko mana pun" bila karyawan tak memegang toko (sengaja, supaya nol tidak terbaca sebagai kinerja nol).
- `/kpi/sla-chat-cs` sengaja mengembalikan **baris terbaru per channel dan toko**, tanpa periode.
- Pembekuan skor berjalan pukul 02.00 WIB (`cron.go`, `0 2 * * *`), menulis dengan `$setOnInsert`; Simpan manual (`POST /kpi`) memakai `ReplaceOne` dan menghitung ulang otomasi dengan data saat itu.

**Contoh PROD: Nawacitra.** Mapping aktif toko ini dibuat **2026-09-02**, sesudah toko dinonaktifkan. Pemegang toko untuk bulan Agustus tidak tercatat di mana pun dalam koleksi mapping; yang tersisa hanya skor beku bulan itu.

**Kandidat banned yang tak terdeteksi.** Care Space Skin (TikTok) punya order terakhir 2026-09-03, **tidak** DISABLED, dan mapping ICC-nya aktif. Tanda banned hanya ada bila sinkron gagal auth lima run beruntun; toko yang berhenti berjualan tanpa galat auth tidak pernah ditandai.

### Preseden bertanggal yang sudah ada di kode

- `kpi_template_assignment.berlaku_mulai` (employee-service): penetapan template dibaca dengan `berlaku_mulai <= periode`, terbaru menang, dengan indeks `(employee_id, berlaku_mulai desc)`.
- `incentive_org.berlaku_dari` / `berlaku_sampai` (insentive-service, `GET /profit/org`): baris berlaku bila `berlaku_dari <= periode` dan `berlaku_sampai` kosong atau `>= periode`, dengan komentar kode "supaya rotasi orang tidak mengubah periode lampau".

Keduanya berbutir **bulan** (`YYYY-MM`). Penugasan toko butuh pertimbangan butir **tanggal** (lihat Opsi A).

### Sumber KPI yang menilai orang dari toko

| Sumber | Cara | Jendela | Pemetaan toko |
|---|---|---|---|
| `kinerja_toko` | HTTP ke marketing-analytics `/kpi/kinerja-toko`, mart level toko | bulan kalender (batas UTC) | ICC aktif, keadaan sekarang; 400 bila tak punya toko, jadi `gagal_sumber` |
| `insentif_profit` | insentive `/profit-dashboard` `mode=bergeser`, order lokal integration | `shipped_at`, cutoff tanggal 25 bulan berikutnya | ICC aktif, keadaan sekarang |
| `kinerja_live` | `mart_live_sessions` | `start_time` dalam bulan | `department_shops`, hapus keras |
| `sla_chat_cs` | baris terbaru per toko | tanpa periode | `cs_shop_mappings` |
| `kinerja_affiliate(_tim)` | `affiliate_orders` | bulan | akun affiliate aktif (di luar cakupan ADR ini) |

### Titik rawan

1. **Mapping dilepas sebelum tanggal 1 bulan berikutnya pukul 02.00 WIB**: toko hilang dari skor bulan banned, senyap. Penyebut cakupan ("N dari M toko berdata") ikut mengecil, sehingga cakupan tampak tetap penuh.
2. **`employee_id` pada mapping diganti (PATCH)**: omzet periode yang belum beku pindah ke orang baru, dan hilang dari pemegang lama.
3. **Seluruh toko seseorang dilepas**: `/kpi/kinerja-toko` membalas 400, sumber `gagal_sumber`, pembekuan otomatis tidak terjadi, dan percobaan ulang cron hanya berlaku selama periode itu masih "bulan lalu".
4. **Settlement dan retur susulan** atas order sebelum banned tidak pernah datang karena sinkron berhenti: profit tampak lebih kecil (biaya belum terpotong atau pendapatan belum masuk, tergantung arah) dan persentase retur tampak lebih baik. Di mode insentif order yang belum final **hangus**; di mode bergeser (KPI) ia **digeser** ke periode berikutnya lalu tak pernah tiba.
5. **`sla_chat_cs`** memakai baris terakhir sebelum banned untuk selamanya.
6. **Simpan manual periode lampau** sesudah mapping berubah menimpa snapshot yang benar dengan hitungan atas pemetaan baru (PROD: 82 dokumen `kpi_score` disunting manual sampai 25 sampai 27 hari sesudah periodenya).
7. **Lazada tidak punya status DISABLED** (`IsValidShopStateChannel` hanya mengenal `shopee` dan `tiktok`), jadi toko Lazada yang banned tak punya tanggal banned yang bisa dirujuk.

Tambahan: snapshot insentif (ADR 0125, bekukan periode) **tidak dibaca KPI**, jadi keberadaannya tidak menutup satu pun titik di atas untuk skor KPI.

## Opsi

### Opsi A: penugasan bertanggal berlaku, ditambah baris, dibaca per periode (akar)

1. **Bentuk.** Tiap penugasan orang ke toko menjadi baris dengan `berlaku_mulai` dan `berlaku_sampai` (kosong = masih berlaku), pola tambah-baris seperti `kpi_template_assignment` dan `incentive_org`. Mengganti pemegang = menutup baris lama (`berlaku_sampai`) dan membuka baris baru; **tak ada lagi penimpaan `employee_id` di tempat** dan tak ada hapus keras untuk baris yang pernah berlaku. Salah ketik dikoreksi dengan baris koreksi beralasan, bukan dengan menyunting riwayat.
2. **Invarian.** Untuk satu `(channel, shop_id)`, rentang tidak boleh tumpang-tindih (satu pemegang pada satu saat, sejalan ADR 0045 keputusan 4). Indeks unik per channel atas mapping aktif hari ini diganti penjaga non-tumpang-tindih di jalur tulis.
3. **Butir waktu.** Usulan: **tanggal**, bukan bulan, karena toko berpindah dan di-banned di tengah bulan, dan agregat mart sudah per toko per hari. Batas hari mengikuti batas yang dipakai pembacanya; hari ini `kinerja_toko` memakai bulan kalender dengan batas UTC sementara aturan lain di ERP ber-WIB, dan keduanya wajib disamakan saat `/plan`, bukan ditebak.
4. **Semua pembaca menerima periode.** marketing-analytics (`kinerja_toko`, dan `kinerja_live` bila `department_shops` ikut), integration `ListIccShopOwners` (dan dengan itu insentif profit serta KPI `insentif_profit`), dan pemetaan CS untuk SLA. Tak ada pembaca yang menilai periode lampau dengan keadaan saat ini.
5. **Satu jalur resolusi per service.** Aturan "baris berlaku pada tanggal t" ditulis sekali (predikat atau pembangun filter murni di pustaka bersama, karena marketing-analytics membaca `integration_db` langsung), dan tiap service punya satu fungsi resolusi pemegang per periode yang memakainya. Pembaca yang menyaring `is_active` saja dilarang lewat pemindai (lihat §Penjaga).
6. **Atribusi per penjualan.** Order dinilai ke pemegang yang berlaku pada tanggal order (atau tanggal yang dipakai jendela sumbernya: `shipped_at` untuk insentif, tanggal mart untuk `kinerja_toko`). Toko yang berpindah di tengah bulan dibagi di tanggal perpindahan.

- **Konsekuensi**: titik rawan 1, 2, 3, dan 6 tertutup di akarnya: melepas atau mengganti pemegang tidak lagi mengubah periode yang sudah lewat, dan Simpan manual periode lampau menghitung dengan pemegang yang berlaku saat itu. Pertanyaan "toko ini dipegang siapa bulan Juli" punya jawaban.
- **Ongkos**: sedang sampai besar. Skema dan jalur tulis ICC Management (layar juga berubah: tanggal mulai dan akhir), migrasi data, dan perubahan di tiga service pembaca (integration, marketing-analytics, insentive lewat integration), beserta test per periode.
- **Risiko**: pembaca yang lupa dipindah tetap membaca keadaan sekarang tanpa gejala; karena itu pemindai wajib. Riwayat sebelum migrasi tidak bisa direkonstruksi sepenuhnya. Layar menjadi lebih rumit bagi yang mengisi (tanggal wajib), dan tanggal yang diketik salah menjadi sumber galat baru; mitigasinya bawaan tanggal hari ini dan tanggal banned diambil sistem (lihat §Aturan toko banned).

### Opsi B: aturan operasional sementara

Tertulis dan disosialisasikan ke pengisi ICC Management: **mapping toko yang di-banned atau berpindah tidak dilepas dan `employee_id`-nya tidak diganti sebelum skor bulan itu beku** (tanggal 1 bulan berikutnya pukul 02.00 WIB untuk KPI; untuk insentif, sesudah snapshot periode itu dibekukan Finance, yang jatuh sesudah tanggal 25 bulan berikutnya). Pemegang baru untuk toko yang sama dicatat sesudah itu.

- **Konsekuensi**: menutup titik 1 dan 2 untuk kasus ke depan, tanpa kode.
- **Ongkos**: nol kode; beban disiplin pada pengisi.
- **Risiko**: disiplin tanpa penjaga (ingatan tim: 18 commit langsung ke branch utama sebelum ada yang menyadari). Tidak menolong pemindahan tengah bulan (pemegang baru harus menunggu hampir sebulan, atau omzetnya tercatat ke pemegang lama). Dua jadwal beku (KPI dan insentif) berbeda, jadi aturannya harus memakai yang **terakhir** dari keduanya. Tidak menutup titik 4, 5, 6, 7.

### Opsi C: kunci Simpan pada periode beku, percobaan ulang cron diperpanjang

`POST /kpi` menolak (atau menuntut alasan dan izin khusus) penyimpanan ulang skor otomatis untuk periode yang sudah beku; cron finalisasi mencoba ulang periode yang gagal lebih lama dari "bulan lalu" saja, dengan batas dan sinyal.

- **Konsekuensi**: titik 6 tertutup (snapshot benar tak tertimpa hitungan atas pemetaan baru) dan titik 3 berkurang (periode yang sempat `gagal_sumber` masih bisa beku sesudah pemetaan dibetulkan).
- **Ongkos**: kecil, di employee-service saja.
- **Risiko**: tidak menyentuh akar; hitungan yang pertama kali beku masih bisa salah bila mapping sudah bergeser sebelum tanggal 1. Mengunci Simpan menghilangkan jalan koreksi yang hari ini dipakai (82 dokumen disunting manual), jadi butuh jalan koreksi beralasan sebagai gantinya.

### Opsi D: KPI membaca snapshot insentif

Sumber `insentif_profit` membaca realisasi dari snapshot insentif yang sudah dibekukan Finance (ADR 0125), bukan dari hitungan langsung.

- **Konsekuensi**: realisasi profit KPI terkunci pada pemetaan saat snapshot dibuat.
- **Ongkos**: kecil sampai sedang.
- **Risiko**: **bentrok dengan [[ADR - 0079 Target Profit Satu Pintu di Insentif, KPI Membacanya]] §8**: KPI sengaja memakai `mode=bergeser` sementara insentif memakai jendela dengan order belum final hangus; membaca snapshot berarti menyatukan realisasi, yang ADR itu tolak. Snapshot dibuat sesudah tanggal 25 bulan berikutnya, sedangkan KPI beku tanggal 1, jadi urutan waktunya terbalik. Hanya menutup satu sumber (`insentif_profit`); `kinerja_toko`, `kinerja_live`, dan `sla_chat_cs` tetap terbuka. Snapshot sendiri dihitung dengan pemetaan saat dibekukan, jadi titik 1 dan 2 berpindah tempat, tidak hilang.

### Opsi E: SLA CS berperiode

`/kpi/sla-chat-cs` menerima periode dan mengembalikan baris terakhir **dalam** periode itu (atau baris terakhir sebelum toko DISABLED), bukan baris terbaru sepanjang masa.

- **Konsekuensi**: titik 5 tertutup.
- **Ongkos**: kecil, satu endpoint dan satu sumber.
- **Risiko**: komentar kode menyatakan pengambilan baris terbaru disengaja karena `mart_cs_sla_daily` berisi rata-rata bergulir 30 hari; memilih baris per periode harus menjaga alasan itu (baris terakhir dalam periode, bukan rata-rata ulang). Independen dari opsi lain; bisa dipasang bersama A.

### Opsi F: snapshot mapping per periode

Tiap awal atau akhir periode, keadaan mapping disalin ke koleksi snapshot per periode, dan pembaca periode lampau membaca snapshot itu.

- **Konsekuensi**: periode lampau kebal terhadap penimpaan sesudah snapshot dibuat.
- **Ongkos**: kecil sampai sedang.
- **Risiko**: **sumber kebenaran kedua** untuk fakta yang sama (ingatan tim, satu fakta satu tempat); kapan snapshot diambil menjadi keputusan baru yang bisa salah. Perubahan **di tengah bulan** tidak tertangkap: snapshot hanya tahu satu pemegang per periode, jadi toko yang berpindah tanggal 15 tetap dinilai seluruhnya ke salah satu pihak. Snapshot yang diambil sesudah penimpaan menyimpan keadaan yang sudah salah.

### Ringkasan pembanding

| Titik rawan | A | B | C | D | E | F |
|---|---|---|---|---|---|---|
| 1. dilepas sebelum beku | ya | ya (disiplin) | tidak | sebagian (profit saja) | tidak | sebagian |
| 2. `employee_id` diganti | ya | ya (disiplin) | tidak | sebagian | tidak | sebagian |
| 3. semua toko dilepas, 400 | ya | ya (disiplin) | berkurang | tidak | tidak | ya |
| 4. settlement susulan | tidak (lihat §Settlement) | tidak | tidak | tidak | tidak | tidak |
| 5. SLA baris terakhir | tidak | tidak | tidak | tidak | ya | tidak |
| 6. Simpan menimpa snapshot | ya (hitung ulang benar) | tidak | ya | tidak | tidak | ya |
| 7. Lazada tanpa DISABLED | tidak | tidak | tidak | tidak | tidak | tidak |
| Pindah di tengah bulan | ya | tidak | tidak | tidak | tidak | tidak |
| Fakta ganda baru | tidak | tidak | tidak | tidak | tidak | ya |

## Aturan untuk toko banned (berlaku bila Opsi A dipilih)

1. **Tanggal banned diambil sistem, bukan diketik.** Sumbernya `shop_status_histories` (transisi ke DISABLED, beserta aktor dan alasan) milik integration (ADR 0052). Perlu dicatat: tanggal DISABLED **sama atau lebih lambat** dari tanggal banned sesungguhnya, karena auto-disable menunggu lima run gagal beruntun. Untuk atribusi selisih itu tidak berarti banyak (toko yang benar-benar banned tidak menghasilkan order baru), tetapi layar tidak boleh menyebutnya "tanggal banned" tanpa keterangan.
2. **Penugasan tidak dilepas, cukup berakhir.** Toko banned tidak dihapus dari penugasan dan `employee_id`-nya tidak diganti. Bila perlu, baris penugasannya diberi `berlaku_sampai`; usulan penulis: **tidak otomatis** diberi tanggal akhir saat DISABLED, karena toko bisa menang banding dan di-enable lagi (ADR 0052 keputusan 6).
3. **Bulan banned tetap dinilai** dengan penugasan yang berlaku saat penjualan terjadi: order Agustus Nawacitra tetap milik pemegang Agustus, apa pun yang terjadi pada mapping sesudahnya.
4. **Cakupan "N dari M toko berdata"** melaporkan toko banned secara terpisah, bukan melebur ke N atau M:
   - toko yang DISABLED **sebelum** periode dimulai dan tetap DISABLED sepanjang periode: **tidak** masuk M, tetapi tercantum di rincian sebagai "nonaktif sejak <tanggal>, tak dinilai";
   - toko yang DISABLED **di dalam** periode: masuk M dan N sesuai datanya, dengan keterangan "nonaktif sejak <tanggal>";
   - toko yang tidak DISABLED tetapi tak punya data (kasus Care Space Skin): tetap masuk M sebagai toko tanpa data. Menyembunyikannya justru menghapus satu-satunya tanda bahwa toko itu mungkin banned tanpa terdeteksi.
5. **Lazada**: sampai `IsValidShopStateChannel` mengenal Lazada, toko Lazada tak punya tanggal banned sistem. Perlakuannya pertanyaan terbuka (lihat butir 5 di bawah).

## Settlement dan retur susulan (pertanyaan terbuka)

Order yang terjadi sebelum banned bisa masih menunggu settlement, escrow, atau retur saat sinkron berhenti. Data susulan itu **tidak akan datang**. Tidak ada opsi di atas yang bisa melengkapinya; yang bisa dipilih hanya bagaimana kekurangannya **dinyatakan**.

Usulan penulis untuk dibahas, bukan keputusan:

- Periode yang memuat toko DISABLED di dalam jendela sumbernya (untuk insentif termasuk jendela sampai cutoff tanggal 25 bulan berikutnya) diberi **penanda** "data pasca-nonaktif tidak lengkap: N order belum settle", di rincian KPI dan di baris dashboard insentif, bukan dibiarkan diam-diam kurang.
- Order yang belum final saat toko DISABLED tidak digeser tanpa batas di mode bergeser (KPI); ia dilaporkan sebagai "tak akan final" pada periode tempat ia seharusnya jatuh.
- Pertanyaan yang belum dijawab: apakah order seperti itu dikecualikan dari realisasi, dihitung dengan nilai sementara, atau dibiarkan hangus seperti aturan insentif hari ini; dan siapa yang memutuskan (Finance untuk insentif, pemilik KPI marketing untuk skor).

## Pertanyaan terbuka untuk manajemen dan marketing

1. **Siapa yang berhak menetapkan penugasan toko beserta tanggal berlakunya?** Hari ini ICC Management diisi marketing leader. Apakah tanggal mulai dan akhir boleh diisi mundur (backdate), dan bila ya, sampai berapa jauh dan dengan persetujuan siapa? Backdate yang menyentuh periode yang sudah beku harus punya jalan koreksi beralasan, bukan penimpaan diam-diam.
2. **Apakah toko yang di-banned di tengah bulan menurunkan target pemegangnya bulan itu?** Pilihannya: target tetap (risiko banned ditanggung pemegang), target **prorata** menurut hari toko aktif (menuntut rumus target per toko, yang hari ini tidak ada karena target profit per orang, ADR 0079), atau diputus per kasus oleh SPV lewat Master Target insentif. Perlu dicatat: target profit hanya diketik di satu tempat (ADR 0079), jadi apa pun jawabannya, penurunannya ditulis di sana, bukan di KPI.
3. **Apakah toko banned yang sudah lewat periodenya diberi tanggal akhir penugasan**, atau dibiarkan menggantung menunggu banding?
4. **Settlement susulan**: dikecualikan, dihitung sementara, atau hangus (§Settlement)?
5. **Lazada**: apakah status DISABLED diperluas ke Lazada (menuntut perubahan di integration dan deteksi galat auth Lazada), atau toko Lazada yang banned ditandai manual dengan alasan wajib?
6. **Rekonstruksi riwayat**: apakah pemegang toko untuk periode yang sudah lewat perlu dipulihkan (dari rincian skor beku, dari catatan tim), atau diterima sebagai "tidak diketahui sebelum tanggal migrasi"?

## Rekomendasi penulis (USULAN, bukan keputusan)

1. **Opsi B sekarang**, sebagai aturan tertulis ke pengisi ICC Management sampai A di kode: jangan lepas mapping dan jangan ganti `employee_id` toko yang banned atau berpindah sebelum skor KPI dan snapshot insentif periode itu beku.
2. **Opsi A sebagai perbaikan permanen**, dengan butir tanggal, `icc_account_mappings` lebih dulu (dua sumber berbobot uang: `kinerja_toko` dan `insentif_profit`), lalu `department_shops` dan pemetaan CS dengan pola yang sama.
3. **Opsi C sebagai pendamping**, karena murah dan menutup titik 6 terlepas dari A; jalan koreksi beralasan disediakan bersamaan.
4. **Opsi E** dipasang bila `sla_chat_cs` dipakai menilai toko yang bisa banned; ia independen dan kecil.
5. **Opsi D dan F ditolak**: D bentrok dengan ADR 0079 §8 dan hanya menutup satu sumber; F melahirkan fakta ganda dan buta terhadap perpindahan tengah bulan.

Alasannya: masalahnya ada di bentuk data penugasan, dan dua preseden bertanggal (`kpi_template_assignment`, `incentive_org`) sudah membuktikan polanya di service yang sama-sama membaca penugasan per periode. Kelemahan usulan ini: A menyentuh tiga service dan layar pengisi, dan riwayat sebelum migrasi tetap tidak lengkap.

## Decision

**TBD.** Diisi setelah §Pertanyaan terbuka dijawab dan pengambil keputusan ditetapkan. Sampai saat itu dok ini tidak boleh dikutip sebagai keputusan. Yang **dapat berlaku tanpa menunggu** (bila disetujui pemilik ICC Management): aturan operasional Opsi B.

## Langkah sesudah diputuskan (daftar task kasar)

Urutan mengikuti usulan penulis; disesuaikan bila opsi lain dipilih.

1. **Ukur dulu** (baca-saja, PROD): jumlah mapping ICC yang pernah diganti `employee_id` atau id tokonya (hanya bisa diperkirakan dari `updated_at` lebih baru dari `created_at`, karena isi lamanya tidak tersimpan), jumlah toko DISABLED per channel beserta tanggalnya, dan untuk tiap periode yang sudah beku apakah rincian `kpi_score` menyebut toko per orang sehingga bisa menjadi bahan rekonstruksi. Tanpa angka ini ongkos migrasi hanya tebakan.
2. **Migrasi**: tiap baris mapping yang ada menjadi baris penugasan dengan `berlaku_mulai = created_at`, atau awal periode tertua yang belum beku bila `created_at` lebih baru (keputusan dipilih di `/plan`, bukan diasumsikan). Riwayat sebelum itu **diakui TBD**: kasus seperti Nawacitra (mapping dibuat sesudah toko banned) tidak bisa dipulihkan dari koleksi mapping. Migrasi mengikuti kerangka dua fase: dry run, cadangan, dijalankan manusia di PROD.
3. **Jalur tulis ICC Management**: ganti pemegang = tutup baris + buka baris; hapus keras hanya untuk baris yang tidak pernah berlaku; penjaga non-tumpang-tindih; layar menampilkan riwayat penugasan per toko.
4. **Pembaca**: predikat "berlaku pada tanggal t" di satu tempat; `ListIccShopOwners` dan pembaca marketing-analytics menerima periode dan membagi toko yang berpindah di tengah periode.
5. **Toko banned**: rincian cakupan membaca tanggal DISABLED dari `shop_status_histories`; penanda data pasca-nonaktif sesuai jawaban §Settlement.
6. **`department_shops` dan pemetaan CS** dengan pola yang sama, sesudah butir 3 dan 4 terbukti.
7. **Sinkron dok**: [[REF - Kepemilikan Data]] (baris pemegang toko aktif dan toko per divisi), [[Sales - ICC Account Manager Mapping]], [[Microservices - Integration Service]], [[Microservices - Marketing Analytics Service]], [[HRIS - Otomasi Skor KPI]], dan amandemen keputusan 4 di ADR 0045.

## Penjaga yang dibutuhkan

- **Test per periode dengan mapping berganti di tengah bulan.** Fixture: satu toko, pemegang X sampai tanggal 15, pemegang Y mulai tanggal 16, order di kedua sisi. Assertion: skor X hanya memuat order sampai tanggal 15, skor Y hanya sesudahnya, dan skor bulan sebelumnya tidak berubah sesudah penugasan baru ditulis. **Fixture wajib memakai `employee_id` dan tanggal yang berbeda** di kedua sisi; fixture yang menyamakannya lulus untuk implementasi yang salah.
- **Kontrol negatif** untuk test itu: kembalikan sebentar pembaca ke `{"is_active": true}` tanpa periode dan pastikan test merah pada assertion atribusi yang diklaimnya, bukan karena sebab lain.
- **Test toko banned**: toko DISABLED di tengah periode tetap dinilai ke pemegangnya untuk order sebelum tanggal DISABLED, dan tercantum di rincian dengan tanggalnya; toko DISABLED sepanjang periode tidak masuk penyebut cakupan tetapi tercantum.
- **Pemindai sumber**: menolak pembacaan koleksi penugasan toko yang tidak melewati fungsi resolusi berperiode (daftar-izin per berkas yang hanya boleh menyusut). Nama koleksi ditulis literal di argumen, supaya pemindai tidak lulus tanpa memeriksa (ingatan tim, kelas penjaga soft-delete yang lumpuh oleh konstanta). Kontrol negatif: tambahkan satu pembaca `is_active` saja di berkas baru dan pastikan pemindai merah.
- **Test jalur tulis**: penggantian pemegang tidak pernah menjalankan `$set` atas `employee_id` baris yang pernah berlaku; rentang tumpang-tindih ditolak dengan pesan yang menyebut sebabnya.
- **Test kontrak lintas service**: bentuk respons berperiode yang dikonsumsi insentive dan employee-service diuji dari rekaman respons sungguhan, bukan struct tiruan.

## Dokumen Terkait

- [[REF - Kepemilikan Data]] · [[Sales - ICC Account Manager Mapping]] · [[REF - Penamaan Metrik & Sumber KPI]]
- [[ADR - 0052 Status Sinkron per Toko]] · [[ADR - 0045 Identitas Tim Tunggal dan Peta Kepemilikan Marketing]] · [[ADR - 0079 Target Profit Satu Pintu di Insentif, KPI Membacanya]] · [[ADR - 0125 Insentif Profit Dibayar lewat Slip Gaji dari Snapshot yang Disetujui Finance]] · [[ADR - 0048 Skor KPI Otomatis Penuh Dibekukan Sistem]] · [[ADR - 0086 Metrik Live Lintas Channel Digabung Satu Angka, Rincian Tetap per Channel]]
- [[Microservices - Integration Service]] · [[Microservices - Marketing Analytics Service]] · [[Microservices - Insentive Service]] · [[Finance - Incentive]]
- [[HRIS - Otomasi Skor KPI]] · [[HRIS - Alur KPI Otomatis]]
