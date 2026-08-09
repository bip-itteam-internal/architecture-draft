---
name: migrasi-tabel-hris
description: Gunakan saat memindahkan halaman daftar erp-frontend ke struktur tabel HRIS (pola satu kartu — Banner bare di dalam toolbar MainTable), atau saat membuat halaman daftar baru. Memuat urutan kerja, jebakan yang sudah terbukti menggigit, dan gerbang verifikasi.
---

# Migrasi halaman daftar ke struktur tabel HRIS

Pola satu kartu: `Banner bare` duduk di dalam prop `toolbar` milik `MainTable`,
sehingga alat penyaring dan hasil penyaringannya terbaca sebagai satu benda.

**Acuan yang sudah jadi**, baca salah satu sebelum menulis:
- `src/app/(main)/hris/resign/page.tsx` — bentuk paling murni, ada aksi tulis.
- `src/app/(main)/finance/piutang/tiktok/page.tsx` — read-only, filter banyak,
  respons BE bergaya marketplace.

## 0. Kumpulkan konteks dari KODE, jangan diasumsikan

- Rute + berkas halaman dan komponen tabelnya sekarang.
- Endpoint yang dipanggil: salin apa adanya dari hook fetch-nya.
- Bentuk respons: `{ data, pagination }` atau `{ data, meta: { page, per_page,
  total_page, total_number } }`. Kalau `meta`, **adaptasi di FE**, jangan minta
  BE berubah.
- Query param yang benar-benar didukung BE.
- Ada aksi tulis atau tidak. Kalau tidak ada, lewati schema + form modal.

## 1. Baca hook & tabel lama LEBIH DULU

Dua hal yang hampir selalu ditemukan dan wajib ikut dibereskan:

- **Nilai yang dirakit lalu dikembalikan tapi tak pernah dibaca halaman.** Di
  `/finance/ar` ada dua query semacam itu di tiga hook, yaitu enam permintaan
  sia-sia tiap kali halaman dibuka.
- **Format tanggal/uang yang dipaku di lapisan fetch** (mis.
  `toLocaleDateString("id-ID")` di dalam fungsi transform). Selama formatnya
  dikerjakan di situ, kolomnya **mustahil** ikut bahasa yang sedang aktif.
  Pindahkan ke `render` kolom memakai `intlLocale(lang)`, dan kunci dengan uji
  berpenanda (isi field lama dengan string penanda, pastikan ia tak muncul).

## 2. Ekstrak keputusan non-UI ke `lib/` dan uji lebih dulu

Aturan yang bukan urusan tampilan (saling-kunci filter, adaptasi paginasi,
konversi tanggal) ditaruh di `features/<modul>/<fitur>/lib/` sebagai fungsi
murni beserta testnya. Alasannya bukan kerapian: selama aturan itu hidup sebagai
rentetan `setState` di dalam hook, satu-satunya cara mengujinya adalah merender
halamannya, dan itu berarti tak diuji sama sekali.

## 3. Rakit

```tsx
const tableState = useTableState({ initialLimit: 20 });

<MainTable
  title="<slug>"
  data={rows}
  columns={columns}
  tableState={tableState}
  pagination={pagination}
  isLoading={isLoading}
  isError={isError}
  toolbar={
    <Banner
      bare
      title="<slug>"
      heading={t("...")}
      subtitle={t("...")}
      searchPlaceholder={t("...")}
      filters={filters}
      tableState={tableState}
      refetch={refetch}
      isRefreshing={isFetching}
      actions={<TombolExportServer />}
    />
  }
/>
```

## Jebakan yang SUDAH terbukti menggigit

- **`FilterTable` hanya mengenal `select` dan `date`. Tidak ada filter angka.**
  Ambang numerik jadi preset select (mis. 3/7/14/30/60 hari) atau kontrol
  rakitan sendiri di slot `actions`. Jangan menambah tipe baru ke `FilterTable`
  demi satu modul: komponen itu dirender puluhan halaman lain.

- **Draft `FilterTable` disemai SEKALI saat panel dibuka** dan tak pernah
  menerima perubahan dari luar. Kalau ada aturan saling-kunci antar filter,
  hitung dari pasangan `(sebelum, sesudah)` dan **gabungkan**
  `{ ...sebelum, ...sesudah }`. Key yang hilang berarti "tak berubah", bukan
  "baru dikosongkan pemakai". Tangani `{}` lebih dulu sebagai kosongkan-semua
  (itu yang dikirim tombol Hapus).
  Tanpa penggabungan: menyetel ambang lalu mengubah filter lain akan membuang
  ambang itu, sementara panel tetap menampilkannya sebagai terpilih.
  **Sisa keterbatasan yang tetap ada**: filter yang dibuang normalisasi masih
  tampil terpilih sampai panel ditutup lalu dibuka. Tulis di komentar, jangan
  dibiarkan senyap.

