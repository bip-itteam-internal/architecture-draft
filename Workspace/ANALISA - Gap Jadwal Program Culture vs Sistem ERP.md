---
publish: false
---
# ANALISA — Gap Jadwal Program Culture (Excel manual) vs Modul ERP

Hasil pembandingan `Jadwal_Program_Culture_Bharata_Club.xlsx` (alat kelola culture SEBELUM ERP) terhadap modul **Program Culture** yang sudah ada di ERP (2026-09-12). Papan kerja/temuan — bukan arsitektur, bukan keputusan. Belum lewat `/analisa-kebutuhan` penuh; tiap kandidat scope di bawah **masih menunggu keputusan pemilik produk** sebelum jadi ADR + task.

**Grounding**: `bip-erp/services/form-builder/{models_culture.go, culture_clubs.go, culture_metrics.go, culture_attendance.go, calendar_feed.go}`, `erp-frontend/src/app/(main)/hris/program-culture/*`. Konteks keputusan: [[ADR - 0066 Modul Kelola Program Culture]], [[ADR - 0084 Kehadiran Program Culture via Scan Menggantikan Feedback, plus Master Program]].

## Isi file Excel (3 sheet)

1. **Jadwal Program Culture** — 5 klub (Badminton, Football, Ladies Sport, Billiard, Music), masing-masing dengan **jadwal berulang tetap**: hari + jam, lokasi, frekuensi (mis. "4x/bulan"), **PIC** (1–2 orang).
2. **Kalender Bulanan** — **matriks distribusi sesi per-pekan** (Pekan 1–4: AKTIF/OFF), total sesi/bulan per klub, total klub aktif per pekan, keterangan (mis. Ladies "bergilir" Yoga→Aerobic→Gym pekan 1–3; Music hanya pekan 1 & 3).
3. **Rekap & Metrik** — frekuensi/bulan, **Dokumen Utama Verifikasi** per klub (Presensi & Nota Lapangan, Form RSVP, Logbook Meja & Turnamen, Dokumentasi), **Indikator Keberhasilan** kualitatif per klub, Status Program.

## Yang SUDAH ada di ERP (agar tak dibangun ulang)

Modul culture ERP sudah matang, beberapa hal melampaui Excel:

- **Klub** (Bharata Club Community): CRUD, logo, link grup WA, anggota, karyawan **join sendiri** (`culture_clubs.go`); anggota bahkan sudah di-seed dari xlsx roster.
- **Program** `jenis=club`: `lokasi`, **PIC (multi)**, `tanggal`, `jam_mulai`/`jam_selesai`, `pelaksanaan` (`models_culture.go`).
- **Absensi nyata via scan QR** + pencatatan manual officer (`culture_attendance.go`) — lebih kuat dari "Presensi" manual.
- **Rating kepuasan peserta** 1–5 → **skor KPI komposit otomatis 30/30/40** (`culture_metrics.go`).
- **Master program** + **feed kalender** personal ("Jadwal Saya" untuk anggota/PIC yang diundang, `calendar_feed.go` `cultureClubItems`).
- **MyBharata**: officer tampilkan QR, peserta scan + rating, pengingat rating persisten.

## Gap yang teridentifikasi

