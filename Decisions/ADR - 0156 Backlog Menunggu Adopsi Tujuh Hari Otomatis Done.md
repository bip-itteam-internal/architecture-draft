# ADR - 0156 Backlog Menunggu Adopsi Tujuh Hari Otomatis Done

> **Status**: 🟢 **Diterima**, 2026-10-08, oleh irfanarfianto (Tech Development, pemilik board). **Belum berjalan**: otomasinya di bip-erp#2786 menunggu merge dan secret token (status diukur di Project #15, bukan dicatat di sini). Mengubah butir 2 [[ADR - 0143 Backlog Pindah dari Linear ke GitHub Project]]. Nomor 0156 diklaim saat push; bila sudah terpakai, geser ke nomor bebas berikutnya.

%% Status di blockquote atas supaya terbaca VAULT-INDEX.json (15 baris pertama). %%

%% Vault ini PUBLIK. Tak ada kredensial, rincian celah, atau data pribadi di dok ini. %%

## Untuk Manajemen

**Masalahnya.** Pekerjaan yang kodenya sudah digabung ditaruh di kolom "Menunggu Adopsi" sampai ada orang yang membuktikan fiturnya dipakai. Bukti itu tidak pernah diisi: dari 578 kartu, **230 menumpuk di kolom itu dan tak satu pun punya bukti**. Papan tidak lagi menunjukkan apa yang benar-benar masih ditunggu.

**Yang diputuskan.** Kartu yang sudah **tujuh hari** di "Menunggu Adopsi" dipindahkan otomatis ke "Done", dengan catatan bahwa ia selesai otomatis, bukan dibuktikan orang.

**Yang berubah maknanya.** "Done" tidak lagi selalu berarti "terbukti dipakai". Ia berarti salah satu dari dua: dibuktikan orang, atau sudah seminggu digabung tanpa ada yang membukanya kembali. Keduanya bisa dibedakan dari isi kolom Bukti Adopsi.

## Deskripsi

*Menambah jalur otomatis dari status Menunggu Adopsi ke Done di GitHub Project #15 berdasarkan lama kartu berada di status itu, dijalankan GitHub Actions terjadwal, dengan penanda di field Bukti Adopsi.*

- **Tanggal**: 2026-10-08
- **Hubungan**: mengubah butir 2 [[ADR - 0143 Backlog Pindah dari Linear ke GitHub Project]] ("Done hanya diisi manusia dengan Bukti Adopsi"). Aturan untuk developer dan agent tetap satu sumber di `.agent-kit/rules/team-memory.md` § Backlog: GitHub Project. Otomasi: `bip-erp` `scripts/board/adopsi_otomatis.py` + `.github/workflows/board-adopsi-otomatis.yml` (issue bip-erp#2786).

## Context

- **Diukur 2026-10-08** di Project #15: 578 kartu, 230 berstatus Menunggu Adopsi, **0** berisi Bukti Adopsi. Board berumur sembilan hari.
- Status Menunggu Adopsi dibuat karena "kode selesai" dan "dipakai" pemiliknya berbeda (audit Linear 2026-09-29: status meleset ke dua arah). Pemisahan itu benar, tetapi langkah terakhirnya menuntut pekerjaan manual per kartu yang tidak dikerjakan siapa pun.
- Contoh pemicu: kartu Kalender perusahaan. Fiturnya hidup di prod, pemakaiannya rendah (1 agenda, 0 templat kewajiban), tak ada pekerjaan kode tersisa, dan kartunya tetap tampil sebagai pekerjaan berjalan.
- Workflow bawaan GitHub Project hanya bereaksi pada kejadian (item ditambah, ditutup, PR digabung); tak ada pemicu berbasis waktu. Project mencatat kapan nilai field Status terakhir diubah, jadi lama di sebuah status bisa dihitung tepat.

## Decision

1. Kartu berstatus **Menunggu Adopsi** yang field Status-nya terakhir diubah **tujuh hari atau lebih** lalu dipindahkan otomatis ke **Done**.
2. Hanya kartu yang isinya issue dan issue-nya **tertutup**. Dilewati: issue masih terbuka (induk yang anaknya belum selesai, issue MyBharata yang belum ditutup manual), issue ditutup *not planned* (seharusnya Canceled), dan kartu yang bukan issue.
3. Field **Bukti Adopsi** yang kosong diisi `otomatis: 7 hari di Menunggu Adopsi (<tanggal>)` **sebelum** status diubah. Yang sudah terisi tidak ditimpa.
4. Dijalankan **GitHub Actions terjadwal harian** di `bip-erp`, bisa dipicu manual dengan mode dry-run. Token dari secret repo ber-scope `project`, dipasang owner org.
5. Manusia tetap boleh memindahkan ke Done lebih cepat dengan mengisi Bukti Adopsi sendiri, dan boleh mengembalikan kartu Done ke status lain bila fiturnya ternyata tak terpakai atau bermasalah.
6. Larangan lama untuk agent dipersempit: agent tetap tidak memindahkan kartu ke Done **secara manual**; yang memindahkan adalah otomasi ini menurut aturan di atas.

## Konsekuensi

- **Done kehilangan sebagian maknanya.** Laporan yang ingin menghitung "fitur terbukti dipakai" wajib menyaring Bukti Adopsi yang **tidak** berawalan `otomatis:`. Menghitung seluruh Done sebagai adopsi akan melebih-lebihkan.
- Pelajaran audit Linear ("merge bukan Done": fitur lengkap di prod dengan nol pemakaian) tidak lagi dijaga oleh kolom status. Ia bergeser ke penanda di Bukti Adopsi, yang hanya berguna bila ada yang membacanya.
- Kartu yang kodenya digabung tetapi **belum di-deploy ke prod** juga akan menjadi Done sesudah tujuh hari; otomasi tidak tahu keadaan deploy.
- Otomasi bergantung pada satu token. Bila token kedaluwarsa, kartu kembali menumpuk tanpa galat di board; run Actions yang gagal adalah satu-satunya tanda.
- Mengganti nama kolom atau field di board (Status, Menunggu Adopsi, Done, Bukti Adopsi) membuat otomasi berhenti dengan pesan, karena id dibaca lewat nama.
