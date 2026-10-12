# ADR - 0173 Copilot Boleh Kueri Eksploratif Baca-Saja atas Data Bisnis Berdaftar-Izin, Dijalankan Service Pemilik

> **Status**: 🟡 **Diusulkan**, 2026-10-12, oleh panpan (Tech Development), lewat sesi `/analisa-kebutuhan`. Pemutus: **irfanarfianto**. Kode belum ada. Mengubah sebagian [[ADR - 0132 Asisten AI Tanya-Jawab Lintas Modul, Lapisan Data Bisnis per Service Bukan Terpusat]] (§4 dan butir 1-2 "Yang sengaja tidak dilakukan") dan Keputusan 3 [[Microservices - Assistant Service]]. ⛔ **Deploy PROD juga menunggu persetujuan tertulis Direksi** untuk data asli lewat relay AI (syarat ADR 0132 yang tidak diubah ADR ini).

## Untuk Manajemen

**Yang berubah di layar.** Copilot mendapat cara menjawab pertanyaan data marketing yang belum punya laporan siap pakai. Copilot menyusun sendiri pencarian ke data penjualan, iklan, live, dan afiliasi, lalu menampilkan hasilnya dengan label **"eksploratif, belum dibakukan"** beserta isi pencariannya, sehingga siapa pun bisa memeriksa ulang. Contoh yang langsung bisa dijawab: penjualan afiliasi dibanding non-afiliasi per bulan.

**Siapa yang terdampak.** Semua pemakai Copilot boleh mencoba. Hasilnya hanya keluar bila penanya memang berhak melihat data marketing di layar ERP. Pemakai lain tetap mendapat jawaban "tidak berhak", sama seperti hari ini.

**Yang tidak dijanjikan.**
- Angka eksploratif **bukan** angka resmi: hanya untuk bahan diskusi dan rapat, tidak untuk gaji, KPI, insentif, atau komisi.
- Data karyawan, gaji, data pribadi, dan data pembeli **tidak** terjangkau.
- Hanya satu sumber data per pertanyaan. Pertanyaan yang harus mencocokkan dua sumber berbeda (misalnya akun live studio dengan order afiliasi) belum bisa.
- Hasil bisa berbeda tipis bila pertanyaan yang sama diulang, karena pencariannya disusun ulang tiap kali.

**Besaran kerja.** Sedang: dua repo. Backend membangun pelaksana pencarian di service marketing dan satu alat Copilot. Frontend menambah label dan tampilan isi pencarian. Ada satu langkah manusia di produksi, yaitu membuat akun database baca-saja.

## Deskripsi

*Copilot mendapat satu tool `kueri` yang mengirim pipeline agregasi MongoDB buatan model ke eksekutor baca-saja di service PEMILIK data (marketing-analytics). Eksekutor itu yang menegakkan pagar: daftar-izin koleksi dan field, wajib agregat, gerbang analitik marketing, user Mongo read-only baru, serta batas waktu dan baris. Hasilnya masuk sebagai hasil alat berpenanda `kueri_eksploratif` dan membawa teks kuerinya. ADR ini mengganti larangan mutlak "tidak ada tool query bebas" di ADR 0132 dengan izin berpagar untuk data bisnis agregat. Larangan untuk data karyawan, gaji, pribadi, dan kredensial tetap.*

- **Status**: 🟡 Diusulkan (lihat baris status di atas)
- **Path di repo**: `bip-erp/services/marketing-analytics/kueri_eksploratif.go` (baru) · `bip-erp/services/marketing-analytics/kueri_eksploratif_handler.go` (baru) · `bip-erp/services/marketing-analytics/routes.go` · `bip-erp/services/assistant/internal/alat/kueri.go` (baru) · `bip-erp/services/assistant/internal/alat/penanda.go` · `bip-erp/services/assistant/main.go` · `bip-erp/docker-compose.yml` · `bip-erp/.env.example` · `bip-erp/scripts/mongo-user-kueri-readonly.js` (baru) · `erp-frontend/src/features/copilot/lib/penanda.ts` · `erp-frontend/src/i18n/locales/{id,en}.ts`
- **Tanggal**: 2026-10-12
- **Analisa & blueprint**: [[ANALISA - Copilot Kueri Eksploratif]]

