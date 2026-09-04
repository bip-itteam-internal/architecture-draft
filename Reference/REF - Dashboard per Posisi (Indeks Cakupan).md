## Deskripsi

*Indeks lintas divisi untuk keluarga dokumen rancangan dashboard per posisi. Menjawab tiga hal yang tak bisa dijawab satu dok divisi: posisi mana saja yang ada, mana yang sudah punya layar, dan penghambat mana yang muncul di banyak divisi sekaligus sehingga satu pekerjaan membuka banyak metrik.*

- **Status**: 🟡 **Rancangan**. Dokumen turunan; yang menentukan tetap dok divisi masing-masing.
- **Diukur 2026-09-04** terhadap [[HRIS - Matriks KPI per Departemen]] (salinan produksi 2026-08-28, bab Recruitment 2026-09-02, sel PPIC diralat 2026-09-02). ⚠️ **Ukur ulang sebelum dipakai mengambil keputusan.**
- **Prinsipnya** di [[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]]; **tata letaknya** di [[REF - Layout Dashboard erp-frontend]].

## Angka pokok

| | |
|---|---:|
| Divisi | 10 |
| Posisi unik | 54 |
| Template KPI | 70 |
| Baris metrik | 311 |
| Posisi yang **punya lembar dashboard** hari ini | 17 |
| Metrik yang **benar-benar otomatis** di produksi | 10 |
| Metrik dinilai manual | 272 (87,5%) |

**Sepuluh dari 311.** Itu angka yang harus diingat saat membaca sisa dokumen ini: rancangan di seluruh keluarga dok ini sebagian besar adalah daftar kebutuhan backend yang terurut, bukan layar yang siap dibangun.

## Dokumen per divisi

| Divisi | Posisi | Metrik | Dok rancangan | Keadaan layar |
|---|---:|---:|---|---|
| Tech Development | 7 | 30 | [[IT - Dashboard per Posisi]] | ringkasan divisi, tanpa tab posisi. **Lembar per posisi DIBATALKAN**, lihat catatan di bawah |
| Finance | 8 | 61 | [[Finance - Dashboard per Posisi (FAT)]] | 9 posisi bertab, hidup |
| Human Resource | 5 | 31 | [[HRIS - Dashboard per Posisi]] | 5 posisi bertab, hidup |
| General Affair | 4 | 24 | [[GA - Dashboard per Posisi]] | 3 posisi bertab, hidup |
| Procurement | 2 | 10 | [[GA - Dashboard per Posisi]] | belum ada |
| Manufaktur | 8 | 52 | [[Manufacture - Dashboard per Posisi]] | belum ada |
| Beauty Hacks | 10 | 30 | [[Sales - Dashboard per Posisi (Beauty Hacks & Kyura)]] | per topik, bukan per posisi |
| Kyura | 9 | 27 | [[Sales - Dashboard per Posisi (Beauty Hacks & Kyura)]] | per topik, bukan per posisi |
| Kesekretariatan | 7 | 28 | [[Unlisted - Dashboard per Posisi (Kesekretariatan)]] | belum ada |
| Quality | 4 | 18 | [[QA - Dashboard per Posisi]] | belum ada |

⚠️ Beauty Hacks dan Kyura **berbagi delapan posisi** dengan struktur metrik yang sama, sehingga jumlah posisi unik lintas perusahaan 54, bukan 64.

## Penghambat lintas divisi, diurutkan daya ungkit

Dihitung dari 311 baris metrik. **Satu metrik bisa masuk lebih dari satu baris** bila sumbernya menyebut lebih dari satu penghambat, jadi kolomnya tidak dimaksudkan dijumlahkan.

