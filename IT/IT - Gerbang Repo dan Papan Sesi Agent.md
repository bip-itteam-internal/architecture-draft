# IT - Gerbang Repo dan Papan Sesi Agent

## Deskripsi

*Dua perkakas kerja developer yang saling melengkapi: **gerbang lokal** yang bisa menolak commit atau push bila pemeriksaan dasarnya belum lolos, dan **papan sesi** yang menunjukkan sesi kerja mana sedang mengerjakan apa saat lebih dari empat sesi berjalan bersamaan. Keduanya hidup di mesin developer, tanpa layanan dan tanpa biaya berjalan. Keputusan yang melahirkannya beserta alasan menolak alternatifnya ada di [[ADR - 0077 Otonomi Merge Agent Digerbang Mekanisme yang Bisa Menolak]].*

- **Status**: 🟡 **Konsep**, 2026-09-06, kode belum ada. Berdiri di atas pengukuran langsung ke GitHub API, isi repo, dan isi agent-kit pada tanggal yang sama.

## Latar Belakang

Per 2026-09-06 tidak ada satu pun gerbang otomatis yang berjalan tanpa manusia di `erp-frontend` maupun `bip-erp`. Bukan lemah, melainkan nol:

- Seluruh workflow yang menggerbangi berstatus `disabled_manually`. Run terakhir `ci.yml` erp-frontend (2026-08-13) bahkan tidak sempat jalan karena kegagalan billing GitHub Actions.
- `pr-notification.yml` bip-erp tercatat `active` tetapi seluruh isinya dikomentari, sehingga tiap push memicu run gagal 0 detik yang tidak menggerbangi apa pun.
- `main` di kedua repo `protected: false`, dan rulesets ditolak 403 dengan tawaran upgrade paket.
- Nol hook git lokal aktif di kedua repo.

Di sisi agent-kit, kelima berkas `rules/` adalah prosa yang dibaca model, bukan skrip. Kedua hook yang terpasang selalu `exit 0`. Satu-satunya proses berexit-code di seluruh kit adalah `build-vault-index.py --check`, dan lingkupnya cuma kesegaran indeks dokumentasi.

Dua cacat kecil yang menjelaskan mengapa ini bisa bertahan lama tanpa terasa. Pertama, hook `PreToolUse` dipasang dengan matcher `Bash` sementara seluruh git di mesin dev Windows dijalankan lewat PowerShell, jadi pengingat pre-commit satu-satunya itu tidak pernah menyala di sana. Kedua, `tests/test-init.ps1` milik kit pernah merah beberapa rilis tanpa terdeteksi karena tidak ada CI yang menjalankannya.

Kebutuhan kedua datang dari pemilik proses: lebih dari empat sesi kerja berjalan bersamaan di satu mesin, dan jejaknya hilang.

## Ruang Lingkup / Cakupan (business view)

**Yang termasuk**

1. **Gerbang lapis satu, hook Claude Code.** Mengembalikan penolakan nyata alih-alih mencetak pengingat lalu lolos. Matcher mencakup PowerShell selain Bash.
2. **Gerbang lapis dua, `pre-push` git hook per repo.** Menjalankan pemeriksaan yang benar-benar bisa gagal: `tsc --noEmit`, `lint`, `build` untuk erp-frontend; `go build ./...` untuk bip-erp. Dipilih `pre-push` dan bukan `pre-commit` karena gerbang yang berbunyi tiap beberapa menit akan dimatikan orang dalam sepekan.
3. **Gerbang kit atas dirinya sendiri.** `tests/test-init.ps1` dan pytest `Tools/` ikut dijalankan.
4. **Papan sesi.** Tiap sesi menulis satu berkas status ke `.task-plans/` berisi branch, task, tahap flow, dan waktu sentuh terakhir, ditulis hook `SessionStart` yang sudah ada. Satu command membacanya jadi satu tabel.

**Yang sengaja TIDAK termasuk**

- Orkestrasi eksternal, agen penilai terpisah, supervisor yang memperbarui skill sendiri, dan dashboard web. Alasan penolakan per butir ada di ADR §6.
- Menghidupkan kembali GitHub Actions. Di luar mandat, alasan biaya dan paket akun.
- Memperbaiki review kode. Angka review 2,2% adalah masalah orang, bukan masalah alat.

## Cara Kerja

**Mengapa gerbangnya lokal.** Tiga batas mengunci pilihan ini dan ketiganya di luar mandat untuk diubah: Actions berbayar tidak boleh diandalkan, branch protection tidak tersedia pada paket akun sekarang, dan self-hosted runner lokasinya tidak diketahui ([[IT - CI-CD]]). Yang tersisa adalah mesin developer sendiri.

**Sebuah aturan baru dianggap gerbang hanya bila ada proses yang keluar dengan status bukan nol, atau hook yang mengembalikan penolakan eksplisit.** Kalimat perintah di dalam berkas prosa bukan gerbang. Konsekuensinya `wrap-completion-gate.md` dan `review-checklist.md` tetap dipakai dan tetap berharga, tetapi namanya turun kelas menjadi checklist.

