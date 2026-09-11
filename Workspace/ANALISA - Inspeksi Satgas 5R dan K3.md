# ANALISA - Inspeksi Satgas 5R dan K3

Papan kerja hasil `/analisa-kebutuhan` 2026-09-11. Keputusan di [[ADR - 0090 Inspeksi Satgas 5R dan K3 di Form Builder dengan Nilai dari Cek Ulang Terakhir]], cara kerja di [[Microservices - Form Builder Service]] bagian "Inspeksi Satgas 5R & K3".

**Kebutuhan asal** (dari manajemen): posisi Culture di HRD sebagai "intel perusahaan"; budaya kepatuhan kantor (sepatu, lanyard) dicatat diam-diam lewat MyBharata dan muncul besoknya per departemen; HRD punya rutinitas Satgas 5R & K3 yang sekarang lewat Google Form "Dokumentasi Temuan Inspeksi SATGAS 5R & K3" (foto, maks 10 berkas, 10 MB).

**Hasil wawancara dan grounding:**

- Catatan atribut **sudah diputuskan** di [[ADR - 0085 Industrial Relation Catatan Kepatuhan Ringan Terpisah dari SP dan KPI]] (Faiz, 2026-09-10). Dikonfirmasi tetap sinyal pembinaan, bukan KPI. Tidak ada ADR baru untuk bagian itu; task-nya di `ANALISA - Industrial Relation`.
- Satgas 5R & K3 ternyata untuk **KPI perorangan Office Boy dan Security**. Beberapa hari setelah temuan dicek ulang, dan **nilai KPI diambil dari cek ulang**. Sekarang PIC diberi tahu manual lewat WhatsApp.
- Pemakai: OD & Industrial Relation Officer. Masalah yang mereka nyatakan: repot mengunggah dokumentasi. Solusi yang mereka minta: file upload di Form Builder.
- Diputuskan user: tetap Form Builder; menu khusus Satgas di MyBharata yang hanya muncul untuk jabatan tertentu (form Satgas tidak muncul di daftar survei); plus halaman rekap di web.
- Usulan awal yang **gugur** setelah informasi pemakai masuk: AI penilai foto, peringkat antar departemen, master area.
- Temuan data (lembar HRD "KPI DEPARTEMEN HRGA"): skor Satgas diketik dengan skala campur; Maret 2026 total KPI Office Girl 131 dari 100 lolos disetujui.

**Urutan**: T0 (keputusan HR) berjalan paralel dan wajib selesai sebelum T3 go-live. T1 → T2 → T3 (backend berantai). T4 dan T6 setelah kontrak T2 turun. T5 setelah T3. Tutup dengan T7. ⛔ **employee-service dan form-builder naik bersama, lalu web, lalu MyBharata.**

⚠️ **Koordinasi**: modul izin di T1 diusulkan dipakai juga oleh menu pencatat ADR 0085 (TBD "petugas ditunjuk"). Beri tahu Faiz sebelum T1 dimulai supaya gerbang petugas tidak dibangun dua kali.

---

## T0. Keputusan HR (bukan kode)

Jawaban wajib sebelum go-live, dicatat ke ADR 0090 §TBD:

- Rumus konversi skala 1-5 ke 0-100: `(v-1)/4` (rumus sistem, 3 = 50) atau `v/5` (praktik lembar HRD, 3 = 60).
- Cek ulang yang jatuh ke bulan berikutnya masuk periode mana.
- Jumlah field foto per orang, dan apakah foto wajib.
- Siapa selain petugas yang boleh membuka rekap web (usul: atasan Office Boy dan Security).
- Jabatan persis yang dipasangi izin Satgas.

**Cara verifikasi**: jawaban tertulis dari HR, ditempel ke ADR 0090.

## T1. BE: modul izin Satgas

Modul izin tersendiri (bukan `hris`, bukan `formbuilder`) tanpa fallback tier: katalog di `shared-library/common`, registrasi di employee-service (`permission_catalogs.go`, `DefaultPermissionSets`), paket default. Nama modul mengikuti konvensi katalog; pertimbangkan satu modul untuk petugas lapangan OD & IR dengan dua izin (Satgas + catatan kepatuhan ADR 0085).

`/start-task buat modul izin baru untuk petugas lapangan OD & IR di shared-library + employee-service (katalog, registrasi, paket default tanpa fallback tier), bukan prefiks hris atau formbuilder`

