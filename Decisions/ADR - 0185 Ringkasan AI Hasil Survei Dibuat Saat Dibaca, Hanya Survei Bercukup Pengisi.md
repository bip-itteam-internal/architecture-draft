# ADR - 0185 Ringkasan AI Hasil Survei Dibuat Saat Dibaca, Hanya Survei Bercukup Pengisi

> **Status**: 🟢 **Diterima**, 2026-10-17, oleh user (Tech Development). Kode ✅ **merged dan live di prod 2026-10-17** (bip-erp [#3243](https://github.com/bip-itteam-internal/bip-erp/pull/3243), erp-frontend [#2550](https://github.com/bip-itteam-internal/erp-frontend/pull/2550)); diverifikasi di prod: biner dan bundel memuat fitur, satu ringkasan survei 160 jawaban berstatus `ready`, nama dan `employee_id` pengisi tak muncul di isinya. ⚠️ **Revisi tampilan** (§Revisi 2026-10-17) di branch `feat/form-builder-ringkasan-ai-ringkas`, belum merge.

%% Status di blockquote atas supaya terbaca VAULT-INDEX.json (15 baris pertama). Vault ini PUBLIK: tidak ada nama orang, kunci, atau isi jawaban survei. %%

## Untuk Manajemen

**Yang berubah di layar.** Halaman Analisa form survei di web ERP mendapat kartu **Ringkasan AI** di tab Ringkasan Eksekutif dan Ringkasan. Pengelola form menekan "Buat ringkasan dengan AI" sekali; sesudahnya ringkasan memperbarui diri saat halaman dibuka bila ada jawaban baru. Isinya empat bagian: tema utama, hal yang dinilai baik, keluhan, dan rekomendasi, masing-masing paling banyak tiga kalimat pendek.

**Yang tidak dijanjikan.** Ringkasan tidak memuat angka (angka tetap dari tab analisa), tidak tersedia untuk form penilaian karyawan, dan tidak dibuat untuk survei dengan kurang dari 5 pengisi. Teks ditulis AI dan wajib diperiksa sebelum dipakai sebagai dasar keputusan.

## Deskripsi

*Pemakai ketiga klien AI [[ADR - 0082 Integrasi AI lewat Klien Tipis di Shared-Library]]: ringkasan teks hasil survei, disimpan per form dan periode, dibuat ulang hanya saat ada jawaban baru DAN halaman dibuka, paling sering sekali per 10 menit. Masukan ke model tidak membawa identitas pengisi ([[ADR - 0142 Pengisi Penilaian dan Survei Selalu Anonim, IT Membuka Identitas lewat Jalur Audit Bercatatan]]).*

- **Tanggal**: 2026-10-17
- **Path di repo**: `bip-erp/services/form-builder/ai_summary.go` · `erp-frontend/src/features/form-builder/components/analytics/ringkasan-ai-card.tsx` · `.../hooks/use-ringkasan-ai.ts`
- **Rute**: `GET` dan `POST /forms/:id/ai-summary?period=` (grup `/forms`, `requireFormManager`), lihat [[API - Form Builder Service]]
- **Koleksi**: `form_ai_summaries`, indeks unik `(form_id, period_key)`

## Context

Halaman analisa sudah merekap angka per pertanyaan, tetapi jawaban teks bebas hanya tampil 5 cuplikan terbaru (`maxTextSamples`); sisanya harus dibaca satu per satu di tab Individu atau export CSV. Pengelola form meminta ringkasan otomatis yang ikut diperbarui saat pengisi bertambah.

Tiga batas yang sudah ada menentukan bentuknya:

- **Gateway memutus di 30 detik**, sedangkan panggilan model bisa sampai 60 detik (ADR 0082). Panggilan sinkron akan terbaca 502 di tombol.
- **Survei selalu anonim** (ADR 0142). Data jawaban di database tetap menyimpan identitas pengisi, jadi penyusun masukan harus menyaringnya secara eksplisit.
- **Tiap panggilan membawa ~2.000 token persona proxy** (ADR 0082). Membuat ulang di setiap jawaban masuk membayar ringkasan yang belum tentu dibaca siapa pun.

## Decision

1. **Hanya survei tanpa sasaran penilaian**: `form_type` `survey` atau kosong (dokumen lama), dan `subjectActive` mati. Form penilaian dikecualikan karena ringkasan per orang yang dinilai sensitif dan sudah dijawab tab "Yang Dinilai". Kartu tidak dirender sama sekali pada form tipe lain.
2. **Minimal 5 pengisi unik** (`minPengisiRingkasan`), dihitung dari `employee_id` berbeda pada cakupan periode yang dibaca. Ringkasan atas dua-tiga jawaban mudah ditebak penulisnya walau namanya tak disebut.
3. **Disimpan per (form, periode)**, mengikuti pemilih periode halaman analisa: periode kosong berarti seluruh periode, sama dengan `analyticsFilter`.
4. **Pemicu: tombol untuk ringkasan pertama, otomatis saat dibaca sesudahnya.** Ringkasan menyimpan `jumlah_jawaban` saat dibuat; bila jumlah sekarang lebih besar, ia **basi**. Kartu memicu `POST` sekali per pemuatan bila basi dan **jeda 10 menit** (`jedaPerbaruiRingkasan`) sejak pembuatan terakhir sudah lewat. Ringkasan yang gagal tidak memicu dirinya sendiri; ulangnya lewat tombol "Coba lagi". Ditolak: membuat ulang di tiap jawaban masuk (ongkos token untuk ringkasan yang tak dibaca).
5. **Async dengan klaim atomik.** `POST` menandai `pending` lewat upsert berfilter `status != pending` (atau pending lebih tua dari 3 menit, dianggap goroutine-nya mati), lalu goroutine memanggil model dan menulis hasil hanya bila penanda klaimnya masih sama. Dua pengelola yang membuka halaman bersamaan menghasilkan satu panggilan: yang kalah menabrak indeks unik dan dijawab `dimulai:false`. Kartu melakukan polling tiap 3 detik selama `pending`.
6. **Masukan tanpa identitas, keluaran tanpa angka.** `susunMasukanRingkasan` hanya membaca jawaban dan waktunya; statistik memakai `aggregateField` yang sama dengan halaman analisa; teks bebas dikirim terbaru dulu, dipotong 500 karakter per jawaban dan 30.000 karakter total (penanda `teks_terpotong` tampil di kartu). Model diminta tidak menulis angka dan tidak menyebut nama.
7. **Keluaran dikunci dua lapis**, pola benefit ADR 0082: `json_schema strict` dengan `rujukan` ber-`enum` key pertanyaan, lalu `saringHasil` membuang rujukan yang bukan key, butir kosong, dan butir di atas `maksButirPerBagian` (3 sejak revisi di bawah; semula 5).

### Revisi 2026-10-17: ringkas, tanpa rujukan di layar

Ringkasan pertama di prod (survei 160 jawaban) dikeluhkan **sulit dibaca**: tiap butir ditempeli satu sampai tiga label pertanyaan rujukan yang panjang (sekitar 40 label di 20 butir, dua label yang sama berulang hampir di setiap butir), topik yang sama muncul di tiga bagian, dan butirnya dua kalimat. Disetujui user hari yang sama:

8. **Rujukan disimpan, tidak ditampilkan.** Label pertanyaan survei terlalu panjang untuk ditempel per butir; data `rujukan` tetap tersimpan untuk pemakaian lain.
9. **Paling banyak 3 butir per bagian, satu kalimat pendek**, tanpa mengutip kalimat pertanyaan atau jawaban dan tanpa mengulang topik di lebih dari satu bagian. Angka batas di prompt dibaca dari konstanta yang sama dengan penyaring (`maksButirPerBagian`), dikunci test, supaya prompt dan penyaring tak bisa menyimpang.
10. **Tata letak**: tema utama selebar kartu, lalu hal baik, keluhan, dan rekomendasi tiga kolom (menumpuk di layar sempit).
11. **`versi_prompt`**: ringkasan yang dibuat dengan versi prompt lain terbaca basi dan **langsung** boleh dibuat ulang, tanpa menunggu jawaban baru dan tanpa jeda 10 menit. Jedanya menjaga ongkos jawaban baru, bukan menahan perbaikan gaya. Naikkan `versiPromptRingkasan` setiap aturan prompt atau bentuk keluaran berubah.

## Konsekuensi

**Yang didapat**

- Jawaban teks yang selama ini hanya terbaca lewat CSV ikut terangkum di layar analisa.
- Ringkasan lama tetap tampil selama pembaruan berjalan atau gagal, jadi kartu tak pernah kosong hanya karena sedang diperbarui.

**Yang dibayar dan diterima sadar**

- ⚠️ **Isi jawaban teks survei keluar dari service** ke endpoint AI internal, yang meneruskannya ke Claude, sama seperti draf lowongan dan screening CV di recruitment. Identitas pengisi tidak ikut, tetapi isi jawaban bisa menyebut nama orang lain; model diminta tidak mengulanginya, dan itu hanya prompt, bukan jaminan.
- ⚠️ **Prompt injection lewat jawaban teks** mungkin. Dampaknya terbatas pada isi ringkasan itu sendiri: bentuk keluaran dikunci skema, rujukan disaring ulang, dan kartu menyatakan teksnya ditulis AI.
- ⚠️ **Larangan angka dan nama hanya ditegakkan lewat prompt.** Skema tak bisa mencegah model menulis "sebagian besar" yang tak didukung data.
- **Pesan galat dari backend berbahasa Indonesia** dan tampil apa adanya di locale English. Diterima karena pembaca utamanya admin yang mendiagnosis; kode galat yang diterjemahkan FE adalah perbaikan bila kelak dibutuhkan.
- **Teks ringkasan hanya Bahasa Indonesia**, apa pun bahasa layar. Label kartu tetap dua bahasa (ADR 0010).
- **Env `AI_*` kini dibutuhkan `form-builder-service`** di kedua compose. Kosong berarti ringkasan berstatus gagal "konfigurasi AI belum lengkap" di layar; sisa service tetap jalan. Env baru menuntut `--force-recreate`.
- `konfigAI` kini tersalin di recruitment dan form-builder. Mengangkatnya ke `shared-library/ai` adalah task tersendiri karena ikut mengubah recruitment.

## Dokumen Terkait

- [[Microservices - Form Builder Service]] §Ringkasan AI hasil survei
- [[IT - Form Builder]] (konsep produk)
- [[API - Form Builder Service]] (kontrak rute)
- [[ADR - 0082 Integrasi AI lewat Klien Tipis di Shared-Library]]
- [[ADR - 0142 Pengisi Penilaian dan Survei Selalu Anonim, IT Membuka Identitas lewat Jalur Audit Bercatatan]]
