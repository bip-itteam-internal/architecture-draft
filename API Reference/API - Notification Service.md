## Deskripsi

*Endpoint **notification-service** (inbox, splash, article, FCM, WhatsApp). Gateway: `/api/notification/*`. Open routes pakai service key `?key=NOTIFICATION_SERVICE_KEY`. Grounded ke `services/notification/main.go`.*

- **Implementasi**: [[Microservices - Notification Service]] · **Status**: ✅
- **Indeks**: [[API - Index]]

## Inbox · Splash · Article (JWT via gateway)
| Method | Path | Fungsi |
|---|---|---|
| GET/DELETE | `/inbox` | List inbox (`?count=unread|read|all`, `?id=` mark read) / hapus |
| GET/POST/DELETE | `/splash` | List/buat (multipart)/hapus splash promotion |
| GET/POST/DELETE | `/article` | List (`?recent=`)/buat (multipart)/hapus artikel |
| GET | `/data-type/:dt` | Enum (inbox-category) |

## Open routes (service key `?key=`)
| Method | Path | Fungsi |
|---|---|---|
| POST | `/inbox/send` | Simpan notifikasi ke inbox (category tervalidasi) |
| POST | `/wa/send-personal` · `/wa/send-group` | Kirim WhatsApp personal/grup |
| POST | `/fcm/send-personal` · `/fcm/send-department` · `/fcm/send-broadcast` | Kirim/broadcast FCM (`?platform=mobile|web_browser`) |

## Sistem
| Method | Path | Fungsi |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/debug/fcm` | Test FCM (debug) |

> Cron harian 03:00 WIB hapus inbox >2 bulan ([[IT - Background Jobs & Schedulers]]).

## Dokumen Terkait
- [[Microservices - Notification Service]] · [[IT - Background Jobs & Schedulers]] · [[API - Index]]
