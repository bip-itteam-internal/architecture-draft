# ADR - 0151 Issue Siap Dikerjakan Agent Bila Keputusannya Bisa Ditunjuk, Ditandai Manusia

> **Status**: 🟡 **Diusulkan**, 2026-10-02, diajukan user (Tech Development). Menunggu persetujuan IT lead / pemilik runner; begitu disetujui, ubah baris ini jadi `🟢 Diterima, <tanggal>, oleh <login>` (butir 3 di bawah berlaku juga untuk ADR ini). Runner backlog **belum** memakai aturan ini; skripnya hanya ada di PC IT. Nomor 0151 diklaim saat push; bila sudah terpakai, geser ke nomor bebas berikutnya.

%% Status di blockquote atas supaya terbaca VAULT-INDEX.json (15 baris pertama). %%

%% Vault ini PUBLIK. Tak ada kredensial, rincian celah, atau data pribadi di dok ini. %%

## Untuk Manajemen

**Masalahnya.** Agent backlog otonom sudah berjalan sejak 29 September, tetapi hampir semua issue yang ia buka ternyata belum bisa dikerjakan: dari 52 issue yang ia sentuh, hanya 4 yang menjadi PR, sementara 46 berhenti di pertanyaan "keputusannya apa?". Issue di backlog kebanyakan berbunyi "ini perlu ada", sedangkan bentuknya (siapa penerima pengingat, ambang berapa, dipecah atau tidak) belum pernah diputuskan siapa pun.

**Yang diputuskan.** Agent hanya mengambil issue yang sudah **ditandai siap oleh manusia**. Sebuah issue disebut siap bila keputusannya sudah tertulis dan bisa ditunjuk, ukurannya satu PR, dan nama pemutusnya tercantum. Pertanyaan yang belum terjawab dikirim ke pemutusnya langsung, tidak lagi disiarkan ke seluruh grup.

**Yang tidak berubah.** Jumlah keputusan yang harus diambil manajemen tetap sama. Bedanya, keputusan itu ditanyakan saat issue ditulis, bukan sesudah agent menghabiskan satu putaran untuk menemukannya.

## Deskripsi

*Menetapkan Definition of Ready (DoR) untuk issue di GitHub Project #15 sebagai gerbang masuk runner backlog: label `Siap Agent` dipasang manusia setelah checklist DoR terpenuhi, persetujuan ADR dicatat di baris status ADR, dan antrean ulang dipicu pelepasan label `Butuh Info`, bukan komentar apa pun.*

- **Tanggal**: 2026-10-02
- **Hubungan**: memperluas [[ADR - 0143 Backlog Pindah dari Linear ke GitHub Project]]. Checklist DoR lengkap ada di `.agent-kit/rules/team-memory.md` § Backlog (satu sumber; dok ini dan template issue tidak menyalin isinya). Runner: [[RUN - Agent Backlog Otonom]].

## Context

- **Hasil runner**, dihitung dari [[LOG - Agent Backlog Otonom 2026-09]] dan [[LOG - Agent Backlog Otonom 2026-10]] per 2026-10-02: 52 baris issue, **4 PR**, **46 Butuh Info**, 2 gagal karena toolchain. Pada 2026-10-02 ada 51 issue terbuka berlabel `Butuh Info` (30 di `bip-erp`, 21 di `erp-frontend`), dan runner berhenti empat putaran berturut-turut tanpa PR.
- **Kriteria kandidat runner saat ini** (RUN, langkah 3): Backlog/Todo, Prioritas Low atau Medium, bukan Jenis Keputusan, tanpa label `Butuh Info`. Artinya setiap issue dianggap siap sampai terbukti tidak; pembuktiannya memakan satu putaran agent per issue.
- **Pola pertanyaan yang diajukan runner** (dikelompokkan dari ringkasan runner 2026-10-02):
  - keputusan bisnis yang belum ditulis di mana pun (penerima, ambang, kanal, cakupan): mayoritas;
  - "boleh dipecah?" karena isi issue melebihi satu PR, sementara PR agent wajib `Closes` issue-nya: 6 issue;
  - ADR yang mendasarinya masih berbunyi "Diusulkan", sehingga agent tak bisa tahu apakah sudah disetujui: 3 issue (ADR 0061, 0123, 0104);
  - butuh data produksi yang runner dilarang baca, atau tindakan tangan manusia (cek Seller Center, pindah Status).