## Context

**Pemicu.** Sesi 2026-10-12: pertanyaan "berapa penjualan dari live, dari iklan, dan organik" hanya bisa dijawab IT lewat kueri langsung ke prod (Claude Code). Hasilnya: TikTok September Rp2,41 M afiliasi vs Rp2,62 M non-afiliasi, dan Shopee September organik (non-afiliasi AMS) Rp1,07 M dari Rp2,08 M. Copilot tak punya endpoint untuk itu, dan ADR 0132 §4 mewajibkan jawaban "tidak tahu". Pemilik usulan menilai siklus "endpoint baru + tool baru" per pertanyaan terlalu lambat.

**Kebutuhan terukur lebih kecil dari dugaan, dan sebagian besar bukan marketing.** Diukur di prod `assistant_db.percakapan` (30 Sep - 12 Okt 2026, 158 giliran, 10 penanya):
- ±10 giliran menjawab "data belum tersedia di Copilot": estimasi kedatangan supplier, jam masuk per kejadian telat, penyetuju izin di HR, karyawan paling sering datang awal, anggota tim, peran penanya, setting target insentif. Pertanyaan afiliasi vs non-afiliasi **belum pernah** ditanyakan di Copilot.
- **7 giliran ditolak dengan benar**: 4 pertanyaan data pribadi ("X lahir di mana", "nomor +62… siapa", umur, agama/status nikah) dan 3 tak berhak (kontrak karyawan, telat seluruh perusahaan). Kueri bebas tanpa pagar akan menjawab ketujuhnya.
- ⚠️ Pengukuran awal sesi yang menyebut "±14 pertanyaan punya tool tapi tool-nya tak dipanggil" **keliru**: field `ukur` baru tersimpan sesudah 30 Sep, sehingga giliran hari itu yang menjawab dengan data terbaca "tanpa alat". Tidak ada bukti masalah pemilihan tool.

**Keadaan infrastruktur yang membentuk pagar.**
- Tidak ada user Mongo read-only di mana pun. Semua URI memakai `MONGO_ROOT_USER` dengan `authSource=admin` (`git grep readOnly|createUser` atas `origin/main` bip-erp hanya menemukan kunci MinIO, 2026-10-12). "Baca-saja" marketing-analytics ke `integration_db` hanya konvensi komentar ([[REF - Kepemilikan Data]] § Pengecualian).
- Samaran identitas Copilot bekerja per field yang dikenal tiap tool ([[Microservices - Assistant Service]] § Samaran identitas). Keluaran kueri bebas yang memuat field sembarang tak terjamin tersaring, jadi yang menjaga adalah daftar-izin field, bukan samaran.
- `transaction_orders` memuat `buyer` (diukur prod 2026-10-12, kunci dokumen Shopee), `live_shifts` memuat `employee_id`.
- Gerbang data marketing di layar: `common.RequireAnalitikMarketing` (marketing leader, staf integration, setara Direktur), per [[Microservices - Marketing Analytics Service]] § Prinsip Arsitektur 3.
- Tool Copilot punya timeout HTTP 20 detik (`services/assistant/main.go:166-170`), gateway 30 detik.

**Yang sudah diputuskan dan dipertahankan.** Copilot memanggil lewat gateway dengan JWT penanya (ADR 0132 Keputusan 2). Konsumsi lewat pemilik ([[REF - Kepemilikan Data]] aturan 2). Penjaga `hitungan_model` ([[ADR - 0166 Copilot Tidak Menyimpulkan Ketiadaan atau Sebab dari Satu Sumber, Cek Silang Dikerjakan Sistem dengan Tiga Keadaan]] K6). Gerbang data upah ([[ADR - 0165 Data Upah di Copilot Hanya untuk Direktur, Supervisor HRD, dan IT, Tanpa Daftar Gaji per Orang]]).

