# ADR - 0140 Versioning Rilis SemVer per Repo dari Tag Git

> **Status**: 🟡 **Diterima, belum diimplementasikan**, 2026-09-29. Diputuskan di sesi Tech Development 2026-09-29; **perlu dikabarkan ke wirkancil**, yang membuat tag dan GitHub Release `v0.1.2` kedua repo dan kebiasaannya diubah di sini. Nol kode: versi belum dibakar ke image mana pun, `/health` belum membawa versi. Implementasinya dua brief (BE dulu, lalu FE), lihat §Implementasi.

%% Status di blockquote atas supaya terbaca VAULT-INDEX.json (15 baris pertama). %%

## Untuk Manajemen

**Masalahnya dalam satu kalimat.** Backend dan frontend ERP sudah diberi nomor versi (`v0.1.2`), tapi belum ada aturan kapan nomornya naik dan tak ada cara membaca dari sistem yang sedang berjalan versi mana yang dipakai, jadi "ERP versi berapa sekarang" belum bisa dijawab dengan pasti.

**Yang diputuskan.** Tiap aplikasi (backend, web, MyBharata) punya nomor versinya sendiri, naik tiap kali dirilis ke produksi, dan tiap service yang berjalan melaporkan versinya sendiri. Untuk satu nomor yang bisa disebut ke manajemen, tiap rilis produksi dicatat dengan nama tanggal (`Rilis 2026.10.02`) yang merangkum versi ketiganya di [[IT - Catatan Rilis ERP]].

**Yang tidak dijanjikan.** Nomor versi backend dan web **tidak** disamakan. Angka yang sama tidak berarti keduanya cocok satu sama lain, dan menyamakannya memaksa rilis kosong di aplikasi yang tidak berubah.

## Deskripsi

*Aturan penomoran versi rilis untuk `bip-erp`, `erp-frontend`, dan `mybharata-app`: SemVer independen per repo, tag git sebagai satu-satunya sumber, tag dibuat saat deploy produksi, versi dibakar ke image lewat build-arg dan dilaporkan `/health`, dan satu catatan rilis payung per deploy produksi.*

- **Path di repo (yang terdampak, belum diubah)**: `bip-erp/services/*/Dockerfile`, `bip-erp/api-gateway/Dockerfile`, `bip-erp/docker-compose.yml`, handler `/health` tiap service (mis. `bip-erp/services/assistant/main.go`, `bip-erp/api-gateway/main.go`), `bip-erp/.github/workflows/deploy.yml` · `erp-frontend/Dockerfile`, `erp-frontend/package.json`
- **Tanggal**: 2026-09-29
- **Diukur ke**: bip-erp `origin/main` (91 commit sesudah `v0.1.2`), erp-frontend `origin/main` (84 commit sesudah `v0.1.2`)

## Context

### Keadaan per 2026-09-29

| | bip-erp | erp-frontend |
|---|---|---|
| Tag | `v0.1.0` (06-08), `v0.1.1` (06-10), `v0.1.2` (09-27) | `v0.1.1` (06-10), `v0.1.2` (09-27) |
| GitHub Release | ada, `v0.1.2` oleh wirkancil 2026-09-27 10:35:00Z | ada, `v0.1.2` oleh wirkancil 10:35:39Z |
| Versi di berkas | tidak ada | `package.json` `"version": "0.1.0"`, **tidak cocok dengan tag** |
| Penanda versi di biner | nol (`git grep 'ldflags\|BuildVersion\|AppVersion\|GIT_SHA'` hanya mengenai `-ldflags="-s -w"`) | nol |
| `/health` | handler sendiri per service, tanpa helper bersama; isinya `{"message":"ok"}` atau semacamnya | - |

Tiga masalah yang tampak dari tabel itu:

1. **Aturan naiknya tak tertulis, dan yang terjadi tidak mengikuti SemVer.** `v0.1.2` adalah kenaikan *patch* yang memuat 860 commit bip-erp dan 5.640 commit erp-frontend selama 3,5 bulan, sebagian besar fitur baru. Angka yang sama di kedua repo lahir karena keduanya dibuat bersamaan, bukan karena aturan.
2. **Satu tag repo tidak menjawab "apa yang berjalan di produksi" untuk backend.** bip-erp di-deploy **per service** ([[RUN - Deploy Microservices bip-erp]] §1: `docker compose up -d --build <svc> --no-deps`), jadi pada satu waktu container produksi bisa dibangun dari commit yang berbeda-beda. Runbook itu sendiri (§1b) menyatakan `/health` **bukan** bukti biner mana yang melayani, dan menjadikan umur image sebagai gantinya.
3. **Fakta versi di dua tempat sudah menyimpang**: tag `v0.1.2` dan `package.json` `0.1.0`.

### Batasan teknis yang menentukan bentuk keputusan

**`.git` sengaja dibuang dari build context Docker di kedua repo.** `.dockerignore` bip-erp mencatat alasannya: di klon server `.git` berukuran 292 MB sementara isi kerjanya 34 MB, dan penulisnya sudah memeriksa bahwa tak ada Dockerfile yang memakai `git describe`. Jadi versi **tidak bisa** dihitung di dalam `docker build`; ia harus dihitung di host lalu dioper masuk. Keputusan ini mempertahankan pembuangan `.git`.

