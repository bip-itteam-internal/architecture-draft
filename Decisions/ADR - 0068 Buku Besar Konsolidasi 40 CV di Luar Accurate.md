## ADR 0068 — Buku besar konsolidasi 40 CV yang berjalan di luar Accurate

- **Status**: 🟡 **Proposed** — keberadaan sistemnya **fakta**, arahnya **belum diputuskan**. Keputusan ada di SPV FAT + IT, bukan di dokumen ini.
- **Tanggal**: 2026-08-31 (sistemnya sendiri berjalan sejak 2026-08-05)
- **Konteks dok**: [[APP - Buku Besar Konsolidasi CV FINCON]] · [[ADR - 0001 Akuntansi via Accurate]] · [[Finance - Big Pictures]]

## Context

[[ADR - 0001 Akuntansi via Accurate]] menetapkan bahwa ERP internal **tidak membangun akuntansi double-entry / general ledger sendiri**: COA, jurnal, buku besar, neraca, dan laba rugi adalah domain Accurate, dan bip-erp hanya menjembatani data ke sana. Keputusan itu masih `Accepted` dan masih tercermin di kode: seluruh angka akuntansi yang dipakai dashboard FAT dan sumber KPI dibaca lewat `/accounting/*` di [[Microservices - Integration Service]], dan tak ada satu pun jalur yang menulis balik ke Accurate.

Sejak **5 Agustus 2026** berjalan sebuah aplikasi yang melakukan persis apa yang dikecualikan ADR itu: [[APP - Buku Besar Konsolidasi CV FINCON]] — bagan akun sendiri (68 akun), jurnal sendiri (kas/piutang/utang/umum/penyesuaian), buku besar, neraca, laba rugi, arus kas, perubahan ekuitas, dan register aset tetap beserta penyusutannya — untuk **40 CV** grup.

Yang membuat ini bukan sekadar alat bantu pribadi:

- **Entitasnya sama.** `CV Pure Glow Lux` adalah badan usaha default [[Microservices - Payroll Service]]; `CV Global Estetika Gemilang` sudah jadi rekening bank Accurate `129903`; `CV Glow Skin Radiant` dan `CV Radiant Fresh X` sudah jadi proyek Accurate 2354 & 2552; `payroll_company` prod berisi 41 dokumen = 1 PT + 40 CV. Daftar 40 CV di aplikasi ini bukan daftar baru.
- **Angkanya bersaing dengan angka yang sudah dipakai menilai orang.** Laba rugi Accurate lewat `/accounting/profit-loss` sudah memasok sumber KPI `admin-nonops` dan mengisi kartu Tax & SPV FAT. Kini ada laba rugi kedua per CV, dari pembukuan lain, tanpa rekonsiliasi.
- **Sistemnya menutup satu celah yang memang nyata.** ERP maupun jalur Accurate yang terdokumentasi **tidak punya** kertas kerja konsolidasi 40 kolom dengan jurnal eliminasi intercompany. Ini bukan duplikasi; ini yang tak dimiliki siapa pun.
- **Ada metrik KPI yang justru menunggu keluarannya.** Templat `KPI Accounting CV` di [[HRIS - Matriks KPI per Departemen]] memuat baris berbobot **0,30** — laporan keuangan akurat maks tanggal 4 bulan berikutnya — berstatus *"Belum dipetakan"*. Laporan itu diproduksi di aplikasi ini.
- **Tata kelolanya di luar pagar.** Repo berada di akun GitHub **pribadi** di luar org `bip-itteam-internal`, satu kontributor, tanpa PR, tanpa test, database Supabase di luar infrastruktur ERP, dan otorisasinya (siapa boleh menyentuh CV mana) hanya ditegakkan di sisi peramban.

Membiarkan keadaan ini tanpa keputusan berarti ADR 0001 tetap tertulis `Accepted` sementara kenyataannya sudah tidak lagi begitu — dan aturan yang diketahui meleset akan diabaikan seluruhnya, termasuk bagiannya yang benar.

