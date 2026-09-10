## Deskripsi

*Cara kerja psikotes **multi-jenis**: katalog tipe tes, bank soal, dan paket tes yang dikelola HRD sendiri, dijalankan oleh tiga mesin penilaian yang tetap berupa kode. Keputusan dan alasannya ada di [[ADR - 0087 Katalog Tipe Psikotes Jadi Master Data, Tiga Bentuk Jawaban Tetap Kode]]; dokumen ini menyimpan cara kerjanya. Jenis tes yang sudah berjalan hari ini dirinci di [[HRIS - Psikotes Kraepelin]].*

- **Status**: 🟡 **Direncanakan (Design)** — belum ada kode. Rencana disetujui 2026-09-10. Papan kerja: `Workspace/ANALISA - Psikotes Multi-Jenis.md`
- **Sisi implementasi**: [[Microservices - Recruitment Service]] (BE) + [[APP - Web ERP]] (FE). Endpoint → [[API - Recruitment Service]]
- **Grounded ke `origin/main` 2026-09-10.** Checkout lokal repo kode di mesin dev tertinggal ratusan commit dan sempat menyesatkan analisis ini sendiri; klaim tentang keadaan kode di dokumen ini diuji ke ref remote, bukan ke berkas di disk

## Latar Belakang

CFIT dan DISC masih dikerjakan kandidat **di kertas** lalu **dikoreksi HR dengan tangan**, dan bebannya menumpuk musiman saat lowongan dibuka. Kraepelin sudah online sejak 2026-09-09 tetapi berdiri sendiri: nol percabangan berdasarkan jenis tes di seluruh jalur eksekusinya, dan bentuk penyimpanan soalnya hanya mengenal deret angka per kolom.

Yang diminta manajemen adalah tiga menu. Yang dibutuhkan adalah berhentinya koreksi manual. Pembedaan itu, beserta akibatnya pada urutan kerja, dicatat di ADR 0087 `## Context`.

## Ruang Lingkup

**Masuk:** katalog tipe tes, bank soal per tipe, paket tes per posisi, tiga mesin penilaian, halaman laporan hasil, dan impor soal dari Excel.

**Tidak masuk:** konversi skor ke IQ atau profil, kesimpulan naratif otomatis, tabel norma, keputusan lolos atau gugur otomatis, dan bentuk jawaban di luar tiga yang dibangun.

## Tiga Bentuk Jawaban

`jenis_jawaban` adalah **kontrak antara katalog dan mesin**, dan nilainya daftar-izin tertutup yang dijaga kode. Ini yang menentukan sampai mana "tanpa coding" berlaku.

| `jenis_jawaban` | Bentuk soal | Yang dihitung | Timer | Dipakai |
|---|---|---|---|---|
| `pilihan_ganda` | teks dan/atau gambar, satu kunci benar | benar/salah → skor mentah per subtes | per subtes | CFIT |
| `most_least` | satu grup berisi empat kata sifat | tally empat dimensi, **tanpa benar/salah** | tidak ada (untimed) | DISC |
| `angka_kolom` | deret digit per kolom | kecepatan, ketelitian, keajegan, ketahanan | per kolom | Kraepelin |

Tipe tes yang menunjuk `jenis_jawaban` yang belum ada mesinnya **ditolak saat disimpan**, bukan gagal saat kandidat mengerjakannya. Menambah bentuk keempat wajib lewat ADR baru.

## Model Data

Tiga koleksi baru di `recruitment_db`, service pemiliknya recruitment ([[REF - Kepemilikan Data]]).

**`psikotes_tipe`** — katalog yang dikelola HRD.
`nama` · `deskripsi` · `jenis_jawaban` · `punya_subtes` + `subtes[]` (nama, jumlah soal, durasi) · `punya_timer` + durasi · `status` aktif/nonaktif.

**`psikotes_item`** — bank soal per tipe tes.
Bentuk isinya mengikuti `jenis_jawaban` tipe induknya: `pilihan_ganda` menyimpan pertanyaan, opsi, dan **satu kunci benar**; `most_least` menyimpan satu grup empat kata sifat beserta pemetaan dimensinya; `angka_kolom` **tidak menyimpan item sama sekali** karena soalnya dibangkitkan otomatis.

> ⛔ Namanya sengaja **bukan** "bank soal" telanjang. Istilah itu sudah dipakai desain LMS People Development untuk quiz karyawan internal. Menurut [[REF - Kepemilikan Data]] itu **dua fakta berbeda, bukan salinan**, dan yang dilarang adalah membiarkan keduanya lahir tanpa ada yang tahu ada dua.

**`psikotes_paket`** — susunan tes per posisi (mis. "Paket Staff").
Daftar tipe tes **berurutan**, masing-masing bisa dinyalakan atau dimatikan tanpa dihapus. Total waktu paket **diturunkan** dari penjumlahan durasi tipe yang aktif, tidak diketik tangan.

