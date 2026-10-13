**Status**: 🟡 Blueprint dari `/analisa-kebutuhan` 2026-10-12 (diperluas ke semua service pada hari yang sama). Keputusannya di [[ADR - 0173 Copilot Boleh Kueri Eksploratif Baca-Saja ke Data Semua Service, Dijalankan Service Pemilik, Kredensial Dikecualikan]]; dok domain [[Microservices - Assistant Service]] § Tool kueri eksploratif. Dok ini papan kerja, bukan arsitektur.

✅ ADR 0173 **Diterima** 2026-10-13 oleh irfanarfianto. Urutan pengerjaan yang diputuskan: #3024 dulu sampai merged, lalu sisanya.

- **Pemutus**: irfanarfianto
- **Ukuran**: **Besar**. Dua repo, dan `bip-erp` butuh enam PR (eksekutor bersama, tool + kueri terverifikasi, empat pemasangan per area). FE harus berubah karena kode penanda yang tak dikenal tampil sebagai label umum tanpa teks kuerinya (`erp-frontend/src/features/copilot/lib/penanda.ts:7-9`), dan karena tombol verifikasi untuk IT belum ada. Bentuknya induk + tujuh sub-issue saudara.
- **Syarat PROD di luar issue**: persetujuan tertulis Direksi untuk data asli lewat relay AI (ADR 0132), dan user Mongo read-only dibuat manusia di tiap container.

## Kebutuhan yang dijawab

Pertanyaan data dari modul mana pun yang belum punya endpoint dijawab Copilot tanpa menunggu siklus endpoint + tool baru. Pemakainya pemakai Copilot: Direktur, Supervisor HRD, dan IT melihat semua, sedangkan supervisor lain hanya departemennya. Angka eksploratif untuk bahan diskusi dan rapat, bukan uang. Kueri yang diverifikasi IT dipakai ulang tanpa label.

Ukur prod `assistant_db.percakapan` (30 Sep - 12 Okt 2026): ±10 dari 158 giliran menjawab "data belum tersedia", dominan HR dan procurement.

## Urutan

1. Induk tanpa PR.
2. **1/7 [BE] eksekutor bersama.**
3. **2/7 [BE] tool + kueri terverifikasi**, dan 3/7 sampai 6/7 pemasangan per area (paralel). Semuanya dikerjakan sesudah 1/7 merged.
4. **7/7 [FE]**, deploy sesudah 2/7.

Deploy:
1. User read-only per container (manusia).
2. Env URI read-only + `--force-recreate` per service.
3. Service per area.
4. assistant-service.
5. Frontend.

---

### Induk: Copilot: tool kueri eksploratif baca-saja (ADR 0173)

