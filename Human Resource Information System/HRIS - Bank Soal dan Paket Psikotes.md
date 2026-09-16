## Deskripsi

*Cara kerja psikotes **multi-jenis**: katalog tipe tes, bank soal, dan paket tes yang dikelola HRD sendiri, dijalankan oleh tiga mesin penilaian yang tetap berupa kode. Keputusan dan alasannya ada di [[ADR - 0087 Katalog Tipe Psikotes Jadi Master Data, Tiga Bentuk Jawaban Tetap Kode]]; dokumen ini menyimpan cara kerjanya. Rincian mesin Kraepelin (skoring, konfigurasi, sesi lama) tetap di [[HRIS - Psikotes Kraepelin]].*

- **Status**: ⚠️ **Implemented (ada catatan)**: T1 sampai T6 dikodekan dan **merged 2026-09-11** (bip-erp #1837 `40323aae` dan #1838 `b73862af`, erp-frontend #1527 `42eccaf8`, career-bharata #10 `15240242`). Terverifikasi di DEV hari itu lewat gateway dan sebagai HR serta kandidat di Chrome (recruitment-service dan api-gateway dinaikkan dari branch; career portal dijalankan lokal terhadap gateway dev). Prod belum. Status ini bergerak, ukur ulang sebelum mengandalkannya. Papan kerja: `Workspace/ANALISA - Psikotes Multi-Jenis.md`
- **Revisi layar kandidat** (tahap tanpa nama tes, soal contoh wajib, boleh kembali, sapaan berdetail): **merged 2026-09-11** (bip-erp #1850 `9bdded4a`, erp-frontend #1541 `428d41b0`, career-bharata #11 `441cf713`; diperiksa ke GitHub 2026-09-15). Teks bertanda *(revisi)* di bawah kini berlaku di `main`; status prod-nya tidak diukur di sini.
- **DISC tanpa kunci skor** (keputusan user 2026-09-15: kunci skor DISC tidak dimuat ke sistem, HR menilai DISC sendiri dari layar): **merged 2026-09-15** (bip-erp #1900 `1683de56`, erp-frontend #1589 `bb3a6117`). Terverifikasi di DEV hari itu lewat gateway dan layar HR dengan backend sungguhan; 24 grup DISC tanpa kunci dimuat ke bank dev. Status prod belum diukur di sini. Teks bertanda *(tanpa kunci)* di bawah kini berlaku di `main`. Keputusan dan penyimpangannya: [[ADR - 0087 Katalog Tipe Psikotes Jadi Master Data, Tiga Bentuk Jawaban Tetap Kode]] butir (9).
- *(internal)* **Bank CFIT diisi soal internal, bukan butir berlisensi** (keputusan user 2026-09-15: HRD tidak punya bahan CFIT, jadi soalnya dibuat agent). 50 soal penalaran gambar orisinal + 2 soal contoh per subtes **dimuat ke DEV 2026-09-16** lewat gateway, dan tipe berkode `cfit` di DEV berganti nama jadi "Penalaran Gambar (internal)". **Tanpa perubahan kode repo**: yang berubah data katalog dan bank soal. Prod belum, dijalankan manusia. Cara kerjanya di §Bank Penalaran Gambar (internal); keputusannya butir (10) di [[ADR - 0087 Katalog Tipe Psikotes Jadi Master Data, Tiga Bentuk Jawaban Tetap Kode]].
- **Sisi implementasi**: [[Microservices - Recruitment Service]] (`services/recruitment/models_psikotes_katalog.go`, `psikotes_katalog_*.go`, `psikotes_paket_*.go`, `psikotes_impor.go`, `seed_psikotes.go`) · [[CORE - API Master Gateway]] (rute publik kandidat) · [[APP - Web ERP]] (layar HR) · [[APP - Portal Karir Bharata]] (layar kandidat). Endpoint: [[API - Recruitment Service]]
- **Dibangun di atas asumsi tertulis** atas keputusan HRD yang belum ada (dipilih user 2026-09-11 supaya fitur siap dipakai): isi soal CFIT dan DISC berlisensi tanggung jawab HRD, jadi **tidak ada butir soal yang di-seed**; mesin kandidat baru hanya di career portal; CFIT boleh dikerjakan jarak jauh dengan batas waktu ditegakkan server. Ketiganya tetap menunggu konfirmasi HRD (§Belum Diputuskan).

## Latar Belakang

CFIT dan DISC masih dikerjakan kandidat **di kertas** lalu **dikoreksi HR dengan tangan**, dan bebannya menumpuk musiman saat lowongan dibuka. Kraepelin sudah online sejak 2026-09-09 tetapi berdiri sendiri. Yang diminta manajemen adalah tiga menu; yang dibutuhkan adalah berhentinya koreksi manual. Pembedaan itu, beserta akibatnya pada urutan kerja, dicatat di ADR 0087 `## Context`. *(tanpa kunci)* Untuk DISC koreksi manual tidak hilang: tanpa kunci skor di sistem, HR tetap menilai DISC sendiri, hanya pindah dari lembar kertas ke lembar jawaban di layar. CFIT tetap dinilai sistem.

## Ruang Lingkup

**Masuk:** katalog tipe tes, bank soal per tipe (manual dan impor Excel, soal dan opsi bergambar), paket tes berurutan, sesi multi-bagian untuk kandidat, tiga mesin penilaian, dan laporan hasil per bagian.

**Tidak masuk:** konversi skor ke IQ, norma, atau profil DISC; kesimpulan otomatis; keputusan lolos atau gugur; EPPS; notifikasi "hasil siap" ke HR; tenggat tautan; drag-and-drop; pembatasan paket per posisi atau per HR.

## Persona / Pengguna

| Persona | Peran & Divisi | Akses/RBAC | Device |
|---|---|---|---|
| HR rekrutmen | Staff atau Supervisor HRD | Baca katalog `PermRecruitmentView`; sunting katalog **dan membaca daftar soal** `PermRecruitmentWork` (daftar soal memuat kunci). Saat penegakan izin mati, keduanya jatuh ke peran HRIS (`isHR`) | Laptop |
| Kandidat | Pelamar, tanpa akun ERP | Token acak di tautan email | Ponsel atau laptop |

- **Tujuan**: HR menyusun tes tanpa developer dan membaca hasil tanpa mengoreksi; kandidat mengerjakan seluruh paket dari satu tautan.
- **Pain point**: lembar CFIT dan DISC dikoreksi tangan; menambah atau mengubah tes menuntut developer.
- **Aksi utama**: HR menyiapkan tipe, soal, dan paket sekali; mengirim paket per kandidat; membaca laporan per bagian. Kandidat mengerjakan bagian demi bagian.

## Tiga Bentuk Jawaban

`jenis_jawaban` adalah **kontrak antara katalog dan mesin**, daftar-izin tertutup yang dijaga kode. Tipe dengan nilai lain **ditolak saat disimpan** (400), bukan gagal saat kandidat mengerjakannya. Menambah bentuk keempat wajib lewat ADR baru.

| `jenis_jawaban` | Bentuk soal | Yang dihitung | Timer | Dipakai |
|---|---|---|---|---|
| `pilihan_ganda` | Pertanyaan teks dan/atau gambar; 2 sampai 6 opsi teks dan/atau gambar; **1 atau 2 kunci per soal**, ditentukan `jumlah_jawaban` subtes | Benar per subtes. Soal berkunci dua benar hanya bila kedua pilihan tepat; urutan klik tak menentukan | Per subtes, ditegakkan server | CFIT (Klasifikasi memilih 2) |
| `most_least` | Satu grup tepat 4 kata; tiap kata punya dimensi untuk Most dan untuk Least: D, I, S, C, atau N (tidak dihitung). *(tanpa kunci)* Atau kedelapan huruf grup kosong: grup tanpa kunci | Tally Most, Least, dan Change (Most dikurangi Least). N ikut dicatat tapi tak pernah masuk Change. Tanpa benar/salah. *(tanpa kunci)* Tally hanya bermakna bila `skor_otomatis`; laporan juga membawa lembar jawaban | Bawaan tanpa timer (kandidat melihat anjuran waktu); HR boleh memasang timer | DISC |
| `angka_kolom` | Deret digit per kolom, dibuat otomatis per kandidat | Metrik Kraepelin | Per kolom | Kraepelin |

⚠️ Dua hal di atas **menyimpang sadar** dari teks ADR 0087, yang menulis "satu kunci benar" dan DISC "untimed": Klasifikasi CFIT asli memilih dua jawaban, dan timer DISC dibiarkan sebagai pilihan HR dengan bawaan tanpa timer.

⚠️ *(tanpa kunci)* Penyimpangan berikutnya (ADR 0087 butir 9): huruf dimensi `most_least` boleh kosong untuk SELURUH grup. Kosong BUKAN N: N berarti kunci menyatakan kata itu tak dihitung, kosong berarti kuncinya tidak ada di sistem. Grup setengah berhuruf ditolak `400`.

## Model Data

Koleksi baru di `recruitment_db`, pemiliknya recruitment ([[REF - Kepemilikan Data]]).

**`psikotes_tipe`**: `kode` (dibuat server, unik, stabil seumur tipe; seed mengenali tipe bawaannya lewat kode) · `nama` (maks 60) · `deskripsi` (maks 500; *(revisi)* berlabel **catatan internal HR** dan tak pernah dikirim ke kandidat) · *(revisi)* `penjelasan_kandidat` (maks 300; satu-satunya teks tipe yang sampai ke kandidat, yang hanya melihat "Tahap N") · `jenis_jawaban` · `punya_subtes` · `subtes[]` · `pakai_timer` · `anjuran` (maks 60) · `kraepelin` {`columns`, `rows`, `seconds`} · `status` `active`/`inactive`.
Tiap subtes: `kode` (rujukan soal; mengganti nama subtes tak memutus soalnya) · `nama` · `petunjuk` (maks 1000) · `jumlah_soal` (0 sampai 200; **0 = pakai semua soal aktif**) · `durasi_detik` (30 detik sampai 2 jam bila bertimer) · `jumlah_jawaban` (1 atau 2, hanya pilihan ganda). Pilihan ganda 1 sampai 4 subtes; `most_least` tepat satu subtes tersirat; `angka_kolom` tanpa subtes.
**Total waktu diturunkan server** (`total_durasi_detik`), tidak diketik: Kraepelin kolom × detik; tipe tanpa timer 0; selain itu jumlah durasi subtes.

**`psikotes_item`** (bank soal): `tipe_id` · `subtes_kode` · `urutan` · `pertanyaan` (maks 2000) · `gambar` (kunci objek, bukan path) · `opsi[]` {`teks` maks 300, `gambar`} · `kunci[]` (indeks opsi) · `kata[]` {`teks` maks 80, `most`, `least`; *(tanpa kunci)* keduanya kosong di seluruh grup untuk grup tanpa kunci} · `aktif` · *(revisi)* `contoh` (soal contoh; pilihan ganda saja, grup DISC bertanda contoh ditolak) · *(revisi)* `penjelasan` (maks 500, alasan jawaban benar; hanya soal contoh, pada soal asli dikosongkan server). Field bentuk lain disimpan sebagai slice kosong.

> ⚠️ *(revisi)* **Soal contoh bukan soal.** `jumlah_soal` di DTO tipe hanya menghitung soal asli aktif; soal contoh aktif dihitung terpisah di `jumlah_contoh`. Contoh tak memakan jatah `jumlah_soal` subtes, tak dinilai, dan tak masuk laporan, jadi menjumlahkan keduanya sebagai "jumlah soal" menghitung butir yang tak pernah dinilai. Pengecualiannya penjaga perubahan tipe (ganti jenis jawaban, buang subtes, ganti jumlah jawaban, hapus tipe): di sana **semua** item dihitung, karena kunci contoh juga dibuat untuk bentuk jawaban tipe itu.

> ⛔ Namanya sengaja **bukan** "bank soal" telanjang: istilah itu dipakai desain LMS People Development untuk quiz karyawan. Dua fakta berbeda, bukan salinan ([[REF - Kepemilikan Data]]).

**`psikotes_paket`**: `nama` · `deskripsi` · `bagian[]` {`tipe_id`, `aktif`} **berurutan** (urutan = urutan array; maks 8 bagian; satu tipe hanya sekali; minimal satu menyala) · `status`. Total waktu paket diturunkan dari bagian menyala yang bertimer.

**`psikotes_seed`**: penanda seed sekali-jalan per lingkungan.

**`psikotes_session`** (diperluas, bukan diganti): sesi berpaket ber-`jenis: "paket"` dengan `paket_id`, `paket_nama`, `bagian[]`, dan `bagian_index` (sengaja tanpa `omitempty` karena dipakai filter). Tiap bagian menyimpan **snapshot** tipe, soal, dan kunci saat terbit (`json:"-"`), status dan `selesai_karena` sendiri, serta per subtes `status`, `deadline`, `soal_index`, dan jawaban. *(revisi)* Bagian juga membekukan `penjelasan_kandidat`, dan tiap subtes `contoh[]` (soal contoh beserta kunci dan penjelasan; kosong pada sesi yang terbit sebelum revisi, dan kandidatnya langsung ke soal). `soal_index` = posisi terjauh yang pernah dicapai, dipakai untuk melanjutkan, **bukan** batas mundur. Jawaban nil (tak pernah dikirim) dan `[]` (dikosongkan) diperlakukan sama oleh skor dan laporan. Satu paket = **satu sesi**, jadi index unik `(candidate_id, round_id)` **tidak disentuh**. Sesi Kraepelin lama tetap berjalan di jalurnya.

**Index**: `idx_psikotes_tipe_kode` (unik) dan `idx_psikotes_item_tipe_subtes` (`tipe_id`, `subtes_kode`, `urutan`), dibuat saat boot **sebelum** seed.

### Kesiapan

Server menilai tiap tipe dengan **satu aturan** (`kesiapanSubtes`): subtes tanpa soal aktif = `soal_kosong`, soal aktif di bawah `jumlah_soal` = `soal_kurang`. *(revisi)* Sesudah soal asli lolos, subtes pilihan ganda tanpa soal contoh aktif = `contoh_kosong` (soal kosong atau kurang disebut lebih dulu), dan `subtes_kurang` ikut memuat subtes itu. Ditambah `tipe_nonaktif` dan `tipe_hilang` untuk bagian paket. Kraepelin selalu siap. Layar membaca **kodenya** (diterjemahkan FE, ADR 0010) dan daftar `subtes_kurang` per tipe; layar tak menghitung ulang aturan itu, supaya chip subtes di Tipe Tes dan Bank Soal tak pernah berbeda pendapat dengan label "belum siap" paket. Paket siap bila semua bagian menyalanya siap.

## Alur Pengguna

**HR (erp-frontend, Pengaturan > Rekrutmen)**, tiga tab ditambahkan **di ujung** supaya tautan `?tab=` lama tak bergeser:
1. **Tipe Tes**: kartu per tipe dengan jenis jawaban, waktu, jumlah soal aktif, chip subtes (amber bila kurang), kesiapan, dan tautan "Kelola soal" ke Bank Soal. Dialog tambah/sunting menghitung total waktu langsung. *(revisi)* Dialog punya field **Penjelasan untuk kandidat** (dengan pengingat tak menyebut nama tes) dan Deskripsi berlabel catatan internal; chip amber yang kurang karena soal contoh menyebut sebabnya lewat `title` dan teks pembaca layar; bentuk jawaban juga terkunci bila tipe baru punya soal contoh.
2. **Bank Soal**: pilih tipe dan subtes; tambah atau sunting soal (unggah gambar soal dan opsi, pilih kunci), naik/turun urutan, nonaktifkan. **Impor Excel**: unduh template, berkas dibaca di peramban, pratinjau per baris, baris rusak ditolak satu per satu, simpan hanya bila berkasnya sama dengan yang dipratinjau. *(revisi)* Tiap subtes pilihan ganda punya bagian **Soal contoh** di atas daftar soal asli: hitungan contoh aktif dari server (`jumlah_contoh`), peringatan amber bila belum ada contoh aktif, tombol Tambah soal contoh, dan urutan naik/turun terpisah dari soal asli. Dialog soal punya sakelar **Soal contoh** dan **Penjelasan jawaban**. Template impor punya kolom opsional `contoh` (`ya`, `yes`, `1`, `x`; isi lain berarti soal asli) dan `penjelasan`; berkas lama tanpa kolom itu tetap terbaca. *(tanpa kunci)* Tipe DISC: dialog grup kata punya satu sakelar **Pakai kunci skor** per grup. Mati: kedelapan huruf dikosongkan sekaligus dan pilihan huruf disembunyikan. Nyala: pilihan D, I, S, C, N dengan placeholder "Pilih huruf". Grup baru dibuka mati; grup berhuruf dibuka menyala. Grup tanpa huruf tampil dengan satu penanda **Tanpa kunci**, bukan delapan chip kosong, dan legenda chip huruf hanya tampil bila ada grup berhuruf. Impor DISC: `kata_1` sampai `kata_4` wajib; kolom `most_*`/`least_*` opsional sebagai SATU kesatuan (tanpa satu pun = grup tanpa kunci; begitu satu ada, kedelapannya wajib dan yang hilang disebut). Dialog impor tipe DISC menampilkan aturan itu, dan baris contoh template DISC tanpa huruf.
3. **Paket Tes**: susun bagian dengan tombol naik/turun, nyala/mati per bagian, total waktu otomatis; bagian belum siap bertanda beserta tautan ke Bank Soal.
4. **Rekrutmen > Kandidat** di babak Psikotest: **Kirim Tes** membuka dialog kartu paket. Bawaannya paket siap pertama. Paket belum siap terkunci dengan alasannya **dan tautan ke tempat membetulkannya** (Bank Soal, Tipe Tes, atau Paket Tes). Daftar paket yang gagal dimuat tampil sebagai galat dengan tombol coba lagi, bukan sebagai "belum ada paket". Sesudah terbit, tautan tampil untuk disalin; email berisi tautan dikirim bila kandidat punya alamat email.
5. Tabel kandidat: badge "Bagian N dari M" selama berjalan; Selesai atau Terputus sesudahnya.
6. Detail kandidat, tab **Hasil Tes**: laporan per bagian. Kraepelin memakai laporan dan kurva lama; CFIT benar per subtes; DISC tabel dan grafik Most/Least/Change (terang dan gelap). *(tanpa kunci)* Tabel dan grafik DISC hanya tampil bila `skor_otomatis` (field absen = backend lama, tetap tampil). Selain itu tampil satu kalimat bahwa soal DISC tes ini dikirim tanpa kunci skor lengkap sehingga D, I, S, dan C tidak ditampilkan, lalu **lembar jawaban** yang meniru kertas: tiap grup empat pernyataan dengan tanda di kolom P (paling sesuai) dan K (paling tidak sesuai), dan grup yang belum dijawab bertanda "Belum dijawab". Lembar juga tampil di bawah grafik bila bank berkunci. Nomor grup = posisi di sesi (urutan Bank Soal saat tes dikirim), jadi keterangan lembar menyuruh HR mencocokkan kunci kertas lewat teks pernyataan. HR memutuskan Pass/Fail di kartu yang sama.

**Kandidat (career portal, tautan email)**:
1. Sapaan, lalu **ringkasan paket** (bagian dan waktunya), lalu per bagian: petunjuk, mengerjakan, layar jeda "bagian N selesai, berikutnya ...", sampai Tes Selesai. Bagian tanpa subtes bernama (DISC, pilihan ganda satu subtes) menampilkan petunjuk HR untuk subtes tunggalnya di layar petunjuk.
2. **CFIT**: layar pembuka tiap subtes, soal satu per satu, maju saja, hitung mundur dari sisa detik server; di laptop A sampai F memilih dan Enter lanjut. Saat waktu habis, pilihan yang sudah ditandai ikut terkirim lalu subtes ditutup.
3. **DISC**: grup 4 kata, pilih satu "Paling sesuai" dan satu "Paling tidak sesuai"; memilih kata yang sama untuk peran lain melepas pilihan sebelumnya.
4. **Kraepelin**: mesin lama. Meninggalkan halaman menutup tes, **hanya di bagian ini**.
5. Terputus atau muat ulang: tautan yang sama melanjutkan dari bagian, subtes, dan soal terakhir; subtes yang waktunya sudah habis tertutup sendiri.

**Kandidat sesudah revisi layar** *(revisi, menggantikan poin 1 sampai 3 di atas)*:
1. **Sapaan** menampilkan lowongan (judul posting, cadangan posisi yang dilamar), nomor telepon, dan email yang **disamarkan server** (minimal empat digit telepon tersembunyi, mis. `0812-****-7890`; email `ri****@gmail.com`), plus kalimat "bila data ini bukan milik Anda, hubungi HR". Nilai lengkapnya tak pernah dikirim, karena tautan bisa diteruskan ke orang lain.
2. **Nama tes tak pernah tampil.** Bagian paket tampil sebagai *Tahap N* beserta `penjelasan_kandidat`; subtes sebagai *Bagian N*. Labelnya satu tempat di career portal (`labelTahap`/`labelBagian`).
3. **Soal contoh wajib sebelum soal asli**, tanpa waktu dan tanpa nilai. Pilihan ganda mengambil contoh dari Bank Soal: kandidat memilih, menekan Periksa jawaban, lalu melihat benar atau belum, jawaban yang benar, dan penjelasannya. Grup contoh DISC dan kolom contoh Kraepelin bawaan portal. Waktu subtes baru berjalan saat Mulai soal. Subtes atau tahap yang waktunya sudah berjalan (kandidat kembali ke tautan) tak diulang contohnya.
4. **Pilihan ganda boleh kembali** selama waktu subtes berjalan: nomor soal bisa diklik, Sebelumnya/Berikutnya, tanda **Ragu-ragu** (hanya di peramban, localStorage per token, tak memengaruhi nilai), dan konfirmasi *Selesaikan bagian* yang menyebut soal kosong, soal dua-jawaban yang baru dipilih satu, dan tanda ragu. Soal yang sekadar dilewati tidak dikirim. **DISC** punya Sebelumnya; **Kraepelin tetap maju saja**.
5. Jawaban dikirim saat soal ditinggalkan dan hanya bila berubah. Kiriman yang menyerah karena gangguan jaringan tak dianggap tersimpan dan dikirim ulang saat bagian diselesaikan atau waktunya habis.

Titik tunggu yang **tetap ada**: HR tak diberi notifikasi saat hasil siap; ia melihat badge tabel.

## Aturan dan Penjaga (server)

- **Tipe yang sudah punya soal** menolak (409) tiga perubahan: mengganti jenis jawaban, membuang subtes yang masih bersoal, dan **mengganti jumlah jawaban subtes yang bersoal** (kunci soalnya dibuat untuk jumlah lama; diterima diam-diam, setiap jawaban kandidat dinilai salah). Menghapus tipe yang masih bersoal atau masih dipakai paket juga 409; jalannya menonaktifkan.
- **Menonaktifkan tipe tidak mengunci sesi yang sudah terbit** (snapshot). Paket yang memakainya menjadi "belum siap" dan tak bisa dikirim sampai bagiannya dimatikan atau tipenya diaktifkan lagi.
- **Terbit**: bagian menyala yang belum siap menggagalkan terbit dengan pesan yang menyebut bagiannya, tidak dilewati diam-diam. Soal yang jumlah kuncinya tak sama dengan `jumlah_jawaban` subtes juga menggagalkan terbit dengan arahan ke Bank Soal. Jumlah soal per subtes dipotong ke `jumlah_soal` menurut urutan bank. *(revisi)* Soal contoh dibekukan terpisah dan tak ikut dipotong; subtes pilihan ganda tanpa soal contoh, atau soal contoh yang jumlah kuncinya salah, menggagalkan terbit dengan arahan ke Bank Soal.
- **Snapshot**: tipe, soal, dan kunci dibekukan ke sesi saat terbit. Perubahan bank sesudahnya tak menyentuh sesi yang sudah terbit, supaya hasil terbaca dengan soal yang benar-benar dikerjakan.
- **Gambar**: unggah multipart maks **2 MB**; tipe ditentukan dari **isi berkas** (PNG, JPG, GIF, WEBP; SVG dan non-gambar ditolak 415). Kunci objek 32 hex plus ekstensi disusun server di prefix `recruitment/psikotes/gambar/`, sehingga soal tak bisa merujuk objek lain di bucket (mis. CV kandidat). Objek **tak pernah dihapus**; mengganti gambar berarti kunci baru. Kandidat hanya bisa mengambil gambar yang ada di snapshot sesinya.
- **Kunci dan dimensi** hanya untuk penyunting: daftar soal digerbang `PermRecruitmentWork`, bukan izin lihat yang paketnya berjangkauan semua orang. Kandidat menerima DTO eksplisit tanpa kunci, dimensi, maupun skor (dikunci test daftar-izin); laporan HR hanya membawa hitungan. *(revisi)* DTO kandidat juga tanpa nama tipe, nama subtes, deskripsi, dan nama paket (konfigurasi kolom ber-key `konfig_kolom`, dulu `kraepelin`); GET sesi paket dikunci test daftar-izin lewat penyusun yang sama dengan handler. **Pengecualian sadar**: kunci dan penjelasan **soal contoh** dikirim lewat endpoint contoh tersendiri; soal asli tetap tanpa kunci.
- *(tanpa kunci)* **Pengecualian sadar kedua, laporan DISC**: laporan HR bagian DISC membawa lembar jawaban (teks pernyataan snapshot + indeks pilihan P dan K, TANPA huruf), terbaca pemegang izin lihat rekrutmen tanpa izin terpisah (keputusan user 2026-09-15). Penjaganya test laporan: daftar-izin dan kehadiran kunci JSON `disc` dan `lembar[]`, larangan kata yang sudah ada, dan larangan huruf "D", "I", "S", "C", "N" yang peka kapital (`larangKata` menurunkan huruf, sehingga larangan tak peka kapital bertabrakan dengan kunci hitungan `d`/`i`/`s`/`c`/`n`). ⚠️ **Tanpa huruf bukan jaminan kerahasiaan kunci**: pada bank BERKUNCI, hitungan Most/Least + lembar dari cukup banyak laporan bisa dipakai menghitung balik huruf pernyataan terpilih. Hari ini laten karena bank DISC tanpa kunci (Belum Diputuskan butir 10).
- **Audit**: tipe dan paket (buat, ubah, hapus), soal (buat, ubah dengan penanda "kunci diubah" **tanpa nilai kuncinya** dan *(revisi)* "dijadikan soal contoh" atau "dijadikan soal asli", hapus, urutan), impor, dan unggah gambar.
- **Batas waktu**: deadline subtes ditulis server saat subtes dimulai. Jawaban yang tiba sesudah deadline plus toleransi 5 detik ditolak `409 waktu_habis`; nomor yang sudah dilewati `409 soal_terlewati` (*(revisi)* dibuang: nomor mana pun dalam rentang boleh dijawab ulang selama subtes berjalan; nomor di luar rentang 400). Kode galat mesin lain: `bukan_giliran`, `belum_mulai`, `subtes_selesai`.
- **Impor Excel**: server memvalidasi per baris dengan aturan yang sama dengan tambah manual, maks 500 baris. Pratinjau (`dry_run`) mengembalikan hash; simpan wajib membawa hash yang sama, beda berarti 409. *(revisi)* Hash ikut mencakup tanda contoh dan penjelasan.
- *(revisi)* **PUT tipe dan soal mempertahankan field yang tak dikirim**: `penjelasan_kandidat`, `contoh`, dan `penjelasan` dari klien yang belum mengenalnya (erp-frontend lama, tab yang dibuka sebelum deploy) tidak dikosongkan; nilai kosong yang dikirim tetap berlaku. Tanpa itu penjelasan bawaan hilang permanen (pengisian susulan hanya mengisi field yang absen) dan soal contoh diam-diam jadi soal asli yang ikut dinilai.
- *(tanpa kunci)* **Grup DISC**: kedelapan huruf kosong = grup tanpa kunci, sah lewat tambah manual maupun impor. Campuran kosong dan terisi → `400` "huruf kunci grup ini harus diisi semua atau dikosongkan semua"; huruf di luar D, I, S, C, N → `400`. Server satu-satunya validator isi; layar hanya memilih tampilan (sakelar, penanda, legenda) dan impor hanya memeriksa bentuk header.

## Penilaian dan Hasil Tes

- Skor pilihan ganda dan tally DISC **dihitung saat laporan dibaca**, bukan disimpan.
- *(tanpa kunci)* `disc.skor_otomatis` = setiap kata di setiap grup SNAPSHOT punya huruf Most dan Least; nol grup = false. Satu grup saja tanpa huruf membuatnya false, karena tally yang melewatkan sebagian grup terbaca utuh padahal tidak. Tally tetap dikirim (huruf kosong terhitung N) supaya bentuk JSON lama utuh. `disc.lembar[]` diturunkan dari snapshot: `nomor` (posisi di sesi), `pernyataan[]`, `pilih_p` dan `pilih_k` (indeks, `null` bila belum dijawab atau jawabannya tak utuh). Tally dan lembar memakai satu aturan jawaban utuh (`pilihanDISC`), supaya grup yang dihitung selalu grup yang tampil terpilih.
- Baris Hasil Tes Psikotest tetap `Pending`. **Skor hanya ditulis untuk paket berisi satu bagian Kraepelin yang tuntas** (bentuk yang sama dengan sesi lama); paket campuran menulis baris **tanpa skor** (`$unset`), karena tak ada satu angka yang jujur mewakili CFIT, DISC, dan Kraepelin sekaligus.

## Penutupan Sesi Paket

- Bagian yang tuntas memajukan giliran; bagian terakhir menutup sesi tuntas.
- **Beacon meninggalkan halaman hanya menutup sesi saat bagian Kraepelin sedang berjalan**, ditegakkan server. Beacon di bagian lain, termasuk yang tiba sesudah bagian Kraepelin ditutup, tak menutup apa pun.
- **Sapuan tanpa aktivitas**: 6 × detik per kolom saat bagian Kraepelin berjalan, selain itu **30 menit**. Filter penutup mengunci giliran bagian dan `last_seen_at` dari data yang dibaca, jadi kandidat yang ternyata aktif di sela baca dan tulis tak ikut ditutup.
- Bagian yang sedang berjalan saat sesi ditutup ikut berakhir dengan alasan yang sama; bagian yang sudah tuntas tetap tuntas; bagian yang belum dimulai tetap pending. Penutup yang kalah balapan tak menulis Hasil Tes.

## Bawaan (seed)

Dipasang **sekali per lingkungan** (penanda `psikotes_seed`), tipe by `kode` dan paket by `_id` tetap dengan `$setOnInsert`, jadi suntingan HR tak pernah ditimpa dan seed yang terulang tak melahirkan salinan.

| Bawaan | Isi |
|---|---|
| Tipe Kraepelin | 45 kolom × 40 baris × 30 detik = 22 menit 30 detik |
| Tipe CFIT | Seri 13 soal 3 menit; Klasifikasi 14 soal 4 menit, **2 jawaban**; Matriks 13 soal 3 menit; Kondisi 10 soal 2 menit 30 detik. Total 12 menit 30 detik. **Tanpa butir soal** |
| Tipe DISC | 24 grup, tanpa timer, anjuran "10-15 menit". **Tanpa butir soal** |
| Paket Kraepelin | Kraepelin saja; siap dikirim |
| Paket Staff | CFIT, DISC, Kraepelin; **belum siap** sampai bank soal CFIT dan DISC diisi. *(internal)* Di DEV **siap sejak 2026-09-16** (diukur lewat gateway: `siap` true untuk paket dan ketiga bagiannya, total 2.100 detik); di prod masih belum |

⚠️ Permintaan manajemen menyebut CFIT "50 soal, 30 menit", tetapi durasi subtes yang diminta sendiri berjumlah 12 menit 30 detik. Seed mengikuti durasi per subtes; HR bisa mengubahnya di Tipe Tes.

*(revisi)* Ketiga tipe bawaan membawa `penjelasan_kandidat` netral tanpa nama tes. Lingkungan yang sudah ter-seed diisi saat boot hanya untuk tipe bawaan yang field-nya **absen** (`$exists: false`), jadi suntingan HR tak ditimpa. Paket bawaan berisi CFIT tetap belum siap sampai HRD mengisi soal contoh tiap subtes, selain soal aslinya.

### Bank Penalaran Gambar (internal)

*(internal)* Seed **tetap tanpa butir soal**; yang terisi adalah DATA di DEV (2026-09-16). Soalnya orisinal buatan internal, bukan butir CFIT berlisensi: keputusannya butir (10) di [[ADR - 0087 Katalog Tipe Psikotes Jadi Master Data, Tiga Bentuk Jawaban Tetap Kode]].

| Hal | Isi |
|---|---|
| Sumber soal | Dibangkitkan skrip berbenih tetap `buat_cfit.py` (Pillow) di `erp/.task-plans/bahan-psikotes/cfit/`: 50 soal asli + 2 soal contoh per subtes, lima opsi bergambar, kesulitan bertahap. Membangkitkan ulang menghasilkan gambar yang byte-identik selama skrip dan benihnya tak berubah |
| Bukti kunci | `test_buat_cfit.py` memakai pemeriksa yang ditulis TERPISAH dari pembangkitnya: seri dan matriks dihitung ulang dari aturannya, klasifikasi wajib hanya punya satu pasangan yang bisa dibenarkan satu sifat, kondisi diuji geometri (ada wilayah yang muat titik). Kontrol negatif menuntut enam soal cacat buatan ditolak |
| Cara muat | `muat_cfit.py` lewat gateway, pratinjau sebagai bawaan: unggah tiap PNG (`POST /psikotes/gambar`), lalu `POST /psikotes/item` per soal, soal contoh dulu baru soal asli tiap subtes. **Impor Excel tak bisa dipakai** karena teks saja (`psikotes_impor.go`). Loader berhenti bila tipe sudah bersoal, dan mencatat id soal serta kunci gambar ke `hasil-muat-<host>.json` |
| Terukur di DEV | 332 gambar, 58 soal; `jumlah_soal` 13/14/13/10, `jumlah_contoh` 2 tiap subtes, kesiapan siap, subtes identik dengan sebelum ganti nama |
| Uji kandidat | Satu sesi paket uji dikerjakan penuh lewat API publik: urutan soal sama dengan manifest, kunci soal contoh sama dengan manifest, gambar 200 PNG selagi sesi berjalan lalu **410 sesudah sesi tutup**, laporan HR benar = jumlah soal dikurangi satu di tiap subtes |
| Prod | Belum. Dijalankan manusia sesudah fitur psikotes multi-jenis naik ke prod |

⚠️ Tingkat kesulitan disusun dari rancangan dan **belum diukur** dari hasil kandidat: tak ada norma, dan skor tetap jumlah benar mentah. Batas waktu subtes masih bawaan seed dan belum diuji terhadap soal ini.

## Yang Dipakai Ulang

| Kebutuhan | Yang sudah ada |
|---|---|
| Sesi bertoken, magic link, status, idempotensi, sapuan kedaluwarsa | `psikotes_session` dan perkakasnya; diperluas dengan cabang paket, bukan disalin |
| Mesin Kraepelin | `kraepelin_soal.go`, `kraepelin_scoring.go` apa adanya untuk bagian `angka_kolom` |
| Pola mesin pilihan ganda | `services/learning`: snapshot saat mulai, timer ditegakkan server. **Polanya**, bukan kodenya |
| Urutan dan nyala/mati | Semantik `AssessmentTypeIDs` dan `Mandatory`; tombol naik/turun (tanpa drag-and-drop) |
| Impor Excel | `bacaSheetPertama` (exceljs) di FE; pola dry-run dengan `expected_hash` di BE |
| Unggah dan pratinjau berkas | Pola berkas kandidat ke MinIO, **ditambah** batas ukuran dan daftar-izin tipe yang tak ada di pola lama |
| Laporan dan grafik | `LaporanIndividual` + `KurvaKerja` untuk bagian Kraepelin; `ChartContainer` + `WARNA_BAGAN` untuk grafik DISC |

## Jebakan yang Sudah Diketahui

- ⛔ **Menyembunyikan kunci jawaban dengan tag `json:"-"` mematikan penguraian body**, sehingga seluruh kunci tersimpan bernilai nol (bug LMS). Di sini kunci **tidak** diberi `json:"-"`; yang menjaganya DTO kandidat eksplisit plus gerbang daftar soal setara penyunting.
- ⛔ **Mengganti spesifikasi index tidak terjadi lewat deploy.** Karena itu paket dijalankan sebagai satu sesi dan index unik sesi tak disentuh.
- ⛔ **Titik percabangan jenis yang terlewat tak berbunyi sebagai galat.** Percabangannya kini per sesi: sesi `jenis: "paket"` bercabang per bagian menurut `jenis_jawaban`; endpoint lama `columns` dan `finish` **menolak** sesi paket (400); sapuan dan beacon punya cabang paket sendiri. Tak ada berkas "dispatcher" tersendiri seperti yang disebut ADR.
- ⚠️ **Rute kandidat di gateway sengaja keluar dari limiter umum** 60 per menit per IP: satu subtes CFIT bergambar penuh (belasan soal × 7 gambar) melampauinya, dan jawaban yang ikut tertolak 429 hilang. Gantinya batas per token dan per IP sendiri ([[CORE - API Master Gateway]]). Jangan dikembalikan ke limiter umum.
- ⚠️ **Paket bawaan Staff belum siap sampai HRD mengisi bank soal.** Di prod ini keadaan hari pertama, bukan kasus pinggir; dialog Kirim Tes karena itu menautkan alasan "belum siap" ke Bank Soal.
- ⚠️ **Dua implementasi halaman kandidat.** Mesin CFIT dan DISC hanya ada di career portal. Halaman kandidat versi erp-frontend menolak sesi paket dengan pesan untuk membuka tautan lewat Portal Karir. Di DEV tautan psikotes semula mengarah ke erp-frontend (`ERP_FRONTEND_URL` dev), jadi tautan paket di dev berakhir di pesan itu. ✅ **Sejak bip-erp #1870 (merged, live dev dan prod 2026-09-14)** tautan psikotes membaca `CAREER_PORTAL_URL`, yang di dev berisi portal karir prod, sehingga tautan dari dev terbaca tidak berlaku (terukur 2026-09-14: `link` terbitan dev berawalan `https://career.bharatainternasional.com/psikotes/`) ([[Microservices - Recruitment Service]] increment **Tautan Email per Penerima**). Uji dev tetap memakai career portal lokal dengan token yang sama.
- ⚠️ *(revisi)* **Urutan deploy recruitment-service, career portal, erp-frontend, tanpa jeda.** Career baru di atas recruitment lama: kembali ke soal sebelumnya ditolak `soal_terlewati` dan subtesnya tertutup. Career lama di atas recruitment baru: DTO tanpa nama tes membuat layar lama menulis "Mulai undefined". erp-frontend lama di atas recruitment baru: `contoh_kosong` tampil sebagai "belum siap" umum dan HR belum bisa menambah soal contoh.
- ⚠️ *(tanpa kunci)* **Urutan deploy: recruitment-service, lalu erp-frontend, BARU 24 grup DISC tanpa kunci dimuat** (DEV oleh agent, PROD oleh manusia). erp-frontend lama di atas recruitment baru menampilkan sesi tanpa kunci sebagai tabel dan grafik bernilai nol dengan seluruh pilihan terhitung N, yang terbaca seperti profil. Bentuk JSON sengaja tetap, jadi tidak crash, tapi juga tidak berbunyi.
- ⛔ *(tanpa kunci)* **Radix `SelectItem` melempar galat untuk value kosong**, sedangkan Root `Select` menerima value kosong sebagai placeholder (`shouldShowPlaceholder`, `@radix-ui/react-select` 2.2). Karena itu tanpa kunci dipilih lewat sakelar per grup, bukan item Select bernilai kosong.

## Belum Diputuskan (TBD)

1. **Legalitas item DISC** (B1). Risiko hukum, bukan teknis: lembar DISC berasal dari bahan HRD, jadi izin pemakaiannya harus dijawab HRD. *(internal)* **Untuk CFIT butir ini tertutup 2026-09-16**: banknya tidak memakai butir berlisensi sama sekali, melainkan soal penalaran gambar orisinal buatan internal (§Bank Penalaran Gambar (internal)).
2. **Bentuk jawaban EPPS**: diasumsikan muat di `most_least`, belum diperiksa.
3. **Mesin kandidat resmi** (B2): dibangun di career portal (de facto jalur prod); keputusan tertulisnya belum ada.
4. **Pendampingan CFIT** (B3): dibangun dengan asumsi boleh jarak jauh, batas waktu ditegakkan server. HRD perlu menerima risikonya tertulis atau memilih pengerjaan diawasi. Rincian di ADR 0087 §Belum Diputuskan.
5. **Tenggat tautan dan status kandidat** (B4): tautan yang belum dibuka tak pernah kedaluwarsa, dan kandidat yang sudah ditolak tetap bisa mengerjakan.
6. **Urutan babak di prod** (`sequence_number` bertabrakan): dirapikan sebagai data atau diberi penjaga keunikan.
7. **Keterangan per baris di pratinjau impor** ditampilkan dari kalimat server berbahasa Indonesia, juga saat bahasa layar Inggris. Belum diputuskan apakah dibiarkan (sama dengan pesan galat server di toast) atau diganti kode yang diterjemahkan FE.
8. ✅ Bentuk perbaikan skor artefak: diputuskan 2026-09-10 (tahap nol), sesi tak tuntas menulis Hasil Tes tanpa skor.
9. *(revisi)* **Tampilan nomor soal bertanda ragu-ragu**: isian amber menutupi status terjawab atau belum (sesuai prototipe yang disetujui; pembaca layar mendengar keduanya). Opsi cincin amber di atas warna status belum diputuskan.
10. *(tanpa kunci)* **Kerahasiaan kunci DISC bila kelak dimuat**: laporan terbaca pemegang izin lihat, dan hitungan + lembar cukup untuk menghitung balik huruf. Hari ini laten (bank tanpa kunci); bila kunci dimuat dan kerahasiaannya penting, perlu keputusan baru (mis. hitungan hanya untuk pemegang izin kelola). Dicatat di ADR 0087 butir (9a).
11. *(tanpa kunci)* **Penanda bank DISC campuran** di Bank Soal (sebagian grup berkunci membuat tiap tes baru tanpa grafik, tanpa tanda apa pun di Bank Soal): ditunda 2026-09-15. Bila dibutuhkan, dihitung server seperti `subtes_kurang`, bukan di layar yang ikut memuat grup nonaktif.
12. *(tanpa kunci)* **Penanda "berkas tanpa kolom huruf"** di pratinjau impor (menangkap kolom huruf yang seluruhnya salah eja, mis. `p_*`/`k_*`, yang kini terbaca sebagai grup tanpa kunci): ditunda 2026-09-15; petunjuk di dialog impor sudah menyebut nama kolomnya.

## Dependensi & Integrasi

- [[Microservices - Recruitment Service]]: rumah kodenya; babak Psikotest dicari by nama ber-`form_type: "test"`
- [[CORE - API Master Gateway]]: satu rute umum publik untuk kandidat, penyaring token dan path, limiter sendiri
- [[Microservices - File Service]]: ⚠️ tidak dipakai; recruitment bicara langsung ke MinIO lewat shared-library, jadi batas 2 MB di sini ditulis sendiri
- [[Microservices - Notification Service]]: email magic link ke kandidat (best-effort)
- [[APP - Web ERP]]: layar HR (Pengaturan Rekrutmen, Kirim Tes, laporan)
- [[APP - Portal Karir Bharata]]: layar kandidat

## Dokumen Terkait

- [[ADR - 0087 Katalog Tipe Psikotes Jadi Master Data, Tiga Bentuk Jawaban Tetap Kode]]: keputusan dan alasannya
- [[HRIS - Psikotes Kraepelin]]: mesin Kraepelin dan sesi lama
- [[HRIS - Recruitment]]: konsep dan keputusan HRD
- [[API - Recruitment Service]]: kontrak endpoint
- [[REF - Kepemilikan Data]]: pemilik koleksi katalog dan salinan snapshot sesi
- [[ADR - 0041 Izin Tipe Form Menempel di Departemen]]: aturan berlaku saat ditetapkan
