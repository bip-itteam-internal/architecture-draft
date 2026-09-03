## Deskripsi

*Sistem audit internal General Affairs — audit kepatuhan terhadap standar & prosedur (K3, keamanan pangan, pemeliharaan). Item #17 pada [[GA - Big Pictures]].*

- **Status**: 🟡 Draft / Direncanakan
- ⚠️ **Rumahnya sudah diputuskan sebelum dok ini dikerjakan**: [[ADR - 0074 Audit Internal Dipisah jadi Service dan Aplikasi Sendiri]] menetapkan aplikasi audit internal yang terpisah sebagai wadah bagi SELURUH audit internal, dan kepatuhan GA direncanakan menyusul ke sana — bukan jadi modul GA tersendiri.

⛔ **DUA HAL BERBEDA SAMA-SAMA BERNAMA "AUDIT INTERNAL".** Yang ini audit **kepatuhan proses fisik** (K3, keamanan pangan, pemeliharaan); [[Finance - Audit Internal]] audit **pembukuan** (36 uji atas angka). Keduanya nyata dan keduanya perlu, tetapi nama yang sama tanpa pembeda sudah terbukti membingungkan permanen di [[APP - Dynamic Task Tracker]] — portal ticketing ERP dan aplikasi terpisah sama-sama bernama "Task Management", dan sampai hari ini orang harus bertanya yang mana. Penamaan final diputuskan di [[ANALISA - Audit Internal Terpisah]] T3.1.

⛔ **Register temuannya TERPISAH dari temuan pembukuan** (ADR 0074 §4), dan itu diputuskan sekarang justru supaya tidak perlu migrasi nanti. Alasannya bukan kerapian: koleksi bersama ber-diskriminator mencemari angka secara senyap — konsumen berikutnya yang lupa menyaring tidak menghasilkan galat melainkan angka yang masuk akal dan salah, dan temuan audit memberi makan metrik KPI. Penolakan yang sama sudah diambil [[ADR - 0073 Modul Audit Internal di finance-service dan Kertas Kerja yang Dipegang Sendiri]] §5 terhadap `quality_capa`.

⚠️ **Bentuk layarnya belum dirancang dan tidak boleh diasumsikan sama.** Registry audit pembukuan berbentuk pembanding dua sisi berangka; checklist kepatuhan berbentuk lain. Belum diperiksa apakah keduanya muat dalam satu bentuk.

## Ruang Lingkup

- Audit kepatuhan terhadap standar: **ISO 22000** (Food Safety Management System), **OHSAS**/K3, serta SOP internal GA
- Audit berbasis **checklist** per fungsi GA
- Pencatatan **temuan (findings)** + tindak lanjut (CAPA) + status

## Fitur / Proses yang Direncanakan

- Jadwal audit (periodik per area/fungsi)
- Checklist audit (template per standar/area) — terkait [[GA - Checklist Management]]
- Temuan → tindakan korektif/preventif → verifikasi penutupan
- Dashboard kepatuhan + riwayat audit

## Dependensi / Dokumen Terkait

- [[Finance - Audit Internal]] · [[APP - Audit Internal]] · [[ADR - 0074 Audit Internal Dipisah jadi Service dan Aplikasi Sendiri]]
- [[GA - Big Pictures]]
- [[GA - Checklist Management]] · [[GA - Risk Management]] · [[GA - Accident Prevention]]
- [[GA - Building Maintenance]] · [[GA - Machine & Utility Maintenance]] · [[GA - Waste Management]]
