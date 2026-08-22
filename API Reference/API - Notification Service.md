## Deskripsi

*Endpoint **notification-service** (inbox, splash, article, FCM, WhatsApp). Gateway: `/api/notification/*`. Open routes pakai service key `?key=NOTIFICATION_SERVICE_KEY`. Grounded ke `services/notification/main.go`.*

- **Implementasi**: [[Microservices - Notification Service]] · **Status**: ✅
- **Indeks**: [[API - Index]]

## Inbox · Splash · Article (JWT via gateway)
| Method | Path | Fungsi |
|---|---|---|
| GET/DELETE | `/inbox` | List inbox (`?count=unread|read|all`, `?id=` mark read) / hapus |
| GET | `/inbox?page=N` | Paginasi **opt-in** (`?limit=` bawaan 15 batas 100, `?status=unread|read`) → `{data, pagination}` |
| POST | `/inbox/read-all` | Tandai semua belum-dibaca milik pemanggil → `{"modified": n}` |
| GET/POST/DELETE | `/splash` | List/buat (multipart)/hapus splash promotion |
| GET/POST/DELETE | `/article` | List (`?recent=`)/buat (multipart)/hapus artikel |
| GET | `/data-type/:dt` | Enum (inbox-category) |

## Open routes (service key `?key=`)
| Method | Path | Fungsi |
|---|---|---|
| POST | `/inbox/send` | Simpan notifikasi ke inbox (category tervalidasi) **lalu push ke browser DAN ponsel**. `400` category tak dikenal · `503` database belum terhubung |
| POST | `/wa/send-personal` · `/wa/send-group` | Kirim WhatsApp personal/grup |
| POST | `/fcm/send-personal` · `/fcm/send-department` · `/fcm/send-broadcast` | Kirim/broadcast FCM (`?platform=mobile|web_browser`) |

## Sistem
| Method | Path | Fungsi |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/debug/fcm` | Test FCM (debug) |

> Cron harian 03:00 WIB hapus inbox >2 bulan ([[IT - Background Jobs & Schedulers]]).

> ⚠️ **`/inbox/send` mengipas sendiri ke dua kanal sejak 2026-08-22.** Service pengirim yang sudah memanggilnya **tidak boleh** memanggil `/fcm/send-*` lagi — penerimanya akan mendapat notifikasi ponsel dua kali. `/fcm/send-*` tetap dipakai untuk pengiriman yang memang bukan notifikasi inbox (pengingat presensi dari cron). Alasan & urutan deploy: [[ADR - 0050 Notifikasi Inbox Mendorong Push ke Browser dan Ponsel Sekaligus]].

> [!warning] `GET /inbox` TANPA `?page` wajib tetap array telanjang
> MyBharata membaca badan respons mentah lalu menguji `data is List`. Begitu balasan
> bawaannya dibungkus jadi objek, uji itu gagal dan cabang `else`-nya mengembalikan **list
> kosong, bukan galat** — inbox jadi kosong tanpa satu pun pesan. APK yang sudah terpasang
> tak bisa dipaksa update, jadi ini kontrak permanen, bukan sampai rilis mobile berikutnya.
> Paginasi karena itu **opt-in**. Detail: [[Microservices - Notification Service]].

## Dokumen Terkait
- [[Microservices - Notification Service]] · [[IT - Background Jobs & Schedulers]] · [[API - Index]]
