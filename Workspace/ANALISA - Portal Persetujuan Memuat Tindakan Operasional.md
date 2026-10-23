## Deskripsi

*Pecahan kerja untuk [[ADR - 0181 Portal Persetujuan Memuat Keputusan dan Tindakan Operasional]]. Bukan rencana per berkas; tiap irisan cukup jelas untuk dilempar ke `/brief` setelah ADR-nya Diterima. Melanjutkan [[ANALISA - Antrean Persetujuan Terpusat di Web]].*

- **Status**: 🟡 Belum dikerjakan. ADR induk 🟢 Diterima 2026-10-15 oleh irfanarfianto; irisan 0 boleh jalan lebih dulu karena berupa perbaikan bug yang tidak bergantung pada keputusan baru.
- **Tanggal**: 2026-10-15
- **Rujukan visual**: mockup Artifact privat https://claude.ai/artifact/8oXpNrXmmzUW11KEHm3wV2 (nama fiktif; judul "Tindakan Saya" di mockup sudah ditolak, halaman tetap "Persetujuan")

## Tujuan

Halaman Persetujuan menjadi tempat setiap orang melihat **semua yang menunggu tangannya**, baik keputusan maupun pekerjaan operasional, dengan kalimat yang menyebut apa yang harus dilakukan, dan satu klik ke tempat yang tepat untuk melakukannya. Pengukuran prod 2026-10-15 (di ADR induk): ±99% isi antrean adalah tindakan operasional, hanya 2 dokumen yang menunggu keputusan.

## Keputusan ringkas

Rinciannya di ADR induk; di sini hanya pegangan:
- Nama, judul, dan rute tetap: "Persetujuan", `/portal/persetujuan`. Menu terbuka untuk semua; penyaringan di service sumber. Karena nama lebih sempit dari isi, kalimat penjelas (pil "Yang perlu Anda lakukan", kolom "Yang harus Anda lakukan", keadaan kosong) wajib ada.
- Agregator mengirim kode `aksi` (`putuskan`, `jawab_stok`, `isi_harga`, `transfer`, `konfirmasi_transfer`, `catat`, `triase`, `pantau`); FE hanya menerjemahkan ke i18n.
- Baris: kategori, nomor, perihal terbaca, pemohon asli + posisi·departemen, Nilai (null ≠ 0), tahap berlabel + langkah x dari y, "Yang harus Anda lakukan". Kontrol "Urutkan: Terlama | Terbaru" (bawaan Menunggu = Terlama, Riwayat = Terbaru), atas seluruh baris, tersimpan di `?urut=` (ADR induk butir 4a).
- Pil per aksi; bawaan "Perlu tindakan" menyembunyikan `pantau`.
- Sheet berkerangka bersama, badan dari komponen detail modul; footer per mode; tanpa "lalu berikutnya".
- Spanduk volume ke layar kerja modul yang sudah ada (`catat` → tab Ringkasan `/finance/tim-accounting`; `transfer` → `/finance/ap`).
- Riwayat tindakan pemanggil (terbaru dulu), dengan kolom Posisi sekarang. Jendelanya mengikuti sumber, BUKAN seragam 30 hari: attendance 30 hari, pengajuan barang 200 dokumen terbaru (`/diproses-saya`); layar tidak menjanjikan angka jendela.
- Tanpa penanda SLA, kecuali usulan spanduk tiket >7 hari.

## Irisan 0: perbaikan bug, bisa langsung dan terpisah

Tidak menunggu ADR induk Diterima; masing-masing benar menurut ADR 0114 yang berlaku hari ini.

**0a. Offer Draft palsu.** Adapter `/offers` di agregator tidak menyaring status (`bip-erp services/employee/antrean_pengajuan.go:642`), sehingga 5 offer berstatus Draft yang sebenarnya sudah Approved tampil sebagai antrean.
- *Yang harus benar*: offer yang sudah Approved tidak tampil di antrean. Test adapter dengan fixture berisi Draft dan Approved; kontrol negatif (cabut saringannya, test merah di assertion itu).
- *Repo*: bip-erp.