⚠️ **Menonaktifkan sebuah tipe tidak boleh mengunci paket atau sesi lama yang terlanjur memakainya.** Aturan berlaku saat sesuatu ditetapkan, bukan saat disunting ([[ADR - 0041 Izin Tipe Form Menempel di Departemen]]); kelas bug ini sudah pernah dibayar di form-builder saat sebuah tipe dihapus.

**`psikotes_session`** (sudah ada, diperluas). Satu paket dijalankan sebagai **satu sesi**, jadi index unik `(candidate_id, round_id)` **tidak disentuh**. Sub-progres per bagian disimpan di dalam sesi. Nilai `config`, `soal`, dan `hasil` sudah bertipe bebas, dan itu memang disengaja sejak awal.

## Alur Pengguna

**HRD menyiapkan (sekali, lalu sesekali):** buat tipe tes → isi bank soalnya (manual atau impor Excel, gambar diunggah untuk CFIT) → susun paket per posisi, atur urutan dan nyala/mati.

**HRD menjalankan (per kandidat):** kandidat di babak Psikotest → HR memilih paket → kandidat menerima **satu tautan**.

**Kandidat:** buka tautan tanpa login → sapaan → instruksi → mengerjakan seluruh paket **berurutan sekali duduk** → selesai. Bila terputus, ia melanjutkan dari bagian yang belum selesai.

**HRD membaca:** skor mentah dan grafik per tipe tes di halaman laporan. **Keputusan lolos atau tidak tetap di HR**; sistem berhenti di `Pending` dan tidak pernah menetapkan nasib kandidat.

## Yang Dipakai Ulang

| Kebutuhan | Yang sudah ada |
|---|---|
| Sesi bertoken, magic link, status, idempotensi, sapuan kedaluwarsa | `psikotes_session` dan perkakasnya, sudah jenis-agnostik |
| Kerangka layar kandidat | sapaan → instruksi → tes → selesai, lanjut-setelah-putus, retry berlapis |
| Pola mesin pilihan ganda | `services/learning`: snapshot soal saat mulai, **timer ditegakkan server**, pencocokan lewat id soal sehingga pengacakan aman, kunci dibuang saat serialisasi. **Polanya**, bukan kodenya |
| Urutan + nyala/mati | `AssessmentTypeIDs` yang sudah terurut, dan flag `Mandatory` |
| Master bersub-struktur | dialog template onboarding: header + baris item dinamis berfield angka |
| Impor Excel | `exceljs` + pembaca sheet bersama di FE; di BE pola dry-run dengan `expected_hash` dan penolakan 409 bila berkas berubah antara pratinjau dan simpan |
| Unggah banyak gambar | pola `multiple` + grid thumbnail + hapus per gambar |
| Struktur tabel | `MainTable` + `useTableState` + `Banner bare` di `toolbar`, sudah dipakai 8 halaman rekrutmen |

## Yang Perlu Dibangun Baru

- **Dispatcher `jenis_jawaban`.** Saat ini **nol** percabangan berdasarkan jenis: sepuluh titik pemanggilan di tiga berkas memanggil Kraepelin langsung, dan jenis sesi ditulis konstan, tidak pernah dari input HR.
- **Bentuk penyimpanan soal untuk `pilihan_ganda` dan `most_least`.** Jembatan yang ada hanya menulis dan membaca dua kunci, sehingga apa pun di luar itu **hilang senyap** pada perjalanan bolak-balik.
- **Gambar pada soal**, termasuk batas ukuran dan allowlist tipe berkas yang harus ditulis sendiri: unggahan recruitment saat ini **tidak punya keduanya**, satu-satunya pagar adalah batas body service.
- **Halaman laporan hasil.** Komponennya sudah jadi dan sudah ada test-nya, tetapi belum pernah di-import di berkas mana pun.
- **Tiga halaman pengelolaan** di Pengaturan Rekrutmen. Pola `LookupPage` yang ada **tidak cukup** karena bentuknya datar tanpa slot sub-koleksi.

⚠️ **Pengurutan memakai tombol naik dan turun, bukan drag-and-drop.** Repo tidak punya satu pun pustaka DnD maupun implementasi buatan sendiri; dua komponen pengurut bertombol sudah terbukti dipakai. Tab baru di Pengaturan wajib ditambahkan **di ujung** supaya tautan `?tab=` lama tidak bergeser.

## Jebakan yang Sudah Diketahui

