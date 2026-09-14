---
publish: false
---
# ANALISA — Tipe Program Culture Non-Event + Jadwal di Master

Daftar task hasil `/analisa-kebutuhan` (2026-09-12). Keputusan: [[ADR - 0093 Tipe Program Culture Non-Event Dinilai Terlaksana dengan Approval SPV HR, plus Jadwal di Master]] (meng-amend [[ADR - 0084 Kehadiran Program Culture via Scan Menggantikan Feedback, plus Master Program]]). Papan kerja — berubah tiap item selesai; bukan arsitektur, bukan rencana per-berkas.

**Urutan wajib**: BE (form-builder) sebelum FE/mobile (perubahan kontrak). **Prod dijalankan MANUSIA.** KPI **tidak** didesain ulang (diatur SK) — non-event hanya menghasilkan komposit lewat jalur internal berbeda, bentuk `GET /internal/culture/metrics` **tetap**.

## Fase 0 — Prasyarat

- [ ] **T0. Ukur status prod modul culture (bukan asumsi).** ADR 0084 menyatakan modul belum prod; ADR 0093 mewarisi itu. Ukur: apakah `culture_programs`/`culture_attendance`/`culture_feedback` sudah ter-deploy & terisi di prod. Modul sudah **live di web ERP & MyBharata (mobile ter-commit)** — pastikan penambahan tipe non-event debut **satu paket**, jangan biarkan versi tanpa `tipe` live lalu ditambal. Baca boleh, tulis TIDAK.

## Fase 1 — Backend form-builder (`bip-erp/services/form-builder/`)

- [ ] **T1. Field `tipe` (event | non_event) di `CultureProgram` & `MasterCultureProgram`.** Default `event` (kompatibel mundur, tanpa migrasi nilai). Validasi daftar tertutup (pola `pelaksanaanSah`). `tipe` disalin master→program saat create (sejajar `nama`/`pilar`/`pelaksanaan`). Sumbu BEDA dari `jenis`/`pelaksanaan` — jangan disatukan. Dependensi: T0.
- [ ] **T2. Field jadwal di `MasterCultureProgram`.** Arti bergantung `pelaksanaan`: `mingguan`→hari-dalam-minggu, `bulanan`→tanggal-dalam-bulan, `harian`→tiap hari kerja, `tahunan`→tanggal spesifik. Hanya disimpan sebagai acuan; TIDAK membangkitkan sesi. Dependensi: T0.
- [ ] **T3. Create program bercabang non-event.** `tipe=non_event` → **lewati** `resolveTargetProgram`, **tidak** buat `scan_token`, `tanggal` **opsional**, tak terima kehadiran/feedback. `tipe=event` tetap seperti sekarang. Dependensi: T1.
- [ ] **T4. Tanda "terlaksana" + approval SPV HR.** Koleksi/rute baru: officer menandai terlaksana program non-event (bebas kapan saja, boleh >1×/periode, opsional catatan/bukti) → status **menunggu approval**; **SPV HR** (gerbang `requireCultureManager`, peran HR — BUKAN atasan `work_data`) approve/tolak. Reuse pola approval + notifikasi yang ada; jangan tulis resolver baru. Dependensi: T1.
- [ ] **T5. `hitungSkorProgram` cabang non-event.** `tipe=non_event` → komposit = **100** bila ada ≥1 tanda terlaksana **disetujui** dalam `period_key`, else **0**; masuk **array `komposit[]` yang sama**. Bobot 30/30/40 event & bentuk `GET /internal/culture/metrics` TAK berubah. Perbarui `culture_metrics_test.go` (fixture non-event; kunci: non-event tanpa approval = 0, dengan approval = 100). Dependensi: T3, T4.

## Fase 2 — Web ERP (`erp-frontend/src/app/(main)/hris/program-culture/*`)

- [ ] **T6. Master page: input `tipe` + jadwal.** `master/page.tsx` — dropdown tipe; input jadwal (hari/tanggal) tampil sesuai `pelaksanaan`. Tipe di `types/culture.ts` + `hooks/use-culture.ts`. i18n `id.ts`+`en.ts`. Dependensi: T1, T2.
- [ ] **T7. Kelola page: tipe + prefill tanggal dari jadwal master.** `kelola/page.tsx` — saat pilih master, pra-isi `tanggal`/jam dari jadwal (perluas `pickMaster`, tetap bisa disesuaikan). Non-event: `tanggal` tak wajib, sembunyikan pemilih target & UI hadir/target. Dependensi: T3, T6.
- [ ] **T8. Dashboard & detail: tampilan non-event.** `page.tsx`/`[id]/page.tsx` — untuk non-event sembunyikan partisipasi/antusiasme/hadir/rating; tampilkan status **terlaksana + approval**. Skor komposit tetap tampil (100/0). Dependensi: T5.
- [ ] **T9. UI approval SPV HR.** Daftar tanda terlaksana menunggu approve + aksi setujui/tolak (halaman/section, reuse pola tabel yang dipakai modul). Digerbang peran HR. Dependensi: T4.

## Fase 3 — MyBharata (`my-bharata/lib/src/features/program_culture/*`)

- [ ] **T10. Guard non-event.** Program `tipe=non_event` **tak** muncul sebagai bisa-di-scan (QR/scan) dan **tak** menagih rating (pengingat). Cek permukaan officer & peserta. Fitur culture sudah ada & ter-commit — ini penyesuaian, bukan scaffold baru. Dependensi: T1, T3.

## Fase 4 — Deploy & verifikasi

- [ ] **T11. Deploy BE→FE + verifikasi end-to-end.** Naikkan form-builder (bila approval pakai kategori inbox baru → notification-service **bersama**). Verifikasi lewat gateway: buat master non-event berjadwal → buat program (tanggal ter-prefill) → tandai terlaksana → SPV HR approve → `GET /internal/culture/metrics` memuat komposit 100 untuk program itu, bentuk payload **tetap**, KPI officer terhitung wajar; non-event TANPA approval = 0. **PROD: agent siapkan perintah, manusia jalankan.** Debut non-event satu paket dengan modul culture (T0).

## Cara Verifikasi (untuk gerbang `/wrap`)

- **Test murni**: `culture_metrics_test.go` mengunci non-event 0 (tanpa approval) vs 100 (disetujui); event tak berubah.
- **Lewat gateway (bukan hanya unit)**: satu perjalanan utuh sebagai orang — officer buat program non-event dari master berjadwal, tandai terlaksana, SPV HR setujui, cek skor naik; lalu cek non-event yang belum disetujui tetap 0.
- **Kontrak metrik**: bandingkan bentuk `GET /internal/culture/metrics` sebelum/sesudah — WAJIB identik (ADR 0032).
- **Mobile**: program non-event tak tampil bisa-di-scan / tak menagih rating.

## Catatan lingkup

- **KPI tak didesain ulang** (SK): tak ada sumber/metrik KPI baru; bobot 30/30/40 event tetap.
- **Bukan** cron/generator sesi — jadwal master hanya acuan pra-isi.
- **Anti-gaming**: program wajib dari master milik HR + approval SPV HR (dua lapis).
- Resolusi approver "SPV HR" = peran HR via `requireCultureManager`, bukan atasan `work_data` officer.