- **Repo**: bip-erp
- **Issue**: [bip-erp#3023](https://github.com/bip-itteam-internal/bip-erp/issues/3023)

**Pemutus:** @irfanarfianto
**PIC:** @

## Masalah

Copilot menjawab "tidak tahu" untuk pertanyaan data yang belum punya endpoint (ADR 0132 §4), dan menambah endpoint + tool per pertanyaan dinilai terlalu lambat. Rincian tiap bagian ada di sub-issue.

## Keputusan

[[ADR - 0173 Copilot Boleh Kueri Eksploratif Baca-Saja ke Data Semua Service, Dijalankan Service Pemilik, Kredensial Dikecualikan]]. Layak `Siap Agent` sesudah ADR itu berstatus Diterima (sekarang 🟡 Diusulkan).

## Yang harus benar

- [ ] Ketujuh sub-issue merged.
- [ ] DEV, sebagai IT: "penjualan TikTok afiliasi vs non-afiliasi September 2026" menghasilkan tabel berlabel eksploratif dengan kuerinya terlihat.
- [ ] DEV, sebagai supervisor non-HRD: kueri presensi hanya mengembalikan departemennya. Kueri ke departemen lain mendapat nol baris berpenanda cakupan, bukan data.
- [ ] DEV: kueri yang menyebut koleksi kredensial ditolak.
- [ ] DEV: kueri yang ditandai terverifikasi dipakai ulang tanpa label eksploratif.

## Di luar cakupan

Join lintas service, membuka samaran identitas, dan deploy PROD (menunggu Direksi + manusia).

## Data / bukti pendukung

Lihat ADR 0173 § Context.

## Prasyarat

Tidak ada.

---

### 1/7 [BE] Eksekutor kueri eksploratif bersama di shared-library

- **Repo**: bip-erp (sub-issue induk)
- **Issue**: [bip-erp#3024](https://github.com/bip-itteam-internal/bip-erp/issues/3024)

**Pemutus:** @irfanarfianto
**PIC:** @

## Masalah

Tidak ada jalur baca terkendali untuk kueri agregasi ad-hoc. Semua koneksi Mongo memakai root (`git grep readOnly|createUser` atas `origin/main`: nol, 2026-10-12).

## Keputusan

ADR 0173 §2, §3, §4, §7, §8 (kamus kolom). Layak `Siap Agent` sesudah ADR itu Diterima. Bentuknya: paket `shared-library/kueri` yang menyediakan handler `POST /kueri-eksploratif` siap pasang. Service pemakai mendaftarkan koleksi, fungsi cakupan per koleksi, dan kamus kolom.

## Yang harus benar

- [ ] Validator pipeline: hanya tahap di ADR 0173 §7. `$lookup`, `$graphLookup`, `$unionWith`, `$out`, `$merge`, `$function`, `$accumulator`, `$where`, serta operator JavaScript ditolak 400 bersebab, termasuk di dalam `$facet`.
- [ ] Daftar-tolak kredensial: koleksi `credentials`, `accurate_credentials`, `accurate_bank_accounts`, `system_authentication`, dan kredensial marketplace ditolak utuh. Field berpola `token|secret|password|pass_hash|api_key|private_key|client_secret|refresh_token|access_token` ditolak di koleksi mana pun dan di tahap mana pun.
- [ ] Test pemindai: memindai tag `bson` seluruh entity di `services/*` dan `shared-library/models`. Field atau koleksi yang cocok pola rahasia tapi belum tercatat ditolak membuat test merah. Kontrol negatif: tambahkan field `api_key` palsu, pastikan test merah.
- [ ] Cakupan: kelompok lihat semua (Direktur, setara Direktur, Supervisor HRD, anggota IT) tanpa saringan. Pemakai lain: `$match` cakupan disisipkan di **awal** pipeline dari `ExpandToDepartmentGroup(ResolveDepartmentFilter(...))`. Koleksi tanpa fungsi cakupan → 403 untuk pemakai lain.
- [ ] Test cakupan dengan label grup `HRGA`: supervisor `Human Resource` mendapat baris `General Affair` juga, dan hasilnya tidak nol.
- [ ] Batas: `maxTimeMS` 15000, maksimal 500 baris (`terpotong: true`), tanpa `allowDiskUse`.
- [ ] Koneksi memakai URI read-only (env terpisah). URI kosong → rute membalas 503 bersebab, service tetap hidup.
- [ ] Kamus kolom: API pendaftaran `{koleksi, field, arti, satuan, aturan}` di dekat entity tiap service. Isinya ikut dikirim bersama hasil.
- [ ] Skrip `scripts/mongo-user-kueri-readonly.js` (dry-run + apply) membuat user ber-peran `read` per DB. **Tidak dijalankan agent di prod.**
- [ ] Test lewat `app.Test` mereproduksi pemotongan prefix gateway, sehingga rute bekerja di akar modul.

## Di luar cakupan

Pemasangan di service (3/7 sampai 6/7), tool di assistant (2/7), FE (7/7), dan menjalankan skrip user.

## Data / bukti pendukung

Daftar container Mongo dari `docker-compose.yml` `origin/main` 2026-10-12: Attendance, Calendar, Employee (Primary), Finance, Form-Builder, HRD-Document, Insentive, Integration, Inventory, Learning, Manufacture, Marketing-Analytics, Notification, Payroll, Procurement, Recruitment, Task-Management, TikTok-Shop, Warehouse (+ Assistant, Vault-MCP, Template yang tidak dipasangi).

## Prasyarat

ADR 0173 Diterima.

---

### 2/7 [BE] Tool kueri dan kueri terverifikasi di assistant-service

- **Repo**: bip-erp (sub-issue induk)
- **Issue**: [bip-erp#3025](https://github.com/bip-itteam-internal/bip-erp/issues/3025)

**Pemutus:** @irfanarfianto
**PIC:** @

## Masalah

Copilot tidak punya tool untuk pertanyaan yang tak dilayani tool khususnya (±10 dari 158 giliran prod, 30 Sep - 12 Okt 2026), dan tidak punya cara menyimpan jawaban yang sudah terbukti benar.

## Keputusan

ADR 0173 §1, §6, §8, §9, §11. Layak `Siap Agent` sesudah ADR itu Diterima.

## Yang harus benar

- [ ] Tool `kueri` (argumen `service`, `koleksi`, `pipeline`, `tujuan`) untuk semua pemakai `BolehPakaiCopilot`. Ia memanggil `POST /api/<module>/kueri-eksploratif` lewat gateway dengan `Authorization` penanya. Service yang belum memasang eksekutor tidak ditawarkan.
- [ ] Deskripsi tool mengarahkan model memakainya hanya bila tak ada tool khusus. Daftar service + koleksi diambil dari satu sumber, bukan diketik ulang.
- [ ] 403 → `tidak_berhak`; 400 → galat bersebab diteruskan ke model untuk diperbaiki (satu jatah); 503 → "sumber belum tersedia".
- [ ] Penanda `kueri_eksploratif` membawa pipeline, `tujuan`, kamus kolom, sumber, dan umur data. `hitungan_model`, `angka_tak_cocok`, samaran, dan `BocorDi` tetap jalan. Kiriman berisi identitas tetap ditahan.
- [ ] Koleksi `kueri_terverifikasi` di `assistant_db`: pertanyaan contoh, service, koleksi, pipeline, penanda, tanggal, dan siapa yang menandai. Endpoint tandai/cabut **hanya untuk anggota IT**.
- [ ] Pertanyaan yang cocok dengan kueri terverifikasi memakai pipeline tersimpan (tetap lewat eksekutor dan cakupan penanya), dan hasilnya berlabel "kueri terverifikasi <tanggal>". Kueri yang belum diverifikasi tidak pernah dipakai ulang otomatis.
- [ ] Uji pertanyaan tetap: satu kasus eksploratif + satu kasus terverifikasi.

## Di luar cakupan

Eksekutor (1/7), pemasangan service, dan FE.

## Data / bukti pendukung

Ukur prod `assistant_db.percakapan` 2026-10-12: 158 giliran, 10 penanya, ±10 "belum tersedia".

## Prasyarat

1/7 merged. Deploy sesudah minimal satu service pemasang naik.

---

### 3/7 [BE] Pasang eksekutor kueri: area marketing dan marketplace

- **Repo**: bip-erp (sub-issue induk)
- **Issue**: [bip-erp#3026](https://github.com/bip-itteam-internal/bip-erp/issues/3026)

**Pemutus:** @irfanarfianto
**PIC:** @

## Masalah

Data marketing dan marketplace belum bisa dikueri Copilot di luar 12 tool khusus.

## Keputusan

ADR 0173 §2-§4, §8. Layak `Siap Agent` sesudah ADR itu Diterima. Service: `marketing-analytics`, `integration`, `insentive`, `tiktok-shop-service`.

## Yang harus benar

- [ ] Tiap service memasang `POST /kueri-eksploratif` dari `shared-library/kueri` dengan daftar koleksinya.
- [ ] Fungsi cakupan per koleksi: toko milik departemen (`department_shops`) untuk data per toko, dan `employee_id` departemen untuk data per orang. Gerbang modul pemilik (`RequireAnalitikMarketing` dan sejenisnya) tetap berlaku.
- [ ] Kamus kolom memuat seluruh aturan [[Microservices - Marketing Analytics Service]] § Aturan Pemakaian Angka (`24h_live_gmv`, `iklan_sia_sia`, `retur`, `per_orang`, `pembatalan`, `shopee_attribution` kosong ≠ organik, `orders` = `sku_orders`).
- [ ] `integration`: koleksi kredensial tertolak (dibuktikan test). Identitas pembeli tetap tertahan samaran.
- [ ] Test cakupan per service terhadap gerbang endpoint setara.

## Di luar cakupan

Area lain.

## Data / bukti pendukung

Kunci `transaction_orders` prod 2026-10-12 memuat `buyer`, `items`, `payment`. Rincian di ADR 0173 § Context.

## Prasyarat

1/7 merged.

---

### 4/7 [BE] Pasang eksekutor kueri: area HR

- **Repo**: bip-erp (sub-issue induk)
- **Issue**: [bip-erp#3027](https://github.com/bip-itteam-internal/bip-erp/issues/3027)

**Pemutus:** @irfanarfianto
**PIC:** @

## Masalah

Pertanyaan HR yang terukur tak terjawab di prod (jam masuk per kejadian telat, penyetuju izin, karyawan paling sering datang awal, anggota tim).

## Keputusan

ADR 0173 §2-§5, §8. Layak `Siap Agent` sesudah ADR itu Diterima. Service: `employee`, `attendance`, `payroll`, `recruitment`, `learning`, `hrd-document`. Daftar gaji per orang boleh untuk kelompok lihat semua (§5).

## Yang harus benar

- [ ] Tiap service memasang eksekutor dengan daftar koleksinya. `system_authentication` tertolak.
- [ ] Cakupan per koleksi lewat `work_data.department` / `employee_id` departemen, dengan jebakan `HRGA` diuji.
- [ ] `payroll`: di atas cakupan, `BolehPayrollCopilot` tetap menggerbang. Supervisor non-HRD mendapat 403 untuk koleksi payroll.
- [ ] Kamus kolom memuat aturan [[Microservices - Payroll Service]] (mis. `period` bukan bulan gaji) dan aturan presensi yang relevan.
- [ ] Field identitas (`personal_data`, `personal_document`) boleh dikueri, tetapi test membuktikan kirimannya ditahan samaran.

## Di luar cakupan

Membuka samaran identitas.

## Data / bukti pendukung

Pertanyaan prod tak terjawab: lihat ADR 0173 § Context.

## Prasyarat

1/7 merged.

---

### 5/7 [BE] Pasang eksekutor kueri: area finance, procurement, gudang, manufaktur

- **Repo**: bip-erp (sub-issue induk)
- **Issue**: [bip-erp#3028](https://github.com/bip-itteam-internal/bip-erp/issues/3028)

**Pemutus:** @irfanarfianto
**PIC:** @

## Masalah

Pertanyaan operasional (mis. estimasi kedatangan supplier) tak terjawab di prod.

## Keputusan

ADR 0173 §2-§4, §8. Layak `Siap Agent` sesudah ADR itu Diterima. Service: `finance`, `procurement`, `warehouse`, `manufacture`, `inventory`.

## Yang harus benar

- [ ] Tiap service memasang eksekutor dengan daftar koleksinya. Gerbang modul pemilik (mis. `RequireFinanceBaca`) tetap berlaku.
- [ ] Cakupan per koleksi atau, bila tak ada dimensi departemen, hanya kelompok lihat semua.
- [ ] `procurement`: token OAuth Accurate yang dibacanya dari `integration_db` tidak terjangkau.
- [ ] Kamus kolom per service.

## Di luar cakupan

Area lain.

## Data / bukti pendukung

Pertanyaan prod "estimasi kedatangan supplier" (2026-10-02) dijawab "belum tersedia".

## Prasyarat

1/7 merged.

---

### 6/7 [BE] Pasang eksekutor kueri: tiket, form, kalender, notifikasi

- **Repo**: bip-erp (sub-issue induk)
- **Issue**: [bip-erp#3029](https://github.com/bip-itteam-internal/bip-erp/issues/3029)

**Pemutus:** @irfanarfianto
**PIC:** @

## Masalah

Modul pendukung belum bisa dikueri.

## Keputusan

ADR 0173 §2-§4, §8. Layak `Siap Agent` sesudah ADR itu Diterima. Service: `task-management`, `form-builder`, `calendar`, `notification`.

## Yang harus benar

- [ ] Tiap service memasang eksekutor dengan daftar koleksinya.
- [ ] `calendar`: agenda pribadi orang lain tidak keluar bagi pemakai di luar kelompok lihat semua (prinsip tiga lapis kalender).
- [ ] `notification`: isi notifikasi milik orang lain hanya untuk kelompok lihat semua.
- [ ] Kamus kolom per service.

## Di luar cakupan

Area lain.

## Data / bukti pendukung

Tidak perlu data prod.

## Prasyarat

1/7 merged.

---

### 7/7 [FE] Label eksploratif, teks kueri, dan tombol verifikasi di layar Copilot

- **Repo**: erp-frontend (sub-issue induk)
- **Issue**: [erp-frontend#2366](https://github.com/bip-itteam-internal/erp-frontend/issues/2366)

**Pemutus:** @irfanarfianto
**PIC:** @

## Masalah

Kode penanda baru tampil sebagai label umum (`src/features/copilot/lib/penanda.ts:7-9`). Pembaca tak tahu angkanya eksploratif, dan IT tak punya cara menandai kueri terverifikasi.

## Keputusan

ADR 0173 §8, §9. Layak `Siap Agent` sesudah ADR itu Diterima.

## Yang harus benar

- [ ] `kueri_eksploratif` dan `kueri_terverifikasi` terdaftar di `KODE_PENANDA_DATA`, dengan label di `copilot.penanda.*` **kedua** locale.
- [ ] Teks pipeline tampil terlipat dan bisa dibuka. Di PDF dan Excel, label + `tujuan` tercetak (lewat fungsi `teksPenanda`).
- [ ] Tombol "Tandai terverifikasi" / "Cabut" hanya tampil untuk anggota IT, memanggil endpoint 2/7, dan memberi umpan balik sukses atau gagal.
- [ ] Test: label kedua bahasa dengan instance i18next asli (kontrol negatif `en` bukan fallback `id`), dan tombol tak tampil untuk non-IT.
- [ ] `pnpm tsc --noEmit`, `pnpm lint`, `pnpm build` lolos; `pnpm test` dibanding baseline `origin/main`.

## Di luar cakupan

Perubahan backend dan komponen shared baru.

## Data / bukti pendukung

Tidak perlu data prod.

## Prasyarat

Deploy sesudah `bip-erp` 2/7 naik (BE sebelum FE).