**Cara verifikasi**: modul muncul di `GET /master/permission-modules`; tanpa paket, tak seorang pun memegang izinnya; memasang paket ke jabatan uji **tidak** mencabut `hris.*` maupun `formbuilder.*` akun itu (bandingkan `/me/capability` Form Builder dan menu HRIS sebelum dan sesudah). Kontrol negatif: pasang izin berprefiks `formbuilder` ke akun uji, pastikan fallback-nya memang mati, supaya uji di atas terbukti bisa merah.

## T2. BE form-builder: penanda Satgas, gerbang pengisian, endpoint menu

**Bergantung T1.** Penanda form Satgas (sah hanya `evaluation` + berulang bulanan; ikut dikirim di `GET /me/forms`). Gerbang izin di kirim jawaban (`response_handlers.go`) **dan** unggah (`uploads.go`) untuk form bertanda. Endpoint `/me/...` meniru `/me/kaizen`: form Satgas milik pemanggil berizin + ringkasan kiriman periode ini per orang yang dinilai.

`/start-task tambah penanda form inspeksi Satgas di form-builder (evaluation + bulanan, dikirim di /me/forms), gerbang izin pada kirim jawaban dan unggah untuk form bertanda, dan endpoint /me menu Satgas meniru /me/kaizen`

**Cara verifikasi**: lewat gateway, akun tanpa izin yang masuk audience mengirim jawaban dan mengunggah ke form bertanda → `403`; akun berizin → sukses; form tanpa penanda tidak berubah perilaku. Uji `app.Test(httptest.NewRequest(...))` untuk jalur galat. Payload `/me/forms` membawa penanda (bandingkan BENTUK respons, bukan status).

## T3. BE: nilai terakhir-menang, endpoint internal, sumber KPI

**Bergantung T2 dan T0 (rumus konversi).** Satu fungsi nilai Satgas (jawaban terakhir per orang per periode, satu rumus konversi) dipakai endpoint internal form-builder, endpoint rekap/menu T2, dan tab analitik "Yang Dinilai" untuk form bertanda. Sumber KPI per orang baru di employee-service. ⛔ Jangan memakai atau menyentuh `service_team_index` / `nilai_layanan_pribadi`.

`/start-task buat fungsi nilai Satgas (jawaban terakhir per orang per periode, satu rumus konversi) untuk endpoint internal form-builder, tab analitik Yang Dinilai, dan sumber KPI per orang baru di employee-service`

**Cara verifikasi**: temuan skor 2 lalu cek ulang skor 5 untuk orang yang sama → nilai = konversi 5, **bukan** rata-rata; tab analitik menampilkan angka yang sama; orang tanpa jawaban → galat (jatuh manual), bukan 0; form ber-`service_team_index` tetap dirata-rata (uji membuktikan kedua aturan tak tertukar, dengan kontrol negatif). Satu panggilan sungguhan lewat gateway, dan draf KPI Office Boy uji terisi setelah HR memasang sumbernya di "Atur Target".

## T4. Web: field foto Form Builder + sakelar penanda

**Bergantung T2 (kontrak penanda).** Tipe `file` di editor (`types/form.ts`, `lib/schema.ts`, `lib/field-types.ts`, `components/question-row.tsx`), tampilan foto di analitik lewat pratinjau pengelola (bukan `upload_id` mentah di `lib/format-answer.ts`), kompresi gambar klien (utilitas `kompresGambar` sudah ada), sakelar penanda Satgas di editor.

`/start-task dukung field file di editor Form Builder erp-frontend (tipe, schema, field-types, question-row), tampilan foto di analitik lewat pratinjau pengelola, kompresi gambar, dan sakelar penanda Satgas`

**Cara verifikasi**: `pnpm tsc --noEmit`, `pnpm lint`, `pnpm test`, `pnpm build` (bandingkan baseline `origin/main`). ⚠️ `fieldTypeEnum` di `schema.ts` adalah literal `z.enum`, jadi compiler tidak menangkap bila lupa diubah. i18n id + en. Buat form dengan field foto, isi dari MyBharata (T6), lihat fotonya di analitik.

## T5. Web: halaman rekap Satgas

**Bergantung T3.** Menu di kategori HRIS, digerbang izin modul T1, membaca endpoint rekap yang sama dengan menu MyBharata. Isi: nilai per orang per bulan, foto temuan dan perbaikan, orang yang belum dicek ulang.

`/start-task buat halaman rekap Satgas di HRIS erp-frontend (menu bergerbang izin modul Satgas, data dari endpoint rekap yang sama dengan menu MyBharata, nilai sama dengan KPI)`

