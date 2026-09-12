# ANALISA - Inspeksi Satgas 5R dan K3

Papan kerja hasil `/analisa-kebutuhan` 2026-09-11. Keputusan di [[ADR - 0090 Inspeksi Satgas 5R dan K3 di Form Builder dengan Nilai dari Cek Ulang Terakhir]], cara kerja di [[Microservices - Form Builder Service]] bagian "Inspeksi Satgas 5R & K3".

**Status papan (2026-09-12):** T1+T2 **merged** 2026-09-11 (bip-erp PR [#1849](https://github.com/bip-itteam-internal/bip-erp/pull/1849)); biner form-builder dev sudah memuatnya (diukur 2026-09-11), employee-service dev belum diukur, dan verifikasi gerbang Satgas lewat gateway belum dijalankan. T4 **merged** 2026-09-11 (bip-erp [#1852](https://github.com/bip-itteam-internal/bip-erp/pull/1852) + erp-frontend [#1542](https://github.com/bip-itteam-internal/erp-frontend/pull/1542)) dan **live dev**: `file_fields` terverifikasi lewat gateway dev, bundel frontend dev memuat editor baru. Prod belum. **T6 selesai di branch** 2026-09-12 (my-bharata `feat/satgas-inspeksi`, `1.18.0+162`, belum PR, belum dicoba di perangkat) bersama PR erp-frontend `feat/form-builder-berkas-wajib` (draft, merge ditahan sampai adopsi). T0 sebagian dijawab 2026-09-12. T3, T5, dan T7 belum dimulai. Rencana (akar `erp/`): `.task-plans/2026-09-11-satgas-kepatuhan-izin-dan-gerbang.md` (T1+T2), `.task-plans/2026-09-11-form-builder-satgas-editor-dan-foto.md` (T4), dan `.task-plans/2026-09-12-mybharata-satgas-inspeksi.md` (T6).

**Kebutuhan asal** (dari manajemen): posisi Culture di HRD sebagai "intel perusahaan"; budaya kepatuhan kantor (sepatu, lanyard) dicatat diam-diam lewat MyBharata dan muncul besoknya per departemen; HRD punya rutinitas Satgas 5R & K3 yang sekarang lewat Google Form "Dokumentasi Temuan Inspeksi SATGAS 5R & K3" (foto, maks 10 berkas, 10 MB).

**Hasil wawancara dan grounding:**

- Catatan atribut **sudah diputuskan** di [[ADR - 0085 Industrial Relation Catatan Kepatuhan Ringan Terpisah dari SP dan KPI]] (Faiz, 2026-09-10). Dikonfirmasi tetap sinyal pembinaan, bukan KPI. Tidak ada ADR baru untuk bagian itu; task-nya di `ANALISA - Industrial Relation`.
- Satgas 5R & K3 ternyata untuk **KPI perorangan Office Boy dan Security**. Beberapa hari setelah temuan dicek ulang, dan **nilai KPI diambil dari cek ulang**. Sekarang PIC diberi tahu manual lewat WhatsApp.
- Pemakai: OD & Industrial Relation Officer. Masalah yang mereka nyatakan: repot mengunggah dokumentasi. Solusi yang mereka minta: file upload di Form Builder.
- Diputuskan user: tetap Form Builder; menu khusus Satgas di MyBharata yang hanya muncul untuk jabatan tertentu (form Satgas tidak muncul di daftar survei); plus halaman rekap di web.
- Diputuskan user saat `/start-task` T1: nama modul **`kepatuhan`**, satu izin dulu (`kepatuhan.satgas.input`), T1+T2 digabung satu PR, temuan = pertanyaan ya/tidak "Ada temuan?", notifikasi terbit dilewati. Saat `/review`: notifikasi "selesai" juga dilewati.
- Usulan awal yang **gugur** setelah informasi pemakai masuk: AI penilai foto, peringkat antar departemen, master area.
- Temuan data (lembar HRD "KPI DEPARTEMEN HRGA"): skor Satgas diketik dengan skala campur; Maret 2026 total KPI Office Girl 131 dari 100 lolos disetujui.

**Urutan**: T0 (keputusan HR) berjalan paralel dan wajib selesai sebelum T3 go-live. T1+T2 (merged) → T3. T4 merged dan live dev; T6 selesai di branch, menunggu PR dan uji perangkat. T5 setelah T3. Tutup dengan T7. ⛔ **employee-service dan form-builder naik bersama, lalu web, lalu MyBharata.**

⚠️ **Koordinasi**: modul `kepatuhan` diusulkan dipakai juga oleh menu pencatat ADR 0085 (TBD "petugas ditunjuk"). Kabari Faiz nama modulnya supaya izin catatan kepatuhan masuk ke modul yang sama, bukan gerbang kedua.

---

## T0. Keputusan HR (bukan kode)

Jawaban wajib sebelum go-live, dicatat ke ADR 0090 §TBD:

- ✅ **Dijawab 2026-09-12**: rumus konversi skala 1-5 ke 0-100 memakai `(v-1)/4` (rumus sistem, 3 = 50), bukan `v/5`.
- ✅ **Dijawab 2026-09-12**: cek ulang yang jatuh ke bulan berikutnya dihitung ke **periode bulan temuan**. ⚠️ Kode belum begitu, lihat T3.
- Jumlah field foto per orang, dan apakah foto wajib.
- Siapa selain petugas yang boleh membuka rekap web (usul: atasan Office Boy dan Security).
- Jabatan persis yang dipasangi paket `kepatuhan_petugas_satgas`.

**Cara verifikasi**: jawaban tertulis dari HR, ditempel ke ADR 0090. Dua jawaban pertama sudah tercatat di ADR 0090 bagian "Diputuskan sesudah ADR ditulis".

## T1+T2. BE: modul izin `kepatuhan` + penanda + gerbang + `/me/satgas` ✅ merged #1849

Digabung satu PR atas keputusan user, supaya tak ada izin tanpa penegak yang ter-deploy ke dev saat merge. Isi branch `feat/form-builder-satgas-kepatuhan`:

- `d94c7c84` modul izin `kepatuhan`: `catalog_kepatuhan.go` (izin `kepatuhan.satgas.input`, paket `kepatuhan_petugas_satgas`, tanpa tier), loop `DefaultPermissionSets`, registrasi employee-service, `init()` uji. Tiga penjaga `permission_catalogs_test.go` dibuktikan merah tanpa registrasi.
- `5fd162d1` penanda `metric_key: inspeksi_satgas`: evaluation, bulanan, sasaran aktif, tepat satu `boolean`, tanpa `single_response`, `metrikJamak`.
- `0391b083` gerbang (`satgas_gate.go`) di kirim jawaban, unggah, daftar sasaran, `listMyForms`; `metric_key` di payload `/me/forms`; kill-switch `KEPATUHAN_PERMISSION_ENFORCEMENT`; notifikasi terbit dilewati; `GET /me/satgas` (`satgas_me.go`).
- `2af244aa` perbaikan review: notifikasi "selesai" juga dilewati (`kirimNotifForm`), nama paket satu konstanta, klaim diurai sekali per permintaan, uji round-trip BSON.
- `4414ea24` nama paket bawaan di seed memakai konstanta yang sama dengan pesan tolakan.

**Yang belum**: PR [#1849](https://github.com/bip-itteam-internal/bip-erp/pull/1849) sudah merged 2026-09-11; biner form-builder dev sudah memuatnya (diukur 2026-09-11), tersisa employee-service dev (ukur, jangan diasumsikan), dan **Cara Verifikasi lewat gateway** di artefak rencana (dua akun: berpaket dan tak berpaket; kirim/unggah 403 vs 201; `/me/satgas` allowed false vs ringkasan; temuan lalu cek ulang berpindah status; regresi form penilaian biasa).

## T3. BE: nilai terakhir-menang, endpoint internal, sumber KPI

**Bergantung T1+T2 dan T0 (rumus konversi).** Pembaca SKOR Satgas: jawaban terakhir per orang per periode, satu rumus konversi, dipakai endpoint internal form-builder dan tab analitik "Yang Dinilai" untuk form bertanda (hari ini tab itu masih `overallOf`, rata-rata). Pakai ulang `ringkasSatgas`/`kirimanLebihBaru` dari `satgas_me.go` untuk memilih jawaban terakhir, jangan menulis urutan-menang kedua. Sumber KPI per orang baru di employee-service. ⛔ Jangan memakai atau menyentuh `service_team_index` / `nilai_layanan_pribadi`.

⚠️ **Keputusan T0 soal periode cek ulang belum ada di kode.** Kiriman selalu masuk periode yang sedang buka (`response_handlers.go:471`), dan `/me/satgas` hanya membaca periode berjalan (`satgas_me.go`). Cek ulang atas temuan bulan lalu harus bisa dihitung ke bulan temuan; rancang cara atribusinya di `/plan` T3 bersama tampilannya di menu MyBharata, jangan ditebak.

`/start-task buat pembaca skor Satgas (jawaban terakhir per orang per periode, satu rumus konversi) untuk endpoint internal form-builder, tab analitik Yang Dinilai pada form inspeksi_satgas, dan sumber KPI per orang baru di employee-service`

**Cara verifikasi**: temuan skor 2 lalu cek ulang skor 5 untuk orang yang sama → nilai = konversi 5, **bukan** rata-rata; tab analitik menampilkan angka yang sama; orang tanpa jawaban → galat (jatuh manual), bukan 0; form ber-`service_team_index` tetap dirata-rata (uji membuktikan kedua aturan tak tertukar, dengan kontrol negatif). Satu panggilan sungguhan lewat gateway, dan draf KPI Office Boy uji terisi setelah HR memasang sumbernya di "Atur Target".

## T4. Web: field foto Form Builder + sakelar penanda + label modul ✅ merged, live dev (prod belum)

Dua PR (urutan naik: bip-erp dulu, lalu erp-frontend):

- bip-erp PR [#1852](https://github.com/bip-itteam-internal/bip-erp/pull/1852) (`feat/form-builder-analitik-berkas`, `c9c509b6`), **merged** 2026-09-11: respons analitik membawa `file_fields [{key,label}]` di luar `fields`. **Temuan `/start-task`**: rute pratinjau saja tak cukup, karena backend membuang berkas dari `fields` dan tab Individu/Pertanyaan mengulang daftar itu (keputusan user: backend kirim daftar berkas).
- erp-frontend PR [#1542](https://github.com/bip-itteam-internal/erp-frontend/pull/1542) (`feat/form-builder-satgas-editor`), **merged** 2026-09-11: `f5ab9f64` tipe `file` + cermin penanda `inspeksi_satgas` + label modul `kepatuhan`; `54cb1049` panel Satgas di form Penilaian (terkunci bila bertanda lain) + keterangan pertanyaan; `b5b8cedb` lampiran di tab Individu dan Pertanyaan; `5b45fb35` temuan review (kedipan galat, validasi id, 404, jenis berkas, helper syarat, celah test); `4ab15b2b` keputusan review.
- **Keputusan user saat `/review`**: antrean Kaizen menampilkan penanda lampiran (bukan id); **pertanyaan berkas belum boleh wajib sampai T6**; mengganti tipe form melepas SEMUA penanda yang tak sah (`TIPE_PENANDA` + `lepasPenandaTakSah`); galat simpan editor kini tampil.
- **Dikeluarkan dari T4**: kompresi gambar di web (erp-frontend tak punya jalur pengisian form; pindah ke T6).
- Verifikasi lokal (sebelum merge `origin/main`): 561 test `src/features/form-builder` hijau, kontrol negatif 11 test kunci terbukti merah; sesudah commit `4ab15b2b` suite penuh 39 gagal identik dengan baseline merge-base e37e4adb dan `pnpm build` lolos. Sesudah merge `origin/main` 428d41b0: tsc, eslint, dan build lolos; suite penuh 37 gagal di 13 berkas, identik dengan 13 berkas yang sama di worktree baseline 428d41b0. BE sesudah merge `origin/main`: `go vet`, `go test`, `gofmt` bersih, dan kontrol negatif dua test `file_fields` terbukti merah.
- **Dev 2026-09-11**: Form-Builder-Service di-restart 14:40Z dengan biner yang memuat `file_fields` (kontrol positif `inspeksi_satgas`, kontrol negatif 0). Lewat gateway dev (akun `panpan`), form uji berberkas membalas `file_fields [{foto_uji}]` dan `fields` tanpa pertanyaan berkas, sedangkan form tanpa berkas tak mengirim kuncinya. Form uji dihapus lunak (`6aa4179a3feb000c0d7bb0d7`, GET sesudahnya 404). Bundel `frontend-hris-dashboard` (restart 14:59Z) memuat teks panel Satgas.

**Yang belum**: deploy prod (manusia; form-builder dulu, baru frontend) dan sisa Cara Verifikasi di artefak rencana: layar alur A/B ditempuh sebagai orang, terang/gelap, sekitar 390px, id/en, dan PDF sungguhan.

## T5. Web: halaman rekap Satgas

**Bergantung T3.** Menu di kategori HRIS, digerbang izin modul `kepatuhan`, membaca data yang sama dengan menu MyBharata. Isi: nilai per orang per bulan, foto temuan dan perbaikan, orang yang belum dicek ulang. Menunya tak boleh bertumpu pada fallback: entri `FALLBACK` di `menu-permission.ts` wajib ada untuk izin `kepatuhan.*` (izin tanpa entri diloloskan `bolehMenu`).

`/start-task buat halaman rekap Satgas di HRIS erp-frontend (menu bergerbang izin kepatuhan.satgas.input, data dari endpoint yang sama dengan menu MyBharata, nilai sama dengan KPI)`

**Cara verifikasi**: angka per orang **sama persis** dengan draf KPI bulan yang sama; akun tanpa izin tidak melihat menu dan ditolak server. Struktur tabel HRIS (skill `/migrasi-tabel-hris`), tanpa `p-6` sendiri, tombol kembali lewat `SidebarBackButton`, loading pakai `Skeleton`, i18n id + en.

## T6. MyBharata: field foto + `boolean`, menu Satgas, penyaring beranda, cek ulang ✅ selesai di branch (belum PR)

**Bergantung T1+T2 (merged #1849).**

**Hasil 2026-09-12** (rencana `.task-plans/2026-09-12-mybharata-satgas-inspeksi.md`):

- my-bharata `feat/satgas-inspeksi` dari `origin/dev`, versi **`1.18.0+162`** (di atas `dev` `1.17.0+161`). Commit: `7c1e88e6` tipe `boolean`/`file`, `metric_key` + `isSatgas`, encoder bool; `c6eed734` unggah + kompresi + kunci tombol; `5a5c24ac` lint; `259ebf24` menu, kartu beranda, halaman Satgas, halaman isi; `4fa5203f` merge `origin/dev`; `a50365ae` versi; `6d51ce2a` tindak lanjut review (413 ke kunci sendiri, test DI dan halaman); `9be35bb6` pesan izin kamera/galeri ditolak dan perangkat tanpa kamera.
- erp-frontend `feat/form-builder-berkas-wajib` `6145448d` (**draft**): mencabut aturan berkas wajib di `lib/schema.ts`, pemangkasan `required` di `lib/field-types.ts`, kunci sakelar di `components/question-row.tsx`, dan kalimat terakhir `formBuilder.question.fileHint`. Backend tak pernah melarang berkas wajib.
- **Penyimpangan dari papan (keputusan user)**: halaman `SatgasFillPage` sendiri, bukan penyesuaian `EvaluationFillPage`; kartu beranda khusus petugas; foto dari kamera **dan** galeri; larangan berkas wajib dicabut di PR terpisah yang merge-nya ditahan sampai adopsi versi T6 terukur, bukan bersama rilis. Unggah hanya mengirim field `file`, karena backend tak membaca `field_key`.
- **Verifikasi lokal**: sesudah merge `origin/dev`, 640 test hijau (satgas, home, form, kaizen, live_shift, core) dan `dart analyze` per folder bersih; sesudah tindak lanjut review, 610 test hijau di folder yang tersentuh. Kontrol negatif terbukti merah: encoder bool, gerbang menu sebelum `roles == null`, favorit Satgas saat izin belum dijawab, jawaban sesudah logout dibuang, kunci tombol selama unggah, pengosongan jawaban saat unggah. PR erp-frontend: 553 test `src/features/form-builder`, tsc, eslint, dan `pnpm build` lolos.
- **Yang belum**: kedua PR; build flavor dev di perangkat (akun berpaket melihat menu dan kartu, akun tanpa paket tidak, termasuk instalasi baru); form Satgas uji di dev (temuan dengan foto kamera ukuran penuh jadi `open_finding`, cek ulang "Tidak" dengan foto galeri jadi `resolved`, `GET /api/form-builder/me/satgas` lewat gateway dev menunjukkan status yang sama, foto terbuka di tab Individu); regresi form penilaian non-Satgas dan kirim Kaizen; ukur `app_version` petugas sebelum merge PR erp-frontend.

- Tipe field **`file`** (kamera/galeri, `maxWidth` sekitar 1920, cek ukuran di bawah 4 MB, tombol kirim terkunci selama unggah, pola unggah-dulu-kirim-id) dan **`boolean`** (untuk "Ada temuan?"; hari ini jatuh ke `unknown`).
- Menu Satgas di `home_quick_access.dart` yang bertanya ke `GET /me/satgas` (tampil bila `allowed`), bukan `system_roles`. Tampilkan status per PIC (`not_rated` / `open_finding` / `resolved`).
- Form bertanda `inspeksi_satgas` dikeluarkan dari `SurveySection` lewat `metric_key` (pola `isKaizen`; `pendingOf` tidak disaring).
- ⚠️ **Cek ulang**: `EvaluationFillPage` menutup diri saat semua orang sudah dinilai, dan daftar sasaran menandai orang yang sudah dinilai sebagai `done`. Menu Satgas harus bisa membuka pengisian untuk orang berstatus `open_finding` walau ia sudah pernah dinilai.
- ⛔ **Cabut larangan wajib pada pertanyaan berkas di editor web** ~~bersama rilis T6~~ lewat PR terpisah yang merge-nya ditahan sampai adopsi versi T6 terukur (diubah user 2026-09-12) (erp-frontend `lib/schema.ts` aturan berkas wajib, `lib/field-types.ts` pemangkasan `required`, `components/question-row.tsx` kunci sakelar, dan keterangan `formBuilder.question.fileHint`). Tanpa itu foto tak pernah bisa diwajibkan.
- Kompresi foto sebelum unggah (pindahan dari T4; web tak punya jalur pengisian).

`/start-task tambah tipe field file dan boolean di form MyBharata, menu Satgas yang bertanya ke GET /me/satgas, penyaring form inspeksi_satgas dari SurveySection, dan pengisian cek ulang untuk PIC yang sudah pernah dinilai`

**Cara verifikasi**: petugas berizin melihat menu, akun lain tidak, **termasuk saat cache peran kosong**; form Satgas tidak muncul di beranda ~~, tetapi tautan notifikasinya tetap membuka form~~ (dicoret 2026-09-12: jalur notifikasi yang membuka form tak ada untuk form mana pun, dan form Satgas tak mengirim notifikasi); foto ponsel ukuran penuh berhasil diunggah (terkompres); cek ulang atas PIC yang sudah dinilai bisa dikirim dan statusnya berpindah ke `resolved`. `dart analyze` per folder (bukan `flutter analyze` seluruh repo). Rilis menaikkan **version name** dan versionCode (`update_version.dart` dua argumen).

## T7. Verifikasi end-to-end + tutup dok

**Bergantung T3 sampai T6.** Satu perjalanan utuh sebagai orang, bukan `curl`: IT memasang paket izin ke jabatan petugas → petugas login ulang → isi temuan dengan foto → cek ulang beberapa hari kemudian → rekap web menampilkan nilai cek ulang → draf KPI Office Boy berisi angka yang sama → atasan memverifikasi.

Negatif: akun non-petugas ditolak `403` saat mengirim; MyBharata versi lama tidak buntu (foto belum wajib).

Tutup: perbarui status ADR 0090 dan bagian Satgas di dok Form Builder ke ✅/⚠️ sesuai kenyataan, perbarui baris `Kebersihan 3` dan `Kerapihan dan kebersihan Pos` di Matriks KPI, lalu `/sync-docs`.

---

## Temuan sampingan untuk `/sync-docs` (bukan task fitur)

- Dok Form Builder belum memuat tipe `report` (keputusan per butir, unggah ulang), penanda `kpi_checklist`, dan `service_team_index` (sumber `nilai_layanan_pribadi` / `indeks_layanan_tim`).
- Matriks KPI masih menulis `Pelayanan Security` "belum dipetakan", padahal kode memakai `nilai_layanan_pribadi` untuk metrik itu (`kpi_sumber_indeks_layanan_tim.go:33-35`). Apakah template sudah memasangnya belum diukur.
- ADR 0066 / ADR 0084 dan dok Form Builder menyebut modul culture "belum merge", padahal `culture_*.go` dan `kpi_sumber_culture.go` sudah di `origin/main` (2026-09-11).
- Pemakaian field `file` di prod (koleksi `form_uploads`) belum diukur.
- Komentar di `services/form-builder/models_form.go` (blok tipe field) masih berbunyi "upload file belum ada, fase 2", padahal `FieldFile` sudah ada.
- **Kegagalan test yang sudah ada di `origin/main`** (bukan dari branch ini): `shared-library/models/employee` `TestDefaultPermissionSetsValid` (+ saudaranya di `permission_set_payroll_test.go`) merah karena `init()` uji tak mendaftarkan katalog `manufacture`; `services/employee` `TestMetrikTanpaIklanGagalTerbacaPadaServiceLama` merah.
- **Suite penuh erp-frontend di merge-base e37e4adb**: 39 test gagal di 15 berkas, jumlah dan daftarnya identik dengan worktree baseline terpisah, jadi baseline, bukan regresi. Di `origin/main` 428d41b0 turun jadi 37 gagal di 13 berkas (baseline dan branch identik). Salah satunya `src/app/(main)/form-builder/page.test.tsx`, jadi "test form-builder hijau" di papan ini berarti `src/features/form-builder`, bukan halaman rutenya.
- **Komite Kaizen tak bisa membuka lampiran** (pratinjau khusus pengelola form). Antrean hanya menampilkan penanda. Rute pratinjau untuk komite **tidak dikejar**: user menyatakan 2026-09-11 modul Kaizen akan dihapus nanti (belum ada ADR maupun task penghapusannya).
- **Objek file-service tersimpan `application/octet-stream`** (`CreateFormFile` di `shared-library/routes/internal_request.go`), jadi PDF mungkin terunduh alih-alih tampil di pratinjau. Ukur di dev dengan berkas sungguhan; perbaikan content-type task tersendiri.
- **Angka versi minimum aplikasi di gateway ditulis mati** (`api-gateway/main.go:701`, `1101103` untuk android dan ios) dan sifatnya ajakan. Adopsi versi T6 tak bisa dipaksa dari server, jadi gerbang merge PR larangan berkas wajib mengukur `app_version` petugas.
- **`EvaluationFillPage` mencoba ulang dengan `LoadEvaluation('')`** saat galat terjadi sebelum form sempat tampil (`evaluation_fill_page.dart`), jadi tombol Coba Lagi di sana tak pernah berhasil. Alur penilaian lain, task tersendiri.
- **Form Satgas yang dibuka lewat `/survey/:id`** dialihkan `SurveyFillPage` ke `EvaluationFillPage` (alur yang menutup diri saat semua sudah dinilai). Menu Satgas tak memakai jalur itu, dan form Satgas tak mengirim notifikasi yang membawa tautannya.
- **Riwayat Kaizen di MyBharata menampilkan `upload_id` mentah** untuk jawaban berkas (`answer_text.dart`), sudah begitu sebelum T6. Tidak dikejar karena Kaizen direncanakan dihapus.

## Yang TIDAK jadi dikerjakan, beserta alasannya

- **AI penilai foto**: tidak diminta pemakai; Satgas menilai sendiri. Syarat ketiga ADR 0058 tak terpenuhi. Foto juga akan keluar ke penyedia pihak ketiga.
- **Peringkat antar departemen + master area**: yang dinilai orang (Office Boy/Security), bukan departemen.
- **Penanda `service_team_index`**: melebur skor 5R dengan rating pelayanan di KPI anggota dan atasan.
- **Tipe `report`**: melarang `subject`, dan pemutusnya atasan departemen pengirim.
- **Modul K3 manufaktur**: area ditulis mati `{Produksi, Gudang}` dan terikat penyebut KPI SPV Manufaktur.
- **Pola menu ADR 0039**: default terbuka sampai ada penugasan pertama.
- **Notifikasi ke PIC dan tautan temuan-cek ulang**: ditinjau setelah satu atau dua bulan pemakaian; butuh kategori inbox baru (form-builder + notification-service naik bersama).
- **`max_files` dan menaikkan batas 4 MB**: ditunda sampai ada pemakai kedua.