- ⛔ **Titik dispatcher yang terlewat tidak akan berbunyi sebagai galat.** Ia akan menilai DISC dengan rumus Kraepelin dan menghasilkan angka yang masuk akal. Tiap titik wajib punya test yang menguncinya.
- ⛔ **Menyembunyikan kunci jawaban dengan tag `json:"-"` mematikan penguraian body**, sehingga seluruh kunci tersimpan bernilai nol. Ini bug nyata yang sudah dibayar di LMS dan komentarnya masih ada di sana; baca sebelum meniru.
- ⛔ **Mengganti spesifikasi index tidak terjadi lewat deploy.** Mongo menolak diam-diam, penjaganya cuma log, dan index lama tetap berlaku sementara build tampak sukses. Karena itu paket sengaja dijalankan sebagai satu sesi.
- ⚠️ **Sesi yang berakhir `ditinggalkan` atau `kedaluwarsa` tetap menghasilkan skor.** Diukur di prod 2026-09-10: 2 dari 2 hasil tersimpan adalah artefak sesi yang terputus di kolom 1 dan kolom 3, dan HR tidak punya cara melihatnya. Ini dibereskan di tahap nol, sebelum jenis tes apa pun ditambahkan.
- ⚠️ **Gateway meng-hardcode kelima path psikotes.** Endpoint publik berbentuk baru menuntut menyunting dan menaikkan gateway juga.
- ⚠️ **Dua implementasi mesin tes kandidat masih hidup berdampingan** (erp-frontend dan career-bharata). Di prod kandidat memakai **career portal** (`ERP_FRONTEND_URL` prod berisi alamat career portal, dibaca 2026-09-10), jadi bentuk jawaban baru harus mendarat di sana. Selama erp-frontend belum resmi dipensiunkan, tiap bentuk jawaban berisiko dibangun dua kali.
- ⚠️ **Batas waktu hari ini ditegakkan browser, bukan server.** Cukup untuk Kraepelin selama kandidatnya jujur, tapi tidak cukup untuk tes berkunci jawaban yang dikerjakan jarak jauh. Pola timer yang ditegakkan server dari waktu mulai sudah ada di LMS dan layak dicontek.

## Belum Diputuskan (TBD)

1. **Legalitas item CFIT dan DISC.** Keduanya instrumen berlisensi. Boleh atau tidaknya didigitalkan dan disimpan di server perusahaan **harus dijawab HRD sebelum bank soal diisi**. Risiko hukum, bukan teknis.
2. **Bentuk jawaban EPPS.** Diasumsikan muat di `most_least` karena sama-sama pilihan berpasangan, tetapi **belum diperiksa**.
3. **Mesin kandidat mana yang dipertahankan resmi.** De facto di prod sudah career portal; keputusan tertulisnya belum ada.
4. **Bentuk perbaikan skor artefak**: ✅ diputuskan 2026-09-10 saat merencanakan tahap nol, yaitu sesi yang tidak tuntas tetap menulis baris Hasil Tes **tanpa skor**, dan status terputusnya dibaca dari laporan sesi.
5. **Urutan babak di prod sudah menyimpang** (`sequence_number` berisi 1, 1, 2, 3, 3, 5, 7 — dua pasang bertabrakan, dua angka bolong). Apakah dirapikan sebagai data atau diberi penjaga keunikan, belum diputuskan.
6. **Pendampingan.** Tes hari ini dikerjakan mandiri tanpa pendamping dan tanpa jejak tempat pengerjaan. Untuk CFIT, yang berkunci jawaban, ini menentukan apakah soalnya boleh dibuka lewat tautan publik sama sekali, dan bila boleh, timernya wajib ditegakkan server. **Wajib dijawab HRD sebelum tahap CFIT.** Rincian: [[ADR - 0087 Katalog Tipe Psikotes Jadi Master Data, Tiga Bentuk Jawaban Tetap Kode]] §Belum Diputuskan.
7. **Tenggat tautan dan status kandidat.** Tautan yang belum dibuka tidak pernah kedaluwarsa, dan kandidat yang sudah ditolak tetap bisa mengerjakan. Rincian di ADR yang sama.

## Dependensi & Integrasi

- [[Microservices - Recruitment Service]] — rumah kodenya; babak Psikotest dicari **by nama** ber-`form_type: "test"`
- [[CORE - API Master Gateway]] — mempublish rute publik tanpa JWT
- [[Microservices - File Service]] — ⚠️ tidak dipakai: recruitment bicara langsung ke MinIO lewat shared-library, jadi batas 4 MB milik file-service **tidak berlaku** baginya dan harus ditulis sendiri
- [[Microservices - Notification Service]] — email magic link ke kandidat
- [[APP - Web ERP]] — layar HR dan halaman kandidat versi erp-frontend
- [[APP - Portal Karir Bharata]] — halaman kandidat versi career portal

## Dokumen Terkait

- [[ADR - 0087 Katalog Tipe Psikotes Jadi Master Data, Tiga Bentuk Jawaban Tetap Kode]] — keputusan dan alasannya
- [[HRIS - Psikotes Kraepelin]] — jenis tes yang sudah berjalan
- [[HRIS - Recruitment]] — konsep dan keputusan HRD
- [[API - Recruitment Service]] — kontrak endpoint