**0b. Live Support bertahap kosong.** `petakanKarya` (`antrean_pengajuan.go:903-909`) mengisi `Tahap` kosong, lalu FE (`tabel-persetujuan.tsx:135`) menampilkan "Tidak menunggu keputusan" untuk baris yang justru menunggu tinjauan.
- *Yang harus benar*: baris Live Support punya tahap terisi dan tidak pernah berbunyi "Tidak menunggu keputusan" selama menunggu tinjauan.
- *Repo*: bip-erp (isi tahap); erp-frontend bila perlu menangani tahap kosong secara jujur.

**0c. Label tahap mentah.** `kunciLangkah` (`erp-frontend src/features/persetujuan/lib/kategori.ts:85`) tidak memakai kunci `pengajuanBarang.tahap.*` yang sudah ada, sehingga `pb_*` tampil mentah; `KATEGORI_KEY` belum punya `rekrutmen_requisition` dan `offer`.
- *Yang harus benar*: tidak ada string `pb_`, `request`, atau `draft` mentah di kolom Tahap untuk kategori mana pun; dua kategori rekrutmen berlabel di kedua locale. Kunci yang ada dipakai ulang, bukan disalin.
- *Repo*: erp-frontend.

**0d. Urutan terbaru dulu.** Agregator mengurut terbaru dulu (`antrean_pengajuan.go:1546-1555`), menyimpang dari ADR 0114 butir 1.
- *Yang harus benar*: baris tertua di atas; test urutan dengan tiga baris beda umur.
- *Repo*: bip-erp.

*Deploy*: 0a, 0b, 0d backend dulu; 0c frontend kapan saja (tidak mengubah kontrak).

## Irisan 1: fondasi kontrak dan tabel, semua kategori (BE + FE)

**Kontrak baris baru** dari `GET /pengajuan/antrean`:

| Field | Isi | Catatan |
|---|---|---|
| `aksi` | kode enum | dipetakan adapter per sumber dari tahap; sumber baru menyetor sendiri |
| `nomor` | nomor dokumen | |
| `nilai` | angka, **nullable** | plus satuan dan catatan (mis. harga belum diisi); `null` ≠ 0 |
| pemohon | nama asli, posisi, departemen | bukan `employee_id` (Pelatihan, Payroll hari ini) |
| tahap | kunci i18n berlabel | bukan kode mentah |
| `langkah_ke` / `langkah_total` | bila sumber tahu | boleh kosong |
| `tautan` | rute per dokumen yang TEPAT | lihat tabel tujuan |

**Tujuan klik per kategori** (wajib dinyatakan sebelum baris kategorinya masuk tabel, syarat ADR 0114 butir 5):

| Kategori | Tujuan | Keadaan |
|---|---|---|
| Pengajuan Barang | `/pengajuan-barang/[id]` | rute ada di `origin/main` |
| Tiket | `/task-management/pending/<id>` (TriageView) | rute `pending/[id]` ada; bahwa ini tujuan yang paling tepat untuk triase masih dugaan, **verifikasi** |
| Requisition | `/hris/recruitment/requisitions/[id]` | rute ada |
| Permintaan GA | `PermintaanDetailSheet` berdasarkan `nomor` | komponen menerima prop `nomor` |
| Booking Ruang | `/ga/peminjaman?nomor=` | **verifikasi** bahwa id baris = nomor dan halaman membaca param itu |
| Live Support, Pelatihan, Permintaan Pembelian (dulu "Permintaan ERP", [[ADR - 0188 Persetujuan Terpusat di MyBharata, Detail Seragam dari Agregator, Tanpa Arahan ke Web]]), Offer | belum ada rute per id | **TBD** |
| Karyawan (absensi) | Sheet detail yang sudah ada | sudah benar hari ini |

**FE**: kolom baru, judul pil "Yang perlu Anda lakukan" dengan pil per aksi dan `pantau` tersembunyi di bawaan, keadaan kosong yang menjelaskan fungsi halaman, sambungkan riwayat Pengajuan Barang ke `GET /pengajuan-barang/diproses-saya` (sudah mengirim `aksi_saya`), kolom Posisi sekarang di Riwayat, kontrol "Urutkan: Terlama | Terbaru" di kedua tab (ADR induk butir 4a). Nama menu, judul, dan rute tidak disentuh.

