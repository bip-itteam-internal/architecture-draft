# ADR - 0143 Backlog Pindah dari Linear ke GitHub Project

> **Status**: 🟢 **Diterima**, 2026-09-29, **sedang diterapkan**: Project dan agent-kit 1.33.0 selesai; migrasi 245 issue berjalan sejak 2026-09-29 (status migrasi diukur di Project, bukan dicatat di sini). Diputuskan user (Tech Development). Linear `BHA` dibekukan jadi arsip baca. Nomor 0143 diklaim saat push; bila sudah terpakai, geser ke nomor bebas berikutnya.

%% Status di blockquote atas supaya terbaca VAULT-INDEX.json (15 baris pertama). %%

%% Vault ini PUBLIK. Tak ada kredensial, rincian celah, atau data pribadi di dok ini. %%

## Untuk Manajemen

**Masalahnya.** Backlog tim di Linear paket Free **berhenti menerima issue di 250**, dan sudah terisi 245. Selain itu hanya 3 dari 10 anggota tim yang punya akun Linear, sehingga penanggung jawab tiap pekerjaan ditulis sebagai teks, bukan penugasan sungguhan.

**Yang diputuskan.** Backlog pindah ke **GitHub Project** milik organisasi, tempat seluruh developer sudah bekerja setiap hari. Tak ada batas jumlah issue, tak ada biaya tambahan, dan penanggung jawab menjadi penugasan sungguhan. Aturan status yang sudah disepakati tetap sama: kode yang sudah digabung **belum** dianggap selesai sampai terbukti dipakai.

**Yang tidak berubah.** Linear tetap bisa dibuka sebagai arsip; tiap pekerjaan lama punya padanan di GitHub dengan nomor lamanya tercantum.

## Deskripsi

*Memindahkan backlog tim dari Linear (`bharata-erp`, tim `BHA`) ke GitHub Project #15 org `bip-itteam-internal`, mempertahankan definisi status "Menunggu Adopsi" dan "merge bukan Done", dan mengganti mekanisme penyambung PR ke issue dari nama branch `bha-<n>` menjadi kata kunci `Closes` di badan PR.*

- **Tanggal**: 2026-09-29
- **Hubungan**: aturan lengkap untuk developer dan agent di `.agent-kit/rules/team-memory.md` § Backlog: GitHub Project (satu sumber; dok ini tidak menyalinnya). Perubahan agent-kit di changelog 1.33.0.

## Context

- **Batas paket.** Linear Free: 250 issue, terisi 245 per 2026-09-29 (106 di antaranya Done). Arsip otomatis tim berjalan 6 bulan sesudah selesai, jadi tak membebaskan slot dalam waktu dekat. Paket berbayar Basic: $10 per anggota per bulan.
- **Keanggotaan.** Linear 3 anggota, org GitHub 10 anggota; PIC ditulis di deskripsi (`**PIC:** ...`) di 207 dari 245 issue.
- **Penyambung PR yang tak dipakai.** Linear menyambungkan PR lewat `bha-<n>` di nama branch/judul; diukur 2026-09-29 hanya 22 dari 100 PR bip-erp dan 14 dari 100 PR erp-frontend yang memuatnya, dan 82 dari 105 issue Done tak punya PR tertaut.
- **GitHub Project** tingkat org: tanpa batas praktis (50.000 item per project), gratis di paket org Free, menampung issue dan PR dari banyak repo, mendukung field kustom dan sub-issue lintas repo.

## Decision

1. **Wadah**: GitHub Project #15 "ERP Bharata - Backlog" (privat), field Status (Backlog, Todo, In Progress, In Review, Menunggu Adopsi, Done, Canceled), Area (7 area sesuai project Linear), Prioritas, Jenis, Linear ID, Target, Bukti Adopsi. Repo kode ERP aktif ditautkan; repo vault `architecture-draft` **tidak**, karena publik.
2. **Status tetap bermakna keadaan ERP**; field Status, bukan issue open/closed, yang menentukan selesai. Merge menutup issue dan workflow *Item closed* memindahkannya ke Menunggu Adopsi. Done hanya diisi manusia dengan Bukti Adopsi.
3. **Penyambung**: `Closes bip-itteam-internal/<repo>#<n>` di badan PR. Nama branch `<domain>/<n>-<slug>` hanya untuk keterbacaan.
4. **Satu issue satu repo**; pekerjaan lintas repo memakai issue induk + sub-issue per repo.
5. **Migrasi**: seluruh 245 issue (termasuk Done), dipecah otomatis ke repo kode yang paling banyak disebut isinya; judul berakhiran `[BHA-<n>]`, badan memuat tautan Linear, komentar, dan lampiran; PIC menjadi assignee.
6. **Linear dibekukan** sebagai arsip baca; `/linear-cek` usang.

## Konsekuensi

- Rujukan `BHA-<n>` di vault, ADR, dan brief lama tetap sah dan diterjemahkan lewat `gh search issues "BHA-<n>"`.
- Pemecahan repo otomatis bisa salah tempat untuk issue lintas repo; memindahkan issue antar-repo di GitHub (`gh issue transfer`) mempertahankan isinya.
- Workflow bawaan project (Item closed, Auto-add) diatur lewat web, bukan API, sehingga tak bisa diuji otomatis; perilakunya perlu dicoba sekali dengan issue uji.
- Laporan mingguan pengganti `/linear-cek` belum ada (TBD).
