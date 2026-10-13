# ADR - 0173 Copilot Boleh Kueri Eksploratif Baca-Saja ke Data Semua Service, Dijalankan Service Pemilik, Kredensial Dikecualikan

> **Status**: 🟢 **Diterima**, 2026-10-13, oleh irfanarfianto (ditegaskan di sesi Claude Code 2026-10-13). Diusulkan 2026-10-12 lewat sesi `/analisa-kebutuhan`. Pemutus: **irfanarfianto**. Kode belum ada. Diperluas dari "data marketing saja" ke semua service pada hari yang sama. Bila diterima, ADR ini mengubah sebagian [[ADR - 0132 Asisten AI Tanya-Jawab Lintas Modul, Lapisan Data Bisnis per Service Bukan Terpusat]] (§4 dan butir 1-2 "Yang sengaja tidak dilakukan"), [[ADR - 0165 Data Upah di Copilot Hanya untuk Direktur, Supervisor HRD, dan IT, Tanpa Daftar Gaji per Orang]] (batas 20 baris dan larangan daftar gaji per orang), serta Keputusan 3 [[Microservices - Assistant Service]]. Di ADR 0165, "siapa boleh melihat" berasal dari pemilik produk dan **tidak** diubah; batas 20 baris dipilih pelaksana (ADR 0165 baris status), dan itulah yang diubah di sini. ⛔ **Deploy PROD menunggu persetujuan tertulis Direksi** untuk data asli lewat relay AI (syarat ADR 0132 yang tidak diubah ADR ini).

## Untuk Manajemen

**Yang berubah di layar.** Copilot bisa menjawab pertanyaan data dari modul ERP mana pun (marketing, HR, presensi, payroll, rekrutmen, keuangan, pengadaan, gudang, produksi, tiket, dan lainnya) walaupun belum ada laporan siap pakai. Copilot menyusun sendiri pencarian ke data, lalu menampilkan hasilnya dengan label **"eksploratif, belum dibakukan"** beserta isi pencariannya. Pencarian yang sudah diperiksa tim IT dan dinyatakan benar disimpan, dan pertanyaan yang sama berikutnya memakai pencarian itu tanpa label eksploratif.

**Siapa melihat apa.**
- Direktur, Supervisor HRD, dan tim IT melihat seluruh data, termasuk daftar gaji per orang.
- Supervisor lain hanya melihat data departemennya sendiri.
- Data per orang (misalnya telat atau KPI per karyawan) boleh tampil sesuai batas itu.

**Yang tidak dijanjikan.**
- Angka eksploratif **bukan** angka resmi: tidak untuk menghitung gaji, KPI, insentif, atau komisi.
- Kata sandi, token, dan kunci akses sistem tidak pernah terjangkau.
- **Data identitas pribadi (NIK, rekening, tanggal lahir, telepon) tetap tidak terkirim** ke model AI sampai ada persetujuan tertulis Direksi, karena model AI-nya berada di penyedia di luar perusahaan.
- Hanya satu sumber data per pencarian. Mencocokkan dua modul sekaligus belum bisa.
- Hasil eksploratif bisa berbeda tipis bila pertanyaan yang sama diulang.

**Besaran kerja.** Besar: dua repo. Backend membangun satu pelaksana pencarian bersama, memasangnya di sekitar 19 service, menambah alat Copilot, dan menyimpan pencarian terverifikasi. Frontend menambah label, tampilan isi pencarian, dan tombol verifikasi untuk IT. Ada satu langkah manusia di produksi per database, yaitu membuat akun baca-saja.

## Deskripsi

*Copilot mendapat tool `kueri` yang mengirim pipeline agregasi MongoDB buatan model ke **eksekutor bersama** (`shared-library`) yang dipasang di tiap service pemilik data. Eksekutor itu menegakkan pagar: daftar-tolak kredensial, cakupan departemen yang disisipkan server, tahap agregasi berdaftar-izin, user Mongo read-only, serta batas waktu dan baris. Hasil membawa penanda `kueri_eksploratif`, teks kueri, dan kamus kolom. Kueri yang ditandai terverifikasi oleh IT disimpan dan dipakai ulang tanpa label eksploratif. ADR ini mengganti larangan mutlak "tidak ada tool query bebas" di ADR 0132 dengan izin berpagar. Samaran identitas sebelum relay AI tidak diubah.*

