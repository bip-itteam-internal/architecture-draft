## Deskripsi

*Desain **penyederhanaan pipeline Recruitment**: mengganti model dua-field `progress` (10 tahap "rekaman HRD") + `status` (keadaan) menjadi **satu field `status` berisi 6 nilai**, membuang tahap Technical Test / Background Check / Psikotes, dan menjadikan **jenis interview** sebagai **Interview Rounds** yang dikelola (katalog global + override per-lowongan). Hasil brainstorming 2026-07-18.*

- **Status**: 🟡 **Direncanakan (Design)** — belum ada kode; ini spec untuk implementasi.
- **Sisi implementasi**: [[Microservices - Recruitment Service]] (BE) + [[APP - Web ERP]] (FE erp-frontend). Endpoint → [[API - Recruitment Service]].
- **Pasangan konsep**: [[HRIS - Recruitment]] (⚠️ akan di-update saat implementasi — lihat Penyimpangan).

## Latar Belakang & Tujuan

- Pipeline saat ini punya **dua field** yang membingungkan pengguna: `progress` (10 tahap: CV Screening→HR/User/Final Interview→Technical Test→Background Check→Psikotes→Offering→Hired→Onboarding) dan `status` (In Progress/Scheduled/Pending/Hold/Withdrawn/Buffer). Terlalu granular untuk operasional HRD sehari-hari.
- **Tujuan**: satu funnel ringkas ala ATS standar + jenis interview yang bisa dikelola tanpa hardcode.

## Keputusan Desain (terkunci)

1. **Satu field `status`** (6 nilai): `New · Screening · Interview · Offer · Hired · Rejected`. Field `progress` lama & field `status`/keadaan lama **dihapus**.
2. **Transisi manual penuh** — HR ubah lewat dropdown inline; bebas ke status mana pun; **Rejected bisa dari mana saja**. Tanpa auto-transition & tanpa guardrail urutan.
3. **Buang tuntas** Technical Test, Background Check, Psikotes (koleksi/handler/route BE + komponen FE) + **migrasi data**.
4. **Interview Rounds** = **katalog global** + **override per-lowongan**. Menu **"Manage Interview Rounds"** ditaruh di **Recruitment → System Setup**.
5. **Screening = status saja** — tanpa record `screening_result`; alasan reject (opsional) ditaruh di **catatan kandidat**.
6. **Onboarding/masa-evaluasi tetap terpisah** (pasca-Hired, lewat Performance Review Onboarding) — bukan bagian 6 status.

## Model & Perubahan

### a. Status kandidat
- Enum baru `CandidateStatus { New, Screening, Interview, Offer, Hired, Rejected }`. `pipeline.go`: `validTransition()` disederhanakan (semua transisi manual diizinkan; Rejected dari mana saja). Field `progress` dihapus dari model `candidate`; kolom `status` lama dihapus/di-repurpose jadi satu field ini.
- **Migrasi data** (script/one-off saat deploy BE):

  | Lama (`progress`/`status`) | Baru (`status`) |
  |---|---|
  | `Applied` | **New** |
  | `CV Screening` | **Screening** |
  | `HR/User/Final Interview`, `Technical Test`, `Background Check`, `Psikotes` | **Interview** |
  | `Offering` | **Offer** |
  | `Hired`, `Onboarding` | **Hired** |
  | `Rejected`, `Withdrawn` | **Rejected** |

### b. Interview Rounds (global + override)
- **Katalog global** `interview_round`: `name`, `sequence`, `is_active`, **flag `sends_feedback_link`** (round mana yang memicu email link feedback ke pewawancara). CRUD di menu **Manage Interview Rounds** (System Setup).
- **Per-lowongan**: lowongan memilih rounds yang dipakai + urutan (aktif/nonaktif) — override atas katalog global.
- Sesi `interview` mereferensikan **`round_id`** (mengganti `stage` HR/User/Final hardcoded). Logika kirim link feedback ikut **flag round** (bukan lagi hardcoded User/Final).

### c. Pembuangan
- **BE** ([[Microservices - Recruitment Service]]): hapus koleksi/handler/route/model `technical_test_result`, `background_check`, `psychotest`, `psychotest_result`, `screening_result`. Enum `progress` & nilai `status` lama dibuang.
- **FE** ([[APP - Web ERP]]): hapus `stage-record-dialog` (bagian technical-test/psikotes/background-check/screening) + entri timeline terkait. **Timeline detail kandidat = hanya sesi interview.**

### d. Dampak yang ikut disesuaikan
- **Funnel dashboard** rekrutmen → 6 tahap (bukan 10).
- **Inline badge** status di tabel kandidat → 6 nilai.
- **Public tracking** (stepper yang dilihat pelamar di [[APP - Portal Karir Bharata]]) → ikut 6 (label curated/ramah).
- **Detail kandidat**: timeline hanya interview; hilangkan section tes/psikotes/bg-check.

## Slicing (PR bertahap; BE dulu baru FE)

1. **BE** — enum `status` 6-nilai + migrasi data + sederhanakan `validTransition`.
2. **BE** — hapus technical-test / background-check / psikotes / screening_result (koleksi/handler/route/model).
3. **BE** — Interview Rounds global + override per-lowongan + `round_id` di sesi + flag `sends_feedback_link`.
4. **FE** — status field + inline badge + funnel dashboard + public tracking.
5. **FE** — hapus stage-record detail + timeline (sisakan interview).
6. **FE** — menu **Manage Interview Rounds** (System Setup) + form jadwal interview pakai round.

## Penyimpangan dari arsitektur terdokumentasi (eksplisit)

Dok **[[HRIS - Recruitment]]** menyatakan pipeline `progress`/`status` mengikuti **"rekaman HRD saat ini"** (10 tahap detail, termasuk Technical Test/Background Check/Psikotes sebagai tahap resmi). Desain ini **sengaja menyimpang**: menyederhanakan ke 6 status & membuang tahap-tahap tersebut sebagai status. **Konsekuensi**: HRD kehilangan pelacakan granular tahap-tahap itu (keputusan disepakati user). Saat implementasi, **[[HRIS - Recruitment]]** & **[[Microservices - Recruitment Service]]** harus di-update (via `/sync-docs`), idealnya disertai **ADR** baru di `Decisions/` yang mencatat keputusan penyederhanaan ini.

## Belum Diputuskan / Catatan

- **Migrasi data lama**: dev berisi data test; script migrasi cukup one-off. Perlu konfirmasi apakah data produksi (bila ada) butuh penanganan khusus.
- **Feedback link per-round**: default flag `sends_feedback_link` untuk round mana (mis. hanya round belakang)? Ditetapkan saat isi katalog awal.
- Interaksi dengan **Glints stage mapping** (di [[HRIS - Recruitment]]) perlu dipetakan ulang ke 6 status.

## Dokumen Terkait

- [[HRIS - Recruitment]] · [[Microservices - Recruitment Service]] · [[API - Recruitment Service]]
- [[APP - Web ERP]] · [[APP - Portal Karir Bharata]]
