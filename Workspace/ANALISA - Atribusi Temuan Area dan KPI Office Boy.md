> **Papan kerja**, bukan dokumen arsitektur. Berubah tiap item selesai.
>
> ⚠️ Berkas ini di `Workspace/`, jadi dok yang terbit ke wiki DILARANG menautkannya.

# Atribusi temuan area dan KPI Office Boy

Diukur 2026-09-24 ke `origin/main` `bip-erp` `7b767ec9` dan ke database produksi. Muncul dari satu pertanyaan sederhana yang tidak punya jawaban: **"temuan di lorong masuknya ke mana?"**

## Pertanyaannya tidak bisa dijawab, dan itu temuannya

Lorong adalah **ruang bersama**. Ia bukan orang, dan bukan departemen. Di model data mana pun yang ada sekarang, **lorong tidak punya pemilik**.

Yang sistem tahu soal "tempat" cuma satu, yaitu **departemen**:

- `area_inspection` menyimpan lokasi sebagai **department**, bukan ruangan fisik. Komentar di `services/employee/area_inspection_departments.go:16` menyatakannya terang: *"Ruangan Inspeksi Area = department yang DIPILIH di Sasaran Penilaian form Satgas"*.
- **`services/attendance` tidak mengenal konsep area sama sekali** (nol hit). Jadi tidak ada jejak siapa memegang area mana pada waktu tertentu.
- Tidak ada penyimpanan penugasan area ke orang: `area_tanggung_jawab`, `area_assignment`, `penugasan_area` semuanya **nol** di seluruh `services/`.

⚠️ Penugasan Office Boy juga **tidak tetap** (dinyatakan pemilik proses, 2026-09-24). Jadi bukan cuma belum tersimpan, melainkan memang berpindah.

## Yang terpapar: 0,70 dari 1,00 bobot Office Boy

Template hidup `Office Boy & Girl Staff HRGA` (diukur `kpi_template` prod, periode berskor terakhir 2026-08):

| Metrik | Bobot | Keadaan |
|---|---:|---|
| Rating Pelayanan dan Kebersihan (1-10) | 0,30 | ✅ otomatis, sumber `nilai_layanan_pribadi` |
| Kondisi kebersihan area yang ditugaskan | 0,30 | manual |
| Kondisi perawatan barang/perabotan, tanaman di area yang ditugaskan | 0,25 | manual |
| Pelaksanaan 5R di Area Pantry dan Area Tanggung Jawab | 0,15 | manual |

Ketiga yang manual berbunyi **"area yang ditugaskan"**. Karena penugasannya berpindah dan tidak tercatat, **0,70 bobot menilai kondisi ruang yang kaitannya dengan orang itu tak bisa diperiksa siapa pun.** Temuan hari Rabu di lorong yang Senin dibersihkan A dan Selasa oleh B jatuh ke siapa? Hari ini: ke siapa pun yang dipilih petugas.

## Ini menjelaskan kenapa ADR 0111 benar

[[ADR - 0111 Inspeksi 5R Area per Department sebagai Catatan Non-KPI dengan Peringatan ke Supervisor]] menetapkan inspeksi area **non-KPI**, dan penegakannya struktural (`area_inspection.go`: *"tak pernah menyentuh kpi_score/employee_warning/payroll"*).

Keputusan itu ternyata berdiri di atas alasan yang lebih kuat daripada yang tertulis: **atribusi kondisi ruang bersama ke perorangan memang tidak andal.** Layak dicatat di ADR itu sebagai penguat, bukan sebagai keputusan baru.

## Arah yang disepakati (2026-09-24)

**Ukur PERBUATAN, bukan KONDISI** untuk KPI perorangan, dan lempar kondisi ruang ke jalur area yang sudah non-KPI.

- **Perbuatan** ("giliranmu dikerjakan dan tercatat") melekat pada orangnya dan bisa dibuktikan.
- **Kondisi** ("lorongnya bersih atau tidak") adalah keadaan yang siapa pun bisa menyebabkannya.

Bukti bahwa arah ini bekerja sudah ada di sistem yang sama: `nilai_layanan_pribadi` menilai **pelayanan orangnya**, bukan keadaan ruangan, dan ia satu-satunya sumber KPI GA yang benar-benar hidup — **1.357** jawaban di form "Pelayanan Tim Security" dan **694** di "Pelayanan Tim Office Boy", keduanya masih terisi sampai 2026-09.

Opsi yang **ditolak**: menyimpan giliran lalu mengatribusikan menurut siapa yang bertugas. Ia hanya mungkin bila rotasinya direncanakan, dan pemilik proses menyatakan penugasan OB tidak tetap.

## ⛔ Batas kewenangan: ini bukan keputusan teknis

Mengubah **cara sebuah angka lahir** adalah keputusan arsitektur. Mengubah **apa yang diukur sebuah metrik** bukan. Struktur, bobot, dan isi metrik KPI diatur **SK** (dinyatakan di [[ADR - 0093 Tipe Program Culture Non-Event Dinilai Terlaksana dengan Approval SPV HR, plus Jadwal di Master]]).

