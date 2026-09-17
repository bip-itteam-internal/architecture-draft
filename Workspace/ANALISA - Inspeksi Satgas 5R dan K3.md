# ANALISA - Inspeksi Satgas 5R dan K3

Papan kerja hasil `/analisa-kebutuhan` 2026-09-11. Keputusan di [[ADR - 0090 Inspeksi Satgas 5R dan K3 di Form Builder dengan Nilai dari Cek Ulang Terakhir]], cara kerja di [[Microservices - Form Builder Service]] bagian "Inspeksi Satgas 5R & K3".

**Status papan (2026-09-12; T3, T6, dan #1550 diperbarui 2026-09-14):** T1+T2 **merged** 2026-09-11 (bip-erp PR [#1849](https://github.com/bip-itteam-internal/bip-erp/pull/1849)); biner form-builder dev sudah memuatnya (diukur 2026-09-11), employee-service dev memuat kode T3 (diukur 2026-09-14), dan gerbang Satgas diuji lewat gateway dev 2026-09-14 (tanpa paket kiriman `403` berpesan paket, berpaket `201`). T4 **merged** 2026-09-11 (bip-erp [#1852](https://github.com/bip-itteam-internal/bip-erp/pull/1852) + erp-frontend [#1542](https://github.com/bip-itteam-internal/erp-frontend/pull/1542)) dan **live dev**: `file_fields` terverifikasi lewat gateway dev, bundel frontend dev memuat editor baru. Prod belum. **T6 merged** 2026-09-14: my-bharata [#144](https://github.com/bip-itteam-internal/my-bharata/pull/144) ke `dev` (`1.18.0+162`, publish Codemagic terpicu, belum dicoba di perangkat); erp-frontend [#1550](https://github.com/bip-itteam-internal/erp-frontend/pull/1550) ikut merged 2026-09-14, **sebelum** adopsi 1.18.0 terukur (ADR menahannya sampai terukur). **T3 merged** 2026-09-14 (bip-erp [#1866](https://github.com/bip-itteam-internal/bip-erp/pull/1866) + [#1867](https://github.com/bip-itteam-internal/bip-erp/pull/1867), erp-frontend [#1555](https://github.com/bip-itteam-internal/erp-frontend/pull/1555), commit T3 di #144) dan **live dev**: uji end-to-end lewat gateway dev lolos 2026-09-14 (rincian di T3). Prod belum deploy, `.env` prod belum diukur, dan cek ulang lintas bulan baru bisa dibuktikan 1-5 Oktober 2026. T0 sebagian dijawab 2026-09-12. T5 dan T7 belum dimulai. Rencana (akar `erp/`): `.task-plans/2026-09-11-satgas-kepatuhan-izin-dan-gerbang.md` (T1+T2), `.task-plans/2026-09-11-form-builder-satgas-editor-dan-foto.md` (T4), `.task-plans/2026-09-12-mybharata-satgas-inspeksi.md` (T6), dan `.task-plans/2026-09-12-satgas-nilai-kpi-cek-ulang.md` (T3).

**Kebutuhan asal** (dari manajemen): posisi Culture di HRD sebagai "intel perusahaan"; budaya kepatuhan kantor (sepatu, lanyard) dicatat diam-diam lewat MyBharata dan muncul besoknya per departemen; HRD punya rutinitas Satgas 5R & K3 yang sekarang lewat Google Form "Dokumentasi Temuan Inspeksi SATGAS 5R & K3" (foto, maks 10 berkas, 10 MB).

**Hasil wawancara dan grounding:**

- Catatan atribut **sudah diputuskan** di [[ADR - 0085 Industrial Relation Catatan Kepatuhan Ringan Terpisah dari SP dan KPI]] (Faiz, 2026-09-10). Dikonfirmasi tetap sinyal pembinaan, bukan KPI. Tidak ada ADR baru untuk bagian itu; task-nya di `ANALISA - Industrial Relation`.
- Satgas 5R & K3 ternyata untuk **KPI perorangan Office Boy dan Security**. Beberapa hari setelah temuan dicek ulang, dan **nilai KPI diambil dari cek ulang**. Sekarang PIC diberi tahu manual lewat WhatsApp.
- Pemakai: OD & Industrial Relation Officer. Masalah yang mereka nyatakan: repot mengunggah dokumentasi. Solusi yang mereka minta: file upload di Form Builder.
- Diputuskan user: tetap Form Builder; menu khusus Satgas di MyBharata yang hanya muncul untuk jabatan tertentu (form Satgas tidak muncul di daftar survei); plus halaman rekap di web.
- Diputuskan user saat `/start-task` T1: nama modul **`kepatuhan`**, satu izin dulu (`kepatuhan.satgas.input`), T1+T2 digabung satu PR, temuan = pertanyaan ya/tidak "Ada temuan?", notifikasi terbit dilewati. Saat `/review`: notifikasi "selesai" juga dilewati.
- Usulan awal yang **gugur** setelah informasi pemakai masuk: AI penilai foto, peringkat antar departemen, master area.
- Temuan data (lembar HRD "KPI DEPARTEMEN HRGA"): skor Satgas diketik dengan skala campur; Maret 2026 total KPI Office Girl 131 dari 100 lolos disetujui.

**Urutan**: T0 (keputusan HR) berjalan paralel dan wajib selesai sebelum T3 go-live. T1+T2 (merged) → T3 (merged, live dev, prod belum). T4 merged dan live dev; T6 merged (#144, #1550 mendahului gerbang adopsinya), menunggu uji perangkat. T5 setelah T3. Tutup dengan T7. ⛔ **employee-service dan form-builder naik bersama (di prod #1866 dan #1867 dalam satu deploy backend), lalu web, lalu MyBharata.**

⚠️ **Koordinasi**: modul `kepatuhan` diusulkan dipakai juga oleh menu pencatat ADR 0085 (TBD "petugas ditunjuk"). Kabari Faiz nama modulnya supaya izin catatan kepatuhan masuk ke modul yang sama, bukan gerbang kedua.

---

## T0. Keputusan HR (bukan kode)

Jawaban wajib sebelum go-live, dicatat ke ADR 0090 §TBD:

- ✅ **Dijawab 2026-09-12**: rumus konversi skala 1-5 ke 0-100 memakai `(v-1)/4` (rumus sistem, 3 = 50), bukan `v/5`.
- ✅ **Dijawab 2026-09-12**: cek ulang yang jatuh ke bulan berikutnya dihitung ke **periode bulan temuan**. Terwujud di T3 (merged #1867), batasnya tanggal 5 bulan berikutnya.
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

## T3. BE: nilai terakhir-menang, endpoint internal, sumber KPI, cek ulang lintas bulan ⚠️ merged, live dev (prod belum)

**Bergantung T1+T2 dan T0 (rumus konversi).** Pembaca SKOR Satgas: jawaban terakhir per orang per periode, satu rumus konversi, dipakai endpoint internal form-builder dan tab analitik "Yang Dinilai" untuk form bertanda. Sumber KPI per orang baru di employee-service. ⛔ Jangan memakai atau menyentuh `service_team_index` / `nilai_layanan_pribadi`.

**Hasil 2026-09-12** (rencana `.task-plans/2026-09-12-satgas-nilai-kpi-cek-ulang.md`):

- bip-erp PR [#1866](https://github.com/bip-itteam-internal/bip-erp/pull/1866) (`feat/satgas-nilai-kpi`), **merged** 2026-09-14: `837df639` pemilih kiriman terakhir dan nilai per periode; `a380d038` tab Yang Dinilai form Satgas memakai kiriman terakhir (`subject_rule`); `6aad728d` `GET /internal/satgas/metrics` digerbang `FORM_BUILDER_SERVICE_KEY`; `032be5fe` galat bertipe "belum dapat dihitung"; `3ab67735` sumber `nilai_inspeksi_satgas`; `27f38f99` compose. Tindak lanjut review: `9728c794` form ditutup langsung final; `f487a31d` pesan 500 diteruskan, kontrak dua sisi dibaca lintas berkas; `e43ea413` muatan internal sempit, `has_form:false` jadi belum dapat dihitung.
- bip-erp PR [#1867](https://github.com/bip-itteam-internal/bip-erp/pull/1867) (`feat/satgas-cek-ulang`), **merged** 2026-09-14: `64853a93` `period_key` di kirim dan unggah (`periodeKiriman`), kartu cek ulang di `/me/satgas`, `fields` di semua entri; `135e6062` tanggal badan galat satu tempat, test kunci bulan temuan; `5303bdae` penjaga cek ulang sesudah penjaga idempotensi; `cc22fe92` gerbang cek ulang ketat (`cekUlangBerlaku`), `owner_department` di `/me/satgas`; `618eb8b7` snapshot bulan temuan yang gagal dibaca menolak cek ulang (500), bagian `cc22fe92` yang terlewat dan ketahuan saat `/sync-docs`.
- erp-frontend PR [#1555](https://github.com/bip-itteam-internal/erp-frontend/pull/1555) (`feat/kpi-sumber-satgas`), **merged** 2026-09-14: `b4c6ffe9` label sumber dan kalimat aturan tab Yang Dinilai; `707afcd4` saran Otomasi untuk alasan Satgas, keterangan sumber tak menjanjikan tab yang tergerbang.
- my-bharata #144 (merged ke `dev` 2026-09-14), commit tambahan: `0972270c` kartu cek ulang, form dari `fields` kartu, `period_key` ke kirim dan unggah; `c4b030cc` daftar dimuat ulang sesudah halaman isi, batas dalam WIB; `92507e26` halaman isi menyebut bulan tujuan; `97032157` departemen pemilik.
- **Keputusan user** (`/start-task`, `/plan`, dan tindak lanjut `/review`): atribusi lewat `period_key` dengan periode tersimpan = bulan temuan; batas tanggal 5 bulan berikutnya 23.59.59 WIB; temuan belum final sebelum batas (form ditutup langsung final); "belum dapat dihitung" untuk belum dinilai, menunggu cek ulang, kiriman tanpa skor, dan bulan tanpa form berjalan; rata-rata nilai akhir antar form; form tanpa skala ditolak sumber dengan judulnya; kunci layanan baru, bukan kunci gateway; muatan internal sempit; `/me/satgas` membawa `fields` dan `owner_department`; "Semua periode" analitik = rata-rata nilai akhir bulanan; form `closed` ikut dibaca; gerbang tulis cek ulang ketat.
- **Verifikasi lokal**: `go test` form-builder hijau; employee-service hanya `TestMetrikTanpaIklanGagalTerbacaPadaServiceLama` yang sama dengan baseline `origin/main`. Kontrol mutasi `go test -overlay` terbukti merah untuk urutan terakhir-menang, gerbang kunci layanan, aturan analitik, galat bertipe, menunggu cek ulang, kunci bulan temuan, form ditutup, pesan 500, salinan kontrak, aturan lewati form, `has_form` galat, jawaban tak terbaca, dan saringan kartu. erp-frontend: vitest berkas terkait, `pnpm tsc`, eslint lolos (`pnpm build` lolos sebelum commit tindak lanjut review). my-bharata: `flutter test` satgas + form 213 hijau, `dart analyze` per folder bersih, kontrol negatif muat ulang, periode unggahan, dan tanggal WIB terbukti merah. `git merge-tree` branch cek ulang terhadap `origin/main` bersih.
- **Merge dan dev 2026-09-14**: #1866 dan #1867 merged 00:31 UTC, #144 ke `dev` 01:27 UTC (publish Codemagic terpicu), #1555 01:32 UTC. Biner form-builder dan employee-service dev memuat kode T3. `FORM_BUILDER_SERVICE_KEY` belum ada di `.env` dev saat merge; diisi 2026-09-14, lalu kedua container dibuat ulang `--force-recreate` dengan kunci yang sama. Frontend dev tak di-rebuild pipeline sesudah #1555, jadi dibangun manual 2026-09-14.
- **Uji end-to-end dev 2026-09-14** (form Satgas uji, akun petugas uji berpaket sementara, template KPI uji; data uji sudah dibersihkan): JWT karyawan biasa tanpa `key` ke `/internal/satgas/metrics` `401` `Unauthorized gateway`, dari dalam Employee-Service dengan kunci `200` berbentuk kontrak sempit; form terbit tanpa snapshot dan tanpa kiriman menghasilkan `has_form:false`; tanpa paket kiriman `403` berpesan paket; berpaket `/me/satgas` `allowed:true` dengan `fields`, `owner_department`, `period_key`; kiriman ber-`period_key` 2026-08 `409` "sudah ditutup 5 September 2026", 2026-13 `400`; unggahan tanpa berkas 2026-08 `409`, 2026-13 `400`, periode berjalan `400` berkas wajib; temuan skor 2 memberi `nilai` 25 + `menunggu_cek_ulang` sampai 5 Oktober 2026 dan `auto-values` "belum dapat dihitung"; Office Boy tanpa kiriman "belum dapat dihitung"; cek ulang skor 5 memberi status `resolved`, analitik `overall` 100 (`responses` 2, `subject_rule`), `nilai` 100, `auto-values` 100 dengan `auto_gagal_sumber:false`; kiriman ulang identik dalam 2 menit `duplicate:true`; tab Yang Dinilai (login sungguhan) menampilkan kalimat aturan dan skor 100.
- **Yang belum**: deploy prod (manusia) dan ukur `.env` prod; uji perangkat MyBharata; jendela 1-5 Oktober 2026 untuk kartu cek ulang lintas bulan, kiriman tercatat ke bulan temuan, dan `409` atas orang yang sudah selesai atau tanpa temuan (TAK TERVERIFIKASI sampai tanggal itu); layar Atur Target (pilihan sumber) dan saran Otomasi (baru unit test); skor otomatis lain orang itu tetap tampil saat periode tanpa form Satgas (baru unit test).

**Cara verifikasi**: temuan skor 2 lalu cek ulang skor 5 untuk orang yang sama → nilai = konversi 5, **bukan** rata-rata; tab analitik menampilkan angka yang sama; orang tanpa jawaban → "belum dapat dihitung" (jatuh manual), bukan 0; form ber-`service_team_index` tetap dirata-rata (uji membuktikan kedua aturan tak tertukar, dengan kontrol negatif). Satu panggilan sungguhan lewat gateway, dan draf KPI Office Boy uji terisi setelah HR memasang sumbernya di "Atur Target".

## T4. Web: field foto Form Builder + sakelar penanda + label modul ✅ merged, live dev (prod belum)

Dua PR (urutan naik: bip-erp dulu, lalu erp-frontend):

- bip-erp PR [#1852](https://github.com/bip-itteam-internal/bip-erp/pull/1852) (`feat/form-builder-analitik-berkas`, `c9c509b6`), **merged** 2026-09-11: respons analitik membawa `file_fields [{key,label}]` di luar `fields`. **Temuan `/start-task`**: rute pratinjau saja tak cukup, karena backend membuang berkas dari `fields` dan tab Individu/Pertanyaan mengulang daftar itu (keputusan user: backend kirim daftar berkas).
- erp-frontend PR [#1542](https://github.com/bip-itteam-internal/erp-frontend/pull/1542) (`feat/form-builder-satgas-editor`), **merged** 2026-09-11: `f5ab9f64` tipe `file` + cermin penanda `inspeksi_satgas` + label modul `kepatuhan`; `54cb1049` panel Satgas di form Penilaian (terkunci bila bertanda lain) + keterangan pertanyaan; `b5b8cedb` lampiran di tab Individu dan Pertanyaan; `5b45fb35` temuan review (kedipan galat, validasi id, 404, jenis berkas, helper syarat, celah test); `4ab15b2b` keputusan review.
- **Keputusan user saat `/review`**: antrean Kaizen menampilkan penanda lampiran (bukan id); **pertanyaan berkas belum boleh wajib sampai T6**; mengganti tipe form melepas SEMUA penanda yang tak sah (`TIPE_PENANDA` + `lepasPenandaTakSah`); galat simpan editor kini tampil.
- **Dikeluarkan dari T4**: kompresi gambar di web (erp-frontend tak punya jalur pengisian form; pindah ke T6).
- Verifikasi lokal (sebelum merge `origin/main`): 561 test `src/features/form-builder` hijau, kontrol negatif 11 test kunci terbukti merah; sesudah commit `4ab15b2b` suite penuh 39 gagal identik dengan baseline merge-base e37e4adb dan `pnpm build` lolos. Sesudah merge `origin/main` 428d41b0: tsc, eslint, dan build lolos; suite penuh 37 gagal di 13 berkas, identik dengan 13 berkas yang sama di worktree baseline 428d41b0. BE sesudah merge `origin/main`: `go vet`, `go test`, `gofmt` bersih, dan kontrol negatif dua test `file_fields` terbukti merah.
- **Dev 2026-09-11**: Form-Builder-Service di-restart 14:40Z dengan biner yang memuat `file_fields` (kontrol positif `inspeksi_satgas`, kontrol negatif 0). Lewat gateway dev (akun `panpan`), form uji berberkas membalas `file_fields [{foto_uji}]` dan `fields` tanpa pertanyaan berkas, sedangkan form tanpa berkas tak mengirim kuncinya. Form uji dihapus lunak (`6aa4179a3feb000c0d7bb0d7`, GET sesudahnya 404). Bundel `frontend-hris-dashboard` (restart 14:59Z) memuat teks panel Satgas.

**Yang belum**: deploy prod (manusia; form-builder dulu, baru frontend) dan sisa Cara Verifikasi di artefak rencana: layar alur A/B ditempuh sebagai orang, terang/gelap, sekitar 390px, id/en, dan PDF sungguhan.

## T5. Web: halaman rekap Satgas ⚠️ code selesai di branch `feat/satgas-rekap`, PR pending (2026-09-17)

**Bergantung T3.** Menu di kategori HRIS, digerbang izin modul `kepatuhan`, membaca data yang sama dengan menu MyBharata. Isi: nilai per orang per bulan, foto temuan dan perbaikan, orang yang belum dicek ulang. Menunya tak boleh bertumpu pada fallback: entri `FALLBACK` di `menu-permission.ts` wajib ada untuk izin `kepatuhan.*` (izin tanpa entri diloloskan `bolehMenu`).

**Hasil 2026-09-17** (rencana `.task-plans/2026-09-17-satgas-rekap-web-hris.md`; belum merged, belum deploy):

- **Izin baca baru** `kepatuhan.satgas.view` + paket `kepatuhan_pembaca_rekap_satgas` (dipasang IT ke posisi **Supervisor HR** dan jabatan **Culture & Industrial** — satu jabatan), di `shared-library/common/catalog_kepatuhan.go`. Pembaca rekap ≠ pengisi; petugas (`.input`) juga boleh membaca. Sudah diantisipasi komentar `catalog_kepatuhan.go` sebelumnya.
- **bip-erp** (branch `feat/satgas-rekap`): rute kaya `GET /satgas/rekap?period=YYYY-MM` (`satgas_rekap.go`) digerbang izin baca lewat JWT, memakai `nilaiSatgasPeriode` yang SAMA dengan KPI (helper `kumpulkanBahanSatgas`/`sumberSatgasDariBahan` diekstrak dari `satgas_metrics.go` untuk dipakai bersama → angka rekap = KPI, terkunci test), plus foto temuan (kiriman awal) dan perbaikan (kiriman terakhir). Rute pratinjau `GET /satgas/uploads/:uploadId/preview` (`satgas_preview.go`) digerbang izin baca + dikunci ke unggahan milik form Satgas (anti-IDOR). ⛔ **BUKAN** melebarkan `/internal/satgas/metrics` yang sempit.
- **erp-frontend** (branch `feat/satgas-rekap`): halaman `/hris/satgas` (`features/hris/satgas/*`), menu HRIS digerbang `kepatuhan.satgas.view` + entri `FALLBACK` tolak + masuk `TANPA_BYPASS_SEMUA_MENU` (super-akses IT/Direktur tak melihatnya tanpa paket → cegah alur putus 403, temuan `/review`). Picker bulan lewat query string, filter status, tabel HRIS (MainTable + Banner bare), Skeleton, dialog foto (presigned saat diklik), i18n id+en.
- **Verifikasi lokal**: form-builder `go test` hijau (termasuk `satgas_rekap_test.go`: konsistensi rekap=KPI, pemilih foto, gerbang 403 lewat Fiber); shared-library common hijau; employee-service hijau (baseline `manufacture.*` yang sudah dikenal tetap merah, bukan regresi). erp-frontend `pnpm tsc`, eslint, `pnpm build` lolos; vitest satgas (keys i18n + statusOrang + gerbang menu + bolehItemSidebar) hijau.
- **Yang belum**: PR + merge (manusia), deploy (manusia; employee-service + form-builder BERSAMA karena katalog izin di shared-library, lalu erp-frontend), IT memasang paket `kepatuhan_pembaca_rekap_satgas` ke posisi pembaca, dan verifikasi lewat gateway dev (angka rekap = draf KPI bulan sama; akun tanpa paket 403). `/sync-docs` penuh ke dok published (Form Builder Service, API, ADR 0090 §6) menyusul SESUDAH merge.

⚠️ **Bahan dari T3**: angka per orang dihitung `nilaiSatgasPeriode` (form-builder, di dalam proses, struct kaya tanpa tag JSON). Rute `/internal/satgas/metrics` sengaja SEMPIT (tanpa nama, rincian per form, dan foto), jadi rekap web butuh rute dan bentuk kirimannya sendiri yang memakai fungsi yang sama, bukan melebarkan rute internal itu.

`/start-task buat halaman rekap Satgas di HRIS erp-frontend (menu bergerbang izin kepatuhan.satgas.input, data dari endpoint yang sama dengan menu MyBharata, nilai sama dengan KPI)`

**Cara verifikasi**: angka per orang **sama persis** dengan draf KPI bulan yang sama; akun tanpa izin tidak melihat menu dan ditolak server. Struktur tabel HRIS (skill `/migrasi-tabel-hris`), tanpa `p-6` sendiri, tombol kembali lewat `SidebarBackButton`, loading pakai `Skeleton`, i18n id + en.

## T6. MyBharata: field foto + `boolean`, menu Satgas, penyaring beranda, cek ulang ⚠️ merged #144 + #1550, belum diuji di perangkat

**Bergantung T1+T2 (merged #1849).**

**Hasil 2026-09-12** (rencana `.task-plans/2026-09-12-mybharata-satgas-inspeksi.md`):

- my-bharata PR [#144](https://github.com/bip-itteam-internal/my-bharata/pull/144) (**merged** ke `dev` 2026-09-14, publish Codemagic terpicu), `feat/satgas-inspeksi` dari `origin/dev`, versi **`1.18.0+162`** (di atas `dev` `1.17.0+161`). Commit: `7c1e88e6` tipe `boolean`/`file`, `metric_key` + `isSatgas`, encoder bool; `c6eed734` unggah + kompresi + kunci tombol; `5a5c24ac` lint; `259ebf24` menu, kartu beranda, halaman Satgas, halaman isi; `4fa5203f` merge `origin/dev`; `a50365ae` versi; `6d51ce2a` tindak lanjut review (413 ke kunci sendiri, test DI dan halaman); `9be35bb6` pesan izin kamera/galeri ditolak dan perangkat tanpa kamera. Commit T3 sesudahnya tercatat di bagian T3.
- erp-frontend PR [#1550](https://github.com/bip-itteam-internal/erp-frontend/pull/1550) (**merged** 2026-09-14, sebelum adopsi 1.18.0 terukur; `feat/form-builder-berkas-wajib`, `6145448d`): mencabut aturan berkas wajib di `lib/schema.ts`, pemangkasan `required` di `lib/field-types.ts`, kunci sakelar di `components/question-row.tsx`, dan kalimat terakhir `formBuilder.question.fileHint`. Backend tak pernah melarang berkas wajib.
- **Penyimpangan dari papan (keputusan user)**: halaman `SatgasFillPage` sendiri, bukan penyesuaian `EvaluationFillPage`; kartu beranda khusus petugas; foto dari kamera **dan** galeri; larangan berkas wajib dicabut di PR terpisah yang merge-nya ditahan sampai adopsi versi T6 terukur, bukan bersama rilis. Unggah hanya mengirim field `file`, karena backend tak membaca `field_key` (sejak T3 ditambah `period_key` kartu).
- **Verifikasi lokal**: sesudah merge `origin/dev`, 640 test hijau (satgas, home, form, kaizen, live_shift, core) dan `dart analyze` per folder bersih; sesudah tindak lanjut review, 610 test hijau di folder yang tersentuh. Kontrol negatif terbukti merah: encoder bool, gerbang menu sebelum `roles == null`, favorit Satgas saat izin belum dijawab, jawaban sesudah logout dibuang, kunci tombol selama unggah, pengosongan jawaban saat unggah. PR erp-frontend: 553 test `src/features/form-builder`, tsc, eslint, dan `pnpm build` lolos.
- **Yang belum** (#144 merged 2026-09-14 sebelum ini lolos): build flavor dev di perangkat (akun berpaket melihat menu dan kartu, akun tanpa paket tidak, termasuk instalasi baru); form Satgas uji di dev (temuan dengan foto kamera ukuran penuh jadi `open_finding`, cek ulang "Tidak" dengan foto galeri jadi `resolved`, `GET /api/form-builder/me/satgas` lewat gateway dev menunjukkan status yang sama, foto terbuka di tab Individu); regresi form penilaian non-Satgas dan kirim Kaizen; ukur `app_version` petugas, yang semestinya mendahului merge #1550 (merged 2026-09-14 sebelum diukur).

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
- **Rute internal form-builder yang lebih dulu ada hanya digerbang kunci gateway** (`service-team-index`, `service-team-detail`, `kpi-checklist/metrics`), padahal gateway memasang header itu untuk setiap permintaan ber-JWT. Ditemukan saat `/start-task` T3; task keamanan tersendiri, ukur lewat gateway dulu sebelum menyimpulkan terbuka.
- **Saran Otomasi KPI `caraMengatasiKey` memetakan setiap alasan "gagal mengambil data" ke saran pemetaan toko ICC** milik sumber marketing, untuk SEMUA sumber non-marketing (bawaan lama, `auto-overview-view.tsx`). T3 hanya mendahulukan pola Satgas.

## Yang TIDAK jadi dikerjakan, beserta alasannya

- **AI penilai foto**: tidak diminta pemakai; Satgas menilai sendiri. Syarat ketiga ADR 0058 tak terpenuhi. Foto juga akan keluar ke penyedia pihak ketiga.
- **Peringkat antar departemen + master area**: yang dinilai orang (Office Boy/Security), bukan departemen.
- **Penanda `service_team_index`**: melebur skor 5R dengan rating pelayanan di KPI anggota dan atasan.
- **Tipe `report`**: melarang `subject`, dan pemutusnya atasan departemen pengirim.
- **Modul K3 manufaktur**: area ditulis mati `{Produksi, Gudang}` dan terikat penyebut KPI SPV Manufaktur.
- **Pola menu ADR 0039**: default terbuka sampai ada penugasan pertama.
- **Notifikasi ke PIC dan tautan temuan-cek ulang**: ditinjau setelah satu atau dua bulan pemakaian; butuh kategori inbox baru (form-builder + notification-service naik bersama).
- **`max_files` dan menaikkan batas 4 MB**: ditunda sampai ada pemakai kedua.
- **Batas cek ulang yang bisa diatur per form**: belum ada pemakai kedua (keputusan T3).
