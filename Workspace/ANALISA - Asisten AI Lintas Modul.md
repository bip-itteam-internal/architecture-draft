# ANALISA - Asisten AI Lintas Modul

Daftar task hasil `/analisa-kebutuhan` (2026-09-28). Keputusan arsitekturnya ada di
[[ADR - 0132 Asisten AI Tanya-Jawab Lintas Modul, Lapisan Data Bisnis per Service Bukan Terpusat]]
dan [[Microservices - Assistant Service]] (dok domain, diperbarui mengikuti ADR ini). Baca
keduanya dulu sebelum `/start-task` tiap item — daftar ini papan kerja, bukan rencana per berkas.

Urutan di bawah wajib dijaga: T1-T3 fondasi (tanpa ini tidak ada yang bisa diuji), T4 gerbang
sebelum bangun apa pun per modul, T5-T8 satu modul dulu sampai terbukti sebelum modul kedua.

## Fondasi

- [ ] **T1 — Klien AI dasar.** Go + Anthropic SDK dengan Tool Runner. Tanpa retry/kuota/cache di
  awal (belum ada bahan ukur untuk merancangnya) — ukur nyata dulu di T12, baru putuskan perlu
  atau tidak. Ini pemakai PERTAMA klien AI di bip-erp mana pun; tidak ada yang bisa dipakai ulang.
- [ ] **T2 — Skeleton `services/assistant/`.** Ikuti pola `services/.template`. Orkestrator saja:
  tidak menyimpan data bisnis, tidak membaca database service lain. Rute lewat
  [[CORE - API Master Gateway]] seperti service lain.
- [ ] **T3 — Gate RBAC baru "Supervisor departemen mana pun ATAU Direktur ATAU IT".** Tulis satu
  fungsi baru (proksi `common.SupervisedDepartmentsStrict(c)) > 0`) dikomposisi lewat pola
  `validateRole(...)` OR yang sudah ada, bersama `common.IsITMember`/`IsITSupervisor` dan
  `common.SetaraDirektur`. **Wajib dapat keputusan eksplisit dari Direktur**: apakah Corporate
  Secretary ikut termasuk (default TIDAK sampai ditegaskan — [[ADR - 0132]] §3). Beri penanda
  `perm` di sidebar sejak commit pertama.

## Modul percontohan pertama

- [ ] **T4 — Pilih modul percontohan final + verifikasi gerbangnya.** Kandidat kuat: attendance,
  marketing-analytics (jebakan datanya sudah paling banyak terdokumentasi). Untuk tiap kandidat,
  cek endpoint yang akan diteruskan SUDAH bergerbang peran atau belum (lihat catatan
  `LOG - 2026-09-17 Audit Checklist Marketing dan Integration` soal Integration & sebagian
  marketing-analytics yang belum bergerbang). Endpoint yang belum bergerbang **wajib diperbaiki
  dulu** sebelum modul itu diikutkan ([[ADR - 0132]] §9) — ini prasyarat, bukan bagian pekerjaan
  fitur ini.
- [ ] **T5 — Endpoint baca baru ("Lapisan Data Bisnis") di modul percontohan pertama.** Ditulis
  pakai struct/fungsi bisnis yang SUDAH ADA di service itu — dilarang menulis ulang aturan kolom
  di tempat baru. Sertakan penanda umur/kesegaran data di responsnya (§4 ADR).
- [ ] **T6 — Tool + uji end-to-end tool tunggal.** Definisikan tool (skema `strict: true`) untuk
  endpoint T5. Uji panggilan lewat gateway `Reroute` (BUKAN `InternalRequest` — itu tidak
  meneruskan `BIP-Permissions`, lihat § Context ADR) pakai JWT akun uji sungguhan, bukan token
  admin. Buktikan jawaban "tidak tahu" muncul untuk pertanyaan di luar cakupan tool ini.

## Modul percontohan kedua + korelasi lintas modul

- [ ] **T7 — Ulangi T5-T6 untuk modul percontohan kedua.**
- [ ] **T8 — Uji korelasi lintas modul.** Satu pertanyaan yang butuh kedua modul (mis. gabungan
  fakta dari modul 1 dan modul 2 by `employee_id`/`shop_id` yang sama) → dua tool call dalam satu
  giliran, model menggabungkan angka yang SUDAH benar dari keduanya, bukan menghitung ulang. Ukur
  total waktu giliran ini vs batas gateway 30 detik ([[ADR - 0132]] §6) — dari angka nyata ini,
  tetapkan batas maksimal modul/tool-call per pertanyaan.

## Presentasi jawaban

- [ ] **T9 — Format keluaran terstruktur (teks/tabel/chart) + panel chat FE.** Chart WAJIB pakai
  `ChartContainer` + Recharts yang sudah baku di erp-frontend (palet `--fb-seri-*`,
  `connectNulls={false}`, dst) — dilarang membangun sistem chart baru.
- [ ] **T10 — Penanda tingkat keyakinan.** Jawaban yang sifatnya judgment/heuristik (bukan
  agregasi pasti) ditandai eksplisit "perlu diperiksa manusia" sebelum disajikan, bukan seolah
  fakta pasti.
- [ ] **T11 — File (Excel/PDF) hanya saat diminta eksplisit.** Jawaban default selalu di dalam
  chat; jangan generate file otomatis untuk tiap jawaban.

## Verifikasi & pengukuran

- [ ] **T12 — Ukur biaya AI per pertanyaan** pada minggu pertama pemakaian nyata (token masuk/keluar,
  model yang benar-benar menjawab), catat di [[Microservices - Assistant Service]].
- [ ] **T13 — Uji gate RBAC negatif dan positif.** Staff biasa ditolak; supervisor departemen mana
  pun (bukan cuma yang diuji manual) lolos; Direktur lolos; IT lolos; Corporate Secretary sesuai
  keputusan T3 (lolos atau ditolak, keduanya harus punya test yang menguncinya).

## Terkait

- [[ADR - 0132 Asisten AI Tanya-Jawab Lintas Modul, Lapisan Data Bisnis per Service Bukan Terpusat]]
- [[Microservices - Assistant Service]]
- [[REF - Kepemilikan Data]]