- **Asal backlog**: sebagian besar issue lahir dari audit (padanan `BHA-<n>`) dan dari `/analisa-kebutuhan`. Keduanya mencatat **masalah**; keputusan bentuk solusinya tidak ikut tertulis.
- **Antrean ulang memicu putaran kosong**: runner mengambil ulang issue begitu ada komentar manusia. Komentar yang hanya menambah data (bukan keputusan) membuat runner membuka issue itu lagi lalu bertanya lagi.
- **Template issue**: `bip-erp` dan `erp-frontend` belum punya `.github/ISSUE_TEMPLATE` (diperiksa ke `origin/main` 2026-10-02).

## Decision

1. **Gerbang masuk runner = label `Siap Agent`.** Runner hanya mengambil issue Backlog/Todo berprioritas Low/Medium yang **berlabel `Siap Agent`** dan tanpa `Butuh Info`. Issue tanpa label itu tidak disentuh, sehingga runner tidak lagi menghabiskan putaran untuk menemukan bahwa sebuah issue sebenarnya keputusan.
2. **Label dipasang manusia** (pembuat issue atau pemutusnya) setelah checklist DoR terpenuhi. Inti checklist: keputusan bisa ditunjuk (ADR berstatus Diterima, ANALISA, atau bagian `## Keputusan` di badan issue); satu repo dan satu PR; kriteria selesai yang bisa diperiksa; data produksi yang dibutuhkan sudah ditempel; prasyarat sudah merged; **Pemutus** tertulis. Rincian di team-memory.
3. **Persetujuan ADR dicatat di baris status ADR itu sendiri**: `🟢 Diterima, <tanggal>, oleh <login atau jabatan>`. ADR yang masih "Diusulkan" tidak memenuhi DoR.
4. **Antrean ulang = pelepasan label `Butuh Info` oleh manusia**, bukan sembarang komentar. Yang menjawab memasang `Siap Agent` sekaligus bila checklist sudah terpenuhi.
5. **Pertanyaan diarahkan ke Pemutus.** Badan issue memuat `**Pemutus:** <login>` (orang yang berwenang memutuskan bentuk solusinya, bisa berbeda dari PIC yang mengerjakan). Komentar Butuh Info dari runner menyebut `@<Pemutus>`, dan ringkasan ke grup dikelompokkan per Pemutus.
6. **Template issue** di `bip-erp` dan `erp-frontend` memuat bagian-bagian DoR, supaya keputusan ditanyakan saat issue ditulis.
7. **Amandemen 2026-10-02 (pemecahan).** Syarat "satu repo, satu PR" sempat berbenturan dengan aturan [[ADR - 0143 Backlog Pindah dari Linear ke GitHub Project]] bahwa sub-issue tidak dipecah lagi (muncul di empat sub-issue sekaligus). Diputuskan IT lead: issue tingkat atas dipecah jadi issue **sejajar**; sub-issue yang kebesaran **diganti** sub-issue saudara di bawah induk yang sama, yang lama ditutup Canceled. Pemecahan dilakukan sesudah keputusannya ada. Rincian di team-memory.

## Konsekuensi

- Issue lama tidak otomatis siap. Backlog hari ini praktis kosong bagi runner sampai ada yang memberi label; ini sengaja, karena keadaan sebelumnya hanya terlihat sibuk.
- Hambatan sebenarnya, yaitu waktu para pemutus, tidak hilang. Ia sekadar menjadi terlihat per orang, bukan tersebar sebagai 51 pertanyaan tanpa pemilik. Sesi keputusan berkala per domain adalah cara yang wajar untuk mengurasnya, tetapi belum diputuskan (TBD).
- Label bisa dipasang terlalu cepat. Runner tetap menjalankan triase brief (`ragu` = berhenti), jadi label yang keliru berakhir di Butuh Info seperti sekarang, bukan di kode yang menebak.
- **Belum diterapkan di runner**: skrip runner hanya ada di PC IT dan belum masuk repo mana pun (RUN, catatan status). Butir 1, 4, dan 5 berlaku setelah skrip itu diperbarui di sana.