| Penghambat | Metrik | Posisi | Divisi | Jenis pekerjaan |
|---|---:|---:|---:|---|
| **Belum dipetakan sama sekali** | 47 | 28 | 8 | keputusan pemilik KPI |
| **Kaizen** | 19 | 15 | 8 | ⛔ tidak dikerjakan, lihat bawah |
| **Batch Record & Production Log kosong** | 16 | 8 | 2 | pemakaian, bukan kode |
| **Modul checklist berjadwal belum ada** | 14 | 8 | 3 | bangun modul |
| **Tracker pajak / audit internal / CAPA / BPOM** | 13 | 10 | 5 | bangun modul |
| **Tracker garapan desain & video** | 10 | 3 | 2 | bangun modul |
| **Akun buzzer personal, tanpa API** | 10 | 2 | 2 | keputusan cara kerja |
| **Log 1-on-1 tidak ada** | 9 | 7 | 2 | bangun fitur |
| **Master anggaran per departemen** | 9 | 8 | 3 | isi master data |
| **Modul Training kosong di prod** | 8 | 3 | 1 | pemakaian, bukan kode |
| **Meta Ads / akun organik tak terintegrasi** | 7 | 3 | 3 | integrasi baru |
| **Modul demand planning / forecast** | 7 | 7 | 5 | bangun modul |
| **Data percakapan CS tidak ada** | 3 | 3 | 3 | integrasi baru |

### Yang paling penting dibaca dari tabel itu

**Penghambat terbesar bukan pekerjaan backend.** Empat puluh tujuh metrik, tersebar di 28 posisi dan 8 divisi, cuma "belum dipetakan": belum ada yang memutuskan data mana di sistem yang menjawabnya. Itu keputusan pemilik KPI, dan mengerjakannya tidak menuntut satu baris kode. Selama 47 metrik itu menganggur, seberapa banyak pun modul dibangun tidak akan menaikkan cakupan.

⛔ **Kaizen (19 metrik, 15 posisi, 8 divisi) TIDAK dikerjakan dan tidak digambar.** Ia manual **karena keputusan**, bukan karena sistemnya kurang ([[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]]). Modulnya ada dan sumbernya terdaftar. Menaruh panel "menunggu penyambungan data" di 19 tempat akan berbohong tentang sebabnya, dan panel jujur yang terbukti berbohong di satu tempat membuat panel jujur di tempat lain ikut tak dipercaya.

⚠️ **Beberapa metrik bernama `Kaizen` justru bukan Kaizen.** `Kaizen dan Growth` (QA Leader) mengukur review SOP dan WI; `Kaizen 1` dan `Kaizen 2` (Leader Production) mengukur CAPA dan kualitas produk; `Inovation & Improvement` (QA RND) juga bukan. Ketiganya butuh sumber sendiri, dan namanya membuat pemetaan yang keliru terasa benar.

**Dua penghambat terbesar berikutnya bukan permintaan fitur.** Batch Record (16 metrik) dan modul Training (8 metrik) sama-sama sudah ada di kode lengkap dengan koleksinya; yang tidak ada isinya. Keduanya pertanyaan ke tim yang memakai, bukan tiket ke tim pengembang, dan menaruhnya di backlog teknis membuatnya menunggu rilis yang tak pernah relevan.

## Salah petak yang tercatat

Metrik yang **punya** sumber tetapi sumbernya menjawab pertanyaan lain. Ini kelas paling berbahaya di seluruh dokumen ini, karena hasilnya bukan galat melainkan **angka yang masuk akal dan salah**, dan tak ada test yang menangkapnya.