- **Status**: 🟡 Diusulkan (lihat baris status di atas)
- **Path di repo**: `bip-erp/shared-library/kueri/` (baru: eksekutor, validator pipeline, cakupan, kamus kolom, pemindai kredensial) · `bip-erp/services/{marketing-analytics,integration,insentive,tiktok-shop-service,employee,attendance,payroll,recruitment,learning,hrd-document,finance,procurement,warehouse,manufacture,inventory,task-management,form-builder,calendar,notification}/kueri_eksploratif.go` (baru, satu per service) · `bip-erp/services/*/routes.go` · `bip-erp/services/assistant/internal/alat/kueri.go` (baru) · `bip-erp/services/assistant/internal/kueriverifikasi/` (baru) · `bip-erp/services/assistant/internal/alat/penanda.go` · `bip-erp/services/assistant/main.go` · `bip-erp/docker-compose.yml` · `bip-erp/.env.example` · `bip-erp/scripts/mongo-user-kueri-readonly.js` (baru) · `erp-frontend/src/features/copilot/` · `erp-frontend/src/i18n/locales/{id,en}.ts`
- **Tanggal**: 2026-10-12
- **Analisa & blueprint**: [[ANALISA - Copilot Kueri Eksploratif]]

## Context

**Pemicu.** Sesi 2026-10-12: pertanyaan "berapa penjualan dari live, dari iklan, dan organik" hanya bisa dijawab IT lewat kueri langsung ke prod. Hasilnya: TikTok September Rp2,41 M afiliasi vs Rp2,62 M non-afiliasi, dan Shopee September organik (non-afiliasi AMS) Rp1,07 M dari Rp2,08 M. Copilot tak punya endpoint untuk itu, dan ADR 0132 §4 mewajibkan jawaban "tidak tahu". Pemilik usulan menilai siklus "endpoint baru + tool baru" per pertanyaan terlalu lambat, dan memutuskan cakupannya semua service sekaligus.

**Kebutuhan terukur.** Diukur di prod `assistant_db.percakapan` (30 Sep - 12 Okt 2026, 158 giliran, 10 penanya):
- ±10 giliran menjawab "data belum tersedia di Copilot", **sebagian besar HR dan procurement**: estimasi kedatangan supplier, jam masuk per kejadian telat, penyetuju izin di HR, karyawan paling sering datang awal, anggota tim, peran penanya, setting target insentif. Pertanyaan afiliasi vs non-afiliasi belum pernah ditanyakan di Copilot.
- 4 pertanyaan data pribadi ("X lahir di mana", "nomor +62… siapa", umur, agama/status nikah) dan 3 tak berhak (kontrak karyawan, telat seluruh perusahaan) ditolak dengan benar.
  - Di bawah ADR ini, yang tak berhak tetap ditolak karena cakupan departemen.
  - Data pribadi tetap tertahan samaran (Decision §6).
- ⚠️ Pengukuran awal sesi yang menyebut "±14 pertanyaan punya tool tapi tool-nya tak dipanggil" **keliru**: field `ukur` baru tersimpan sesudah 30 Sep.

