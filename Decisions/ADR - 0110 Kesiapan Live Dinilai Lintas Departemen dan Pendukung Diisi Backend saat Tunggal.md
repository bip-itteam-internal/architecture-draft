# ADR - 0110 Kesiapan Live Dinilai Lintas Departemen dan Pendukung Diisi Backend saat Tunggal

## Deskripsi

*Metrik kesiapan siaran berhenti dibatasi departemen: atribusinya murni lewat `live_shifts.pendukung[]`, karena posisi **Live Support** ditugaskan lintas departemen. Dan karena pemilih pendukung di MyBharata opsional serta terbukti tak pernah diisi, **marketing-analytics mengisinya sendiri** saat perusahaan hanya punya satu pemegang posisi itu.*

- **Status**: 🟡 Diputuskan, **PR terbuka, belum merge, belum deploy**. Kode: bip-erp [#1970](https://github.com/bip-itteam-internal/bip-erp/pull/1970) `feat/kpi-kesiapan-live-lintas-departemen` (marketing-analytics, employee-service). Test hijau dibanding baseline `origin/main` (marketing-analytics hijau penuh; employee menyisakan satu merah yang sudah merah di baseline), kontrol negatif dijalankan untuk tiga penjaga utamanya. **Belum pernah dipanggil lewat gateway mana pun.** Gerbang verifikasinya di `.task-plans/2026-09-18-kpi-kesiapan-live-lintas-departemen.md`.
- **Tanggal**: 2026-09-18
- **Terkait**: [[Microservices - Marketing Analytics Service]] · [[Microservices - Employee Service]] · [[APP - MyBharata]] · [[HRIS - Matriks KPI per Departemen]]

## Context

Diukur di produksi 2026-09-18 sebelum keputusan diambil, bukan disimpulkan:

1. **Nol dari 234 sesi mencantumkan pendukung.** `marketing_analytics_db.live_shifts` memuat 234 dokumen; **0** punya `pendukung` terisi dan **1** punya `kesiapan`. Backend sudah menulis field `pendukung` sejak 2026-09-16 pukul 14:01 WIB (52 dokumen ber-field, 182 sisanya lahir sebelum field itu ada), jadi yang kosong isinya, bukan kemampuannya.

2. **Versi aplikasi baru saja TIDAK cukup.** Ceklis kesiapan dan pemilih Live Support masuk dalam commit yang sama di MyBharata (`3361d077`, 2026-09-16), jadi sesi yang membawa `kesiapan` membuktikan kliennya sudah versi baru. Sesi 2026-09-18 milik Fitri Baniaturrohmah membawa kesiapan lengkap, **pendukungnya tetap kosong**. Pemilihnya opsional, bawaannya kosong, dan host tak diberi tanda apa pun bahwa melewatinya membuat sesi itu tak masuk hitungan siapa pun.

3. **Posisi Live Support ditugaskan lintas departemen** (keputusan user 2026-09-18). Host live yang dia topang bukan hanya di departemennya sendiri.

4. **Lapisan hitung membuang sesi lintas departemen, senyap.** `HandlerKPIKesiapanLive` menyaring shift ke toko departemen orang yang dinilai (`tokoTikTokDepartemen` + `saringShiftToko`), dengan komentar yang menyatakan batas itu disengaja. Untuk periode September: 152 sesi toko Kyura terhitung, **82 sesi toko Beauty Hacks dibuang**, yaitu 35% dari seluruh sesi. Tak ada galat, tak ada tanda; di layar terbaca sebagai orang yang tak bekerja.

5. **Satu-satunya pemegang posisi Live Support di PT BIP tetap satu orang** (`BIP-0240-05-26`, `position` "Live Support", `position_key` masih "videographer"), dan departemennya Kyura sementara sesi yang dia topang melintasi Kyura dan Beauty Hacks.

6. **Preseden kopling sudah ada.** [[ADR - 0106 Tema dan Teaser Live Support Disetor dan Diputus Penyetuju Departemen sebagai Dasar KPI]] sudah membuat marketing-analytics memanggil employee-service (`GET /internal/department-approver`, env `EMPLOYEE_MODULE_URL`), menyimpang sadar dari [[ADR - 0101 Kesiapan Siaran Dicatat Host saat Mulai sebagai Dasar KPI Live Support]] §3.

## Decision

1. **Atribusi `kesiapan_live` MURNI lewat `pendukung[]`, tanpa batas departemen.** `tokoTikTokDepartemen` dan `saringShiftToko` dibuang dari jalur hitung; `saringShiftToko` dihapus seluruhnya karena fungsi tak terpakai yang namanya meyakinkan adalah undangan dipakai lagi. `tokoTikTokDepartemen` **tetap hidup dan tetap benar** di `kinerja_live`, yang atribusinya lewat `host[]`.

2. **`department` berhenti jadi parameter `GET /kpi/kesiapan-live`.** Bukan sekadar berhenti diwajibkan: parameter yang tetap diterima tapi tak lagi berefek membuat pembaca berikutnya yakin ada penyaringan yang sudah tiada. Pemanggil versi lama tak patah, query string yang tak dibaca diabaikan Fiber.

3. **Dua field berganti nama karena lingkupnya berubah**, dan namanya wajib ikut berubah supaya tak ada nama yang bertahan sementara artinya bergeser:
   - `sesi_departemen_tanpa_pendukung` → **`sesi_tanpa_pendukung`**
   - `toko_diminta` → **`sesi_seluruhnya`**

4. **Penjaga sebab-di-hulu berpindah pertanyaan, tidak dihapus.** `toko_diminta` menjawab "berapa toko departemen ini terpetakan", pertanyaan yang kehilangan artinya begitu atribusinya lepas dari departemen. `sesi_seluruhnya` menjawab yang masih berlaku: adakah sesi live tercatat sama sekali pada periode itu. Nol tetap menerbitkan kalimat yang menunjuk hulu, bukan menyalahkan orangnya. Keduanya tetap **POINTER** di sisi employee-service, jadi kedua urutan deploy aman: nil berarti sisi seberang masih versi lama.

5. **Penjaga "karyawan belum punya departemen" dibuang.** Menolak menilai orang atas data induk yang sudah tak menentukan hasilnya sama mahalnya dengan kegagalan yang dulu hendak dicegah penjaga itu.

6. **marketing-analytics mengisi `pendukung[]` sendiri saat kosong**, lewat `GET /internal/live-support?company_id=` di employee-service (rute baru, memakai ulang `filterPosisiLiveSupport()` dua lapis).

7. **Hanya saat kandidatnya TEPAT SATU.** Nol berarti tak ada yang bisa dicatat; lebih dari satu berarti sistem tak punya cara tahu siapa yang benar-benar menopang sesi itu, dan menebak di sini bukan sekadar salah data melainkan menuliskan dasar penilaian kinerja atas nama orang yang mungkin sedang tak bekerja.

8. **Hanya saat host TIDAK memilih.** Pilihan host menang atas tebakan sistem, termasuk saat pilihannya bukan satu-satunya Live Support.

9. **GAGAL-TERBUKA**, kebalikan dari resolver penyetuju di ADR 0106 §8 yang gagal-tertutup. Di sana yang dijaga wewenang memutus; di sini cuma kelengkapan catatan, sementara yang dipertaruhkan siaran yang sedang dimulai. [[ADR - 0101 Kesiapan Siaran Dicatat Host saat Mulai sebagai Dasar KPI Live Support]] §2 sudah memutuskan siaran tidak pernah mati karena kelengkapan ini. Batas waktunya **3 detik**, lebih pendek daripada resolver penyetuju (5 detik), karena yang menunggu di ujung sini host yang sedang menekan Mulai.

10. **Disisipkan di `handleShiftMulai`, BUKAN di `rakitSesiBaru`.** Perakit itu dipakai bersama jalur eksekusi ambil alih, yang membawa permintaan lama supaya sesi barunya **mewarisi** pendukung (ADR 0101 §6). Menyisipkan bawaan di sana akan menimpa warisan itu saat pemegang aslinya memilih orang lain, dan gagalnya senyap: dokumennya tetap sah, cuma menyebut orang yang salah sebagai dasar penilaian.

### Menyimpang sadar dari ADR 0101 §3, untuk KEDUA kalinya

ADR 0101 §3 menulis marketing-analytics sengaja tak memanggil employee-service. Penyimpangan pertama dilakukan ADR 0106. Keputusan ini yang kedua, dan sah menurut [[REF - Kepemilikan Data]] aturan 2 (konsumsi lewat pemilik, bukan lewat database-nya): daftar pemegang jabatan tetap diselesaikan employee-service dan tak pernah disalin ke marketing-analytics. Yang dipertahankan dari ADR 0101: marketing-analytics tak menyimpan salinan data karyawan apa pun.

⚠️ Dua penyimpangan berturut-turut atas pasal yang sama adalah tanda pasalnya sendiri yang perlu ditinjau, bukan sekadar dikecualikan lagi. Peninjauan itu **belum dilakukan** dan sengaja tidak diselundupkan ke sini.

## Consequences

### Yang membaik

- Sesi lintas departemen yang benar-benar dia dukung berhenti hilang dari penilaian. Untuk September, 82 sesi yang tadinya dibuang kini masuk hitungan begitu tercatat.
- Metrik berhenti bergantung pada host mengingat menyentuh satu dropdown opsional.
- Kelalaian pengisian tetap terlihat penilai lewat `sesi_tanpa_pendukung` di `Catatan`.

### Yang memburuk atau tetap terbuka

- ⛔ **ARTI METRIKNYA BERGESER.** Selama hanya ada satu Live Support, praktis setiap sesi perusahaan tercatat atas namanya, termasuk saat dia cuti, sakit, atau sesi berlangsung di luar jam kerjanya. Metriknya efektif berubah dari "sesi yang dia dukung" menjadi "sesi perusahaan", dan tak ada apa pun di sistem yang membedakan keduanya. Diterima sadar; yang menolaknya harus menyediakan sumber kehadiran per sesi, yang belum ada.
- ⛔ **Fitur bawaan MATI SENDIRI begitu Live Support kedua diangkat**, dan matinya SENYAP bagi host. Yang tersisa log yang menyebut cacah kandidat, plus `sesi_tanpa_pendukung` yang ikut naik di Catatan. **Tidak ada notifikasi ke siapa pun.**
- ⚠️ **Mengisi pendukung TIDAK menyelamatkan periode berjalan sendirian.** Sesi tanpa `kesiapan` tetap keluar dari penyebut persentase, dan `kesiapan` hanya dikirim aplikasi versi baru. Selama host belum memperbarui MyBharata, metriknya berpindah dari "belum ada sesi yang mencatatnya" ke "sesi mencatatnya, tetapi belum satu pun mengisi ceklis" — tetap gagal hitung, hanya kalimatnya yang berubah.
- ⚠️ **Sesi lama tidak di-backfill.** Mengisi pendukung surut tidak menolong karena `kesiapan`-nya nil: ia menambah `sesi_total` tanpa menambah `sesi_berceklis` dan justru menjatuhkan cakupan. Mengarang ceklisnya dilarang ADR 0101 §4.
- ⚠️ **`sesi_tanpa_pendukung` kini mencacah seluruh perusahaan**, jadi Catatan metrik menyebut cacahan sesi departemen lain. Cacahan saja, tanpa detail; diterima sebagai harga dari atribusi lintas departemen.
- ⚠️ **Satu panggilan lintas-service baru di jalur terpanas**, yaitu tiap kali sesi dimulai. Terukur ~8 sesi per hari, jadi bebannya kecil; yang perlu dijaga batas waktunya, bukan volumenya.
- ⚠️ **Nama jabatan "Live Support" kini hidup di EMPAT tempat** (employee `posisiLiveSupport`, marketing-analytics `posisiPenyetorKarya`, erp-frontend `bolehSetorKarya`, dan kini filter rute internal yang memakai ulang `posisiLiveSupport`). Yang keempat memakai ULANG, bukan menyalin, jadi utangnya tidak bertambah — tetapi utang yang dicatat ADR 0106 tetap berdiri.

### Yang sengaja tidak dilakukan

- **Mewajibkan pemilih pendukung di MyBharata**, karena menuntut rilis aplikasi, yang justru ingin dihindari.
- **Mengisi `kesiapan` default di server**, karena mengarang pemeriksaan yang tidak pernah terjadi.
- **Menyaring pendukung bawaan menurut kehadiran atau jadwal**, karena sumber kehadiran per sesi belum ada dan menebaknya lebih buruk daripada mencatat apa adanya.
- **Meninjau ulang ADR 0101 §3** meski sudah disimpangi dua kali; itu pekerjaan tersendiri, bukan sisipan.

## Dokumen Terkait

- [[Microservices - Marketing Analytics Service]] § pencatatan sesi live dan `/kpi/kesiapan-live`
- [[Microservices - Employee Service]] § sumber KPI `kesiapan_live`, rute `/internal/live-support`
- [[API - Marketing Analytics Service]] · [[API - Employee Service]]
- [[HRIS - Matriks KPI per Departemen]] § Kyura → Live Support
- [[REF - Kepemilikan Data]] · [[RUN - Menambah Metrik KPI Otomatis]]
- [[ADR - 0101 Kesiapan Siaran Dicatat Host saat Mulai sebagai Dasar KPI Live Support]] · [[ADR - 0106 Tema dan Teaser Live Support Disetor dan Diputus Penyetuju Departemen sebagai Dasar KPI]] · [[ADR - 0088 Ambil Alih Sesi Live oleh Host Terjadwal dan Tutup Otomatis Akhir Shift]]
