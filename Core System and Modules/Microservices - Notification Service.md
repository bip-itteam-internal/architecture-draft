## Deskripsi

*Hub notifikasi multi-channel untuk seluruh ekosistem: in-app inbox, FCM push, WhatsApp, splash promotion, dan article. Menyatukan berbagai channel pihak ketiga dalam satu service sehingga tiap service lain tidak perlu melakukan setup sendiri-sendiri.*

- **Stack:** Go + Fiber v2 + MongoDB
- **Path:** `services/notification`
- **Status:** ✅ Implemented penuh

## Endpoint / Fitur (Sudah Diimplementasikan)

- **Health & util:**
	- `GET /health`
	- `GET /data-type/:dt`
	- `GET /debug/fcm` (khusus dev)
- **Inbox (in-app):**
	- `GET /inbox` — list, dukung `?count=unread|read|all`, serta `?id=` untuk mark-read
	- `DELETE /inbox`
- **Splash promotion:**
	- `GET /splash` — yang aktif, atau `?show_all`
	- `POST /splash` — multipart image (di-upload via file-service/MinIO)
	- `DELETE /splash` — sekaligus menghapus object di MinIO
- **Article:**
	- `GET /article` — `?id`, `?recent`, atau seluruhnya
	- `POST /article` — multipart
	- `DELETE /article`
- **Route pengiriman (ber-service-key, `?key=` cocok `NotificationServiceKey`):**
	- `POST /inbox/send`
	- `POST /wa/send-personal`
	- `POST /wa/send-group`
	- `POST /fcm/send-personal`
	- `POST /fcm/send-department`
	- `POST /fcm/send-broadcast` (batch 500 token)
	- `POST /email/send` — Email via **Resend** (`resend-go/v3`); body `html`/`text`, attachment (base64 `content` atau `path` URL, mis. offer letter PDF), dan `idempotency_key` opsional untuk retry-safe.
- **Cron:** harian pukul 03:00 WIB menghapus inbox berumur > 2 bulan.

## Belum Diimplementasikan / Catatan

- **Channel Email (Resend)** — ✅ sudah di kode (`POST /email/send`, lihat di atas) memakai SDK resmi `resend-go/v3`; ditujukan untuk notifikasi **kandidat recruitment** ([[Microservices - Recruitment Service]]). Catatan operasional: `from` wajib memakai domain terverifikasi di Resend (`bharatainternasional.com` — SPF/DKIM/DMARC) atau Resend menolak (HTTP 422); env `RESEND_API_KEY` & `RESEND_FROM_EMAIL` perlu diset saat deploy — bila kosong, `email.Init()` warn-and-skip sehingga service tetap berjalan. Belum ada smoke test pengiriman live yang tercatat.
- Semua channel (inbox/FCM/WhatsApp/email/splash/article) sudah fungsional di kode — tidak ada stub berarti.
- Group `/debug/fcm` ditandai dapat dihapus saat production.

## Dependencies & Integrasi

- **MongoDB** — penyimpanan inbox, splash, dan article.
- **FCM** — push notification (via shared-library).
- **WhatsApp** — pesan personal/grup (via shared-library).
- **Resend** — provider email transactional (via `resend-go/v3` di shared-library `notification/email`); butuh env `RESEND_API_KEY` & `RESEND_FROM_EMAIL` (sender pada domain terverifikasi).
- Service lain:
	- [[Microservices - Employee Service]] — sumber nomor telepon & FCM token (by id/nama/department/platform).
	- [[Microservices - File Service]] — upload/hapus object di MinIO untuk image splash & article.
- Diakses melalui [[CORE - API Master Gateway]].
- Lihat juga [[DB - Overview and Notes]].

## Dokumen Terkait

- [[CORE - API Master Gateway]]
- [[Microservices - Employee Service]]
- [[Microservices - File Service]]
- [[DB - Overview and Notes]]
- [[APP - MyBharata]]
- [[IT - Background Jobs & Schedulers]] — cron service ini (cleanup inbox >2 bulan, harian 03:00)