Produksi membangun image **dari checkout di VM** (`git reset --hard origin/main` lalu `--build`, untuk backend maupun [[RUN - Deploy Frontend ERP ke Produksi]]), jadi host yang membangun selalu punya `.git` untuk menghitung versinya.

MyBharata sudah punya aturan versi lengkap di repo-nya sendiri (`mybharata-app/docs/development/VERSION_MANAGEMENT.md`: SemVer `major.minor.patch+code`, version name DAN code wajib naik tiap unggah ke toko). ADR ini **merujuknya, tidak menyalinnya**.

## Decision

### 1. SemVer independen per repo

`bip-erp` dan `erp-frontend` masing-masing memakai `vMAJOR.MINOR.PATCH` sendiri. `mybharata-app` tetap mengikuti `VERSION_MANAGEMENT.md`. **Angka yang kebetulan sama antar-repo tidak bermakna apa pun**, dan tidak ada kewajiban menaikkan repo yang tidak berubah.

Kecocokan antar-repo, bila diperlukan, dicatat sebagai kebutuhan minimum di catatan rilis ("FE `v0.3.0` butuh BE ≥ `v0.4.0`"), bukan lewat angka yang disamakan.

### 2. Tag git adalah satu-satunya sumber versi

Nilai versi ada di **tag git**. GitHub Release dibuat dari tag itu. Semua tempat lain (biner, `/health`, bundle FE, `package.json` di dalam image, catatan rilis) **menurunkannya**, tidak pernah ditulis tangan. `package.json` yang ter-commit di erp-frontend tidak lagi dianggap versi (lihat §5).

### 3. Kapan dan oleh siapa tag dibuat

- Tag dibuat **tepat sebelum deploy produksi**, pada commit `origin/main` yang akan di-checkout di VM. Merge ke `main` sendiri tidak membuat tag.
- Yang membuat tag adalah **orang yang menjalankan deploy produksi**, sejalan dengan aturan bahwa deploy produksi dijalankan manusia.
- Satu deploy produksi yang hanya menaikkan sebagian service bip-erp tetap satu tag repo. Service yang tidak di-rebuild tetap melaporkan versi lamanya (§4), dan itu **benar**: memang biner lama yang melayaninya.

### 4. Aturan naik selama fase `0.x`

| Naik | Bila rilis memuat |
|---|---|
| **MINOR** (`0.1.x` → `0.2.0`) | fitur baru, **atau** perubahan kontrak API (field/rute baru, bentuk respons berubah, env baru) |
| **PATCH** (`0.2.0` → `0.2.1`) | hanya perbaikan tanpa kontrak berubah |

Bila ragu, naikkan MINOR. `v0.1.2` di atas adalah contoh yang meleset (fitur dirilis sebagai patch) dan tidak diubah surut.

**Pindah ke `1.0.0` butuh ADR tersendiri**, diambil saat tim bersedia berkomitmen pada kontrak API yang stabil. Sampai saat itu SemVer `0.x` mengizinkan MINOR membawa perubahan yang merusak kompatibilitas, dan itu disengaja.

### 5. Versi dibakar ke image saat build, dihitung di host

Di host yang membangun (VM produksi, dan pipeline dev):

```bash
git fetch origin main --tags
git reset --hard origin/main
export APP_VERSION=$(git describe --tags --always --dirty)
```

`git describe` menghasilkan `v0.2.0` bila commit yang dibangun persis bertag, `v0.2.0-3-g58b95f6` bila tiga commit sesudahnya, dan akhiran `-dirty` bila checkout di server disunting tangan. Ketiganya **jujur**, dan justru itu gunanya: build di luar tag tetap terbaca sebagai bukan rilis.

- **bip-erp**: compose mengoper `APP_VERSION` sebagai `build.args`, Dockerfile menerimanya lewat `ARG APP_VERSION=unknown` dan menanamnya dengan `go build -ldflags "-s -w -X <paket>.Version=${APP_VERSION}"`. Tiap service menambahkan field `version` ke respons `/health`-nya **tanpa mengubah field yang sudah ada** (healthcheck container memakai `wget --spider`, jadi isi badan tak memengaruhinya).
- **erp-frontend**: build-arg yang sama menjadi `NEXT_PUBLIC_APP_VERSION` dan ditulis ke `package.json` di dalam image saat build. Nilai `version` di `package.json` yang ter-commit dibekukan sebagai `0.0.0` supaya tak ada yang membacanya sebagai versi. Versi tampil di satu tempat di UI, lewat i18n (ADR 0010).
- ⛔ **Nilai bawaan wajib `unknown`, bukan string kosong.** Lupa meng-export `APP_VERSION` adalah kegagalan yang paling mungkin, dan dengan bawaan kosong ia senyap. Gerbang deploy menolak `unknown` (§6).
- ⛔ **`--tags` pada fetch wajib ditulis eksplisit.** Tag yang dibuat sesudah commit-nya sudah ada di VM tidak dijamin ikut ter-fetch, dan `describe` yang tak melihat tag baru melaporkan tag lama tanpa satu pun galat.