**Keadaan yang membentuk pagar.**
- Ada 24 folder service. 19 di antaranya memegang data bisnis di container Mongo masing-masing. `assistant` (riwayat percakapan orang lain), `vault-mcp`, `file`, `monitoring`, dan `.template` tidak termasuk.
- **Tidak ada user Mongo read-only** di repo; semua URI memakai `MONGO_ROOT_USER` (`git grep readOnly|createUser` atas `origin/main`, 2026-10-12).
- Kredensial tersimpan di beberapa koleksi: `integration_db.credentials`, `accurate_credentials`, `accurate_bank_accounts`, kredensial marketplace, serta `employee_db.system_authentication` (berisi hash password), menurut [[DB - Overview and Notes]] dan [[REF - Kepemilikan Data]].
- Samaran Copilot menahan kiriman bila masih ada sisa identitas, dan dekode berdaftar-putihnya membuang NIK, NPWP, rekening, BPJS, telepon, email, serta alamat ([[Microservices - Assistant Service]] § Samaran identitas). Alasannya: persetujuan tertulis Direksi untuk data asli ke relay AI belum ada (ADR 0132).
- ⛔ Label grup departemen seperti `HRGA` bukan nama departemen siapa pun. Saringan departemen yang memakai `SupervisedDepartments` atas nilai dari luar menghasilkan **200 berisi nol baris** tanpa galat (dua kejadian 2026-08-26, team-memory § RBAC). Yang benar `ExpandToDepartmentGroup(ResolveDepartmentFilter(...))`.
- ADR 0165 (🟡 Diusulkan, keputusan pemilik produk): data upah hanya untuk Direktur, Supervisor HRD, dan IT, tanpa daftar gaji per orang (peringkat paling banyak 20 baris). Pemilik usulan ADR ini memutuskan daftar penuh boleh untuk ketiga kelompok itu.

**Yang dipertahankan.**
- Copilot memanggil lewat gateway dengan JWT penanya (ADR 0132 Keputusan 2).
- Data dikonsumsi lewat pemiliknya ([[REF - Kepemilikan Data]] aturan 2).
- Penjaga `hitungan_model` ([[ADR - 0166 Copilot Tidak Menyimpulkan Ketiadaan atau Sebab dari Satu Sumber, Cek Silang Dikerjakan Sistem dengan Tiga Keadaan]] K6).
- Samaran identitas.

**Alternatif yang dipertimbangkan dan tidak diambil.**
- *Laporan bernama* (kueri ditulis IT, Copilot hanya memilih nama): rumusnya ditinjau manusia, tapi pertanyaan baru tetap menunggu PR. Sebagian sifatnya diambil lewat kueri terverifikasi (Decision §8).
- *Hanya data marketing*: versi awal ADR ini. Ditolak karena kebutuhan terukur justru dominan HR dan procurement.
- *Bertahap per service*: ditolak pemilik usulan, dan dipilih semua sekaligus. Eksekutor bersama (§2) membuat pemasangan per service tipis.
- *Kueri bebas dengan kredensial root tanpa pagar*: ditolak karena membuka kredensial dan melewati cakupan departemen.

## Decision

1. **Tool `kueri` di assistant-service.**
   - Argumen: `service`, `koleksi`, `pipeline` (tahap agregasi MongoDB dalam JSON), `tujuan` (satu kalimat).
   - Tool memanggil eksekutor service yang dituju **lewat gateway dengan JWT penanya**.
   - Ditawarkan ke semua pemakai `BolehPakaiCopilot`. Model diarahkan memakainya **hanya bila tidak ada tool khusus** yang menjawab.
2. **Eksekutor bersama di `shared-library/kueri`**, dipasang sebagai `POST /kueri-eksploratif` di tiap service pemilik data. Satu kode, sehingga aturan pagar tidak punya salinan per service.
   - Tiap service hanya mendaftarkan dua hal: koleksinya, dan fungsi cakupan per koleksi (§4).
   - Service yang belum mendaftar tidak punya rute ini.
3. **Pengecualian: kredensial dan token, di semua service.**
   - Koleksi kredensial ditolak utuh: `credentials`, `accurate_credentials`, `accurate_bank_accounts`, `system_authentication`, dan koleksi kredensial marketplace.
   - Field yang namanya cocok pola rahasia (`token`, `secret`, `password`, `pass_hash`, `api_key`, `private_key`, `client_secret`, `refresh_token`, `access_token`) ditolak di koleksi mana pun.
   - Karena bentuknya **daftar-tolak**, sebuah test memindai seluruh entity tiap service dan memerahkan build bila ada field atau koleksi baru yang cocok pola rahasia tapi belum tercatat ditolak. Dengan begitu field rahasia baru tidak lolos diam-diam.