- **Tiap baris wajib punya `_id` / `id` / `employee_id`**; `MainTable` memakainya
  sebagai key. Kalau tipe dari BE tak punya, petakan dulu, dan pastikan unik
  (mis. `order_id` bisa bertabrakan antar-kanal, jadi gabung dengan channel).

- **Punya export SERVER? kirim `hideExport`.** Kalau tidak, tombol unduh bawaan
  `MainTable` (hanya baris yang sedang tampil) berdiri bersebelahan dengan
  export server (seluruh data), dua tombol dengan hasil berbeda jauh tanpa ada
  yang menjelaskan bedanya. Konsekuensinya `exportValue` per kolom jadi
  konfigurasi mati; jangan dipasang.

- **Header bisa-urut tidak menuntut perubahan komponen bersama.**
  `Column.header` menerima fungsi. Bungkus sebagai **komponen bernama**, bukan
  arrow yang dikembalikan factory, atau `react/display-name` menggagalkan lint.

- **Batas atas rentang tanggal**: periksa apakah param BE eksklusif (`*_lt`).
  Kalau ya, kirim tengah malam **hari berikutnya**, atau tanggal terakhir hilang
  diam-diam dan tabelnya tetap terisi sehingga tak ada yang curiga.

- **`emptyText` hanya diisi** bila layar punya sebab kosong yang lebih
  menjelaskan daripada `common.noData` (mis. "pilih toko dulu"). Untuk daftar
  biasa, bawaannya sudah tepat.

- **Mode yang tak berpaginasi**: kirim `pagination` kosong. `MainTable` tak
  merender kaki paginasi, jadi yang hilang hanya kontrol yang memang tak
  berlaku. Sebutkan alasannya di layar.

## i18n (ADR 0010)

- Semua teks user-facing lewat `t()`; kunci ditambahkan ke **kedua** locale.
- Istilah teknis lazim dibiarkan English **di kedua locale**. Yang bukan istilah
  teknis tetap diterjemahkan: "GMV (kotor)" jadi "GMV (gross)", bukan dibiarkan
  berbahasa Indonesia di locale `en`.
- ⚠️ **Variabel interpolasi bernama `count` menyalakan pluralisasi i18next**
  (`key_one`/`key_other` dicari lebih dulu). Uji halaman memakai `t` tiruan
  sehingga **buta** terhadap ini. Tambahkan uji memakai instance i18next asli,
  berikut kontrol negatif bahwa locale `en` tidak sekadar fallback ke `id`.
- ⚠️ **`id.ts` dan `en.ts` adalah berkas yang paling sering disunting paralel.**
  Sebelum merge, jalankan `git merge origin/main` lokal lalu `pnpm tsc` **dan**
  `pnpm build`. Auto-merge git bisa menelan kurung tutup dan menghasilkan berkas
  yang tidak sah. Itu galat **parse**, bukan galat tipe, dan mematikan SELURUH
  halaman. Sudah terjadi 2026-08-09: dua PR menyunting titik yang sama berselang
  enam menit, `main` tak bisa di-build selama 48 menit.

## Verifikasi

Gerbang CI erp-frontend sedang mati (lihat team-memory), jadi ini satu-satunya
yang berdiri.

1. `pnpm tsc` bersih.
2. `pnpm lint` 0 error (warning lama boleh).
3. `pnpm build` — satu-satunya yang menangkap galat parse & resolusi modul.
4. Minimal satu uji yang **benar-benar merender** tiap halaman/komponen baru.
   Uji fungsi murni tidak menangkap cacat perakitan.
5. Uji Radix Tabs pakai `fireEvent.mouseDown`, **bukan** `click`. Dengan `click`
   tabnya tak berpindah dan testnya lolos-diam.
6. `pnpm test` penuh, lalu **bandingkan kegagalannya dengan baseline
   `origin/main`** sebelum menyalahkan perubahan sendiri. Test yang gagal di
   suite penuh tapi lolos sendirian = flake timeout, bukan regresi.
7. Buka halamannya di aplikasi sungguhan sekali. Merge bukan bukti fitur bisa
   dipakai.

## Larangan

- Jangan merakit tabel, filter, atau paginasi sendiri; reuse `@/components/table`.
- Jangan hardcode string user-facing maupun `"id-ID"`.
- Jangan jadikan hasil `useQuery` (`data = []`) sebagai dependensi `useEffect`;
  array baru tiap render menghasilkan lingkaran render yang lolos tsc, lint,
  dan seluruh test.
- Jangan mengubah kontrak backend supaya FE lebih mudah; adaptasi di FE.