## Decision

**Belum diputuskan.** Yang bisa ditetapkan hari ini hanyalah bahwa keadaannya **harus** diputuskan, dan pilihannya ada tiga:

**A. Kukuhkan ADR 0001 — pembukuan tetap satu, di Accurate.** Konsolidasi & eliminasi dibangun sebagai fitur di atas data Accurate (lewat `/accounting/journals` yang sudah ada), aplikasi ini dipensiunkan setelah fitur penggantinya jalan.
*Untung*: satu buku besar, satu angka laba. *Rugi*: kertas kerja konsolidasi harus dibangun dari nol, dan pekerjaan yang hari ini sudah jalan berhenti dulu.

**B. Amandemen ADR 0001 — akui pengecualian konsolidasi.** Accurate tetap sumber kebenaran per-entitas; aplikasi ini **berhenti membukukan sendiri** dan berubah jadi lapisan konsolidasi yang **menarik** saldo per CV dari Accurate, lalu hanya memiliki jurnal eliminasi (satu-satunya data yang benar-benar miliknya).
*Untung*: celah asli tetap tertutup tanpa buku besar kedua. *Rugi*: menuntut pemetaan COA aplikasi ↔ COA Accurate, dan aplikasi ini harus masuk ke dalam pagar ERP lebih dulu.

**C. Akui sebagai sistem terpisah yang sah, dan pagari.** Pembukuannya sendiri diterima sebagai sumber kebenaran untuk lapisan CV, tetapi wajib dipindahkan ke org, ber-SSO, ber-RBAC, ber-RLS, ber-test, dan **wajib punya rekonsiliasi berkala terhadap Accurate**.
*Untung*: paling sedikit mengganggu pekerjaan yang sedang berjalan. *Rugi*: menerima dua buku besar secara permanen — dan tanpa rekonsiliasi yang benar-benar dijalankan, ini pilihan terburuk dari ketiganya.

**Yang tidak boleh terjadi apa pun pilihannya**: keadaan sekarang dibiarkan berjalan tanpa dipilih. Dua laba rugi tanpa rekonsiliasi tidak gagal dengan galat, melainkan dengan dua angka yang sama-sama masuk akal.

## Consequences

- ➕ Keberadaan sistemnya berhenti tak terlihat: apa pun keputusannya, ia sudah tercatat, terhubung ke dok Finance, dan bisa ditemukan lewat indeks vault.
- ➕ Pilihan B dan C sama-sama membuka jalan bagi metrik `KPI Accounting CV` berbobot 0,30 yang hari ini "belum dipetakan".
- ➖ Selama belum diputuskan, setiap laporan laba per CV punya dua sumber yang sah-sah saja dan tak ada yang bertanggung jawab menyamakannya.
- ⚠️ Temuan teknisnya (kredensial di bundel klien, otorisasi hanya di klien, RLS tak diketahui, impor yang menghapus lintas-perusahaan, salah golong arus kas) **berlaku hari ini**, tak menunggu keputusan arah. Daftar lengkap + rujukan barisnya ada di § *Belum Diimplementasikan / Catatan* pada [[APP - Buku Besar Konsolidasi CV FINCON]].
- ⚠️ Bila pilihan A diambil, [[ADR - 0001 Akuntansi via Accurate]] tetap berlaku apa adanya. Bila B atau C, ADR itu **wajib** diberi amandemen atau di-supersede — jangan tinggalkan dua ADR yang saling bertentangan.

## Dokumen Terkait

- [[APP - Buku Besar Konsolidasi CV FINCON]] · [[ADR - 0001 Akuntansi via Accurate]] · [[External - Accurate]]
- [[Finance - Big Pictures]] · [[Finance - Rancangan Finance Service]] · [[Finance - Dashboard per Posisi (FAT)]]
- [[API - Integration Service]] · [[Microservices - Integration Service]] · [[Microservices - Payroll Service]] · [[HRIS - Matriks KPI per Departemen]]