| Posisi | Metrik | Dipetakan ke | Seharusnya soal |
|---|---|---|---|
| Staff Inventory (Procurement) | ketersediaan bahan baku (0,4) | data iklan TikTok | stok produksi |
| Staff Inventory (Procurement) | on time delivery supplier (0,2) | data iklan TikTok | pengiriman pemasok |
| PPIC (Manufaktur) | OTIF finished good (0,2) | data iklan TikTok | pengiriman ke gudang |
| PPIC (Manufaktur) | factory utilization (0,15) | tracker BPOM | utilisasi pabrik |
| HRD Supervisor | monitoring aset (0,05) | data retur | aset |
| Procurement Leader | rebate kontrak vendor (0,1) | kontrak **karyawan** | kontrak vendor |
| Internal Audit | kelengkapan laporan audit (0,25) | data absensi | mutu laporan |
| Personal Assistant | responsivitas ke Direktur (0,15) | chat marketplace | respons asisten |
| Senior Accountant | pengelolaan aset tetap (0,15) | resi & fulfillment gudang | aset tetap akuntansi |
| Junior Accountant | pengelolaan aset (0,15) | resi & fulfillment gudang | aset akuntansi |
| Host Live (Beauty Hacks) | ROI (0,3) | tracker pajak & BPOM | ROI live |
| Recruitment & Onboarding | turnover probation (0,1) | resign sukarela **seluruh perusahaan** | probation saja |

**Dua belas metrik, sembilan posisi, tujuh divisi.** Tiga di antaranya menunjuk data iklan TikTok yang berisi ratusan ribu baris, sehingga akan menghasilkan angka yang mulus dan stabil.

⚠️ **Memperbaikinya harus mendahului merancang layarnya.** Dashboard yang menggambar metrik salah petak memberi kesalahan itu tampilan resmi, dan sejak saat itu ia jauh lebih sulit dicabut.

## Posisi yang dinyatakan TIDAK direkomendasikan

Sesuai [[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]] §4, sebuah posisi yang seluruh KPI-nya manual **dan** tak punya jejak pekerjaan di sistem tidak dibuatkan dashboard sampai sumbernya ada.

| Posisi | Divisi | Sebab | Yang membalikkannya |
|---|---|---|---|
| Office Boy | General Affair | 4 dari 4 metrik menunggu modul checklist | modul checklist berdiri |
| Security | General Affair | 0 dari 4 bersumber | modul checklist, atau buku tamu diakui sebagai metrik |
| Admin Production | Manufaktur | 0 dari 4 bersumber | Batch Record terisi |
| PPIC | Manufaktur | 5 pemetaan bermasalah | tinjau ulang pemetaannya |
| QA Leader | Quality | 0 dari 4 bersumber | Batch Record terisi |
| QC Production | Quality | praktis nol | Batch Record terisi |
| Meta Advertiser | Beauty Hacks & Kyura | Meta Ads tak terintegrasi | integrasi Meta Ads |
| Buzzer | Beauty Hacks & Kyura | akun personal, tanpa API | keputusan cara kerja buzzer |
| Video Editor | Beauty Hacks & Kesekretariatan | tak ada tracker garapan | tracker garapan berdiri |
| Company Branding | Kesekretariatan | akun organik tak terintegrasi | integrasi akun korporat |
| Corporate Secretary | Kesekretariatan | 0 dari 4 bersumber | periksa Calendar & Task Management |
| Graphic Design | Kesekretariatan | tak ada tracker garapan | tracker garapan berdiri |
| Personal Assistant | Kesekretariatan | 0 dari 4 bersumber | periksa Calendar & Task Management |
| Backend / Frontend Developer, IT Infrastructure, Tech Development Supervisor | Tech Development | template arsip, **nol akun aktif** | posisinya diisi lagi |

**Ini jawaban, bukan kegagalan.** Menyatakan sebuah posisi belum layak punya dashboard jauh lebih berguna daripada membangun layar yang seluruhnya panel menunggu, karena layar semacam itu mengajari pemakainya bahwa dashboard memang tidak berisi apa-apa, dan kerusakan itu menular ke layar lain yang sebenarnya berguna.

## ⛔ Sebelum merancang lembar mana pun: periksa `/portal/kpi` dulu

Ditemukan 2026-09-04 saat divisi IT hendak dibangun, dan **berlaku untuk kesepuluh divisi**.

`/portal/kpi` sudah punya kaskade persona yang melayani setiap karyawan: yang punya bawahan mendapat KPI timnya, yang bukan penilai mendapat `KpiSayaView` miliknya sendiri, lengkap dengan pemilih periode, tren, band skor, lencana sumber otomatis/semi/manual, cakupan per metrik, dan unggah bukti.

