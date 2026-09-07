## Deskripsi

*Aturan tata letak untuk halaman yang isinya ANGKA (dashboard, ringkasan, analytics) di `erp-frontend`. Sengaja terpisah dari aturan bagan yang sudah ada: `.agent-kit/rules/team-memory.md` § Bagan/chart mengatur WARNA, AMBANG, dan komponen bersama, dan tak satu barisnya mengatur KOMPOSISI halaman. Celah itulah yang diisi dokumen ini.*

- **Status**: 🟡 Pedoman berlaku, belum ditegakkan test dan belum diadopsi merata. Diturunkan dari enam aturan layout dashboard (materi Skula Talks, dibagikan 2026-09-03) lalu **diterjemahkan ke komponen yang benar-benar ada di repo**, bukan disalin mentah. Seberapa jauh adopsinya, termasuk aturan 2 yang masih nol, ada di bagian "Keadaan terukur" yang diukur langsung ke kode pada tanggal yang sama.
- **Ruang lingkup**: halaman di bawah `erp-frontend/src/app/(main)/` yang isinya kartu angka dan bagan. Halaman DAFTAR tidak diatur di sini, sudah punya prosedurnya sendiri di skill `/migrasi-tabel-hris`.
- **Bukan aturan bagan**: pilihan warna, ambang, `type="monotone"`, `connectNulls`, id gradien, semuanya tetap di team-memory. Dokumen ini berhenti di batas kartu.

## Kenapa dokumen ini ada

Semua gerbang yang berlaku hari ini bertanya apakah KODENYA benar. Tak satu pun bertanya apakah layarnya bisa dibaca. Akibatnya konsisten dan bisa diukur: 18 komponen bagan di repo ini, **nol** di antaranya pernah diberi ukuran dominan, jadi setiap dashboard menggambar semua hal sama besar dan tak memberi tahu pembacanya harus mulai dari mana.

Dokumen ini juga sengaja TIDAK ditaruh di `team-memory.md`. Berkas itu di-load tiap sesi dan sudah sangat panjang; aturan yang cuma dibutuhkan saat merancang layar harus dibaca on-demand.

## Enam aturan, diterjemahkan ke komponen kita

### 1. Kerangka dulu, grafik belakangan

Tentukan zona halaman sebelum memilih jenis bagan. Tiga zona yang wajib diputuskan:

| Zona | Komponen yang sudah ada | Catatan |
|---|---|---|
| Baris saringan di ATAS | `PageShell` (`features/marketing-analytics/components/page-shell.tsx`) | Ia memakai `Banner bare` di dalam satu kartu, pola yang sama dengan `MainTable`. Jangan merakit baris saringan sendiri. |
| Satu area fokus utama | belum ada komponennya | lihat aturan 2 |
| Ruang untuk catatan/insight | `BarisKonteksVonis`, `kolom-keputusan.tsx` (marketing-analytics) | Angka tanpa kalimat menuntut pembacanya menyimpulkan sendiri, dan tiap pembaca menyimpulkan beda. |

⚠️ `PageShell` punya prop `tanpaKartu` justru untuk halaman depan yang isinya sudah kartu semua. Membungkus kartu dengan kartu (aturan 5) lebih buruk daripada tanpa kerangka sama sekali, dan itu sudah tertulis di komentar komponennya.

### 2. Satu insight utama yang dominan

⛔ **Ini yang paling kosong di repo kita.** Grafik terpenting harus berukuran lebih besar dari pelengkapnya, bukan satu sel di grid simetris.

Cara melakukannya di sini: bungkus bagan utama dalam `<Card className="lg:col-span-2">` di dalam `grid lg:grid-cols-3`. Satu-satunya contoh yang sudah ada: `features/procurement/kas/components/DashboardAnggaranKas.tsx:213`. Padanan tanpa kartu: `beranda-portal.tsx:25` (`lg:col-span-2` untuk kolom utama, `lg:col-span-1` untuk pengumuman).

Yang harus dihindari: `grid gap-4 lg:grid-cols-2` berisi dua bagan setara, lalu `grid gap-4 lg:grid-cols-2` lagi berisi dua bagan setara. Empat bagan sama besar tidak punya urutan baca, dan pembacanya memulai dari mana saja.

### 3. Kelompokkan yang satu tema

Sudah dilakukan dengan benar di `features/hris/dashboard/kartu/isi/isi-ringkasan.tsx`: tiga kartu angka divisi dalam satu grid, dua bagan turnover dalam grid berikutnya, dua bagan sebaran dalam grid ketiga. Komentar di berkas itu bahkan menjelaskan kenapa dua bagan turnover bertetangga (sumber deret yang sama, pertanyaan berbeda). Pertahankan bentuk itu.

Yang menandai kelompok adalah **jarak**, bukan garis atau kotak tambahan.

### 4. Jarak yang konsisten

⚠️ **`Container` (layout `(main)`) SUDAH memasang `p-4 sm:p-6` dan `gap-4 sm:gap-6`** (`components/layout/container.tsx:38`). Padding sendiri di halaman berarti padding ganda, dan itu sudah jadi gotcha lama di team-memory.

