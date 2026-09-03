# Finance - Audit Internal

## Deskripsi

*Pengujian bulanan atas pembukuan PT Bharata Internasional Pharmaceutical, dijalankan sebagai modul di dalam finance-service yang menarik kedua sisi pembanding lewat pembaca yang sudah ada lalu menyajikan selisihnya sebagai kertas kerja. Sistem membandingkan; auditor menilai, menelusuri, dan menandatangani. Sumbernya BUKAN selalu Accurate — dari 36 pengujian, sisi bersumber Accurate justru minoritas.*

- **Status**: âœ… **Implemented** â€” **LIVE DI PRODUKSI per 2026-09-03**. Backend (bip-erp [#1676](https://github.com/bip-itteam-internal/bip-erp/pull/1676) + [#1679](https://github.com/bip-itteam-internal/bip-erp/pull/1679)) dan layar di Web ERP (erp-frontend [#1429](https://github.com/bip-itteam-internal/erp-frontend/pull/1429)) keduanya sudah di-deploy. Data nyata: `audit_kertas_kerja` 1 periode, `audit_baris` **36 uji**. âš ï¸ Yang belum: paket izin `Audit: *` belum ditugaskan ke satu akun pun, sehingga belum ada yang benar-benar memakainya.
- **Implementasi**: [[Microservices - Procurement Service]] dan [[Microservices - Integration Service]] sebagai sumber; modulnya sendiri di `bip-erp/services/finance/audit_*.go`; layarnya di `erp-frontend/src/app/(main)/audit/*` + `src/features/audit/*`
- **Keputusan**: [[ADR - 0073 Modul Audit Internal di finance-service dan Kertas Kerja yang Dipegang Sendiri]], diamandemen [[ADR - 0074 Audit Internal Dipisah jadi Service dan Aplikasi Sendiri]]
- ⛔ **Modul ini AKAN PINDAH** keluar `finance-service` jadi service + database sendiri, dan layarnya keluar `erp-frontend` jadi [[APP - Audit Internal]]. Dok ini tetap memegang domainnya — 36 uji, semantik kolom, dan aturan layar — apa pun rumahnya. Papan kerjanya [[ANALISA - Audit Internal Terpisah]].

## Latar Belakang

Auditnya sudah berjalan manual dan prosedurnya sudah terbukti sekali dipakai, dengan kertas kerja posisi **6 Agustus 2026** sebagai baseline. Yang membakar waktu bukan pengujiannya melainkan perakitan kertas kerjanya: menarik data, mencocokkan, dan menyusun ulang dari nol tiap bulan.

Baseline itu memunculkan angka yang jadi contoh uji yang berbunyi: selisih buku besar terhadap buku pembantu piutang Rp 954,7 juta, saldo barang dalam proses minus Rp 164 juta, harga pokok penjualan 13,4% dari pendapatan, PPN keluaran Rp 295 juta atas pendapatan Rp 70,6 miliar, 13 akun tanpa 2FA, dan proses akhir bulan tertinggal dua bulan.

**Independensi justru menguat.** Dokumen prosedurnya menulis bahwa otomasi tidak memperbaiki independensi karena datanya tetap diekspor manusia. Itu benar untuk ekspor Excel, tidak berlaku di sini: ERP menarik lewat kredensial sistem, sehingga angka yang diperiksa tidak pernah melewati tangan divisi yang diaudit.

## Ruang Lingkup / Cakupan

### 36 uji, tiga kelompok menurut asal sisi pembandingnya

Pengelompokan ini yang menentukan kekuatan tiap uji, bukan kecanggihannya.

| Kelompok | Sisi pembandingnya | Jumlah | Kekuatannya |
|---|---|---|---|
| 1 | Dari luar perusahaan: rekening koran, jawaban pelanggan, hitung fisik, akta | 12 (8 campuran, 4 manual) | **Paling kuat.** Tak seorang pun di dalam Bharata bisa mengarangnya |
| 2 | Dokumen internal di luar Accurate: surat jalan, berita acara, perintah kerja, PO dari CV | 8 (7 campuran, 1 manual) | Bisa dipalsukan, tapi menuntut usaha dan meninggalkan jejak fisik |
| 3 | Pembandingnya **aturan**, bukan data: logika akuntansi, ambang batas, standar konfigurasi Direksi | 16 (12 sistem, 4 campuran) | Bertahan menghadapi pembukuan yang dirapikan utuh |

⛔ **Tiga belas uji yang membandingkan neraca dengan laporan pendukungnya sudah DIKELUARKAN** — piutang terhadap umur piutang, persediaan terhadap kartu stok, aset tetap terhadap register, dan seterusnya. Kedua sisinya sama-sama tarikan dari basis data yang sama, sehingga pihak yang mampu mengubah pembukuan secara utuh tidak tertangkap di sana. Hasilnya cepat dan rapi, tapi keyakinan yang diberikannya semu.

⚠️ **Konsekuensi yang harus disadari:** dua dari empat temuan utama kertas kerja 6 Agustus lahir dari uji yang dikeluarkan itu (selisih piutang Rp 954,7 juta dan PPN keluaran 0,42%). Kriteria "bertahan menghadapi pembukuan yang dirapikan utuh" tepat untuk menilai kekuatannya sebagai **deteksi**, tetapi ikut membuang kemampuannya sebagai **akurasi** — dan selisih piutang jauh lebih mungkin lahir dari kesalahan pembukuan daripada kecurangan. **Belum diputuskan** apakah kelompok itu dihidupkan kembali sebagai kelompok "konsistensi internal" berlabel jujur; lihat TBD.

### Tiap uji punya kolom tujuan dan kondisi ideal

- **Tujuan** mengacu tiga sasaran yang ditetapkan: **akurasi** (ketepatan angka), **deteksi** (indikasi kecurangan), **mitigasi** (menutup peluang). Yang pertama disebut adalah sasaran utamanya.
- **Kondisi ideal** menyatakan hasil yang dianggap bersih. Tanpanya, tiap uji butuh penafsir untuk memutuskan apa yang dianggap bersih, dan penafsirnya berganti tiap bulan. Setiap penyimpangan dari kondisi ideal jadi calon temuan.

### Enam uji sudah punya penjalan otomatis

| Uji | Sisi A | Sisi B | Keadaan |
|---|---|---|---|
| Silang pemasok terhadap karyawan | ERP procurement | ERP employee | Menunggu dua endpoint dibangun |
| Saldo kas berjalan tidak negatif | Accurate, buku besar per akun | aturan | Jalan, menunggu setelan akun |
| Barang dalam proses tidak negatif | Accurate, saldo akun | aturan | Jalan, menunggu setelan akun |
| Hitung ulang penyusutan | Accurate, register aset | aturan | Jalan |
| Deskripsi jurnal | Accurate, jurnal umum | standar kelengkapan | Jalan |
| Jurnal manual besar | Accurate, jurnal umum | dokumen sumber | Pemilihan jalan; pembandingnya menunggu manusia |

Tiga puluh sisanya **terdaftar dan terbit di kertas kerja** berkeadaan `belum_diimplementasi`. Uji yang hilang dari daftar akan terbaca sebagai uji yang lolos, dan itu kelas kesalahan paling mahal di modul ini.

### Yang TIDAK dicakup

- **Pembukuan 40 CV.** Terkunci [[ADR - 0068 Buku Besar Konsolidasi 40 CV di Luar Accurate]]; sistemnya di [[APP - Buku Besar Konsolidasi CV FINCON]].
- **Kesimpulan kecurangan.** Modul menunjukkan selisih lalu berhenti.
- **Sembilan prosedur yang menuntut kehadiran fisik, korespondensi resmi, atau tanda tangan.**

## Sampling: sepuluh uji, dan separuhnya justru tidak boleh acak

Dari 36 uji, **sepuluh menuntut pemilihan sampel**; 26 sisanya atas populasi penuh. Nol dari 16 uji kelompok 3 butuh sampling, dan itu imbalan terbesar otomasi: sampling ada karena manusia tak sanggup memeriksa semuanya, bukan karena memeriksa sebagian lebih baik.

⚠️ **Acak dan terarah menjawab pertanyaan yang BERBEDA.** Lima menuntut acak (konfirmasi saldo pelanggan, stock opname, cek fisik aset, retur penjualan, penyesuaian persediaan) karena kesimpulannya diekstrapolasi ke populasi dan karena yang diperiksa tak boleh bisa menebak. Lima lagi justru harus terarah (jurnal manual besar, kapitalisasi versus beban, pisah batas penjualan, varian produksi, penjualan PT ke CV) karena yang dicari memang yang bernilai besar atau berisiko. Sampel acak untuk "20 jurnal terbesar" akan melewatkan jurnal terbesar.

**Cash opname butuh waktu yang acak, bukan item yang acak.** Ia menghitung seluruh kas; yang harus tak terduga adalah harinya, dan keacakan itu gampang hilang begitu jadwalnya tersimpan di kalender yang bisa dilihat orang.

**Ukuran sampel adalah master data Direksi**, berlantai 5 untuk metode acak, berbenih tak tertebak, dan berjejak. Yang tersimpan bukan hanya yang terpilih melainkan juga ukuran populasi, metode, dan benihnya — tanpa ketiganya sampel tak bisa direproduksi dan auditor tak punya cara membuktikan ia tidak memilih yang mudah.

## Alur Bulanan

- **H+1** — verifikasi Modul G lebih dulu. Selama pembatasan tanggal transaksi terbuka dan hak hapus melekat, bukti yang dikejar modul lain masih bisa berubah di tengah pengujian.
- **H+2** — penarikan otomatis lewat kredensial sistem. Kertas kerja dibuka tanggal 6, bukan 1: pemeriksaan berjalan atas bulan yang **sudah** ditutup.
- **H+3** — uji berjalan.
- **H+4 sampai H+7** — penelusuran manusia ke dokumen sumber, lalu klarifikasi ke auditee.
- **H+8** — laporan ditandatangani dan diserahkan ke Direktur. Periode yang sudah diterbitkan **menolak ditarik ulang**.

Pengisian berlangsung berhari-hari, sehingga kertas kerja **wajib bisa disimpan sebagian**. Ini salah satu alasan form-builder tidak dipakai.

## Tiga Layar, dan Kategori Sidebarnya Sendiri

Rute `/audit` (kertas kerja bulanan), `/audit/temuan` (register temuan), `/audit/setelan` (ukuran sampel). Ketiganya memakai struktur tabel HRIS dan mengambil daftar 36 uji dari `GET /audit/uji` — daftarnya **tidak** disalin ke sisi layar, sebab tiap uji butuh implementasi pembandingnya dan salinan di layar akan menyimpang jadi baris yang tampil tanpa pernah dijalankan siapa pun.

⛔ **Kategori sidebarnya `audit`, berdiri sendiri, bukan menumpang FAT.** Frontend memotong tiap izin di titik pertama untuk menentukan kategori, jadi izin ber-prefiks `finance` akan memunculkan seluruh menu keuangan bagi auditor. Yang lebih menentukan arah sebaliknya: menyatukannya membuat pemegang izin finance ikut membuka kertas kerja yang memeriksa pekerjaannya sendiri, dan pemisahan itu justru inti modul ini.

⚠️ **Kategori ini lahir HANYA dari paket izin, tak pernah dari `system_roles`.** Tidak ada `system_roles.audit`, dan `AuditTierDefault` mengembalikan kosong untuk tier apa pun, jadi tak seorang pun mendapat modul ini karena kebetulan supervisor di modul lain. Yang belum ditugaskan salah satu paket `Audit: *` tidak melihat kategorinya — itu keadaan yang benar, bukan kerusakan.

⚠️ **DENGAN SATU PENGECUALIAN yang berlaku di seluruh aplikasi**: super-akses sidebar (`aksesSemuaMenu` — IT supervisor **atau** jabatan Direktur) meloloskan tiap item **sebelum** `perm` dinilai, kecuali izin yang terdaftar di `TANPA_BYPASS_SEMUA_MENU`. Izin audit sengaja **tidak** didaftarkan di sana, mengikuti modul lain yang tier defaultnya juga kosong (`BudgetTierDefault`, `KasKecilTierDefault`). Konsekuensinya jujur: keduanya melihat menu audit tanpa paket apa pun, lalu backend menolak. Untuk Direktur itu justru yang diinginkan — ia memang pemakai `/audit/setelan`, tinggal dipasangi paket `Audit: Direksi`. Untuk supervisor IT di luar Tech Development itu alur terputus yang diterima sadar, sama seperti modul lain. Bila kelak dinilai tak dapat diterima, obatnya menambahkan keempat izin ke `TANPA_BYPASS_SEMUA_MENU`, bukan mengubah tier default.

⚠️ **Gerbang TOMBOL tidak kena pengecualian itu.** `bolehMenu` — yang dipakai `features/audit/lib/izin.ts` — tak punya bypass super-akses; bypass itu hanya hidup di `bolehItemSidebar`. Jadi pemegang super-akses tanpa paket melihat menunya, membuka halamannya, dan **tidak** melihat satu pun tombol aksi. Itu perilaku yang benar dan disengaja.

### Pemetaan aksi layar → izin: TIGA izin tulis, bukan satu

⛔ Aturan ini sebelumnya hanya hidup sebagai gerbang rute di `audit_handler.go`, dan layar pertama yang dirancang dari dokumentasi memang melewatkannya seluruhnya — ketiga tombolnya tampil untuk semua pemegang `audit.view`.

| Aksi di layar | Endpoint | Izin | Auditor | Direksi | Pembaca |
|---|---|---|---|---|---|
| Membaca kertas kerja, temuan, setelan | `GET /audit/*` | `audit.view` | ✅ | ✅ | ✅ |
| Tarik ulang periode | `POST /periode/:periode/tarik` | `audit.tinjau` | ✅ | — | — |
| Tandai wajar (+ alasan) | `PATCH /periode/:periode/baris/:kode/tinjau` | `audit.tinjau` | ✅ | — | — |
| Terbitkan temuan | `POST /periode/:periode/baris/:kode/temuan` | `audit.temuan.terbitkan` | ✅ | — | — |
| Simpan ukuran sampel | `PUT /setelan-sampel/:kode` | `audit.master.save` | — | ✅ | — |

Tiga hal yang mudah salah dan sudah terbukti salah sekali:

- ⛔ **`audit.tinjau` dan `audit.temuan.terbitkan` BUKAN satu izin.** Menggerbangi tombol "Jadikan temuan" dengan `audit.tinjau` membuka formulir lima unsur bagi orang yang baru ditolak **setelah** semuanya selesai diketik.
- ⚠️ **Membaca setelan sampel hanya butuh `audit.view`**, jadi auditor memang boleh melihat berapa sampel yang ditetapkan untuknya — ia perlu tahu bebannya. Yang disembunyikan kolom aksinya, bukan halamannya.
- ⚠️ **Direksi dan Pembaca sama-sama memegang `audit.view`**, sehingga keduanya **rutin** membuka kertas kerja tanpa satu pun izin tulis. Tombol yang pasti dijawab 403 membuat pemakainya menyimpulkan sistemnya rusak, bukan bahwa meninjau memang bukan tugasnya.

Penjaga sebenarnya tetap backend: menyembunyikan menu maupun tombol **bukan keamanan** ([[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]], ditegaskan ulang [[ADR - 0031 Prefix internal Bukan Batas Keamanan]]). Yang dikerjakan gerbang layar hanya mencegah **alur terputus**. Di frontend pemetaannya tinggal di satu berkas, `features/audit/lib/izin.ts`.

### Keadaan baris dihitung backend, tidak di layar

Layar membaca `keadaan_efektif` dari respons dan **tidak** menghitung ulang urutan menang antara vonis manusia dan keadaan mesin. Itu satu fakta; dua salinannya pasti menyimpang tanpa satu pun galat, lalu tabel dan kartu ringkasan menampilkan keadaan berbeda untuk baris yang sama. Bila field itu tidak dikirim (backend sebelum bip-erp #1679), layar menandainya **eksplisit** alih-alih menebak dari `hasil.keadaan` — sel kosong maupun tebakan sama-sama terbaca sebagai baris yang belum diperiksa.

⛔ **Baris `menunggu_data` dan `belum_diimplementasi` tidak disembunyikan, dan tidak boleh disembunyikan sebagai perilaku bawaan.** Tiga puluh dari 36 uji berkeadaan belum berimplementasi; daftar yang "dibersihkan" menyisakan segelintir baris hijau dan memberi kesan pemeriksaan jauh lebih lengkap daripada kenyataannya. Urutannya menaikkan **kelompok 1**, bukan yang paling merah: uji berpembanding dari luar perusahaan paling sulit dikalahkan, jadi keadaan pengerjaannya yang paling perlu terlihat lebih dulu.

### Urutan deploy: BE sebelum FE, dan kenapa itu sempat mengikat

✅ **Sudah tidak mengikat lagi** — [#1679](https://github.com/bip-itteam-internal/bip-erp/pull/1679) merged, jadi `bip-erp/main` kini mengirim field JSON `keadaan_efektif` (`audit_handler.go` memanggil `IsiKeadaanEfektif` sebelum membalas).

Dicatat karena bentuknya akan berulang. Sebelum #1679, `main` hanya punya **metode** Go `KeadaanEfektif()` yang dipakai internal untuk jejak — bukan field yang terkirim. Layar membacanya dari respons dan sengaja menolak menebak dari `hasil.keadaan`, jadi FE yang naik lebih dulu akan menampilkan "tak terbaca" di **seluruh** baris, bukan sebagian.

⚠️ **Yang tetap berlaku saat deploy**: naikkan `finance-service` sebelum atau bersama frontend. Penanda "tak terbaca" memang dirancang, tetapi sebagai penanda **sementara** — kalau ia yang terlihat setelah deploy, yang salah urutannya, bukan layarnya.
## Persona / Pengguna| Persona | Peran & Divisi | Akses / RBAC | Device |
|---|---|---|---|
| Auditor internal | Posisinya **belum ada**; direncanakan | `audit_auditor` (view, tinjau, terbitkan) | Web ERP |
| Reviewer silang | Staf dari divisi di luar yang diaudit | `audit_auditor` | Web ERP |
| Direktur | Penerima laporan, penyetel ukuran sampel | `audit_direksi` (view, master.save) | Web ERP |

- **Tujuan**: memastikan ketepatan angka, mendeteksi indikasi kecurangan, dan menutup peluangnya.
- **Pain point**: kertas kerja dirakit ulang dari nol tiap bulan, dan datanya diminta dari divisi yang sedang diperiksa.
- **Aksi utama**: meninjau baris yang berbunyi, menelusuri ke dokumen sumber, menandai wajar dengan alasan tertulis, atau menaikkannya jadi temuan.

⛔ **Finance bukan pemakai modul ini**, melainkan pihak yang dimintai klarifikasi.
⛔ **Direktur tidak meninjau, auditor tidak menyetel ukuran sampel.** Yang menetapkan beban pemeriksaan bukan yang mengerjakannya.

## Aturan yang Wajib Dibaca Sebelum Merancang Layar

Aturan berikut selama ini hanya hidup sebagai komentar Go, sehingga siapa pun yang merancang layar dari dokumentasi tidak punya cara mengetahuinya. Salah memakainya menghasilkan **angka salah yang masuk akal**, tanpa galat dan tanpa test merah.

### Semantik kolom

- ⛔ **Aset tetap: `kuantitas` adalah `quantityAvailable`** (sisa, sudah dikurangi pelepasan), **bukan** `quantity` (perolehan awal). `biaya_perolehan` juga basis current. **Mencampur biaya current dengan kuantitas perolehan salah dua kali.**
- ⛔ **`BelumDidepresiasi` HIMPUNAN BAGIAN dari `TotalAset`.** Aset draft dikecualikan; penyusutannya selalu nol.
- ⛔ **Piutang historis: `lebih14` ⊇ `lebih60` ⊇ `lebih90` BERSARANG. Jangan dijumlahkan.**
- ✅ Umur piutang B2B: ember `0-30`, `31-60`, `61+` **partisi saling lepas**. Boleh dijumlahkan.
- ⛔ **Umur utang: `TanpaJatuhTempo` wajib dipisah**, dan **`TotalUangMuka` berpopulasi SAMA tetapi berdimensi BERBEDA** — bukan subset, bukan komponen.
- ⛔ **PPN: `TotalDPP` dan `TotalPPN` HANYA dari subset `Taxable`.**
- ⛔ **Jurnal: `Amount` + `AmountType` adalah SATU nilai bertanda implisit**, bukan dua kolom sejajar.
- ⛔ **Buku besar per akun: `Nominal` turunan bertanda `Debit − Kredit`.** Akun beban sesekali menerima kredit.
- ⛔ **Realisasi per departemen wajib `glaccount/get-balance.do`**, bukan `get-pl-account-amount.do` yang mengabaikan `departmentName` diam-diam.

### Semantik keadaan baris

- ⛔ **Tidak ada keadaan "kosong".** Penarikan yang gagal berkeadaan `gagal_tarik` beserta sebabnya, bukan bersih bernilai nol.
- ⛔ **Vonis manusia (`keadaan_tinjauan`) hidup DI LUAR hasil mesin**, dan yang dibaca layar `KeadaanEfektif()` — vonis menang atas keadaan mesin. Menyalin urutan menang itu ke sisi layar melahirkan sumber kebenaran kedua.
- ⛔ **Frontend WAJIB membaca daftar 36 uji dari `GET /audit/uji`**, jangan menyalinnya. Salinan di layar menyimpang jadi baris yang tampil tanpa pernah dijalankan.
- ⚠️ **Hasil kelompok 3 tidak boleh jadi ringkasan teratas**, dan urutan daftar menaikkan kelompok 1. Layar yang membuka dengan uji hijau memproduksi rasa aman yang tidak dijamin ujinya.

## Konsumen Data

- [[APP - Web ERP]] â€” layar kertas kerja, register temuan, dan ukuran sampel; kategori sidebar `audit` tersendiri (**live di prod 2026-09-03**). Akan dicabut setelah [[APP - Audit Internal]] berjalan.
- Direktur — laporan bulanan; penerimanya orang, bukan sistem

## Kendala

- **Master pemasok tidak menyimpan nomor rekening sama sekali.** Sumbu silang yang dipakai: NPWP, NIK, nama, alamat, telepon, email. Kondisi ideal uji itu wajib menyebut batasnya, kalau tidak laporannya terbaca sebagai "rekening sudah diperiksa dan bersih".
- **Schema resmi Accurate tidak lengkap**; tiga endpoint yang dipanggil produksi tidak terdaftar di sana. Ketiadaan di schema bukan bukti.
- **Limiter Accurate 6 permintaan per detik dibagi lintas service**, dan sudah ada tiga klien terpisah.
- ⚠️ **`finance-service` tidak ada di `docker-compose.dev.yml`**, jadi modul ini **tak dapat dicoba di dev sama sekali** — yang ada hanya `FINANCE_MODULE_URL` di blok gateway, dan portnya sempat ditulis mati `9999` alih-alih `${FINANCE_SERVICE_PORT}`, satu-satunya dari 22 module URL yang begitu. Konsekuensinya terbalik dari kebiasaan: yang hidup justru PRODUKSI, sehingga percobaan menulis (tinjau, terbitkan temuan) tidak punya tempat latihan yang aman.
- ⚠️ **`INTEGRATION_SERVICE_KEY` kosong di dev, terisi di prod.** Buku besar per akun karena itu hanya terjangkau di produksi; di dev uji yang memakainya berkeadaan `gagal_tarik` dengan sebab terbaca — bukan bersih.
- **Pemakai utamanya belum ada.**

## Belum Diputuskan (TBD)

- Apakah Accurate mengirim jejak pelaku pada dokumennya. **Menyandera dua uji** (waktu pembuatan transaksi, sebaran aktivitas pengguna).
- Apakah `access-privilege/list.do` benar-benar dapat ditarik. **Menyandera seluruh Modul G**; lock period, konfigurasi penyetuju, dan status 2FA belum ditemukan di schema mana pun.
- Apakah dokumen Bayar Uang membawa rekening penerima.
- Apakah tiga belas uji konsistensi internal dihidupkan kembali sebagai kelompok berlabel jujur, mengingat dua temuan utama baseline lahir dari sana.
- Angka kapasitas produksi normal PSAK 14 untuk uji alokasi biaya konversi — tidak ada di sistem mana pun, penetapannya keputusan Finance.
- Ambang tiap uji yang pembandingnya aturan (batas nilai persetujuan, kebijakan diskon), sebagiannya menuntut kebijakan tertulis yang belum ada.
- Kapan cakupan diperluas ke pembukuan 40 CV.

## Dokumen Terkait

- [[ADR - 0073 Modul Audit Internal di finance-service dan Kertas Kerja yang Dipegang Sendiri]]
- [[ADR - 0001 Akuntansi via Accurate]] · [[ADR - 0068 Buku Besar Konsolidasi 40 CV di Luar Accurate]]
- [[API - Integration Service]] · [[Microservices - Integration Service]] · [[External - Accurate]]
- [[Finance - Big Pictures]] · [[Finance - Rancangan Finance Service]] · [[Finance - Dashboard per Posisi (FAT)]]
- [[APP - Buku Besar Konsolidasi CV FINCON]] · [[CORE - RBAC dan Permission Set]]