4. **Cakupan disisipkan server, tidak dipercayakan ke model.**
   - Kelompok **lihat semua**: Direktur, setara Direktur (Corporate Secretary), Supervisor HRD, dan anggota IT.
   - Pemakai Copilot lain: eksekutor menyisipkan `$match` cakupan departemen di **awal** pipeline, dari departemen yang ia supervisi. Departemennya diturunkan lewat `ExpandToDepartmentGroup(ResolveDepartmentFilter(...))`, bukan `SupervisedDepartments` atas nilai mentah.
   - Tiap koleksi mendaftarkan cara menyaringnya: field departemen langsung, `employee_id` milik departemen itu, atau toko milik departemen (`department_shops`).
   - Koleksi tanpa dimensi departemen hanya terbuka untuk kelompok lihat semua.
   - Gerbang modul pemilik (mis. `RequireAnalitikMarketing`, `BolehPayrollCopilot`) tetap berlaku di atas cakupan ini.
5. **Data per orang boleh**, dalam cakupan §4. Untuk payroll: Direktur, Supervisor HRD, dan IT boleh daftar gaji penuh per orang. Ini mengubah batas 20 baris ADR 0165 untuk jalur ini saja; tool payroll khusus tetap memakai aturannya.
6. **Samaran identitas TIDAK diubah.**
   - Hasil kueri melewati samaran dan penjaga `BocorDi` seperti tool lain.
   - Kiriman yang masih memuat NIK, NPWP, rekening, BPJS, telepon, email, alamat, atau tanggal lahir **ditahan**, sehingga data itu secara efektif tak terjawab.
   - Ini bertahan sampai persetujuan tertulis Direksi dan tinjauan perlindungan data pribadi. Membukanya butuh ADR tersendiri.
7. **Bentuk pipeline.**
   - Tahap yang diizinkan: `$match`, `$project`, `$addFields`/`$set`, `$group`, `$sort`, `$limit`, `$skip`, `$unwind`, `$count`, `$bucket`, `$facet` (isinya tunduk aturan yang sama).
   - Ditolak: `$lookup`, `$graphLookup`, `$unionWith`, `$out`, `$merge`, `$function`, `$accumulator`, `$where`, dan operator JavaScript apa pun.
   - Batas: `maxTimeMS` 15 detik, maksimal 500 baris keluaran (bertanda `terpotong`), tanpa `allowDiskUse`.
   - Eksekutor memakai **user Mongo read-only** baru, satu per container, peran `read` hanya pada DB service itu. Skrip pembuatannya disiapkan di repo dan **dijalankan manusia**.
8. **Kamus kolom dan kueri terverifikasi.**
   - **Kamus kolom**: tiap service mendaftarkan arti, satuan, dan aturan pemakaian kolomnya (mis. "`24h_live_gmv` jangan dijumlah dengan `gmv`", "`shopee_attribution` kosong = belum dilabeli, bukan organik") di satu tempat di kode, dekat entity-nya. Eksekutor mengirimnya bersama hasil, dan tool `kueri` membacanya. Tidak ada salinan aturan kolom di prompt.
   - **Kueri terverifikasi**: assistant-service menyimpan kueri yang ditandai **terverifikasi oleh anggota IT** (koleksi baru di `assistant_db`: pertanyaan contoh, service, koleksi, pipeline, penanda, tanggal). Pertanyaan yang cocok memakai kueri itu, dan hasilnya tidak berlabel eksploratif tapi menyebut "kueri terverifikasi <tanggal>". Status terverifikasi bisa dicabut.
   - Kueri yang belum diverifikasi **tidak pernah** dipakai ulang otomatis.
9. **Penanda dan keterbacaan.**
   - Tiap hasil eksploratif membawa penanda `kueri_eksploratif` dengan teks pipeline dan `tujuan`, sumber, serta umur data.
   - Layar Copilot menampilkan label "eksploratif, belum dibakukan", dan pipeline-nya dapat dibuka.
   - Penjaga `hitungan_model` tetap berlaku.
