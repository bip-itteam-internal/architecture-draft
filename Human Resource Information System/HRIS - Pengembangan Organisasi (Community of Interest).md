## Deskripsi

*Menu **Pengembangan Organisasi** (Organization Development) di Web ERP: wadah program non-transaksional HR, yaitu komunitas minat karyawan (**Community of Interest**) dan perayaan **ulang tahun** karyawan. Berbeda dari menu HRIS lain yang berbasis transaksi (absensi, cuti, payroll), isi menu ini bersifat program dan budaya kerja. Sisi konsep engagement-nya bertaut ke [[HRIS - Retention]].*

- **Stack**: Next.js App Router (client component) + shadcn/ui + Tailwind; `react-i18next` (id + en)
- **Path di repo**: `erp-frontend`, yaitu `src/features/hris/community/*`, halaman `src/app/(main)/hris/community/{schedule,documentation}/page.tsx`, dan menu `src/components/layout/sidebar-menus.tsx`
- **Status**: ⚠️ Implemented (ada catatan). UI jalan penuh, tetapi **seluruh data klub & dokumentasi masih konstanta di frontend**; belum ada service maupun storage di backend
- **Branch**: `feat/od-community-of-interest` (belum merge saat dok ini ditulis, 2026-07-29)

## Fitur (Sudah Diimplementasikan)

**Struktur menu**: grup sidebar **Pengembangan Organisasi** di modul `hris`, berisi satu menu collapsible **Community of Interest** dengan tiga sub-item:

| Sub-menu | Route | Sumber data |
|---|---|---|
| Jadwal Club | `/hris/community/schedule` | Konstanta FE `data/clubs.ts` |
| Dokumentasi Kegiatan Club | `/hris/community/documentation` | Konstanta FE `data/activities.ts` (data contoh) |
| Ulang Tahun | `/hris/birthdays` | `GET /api/employee/birthdays?month=` ([[Microservices - Employee Service]]) |

**Jadwal Club**: jadwal rutin **Bharata Club Community**, ditampilkan sebagai kisi sepekan (Senin sampai Minggu, hari berjalan ditandai) plus daftar klub.

| Klub | Hari rutin |
|---|---|
| Bharata Badminton Club | Selasa |
| Bharata Football Club | Kamis |
| Bharata Ladies Sport Club | Jumat |
| Bharata Billiard Club | Kamis dan Jumat |

Hari disimpan sebagai **angka `Date#getDay()`**, bukan string "Selasa", lalu diterjemahkan lewat `toLocaleDateString(intlLocale(lang), { weekday: "long" })` agar ikut bahasa aktif sesuai [[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]]. Nama klub adalah nama diri sehingga sengaja **tidak** diterjemahkan.

**Dokumentasi Kegiatan Club**: galeri kegiatan per klub (judul, klub, tanggal, deskripsi, jumlah foto), filter per klub, urut terbaru dulu. Halaman **read-only** dan diberi badge **"Data contoh"** di UI supaya isinya tidak dikira arsip sungguhan.

**Ulang Tahun**: halaman lama `/hris/birthdays` (tabel per bulan + kartu ulang tahun hari ini + export Excel) **dipindah** ke grup ini dari daftar menu HRIS teratas. Route, halaman, dan endpoint tidak berubah, dan menunya tidak diduplikasi.

**i18n**: namespace `hris.community.*` di `src/i18n/locales/id.ts` dan `en.ts`, plus key label sidebar (`pengembangan_organisasi`, `community_of_interest`, `jadwal_club`, `dokumentasi_kegiatan_club`). **Header grup sidebar kini ikut diterjemahkan** (`navigation.tsx` merender `tr(section.group)`); grup lama tanpa key otomatis fallback ke label aslinya.

**Akses**: mengikuti gating modul sidebar, yaitu tampil bagi pemegang `system_roles.hris` dan IT supervisor. Tidak ada penyaringan tambahan per posisi.

**Test**: `clubs.test.ts`, `activities.test.ts`, `utils.test.ts` (nama hari terlokalisasi), `od-menu.test.ts` (struktur grup, anti-duplikat route ulang tahun, kelengkapan key i18n dua locale), dan dua render test halaman.

## Persona / Pengguna

| Persona | Peran & Divisi | Akses/RBAC | Device |
|---|---|---|---|
| Staf OD / HR | Pengembangan Organisasi, HRD | `system_roles.hris` | Desktop |
| IT supervisor | IT | super-akses sidebar | Desktop |

- **Tujuan**: memberi tahu jadwal klub yang berjalan dan mengarsipkan jejak kegiatan komunitas karyawan.
- **Pain point**: jadwal klub sebelumnya hanya beredar lewat obrolan grup, dokumentasi kegiatan tersebar di ponsel masing-masing.
- **Aksi utama**: melihat jadwal sepekan, menelusuri dokumentasi per klub, memantau ulang tahun karyawan bulan berjalan.

> ⚠️ **Karyawan peserta klub belum termasuk pengguna**: menu berada di modul `hris`, sehingga karyawan tanpa role HRIS tidak melihatnya. Keputusan membuka akses lewat Portal Saya masih **TBD** (lihat di bawah).

## Belum Diimplementasikan / Catatan

- **Tidak ada backend**: belum ada service, koleksi, maupun object storage untuk klub, keanggotaan, jadwal, dan foto kegiatan. Konsekuensinya jadwal tidak bisa diubah dari UI dan **unggah foto belum tersedia**.
- **Data dokumentasi = data contoh**, ditandai `TODO(BE)` di `data/activities.ts` dan badge di UI. Harus diganti data nyata sebelum dianggap arsip resmi.
- **Keanggotaan klub, absensi kegiatan, dan notifikasi jadwal**: TBD, belum dibahas.
- **Cakupan akses**: apakah menu dibuka untuk semua karyawan (via Portal Saya atau [[APP - MyBharata]]) atau tetap HR-only, masih TBD.
- Struktur tipe `Club` dan `ClubActivity` sengaja dibuat menyerupai bentuk respons API supaya penggantian ke hook react-query nanti tidak mengubah komponen.

## Dependensi & Integrasi

- [[APP - Web ERP]]: aplikasi induk (menu, sidebar, i18n)
- [[Microservices - Employee Service]]: satu-satunya sumber data nyata di menu ini (ulang tahun karyawan)
- [[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]]: aturan i18n yang diikuti halaman ini

## Dokumen Terkait

- [[HRIS - Retention]]: program engagement karyawan (konsep); menu ini adalah wujud konkret pertamanya
- [[HRIS - Personalia]] · [[HRIS - Big Pictures]]