Tiga metrik di atas berbunyi "kondisi area". Menggantinya jadi "perbuatan pada giliran" adalah **perumusan ulang metrik**, jadi yang memutuskan **pemilik KPI (HRD)**, bukan tim teknis. Papan ini menyiapkan bahannya, tidak memutuskannya.

Yang dibawa ke pemilik KPI, cukup satu kalimat: *tiga metrik Office Boy berbobot total 0,70 menilai kondisi ruang bersama yang penugasannya berpindah dan tidak tercatat, sehingga angkanya tidak bisa dipertanggungjawabkan; apakah metriknya diubah menjadi perbuatan yang bisa dibuktikan, atau kondisi ruang dipindahkan ke jalur area yang tidak menilai perorangan?*

## Temuan kedua: penyaluran temuan tidak punya aturan

Satu temuan fisik yang sama bisa sah masuk ke tiga tempat, dengan akibat yang berbeda tajam:

| Jenis temuan di lorong | Jalur | Akibat |
|---|---|---|
| kotor, ada OB yang dianggap bertugas | Satgas per-PIC (subjek orang) | memotong KPI orang itu |
| kotor, area milik departemen | Inspeksi Area (subjek departemen) | non-KPI, peringatan ke supervisor |
| rusak (lampu, plafon, keramik) | tiket space `Building Maintenance` | menyuapi `kinerja_tiket` posisi Building |
| bahaya K3 | dicatat sebagai temuan K3 | ⛔ **buntu**, lihat di bawah |

⚠️ Yang memutuskan **petugas yang sama**: izin `kepatuhan.satgas.input` menggerbangi Satgas per-PIC **dan** Inspeksi Area (`gatePetugasSatgas`, `area_inspection.go`). Jadi tidak ada pemisahan pengambil keputusan, dan tidak ada aturan tertulis yang memandu pilihannya. Dua petugas yang melihat lorong yang sama bisa menghasilkan tiga akibat berbeda, dan salah satunya memotong skor seseorang.

## Temuan ketiga: temuan K3 buntu

[[ADR - 0090 Inspeksi Satgas 5R dan K3 di Form Builder dengan Nilai dari Cek Ulang Terakhir]] menyatakannya sendiri: temuan K3 **hanya tercatat, belum punya alur tindak lanjut ke GA**.

Ini yang paling mendesak dari ketiganya, dan bukan karena bobot. Lantai licin atau kabel terbuka yang dicatat tetapi tidak diteruskan ke siapa pun adalah temuan yang **tidak menghasilkan perbaikan apa pun**. K3 justru satu-satunya kategori di sini yang punya konsekuensi di luar skor.

## Keadaan produksi: semuanya kosong

Diukur 2026-09-24 di `employee_db` dan `form_builder_db` prod:

| Koleksi / objek | Isi |
|---|---|
| `area_inspection` | **0** |
| `compliance_note` | **0** |
| form Satgas di form-builder | **nol** dari 20 form |
| `satgas_finding` ([[ADR - 0122 Satgas Per-PIC Input Bebas Gantikan Form Builder, SLA Temuan dan Skor dari Approval]]) | belum ada, kodenya belum ditulis |
| `employee_warning` (SP) | 9 |

Jadi hari ini jawaban sesungguhnya atas "temuan di lorong masuknya ke mana" adalah: **tidak ke mana-mana**. ADR 0090 mencatat pemberitahuan temuan masih lewat **WhatsApp**.

## Langkah berikutnya

| ☐ | Langkah | Siapa |
|---|---|---|
| ☐ | Bawa pertanyaan perumusan ulang tiga metrik OB (0,70) ke pemilik KPI | pemilik KPI, bukan dev |
| ☐ | Tetapkan aturan penyaluran temuan: kapan jadi urusan orang, departemen, atau tiket kerusakan | pemilik proses + GA |
| ☐ | Putuskan alur tindak lanjut temuan K3 ke GA | GA + K3 |
| ☐ | Catat penguat di ADR 0111 (atribusi ruang bersama tidak andal) | dokumentasi |

⚠️ **Tidak ada satu pun di atas yang dimulai dengan menulis kode**, dan itu bukan kebetulan. Tiga mekanisme di lingkup ini sudah dibangun lalu tidak pernah terisi; menambah yang keempat sebelum aturannya jelas akan mengulang hasil yang sama.

## Yang di luar lingkup papan ini

- **Preventive maintenance** sudah punya keputusan sendiri: `Decisions/ADR - 0123 Preventive Maintenance Berjadwal per Aset di Inventory Service, Skor dari Penyelesaian Berbukti.md`, papan kerjanya `Workspace/ANALISA - Preventive Maintenance Berjadwal per Aset.md`.
- **Redesign Satgas per-PIC** ada di ADR 0122 dan papannya sendiri.
