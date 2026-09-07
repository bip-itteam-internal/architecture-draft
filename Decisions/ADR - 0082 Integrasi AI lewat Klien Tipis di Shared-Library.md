## Deskripsi

*Integrasi LLM pertama di bip-erp: paket tipis `shared-library/ai/` yang memanggil endpoint internal ber-antarmuka OpenAI-compatible, dengan `stream:false` ditanam mati dan balasan dipaksa `json_schema strict`. Pemakai pertamanya menulis isi lowongan otomatis begitu Job Requisition disetujui.*

- **Status**: ⚠️ Implemented (ada catatan) — klien dan draf lowongan sudah ditulis dan diuji (bip-erp [#1776](https://github.com/bip-itteam-internal/bip-erp/pull/1776) + [#1777](https://github.com/bip-itteam-internal/bip-erp/pull/1777), erp-frontend [#1480](https://github.com/bip-itteam-internal/erp-frontend/pull/1480)); **belum di-deploy**, dan belum ada kuota maupun cache.
- **Path di repo**: `bip-erp/shared-library/ai/client.go` · `services/recruitment/ai_draft.go` · `ai_prompt.go` · `models_ai_draft.go` · `erp-frontend/src/features/hris/recruitment/postings/lib/draf-ai.ts`
- **Tanggal**: 2026-09-07

## Context

Sebelum ini bip-erp **tidak punya integrasi AI/LLM apa pun**; dibuktikan `git grep` atas `openai`, `chat/completions`, dan `llm` di seluruh `services/` dan `shared-library/` — nol hasil.

Kebutuhan pertamanya konkret. Dari 3 lowongan di produksi, satu memperlihatkan masalahnya: **Office Boy** terbit dengan `requirements` berupa keluaran prefill mentah (`- Pendidikan: SMA/SMK`, `- Usia: 18-30`, `- Jenis kelamin: Laki-laki`), deskripsi satu frasa, dan `benefits` diisi **"10-20 juta"** yang sebenarnya gaji. Dua lowongan lain sudah dipoles tangan HR jadi Markdown yang layak dibaca. Selisih itu yang mau ditutup, tanpa meminta pengaju memperbaiki sendiri.

Endpoint internal `https://code.bharatainternasional.com/v1` diprobe langsung 2026-09-07 sebelum keputusan diambil:

| Sifat | Nilai terukur |
|---|---|
| Bentuk | OpenAI-compatible |
| ⛔ `stream` | **default TRUE bila tak dikirim**, kebalikan spesifikasi OpenAI |
| Gejala bila `stream` terlewat | HTTP **200** dengan `choices` **null**, tanpa satu pun galat |
| ⚠️ Prefiks `cc/` | menyuntikkan **~2.030 token** system prompt Claude Code ke tiap panggilan |
| Persona suntikan | bisa ditimpa system message sendiri |
| `json_schema` `strict:true` | didukung, mengembalikan JSON sah |
| Model dipakai | `cc/claude-sonnet-4-6` |

Probe satu kalimat menghasilkan `prompt_tokens` **2163**, yang mengonfirmasi overhead persona itu nyata dan tetap.

## Decision

### 1. Klien tipis di shared-library, BUKAN microservice

`shared-library/ai/` sebaris dengan `notification/whatsapp`, `notification/email`, dan `accurate/` yang sudah ada. Satu fungsi `GenerateJSON`.

Microservice tersendiri ditolak untuk sekarang: ia menuntut entri compose dev **dan** prod, `AI_MODULE_URL` di gateway, rute, deploy, dan runbook baru — sementara pemakainya baru satu. [[RUN - Deploy Microservices bip-erp]] §3a2 mencatat bahwa service baru justru yang paling mudah terlewat dari compose dev, dan panggilannya lalu mati di resolusi DNS sebagai 502 yang menyesatkan.

Bila kelak ada pemakai kedua dan ketiga, memindahkan paket ini jadi service adalah perubahan mekanis. Membangunnya sekarang adalah ongkos di muka untuk manfaat yang mungkin tak datang.

### 2. `stream: false` ditanam mati, bukan parameter

Bukan kerapian melainkan pengaman. Field ini default TRUE di endpoint tersebut, dan kegagalannya **tidak terbaca sebagai kegagalan**: status 200, tanpa galat, nilai kosong mengalir ke bawah. Tak ada pemakaian sah yang membutuhkannya `true` di sini.

Dikunci test berkontrol-negatif yang dibuktikan merah sebelum dikembalikan.

### 3. Benefit dikunci ENUM di skema, bukan diminta lewat prompt

Empat butir baku perusahaan diambil verbatim dari dua lowongan yang sudah dipoles HR, lalu dipasang sebagai `enum` di `json_schema`. Model karena itu secara **struktural** tak bisa mengarang fasilitas.

Lowongan terbit ke publik; menjanjikan yang perusahaan tak punya adalah masalah nyata, dan meminta model "jangan mengarang" lewat prompt tidak mengikat apa pun.

Usulan di luar daftar dibatasi 2 butir dan disimpan di field **terpisah** (`benefit_tambahan`), dirender dengan tombol Tambahkan, supaya HR tahu persis butir mana yang perlu diperiksa. Disaring **dua lapis**: enum di skema, lalu penyaringan ulang di sisi kita, sebab endpoint bisa berubah dan model bisa diganti.

### 4. Asinkron saat disetujui; persetujuan tak pernah gagal karena AI

Goroutine best-effort dengan konteksnya sendiri. `ai_draft: pending` **tidak** dititipkan lewat `extra` milik `setReqStatus` — itu akan berlomba dengan tulisan goroutine dan bisa menimpa draf yang sudah `ready`. Goroutine menulis `pending` sendiri setelah membaca ulang requisition dan memastikan statusnya benar-benar `Approved`.

Hanya ID yang dioper, bukan `*fiber.Ctx`: Fiber mengembalikan `Ctx` ke pool begitu handler selesai. Pola sama dengan `notifyHRSupervisors`.

## Consequences

**Yang didapat**

- Isi lowongan yang layak dibaca pelamar sejak draf pertama; HR meninjau alih-alih mengetik, dan pengaju tak perlu diminta memperbaiki.
- Pondasi yang bisa dipakai fitur lain tanpa menambah service, gateway, atau compose.

**Yang dibayar**

- ⚠️ **Overhead ~2.030 token per panggilan** dari suntikan persona proxy, seragam untuk semua model. Memilih model lebih kecil karena itu tidak banyak menghemat.
- ⚠️ **Draf adalah potret sekali jalan.** Mengedit requisition sesudahnya tidak memperbarui draf; HR memakai tombol buat ulang bila perlu.
- ⛔ **Kunci API hidup di `.env` server saja.** Ia sempat tertempel di percakapan saat fitur ini dirancang, jadi **wajib dirotasi**. `.env.example` hanya memuat nama variabelnya.
- Env `AI_*` dibaca saat container **dibuat**, jadi deploy menuntut `--force-recreate`, bukan `restart`.

**Batas yang sengaja tidak dilewati**

Registry prompt, template engine, abstraksi multi-provider, kuota, dan cache. Semuanya menebak pemakai yang belum ada; prinsip tim menahan abstraksi sampai pemakai **ketiga** muncul.

## Dokumen Terkait

- [[Microservices - Recruitment Service]] — pemakai pertama
- [[HRIS - Recruitment]] — konsep/bisnis rekrutmen
- [[RUN - Deploy Microservices bip-erp]] — prosedur deploy & jebakan env
- [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] — gerbang izin endpoint buat ulang
