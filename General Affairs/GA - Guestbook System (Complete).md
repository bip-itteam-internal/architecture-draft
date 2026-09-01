## Deskripsi

*Versi digital guestbook perusahaan yang dulunya manual. Aplikasi web publik untuk pengunjung mengisi buku tamu via QR code; datanya disimpan di [[Microservices - Attendance Service]]. Sistem ini dimiliki penuh oleh GA Security. Lihat [repository GitHub](https://github.com/bip-itteam-internal/guestbook-system).*

- **Stack**: Astro 5 (SSR, `output: 'server'`) + Svelte 5 (island form) + Tailwind v4; adapter `@astrojs/node` (standalone)
- **Path**: `guestbook-system` (repo terpisah), branch `master`
- **Deploy**: `tamu.bharatainternasional.com` — mobile-first, publik (tanpa login; akses di-gate oleh token per-kunjungan di URL)
- **Status**: ✅ Implemented (funnel pengisian tamu; bukan sistem admin lengkap)

> ⚠️ **Repo ini hanya menangani kategori `personal` dan `group`.** Kategori ketiga, **`internal`** (security mencatat karyawan yang datang terlambat, `visit_purpose` "Verifikasi Karyawan Terlambat"), ditulis dari **[[APP - MyBharata]]** lewat scan QR karyawan, bukan dari aplikasi Astro ini — tipenya memang tak mengenal nilai itu.
>
> ⛔ **Catatan `internal` bukan sekadar buku tamu; ia menggerakkan dua hal di luar layar ini.**
> 1. Mengunci pengajuan koreksi presensi karyawan bersangkutan pada hari itu ([[HRIS - Attendance Correction]] §Aturan Validasi & Anti-Fraud).
> 2. 🔜 Menjadi **sumber angka kartu Terlambat** di Kelola Kehadiran ([[HRIS - Attendance System]]), menggantikan cacah status. Belum live; menunggu bip-erp [#1614](https://github.com/bip-itteam-internal/bip-erp/pull/1614).
>
> Konsekuensi praktisnya: **kesalahan input di sini langsung memengaruhi angka yang dibaca HR.** Satu kedatangan yang tercatat dua kali menaikkan hitungannya, dan itu bukan hipotesis — Agustus 2026 punya 22 baris untuk 21 kejadian, satu nama tersimpan dua kali pada 15 Agustus dengan jam identik. Hitungannya memakai kejadian unik (nama + tanggal) supaya duplikat tak menggandakan angka, tetapi duplikatnya tetap layak dibereskan di sini.

## Alur & Halaman (Sudah Diimplementasikan)

- `index.astro` — landing statis "Cara Penggunaan" (3 langkah)
- `visit/[token].astro` — halaman inti: validasi token (SSR) ke API, gagal → redirect `/invalid`; tampilkan splash + `GuestForm`. Membaca query opsional `standby_security` & `visiting_office`
- `success.astro` — konfirmasi setelah submit
- `invalid.astro` — halaman error (`?reason=invalid|expired|used|notfound`); `404.astro` → redirect ke `/invalid`

**Alur tamu:** Security tampilkan QR → pengunjung scan → `/visit/<token>` → token divalidasi → isi form (kategori personal/rombongan; nama, telepon, instansi, plat, tujuan, orang yang ditemui, jumlah orang bila rombongan) → submit → `/success`. Jika error API, muncul toast dan form tetap aktif.

**Jalur cepat karyawan terlambat** (lewat [[APP - MyBharata]]): karyawan clock-in di gerbang → Security pilih "scan late employee QR" → scan QR data karyawan → detail terisi otomatis & diteruskan ke guestbook.

## Integrasi Backend & Notifikasi

- API client tipis (`fetch`), base URL dari `PUBLIC_API_BASE_URL`. **Tanpa auth header** (akses publik token-based).
- Endpoint yang dipakai (lewat [[CORE - API Master Gateway]] → [[Microservices - Attendance Service]]):
	- Validasi token: `POST /public/guestbook?validate=token`
	- Submit tamu: `POST /public/guestbook`
- Token guestbook dirotasi tiap hari (pukul 04:00) oleh sistem ERP.
- **Notifikasi host** (mis. WhatsApp/FCM saat tamu datang) **dipicu di sisi backend** sebagai respon `POST /public/guestbook`, bukan oleh aplikasi web ini. Di FE hanya ada toast on-screen.
- **Tampilan/daftar guestbook** untuk GA/Security & role HR ada di [[APP - Web ERP]] (bukan di aplikasi tamu ini).

## Belum Diimplementasikan / Catatan

- Tidak ada halaman admin / log kunjungan di aplikasi tamu ini (murni funnel submission)
- QR code di-generate di tempat lain; app ini hanya mengonsumsi link `/visit/<token>`
- `PUBLIC_API_BASE_URL=/proxy` di production bergantung pada reverse proxy eksternal (nginx) — tidak ada middleware proxy di repo
- README sudah usang (masih menyebut endpoint `/api/guest` & field lama; klaim auto-redirect 10 detik di `/success` tidak ada di kode)
- Validasi token meredirect semua kegagalan ke `?reason=invalid` (varian `expired`/`used` praktis tak terjangkau)
- Sisa artifact build Vercel masih ada di tree meski sudah pindah ke adapter Node

## Pratinjau

Aplikasi ini mobile-first; tampilan desktop belum diprioritaskan.

![[Pasted image 20260307112209.png]]

## Dokumen Terkait

- [[Microservices - Attendance Service]]
- [[APP - Web ERP]]
- [[APP - MyBharata]]