**Alternatif yang dipertimbangkan dan tidak diambil.**
- *Laporan bernama* (kueri ditulis IT, Copilot hanya memilih nama): direkomendasikan analis karena rumusnya ditinjau manusia, tapi pemilik usulan memilih kueri buatan model supaya pertanyaan baru tak menunggu PR.
- *Tetap seperti ADR 0132*: ditolak pemilik usulan karena siklus per pertanyaan.
- *Kueri bebas tanpa pagar dengan kredensial root*: ditolak karena 7 penolakan sah di atas.

## Decision

1. **Tool `kueri` di assistant-service.** Argumennya: `sumber` (`marketing_analytics` atau `integration`), `koleksi`, `pipeline` (array tahap agregasi MongoDB dalam JSON), dan `tujuan` (satu kalimat: apa yang dihitung). Tool memanggil eksekutor (butir 2) **lewat gateway dengan JWT penanya**, seperti tool lain. Tool ditawarkan ke semua pemakai `BolehPakaiCopilot`. Model diarahkan memakai tool ini **hanya bila tidak ada tool khusus** yang menjawab.
2. **Eksekutor di service pemilik: `POST /kueri-eksploratif` di marketing-analytics.** Ia sudah memegang `marketing_analytics_db` dan membaca `integration_db`, sehingga tidak ada service yang membuka jalur baca baru ke DB lain. Eksekutor menolak (400 bersebab) dan tidak pernah memperbaiki diam-diam:
   - **Daftar-izin koleksi DAN field**, satu tempat di kode. Versi awal: `marketing_analytics_db` → `mart_live_sessions`, `mart_profit_attribution`, `mart_video_performance`, `live_shifts` (tanpa `employee_id`); `integration_db` → `transaction_orders` (tanpa `buyer`, alamat, telepon, dan field identitas pembeli lain), `affiliate_orders`, `shopee_affiliate_conversion`. Field di luar daftar yang disebut di tahap mana pun = tolak.
   - **Tahap yang diizinkan**: `$match`, `$project`, `$addFields`/`$set`, `$group`, `$sort`, `$limit`, `$unwind`, `$count`, `$bucket`. Ditolak: `$lookup`, `$graphLookup`, `$unionWith`, `$out`, `$merge`, `$function`, `$accumulator`, `$where`, dan operator JavaScript apa pun.
   - **Wajib agregat**: pipeline harus memuat `$group` atau `$count`, dan tidak ada `$project` sesudahnya yang menghidupkan field mentah. Hasil = baris agregat, bukan dokumen.
   - **Batas**: `maxTimeMS` 15 detik, maksimal 200 baris keluaran, tanpa `allowDiskUse`.
3. **Gerbang mengikuti pemilik**: eksekutor digerbang `common.RequireAnalitikMarketing`, gerbang yang sama dengan layar analitik marketing. Penanya tak lolos → `tidak_berhak`, seperti tool marketing lain. Cakupan per toko yang berlaku di layar untuk peran itu juga berlaku di sini.
4. **User Mongo read-only baru**, satu per container (`Marketing-Analytics-MongoDB`, `Integration-MongoDB`), peran `read` hanya pada DB-nya. Eksekutor memakai URI terpisah dari URI tulis service. Skrip pembuatan user disiapkan di repo, **dijalankan manusia** di dev dan prod (keputusan tim 2026-08-14).
5. **Penanda dan keterbacaan**: tiap hasil membawa penanda `kueri_eksploratif` dengan teks pipeline dan `tujuan`, sumber, serta umur data. Layar Copilot menampilkan label "eksploratif, belum dibakukan" dan pipeline-nya dapat dibuka. Penjaga `hitungan_model` tetap berlaku: angka di jawaban wajib ada di hasil alat.
6. **Larangan yang tetap utuh**: DB employee, payroll, recruitment, attendance, insentive, kredensial, dan koleksi mana pun di luar daftar-izin tidak terjangkau tool ini. Menambah koleksi ke daftar-izin = PR yang menyebut alasan per field, ditinjau seperti endpoint baru.
7. **Satu sumber per panggilan.** Tidak ada join lintas DB (`$lookup` ditolak, dan lintas container memang mustahil). Mencocokkan dua sumber tidak dijanjikan di versi ini.
8. **Pemakaian angka**: hasil `kueri` tidak boleh menjadi sumber KPI, insentif, payroll, atau komisi, dan tidak boleh dipakai alat lain sebagai masukan.