*Yang harus benar*:
- Setiap baris dari setiap sumber berisi `aksi` yang dikenal; test per adapter mendaftar **semua** tahap modulnya dan gagal bila ada tahap tanpa pemetaan.
- PB tahap `pb_cek_stok_ga` tampil dengan aksi `jawab_stok`, dan kliknya membuka dokumen itu, bukan layar persetujuan yang membuangnya.
- Nilai `null` tampil sebagai catatan, bukan "Rp 0".
- Tidak ada `employee_id` di kolom pemohon.
- Bawaan tab Menunggu urut **Terlama** (paling lama menunggu di atas), bawaan tab Riwayat **Terbaru**; kontrol "Urutkan: Terlama | Terbaru" membalik urutan.
- Urutan diterapkan atas **seluruh** baris agregator sebelum paginasi tampilan: dengan lebih dari satu halaman data, baris tertua seluruh antrean ada di baris pertama halaman 1 (test dengan data melebihi satu halaman; `MainTable` tidak mengurutkan `data`, jadi mengurutkan per halaman lolos test kecil dan salah di data nyata).
- Pilihan urutan tersimpan di `?urut=terlama|terbaru`: memuat ulang, tombol Back peramban, dan tautan yang dibagikan mempertahankannya; nilai tak dikenal jatuh ke bawaan tab. `useSearchParams` di dalam `Suspense` (tanpa itu gagal di `pnpm build`).
- Pengguna tanpa antrean melihat penjelasan bahwa halaman ini memuat keputusan dan tindakan yang menunggunya, plus tautan ke Pengajuan dan Riwayat, bukan tabel kosong polos.
- Semua teks baru lewat `t()` di `id.ts` dan `en.ts`.
- Satu perjalanan sebagai orang lewat gateway per peran utama (bukan `curl`), sebelum diklaim selesai.

*Repo*: bip-erp (agregator), erp-frontend (layar). *Deploy*: **bip-erp sebelum erp-frontend**; FE wajib aman bila field baru belum ada (fallback ke bentuk lama).

## Rincian tampilan yang disepakati (mockup 2026-10-15)

