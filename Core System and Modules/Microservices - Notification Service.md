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
- **Cron:** harian pukul 03:00 WIB menghapus inbox berumur > 2 bulan.

## Belum Diimplementasikan / Catatan

- **Channel Email (direncanakan)** — belum ada di kode; dibutuhkan untuk notifikasi **kandidat recruitment** ([[Microservices - Recruitment Service]]). Rekomendasi provider **Resend** (transactional, dukung attachment mis. offer letter PDF); prasyarat deliverability: SPF/DKIM/DMARC di domain `bharatainternasional.com`.
- Selain email, channel yang ada (inbox/FCM/WhatsApp/splash/article) tidak ada stub berarti — fungsional penuh.
- Group `/debug/fcm` ditandai dapat dihapus saat production.

## Dependencies & Integrasi

- **MongoDB** — penyimpanan inbox, splash, dan article.
- **FCM** — push notification (via shared-library).
- **WhatsApp** — pesan personal/grup (via shared-library).
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