Akibatnya, **lembar per posisi yang isinya sekadar scorecard KPI adalah duplikat**, dan repo sudah pernah memutuskan untuk menghindarinya: komentar di `portal/kpi/page.tsx` menyatakan kartu skor KPI di dashboard sengaja tidak melayani cakupan "diri" karena *"dua layar yang menjawab pertanyaan sama akan menyimpang, dan yang ini sudah lebih matang"*.

**Yang tetap layak dibangun** adalah yang TIDAK ada di scorecard KPI: angka operasional, antrean pekerjaan, ambang yang perlu ditindak, dan metrik mentah di balik skornya. Divisi IT berakhir dengan dua penambahan kecil semacam itu, bukan tiga lembar ([[IT - Dashboard per Posisi]] § Kenapa lembar per posisi dibatalkan).

⚠️ Tabel di bawah karena itu membaca **kesiapan DATA**, bukan rekomendasi membangun layar. Posisi yang siap datanya tetap bisa berakhir tidak dibuatkan lembar.

## Posisi yang paling siap dibangun

Diurutkan menurut porsi bobot yang sudah punya sumber.

| Posisi | Divisi | Kesiapan | Dokumen |
|---|---|---|---|
| Tech Development Leader | Tech Development | 4 dari 5 metrik ber-`auto` | [[IT - Dashboard per Posisi]] |
| Warehouse Staff | Manufaktur | 3 dari 4, bobot 0,8 | [[Manufacture - Dashboard per Posisi]] |
| Admin Warehouse | Manufaktur | 5 dari 6, bobot 0,9 | [[Manufacture - Dashboard per Posisi]] |
| IT Support | Tech Development | 3 dari 4 | [[IT - Dashboard per Posisi]] |
| Warehouse Leader | Manufaktur | 5 dari 8, bobot 0,7 | [[Manufacture - Dashboard per Posisi]] |
| AR Staff (Piutang) | Finance | bobot 0,9 bersumber | [[Finance - Dashboard per Posisi (FAT)]] |
| Supervisor (BH & Kyura) | Sales | bobot 0,9, menunggu atribusi | [[Sales - Dashboard per Posisi (Beauty Hacks & Kyura)]] |
| ICC | Beauty Hacks & Kyura | 3 dari 3, menunggu atribusi | [[Sales - Dashboard per Posisi (Beauty Hacks & Kyura)]] |
| Personalia | Human Resource | 3 dari 5 | [[HRIS - Dashboard per Posisi]] |

⚠️ Kesiapan Sales **seluruhnya bergantung `icc_account_mappings`**. Datanya paling tebal di perusahaan tetapi tidak beratribut `employee_id`; tanpa jembatan itu layarnya menampilkan angka orang lain tanpa satu pun galat.

## Batas dokumen ini

Tidak menentukan urutan pembangunan antar-divisi, tidak menunjuk pemilik tiap layar, dan tidak memutuskan apakah 17 dashboard yang sudah ada akan diselaraskan mundur ke ADR 0076. Ketiganya keputusan tersendiri.

Seluruh angka bersandar pada **salinan** data produksi bertanggal, bukan sumber hidup. Bila `kpi_template` berubah, dokumen ini basi tanpa ada yang berbunyi.

## Dokumen Terkait

- [[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]] — prinsip penurunannya
- [[REF - Layout Dashboard erp-frontend]] — cara menyusunnya di layar
- [[HRIS - Matriks KPI per Departemen]] — sumber seluruh angka di sini
- [[REF - Penamaan Metrik & Sumber KPI]] — aturan penamaan, penyebab beberapa salah petak di atas
- [[HRIS - Otomasi Skor KPI]] — kelayakan otomasi dan rencana bertahap
- [[RUN - Menambah Metrik KPI Otomatis]] — cara mengerjakan pemetaan yang belum ada