### 6. Gerbang deploy: versi yang dilaporkan sama dengan tag yang baru dibuat

Sesudah deploy produksi, untuk tiap service yang dinaikkan, `version` di `/health` harus **sama persis** dengan tag yang baru dibuat. `unknown`, tag lama, atau akhiran `-N-g<sha>` berarti build-arg tak masuk, tag tak ter-fetch, atau tag dibuat di commit yang berbeda dari yang dibangun. Gerbang ini **tidak menggantikan** gerbang umur image dan gerbang perilaku di runbook; ia menambah satu bukti yang bisa dibaca dari luar container.

### 7. Catatan rilis payung per deploy produksi

Tiap deploy produksi dicatat sebagai satu baris di [[IT - Catatan Rilis ERP]] bernama kalender `Rilis YYYY.MM.DD` (akhiran `.2`, `.3` bila lebih dari satu rilis sehari), berisi tag bip-erp beserta service yang dinaikkan, tag erp-frontend, dan versi MyBharata yang sedang di toko. Catatan itu **mencatat, bukan sumber**: bila ia bertentangan dengan tag atau `/health`, yang benar tag dan `/health`.

### 8. Versi terlihat publik: diterima sadar

Gateway meneruskan `GET /health?check=<svc>` dari internet ([[RUN - Deploy Microservices bip-erp]] §4), jadi tag dan sha pendek akan terbaca siapa pun. Isinya hanya versi, tanpa env, host, atau konfigurasi. Risikonya dinilai kecil dibanding manfaat bisa membaca versi yang berjalan tanpa akses SSH.

## Consequences

- **Pertanyaan "versi berapa yang jalan" bisa dijawab dari luar container**, per service, tanpa SSH, sesudah kedua brief implementasi mendarat. Sebelum itu tidak berubah apa pun.
- **Orang yang men-deploy produksi mendapat dua langkah tambahan**: membuat tag (dan GitHub Release) sebelum build, lalu menulis satu baris catatan rilis sesudahnya. Keduanya masuk ke runbook deploy BE dan FE.
- **Rilis ke dev tidak memakai tag**, dan `/health` dev akan melaporkan `v0.x.y-N-g<sha>`. Itu benar: dev menjalankan `main`, bukan rilis.
- **`package.json` erp-frontend berhenti bermakna sebagai versi.** Siapa pun yang mencari versi FE di sana akan menemukan `0.0.0` dan harus melihat tag.
- **Menambah service baru di bip-erp berarti ikut menambah `ARG APP_VERSION` dan field `version`**, atau service itu melaporkan `unknown` dan gerbang §6 menolaknya. Itu disengaja: service yang lupa terlihat di rilis pertamanya.
- **Tag `v0.1.0` sampai `v0.1.2` tidak diubah.** Rilis berikutnya dimulai dari `v0.2.0` untuk kedua repo karena keduanya memuat fitur sejak `v0.1.2`; sesudah itu angka keduanya akan menyimpang, dan itu diharapkan.

## Implementasi

Dua brief, backend lebih dulu:

1. **bip-erp**: paket versi di `shared-library` (satu variabel `Version`, bawaan `unknown`), `ARG APP_VERSION` + `-ldflags -X` di tiap Dockerfile, `build.args` di `docker-compose.yml`, `version` di `/health` tiap service dan gateway, export `APP_VERSION` di pipeline dev. Uji: tiap service yang punya Dockerfile wajib punya `ARG APP_VERSION` (pemindai sumber, supaya service baru yang lupa tertangkap).
2. **erp-frontend**: `ARG APP_VERSION` di Dockerfile, `NEXT_PUBLIC_APP_VERSION`, `package.json` ditulis saat build dan dibekukan `0.0.0` di repo, versi tampil di UI lewat i18n.

Langkah deploy-nya ditulis di [[RUN - Deploy Microservices bip-erp]] §1c dan [[RUN - Deploy Frontend ERP ke Produksi]] §Versi rilis.

## Di luar keputusan ini

- **Otomasi pembuatan tag** (tag otomatis saat merge atau lewat pipeline): deploy produksi dijalankan manusia, jadi tag ikut manusia.
- **Changelog otomatis**: GitHub Release boleh memakai "generate release notes" bawaan, tapi tak ada format yang diwajibkan.
- **Versi per service di bip-erp** (tag `employee-service/v1.2.0`): satu tag repo cukup karena `/health` sudah melaporkan versi per container.

## Dokumen Terkait

- [[RUN - Deploy Microservices bip-erp]] · [[RUN - Deploy Frontend ERP ke Produksi]]: tempat langkah tag dan gerbang versi dijalankan
- [[IT - Catatan Rilis ERP]]: catatan rilis payung (§7)
- [[IT - CI-CD]]: pipeline dev dan jalur produksi
- [[APP - MyBharata]]: aturan versinya di `mybharata-app/docs/development/VERSION_MANAGEMENT.md`