**Cara verifikasi**: angka per orang **sama persis** dengan draf KPI bulan yang sama; akun tanpa izin tidak melihat menu dan ditolak server. Struktur tabel HRIS (skill `/migrasi-tabel-hris`), tanpa `p-6` sendiri, tombol kembali lewat `SidebarBackButton`, loading pakai `Skeleton`, i18n id + en.

## T6. MyBharata: field foto, menu Satgas, penyaring beranda

**Bergantung T2.** Tipe field `file` (kamera/galeri, `maxWidth` sekitar 1920, cek ukuran di bawah 4 MB, tombol kirim terkunci selama unggah, pola unggah-dulu-kirim-id). Menu Satgas di `home_quick_access.dart` yang bertanya ke server (endpoint T2), bukan `system_roles`. Form bertanda Satgas dikeluarkan dari `SurveySection` (pola `isKaizen`; `pendingOf` tidak disaring).

`/start-task tambah tipe field file di form MyBharata (kamera, kompresi, batas 4 MB) + menu Satgas yang bertanya ke server + keluarkan form bertanda Satgas dari SurveySection`

**Cara verifikasi**: petugas berizin melihat menu, akun lain tidak, **termasuk saat cache peran kosong**; form Satgas tidak muncul di beranda, tetapi tautan notifikasinya tetap membuka form; foto ponsel ukuran penuh berhasil diunggah (terkompres). `dart analyze` per folder (bukan `flutter analyze` seluruh repo). Rilis menaikkan **version name** dan versionCode (`update_version.dart` dua argumen).

## T7. Verifikasi end-to-end + tutup dok

**Bergantung T3 sampai T6.** Satu perjalanan utuh sebagai orang, bukan `curl`: IT memasang paket izin ke jabatan petugas → petugas login ulang → isi temuan dengan foto → cek ulang beberapa hari kemudian → rekap web menampilkan nilai cek ulang → draf KPI Office Boy berisi angka yang sama → atasan memverifikasi.

Negatif: akun non-petugas ditolak `403` saat mengirim; MyBharata versi lama tidak buntu (foto belum wajib).

Tutup: perbarui status ADR 0090 dan bagian Satgas di dok Form Builder dari 🟡 ke ✅/⚠️ sesuai kenyataan, perbarui baris `Kebersihan 3` dan `Kerapihan dan kebersihan Pos` di Matriks KPI, lalu `/sync-docs`.

---

## Temuan sampingan untuk `/sync-docs` (bukan task fitur)

- Dok Form Builder belum memuat tipe `report` (keputusan per butir, unggah ulang), penanda `kpi_checklist`, dan `service_team_index` (sumber `nilai_layanan_pribadi` / `indeks_layanan_tim`).
- Matriks KPI masih menulis `Pelayanan Security` "belum dipetakan", padahal kode memakai `nilai_layanan_pribadi` untuk metrik itu (`kpi_sumber_indeks_layanan_tim.go:33-35`). Apakah template sudah memasangnya belum diukur.
- ADR 0066 / ADR 0084 dan dok Form Builder menyebut modul culture "belum merge", padahal `culture_*.go` dan `kpi_sumber_culture.go` sudah di `origin/main` (2026-09-11).
- Tipe field `boolean` di backend belum dikenal MyBharata (jatuh ke `unknown`).
- Pemakaian field `file` di prod (koleksi `form_uploads`) belum diukur.

## Yang TIDAK jadi dikerjakan, beserta alasannya

- **AI penilai foto**: tidak diminta pemakai; Satgas menilai sendiri. Syarat ketiga ADR 0058 tak terpenuhi. Foto juga akan keluar ke penyedia pihak ketiga.
- **Peringkat antar departemen + master area**: yang dinilai orang (Office Boy/Security), bukan departemen.
- **Penanda `service_team_index`**: melebur skor 5R dengan rating pelayanan di KPI anggota dan atasan.
- **Tipe `report`**: melarang `subject`, dan pemutusnya atasan departemen pengirim.
- **Modul K3 manufaktur**: area ditulis mati `{Produksi, Gudang}` dan terikat penyebut KPI SPV Manufaktur.
- **Pola menu ADR 0039**: default terbuka sampai ada penugasan pertama.
- **Notifikasi ke PIC dan tautan temuan-cek ulang**: ditinjau setelah satu atau dua bulan pemakaian; butuh kategori inbox baru (form-builder + notification-service naik bersama).
- **`max_files` dan menaikkan batas 4 MB**: ditunda sampai ada pemakai kedua.