## Consequences

**Positif**
- Pertanyaan data marketing baru terjawab tanpa menunggu endpoint dan tool baru.
- User read-only lahir untuk pertama kalinya, dan bisa jadi titik awal menutup utang "baca-saja hanya konvensi" di [[REF - Kepemilikan Data]].
- Kueri yang terbukti sering ditanyakan menjadi kandidat endpoint resmi: teks kuerinya sudah ada.

**Negatif / risiko yang diterima**
- **Rumus ditulis model.** Kesalahan semacam "kosong dianggap organik", menjumlahkan kolom yang tak boleh dijumlah ([[Microservices - Marketing Analytics Service]] § Aturan Pemakaian Angka), atau rentang tanggal salah tidak tertangkap penjaga mana pun. Mitigasinya hanya label eksploratif + kueri yang terlihat. Itulah alasan butir 8.
- **Jawaban tak stabil**: pertanyaan yang sama bisa menghasilkan kueri dan angka berbeda ([[REF - Penyajian Laporan Copilot]] menyatakan angka alat sama setiap kali; tool ini pengecualian).
- **Data lebih beragam lewat relay AI** ke penyedia luar. Syarat persetujuan tertulis Direksi (ADR 0132) tetap menahan deploy prod.
- **Daftar-izin field harus dijaga tiap kali skema berubah**: field identitas baru di `transaction_orders` tidak otomatis tertolak bila daftar-izinnya berupa daftar-tolak. Karena itu daftar-izin berupa **izin**, bukan tolak.
- **Beban DB prod**: agregasi tanpa indeks atas `transaction_orders` (ratusan ribu dokumen) bisa berat. `maxTimeMS` membatasi tiap kueri, tetapi tidak membatasi jumlah penanya serentak.

**Deploy**
- Urutan: (1) manusia membuat user read-only di kedua container; (2) env URI read-only baru di blok marketing-analytics, lalu `docker compose up -d --force-recreate`, bukan restart; (3) marketing-analytics; (4) assistant-service; (5) frontend. Merged duluan boleh, deploy duluan tidak.
- PROD hanya sesudah persetujuan tertulis Direksi.

## Dokumen Terkait

- [[ADR - 0132 Asisten AI Tanya-Jawab Lintas Modul, Lapisan Data Bisnis per Service Bukan Terpusat]]: diubah sebagian oleh ADR ini
- [[Microservices - Assistant Service]]: dok domain, § Tool kueri eksploratif
- [[ADR - 0166 Copilot Tidak Menyimpulkan Ketiadaan atau Sebab dari Satu Sumber, Cek Silang Dikerjakan Sistem dengan Tiga Keadaan]]
- [[ADR - 0165 Data Upah di Copilot Hanya untuk Direktur, Supervisor HRD, dan IT, Tanpa Daftar Gaji per Orang]]
- [[REF - Kepemilikan Data]] · [[REF - Penyajian Laporan Copilot]]
- [[Microservices - Marketing Analytics Service]]
- [[ANALISA - Copilot Kueri Eksploratif]]