**Distribusi hook adalah bagian tersulitnya, bukan isinya.** `.git/hooks/` tidak ikut ter-clone, jadi hook wajib disimpan sebagai berkas ter-commit di repo lalu diaktifkan lewat `git config core.hooksPath`, dan pengaktifannya wajib menjadi langkah `init`. Tanpa itu gerbangnya cuma hidup di mesin yang kebetulan memasangnya, dan itu mengulang persis pola disiplin-tanpa-penjaga yang sudah gagal 18 kali berturut-turut di repo `audit-bharata`.

**Papan sesi berupa berkas, bukan layanan**, supaya ia tidak ikut mati saat layanannya mati. Satu-satunya saat orang membutuhkan papan ini adalah saat keadaan sedang kacau.

## Persona / Pengguna

| Persona | Peran & Divisi | Akses / RBAC | Device |
|---|---|---|---|
| Developer | Tech Development | tidak lewat RBAC ERP, cukup akses repo | Workstation |
| Agent AI | dijalankan developer di workspace | mewarisi akses mesin yang menjalankannya | Workstation |

- **Tujuan**: menjalankan banyak sesi kerja tanpa kehilangan jejak, dan tidak mendorong perubahan yang belum lolos pemeriksaan dasar.
- **Pain point**: nol gerbang otomatis, sehingga kesalahan hanya ketahuan sesudah mendarat; dan empat sesi lebih berjalan bersamaan tanpa cara melihat keadaannya selain membuka satu per satu.
- **Aksi utama**: menjalankan flow wajib per task; gerbang menyala sendiri saat commit dan push; papan sesi dibaca lewat satu command.

Karyawan pengguna ERP **tidak** menjadi persona di sini. Perkakas ini tidak menyentuh satu pun layar ERP dan tidak memuat data karyawan.

## Konsumen Data

- [[DEVELOPER GUIDE]] — flow wajib per task yang digerbangi perkakas ini
- [[RUN - Onboarding Developer Baru]] — jalur pemasangan; pengaktifan `core.hooksPath` menjadi langkah di sini
- [[IT - Development Apps and Tools]] — daftar perkakas internal tim

## Kendala

- **Gerbang lokal bisa dilewati** dengan `--no-verify`. Diterima sadar: ia menahan kelalaian, bukan niat, dan kelalaian adalah yang benar-benar terjadi di sini.
- **Gerbang lokal tidak berlaku bagi yang belum memasangnya.** Inilah alasan `core.hooksPath` wajib jadi langkah `init`, bukan anjuran.
- **Branch protection tetap tidak ada**, jadi tidak ada apa pun di sisi GitHub yang menahan push langsung ke `main`.
- **`pnpm test` erp-frontend tidak pernah hijau penuh di `main`**, jadi test tidak bisa dipakai sebagai syarat lolos dalam bentuk mentah. Yang dipakai di gerbang push adalah `tsc`, `lint`, dan `build`; menambahkan test menuntut baseline pembanding lebih dulu.
- **Waktu tunggu push bertambah.** `build` erp-frontend tidak murah. Bila ternyata mengganggu, yang diturunkan adalah cakupannya, bukan sifat menolaknya.

## Batas dengan Papan Aktivitas Developer

[[IT - Papan Aktivitas Developer]] mencatat peristiwa GitHub yang **sudah terjadi** (push, PR, review) lewat webhook, di Cloudflare. Papan sesi mencatat pekerjaan yang **sedang berjalan dan belum menghasilkan peristiwa apa pun**.

Keduanya tidak bisa saling menggantikan, dan itu bukan soal selera: sesi yang macet tiga jam tanpa satu commit pun tidak akan pernah muncul di papan aktivitas, karena tidak ada webhook yang terbit. Menggabungkannya akan melahirkan satu papan yang benar untuk separuh pertanyaan dan diam untuk separuhnya lagi.

## Belum Diputuskan (TBD)

- Apakah papan sesi kelak perlu lintas-mesin. Sekarang dirancang untuk satu mesin, karena jumlah dev yang benar-benar memakai kit belum diukur.
- Apakah keluaran papan sesi layak disalurkan ke [[IT - Papan Aktivitas Developer]] sebagai sumber kedua, atau justru harus tetap terpisah agar tidak melahirkan dua angka yang menyimpang.
- Bentuk gerbang untuk repo selain `erp-frontend` dan `bip-erp`.
- Ekstraksi skill dari sesi manual. Bahan mentahnya sudah menumpuk (`erp/.agents/AGENTS.md`, 721 baris, 26 entri ber-`originSessionId`) dan cetakan pipeline-nya sudah terbukti di `Tools/`, tetapi urutannya sesudah gerbang dan papan sesi.

## Dokumen Terkait

- [[ADR - 0077 Otonomi Merge Agent Digerbang Mekanisme yang Bisa Menolak]] — keputusan dan alasannya
- [[IT - CI-CD]] — keadaan pipeline, jalur deploy produksi yang belum terverifikasi
- [[IT - Papan Aktivitas Developer]] — papan peristiwa GitHub, beda lingkup
- [[ADR - 0034 Papan Aktivitas Developer di Luar Arsitektur ERP]] — preseden perkakas developer di luar arsitektur ERP
- [[RUN - Onboarding Developer Baru]] — pemasangan kit
- [[DEVELOPER GUIDE]] — flow wajib per task
- [[IT - SOP Dokumentasi Vault]] — konvensi dokumentasi