| # | Elemen Excel | Status ERP | Bukti / catatan |
|---|---|---|---|
| **A** | Jadwal **berulang** ("Setiap Selasa 16.00", "4x/bulan") | ❌ Tak ada mesin recurring | `CultureProgram` = event **satuan** per `tanggal`. `pelaksanaan` (harian/mingguan/…) hanya **label** yang disalin dari master, tak membangkitkan sesi (`models_culture.go:46-49`). Officer membuat tiap sesi manual. **Gap terbesar.** |
| **B** | Jadwal + lokasi + PIC melekat di **KLUB** (standing) | ⚠️ Sebagian | `CultureClub` tak menyimpan hari/jam/lokasi. Master program bawa default PIC/target, **bukan** jadwal hari-jam-lokasi tetap → diketik ulang tiap event. |
| **C** | **Matriks distribusi per-pekan** (Sheet 2) + rotasi "bergilir" | ❌ Tak ada | Feed kalender **personal**, invited-only (`cultureClubItems`). Tak ada grid perencanaan HR agregat "klub × pekan"; konsep rotasi mingguan dalam satu klub (Ladies Yoga/Aerobic/Gym) tak terwakili. |
| **D** | Target **frekuensi vs realisasi** (4x/bulan) | ❌ Tak ada | Tanpa baseline jadwal → tak ada metrik "direncanakan 4, terlaksana 3" per klub. |
| **E** | **Dokumen/bukti sesi** (Dokumentasi, Logbook, Nota Lapangan) | ❌ Tak ada | Grep backend culture: nol `foto/dokumentasi/nota/logbook`. Hanya scan + rating; tak ada unggah foto/logbook per sesi. |
| **F** | **RSVP** (Football "Form RSVP") | ❌ Tak ada — **SENGAJA** | [[ADR - 0084 Kehadiran Program Culture via Scan Menggantikan Feedback, plus Master Program]] & keputusan kalender: undangan **memberi tahu, bukan minta izin**. Bukan lupa. |
| **G** | **Biaya / Nota Lapangan** (venue eksternal berbayar) | ❌ Tak ada | Modul culture nol biaya/budget; tak tertaut Finance ([[Finance - Kas Kecil dan Pengajuan Budget]]). Spend per-klub tak terlacak. |
| **H** | Indikator keberhasilan **spesifik-klub / kualitatif** + kehadiran ≥80% per klub | ⚠️ Diseragamkan — **sebagian sengaja** | ERP pukul rata jadi komposit 30/30/40 yang dinilaikan ke **officer** (ADR 0066), bukan outcome kualitatif per klub ("repertoar lagu", "sportivitas", "wellness"). Target kehadiran ≥80% per klub tak muncul sebagai KPI klub. |

> Venue eksternal yang tersirat di Excel (butuh Nota Lapangan/biaya): Merpati 88 Futsal, Gold Studio, Powerzone Gym, YR12 Matuz Music Studio.

## Kandidat scope (menunggu keputusan pemilik produk)

Urutan by nilai. **Belum diputuskan**; bila disetujui → jadikan ADR + daftar task via `/analisa-kebutuhan`/`/plan`.

1. **Jadwal berulang per klub (A + B + D)** — nilai inti file Excel. Definisikan schedule standing di level klub (hari, jam, lokasi, PIC, frekuensi target) → bangkitkan sesi otomatis → sekaligus membuka metrik plan-vs-actual. ⚠️ Perlu putuskan: recurring digenerate jadi dokumen `CultureProgram` nyata (agar scan/rating jalan) vs. sekadar template tampilan.
2. **Matriks bulanan HR (C)** — view agregat "klub × pekan" untuk perencanaan, bukan hanya "Jadwal Saya" personal. Rotasi "bergilir" perlu model tersendiri bila mau dipertahankan.
3. **Dokumentasi & biaya sesi (E + G)** — unggah foto/nota per sesi + kaitkan spend venue ke Finance kas kecil.
4. **Indikator per-klub (H)** — hanya bila pemilik produk memang mau menilai kesehatan **klub** (kehadiran trend, ≥80%), berbeda dari KPI **officer** yang sudah ada. Bisa jadi cukup dashboard baca, bukan KPI baru.

## Sengaja JANGAN dikejar buta

- **F (RSVP)** — keputusan desain tercatat; menambahnya melawan ADR 0084.
- **H sebagian** — KPI officer-centric komposit adalah keputusan ADR 0066 (mengganti self-report). Jangan bongkar tanpa ADR baru.

## Dokumen Terkait

- [[ADR - 0066 Modul Kelola Program Culture]] — keputusan modul + skor komposit 30/30/40
- [[ADR - 0084 Kehadiran Program Culture via Scan Menggantikan Feedback, plus Master Program]] — scan kehadiran, master program, MyBharata
- [[ANALISA - Program Culture Scan Kehadiran & Master Program]] — daftar task turunan ADR 0084
- [[Microservices - Form Builder Service]] — rumah kode modul culture
- [[Finance - Kas Kecil dan Pengajuan Budget]] — kandidat integrasi biaya venue (gap G)