Diputus pemilik produk lewat beberapa putaran mockup (https://claude.ai/artifact/8oXpNrXmmzUW11KEHm3wV2, privat). Mengikat irisan 1 dan 2.

**Tabel**
- Kolom Menunggu (5): Menunggu · **Yang harus Anda lakukan** · Dokumen · Pemohon · Nilai. Kolom penentu di posisi kedua (`ui-checklist.md` §2c no. 5). Tidak ada kolom Tahap: lencana aksi + "langkah x dari y" sudah mewakilinya. Kalimat panjang per aksi hanya di panel, tidak diulang tiap baris.
- Kolom Riwayat (6): Diproses · Tindakan Anda (lencana hasil + alasan atau tahap Anda) · Dokumen · Pemohon · Nilai · Posisi sekarang.
- Waktu relatif ditulis lengkap ("20 menit yang lalu", "7 hari yang lalu") lewat `Intl.RelativeTimeFormat` + `intlLocale(lang)`, tanggal kecil di bawahnya. Kolom cukup lebar supaya tidak terpotong tiga baris.
- Dokumen: lencana kategori + nomor + perihal + satu baris keterangan yang tidak mengulang jenis (mis. entitas, jumlah item).
- Pemohon: `Avatar` (foto profil, fallback inisial) satu baris dengan nama + posisi·departemen. Butuh field foto dari backend.
- Lencana aksi = `Badge` berikon; identitas dari ikon + teks, warna penguat, pasangan yang tampil bersama berbeda rona dan terang: putuskan `info`, konfirmasi_transfer dan transfer `warning`, catat, isi_harga, dan periksa_qc `pending`, jawab_stok dan triase `secondary`, serah_terima `default` (beda dari jawab_stok yang tampil bersama di layar Gudang GA), tindak_lanjut dan pantau `outline`. Hasil riwayat: disetujui `success`, ditolak `destructive`, dikembalikan `warning`, lainnya `default`.
- Lima keadaan (`ui-checklist.md` §2): Skeleton setinggi baris, galat bersebab + Coba lagi, terkunci menyebut siapa yang boleh, sebagian menandai sumber `degraded`, kosong `MascotState` (total vs saringan dibedakan).
- Ponsel: periksa dulu apakah `MainTable` sudah punya tampilan kartu; bila belum, task terpisah, jangan menambah prop ke `MainTable` demi satu halaman.

**Panel (Sheet), urutan isi**
1. Header tetap: judul perihal, baris "nomor · kategori · keterangan", **nominal besar** + catatan, avatar + nama + posisi + "diajukan … yang lalu". "Buka halaman dokumen" berupa tombol ikon di header, bukan di footer.
2. Kotak tindakan dua baris: lencana + "tahap · langkah x dari y", satu kalimat baku per aksi (+ langkah berikutnya).
3. Blok utama per aksi: `konfirmasi_transfer` tabel **Cocokkan dengan bukti transfer** (nominal, rekening tujuan, atas nama; Cocok/Beda) dan bukti transfer AP tampil lebih dulu dan besar; `putuskan` keperluan; `transfer` rekening tujuan (bank, nomor **penuh, tidak disensor**, atas nama, nominal); `catat` data pencatatan (nomor bukti, tanggal transfer, entitas, akun); `jawab_stok` barang diminta + jumlah; `triase` detail tiket.
4. Lampiran dikelompokkan: "Bukti transfer (dari AP)" dan "Bukti pengajuan (dari pemohon)".
5. Isian dobel dibuang: jenis (sudah di lencana), entitas (sudah di header), penerima yang sama dengan pemohon, rincian yang cuma satu baris (tampil hanya bila >1 item, dengan baris total).
6. Jenjang ringkas dengan **nama pelaku** tiap langkah dan "Anda" pada giliran pembaca.
7. Footer `SheetFooter`: satu tombol utama + satu outline. Tanpa "lalu berikutnya".
- Anak badan Sheet yang menggulir wajib `shrink-0`: kartu ber-`overflow-hidden` di kolom flex terjepit jadi sebaris saat isi panjang (terbukti di mockup).
- Nomor rekening penuh hanya boleh terkirim ke pemanggil yang berhak menindak dokumen itu (gerbang di service sumber).
- Data yang perlu diukur ke procurement sebelum panel dibangun (TBD bila belum ada): nominal + rekening yang dicatat AP saat transfer, nama pelaku tiap langkah jenjang, keperluan pengajuan.

### Keputusan panel Pengajuan Barang (Pemutus irfanarfianto, 2026-10-16)

Diukur ke kode `origin/main` sebelum dibangun:
- **"Kembalikan ke AP" TIDAK dibangun di irisan ini.** Fitur itu belum ada di FE maupun BE, dan BE sengaja menutup tolak/revisi di `pb_spv_transfer` (`services/procurement/pengajuan_barang_transisi.go`). Panel hanya punya "Konfirmasi transfer"; bila bukti tak cocok SPV membuka halaman dokumen. Kembalikan ke AP = kebutuhan terpisah yang butuh ADR (mengubah alur finance).
- **Rekening di blok Cocokkan memakai data yang ada.** Pembelian: `rekening_pemasok` (bank, nomor penuh, atas nama) dari amplop detail (sudah dikirim BE, belum dibaca FE). Non-pembelian (Dana/Iklan/Pajak): sistem tidak menyimpan rekening penerima; tampilkan nama penerima dari `bkk_isian.dibayarkan_kepada` + kalimat bahwa rekening dicocokkan di bukti transfer. Nominal dicocokkan pengajuan vs nominal transfer AP (`nominal_disesuaikan_ap` / `transfer[]`); bukti transfer dari `GET /pengajuan-barang/:id/bukti-transfer`.
- **Badan panel disusun dari komponen modul yang sudah ada** (bukan salinan, bukan mengekstrak `SheetDetailPengajuan` yang merender Sheet utuh): `LinimasaPengajuan` (nama pelaku per langkah), `LampiranPengajuan`, `AksiPersetujuanSheet`, `KartuKonfirmasiTransferPembelian`, `FormCekStok`. Aksi yang perakitannya terikat halaman (transfer AP, isi harga, catat accounting, kedatangan/QC) = satu tombol ke `/pengajuan-barang/<id>`.

### Keputusan panel Tiket (Pemutus irfanarfianto, 2026-10-16)

Diukur ke kode `origin/main` sebelum dibangun (induk bip-erp#3223):
- **Tautan baris tiket = `/task-management/pending/<id>`** (`TriageView`), bukan `/task-management/<id>` (`TaskDetailView`, tanpa aksi triase). Dihitung per baris di `petakanTiket` (`services/employee/antrean_pengajuan.go`).
- **Form triase dan dialog tolak DIEKSTRAK dari `TriageView`** jadi komponen mandiri di modul task-management (`form-triase.tsx`: `useTriase` + `FormTriase`; `dialog-tolak-tiket.tsx`), dipakai bersama halaman triase dan panel. Navigasi lewat callback, bukan `router.push` di dalam komponen.
- **Alasan tolak WAJIB**, berlaku juga di halaman triase karena dialognya dipakai bersama.
- **Panel memuat** keluhan, pemohon · divisi · space, deskripsi, lampiran, form triase (prioritas dengan tenggat otomatis, PIC, tanggal mulai), footer Setujui + Tolak. Syarat Setujui mengikuti `useTriase` (sumber tunggal, logika halaman lama: prioritas dan PIC, kecuali space auto-assign yang punya anggota). **Koreksi tipe dan pindah space tetap di halaman triase.**
- Spanduk tiket menunggu > 7 hari: TBD.

## Irisan 2 dan seterusnya: panel per kategori, urut volume prod

1. **Pengajuan Barang**: aksi `catat`, `transfer`, `konfirmasi_transfer`, `jawab_stok`, `isi_harga`, `putuskan`. Badan memakai `SheetDetailPengajuan`; footer per mode (ADR induk butir 6). Spanduk volume: `catat` ke tabel antrean pencatatan di tab Ringkasan `/finance/tim-accounting` (`antrean-pencatatan-accounting.tsx`; halaman digerbang `finance.accounting.view`, tabelnya hanya bagi pemegang `budget.accounting.pencatatan`, jadi spanduk hanya untuk pemegang izin yang sama), `transfer` ke `/finance/ap`.
2. **Tiket**: aksi `triase`. Spanduk tiket >7 hari bila ambangnya diputus (TBD 1).
3. **Sisanya saat datanya ada.** Pelatihan, Permintaan GA, Permintaan Pembelian, dan Payroll belum perlu (0 data prod 2026-10-15).

*Yang harus benar per panel*:
- Sheet berangka tiga: header tetap, badan `flex-1 min-h-0 overflow-y-auto px-4 pb-4`, footer `SheetFooter`.
- Tolak dan Kembalikan menolak dikirim tanpa alasan.
- Setujui dokumen bernilai uang memunculkan konfirmasi yang menyebut nomor + nominal.
- Sesudah tindakan, panel tertutup, baris hilang, dan hitungan pil turun. Tidak ada tombol "lalu berikutnya".
- Badan memakai komponen detail modul; tidak ada salinan detail baru.
- Spanduk volume tidak tampil bagi yang tak bisa membuka layar tujuannya.
- `AlertDialog` di dalam `Sheet` dicoba dengan tangan termasuk Escape (jsdom buta).

*Repo*: erp-frontend, kecuali kategori yang butuh endpoint baru. *Deploy*: frontend saja bila kontrak irisan 1 sudah naik.

## Kebutuhan terpisah, di luar ADR ini

- **Layar pencatatan massal Accounting.** 288 dokumen menunggu dicatat (median 6,1 hari) dan hari ini dicatat satu per satu di `/pengajuan-barang/[id]`. Perlu atau tidaknya diputus tersendiri; halaman Persetujuan hanya mengarahkan ke antrean yang sudah ada.

## Gotcha yang relevan

- **`data: null` vs kunci hilang**: sumber yang tak punya baris bisa membalas `"data": null`. Bedakan dari kunci absen (`json.RawMessage`); `null` = nol baris, kunci absen = galat (team-memory § Memanggil endpoint DAFTAR).
- **Paginasi sumber bawaan 25**: adapter yang memperlakukan halaman pertama sebagai populasi membuat hitungan pil salah tanpa galat. Periksa tiap sumber; beberapa sudah dicatat tak berpaginasi di komentar `antrean_pengajuan.go`.
- **Sheet berangka tiga** (`ui-checklist.md` §2a): `overflow-y-auto` di badan, bukan di `SheetContent`.
- **i18n dua bahasa** (ADR 0010): label aksi, tahap, penjelasan baku per kode aksi, keadaan kosong.
- **Panduan menu**: `/portal/persetujuan` belum punya panduan di `src/features/panduan/isi/`; isinya yang berubah membuat panduan lebih dibutuhkan. Pemilik untuk menu umum TBD 4.
- **Gerbang lazim satu lapis di atas**: sebelum menyimpulkan sebuah sumber "bocor" atau "tak menyaring pemanggil", baca pendaftaran rutenya dulu.
- Label grup HRGA tidak relevan di sini (antrean disaring per identitas, bukan per departemen).

## Belum Diputuskan (TBD)

1. Ambang 7 hari spanduk tiket.
2. Endpoint riwayat Tiket, Live Support, Permintaan GA, Rekrutmen.
3. Rute per dokumen Live Support, Pelatihan, Permintaan Pembelian, Offer.
4. Pemilik panduan menu umum.
5. Verifikasi tujuan Tiket (`pending/<id>`) dan Booking (`?nomor=`).

## Alur Pengguna

- **Staf tanpa antrean** (mayoritas): buka menu Persetujuan → halaman menjelaskan bahwa di sini muncul keputusan dan tindakan yang menunggunya → klik "Lihat status pengajuan saya" ke menu Pengajuan, atau Riwayat. Titik putus yang dihindari: tabel kosong tanpa kalimat, terbaca rusak; atau staf mencari status pengajuannya sendiri di sini karena namanya "Persetujuan".
- **SPV Finance**: pil "Putuskan" → baris PB tahap `pb_spv_finance` → panel: rincian, nominal, jenjang → Setujui → konfirmasi nomor + nominal → panel tertutup. Baris `pb_spv_transfer` tampil dengan aksi `konfirmasi_transfer` → Konfirmasi transfer, atau Kembalikan ke AP dengan alasan.
- **Staff Accounting**: spanduk "288 menunggu dicatat" → tabel antrean di tab Ringkasan `/finance/tim-accounting`; atau klik satu baris → panel → "Catat di halaman dokumen" → `/pengajuan-barang/[id]`. Titik putus yang diketahui: pencatatan tetap satu per satu (kebutuhan terpisah).
- **AP**: pil "Transfer" → baris `pb_ap_transfer` → panel → tombol ke langkah transfer dokumen itu (atau spanduk ke `/finance/ap`).
- **Gudang GA**: menu Persetujuan → pil "Jawab stok" → PB `pb_cek_stok_ga` → kolom "Yang harus Anda lakukan" menyebut "jawab ketersediaan stok", bukan setujui → panel → tombol ke form jawaban stok dokumen itu. Ini alur yang hari ini buntu.
- **Kepala divisi tiket**: pil "Triase" → tiket tertua di atas → panel / `/task-management/pending/<id>` → pilah. Spanduk >7 hari bila ambang diputus.
- **Direktur**: pil "Putuskan" → keputusan yang menunggunya; baris yang bukan gilirannya tersembunyi di "Pantauan" dan bisa dibuka baca-saja.

## Dokumen Terkait

- [[ADR - 0181 Portal Persetujuan Memuat Keputusan dan Tindakan Operasional]]
- [[ADR - 0114 Antrean Persetujuan Terpusat di Web, Satu Tabel Seragam dari Agregator Employee-Service]] · [[ANALISA - Antrean Persetujuan Terpusat di Web]]
- [[ADR - 0149 Sidebar Satu Daftar Urusan, Menu Digerbang Izin Posisi, Beranda Ruang Kerja Posisi]] · [[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]]
- [[REF - Alur Persetujuan]] · [[Microservices - Employee Service]]
