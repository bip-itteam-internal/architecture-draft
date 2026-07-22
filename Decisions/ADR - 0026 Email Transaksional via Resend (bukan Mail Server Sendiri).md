## ADR 0026 — Email Transaksional via Resend (bukan Mail Server Sendiri)

- **Status**: ✅ Accepted (mencerminkan kondisi kode; Resend sudah jalan di produksi)
- **Tanggal**: 2026-07-22
- **Konteks dok**: [[Microservices - Notification Service]] · [[Microservices - Recruitment Service]] · [[IT - Server, VMs and Databases]]

## Context

Sistem mengirim email transaksional keluar: konfirmasi lamaran, jadwal interview, surat penawaran, hasil seleksi, dan link form feedback. Implementasinya sudah ada dan jalan:

- Channel email di [[Microservices - Notification Service]] memakai **Resend** lewat `resend-go/v3` (`shared-library/notification/email/email.go`), fungsi `Send(from, to[], subject, html, text, attachments, idempotencyKey)`.
- Service lain memanggil lewat HTTP internal `POST /email/send` (service-key + gateway key), bukan message queue.
- Env: `RESEND_API_KEY` (wajib) dan `RESEND_FROM_EMAIL` (pengirim default). Gagal-lunak: kalau `RESEND_API_KEY` kosong, notification service tetap jalan, hanya channel email yang mati.
- **Terverifikasi live** di dev 2026-07-16: email "Lamaran Anda Telah Kami Terima" sampai ke inbox pelamar.

Muncul pertanyaan dari tim: apakah sebaiknya pindah ke **Mailu** (mail server self-hosted berbasis Docker) supaya tidak bergantung layanan pihak ketiga dan tidak ada biaya per-email.

Fakta yang membentuk keputusan ini:

- **Penerima utamanya orang luar.** Pelamar memakai Gmail, Yahoo, Outlook. Ini beda mendasar dengan email internal antar-karyawan.
- **Infrastruktur pengirim adalah VPS**, antara lain Biznet Gio ([[IT - Server, VMs and Databases]]). IP VPS tanpa reputasi adalah kondisi terburuk untuk pengiriman ke penyedia mail besar, dan PTR record sering tidak bisa diatur sendiri di kelas VPS ini.
- **Kegagalan email bersifat senyap.** Kalau email masuk spam atau ditolak, tidak ada yang tahu sampai ada pelamar yang mengeluh. Pengiriman di recruitment memang *best-effort* (gagal kirim tidak menggagalkan aksi inti), jadi tidak ada sinyal kegagalan yang naik ke UI.

## Decision

**Email transaksional keluar tetap lewat Resend.** Jangan pindahkan ke mail server self-hosted.

Resend dan Mailu **bukan alternatif setara** — keduanya beda kategori:

| | Resend | Mailu |
|---|---|---|
| Bentuk | Layanan pengiriman via API | Mail server self-hosted |
| Kotak surat | Tidak ada | Ada (SMTP/IMAP/webmail) |
| Terima email | Tidak | Ya |
| Deliverability | Ditanggung penyedia | **Ditanggung kita** |
| Setup | API key | DNS (SPF/DKIM/DMARC/PTR), TLS, antispam, backup |
| Data | Keluar ke pihak ketiga | Tetap di infrastruktur sendiri |

**Mailu boleh dipertimbangkan untuk kebutuhan yang berbeda**, bukan sebagai pengganti:

- Kotak surat internal tim (`hrd@`, `finance@`, `it@`) tanpa biaya per-user
- Menerima email, misalnya balasan pelamar
- Bila muncul kewajiban data harus tetap di dalam negeri

Pola yang disarankan bila keduanya dipakai: **mail server untuk manusia, ESP untuk mesin.**

## Consequences

**Konsekuensi menerima:**

- Ada ketergantungan pada layanan pihak ketiga, dan isi email (termasuk data pelamar) melewati infrastruktur mereka. Perlu diperhitungkan bila ada kewajiban privasi data pelamar.
- Ada biaya begitu volume melewati kuota gratis. Volume saat ini kecil (email per-peristiwa recruitment), tapi rencana digest/reminder harian akan menaikkannya.
- `RESEND_API_KEY` wajib ada di env produksi. **Ini titik gagal senyap:** kalau belum di-set, UI tetap melaporkan sukses tapi email tidak pernah terkirim. Catat di [[IT - Environment Inventory]] dan verifikasi setelah tiap deploy notification service.

**Konsekuensi menolak Mailu untuk kasus ini:**

- Tidak menghemat biaya lisensi, tapi menghindari biaya yang lebih mahal dan tidak kelihatan: waktu mengurus reputasi IP, blocklist, dan antispam.
- Kalau nanti tetap dipasang untuk kotak surat internal, **jangan sekalian dijadikan pengirim email transaksional** tanpa mengukur dulu tingkat sampainya ke Gmail dan Outlook.

**Kalau suatu saat keputusan ini ditinjau ulang**, minimal yang harus disiapkan sebelum memindahkan email transaksional ke server sendiri:

1. IP terpisah khusus kirim, dengan PTR record yang bisa diatur
2. SPF, DKIM, dan DMARC tegak dan terverifikasi
3. Proses IP warming bertahap
4. Monitoring bounce dan complaint, plus pengecekan blocklist rutin
5. Uji kirim nyata ke Gmail, Outlook, dan Yahoo, diukur masuk inbox atau spam

Tanpa kelimanya, memindahkan email pelamar ke server sendiri berisiko membuat pelamar tidak menerima kabar sama sekali, dan itu langsung merusak citra perusahaan sebagai pemberi kerja ([[APP - Portal Karir Bharata]]).

## Dokumen Terkait

- [[Microservices - Notification Service]] — implementasi channel email, endpoint `/email/send`
- [[API - Notification Service]] — daftar endpoint
- [[Microservices - Recruitment Service]] — konsumen terbesar channel email saat ini
- [[IT - Environment Inventory]] — tempat mencatat env `RESEND_API_KEY` / `RESEND_FROM_EMAIL`
- [[IT - Server, VMs and Databases]] — inventaris VPS/VM
- [[APP - Portal Karir Bharata]] — portal publik yang mengandalkan email konfirmasi lamaran