Yang belum tercatat: irama VERTIKALNYA pun sudah ditentukan di sana, jadi tiap halaman yang menulis `space-y-*` sendiri sedang menyatakan ulang fakta yang sudah dimiliki layout. Satu tab Ringkasan Divisi hari ini memakai empat nilai jarak sekaligus:

| Lapisan | Nilai | Berkas |
|---|---|---|
| Layout | `gap-4 sm:gap-6` | `components/layout/container.tsx` |
| Halaman | `space-y-6` | `app/(main)/hris/page.tsx` |
| Isi tab | `space-y-8` | `features/hris/dashboard/kartu/isi-tab.tsx` |
| Grid kartu | `gap-4` | `isi/isi-ringkasan.tsx` |

**Aturan yang berlaku**: jarak antar-seksi `gap-6` (24px), jarak antar-kartu di dalam satu grid `gap-4` (16px). Dua nilai, bukan empat. `space-y-5`, `gap-5`, `gap-10` tidak dipakai di halaman dashboard.

### 5. Lebih sedikit kotak

Gabungkan area berfungsi serupa ke satu wadah. Hindari kotak di dalam kotak. Yang memisahkan bagian adalah ruang kosong, bukan garis tebal.

`PageShell` sudah menegakkan ini di marketing-analytics, lengkap dengan alasannya tertulis di komentar: sebelum ada kerangka itu, judul dan saringan melayang di latar halaman lalu tabel jadi benda lain di bawahnya, dan enam belas halaman terbaca seperti enam belas aplikasi.

### 6. Rancang alur pandangan mata

Urutan bakunya: **saringan dan rentang waktu → kartu KPI → bagan inti → detail pendukung → catatan aksi**.

Konsekuensi yang sering terlewat: **titik awal alur harus sama di layar yang bersebelahan.** Hari ini `/direktur` merender `<h1>` judul halaman sementara `/hris` sengaja mencabutnya (alasannya tertulis di kedua berkas, dan masing-masing masuk akal sendiri-sendiri). Keduanya dashboard tingkat atas yang dibuka orang yang sama, dan mata memulai di tempat berbeda. Salah satu harus mengalah; putuskan sekali, jangan per halaman.

## Keadaan terukur (2026-09-03)

Diukur ke `erp-frontend/src`, 1.526 berkas `.tsx` non-test.

| Yang diukur | Angka | Artinya |
|---|---|---|
| Komponen bagan memakai `ChartContainer` | 18 | populasi bagan sungguhan |
| Di antaranya yang punya ukuran dominan (`col-span-*`) | **0** | aturan 2 belum dipakai sama sekali |
| Berkas memakai `col-span-2` | 53 | praktis semuanya field formulir dan halaman detail, bukan dashboard |
| Pemakai `PageShell` | 16 | seluruhnya di `features/marketing-analytics/`, nol di luar |
| Pemakai `MainTable` | 126 | kerangka tabel bersama |
| Pemakai `MarketingInsightTable` | 11 | kerangka tabel TANDINGAN, lihat di bawah |

### Dua sistem desain hidup berdampingan

`features/marketing-insight/` (53 berkas) memakai kosakata visualnya sendiri: 20 berkas memakai token `marketing-insight-{neutral,primary,secondary,tertiary}-*`, dan 16 berkas memakai `bg-white` mati. Dari 59 berkas ber-`bg-white` di SELURUH aplikasi, 16 ada di satu fitur ini, dan `bg-white` berarti **mode gelap tidak berlaku di sana**.

Ini bukan soal selera. Modul itu juga memakai jarak yang berbeda (`gap-5`, `gap-10`, `p-5`) sehingga halaman marketing-insight tidak bisa diletakkan bersebelahan dengan halaman HRIS tanpa terlihat berasal dari aplikasi lain.

### Temuan yang bisa langsung diperbaiki

`app/(main)/marketing-insight/page.tsx`:

1. **Dua dari enam kartu modul tidak punya `href`** (`Content Analysis`, `Logistic Monitoring`), tetapi tetap diberi `cursor-pointer`. Kartunya terlihat bisa diklik dan tidak melakukan apa pun. Kelas "alur pengguna terputus" yang dicari `/review` §F.
2. **`grid grid-cols-4` tanpa breakpoint responsif** sama sekali. Empat kolom dipaksakan sampai lebar layar terkecil.
3. **Deskripsi `GMV Max Monitoring` dan `Logistic Monitoring` identik** kata per kata.
4. Seluruh teksnya hardcode English, melanggar ADR 0010 (i18n dua bahasa).

## Yang TIDAK diatur di sini

- Warna, palet, ambang, dan seluruh keputusan Recharts: `team-memory.md` § Bagan/chart.
- Halaman daftar/tabel: skill `/migrasi-tabel-hris`.
- Apakah sebuah metrik layak ditampilkan sama sekali: itu pertanyaan `/analisa-kebutuhan`, bukan pertanyaan layout.

## Rujukan

- [[REF - Penamaan Metrik & Sumber KPI]] (label yang muncul di kartu ini)
- [[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]]
- `.agent-kit/rules/team-memory.md` § Konvensi FE / UI, § Bagan/chart