10. **Satu sumber per panggilan.** Tidak ada join lintas service. Mencocokkan dua modul tidak dijanjikan.
11. **Pemakaian angka**: hasil eksploratif tidak boleh menjadi sumber KPI, insentif, payroll, atau komisi, dan tidak boleh dipakai alat lain sebagai masukan.

## Consequences

**Positif**
- Pertanyaan data dari modul mana pun terjawab tanpa menunggu endpoint dan tool baru. Kebutuhan terukur di prod (dominan HR dan procurement) ikut tertutup.
- Cakupan departemen ditegakkan di satu kode bersama. Ini lebih seragam daripada gerbang yang selama ini ditulis per endpoint.
- User Mongo read-only lahir di setiap container, sehingga utang "baca-saja hanya konvensi" ([[REF - Kepemilikan Data]]) ikut berkurang.
- Kueri terverifikasi menjadi jalan murah dari pertanyaan eksploratif ke jawaban yang stabil.

**Negatif / risiko yang diterima**
- **Rumus ditulis model.** Kesalahan semacam label kosong dianggap organik, kolom yang tak boleh dijumlah ikut dijumlah, atau rentang tanggal salah tidak tertangkap penjaga mana pun. Mitigasinya: kamus kolom, label eksploratif, kueri terlihat, kueri terverifikasi, dan butir 11.
- **Cakupan ditulis ulang per koleksi.** Fungsi cakupan per koleksi (§4) adalah salinan ke-N dari aturan "siapa boleh melihat apa" yang sudah ada di endpoint tiap service, dan salinan bisa menyimpang. Tiap fungsi cakupan wajib diuji terhadap gerbang endpoint yang setara, termasuk kasus grup `HRGA`.
- **Daftar gaji penuh** kini terjangkau dari percakapan untuk tiga kelompok. Itu berbeda dari ADR 0165, dan pemilik produk ADR 0165 perlu menyetujuinya.
- **Daftar-tolak lebih rapuh daripada daftar-izin.** Penjaganya pemindai entity (§3). Koleksi rahasia yang tidak lewat entity Go (mis. dibuat skrip) tidak terpindai.
- **Jawaban tak stabil** untuk kueri yang belum terverifikasi ([[REF - Penyajian Laporan Copilot]] menyatakan angka alat sama setiap kali; ini pengecualian).
- **Beban DB prod**: agregasi tanpa indeks atas koleksi besar bisa berat. `maxTimeMS` membatasi tiap kueri, tetapi tidak membatasi jumlah penanya serentak.
- **Data lebih beragam lewat relay AI** ke penyedia luar. Persetujuan tertulis Direksi tetap menahan deploy prod.

**Deploy**
- Urutan:
  1. Manusia membuat user read-only per container.
  2. Env URI read-only per service, lalu `docker compose up -d --force-recreate <svc>`, bukan restart.
  3. Service pemilik data, per area.
  4. assistant-service.
  5. Frontend.
- Merged duluan boleh, deploy duluan tidak. Service yang belum naik cukup tidak ditawarkan ke tool, bukan galat.
- PROD hanya sesudah persetujuan tertulis Direksi.

## Dokumen Terkait

- [[ADR - 0132 Asisten AI Tanya-Jawab Lintas Modul, Lapisan Data Bisnis per Service Bukan Terpusat]]: diusulkan diubah sebagian
- [[ADR - 0165 Data Upah di Copilot Hanya untuk Direktur, Supervisor HRD, dan IT, Tanpa Daftar Gaji per Orang]]: diusulkan diubah sebagian
- [[Microservices - Assistant Service]]: dok domain, § Tool kueri eksploratif
- [[Microservices - Payroll Service]]
- [[ADR - 0166 Copilot Tidak Menyimpulkan Ketiadaan atau Sebab dari Satu Sumber, Cek Silang Dikerjakan Sistem dengan Tiga Keadaan]]
- [[REF - Kepemilikan Data]] · [[REF - Penyajian Laporan Copilot]] · [[DB - Overview and Notes]]
- [[ANALISA - Copilot Kueri Eksploratif]]
